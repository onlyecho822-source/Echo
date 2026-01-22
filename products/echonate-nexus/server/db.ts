import { eq, desc, and, gte, sql } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import { 
  InsertUser, users, 
  signals, InsertSignal, Signal,
  subscriptions, InsertSubscription, Subscription,
  alertPreferences, InsertAlertPreference, AlertPreference,
  alertLogs,
  orders, Order, InsertOrder
} from "../drizzle/schema";
import { ENV } from './_core/env';

let _db: ReturnType<typeof drizzle> | null = null;

export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

// ============================================
// USER QUERIES
// ============================================

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }

  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot upsert user: database not available");
    return;
  }

  try {
    const values: InsertUser = {
      openId: user.openId,
    };
    const updateSet: Record<string, unknown> = {};

    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];

    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };

    textFields.forEach(assignNullable);

    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role !== undefined) {
      values.role = user.role;
      updateSet.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      values.role = 'admin';
      updateSet.role = 'admin';
    }

    if (!values.lastSignedIn) {
      values.lastSignedIn = new Date();
    }

    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }

    await db.insert(users).values(values).onDuplicateKeyUpdate({
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get user: database not available");
    return undefined;
  }

  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);
  return result.length > 0 ? result[0] : undefined;
}

// ============================================
// SIGNAL QUERIES
// ============================================

export async function getSignals(options: {
  limit: number;
  offset: number;
  signalType?: string;
  tier: string;
}): Promise<Signal[]> {
  const db = await getDb();
  if (!db) return [];

  const { limit, offset, signalType, tier } = options;
  
  // Build conditions
  const conditions = [];
  
  // Free tier: show all signals but with 24h delay messaging (no actual filter for now)
  // Pro/Enterprise get real-time access
  // For demo purposes, show all signals to free users too
  if (tier === "free") {
    // No date filter for now - just show all signals
    // The UI indicates they're delayed by 24h
  }
  
  if (signalType) {
    conditions.push(eq(signals.signalType, signalType as any));
  }

  const query = db
    .select()
    .from(signals)
    .orderBy(desc(signals.detectedAt))
    .limit(limit)
    .offset(offset);

  if (conditions.length > 0) {
    return query.where(and(...conditions));
  }
  
  return query;
}

export async function getSignalById(id: number): Promise<Signal | undefined> {
  const db = await getDb();
  if (!db) return undefined;

  const result = await db.select().from(signals).where(eq(signals.id, id)).limit(1);
  return result.length > 0 ? result[0] : undefined;
}

export async function getSignalStats() {
  const db = await getDb();
  if (!db) return { total: 0, byType: {}, accuracy: 0 };

  const allSignals = await db.select().from(signals);
  
  const byType: Record<string, number> = {};
  let correct = 0;
  let evaluated = 0;
  
  for (const signal of allSignals) {
    byType[signal.signalType] = (byType[signal.signalType] || 0) + 1;
    if (signal.actualOutcome !== "pending") {
      evaluated++;
      if (signal.actualOutcome === "correct") correct++;
    }
  }

  return {
    total: allSignals.length,
    byType,
    accuracy: evaluated > 0 ? correct / evaluated : 0,
    evaluated,
  };
}

export async function createSignal(input: Omit<InsertSignal, "id" | "createdAt" | "updatedAt">): Promise<Signal> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const result = await db.insert(signals).values({
    ...input,
    strength: String(input.strength),
    confidence: String(input.confidence),
  });
  
  const inserted = await db.select().from(signals).where(eq(signals.id, Number(result[0].insertId))).limit(1);
  return inserted[0];
}

// ============================================
// SUBSCRIPTION QUERIES
// ============================================

export async function getUserSubscription(userId: number): Promise<Subscription | null> {
  const db = await getDb();
  if (!db) return null;

  const result = await db
    .select()
    .from(subscriptions)
    .where(eq(subscriptions.userId, userId))
    .limit(1);
  
  // Return the subscription if found, otherwise return a default free tier
  if (result.length > 0) {
    return result[0];
  }
  
  // Return default free tier for users without explicit subscription
  return {
    id: 0,
    userId,
    tier: "free" as const,
    status: "active" as const,
    stripeCustomerId: null,
    stripeSubscriptionId: null,
    currentPeriodStart: null,
    currentPeriodEnd: null,
    createdAt: new Date(),
    updatedAt: new Date(),
  };
}

