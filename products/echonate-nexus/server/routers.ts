import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, protectedProcedure, router } from "./_core/trpc";
import { z } from "zod";
import * as db from "./db";
import Stripe from "stripe";
import { PRODUCTS, getProduct, formatPrice } from "./products";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2025-12-15.clover",
});

export const appRouter = router({
  system: systemRouter,
  
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),
  }),

  // Signal procedures
  signals: router({
    // Get all signals (public - but limited for free tier)
    list: publicProcedure
      .input(z.object({
        limit: z.number().min(1).max(100).default(20),
        offset: z.number().min(0).default(0),
        signalType: z.enum(["seismic", "health", "sentiment", "solar", "forex", "crypto", "geopolitical"]).optional(),
      }).optional())
      .query(async ({ input, ctx }) => {
        const limit = input?.limit ?? 20;
        const offset = input?.offset ?? 0;
        const signalType = input?.signalType;
        
        // Check if user is pro/enterprise for full access
        let userTier = "free";
        if (ctx.user) {
          const subscription = await db.getUserSubscription(ctx.user.id);
          userTier = subscription?.tier ?? "free";
        }
        
        // Free tier: only last 7 days, delayed 24h
        const signals = await db.getSignals({ 
          limit, 
          offset, 
          signalType,
          tier: userTier 
        });
        
        return {
          signals,
          tier: userTier,
          hasMore: signals.length === limit,
        };
      }),

    // Get single signal detail
    get: publicProcedure
      .input(z.object({ id: z.number() }))
      .query(async ({ input }) => {
        return db.getSignalById(input.id);
      }),

    // Get signal stats
    stats: publicProcedure.query(async () => {
      return db.getSignalStats();
    }),

    // Create signal (admin only - for ingestion from GitHub agents)
    create: protectedProcedure
      .input(z.object({
        signalType: z.enum(["seismic", "health", "sentiment", "solar", "forex", "crypto", "geopolitical"]),
        source: z.string(),
        sourceUrl: z.string().optional(),
        targetTicker: z.string().optional(),
        targetSector: z.string().optional(),
        direction: z.enum(["bullish", "bearish", "neutral"]),
        strength: z.string(),
        confidence: z.string(),
        title: z.string(),
        summary: z.string(),
        rationale: z.string(),
        rawData: z.any().optional(),
        expiresAt: z.date().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        // Only admin can create signals
        if (ctx.user.role !== "admin") {
          throw new Error("Unauthorized: Admin only");
        }
        return db.createSignal(input);
      }),
  }),

  // Subscription procedures
  subscription: router({
    // Get current user's subscription
    current: protectedProcedure.query(async ({ ctx }) => {
      return db.getUserSubscription(ctx.user.id);
    }),

    // Get pricing tiers
    tiers: publicProcedure.query(() => {
      return [
        {
          id: "free",
          name: "Free",
          price: 0,
          features: [
            "Last 7 days of signals (24h delay)",
            "Basic dashboard access",
            "Email signup required",
          ],
        },
        {
          id: "pro",
          name: "Pro",
          price: 49,
          priceId: process.env.STRIPE_PRO_PRICE_ID,
          features: [
            "Real-time signal alerts",
            "Full signal history",
            "Confidence scores & rationale",
            "API access (100 calls/day)",
            "Priority support",
          ],
        },
        {
          id: "enterprise",
          name: "Enterprise",
          price: 199,
          priceId: process.env.STRIPE_ENTERPRISE_PRICE_ID,
          features: [
            "Everything in Pro",
            "Custom signal configuration",
            "Unlimited API access",
            "Webhook integrations",
            "Dedicated support",
          ],
        },
      ];
    }),
  }),

  // Payment/Checkout procedures
  payments: router({
    // Create checkout session for one-time purchase
    createCheckout: protectedProcedure
      .input(z.object({
        productId: z.string(),
      }))
      .mutation(async ({ input, ctx }) => {
        const product = getProduct(input.productId);
        if (!product) {
          throw new Error("Product not found");
        }

        const origin = ctx.req.headers.origin || "http://localhost:3000";

        const session = await stripe.checkout.sessions.create({
          mode: product.type === "subscription" ? "subscription" : "payment",
          payment_method_types: ["card"],
          customer_email: ctx.user.email || undefined,
          client_reference_id: ctx.user.id.toString(),
          metadata: {
            user_id: ctx.user.id.toString(),
            customer_email: ctx.user.email || "",
            customer_name: ctx.user.name || "",
            product_id: product.id,
          },
          line_items: [
            {
              price_data: {
                currency: product.currency,
                unit_amount: product.price,
                product_data: {
                  name: product.name,
                  description: product.description,
                },
                ...(product.type === "subscription" && {
                  recurring: {
                    interval: product.interval,
                  },
                }),
              },
              quantity: 1,
            },
          ],
          allow_promotion_codes: true,
          success_url: `${origin}/payment/success?session_id={CHECKOUT_SESSION_ID}`,
          cancel_url: `${origin}/payment/cancel`,
        });

        return { url: session.url };
      }),

    // Get user's orders/payments
    orders: protectedProcedure.query(async ({ ctx }) => {
      return db.getUserOrders(ctx.user.id);
    }),

    // Get available products
    products: publicProcedure.query(() => {
      return Object.values(PRODUCTS).map(p => ({
        ...p,
        formattedPrice: formatPrice(p.price, p.currency),
      }));
    }),
  }),

  // Watchlist procedures
  watchlists: router({
    // Get user's watchlists
    list: protectedProcedure.query(async ({ ctx }) => {
      return db.getUserWatchlists(ctx.user.id);
    }),

    // Create watchlist
    create: protectedProcedure
      .input(z.object({
        name: z.string().min(1).max(100),
        description: z.string().optional(),
        tickers: z.array(z.string()).optional(),
        alertOnSignal: z.boolean().optional(),
        minConfidence: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        return db.createWatchlist(ctx.user.id, input);
      }),

    // Update watchlist
    update: protectedProcedure
      .input(z.object({
        id: z.number(),
        name: z.string().min(1).max(100).optional(),
        description: z.string().optional(),
        tickers: z.array(z.string()).optional(),
        alertOnSignal: z.boolean().optional(),
        minConfidence: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        const { id, ...data } = input;
        return db.updateWatchlist(ctx.user.id, id, data);
      }),

    // Delete watchlist
    delete: protectedProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input, ctx }) => {
        return db.deleteWatchlist(ctx.user.id, input.id);
      }),

    // Add ticker to watchlist
    addTicker: protectedProcedure
      .input(z.object({
        watchlistId: z.number(),
        ticker: z.string(),
      }))
      .mutation(async ({ input, ctx }) => {
        return db.addTickerToWatchlist(ctx.user.id, input.watchlistId, input.ticker);
      }),

    // Remove ticker from watchlist
    removeTicker: protectedProcedure
      .input(z.object({
        watchlistId: z.number(),
        ticker: z.string(),
      }))
      .mutation(async ({ input, ctx }) => {
        return db.removeTickerFromWatchlist(ctx.user.id, input.watchlistId, input.ticker);
      }),
  }),

  // Bookmark procedures
  bookmarks: router({
    // Get user's bookmarks
    list: protectedProcedure.query(async ({ ctx }) => {
      return db.getUserBookmarks(ctx.user.id);
    }),

    // Toggle bookmark
    toggle: protectedProcedure
      .input(z.object({
        signalId: z.number(),
        notes: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        return db.toggleBookmark(ctx.user.id, input.signalId, input.notes);
      }),

    // Check if signal is bookmarked
    isBookmarked: protectedProcedure
      .input(z.object({ signalId: z.number() }))
      .query(async ({ input, ctx }) => {
        return db.isSignalBookmarked(ctx.user.id, input.signalId);
      }),
  }),

  // API Key management
  apiKeys: router({
    // List user's API keys
    list: protectedProcedure.query(async ({ ctx }) => {
      return db.getUserApiKeys(ctx.user.id);
    }),

    // Create new API key
    create: protectedProcedure
      .input(z.object({
        name: z.string().min(1).max(100),
        scopes: z.array(z.string()).optional(),
        expiresAt: z.date().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        // Check subscription tier for API access
        const subscription = await db.getUserSubscription(ctx.user.id);
        if (!subscription || subscription.tier === "free") {
          throw new Error("API access requires Pro or Enterprise subscription");
        }
        return db.createApiKey(ctx.user.id, input);
      }),

    // Revoke API key
    revoke: protectedProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input, ctx }) => {
        return db.revokeApiKey(ctx.user.id, input.id);
      }),
  }),

  // Signal accuracy and outcome tracking
  accuracy: router({
    // Get accuracy stats by signal type
    byType: publicProcedure.query(async () => {
      return db.getAccuracyByType();
    }),

    // Record signal outcome (admin only)
    recordOutcome: protectedProcedure
      .input(z.object({
        signalId: z.number(),
        outcome: z.enum(["correct", "incorrect", "expired"]),
        priceAtSignal: z.string().optional(),
        priceAtValidation: z.string().optional(),
        actualReturn: z.string().optional(),
        notes: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        if (ctx.user.role !== "admin") {
          throw new Error("Unauthorized: Admin only");
        }
        return db.recordSignalOutcome(input);
      }),
  }),

  // Alert preferences
  alerts: router({
    // Get user's alert preferences
    preferences: protectedProcedure.query(async ({ ctx }) => {
      return db.getAlertPreferences(ctx.user.id);
    }),

    // Update alert preferences
    updatePreferences: protectedProcedure
      .input(z.object({
        enableSeismic: z.boolean().optional(),
        enableHealth: z.boolean().optional(),
        enableSentiment: z.boolean().optional(),
        enableSolar: z.boolean().optional(),
        enableForex: z.boolean().optional(),
        enableCrypto: z.boolean().optional(),
        enableGeopolitical: z.boolean().optional(),
        minConfidence: z.string().optional(),
        emailEnabled: z.boolean().optional(),
        emailAddress: z.string().email().optional(),
        digestFrequency: z.enum(["instant", "hourly", "daily"]).optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        return db.updateAlertPreferences(ctx.user.id, input);
      }),
  }),
});

// Webhook for GitHub agent signal ingestion
export const webhookRouter = router({
  // Ingest signal from GitHub agent
  ingestSignal: publicProcedure
    .input(z.object({
      source: z.string(),
      eventType: z.string(),
      payload: z.any(),
      secret: z.string(), // Webhook secret for authentication
    }))
    .mutation(async ({ input }) => {
      // Verify webhook secret
      const expectedSecret = process.env.WEBHOOK_SECRET || "echo-webhook-secret";
      if (input.secret !== expectedSecret) {
        throw new Error("Invalid webhook secret");
      }
      return db.processWebhookEvent(input);
    }),
});

export type AppRouter = typeof appRouter;
