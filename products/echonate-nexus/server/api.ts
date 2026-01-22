import { Router, Request, Response, NextFunction } from "express";
import { getDb } from "./db";
import { signals, subscriptions, users, apiUsage } from "../drizzle/schema";
import { eq, desc, gte, lte, and, sql } from "drizzle-orm";
import jwt from "jsonwebtoken";

const router = Router();

// Rate limits per tier (requests per day)
const RATE_LIMITS = {
  free: 0,      // No API access
  pro: 100,     // 100 calls/day
  enterprise: -1, // Unlimited
};

interface AuthenticatedRequest extends Request {
  user?: {
    id: number;
    tier: string;
  };
}

/**
 * API Key authentication middleware
 * Expects: Authorization: Bearer <jwt_token>
 */
async function authenticateApiKey(
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): Promise<void> {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    res.status(401).json({
      error: "Unauthorized",
      message: "Missing or invalid Authorization header. Use: Bearer <api_key>",
    });
    return;
  }

  const token = authHeader.substring(7);
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as {
      userId: number;
      type: string;
    };

    if (decoded.type !== "api_key") {
      res.status(401).json({
        error: "Unauthorized",
        message: "Invalid API key type",
      });
      return;
    }

    const db = await getDb();
    if (!db) {
      res.status(500).json({ error: "Database unavailable" });
      return;
    }

    // Get user subscription
    const [subscription] = await db
      .select()
      .from(subscriptions)
      .where(eq(subscriptions.userId, decoded.userId))
      .limit(1);

    const tier = subscription?.tier || "free";

    // Check if tier allows API access
    if (RATE_LIMITS[tier as keyof typeof RATE_LIMITS] === 0) {
      res.status(403).json({
        error: "Forbidden",
        message: "API access requires Pro or Enterprise subscription",
      });
      return;
    }

    // Check rate limit
    if (RATE_LIMITS[tier as keyof typeof RATE_LIMITS] > 0) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      const [usage] = await db
        .select({ count: sql<number>`count(*)` })
        .from(apiUsage)
        .where(
          and(
            eq(apiUsage.userId, decoded.userId),
            gte(apiUsage.calledAt, today)
          )
        );

      if (usage.count >= RATE_LIMITS[tier as keyof typeof RATE_LIMITS]) {
        res.status(429).json({
          error: "Rate limit exceeded",
          message: `Daily limit of ${RATE_LIMITS[tier as keyof typeof RATE_LIMITS]} requests reached`,
          resetAt: new Date(today.getTime() + 24 * 60 * 60 * 1000).toISOString(),
        });
        return;
      }
    }

    req.user = { id: decoded.userId, tier };
    next();
  } catch (error) {
    res.status(401).json({
      error: "Unauthorized",
      message: "Invalid or expired API key",
    });
  }
}

/**
 * Log API usage
 */
async function logApiUsage(
  userId: number,
  endpoint: string,
  method: string,
  responseTime: number,
  statusCode: number
): Promise<void> {
  const db = await getDb();
  if (!db) return;

  await db.insert(apiUsage).values({
    userId,
    endpoint,
    method,
    responseTime,
    statusCode,
  });
}

/**
 * GET /api/v1/signals
 * List signals with filtering
 */
