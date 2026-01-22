import { int, mysqlEnum, mysqlTable, text, timestamp, varchar, decimal, boolean, json } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 */
export const users = mysqlTable("users", {
  id: int("id").autoincrement().primaryKey(),
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

/**
 * User subscriptions for tiered access
 */
export const subscriptions = mysqlTable("subscriptions", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull(),
  tier: mysqlEnum("tier", ["free", "pro", "enterprise"]).default("free").notNull(),
  stripeCustomerId: varchar("stripeCustomerId", { length: 255 }),
  stripeSubscriptionId: varchar("stripeSubscriptionId", { length: 255 }),
  status: mysqlEnum("status", ["active", "canceled", "past_due", "trialing"]).default("active").notNull(),
  currentPeriodStart: timestamp("currentPeriodStart"),
  currentPeriodEnd: timestamp("currentPeriodEnd"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Subscription = typeof subscriptions.$inferSelect;
export type InsertSubscription = typeof subscriptions.$inferInsert;

/**
 * Market signals detected by the correlation engine
 */
export const signals = mysqlTable("signals", {
  id: int("id").autoincrement().primaryKey(),
  
  // Signal identification
  signalType: mysqlEnum("signalType", [
    "seismic", 
    "health", 
    "sentiment", 
    "solar", 
    "forex", 
    "crypto",
    "geopolitical"
  ]).notNull(),
  
  // Source information
  source: varchar("source", { length: 100 }).notNull(), // e.g., "USGS", "disease.sh"
  sourceUrl: text("sourceUrl"),
  
  // Target information
  targetTicker: varchar("targetTicker", { length: 20 }), // e.g., "TRV", "PFE"
  targetSector: varchar("targetSector", { length: 100 }), // e.g., "Insurance", "Pharma"
  
  // Signal details
  direction: mysqlEnum("direction", ["bullish", "bearish", "neutral"]).notNull(),
  strength: decimal("strength", { precision: 4, scale: 2 }).notNull(), // 0.00 to 1.00
  confidence: decimal("confidence", { precision: 4, scale: 2 }).notNull(), // 0.00 to 1.00
  
  // Rationale
  title: varchar("title", { length: 255 }).notNull(),
  summary: text("summary").notNull(),
  rationale: text("rationale").notNull(),
  
  // Raw data that triggered the signal
  rawData: json("rawData"),
  
  // Tracking
  detectedAt: timestamp("detectedAt").defaultNow().notNull(),
  expiresAt: timestamp("expiresAt"),
  
  // Performance tracking (updated after the fact)
  actualOutcome: mysqlEnum("actualOutcome", ["correct", "incorrect", "pending"]).default("pending"),
  actualReturn: decimal("actualReturn", { precision: 8, scale: 4 }),
  
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Signal = typeof signals.$inferSelect;
export type InsertSignal = typeof signals.$inferInsert;

/**
 * User alert preferences
 */
export const alertPreferences = mysqlTable("alertPreferences", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull(),
  
  // Which signals to receive
  enableSeismic: boolean("enableSeismic").default(true),
  enableHealth: boolean("enableHealth").default(true),
  enableSentiment: boolean("enableSentiment").default(true),
  enableSolar: boolean("enableSolar").default(true),
  enableForex: boolean("enableForex").default(true),
  enableCrypto: boolean("enableCrypto").default(true),
  enableGeopolitical: boolean("enableGeopolitical").default(true),
  
  // Minimum confidence threshold
  minConfidence: decimal("minConfidence", { precision: 4, scale: 2 }).default("0.60"),
  
  // Delivery preferences
  emailEnabled: boolean("emailEnabled").default(true),
  emailAddress: varchar("emailAddress", { length: 320 }),
  
  // Frequency
  digestFrequency: mysqlEnum("digestFrequency", ["instant", "hourly", "daily"]).default("instant"),
  
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type AlertPreference = typeof alertPreferences.$inferSelect;
export type InsertAlertPreference = typeof alertPreferences.$inferInsert;

/**
 * Alert delivery log
 */
export const alertLogs = mysqlTable("alertLogs", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull(),
  signalId: int("signalId").notNull(),
  
  deliveryMethod: mysqlEnum("deliveryMethod", ["email", "api", "webhook"]).notNull(),
  deliveredAt: timestamp("deliveredAt").defaultNow().notNull(),
  status: mysqlEnum("status", ["sent", "failed", "bounced"]).default("sent"),
  
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type AlertLog = typeof alertLogs.$inferSelect;
export type InsertAlertLog = typeof alertLogs.$inferInsert;

/**
 * API usage tracking
 */
export const apiUsage = mysqlTable("apiUsage", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull(),
  
  endpoint: varchar("endpoint", { length: 255 }).notNull(),
  method: varchar("method", { length: 10 }).notNull(),
  
  calledAt: timestamp("calledAt").defaultNow().notNull(),
  responseTime: int("responseTime"), // milliseconds
  statusCode: int("statusCode"),
});

export type ApiUsage = typeof apiUsage.$inferSelect;
export type InsertApiUsage = typeof apiUsage.$inferInsert;

/**
 * Signal type accuracy tracking - Bayesian confidence updating
 */
export const signalAccuracy = mysqlTable("signalAccuracy", {
  id: int("id").autoincrement().primaryKey(),
  
  signalType: mysqlEnum("signalType", [
    "seismic", 
    "health", 
    "sentiment", 
    "solar", 
    "forex", 
    "crypto",
    "geopolitical"
  ]).notNull().unique(),
  
  // Bayesian prior parameters
  priorAlpha: decimal("priorAlpha", { precision: 10, scale: 4 }).default("1.0000"), // successes + 1
  priorBeta: decimal("priorBeta", { precision: 10, scale: 4 }).default("1.0000"),  // failures + 1
  
  // Running totals
  totalSignals: int("totalSignals").default(0),
  correctSignals: int("correctSignals").default(0),
  incorrectSignals: int("incorrectSignals").default(0),
  pendingSignals: int("pendingSignals").default(0),
  
  // Calculated accuracy (posterior mean = alpha / (alpha + beta))
  currentAccuracy: decimal("currentAccuracy", { precision: 5, scale: 4 }).default("0.5000"),
  
  // 30-day rolling accuracy
  rolling30dCorrect: int("rolling30dCorrect").default(0),
  rolling30dTotal: int("rolling30dTotal").default(0),
  rolling30dAccuracy: decimal("rolling30dAccuracy", { precision: 5, scale: 4 }).default("0.5000"),
  
  // Confidence interval (95%)
  confidenceLower: decimal("confidenceLower", { precision: 5, scale: 4 }).default("0.0250"),
  confidenceUpper: decimal("confidenceUpper", { precision: 5, scale: 4 }).default("0.9750"),
  
  lastUpdated: timestamp("lastUpdated").defaultNow().onUpdateNow().notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type SignalAccuracy = typeof signalAccuracy.$inferSelect;
export type InsertSignalAccuracy = typeof signalAccuracy.$inferInsert;

/**
 * Signal outcome validation log
 */
export const signalValidations = mysqlTable("signalValidations", {
  id: int("id").autoincrement().primaryKey(),
  signalId: int("signalId").notNull(),
  
  // Validation details
  validatedAt: timestamp("validatedAt").defaultNow().notNull(),
  outcome: mysqlEnum("outcome", ["correct", "incorrect", "expired"]).notNull(),
  
  // Market data at validation time
  priceAtSignal: decimal("priceAtSignal", { precision: 12, scale: 4 }),
  priceAtValidation: decimal("priceAtValidation", { precision: 12, scale: 4 }),
  actualReturn: decimal("actualReturn", { precision: 8, scale: 4 }),
  
  // Validation method
  validationMethod: mysqlEnum("validationMethod", ["auto", "manual"]).default("auto"),
  notes: text("notes"),
  
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type SignalValidation = typeof signalValidations.$inferSelect;
export type InsertSignalValidation = typeof signalValidations.$inferInsert;

/**
 * Orders/Purchases tracking
 */
export const orders = mysqlTable("orders", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull(),
  
  // Stripe identifiers
  stripePaymentIntentId: varchar("stripePaymentIntentId", { length: 255 }),
  stripeSessionId: varchar("stripeSessionId", { length: 255 }),
  
  // Product info
  productId: varchar("productId", { length: 100 }).notNull(),
  productName: varchar("productName", { length: 255 }).notNull(),
  
  // Payment details
  amount: int("amount").notNull(), // in cents
  currency: varchar("currency", { length: 10 }).default("usd").notNull(),
  status: mysqlEnum("status", ["pending", "completed", "failed", "refunded"]).default("pending").notNull(),
  
  // Metadata
  customerEmail: varchar("customerEmail", { length: 320 }),
  
  completedAt: timestamp("completedAt"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Order = typeof orders.$inferSelect;
export type InsertOrder = typeof orders.$inferInsert;


/**
 * User watchlists for tracking specific tickers
 */
export const watchlists = mysqlTable("watchlists", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull(),
  
  name: varchar("name", { length: 100 }).notNull(),
  description: text("description"),
  
  // Tickers in this watchlist (stored as JSON array)
  tickers: json("tickers").$type<string[]>(),
  
  // Alert settings for this watchlist
  alertOnSignal: boolean("alertOnSignal").default(true),
  minConfidence: decimal("minConfidence", { precision: 4, scale: 2 }).default("0.70"),
  
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Watchlist = typeof watchlists.$inferSelect;
export type InsertWatchlist = typeof watchlists.$inferInsert;

/**
 * API keys for programmatic access
 */
export const apiKeys = mysqlTable("apiKeys", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull(),
  
  name: varchar("name", { length: 100 }).notNull(),
  keyHash: varchar("keyHash", { length: 255 }).notNull(), // SHA-256 hash of the key
  keyPrefix: varchar("keyPrefix", { length: 12 }).notNull(), // First 8 chars for identification
  
  // Permissions
  scopes: json("scopes").$type<string[]>(),
  
  // Usage tracking
  lastUsedAt: timestamp("lastUsedAt"),
  usageCount: int("usageCount").default(0),
  
  // Expiration
  expiresAt: timestamp("expiresAt"),
  revokedAt: timestamp("revokedAt"),
  
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type ApiKey = typeof apiKeys.$inferSelect;
export type InsertApiKey = typeof apiKeys.$inferInsert;

/**
 * GitHub agent webhook events
 */
export const webhookEvents = mysqlTable("webhookEvents", {
  id: int("id").autoincrement().primaryKey(),
  
  // Source identification
  source: varchar("source", { length: 100 }).notNull(), // e.g., "github-agent"
  eventType: varchar("eventType", { length: 100 }).notNull(),
  
  // Payload
  payload: json("payload"),
  
  // Processing status
  status: mysqlEnum("status", ["pending", "processed", "failed"]).default("pending").notNull(),
  processedAt: timestamp("processedAt"),
  errorMessage: text("errorMessage"),
  
  // Result
  signalId: int("signalId"), // If a signal was created from this event
  
  receivedAt: timestamp("receivedAt").defaultNow().notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type WebhookEvent = typeof webhookEvents.$inferSelect;
export type InsertWebhookEvent = typeof webhookEvents.$inferInsert;

/**
 * User bookmarked signals
 */
export const bookmarks = mysqlTable("bookmarks", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull(),
  signalId: int("signalId").notNull(),
  
  notes: text("notes"),
  
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type Bookmark = typeof bookmarks.$inferSelect;
export type InsertBookmark = typeof bookmarks.$inferInsert;
