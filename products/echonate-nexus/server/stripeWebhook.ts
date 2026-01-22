import { Router, raw } from "express";
import Stripe from "stripe";
import * as db from "./db";
import { getProduct } from "./products";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2025-12-15.clover",
});

const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!;

export const stripeWebhookRouter = Router();

// IMPORTANT: Use raw body parser for webhook signature verification
stripeWebhookRouter.post(
  "/",
  raw({ type: "application/json" }),
  async (req, res) => {
    const sig = req.headers["stripe-signature"];

    if (!sig) {
      console.error("[Stripe Webhook] No signature header");
      return res.status(400).send("No signature");
    }

    let event: Stripe.Event;

    try {
      event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret);
    } catch (err: any) {
      console.error("[Stripe Webhook] Signature verification failed:", err.message);
      return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    // Handle test events
    if (event.id.startsWith("evt_test_")) {
      console.log("[Stripe Webhook] Test event detected, returning verification response");
      return res.json({ verified: true });
    }

    console.log(`[Stripe Webhook] Received event: ${event.type} (${event.id})`);

    try {
      switch (event.type) {
        case "checkout.session.completed": {
          const session = event.data.object as Stripe.Checkout.Session;
          
          console.log(`[Stripe Webhook] Checkout completed: ${session.id}`);
          
          // Update order status
          await db.updateOrderStatus(
            session.id,
            "completed",
            session.payment_intent as string
          );

          // If subscription, update user subscription tier
          if (session.mode === "subscription" && session.subscription) {
            const userId = parseInt(session.metadata?.user_id || "0");
            const productId = session.metadata?.product_id;
            
            if (userId && productId) {
              const tier = productId.includes("enterprise") ? "enterprise" : "pro";
              await db.createOrUpdateSubscription(userId, {
                tier,
                stripeCustomerId: session.customer as string,
                stripeSubscriptionId: session.subscription as string,
                status: "active",
              });
            }
          }
          break;
        }

        case "customer.subscription.updated": {
          const subscription = event.data.object as Stripe.Subscription;
          console.log(`[Stripe Webhook] Subscription updated: ${subscription.id}`);
          
          // Update subscription status in database
          // Find user by stripeSubscriptionId and update status
          break;
        }

        case "customer.subscription.deleted": {
          const subscription = event.data.object as Stripe.Subscription;
          console.log(`[Stripe Webhook] Subscription canceled: ${subscription.id}`);
          
          // Downgrade user to free tier
          break;
        }

        case "invoice.payment_failed": {
          const invoice = event.data.object as Stripe.Invoice;
          console.log(`[Stripe Webhook] Payment failed for invoice: ${invoice.id}`);
          
          // Mark subscription as past_due
          break;
        }

        default:
          console.log(`[Stripe Webhook] Unhandled event type: ${event.type}`);
      }

      res.json({ received: true });
    } catch (err: any) {
      console.error(`[Stripe Webhook] Error processing event:`, err);
      res.status(500).json({ error: "Webhook handler failed" });
    }
  }
);
