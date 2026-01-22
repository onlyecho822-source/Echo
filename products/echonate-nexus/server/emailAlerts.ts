import { getDb } from "./db";
import { alertPreferences, alertLogs, signals, users } from "../drizzle/schema";
import { eq, and, gte, lte } from "drizzle-orm";
import { notifyOwner } from "./_core/notification";

interface Signal {
  id: number;
  signalType: string;
  title: string;
  summary: string;
  direction: string;
  confidence: string;
  targetTicker?: string | null;
  source: string;
  detectedAt: Date;
}

interface AlertPreference {
  userId: number;
  enableSeismic: boolean | null;
  enableHealth: boolean | null;
  enableSentiment: boolean | null;
  enableSolar: boolean | null;
  enableForex: boolean | null;
  enableCrypto: boolean | null;
  enableGeopolitical: boolean | null;
  minConfidence: string | null;
  emailEnabled: boolean | null;
  emailAddress: string | null;
  digestFrequency: string | null;
}

// Map signal types to preference keys
const signalTypeToPreference: Record<string, keyof AlertPreference> = {
  seismic: "enableSeismic",
  health: "enableHealth",
  sentiment: "enableSentiment",
  solar: "enableSolar",
  forex: "enableForex",
  crypto: "enableCrypto",
  geopolitical: "enableGeopolitical",
};

/**
 * Check if a user should receive an alert for a given signal
 */
export function shouldAlertUser(signal: Signal, prefs: AlertPreference): boolean {
  // Check if email is enabled
  if (!prefs.emailEnabled) return false;
  
  // Check if signal type is enabled
  const prefKey = signalTypeToPreference[signal.signalType];
  if (prefKey && !prefs[prefKey]) return false;
  
  // Check confidence threshold
  const minConfidence = parseFloat(prefs.minConfidence || "0.6");
  const signalConfidence = parseFloat(signal.confidence);
  if (signalConfidence < minConfidence) return false;
  
  return true;
}

/**
 * Format a signal for email notification
 */
export function formatSignalEmail(signal: Signal): { subject: string; body: string } {
  const directionEmoji = signal.direction === "bullish" ? "📈" : signal.direction === "bearish" ? "📉" : "➡️";
  const confidencePercent = Math.round(parseFloat(signal.confidence) * 100);
  
  const subject = `${directionEmoji} Echo Signal: ${signal.title}`;
  
  const body = `
# New Signal Detected

**${signal.title}**

${signal.summary}

---

**Details:**
- Type: ${signal.signalType.charAt(0).toUpperCase() + signal.signalType.slice(1)}
- Direction: ${signal.direction.charAt(0).toUpperCase() + signal.direction.slice(1)} ${directionEmoji}
- Confidence: ${confidencePercent}%
${signal.targetTicker ? `- Target: ${signal.targetTicker}` : ''}
- Source: ${signal.source}
- Detected: ${new Date(signal.detectedAt).toLocaleString()}

---

*This is an automated alert from Echo Signal Detector. Signals are informational only and not financial advice.*

[View in Dashboard](${process.env.VITE_APP_URL || 'https://echonate.manus.space'}/dashboard)
`;

  return { subject, body };
}

/**
 * Send alert for a new signal to all eligible users
 */
export async function sendSignalAlerts(signal: Signal): Promise<{ sent: number; failed: number }> {
  const db = await getDb();
  if (!db) return { sent: 0, failed: 0 };

  let sent = 0;
  let failed = 0;

  try {
    // Get all users with alert preferences
    const allPrefs = await db
      .select()
      .from(alertPreferences)
      .where(eq(alertPreferences.emailEnabled, true));

    for (const prefs of allPrefs) {
      if (!shouldAlertUser(signal, prefs as AlertPreference)) continue;
      
      // Check digest frequency - only send instant alerts here
      if (prefs.digestFrequency !== "instant") continue;

      try {
        const { subject, body } = formatSignalEmail(signal);
        
        // Use the notification system to send email
        // In production, this would integrate with an email service
        const success = await notifyOwner({
          title: subject,
          content: body,
        });

        // Log the alert
        await db.insert(alertLogs).values({
          userId: prefs.userId,
          signalId: signal.id,
          deliveryMethod: "email",
          status: success ? "sent" : "failed",
        });

        if (success) {
          sent++;
        } else {
          failed++;
        }
      } catch (error) {
        console.error(`Failed to send alert to user ${prefs.userId}:`, error);
        failed++;
        
        await db.insert(alertLogs).values({
          userId: prefs.userId,
          signalId: signal.id,
          deliveryMethod: "email",
          status: "failed",
        });
      }
    }
  } catch (error) {
    console.error("Error sending signal alerts:", error);
  }

  return { sent, failed };
}