export async function createOrUpdateSubscription(
  userId: number, 
  data: Partial<InsertSubscription>
): Promise<Subscription> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const existing = await getUserSubscription(userId);
  
  if (existing) {
    await db
      .update(subscriptions)
      .set(data)
      .where(eq(subscriptions.userId, userId));
    return { ...existing, ...data } as Subscription;
  } else {
    await db.insert(subscriptions).values({
      userId,
      tier: "free",
      status: "active",
      ...data,
    });
    return (await getUserSubscription(userId))!;
  }
}

// ============================================
// ALERT PREFERENCE QUERIES
// ============================================

export async function getAlertPreferences(userId: number): Promise<AlertPreference | undefined> {
  const db = await getDb();
  if (!db) return undefined;

  const result = await db
    .select()
    .from(alertPreferences)
    .where(eq(alertPreferences.userId, userId))
    .limit(1);
  
  // Create default preferences if none exist
  if (result.length === 0) {
    await db.insert(alertPreferences).values({ userId });
    return (await getAlertPreferences(userId))!;
  }
  
  return result[0];
}

export async function updateAlertPreferences(
  userId: number,
  data: Partial<InsertAlertPreference>
): Promise<AlertPreference> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  // Ensure preferences exist
  await getAlertPreferences(userId);
  
  // Convert minConfidence to string if present
  const updateData = { ...data };
  if (updateData.minConfidence !== undefined) {
    updateData.minConfidence = String(updateData.minConfidence) as any;
  }
  
  await db
    .update(alertPreferences)
    .set(updateData)
    .where(eq(alertPreferences.userId, userId));
  
  return (await getAlertPreferences(userId))!;
}

// ============================================
// ALERT LOG QUERIES
// ============================================

export async function logAlert(
  userId: number,
  signalId: number,
  deliveryMethod: "email" | "api" | "webhook",
  status: "sent" | "failed" | "bounced" = "sent"
) {
  const db = await getDb();
  if (!db) return;

  await db.insert(alertLogs).values({
    userId,
    signalId,
    deliveryMethod,
    status,
  });
}

// ============================================
// ORDER QUERIES
// ============================================

export async function getUserOrders(userId: number): Promise<Order[]> {
  const db = await getDb();
  if (!db) return [];

  return db
    .select()
    .from(orders)
    .where(eq(orders.userId, userId))
    .orderBy(desc(orders.createdAt));
}

export async function createOrder(data: InsertOrder): Promise<Order> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const result = await db.insert(orders).values(data);
  const inserted = await db.select().from(orders).where(eq(orders.id, Number(result[0].insertId))).limit(1);
  return inserted[0];
}

export async function updateOrderStatus(
  stripeSessionId: string,
  status: "pending" | "completed" | "failed" | "refunded",
  paymentIntentId?: string
): Promise<void> {
  const db = await getDb();
  if (!db) return;

  const updateData: Partial<InsertOrder> = { status };
  if (status === "completed") {
    updateData.completedAt = new Date();
  }
  if (paymentIntentId) {
    updateData.stripePaymentIntentId = paymentIntentId;
  }

  await db
    .update(orders)
    .set(updateData)
    .where(eq(orders.stripeSessionId, stripeSessionId));
}


// ============================================
// WATCHLIST QUERIES
// ============================================

import { 
  watchlists, Watchlist, InsertWatchlist,
  bookmarks, Bookmark, InsertBookmark,
  apiKeys, ApiKey, InsertApiKey,
  signalAccuracy, SignalAccuracy,
  signalValidations, InsertSignalValidation,
  webhookEvents, WebhookEvent
} from "../drizzle/schema";
import crypto from "crypto";

export async function getUserWatchlists(userId: number): Promise<Watchlist[]> {
  const db = await getDb();
  if (!db) return [];

  return db
    .select()
    .from(watchlists)
    .where(eq(watchlists.userId, userId))
    .orderBy(desc(watchlists.createdAt));
}

