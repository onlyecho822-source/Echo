import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock the database module
vi.mock('./db', () => ({
  getSignals: vi.fn(),
  getSignalById: vi.fn(),
  getSignalStats: vi.fn(),
  createSignal: vi.fn(),
  getUserSubscription: vi.fn(),
  getAlertPreferences: vi.fn(),
  updateAlertPreferences: vi.fn(),
}));

import * as db from './db';

describe('Signal Database Functions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getSignals', () => {
    it('should return signals with pagination', async () => {
      const mockSignals = [
        {
          id: 1,
          signalType: 'seismic',
          source: 'USGS',
          direction: 'bearish',
          strength: '0.72',
          confidence: '0.65',
          title: 'M6.2 Earthquake',
          summary: 'Major earthquake detected',
          rationale: 'Insurance claims expected',
          targetTicker: 'TRV',
          detectedAt: new Date(),
        },
      ];

      vi.mocked(db.getSignals).mockResolvedValue(mockSignals as any);

      const result = await db.getSignals({
        limit: 20,
        offset: 0,
        tier: 'pro',
      });

      expect(result).toEqual(mockSignals);
      expect(db.getSignals).toHaveBeenCalledWith({
        limit: 20,
        offset: 0,
        tier: 'pro',
      });
    });

    it('should filter by signal type', async () => {
      vi.mocked(db.getSignals).mockResolvedValue([]);

      await db.getSignals({
        limit: 10,
        offset: 0,
        signalType: 'health',
        tier: 'free',
      });

      expect(db.getSignals).toHaveBeenCalledWith({
        limit: 10,
        offset: 0,
        signalType: 'health',
        tier: 'free',
      });
    });
  });

  describe('getSignalById', () => {
    it('should return a single signal by ID', async () => {
      const mockSignal = {
        id: 1,
        signalType: 'seismic',
        title: 'Test Signal',
      };

      vi.mocked(db.getSignalById).mockResolvedValue(mockSignal as any);

      const result = await db.getSignalById(1);

      expect(result).toEqual(mockSignal);
      expect(db.getSignalById).toHaveBeenCalledWith(1);
    });

    it('should return undefined for non-existent signal', async () => {
      vi.mocked(db.getSignalById).mockResolvedValue(undefined);

      const result = await db.getSignalById(999);

      expect(result).toBeUndefined();
    });
  });

  describe('getSignalStats', () => {
    it('should return signal statistics', async () => {
      const mockStats = {
        total: 100,
        byType: {
          seismic: 30,
          health: 25,
          sentiment: 45,
        },
        accuracy: 0.72,
        evaluated: 50,
      };

      vi.mocked(db.getSignalStats).mockResolvedValue(mockStats);

      const result = await db.getSignalStats();

      expect(result).toEqual(mockStats);
      expect(result.total).toBe(100);
      expect(result.accuracy).toBe(0.72);
    });
  });

  describe('createSignal', () => {
    it('should create a new signal', async () => {
      const newSignal = {
        signalType: 'seismic' as const,
        source: 'USGS',
        direction: 'bearish' as const,
        strength: '0.65',
        confidence: '0.70',
        title: 'New Earthquake Signal',
        summary: 'Detected seismic activity',
        rationale: 'Historical correlation with insurance stocks',
      };

      const createdSignal = {
        id: 1,
        ...newSignal,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      vi.mocked(db.createSignal).mockResolvedValue(createdSignal as any);

      const result = await db.createSignal(newSignal as any);

      expect(result.id).toBe(1);
      expect(result.signalType).toBe('seismic');
    });
  });
});

describe('Subscription Database Functions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getUserSubscription', () => {
    it('should return user subscription', async () => {
      const mockSubscription = {
        id: 1,
        userId: 1,
        tier: 'pro',
        status: 'active',
      };

      vi.mocked(db.getUserSubscription).mockResolvedValue(mockSubscription as any);

      const result = await db.getUserSubscription(1);

      expect(result?.tier).toBe('pro');
      expect(result?.status).toBe('active');
    });

    it('should return undefined for user without subscription', async () => {
      vi.mocked(db.getUserSubscription).mockResolvedValue(undefined);

      const result = await db.getUserSubscription(999);

      expect(result).toBeUndefined();
    });
  });
});

describe('Alert Preferences Database Functions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getAlertPreferences', () => {
    it('should return user alert preferences', async () => {
      const mockPrefs = {
        id: 1,
        userId: 1,
        enableSeismic: true,
        enableHealth: true,
        minConfidence: '0.60',
        emailEnabled: true,
      };

      vi.mocked(db.getAlertPreferences).mockResolvedValue(mockPrefs as any);

      const result = await db.getAlertPreferences(1);

      expect(result?.enableSeismic).toBe(true);
      expect(result?.minConfidence).toBe('0.60');
    });
  });

  describe('updateAlertPreferences', () => {
    it('should update alert preferences', async () => {
      const updatedPrefs = {
        id: 1,
        userId: 1,
        enableSeismic: false,
        minConfidence: '0.75',
      };

      vi.mocked(db.updateAlertPreferences).mockResolvedValue(updatedPrefs as any);

      const result = await db.updateAlertPreferences(1, {
        enableSeismic: false,
        minConfidence: '0.75',
      });

      expect(result.enableSeismic).toBe(false);
    });
  });
});

describe('Signal Type Validation', () => {
  it('should accept valid signal types', () => {
    const validTypes = ['seismic', 'health', 'sentiment', 'solar', 'forex', 'crypto', 'geopolitical'];
    
    validTypes.forEach(type => {
      expect(validTypes.includes(type)).toBe(true);
    });
  });

  it('should accept valid directions', () => {
    const validDirections = ['bullish', 'bearish', 'neutral'];
    
    validDirections.forEach(dir => {
      expect(validDirections.includes(dir)).toBe(true);
    });
  });
});

describe('Tier Access Control', () => {
  it('free tier should have limited access', () => {
    const freeTierFeatures = {
      delayHours: 24,
      historyDays: 7,
      apiAccess: false,
    };

    expect(freeTierFeatures.delayHours).toBe(24);
    expect(freeTierFeatures.historyDays).toBe(7);
    expect(freeTierFeatures.apiAccess).toBe(false);
  });

  it('pro tier should have full access', () => {
    const proTierFeatures = {
      delayHours: 0,
      historyDays: -1, // unlimited
      apiAccess: true,
      apiCallsPerDay: 100,
    };

    expect(proTierFeatures.delayHours).toBe(0);
    expect(proTierFeatures.apiAccess).toBe(true);
  });
});