/**
 * Generate hourly digest for users
 */
export async function sendHourlyDigest(): Promise<void> {
  const db = await getDb();
  if (!db) return;

  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);

  // Get signals from the last hour
  const recentSignals = await db
    .select()
    .from(signals)
    .where(gte(signals.detectedAt, oneHourAgo));

  if (recentSignals.length === 0) return;

  // Get users with hourly digest preference
  const hourlyUsers = await db
    .select()
    .from(alertPreferences)
    .where(
      and(
        eq(alertPreferences.emailEnabled, true),
        eq(alertPreferences.digestFrequency, "hourly")
      )
    );

  for (const prefs of hourlyUsers) {
    const eligibleSignals = recentSignals.filter(s => 
      shouldAlertUser(s as Signal, prefs as AlertPreference)
    );

    if (eligibleSignals.length === 0) continue;

    const subject = `Echo Signal Hourly Digest: ${eligibleSignals.length} new signals`;
    const body = `
# Hourly Signal Digest

You have **${eligibleSignals.length}** new signals in the last hour.

${eligibleSignals.map(s => `
## ${s.title}
- Type: ${s.signalType}
- Direction: ${s.direction}
- Confidence: ${Math.round(parseFloat(s.confidence) * 100)}%
`).join('\n---\n')}

[View All in Dashboard](${process.env.VITE_APP_URL || 'https://echonate.manus.space'}/dashboard)
`;

    await notifyOwner({ title: subject, content: body });
  }
}

/**
 * Generate daily digest for users
 */
export async function sendDailyDigest(): Promise<void> {
  const db = await getDb();
  if (!db) return;

  const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);

  // Get signals from the last 24 hours
  const recentSignals = await db
    .select()
    .from(signals)
    .where(gte(signals.detectedAt, oneDayAgo));

  if (recentSignals.length === 0) return;

  // Get users with daily digest preference
  const dailyUsers = await db
    .select()
    .from(alertPreferences)
    .where(
      and(
        eq(alertPreferences.emailEnabled, true),
        eq(alertPreferences.digestFrequency, "daily")
      )
    );

  for (const prefs of dailyUsers) {
    const eligibleSignals = recentSignals.filter(s => 
      shouldAlertUser(s as Signal, prefs as AlertPreference)
    );

    if (eligibleSignals.length === 0) continue;

    // Group by signal type
    const byType: Record<string, typeof eligibleSignals> = {};
    eligibleSignals.forEach(s => {
      if (!byType[s.signalType]) byType[s.signalType] = [];
      byType[s.signalType].push(s);
    });

    const subject = `Echo Signal Daily Digest: ${eligibleSignals.length} signals today`;
    const body = `
# Daily Signal Digest

You have **${eligibleSignals.length}** signals from the last 24 hours.

${Object.entries(byType).map(([type, sigs]) => `
## ${type.charAt(0).toUpperCase() + type.slice(1)} (${sigs.length})
${sigs.slice(0, 5).map(s => `- ${s.title} (${s.direction}, ${Math.round(parseFloat(s.confidence) * 100)}%)`).join('\n')}
${sigs.length > 5 ? `\n*...and ${sigs.length - 5} more*` : ''}
`).join('\n')}

[View All in Dashboard](${process.env.VITE_APP_URL || 'https://echonate.manus.space'}/dashboard)
`;

    await notifyOwner({ title: subject, content: body });
  }
}