export async function createWatchlist(
  userId: number,
  data: Omit<InsertWatchlist, "id" | "userId" | "createdAt" | "updatedAt">
): Promise<Watchlist> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const result = await db.insert(watchlists).values({
    userId,
    ...data,
    tickers: data.tickers || [],
  });
  
  const inserted = await db.select().from(watchlists).where(eq(watchlists.id, Number(result[0].insertId))).limit(1);
  return inserted[0];
}

export async function updateWatchlist(
  userId: number,
  watchlistId: number,
  data: Partial<InsertWatchlist>
): Promise<Watchlist | null> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  // Verify ownership
  const existing = await db
    .select()
    .from(watchlists)
    .where(and(eq(watchlists.id, watchlistId), eq(watchlists.userId, userId)))
    .limit(1);
  
  if (existing.length === 0) return null;

  await db
    .update(watchlists)
    .set(data)
    .where(eq(watchlists.id, watchlistId));
  
  const updated = await db.select().from(watchlists).where(eq(watchlists.id, watchlistId)).limit(1);
  return updated[0];
}

export async function deleteWatchlist(userId: number, watchlistId: number): Promise<boolean> {
  const db = await getDb();
  if (!db) return false;

  const result = await db
    .delete(watchlists)
    .where(and(eq(watchlists.id, watchlistId), eq(watchlists.userId, userId)));
  
  return true;
}

export async function addTickerToWatchlist(
  userId: number,
  watchlistId: number,
  ticker: string
): Promise<Watchlist | null> {
  const db = await getDb();
  if (!db) return null;

  const existing = await db
    .select()
    .from(watchlists)
    .where(and(eq(watchlists.id, watchlistId), eq(watchlists.userId, userId)))
    .limit(1);
  
  if (existing.length === 0) return null;

  const currentTickers = (existing[0].tickers as string[]) || [];
  if (!currentTickers.includes(ticker.toUpperCase())) {
    currentTickers.push(ticker.toUpperCase());
    await db
      .update(watchlists)
      .set({ tickers: currentTickers })
      .where(eq(watchlists.id, watchlistId));
  }
  
  const updated = await db.select().from(watchlists).where(eq(watchlists.id, watchlistId)).limit(1);
  return updated[0];
}

export async function removeTickerFromWatchlist(
  userId: number,
  watchlistId: number,
  ticker: string
): Promise<Watchlist | null> {
  const db = await getDb();
  if (!db) return null;

  const existing = await db
    .select()
    .from(watchlists)
    .where(and(eq(watchlists.id, watchlistId), eq(watchlists.userId, userId)))
    .limit(1);
  
  if (existing.length === 0) return null;

  const currentTickers = (existing[0].tickers as string[]) || [];
  const newTickers = currentTickers.filter(t => t !== ticker.toUpperCase());
  
  await db
    .update(watchlists)
    .set({ tickers: newTickers })
    .where(eq(watchlists.id, watchlistId));
  
  const updated = await db.select().from(watchlists).where(eq(watchlists.id, watchlistId)).limit(1);
  return updated[0];
}

// ============================================
// BOOKMARK QUERIES
// ============================================

export async function getUserBookmarks(userId: number): Promise<(Bookmark & { signal?: Signal })[]> {
  const db = await getDb();
  if (!db) return [];

  const userBookmarks = await db
    .select()
    .from(bookmarks)
    .where(eq(bookmarks.userId, userId))
    .orderBy(desc(bookmarks.createdAt));

  // Fetch associated signals
  const result = [];
  for (const bookmark of userBookmarks) {
    const signal = await getSignalById(bookmark.signalId);
    result.push({ ...bookmark, signal });
  }
  
  return result;
}

export async function toggleBookmark(
  userId: number,
  signalId: number,
  notes?: string
): Promise<{ bookmarked: boolean }> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const existing = await db
    .select()
    .from(bookmarks)
    .where(and(eq(bookmarks.userId, userId), eq(bookmarks.signalId, signalId)))
    .limit(1);
  
  if (existing.length > 0) {
    await db
      .delete(bookmarks)
      .where(and(eq(bookmarks.userId, userId), eq(bookmarks.signalId, signalId)));
    return { bookmarked: false };
  } else {
    await db.insert(bookmarks).values({ userId, signalId, notes });
    return { bookmarked: true };
  }
}

