import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock database functions
vi.mock("./db", () => ({
  getUserWatchlists: vi.fn().mockResolvedValue([
    { id: 1, userId: 1, name: "Tech Stocks", tickers: ["AAPL", "GOOGL"], alertOnSignal: true, minConfidence: "0.70" }
  ]),
  createWatchlist: vi.fn().mockResolvedValue({ id: 2, userId: 1, name: "New List", tickers: [] }),
  updateWatchlist: vi.fn().mockResolvedValue({ id: 1, name: "Updated" }),
  deleteWatchlist: vi.fn().mockResolvedValue(true),
  addTickerToWatchlist: vi.fn().mockResolvedValue({ id: 1, tickers: ["AAPL", "GOOGL", "MSFT"] }),
  removeTickerFromWatchlist: vi.fn().mockResolvedValue({ id: 1, tickers: ["AAPL"] }),
  getUserBookmarks: vi.fn().mockResolvedValue([
    { id: 1, userId: 1, signalId: 1, signal: { id: 1, title: "Test Signal" } }
  ]),
  toggleBookmark: vi.fn().mockResolvedValue({ bookmarked: true }),
  isSignalBookmarked: vi.fn().mockResolvedValue(true),
  getUserApiKeys: vi.fn().mockResolvedValue([
    { id: 1, name: "Test Key", keyPrefix: "echo_abc123", usageCount: 10, createdAt: new Date() }
  ]),
  createApiKey: vi.fn().mockResolvedValue({ key: "echo_test_key_123", keyPrefix: "echo_test_k", id: 1 }),
  revokeApiKey: vi.fn().mockResolvedValue(true),
  validateApiKey: vi.fn().mockResolvedValue({ userId: 1, scopes: ["signals:read"] }),
  getAccuracyByType: vi.fn().mockResolvedValue([
    { signalType: "seismic", currentAccuracy: "0.7500", totalSignals: 20, correctSignals: 15 }
  ]),
  recordSignalOutcome: vi.fn().mockResolvedValue(undefined),
  processWebhookEvent: vi.fn().mockResolvedValue({ eventId: 1, signalId: 1 }),
  getUserSubscription: vi.fn().mockResolvedValue({ tier: "pro", status: "active" }),
  getSignals: vi.fn().mockResolvedValue([]),
  getSignalById: vi.fn().mockResolvedValue({ id: 1, title: "Test" }),
}));

describe("Watchlist Features", () => {
  it("should list user watchlists", async () => {
    const db = await import("./db");
    const result = await db.getUserWatchlists(1);
    expect(result).toHaveLength(1);
    expect(result[0].name).toBe("Tech Stocks");
  });

  it("should create a watchlist", async () => {
    const db = await import("./db");
    const result = await db.createWatchlist(1, { name: "New List" });
    expect(result.id).toBe(2);
    expect(result.name).toBe("New List");
  });

  it("should add ticker to watchlist", async () => {
    const db = await import("./db");
    const result = await db.addTickerToWatchlist(1, 1, "MSFT");
    expect(result.tickers).toContain("MSFT");
  });

  it("should remove ticker from watchlist", async () => {
    const db = await import("./db");
    const result = await db.removeTickerFromWatchlist(1, 1, "GOOGL");
    expect(result.tickers).not.toContain("GOOGL");
  });
});

describe("Bookmark Features", () => {
  it("should list user bookmarks", async () => {
    const db = await import("./db");
    const result = await db.getUserBookmarks(1);
    expect(result).toHaveLength(1);
    expect(result[0].signal.title).toBe("Test Signal");
  });

  it("should toggle bookmark", async () => {
    const db = await import("./db");
    const result = await db.toggleBookmark(1, 1);
    expect(result.bookmarked).toBe(true);
  });

  it("should check if signal is bookmarked", async () => {
    const db = await import("./db");
    const result = await db.isSignalBookmarked(1, 1);
    expect(result).toBe(true);
  });
});

describe("API Key Features", () => {
  it("should list user API keys", async () => {
    const db = await import("./db");
    const result = await db.getUserApiKeys(1);
    expect(result).toHaveLength(1);
    expect(result[0].name).toBe("Test Key");
  });

  it("should create API key", async () => {
    const db = await import("./db");
    const result = await db.createApiKey(1, { name: "New Key" });
    expect(result.key).toContain("echo_");
    expect(result.keyPrefix).toBe("echo_test_k");
  });

  it("should revoke API key", async () => {
    const db = await import("./db");
    const result = await db.revokeApiKey(1, 1);
    expect(result).toBe(true);
  });

  it("should validate API key", async () => {
    const db = await import("./db");
    const result = await db.validateApiKey("echo_test_key");
    expect(result).not.toBeNull();
    expect(result?.userId).toBe(1);
    expect(result?.scopes).toContain("signals:read");
  });
});

describe("Accuracy Tracking (Bayesian)", () => {
  it("should get accuracy by signal type", async () => {
    const db = await import("./db");
    const result = await db.getAccuracyByType();
    expect(result).toHaveLength(1);
    expect(result[0].signalType).toBe("seismic");
    expect(parseFloat(result[0].currentAccuracy)).toBe(0.75);
  });

  it("should record signal outcome", async () => {
    const db = await import("./db");
    await expect(db.recordSignalOutcome({
      signalId: 1,
      outcome: "correct",
      priceAtSignal: "100.00",
      priceAtValidation: "105.00",
      actualReturn: "0.05",
    })).resolves.not.toThrow();
  });
});

describe("Webhook Processing", () => {
  it("should process webhook event", async () => {
    const db = await import("./db");
    const result = await db.processWebhookEvent({
      source: "github-agent",
      eventType: "signal.detected",
      payload: { signalType: "seismic", title: "Test" },
    });
    expect(result.eventId).toBe(1);
    expect(result.signalId).toBe(1);
  });
});

describe("Subscription Tier Access", () => {
  it("should return pro subscription", async () => {
    const db = await import("./db");
    const result = await db.getUserSubscription(1);
    expect(result?.tier).toBe("pro");
    expect(result?.status).toBe("active");
  });
});