router.get("/signals", authenticateApiKey, async (req: AuthenticatedRequest, res: Response) => {
  const startTime = Date.now();
  
  try {
    const db = await getDb();
    if (!db) {
      res.status(500).json({ error: "Database unavailable" });
      return;
    }

    // Parse query parameters
    const limit = Math.min(parseInt(req.query.limit as string) || 20, 100);
    const offset = parseInt(req.query.offset as string) || 0;
    const signalType = req.query.type as string;
    const direction = req.query.direction as string;
    const minConfidence = parseFloat(req.query.min_confidence as string) || 0;
    const ticker = req.query.ticker as string;
    const since = req.query.since ? new Date(req.query.since as string) : null;
    const until = req.query.until ? new Date(req.query.until as string) : null;

    // Build query conditions
    const conditions = [];
    
    if (signalType) {
      conditions.push(eq(signals.signalType, signalType as any));
    }
    if (direction) {
      conditions.push(eq(signals.direction, direction as any));
    }
    if (minConfidence > 0) {
      conditions.push(gte(signals.confidence, minConfidence.toString()));
    }
    if (ticker) {
      conditions.push(eq(signals.targetTicker, ticker.toUpperCase()));
    }
    if (since) {
      conditions.push(gte(signals.detectedAt, since));
    }
    if (until) {
      conditions.push(lte(signals.detectedAt, until));
    }

    // Execute query
    let query = db.select().from(signals);
    
    if (conditions.length > 0) {
      query = query.where(and(...conditions)) as any;
    }

    const results = await query
      .orderBy(desc(signals.detectedAt))
      .limit(limit)
      .offset(offset);

    // Get total count
    const [countResult] = await db
      .select({ count: sql<number>`count(*)` })
      .from(signals)
      .where(conditions.length > 0 ? and(...conditions) : undefined);

    const responseTime = Date.now() - startTime;

    // Log usage
    await logApiUsage(req.user!.id, "/api/v1/signals", "GET", responseTime, 200);

    res.json({
      data: results.map(s => ({
        id: s.id,
        type: s.signalType,
        source: s.source,
        sourceUrl: s.sourceUrl,
        ticker: s.targetTicker,
        sector: s.targetSector,
        direction: s.direction,
        strength: parseFloat(s.strength),
        confidence: parseFloat(s.confidence),
        title: s.title,
        summary: s.summary,
        rationale: s.rationale,
        detectedAt: s.detectedAt,
        expiresAt: s.expiresAt,
        outcome: s.actualOutcome,
        actualReturn: s.actualReturn ? parseFloat(s.actualReturn) : null,
      })),
      meta: {
        total: countResult.count,
        limit,
        offset,
        hasMore: offset + results.length < countResult.count,
      },
    });
  } catch (error) {
    const responseTime = Date.now() - startTime;
    await logApiUsage(req.user!.id, "/api/v1/signals", "GET", responseTime, 500);
    
    console.error("API error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

/**
 * GET /api/v1/signals/:id
 * Get single signal by ID
 */
router.get("/signals/:id", authenticateApiKey, async (req: AuthenticatedRequest, res: Response) => {
  const startTime = Date.now();
  
  try {
    const db = await getDb();
    if (!db) {
      res.status(500).json({ error: "Database unavailable" });
      return;
    }

    const signalId = parseInt(req.params.id);
    
    const [signal] = await db
      .select()
      .from(signals)
      .where(eq(signals.id, signalId))
      .limit(1);

    const responseTime = Date.now() - startTime;
    await logApiUsage(req.user!.id, `/api/v1/signals/${signalId}`, "GET", responseTime, signal ? 200 : 404);

    if (!signal) {
      res.status(404).json({ error: "Signal not found" });
      return;
    }

    res.json({
      data: {
        id: signal.id,
        type: signal.signalType,
        source: signal.source,
        sourceUrl: signal.sourceUrl,
        ticker: signal.targetTicker,
        sector: signal.targetSector,
        direction: signal.direction,
        strength: parseFloat(signal.strength),
        confidence: parseFloat(signal.confidence),
        title: signal.title,
        summary: signal.summary,
        rationale: signal.rationale,
        rawData: signal.rawData,
        detectedAt: signal.detectedAt,
        expiresAt: signal.expiresAt,
        outcome: signal.actualOutcome,
        actualReturn: signal.actualReturn ? parseFloat(signal.actualReturn) : null,
      },
    });
  } catch (error) {
    const responseTime = Date.now() - startTime;
    await logApiUsage(req.user!.id, `/api/v1/signals/${req.params.id}`, "GET", responseTime, 500);
    
    console.error("API error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

/**
 * GET /api/v1/stats
 * Get signal statistics
 */
router.get("/stats", authenticateApiKey, async (req: AuthenticatedRequest, res: Response) => {
  const startTime = Date.now();
  
  try {
    const db = await getDb();
    if (!db) {
      res.status(500).json({ error: "Database unavailable" });
      return;
    }

    // Total signals
    const [totalResult] = await db
      .select({ count: sql<number>`count(*)` })
      .from(signals);

    // Signals by type
    const byType = await db
      .select({
        type: signals.signalType,
        count: sql<number>`count(*)`,
      })
      .from(signals)
      .groupBy(signals.signalType);

    // Signals by direction
    const byDirection = await db
      .select({
        direction: signals.direction,
        count: sql<number>`count(*)`,
      })
      .from(signals)
      .groupBy(signals.direction);

    // Accuracy stats
    const [accuracyResult] = await db
      .select({
        total: sql<number>`count(*)`,
        correct: sql<number>`sum(case when actualOutcome = 'correct' then 1 else 0 end)`,
        incorrect: sql<number>`sum(case when actualOutcome = 'incorrect' then 1 else 0 end)`,
      })
      .from(signals)
      .where(sql`actualOutcome != 'pending'`);

    const responseTime = Date.now() - startTime;
    await logApiUsage(req.user!.id, "/api/v1/stats", "GET", responseTime, 200);

    res.json({
      data: {
        total: totalResult.count,
        byType: Object.fromEntries(byType.map(t => [t.type, t.count])),
        byDirection: Object.fromEntries(byDirection.map(d => [d.direction, d.count])),
        accuracy: {
          evaluated: accuracyResult.total || 0,
          correct: accuracyResult.correct || 0,
          incorrect: accuracyResult.incorrect || 0,
          rate: accuracyResult.total > 0 
            ? (accuracyResult.correct || 0) / accuracyResult.total 
            : 0,
        },
      },
    });
  } catch (error) {
    const responseTime = Date.now() - startTime;
    await logApiUsage(req.user!.id, "/api/v1/stats", "GET", responseTime, 500);
    
    console.error("API error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

/**
 * GET /api/v1/usage
 * Get API usage statistics for the authenticated user
 */
router.get("/usage", authenticateApiKey, async (req: AuthenticatedRequest, res: Response) => {
  const startTime = Date.now();
  
  try {
    const db = await getDb();
    if (!db) {
      res.status(500).json({ error: "Database unavailable" });
      return;
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Today's usage
    const [todayUsage] = await db
      .select({ count: sql<number>`count(*)` })
      .from(apiUsage)
      .where(
        and(
          eq(apiUsage.userId, req.user!.id),
          gte(apiUsage.calledAt, today)
        )
      );

    // Total usage
    const [totalUsage] = await db
      .select({ count: sql<number>`count(*)` })
      .from(apiUsage)
      .where(eq(apiUsage.userId, req.user!.id));

    const limit = RATE_LIMITS[req.user!.tier as keyof typeof RATE_LIMITS];

    const responseTime = Date.now() - startTime;
    await logApiUsage(req.user!.id, "/api/v1/usage", "GET", responseTime, 200);

    res.json({
      data: {
        tier: req.user!.tier,
        today: {
          used: todayUsage.count,
          limit: limit === -1 ? "unlimited" : limit,
          remaining: limit === -1 ? "unlimited" : Math.max(0, limit - todayUsage.count),
        },
        total: totalUsage.count,
        resetAt: new Date(today.getTime() + 24 * 60 * 60 * 1000).toISOString(),
      },
    });
  } catch (error) {
    const responseTime = Date.now() - startTime;
    await logApiUsage(req.user!.id, "/api/v1/usage", "GET", responseTime, 500);
    
    console.error("API error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
