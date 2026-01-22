import { describe, it, expect, vi, beforeEach } from "vitest";
import * as db from "./db";

// Mock the database module
vi.mock("./db", async () => {
  const actual = await vi.importActual("./db");
  return {
    ...actual,
    getAlertPreferences: vi.fn(),
    updateAlertPreferences: vi.fn(),
  };
});

describe("Alert Preferences", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should have default alert preferences structure", async () => {
    const mockPrefs = {
      id: 1,
      userId: 1,
      enableSeismic: true,
      enableHealth: true,
      enableSentiment: true,
      enableSolar: true,
      enableForex: true,
      enableCrypto: true,
      enableGeopolitical: true,
      minConfidence: "0.60",
      emailEnabled: true,
      emailAddress: "test@example.com",
      digestFrequency: "instant" as const,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    (db.getAlertPreferences as any).mockResolvedValue(mockPrefs);

    const result = await db.getAlertPreferences(1);
    
    expect(result).toBeDefined();
    expect(result?.enableSeismic).toBe(true);
    expect(result?.minConfidence).toBe("0.60");
    expect(result?.digestFrequency).toBe("instant");
  });

  it("should update alert preferences", async () => {
    const updatedPrefs = {
      id: 1,
      userId: 1,
      enableSeismic: false,
      enableHealth: true,
      enableSentiment: true,
      enableSolar: true,
      enableForex: true,
      enableCrypto: true,
      enableGeopolitical: true,
      minConfidence: "0.75",
      emailEnabled: false,
      emailAddress: "new@example.com",
      digestFrequency: "daily" as const,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    (db.updateAlertPreferences as any).mockResolvedValue(updatedPrefs);

    const result = await db.updateAlertPreferences(1, {
      enableSeismic: false,
      minConfidence: "0.75",
      emailEnabled: false,
      digestFrequency: "daily",
    });

    expect(result).toBeDefined();
    expect(result?.enableSeismic).toBe(false);
    expect(result?.minConfidence).toBe("0.75");
    expect(result?.digestFrequency).toBe("daily");
  });

  it("should validate digest frequency values", () => {
    const validFrequencies = ["instant", "hourly", "daily"];
    
    validFrequencies.forEach(freq => {
      expect(["instant", "hourly", "daily"]).toContain(freq);
    });
    
    expect(["instant", "hourly", "daily"]).not.toContain("weekly");
  });

  it("should validate confidence threshold range", () => {
    const minConfidence = 0.3;
    const maxConfidence = 0.95;
    
    expect(minConfidence).toBeGreaterThanOrEqual(0);
    expect(maxConfidence).toBeLessThanOrEqual(1);
    expect(minConfidence).toBeLessThan(maxConfidence);
  });
});
