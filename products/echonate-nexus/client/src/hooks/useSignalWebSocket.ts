/**
 * React Hook for WebSocket Signal Connection
 * Provides real-time signal updates to components
 */

import { useEffect, useRef, useState, useCallback } from "react";

interface Signal {
  id?: number;
  signalType: string;
  title: string;
  summary: string;
  targetTicker: string;
  direction: "bullish" | "bearish" | "neutral";
  strength: string;
  confidence: string;
  source: string;
  detectedAt: string | Date;
}

interface WebSocketStats {
  connected: boolean;
  clientCount?: number;
  lastFetch?: string;
  signalsFetched?: number;
  signalsSaved?: number;
  subscriptions?: string[];
}

interface UseSignalWebSocketOptions {
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  signalTypes?: string[];
}

interface UseSignalWebSocketReturn {
  isConnected: boolean;
  signals: Signal[];
  stats: WebSocketStats;
  connect: () => void;
  disconnect: () => void;
  subscribe: (signalTypes: string[]) => void;
  unsubscribe: (signalTypes: string[]) => void;
  clearSignals: () => void;
}

export function useSignalWebSocket(
  options: UseSignalWebSocketOptions = {}
): UseSignalWebSocketReturn {
  const {
    autoConnect = true,
    reconnectInterval = 5000,
    maxReconnectAttempts = 10,
    signalTypes = ["seismic", "health", "sentiment", "solar", "forex", "crypto", "geopolitical"],
  } = options;

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const [isConnected, setIsConnected] = useState(false);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [stats, setStats] = useState<WebSocketStats>({ connected: false });

  /**
   * Get WebSocket URL based on current location
   */
  const getWebSocketUrl = useCallback(() => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    return `${protocol}//${host}/ws`;
  }, []);

  /**
   * Send message to WebSocket server
   */
  const sendMessage = useCallback((type: string, data?: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, data, timestamp: Date.now() }));
    }
  }, []);

  /**
   * Connect to WebSocket server
   */
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const url = getWebSocketUrl();
    console.log("[WebSocket] Connecting to", url);

    try {
      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        console.log("[WebSocket] Connected");
        setIsConnected(true);
        setStats((prev) => ({ ...prev, connected: true }));
        reconnectAttemptsRef.current = 0;

        // Subscribe to signal types
        if (signalTypes.length > 0) {
          sendMessage("subscribe", { signalTypes });
        }

        // Start ping interval
        pingIntervalRef.current = setInterval(() => {
          sendMessage("ping");
        }, 25000);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          switch (message.type) {
            case "signal":
              // Add new signal to the beginning of the list
              setSignals((prev) => {
                const newSignals = [message.data, ...prev];
                // Keep only last 100 signals in memory
                return newSignals.slice(0, 100);
              });
              break;

            case "stats":
              setStats((prev) => ({
                ...prev,
                ...message.data,
                connected: true,
              }));
              break;

            case "pong":
              // Connection is alive
              break;

            default:
              console.log("[WebSocket] Unknown message type:", message.type);
          }
        } catch (error) {
          console.error("[WebSocket] Error parsing message:", error);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log("[WebSocket] Disconnected:", event.code, event.reason);
        setIsConnected(false);
        setStats((prev) => ({ ...prev, connected: false }));

        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // Attempt reconnection
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(
            `[WebSocket] Reconnecting in ${reconnectInterval}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
          );
          reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error("[WebSocket] Error:", error);
      };
    } catch (error) {
      console.error("[WebSocket] Failed to connect:", error);
    }
  }, [getWebSocketUrl, sendMessage, signalTypes, reconnectInterval, maxReconnectAttempts]);

  /**
   * Disconnect from WebSocket server
   */
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, "User disconnect");
      wsRef.current = null;
    }

    setIsConnected(false);
    setStats({ connected: false });
  }, []);

  /**
   * Subscribe to signal types
   */
  const subscribe = useCallback(
    (types: string[]) => {
      sendMessage("subscribe", { signalTypes: types });
    },
    [sendMessage]
  );

  /**
   * Unsubscribe from signal types
   */
  const unsubscribe = useCallback(
    (types: string[]) => {
      sendMessage("unsubscribe", { signalTypes: types });
    },
    [sendMessage]
  );

  /**
   * Clear signals buffer
   */
  const clearSignals = useCallback(() => {
    setSignals([]);
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    isConnected,
    signals,
    stats,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    clearSignals,
  };
}

export default useSignalWebSocket;