export async function isSignalBookmarked(userId: number, signalId: number): Promise<boolean> {
  const db = await getDb();
  if (!db) return false;

  const existing = await db
    .select()
    .from(bookmarks)
    .where(and(eq(bookmarks.userId, userId), eq(bookmarks.signalId, signalId)))
    .limit(1);
  
  return existing.length > 0;
}

// ============================================
// API KEY QUERIES
// ============================================

export async function getUserApiKeys(userId: number): Promise<Omit<ApiKey, "keyHash">[]> {
  const db = await getDb();
  if (!db) return [];

  const keys = await db
    .select()
    .from(apiKeys)
    .where(and(eq(apiKeys.userId, userId), sql`revokedAt IS NULL`))
    .orderBy(desc(apiKeys.createdAt));
  
  // Remove keyHash from response for security
  return keys.map(({ keyHash, ...rest }) => rest);
}

export async function createApiKey(
  userId: number,
  data: { name: string; scopes?: string[]; expiresAt?: Date }
): Promise<{ key: string; keyPrefix: string; id: number }> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  // Generate a secure random key
  const rawKey = `echo_${crypto.randomBytes(32).toString("hex")}`;
  const keyHash = crypto.createHash("sha256").update(rawKey).digest("hex");
  const keyPrefix = rawKey.substring(0, 12);

  const result = await db.insert(apiKeys).values({
    userId,
    name: data.name,
    keyHash,
    keyPrefix,
    scopes: data.scopes || ["signals:read"],
    expiresAt: data.expiresAt,
  });

  return {
    key: rawKey,
    keyPrefix,
    id: Number(result[0].insertId),
  };
}

export async function revokeApiKey(userId: number, keyId: number): Promise<boolean> {
  const db = await getDb();
  if (!db) return false;

  await db
    .update(apiKeys)
    .set({ revokedAt: new Date() })
    .where(and(eq(apiKeys.id, keyId), eq(apiKeys.userId, userId)));
  
  return true;
}

export async function validateApiKey(rawKey: string): Promise<{ userId: number; scopes: string[] } | null> {
  const db = await getDb();
  if (!db) return null;

  const keyHash = crypto.createHash("sha256").update(rawKey).digest("hex");
  
  const result = await db
    .select()
    .from(apiKeys)
    .where(and(
      eq(apiKeys.keyHash, keyHash),
      sql`revokedAt IS NULL`,
      sql`(expiresAt IS NULL OR expiresAt > NOW())`
    ))
    .limit(1);
  
  if (result.length === 0) return null;

  // Update usage stats
  await db
    .update(apiKeys)
    .set({ 
      lastUsedAt: new Date(),
      usageCount: sql`usageCount + 1`
    })
    .where(eq(apiKeys.id, result[0].id));

  return {
    userId: result[0].userId,
    scopes: (result[0].scopes as string[]) || ["signals:read"],
  };
}

// ============================================
// SIGNAL ACCURACY QUERIES (Bayesian)
// ============================================

export async function getAccuracyByType(): Promise<SignalAccuracy[]> {
  const db = await getDb();
  if (!db) return [];

  return db.select().from(signalAccuracy);
}

export async function recordSignalOutcome(data: {
  signalId: number;
  outcome: "correct" | "incorrect" | "expired";
  priceAtSignal?: string;
  priceAtValidation?: string;
  actualReturn?: string;
  notes?: string;
}): Promise<void> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  // Get the signal
  const signal = await getSignalById(data.signalId);
  if (!signal) throw new Error("Signal not found");

  // Record validation
  await db.insert(signalValidations).values({
    signalId: data.signalId,
    outcome: data.outcome,
    priceAtSignal: data.priceAtSignal,
    priceAtValidation: data.priceAtValidation,
    actualReturn: data.actualReturn,
    notes: data.notes,
    validationMethod: "manual",
  });

  // Update signal outcome
  await db
    .update(signals)
    .set({ 
      actualOutcome: data.outcome === "expired" ? "incorrect" : data.outcome,
      actualReturn: data.actualReturn,
    })
    .where(eq(signals.id, data.signalId));

  // Update Bayesian accuracy for signal type
  await updateBayesianAccuracy(signal.signalType, data.outcome);
}

