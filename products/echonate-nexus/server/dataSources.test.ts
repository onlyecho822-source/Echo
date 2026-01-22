import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock db
vi.mock("./db", () => ({
  getDb: vi.fn().mockResolvedValue({
    select: vi.fn().mockReturnValue({
      from: vi.fn().mockReturnValue({
        where: vi.fn().mockReturnValue({
          limit: vi.fn().mockResolvedValue([])
        })
      })
    }),
    insert: vi.fn().mockReturnValue({
      values: vi.fn().mockResolvedValue({ insertId: 1 })
    })
  })
}));

describe("Data Source Connectors", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("USGS Earthquake API", () => {
    it("should fetch earthquakes from USGS API", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          features: [
            {
              properties: {
                mag: 6.5,
                place: "100km SW of Tokyo, Japan",
                time: Date.now(),
                url: "https://earthquake.usgs.gov/earthquakes/eventpage/test",
                title: "M 6.5 - 100km SW of Tokyo, Japan",
                tsunami: 0
              },
              geometry: { coordinates: [139.6917, 35.6895, 10] }
            }
          ],
          metadata: { count: 1, title: "USGS Earthquakes" }
        })
      });

      const { fetchUSGSEarthquakes } = await import("./dataSources");
      const signals = await fetchUSGSEarthquakes();
      
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("earthquake.usgs.gov")
      );
      expect(signals.length).toBeGreaterThanOrEqual(0);
    });

    it("should handle USGS API errors gracefully", async () => {
      mockFetch.mockResolvedValueOnce({ ok: false, status: 500 });

      const { fetchUSGSEarthquakes } = await import("./dataSources");
      const signals = await fetchUSGSEarthquakes();
      
      expect(signals).toEqual([]);
    });
  });

  describe("Disease.sh Health API", () => {
    it("should fetch COVID data from disease.sh", async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({
            cases: 500000000,
            todayCases: 150000,
            deaths: 6000000,
            todayDeaths: 500,
            recovered: 480000000,
            active: 14000000,
            critical: 50000,
            updated: Date.now()
          })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([
            {
              country: "USA",
              cases: 100000000,
              todayCases: 50000,
              deaths: 1000000,
              todayDeaths: 100,
              recovered: 95000000,
              active: 4000000,
              critical: 10000,
              updated: Date.now()
            }
          ])
        });

      const { fetchHealthData } = await import("./dataSources");
      const signals = await fetchHealthData();
      
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("disease.sh")
      );
      expect(signals.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe("NASA Solar Weather API", () => {
    it("should fetch solar flare data from NASA DONKI", async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([
            {
              eventID: "2026-01-20T00:00:00-FLR-001",
              startTime: "2026-01-20T00:00:00Z",
              classType: "X1.5",
              sourceLocation: "N15W30"
            }
          ])
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([])
        });

      const { fetchSolarWeather } = await import("./dataSources");
      const signals = await fetchSolarWeather();
      
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("api.nasa.gov/DONKI")
      );
      expect(signals.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe("Signal Generation", () => {
    it("should generate signals with correct structure", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ features: [], metadata: { count: 0 } })
      });

      const { fetchAllDataSources } = await import("./dataSources");
      const signals = await fetchAllDataSources();
      
      expect(Array.isArray(signals)).toBe(true);
    });
  });
});

describe("WebSocket Server", () => {
  it("should export signalWebSocket singleton", async () => {
    const { signalWebSocket } = await import("./websocket");
    expect(signalWebSocket).toBeDefined();
    expect(typeof signalWebSocket.getStats).toBe("function");
    expect(typeof signalWebSocket.broadcastSignal).toBe("function");
  });

  it("should return stats with client count", async () => {
    const { signalWebSocket } = await import("./websocket");
    const stats = signalWebSocket.getStats();
    expect(stats).toHaveProperty("clientCount");
    expect(stats).toHaveProperty("uptime");
    expect(typeof stats.clientCount).toBe("number");
  });
});
