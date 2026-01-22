/**
 * WebSocket Server for Real-Time Signal Broadcasting
 * Provides instant signal updates to connected clients
 */

import { WebSocketServer, WebSocket } from "ws";
import { Server } from "http";
import { runScheduledFetch } from "./dataSources";

interface SignalMessage {
  type: "signal" | "stats" | "ping" | "pong" | "subscribe" | "unsubscribe";
  data?: any;
  timestamp: number;
}

interface ClientConnection {
  ws: WebSocket;
  userId?: string;
  subscriptions: Set<string>; // Signal types to receive
  isAlive: boolean;
  connectedAt: Date;
}

class SignalWebSocketServer {
  private wss: WebSocketServer | null = null;
  private clients: Map<WebSocket, ClientConnection> = new Map();
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private fetchInterval: NodeJS.Timeout | null = null;
  
  /**
   * Initialize WebSocket server attached to HTTP server
   */
  initialize(server: Server): void {
    this.wss = new WebSocketServer({ 
      server,
      path: "/ws",
    });
    
    console.log("[WebSocket] Server initialized on /ws");
    
    this.wss.on("connection", (ws, req) => {
      this.handleConnection(ws, req);
    });
    
    this.wss.on("error", (error) => {
      console.error("[WebSocket] Server error:", error);
    });
    
    // Start heartbeat to detect dead connections
    this.startHeartbeat();
    
    // Start periodic data fetching
    this.startDataFetching();
  }
  
  /**
   * Handle new WebSocket connection
   */
  private handleConnection(ws: WebSocket, req: any): void {
    const clientIp = req.socket.remoteAddress;
    console.log(`[WebSocket] New connection from ${clientIp}`);
    
    // Initialize client connection
    const connection: ClientConnection = {
      ws,
      subscriptions: new Set(["seismic", "health", "sentiment", "solar", "forex", "crypto", "geopolitical"]),
      isAlive: true,
      connectedAt: new Date(),
    };
    
    this.clients.set(ws, connection);
    
    // Send welcome message
    this.sendToClient(ws, {
      type: "stats",
      data: {
        connected: true,
        clientCount: this.clients.size,
        subscriptions: Array.from(connection.subscriptions),
      },
      timestamp: Date.now(),
    });
    
    // Handle incoming messages
    ws.on("message", (data) => {
      this.handleMessage(ws, data);
    });
    
    // Handle pong responses
    ws.on("pong", () => {
      const client = this.clients.get(ws);
      if (client) {
        client.isAlive = true;
      }
    });
    
    // Handle disconnection
    ws.on("close", () => {
      console.log(`[WebSocket] Client disconnected`);
      this.clients.delete(ws);
    });
    
    // Handle errors
    ws.on("error", (error) => {
      console.error("[WebSocket] Client error:", error);
      this.clients.delete(ws);
    });
  }
  
  /**
   * Handle incoming WebSocket message
   */
  private handleMessage(ws: WebSocket, data: any): void {
    try {
      const message: SignalMessage = JSON.parse(data.toString());
      const client = this.clients.get(ws);
      
      if (!client) return;
      
      switch (message.type) {
        case "ping":
          this.sendToClient(ws, { type: "pong", timestamp: Date.now() });
          break;
          
        case "subscribe":
          if (message.data?.signalTypes && Array.isArray(message.data.signalTypes)) {
            message.data.signalTypes.forEach((type: string) => {
              client.subscriptions.add(type);
            });
            this.sendToClient(ws, {
              type: "stats",
              data: { subscriptions: Array.from(client.subscriptions) },
              timestamp: Date.now(),
            });
          }
          break;
          
        case "unsubscribe":
          if (message.data?.signalTypes && Array.isArray(message.data.signalTypes)) {
            message.data.signalTypes.forEach((type: string) => {
              client.subscriptions.delete(type);
            });
            this.sendToClient(ws, {
              type: "stats",
              data: { subscriptions: Array.from(client.subscriptions) },
              timestamp: Date.now(),
            });
          }
          break;
          
        default:
          console.log(`[WebSocket] Unknown message type: ${message.type}`);
      }
    } catch (error) {
      console.error("[WebSocket] Error parsing message:", error);
    }
  }
  
  /**
   * Send message to specific client
   */
  private sendToClient(ws: WebSocket, message: SignalMessage): void {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    }
  }
  
  /**
   * Broadcast signal to all subscribed clients
   */
  broadcastSignal(signal: any): void {
    const message: SignalMessage = {
      type: "signal",
      data: signal,
      timestamp: Date.now(),
    };
    
    let sentCount = 0;
    
    this.clients.forEach((client, ws) => {
      // Check if client is subscribed to this signal type
      if (client.subscriptions.has(signal.signalType)) {
        this.sendToClient(ws, message);
        sentCount++;
      }
    });
    
    if (sentCount > 0) {
      console.log(`[WebSocket] Broadcast signal to ${sentCount} clients: ${signal.title}`);
    }
  }
  
  /**
   * Broadcast multiple signals
   */
  broadcastSignals(signals: any[]): void {
    for (const signal of signals) {
      this.broadcastSignal(signal);
    }
  }
  
  /**
   * Start heartbeat to detect dead connections
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      this.clients.forEach((client, ws) => {
        if (!client.isAlive) {
          console.log("[WebSocket] Terminating dead connection");
          ws.terminate();
          this.clients.delete(ws);
          return;
        }
        
        client.isAlive = false;
        ws.ping();
      });
    }, 30000); // Check every 30 seconds
  }
  
  /**
   * Start periodic data fetching from external sources
   */
  private startDataFetching(): void {
    // Initial fetch after 5 seconds
    setTimeout(async () => {
      await this.fetchAndBroadcast();
    }, 5000);
    
    // Then fetch every 5 minutes
    this.fetchInterval = setInterval(async () => {
      await this.fetchAndBroadcast();
    }, 5 * 60 * 1000);
  }
  
  /**
   * Fetch data from sources and broadcast new signals
   */
  private async fetchAndBroadcast(): Promise<void> {
    try {
      console.log("[WebSocket] Running scheduled data fetch...");
      const result = await runScheduledFetch();
      console.log(`[WebSocket] Fetched ${result.fetched} signals, saved ${result.saved} new`);
      
      // Broadcast stats update
      const statsMessage: SignalMessage = {
        type: "stats",
        data: {
          lastFetch: new Date().toISOString(),
          signalsFetched: result.fetched,
          signalsSaved: result.saved,
          clientCount: this.clients.size,
        },
        timestamp: Date.now(),
      };
      
      this.clients.forEach((_, ws) => {
        this.sendToClient(ws, statsMessage);
      });
    } catch (error) {
      console.error("[WebSocket] Error in scheduled fetch:", error);
    }
  }
  
  /**
   * Get current connection stats
   */
  getStats(): { clientCount: number; uptime: number } {
    return {
      clientCount: this.clients.size,
      uptime: process.uptime(),
    };
  }
  
  /**
   * Shutdown WebSocket server
   */
  shutdown(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }
    if (this.fetchInterval) {
      clearInterval(this.fetchInterval);
    }
    
    this.clients.forEach((_, ws) => {
      ws.close(1000, "Server shutting down");
    });
    
    this.wss?.close();
    console.log("[WebSocket] Server shut down");
  }
}

// Singleton instance
export const signalWebSocket = new SignalWebSocketServer();