async function updateBayesianAccuracy(
  signalType: string,
  outcome: "correct" | "incorrect" | "expired"
): Promise<void> {
  const db = await getDb();
  if (!db) return;

  // Get or create accuracy record
  let accuracy = await db
    .select()
    .from(signalAccuracy)
    .where(eq(signalAccuracy.signalType, signalType as any))
    .limit(1);

  if (accuracy.length === 0) {
    await db.insert(signalAccuracy).values({
      signalType: signalType as any,
      priorAlpha: "1.0000",
      priorBeta: "1.0000",
      totalSignals: 0,
      correctSignals: 0,
      incorrectSignals: 0,
      pendingSignals: 0,
    });
    accuracy = await db
      .select()
      .from(signalAccuracy)
      .where(eq(signalAccuracy.signalType, signalType as any))
      .limit(1);
  }

  const current = accuracy[0];
  const alpha = parseFloat(current.priorAlpha || "1");
  const beta = parseFloat(current.priorBeta || "1");
  
  // Bayesian update: alpha += success, beta += failure
  const newAlpha = outcome === "correct" ? alpha + 1 : alpha;
  const newBeta = outcome !== "correct" ? beta + 1 : beta;
  
  // Posterior mean = alpha / (alpha + beta)
  const newAccuracy = newAlpha / (newAlpha + newBeta);
  
  // 95% confidence interval using beta distribution approximation
  const variance = (newAlpha * newBeta) / ((newAlpha + newBeta) ** 2 * (newAlpha + newBeta + 1));
  const stdDev = Math.sqrt(variance);
  const confidenceLower = Math.max(0, newAccuracy - 1.96 * stdDev);
  const confidenceUpper = Math.min(1, newAccuracy + 1.96 * stdDev);

  await db
    .update(signalAccuracy)
    .set({
      priorAlpha: newAlpha.toFixed(4),
      priorBeta: newBeta.toFixed(4),
      totalSignals: sql`totalSignals + 1`,
      correctSignals: outcome === "correct" ? sql`correctSignals + 1` : current.correctSignals,
      incorrectSignals: outcome !== "correct" ? sql`incorrectSignals + 1` : current.incorrectSignals,
      currentAccuracy: newAccuracy.toFixed(4),
      confidenceLower: confidenceLower.toFixed(4),
      confidenceUpper: confidenceUpper.toFixed(4),
    })
    .where(eq(signalAccuracy.signalType, signalType as any));
}

// ============================================
// WEBHOOK EVENT QUERIES
// ============================================

export async function processWebhookEvent(data: {
  source: string;
  eventType: string;
  payload: any;
}): Promise<{ eventId: number; signalId?: number }> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  // Record the webhook event
  const result = await db.insert(webhookEvents).values({
    source: data.source,
    eventType: data.eventType,
    payload: data.payload,
    status: "pending",
  });

  const eventId = Number(result[0].insertId);

  try {
    // Process based on event type
    if (data.eventType === "signal.detected") {
      // Create signal from webhook payload
      const signalData = data.payload;
      const signal = await createSignal({
        signalType: signalData.signalType,
        source: signalData.source || data.source,
        sourceUrl: signalData.sourceUrl,
        targetTicker: signalData.targetTicker,
        targetSector: signalData.targetSector,
        direction: signalData.direction,
        strength: signalData.strength,
        confidence: signalData.confidence,
        title: signalData.title,
        summary: signalData.summary,
        rationale: signalData.rationale,
        rawData: signalData.rawData,
        expiresAt: signalData.expiresAt ? new Date(signalData.expiresAt) : undefined,
      });

      // Update webhook event with signal ID
      await db
        .update(webhookEvents)
        .set({ 
          status: "processed",
          processedAt: new Date(),
          signalId: signal.id,
        })
        .where(eq(webhookEvents.id, eventId));

      return { eventId, signalId: signal.id };
    }

    // Mark as processed for other event types
    await db
      .update(webhookEvents)
      .set({ 
        status: "processed",
        processedAt: new Date(),
      })
      .where(eq(webhookEvents.id, eventId));

    return { eventId };
  } catch (error) {
    // Mark as failed
    await db
      .update(webhookEvents)
      .set({ 
        status: "failed",
        errorMessage: error instanceof Error ? error.message : "Unknown error",
      })
      .where(eq(webhookEvents.id, eventId));

    throw error;
  }
}
