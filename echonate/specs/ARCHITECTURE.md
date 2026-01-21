# EchoNate Nexus — Technical Architecture

**Version:** 1.0.0
**Codename:** KRAKEN
**Created:** 2026-01-21

---

## 1. SYSTEM OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ECHONATE NEXUS (THE KRAKEN)                         │
│                    Command & Control Intelligence System                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        KRAKEN CORE (BRAIN)                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │  LLM Engine │  │  Decision   │  │  Memory     │                 │   │
│  │  │  (Claude)   │  │  Matrix     │  │  Cortex     │                 │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │   │
│  │         └────────────────┼────────────────┘                         │   │
│  │                          │                                          │   │
│  │                   ┌──────▼──────┐                                   │   │
│  │                   │   NEXUS     │                                   │   │
│  │                   │   ROUTER    │                                   │   │
│  │                   └──────┬──────┘                                   │   │
│  └──────────────────────────┼──────────────────────────────────────────┘   │
│                             │                                               │
│  ┌──────────────────────────┼──────────────────────────────────────────┐   │
│  │                    TENTACLE ARRAY (8 ARMS)                          │   │
│  │                                                                      │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                        │   │
│  │  │TENTACLE│ │TENTACLE│ │TENTACLE│ │TENTACLE│                        │   │
│  │  │   1    │ │   2    │ │   3    │ │   4    │                        │   │
│  │  │ GitHub │ │ GitLab │ │ Social │ │  News  │                        │   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘                        │   │
│  │                                                                      │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                        │   │
│  │  │TENTACLE│ │TENTACLE│ │TENTACLE│ │TENTACLE│                        │   │
│  │  │   5    │ │   6    │ │   7    │ │   8    │                        │   │
│  │  │ Email  │ │ Search │ │ Archive│ │ Custom │                        │   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘                        │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         OPERATOR INTERFACE                           │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │   │
│  │  │   Chat   │  │ Dashboard│  │  Action  │  │  Brain   │             │   │
│  │  │ Terminal │  │  Monitor │  │   Log    │  │   Map    │             │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. DATABASE SCHEMA

### 2.1 Core Tables

```sql
-- Tentacle definitions (the 8 arms)
CREATE TABLE tentacles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL UNIQUE,        -- 'github', 'gitlab', 'twitter', etc.
  display_name VARCHAR(128) NOT NULL,       -- 'GitHub Tentacle'
  tentacle_type ENUM('code', 'social', 'news', 'email', 'search', 'archive', 'custom') NOT NULL,
  status ENUM('active', 'dormant', 'error', 'disabled') DEFAULT 'dormant',
  config JSON,                              -- API keys, endpoints, settings
  last_pulse TIMESTAMP,                     -- Last successful connection
  pulse_count INT DEFAULT 0,                -- Total operations
  error_count INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW() ON UPDATE NOW()
);

-- Actions performed by EchoNate
CREATE TABLE actions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  action_type ENUM('commit', 'pr', 'workflow', 'post', 'fetch', 'analyze', 'seed', 'custom') NOT NULL,
  tentacle_id INT NOT NULL,
  status ENUM('pending', 'executing', 'success', 'failed', 'rolled_back') DEFAULT 'pending',
  command TEXT,                             -- Original command/instruction
  payload JSON,                             -- Action parameters
  result JSON,                              -- Execution result
  rollback_data JSON,                       -- Data needed to undo action
  can_rollback BOOLEAN DEFAULT FALSE,
  parent_action_id INT,                     -- For chained actions
  execution_time_ms INT,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  executed_at TIMESTAMP,
  FOREIGN KEY (tentacle_id) REFERENCES tentacles(id),
  FOREIGN KEY (parent_action_id) REFERENCES actions(id)
);

-- Chat messages with EchoNate
CREATE TABLE messages (
  id INT AUTO_INCREMENT PRIMARY KEY,
  role ENUM('user', 'echonate', 'system') NOT NULL,
  content TEXT NOT NULL,
  content_type ENUM('text', 'command', 'result', 'error', 'voice') DEFAULT 'text',
  metadata JSON,                            -- Attachments, context, etc.
  action_id INT,                            -- If message triggered an action
  session_id VARCHAR(64),                   -- Conversation session
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (action_id) REFERENCES actions(id)
);

-- Media monitoring sources
CREATE TABLE media_sources (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  source_type ENUM('news', 'social', 'blog', 'forum', 'rss', 'api') NOT NULL,
  url VARCHAR(512),
  config JSON,                              -- API keys, selectors, filters
  priority ENUM('critical', 'high', 'medium', 'low') DEFAULT 'medium',
  scan_frequency_minutes INT DEFAULT 60,
  last_scanned TIMESTAMP,
  status ENUM('active', 'paused', 'error') DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Media items collected
CREATE TABLE media_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  source_id INT NOT NULL,
  title VARCHAR(512),
  content TEXT,
  url VARCHAR(512),
  author VARCHAR(256),
  published_at TIMESTAMP,
  sentiment ENUM('positive', 'negative', 'neutral'),
  relevance_score DECIMAL(3,2),             -- 0.00 to 1.00
  keywords JSON,
  is_seeding_target BOOLEAN DEFAULT FALSE,
  seeding_status ENUM('none', 'queued', 'seeded', 'verified') DEFAULT 'none',
  metadata JSON,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (source_id) REFERENCES media_sources(id)
);

-- Phoenix ecosystem nodes (repos, systems)
CREATE TABLE ecosystem_nodes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  node_type ENUM('repository', 'service', 'api', 'database', 'external') NOT NULL,
  name VARCHAR(128) NOT NULL,
  platform VARCHAR(64),                     -- 'github', 'gitlab', 'vercel', etc.
  url VARCHAR(512),
  status ENUM('active', 'synced', 'stale', 'offline') DEFAULT 'active',
  parent_node_id INT,                       -- For hierarchical structure
  metadata JSON,                            -- Stars, forks, last commit, etc.
  last_sync TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (parent_node_id) REFERENCES ecosystem_nodes(id)
);

-- Connections between nodes (for brain visualization)
CREATE TABLE node_connections (
  id INT AUTO_INCREMENT PRIMARY KEY,
  source_node_id INT NOT NULL,
  target_node_id INT NOT NULL,
  connection_type ENUM('sync', 'mirror', 'depends', 'triggers', 'feeds') NOT NULL,
  data_flow_direction ENUM('unidirectional', 'bidirectional') DEFAULT 'unidirectional',
  strength DECIMAL(3,2) DEFAULT 1.00,       -- Connection strength for visualization
  last_activity TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (source_node_id) REFERENCES ecosystem_nodes(id),
  FOREIGN KEY (target_node_id) REFERENCES ecosystem_nodes(id)
);

-- EchoNate identity and personality
CREATE TABLE identity (
  id INT AUTO_INCREMENT PRIMARY KEY,
  key_name VARCHAR(64) NOT NULL UNIQUE,
  value TEXT,
  value_type ENUM('text', 'url', 'json', 'number') DEFAULT 'text',
  category ENUM('personality', 'voice', 'visual', 'behavior') NOT NULL,
  updated_at TIMESTAMP DEFAULT NOW() ON UPDATE NOW()
);
```

### 2.2 Drizzle Schema (TypeScript)

```typescript
// drizzle/schema.ts

import { 
  int, mysqlEnum, mysqlTable, text, timestamp, 
  varchar, json, boolean, decimal 
} from "drizzle-orm/mysql-core";

// Tentacle definitions
export const tentacles = mysqlTable("tentacles", {
  id: int("id").autoincrement().primaryKey(),
  name: varchar("name", { length: 64 }).notNull().unique(),
  displayName: varchar("display_name", { length: 128 }).notNull(),
  tentacleType: mysqlEnum("tentacle_type", [
    'code', 'social', 'news', 'email', 'search', 'archive', 'custom'
  ]).notNull(),
  status: mysqlEnum("status", ['active', 'dormant', 'error', 'disabled']).default('dormant'),
  config: json("config"),
  lastPulse: timestamp("last_pulse"),
  pulseCount: int("pulse_count").default(0),
  errorCount: int("error_count").default(0),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
});

// Actions
export const actions = mysqlTable("actions", {
  id: int("id").autoincrement().primaryKey(),
  actionType: mysqlEnum("action_type", [
    'commit', 'pr', 'workflow', 'post', 'fetch', 'analyze', 'seed', 'custom'
  ]).notNull(),
  tentacleId: int("tentacle_id").notNull(),
  status: mysqlEnum("status", [
    'pending', 'executing', 'success', 'failed', 'rolled_back'
  ]).default('pending'),
  command: text("command"),
  payload: json("payload"),
  result: json("result"),
  rollbackData: json("rollback_data"),
  canRollback: boolean("can_rollback").default(false),
  parentActionId: int("parent_action_id"),
  executionTimeMs: int("execution_time_ms"),
  errorMessage: text("error_message"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  executedAt: timestamp("executed_at"),
});

// Messages
export const messages = mysqlTable("messages", {
  id: int("id").autoincrement().primaryKey(),
  role: mysqlEnum("role", ['user', 'echonate', 'system']).notNull(),
  content: text("content").notNull(),
  contentType: mysqlEnum("content_type", [
    'text', 'command', 'result', 'error', 'voice'
  ]).default('text'),
  metadata: json("metadata"),
  actionId: int("action_id"),
  sessionId: varchar("session_id", { length: 64 }),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Media sources
export const mediaSources = mysqlTable("media_sources", {
  id: int("id").autoincrement().primaryKey(),
  name: varchar("name", { length: 128 }).notNull(),
  sourceType: mysqlEnum("source_type", [
    'news', 'social', 'blog', 'forum', 'rss', 'api'
  ]).notNull(),
  url: varchar("url", { length: 512 }),
  config: json("config"),
  priority: mysqlEnum("priority", ['critical', 'high', 'medium', 'low']).default('medium'),
  scanFrequencyMinutes: int("scan_frequency_minutes").default(60),
  lastScanned: timestamp("last_scanned"),
  status: mysqlEnum("status", ['active', 'paused', 'error']).default('active'),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Media items
export const mediaItems = mysqlTable("media_items", {
  id: int("id").autoincrement().primaryKey(),
  sourceId: int("source_id").notNull(),
  title: varchar("title", { length: 512 }),
  content: text("content"),
  url: varchar("url", { length: 512 }),
  author: varchar("author", { length: 256 }),
  publishedAt: timestamp("published_at"),
  sentiment: mysqlEnum("sentiment", ['positive', 'negative', 'neutral']),
  relevanceScore: decimal("relevance_score", { precision: 3, scale: 2 }),
  keywords: json("keywords"),
  isSeedingTarget: boolean("is_seeding_target").default(false),
  seedingStatus: mysqlEnum("seeding_status", [
    'none', 'queued', 'seeded', 'verified'
  ]).default('none'),
  metadata: json("metadata"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Ecosystem nodes
export const ecosystemNodes = mysqlTable("ecosystem_nodes", {
  id: int("id").autoincrement().primaryKey(),
  nodeType: mysqlEnum("node_type", [
    'repository', 'service', 'api', 'database', 'external'
  ]).notNull(),
  name: varchar("name", { length: 128 }).notNull(),
  platform: varchar("platform", { length: 64 }),
  url: varchar("url", { length: 512 }),
  status: mysqlEnum("status", ['active', 'synced', 'stale', 'offline']).default('active'),
  parentNodeId: int("parent_node_id"),
  metadata: json("metadata"),
  lastSync: timestamp("last_sync"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Node connections
export const nodeConnections = mysqlTable("node_connections", {
  id: int("id").autoincrement().primaryKey(),
  sourceNodeId: int("source_node_id").notNull(),
  targetNodeId: int("target_node_id").notNull(),
  connectionType: mysqlEnum("connection_type", [
    'sync', 'mirror', 'depends', 'triggers', 'feeds'
  ]).notNull(),
  dataFlowDirection: mysqlEnum("data_flow_direction", [
    'unidirectional', 'bidirectional'
  ]).default('unidirectional'),
  strength: decimal("strength", { precision: 3, scale: 2 }).default("1.00"),
  lastActivity: timestamp("last_activity"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Identity
export const identity = mysqlTable("identity", {
  id: int("id").autoincrement().primaryKey(),
  keyName: varchar("key_name", { length: 64 }).notNull().unique(),
  value: text("value"),
  valueType: mysqlEnum("value_type", ['text', 'url', 'json', 'number']).default('text'),
  category: mysqlEnum("category", [
    'personality', 'voice', 'visual', 'behavior'
  ]).notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
});

// Type exports
export type Tentacle = typeof tentacles.$inferSelect;
export type Action = typeof actions.$inferSelect;
export type Message = typeof messages.$inferSelect;
export type MediaSource = typeof mediaSources.$inferSelect;
export type MediaItem = typeof mediaItems.$inferSelect;
export type EcosystemNode = typeof ecosystemNodes.$inferSelect;
export type NodeConnection = typeof nodeConnections.$inferSelect;
export type Identity = typeof identity.$inferSelect;
```

---

## 3. API CONTRACTS (tRPC)

### 3.1 Router Structure

```typescript
// server/routers.ts

export const appRouter = router({
  auth: authRouter,
  system: systemRouter,
  
  // KRAKEN CORE
  echonate: router({
    chat: chatRouter,           // Conversation with EchoNate
    identity: identityRouter,   // Avatar, voice, personality
  }),
  
  // TENTACLE ARRAY
  tentacles: router({
    list: tentacleListRouter,
    github: githubTentacleRouter,
    gitlab: gitlabTentacleRouter,
    social: socialTentacleRouter,
    news: newsTentacleRouter,
    email: emailTentacleRouter,
    search: searchTentacleRouter,
    archive: archiveTentacleRouter,
    custom: customTentacleRouter,
  }),
  
  // ACTION SYSTEM
  actions: router({
    list: actionListRouter,
    execute: actionExecuteRouter,
    rollback: actionRollbackRouter,
  }),
  
  // MONITORING
  media: router({
    sources: mediaSourcesRouter,
    items: mediaItemsRouter,
    seeding: seedingRouter,
  }),
  
  // ECOSYSTEM
  ecosystem: router({
    nodes: ecosystemNodesRouter,
    connections: connectionsRouter,
    map: ecosystemMapRouter,
  }),
});
```

### 3.2 Chat Router (Core EchoNate Interaction)

```typescript
// server/routers/echonate/chat.ts

import { z } from "zod";
import { router, protectedProcedure } from "../../_core/trpc";
import { invokeLLM } from "../../_core/llm";

export const chatRouter = router({
  // Send message to EchoNate
  send: protectedProcedure
    .input(z.object({
      content: z.string().min(1).max(10000),
      sessionId: z.string().optional(),
    }))
    .mutation(async ({ ctx, input }) => {
      // 1. Save user message
      // 2. Parse for commands (starts with /)
      // 3. If command, route to tentacle
      // 4. If conversation, invoke LLM with EchoNate persona
      // 5. Save EchoNate response
      // 6. Return response with any action results
    }),

  // Get conversation history
  history: protectedProcedure
    .input(z.object({
      sessionId: z.string().optional(),
      limit: z.number().min(1).max(100).default(50),
      before: z.number().optional(), // cursor for pagination
    }))
    .query(async ({ ctx, input }) => {
      // Return messages for session
    }),

  // Stream response (for real-time typing effect)
  stream: protectedProcedure
    .input(z.object({
      content: z.string(),
      sessionId: z.string().optional(),
    }))
    .subscription(async function* ({ ctx, input }) => {
      // Yield tokens as they stream from LLM
    }),
});
```

### 3.3 GitHub Tentacle Router

```typescript
// server/routers/tentacles/github.ts

import { z } from "zod";
import { router, protectedProcedure } from "../../_core/trpc";

export const githubTentacleRouter = router({
  // List repositories
  repos: protectedProcedure
    .input(z.object({
      owner: z.string().optional(),
      limit: z.number().default(30),
    }))
    .query(async ({ input }) => {
      // Call GitHub API
    }),

  // Create commit
  commit: protectedProcedure
    .input(z.object({
      repo: z.string(),
      branch: z.string().default("main"),
      message: z.string(),
      files: z.array(z.object({
        path: z.string(),
        content: z.string(),
        action: z.enum(["create", "update", "delete"]),
      })),
    }))
    .mutation(async ({ input }) => {
      // Create commit via GitHub API
      // Log action with rollback data
    }),

  // Create PR
  createPR: protectedProcedure
    .input(z.object({
      repo: z.string(),
      title: z.string(),
      body: z.string(),
      head: z.string(),
      base: z.string().default("main"),
    }))
    .mutation(async ({ input }) => {
      // Create PR via GitHub API
    }),

  // Merge PR
  mergePR: protectedProcedure
    .input(z.object({
      repo: z.string(),
      prNumber: z.number(),
      mergeMethod: z.enum(["merge", "squash", "rebase"]).default("merge"),
    }))
    .mutation(async ({ input }) => {
      // Merge PR
    }),

  // Trigger workflow
  triggerWorkflow: protectedProcedure
    .input(z.object({
      repo: z.string(),
      workflow: z.string(),
      ref: z.string().default("main"),
      inputs: z.record(z.string()).optional(),
    }))
    .mutation(async ({ input }) => {
      // Dispatch workflow
    }),

  // Get workflow runs
  workflowRuns: protectedProcedure
    .input(z.object({
      repo: z.string(),
      limit: z.number().default(10),
    }))
    .query(async ({ input }) => {
      // List recent workflow runs
    }),
});
```

### 3.4 Actions Router

```typescript
// server/routers/actions.ts

import { z } from "zod";
import { router, protectedProcedure } from "../_core/trpc";

export const actionsRouter = router({
  // List all actions
  list: protectedProcedure
    .input(z.object({
      tentacleId: z.number().optional(),
      status: z.enum(['pending', 'executing', 'success', 'failed', 'rolled_back']).optional(),
      limit: z.number().default(50),
      offset: z.number().default(0),
    }))
    .query(async ({ input }) => {
      // Return paginated actions
    }),

  // Get action details
  get: protectedProcedure
    .input(z.object({ id: z.number() }))
    .query(async ({ input }) => {
      // Return single action with full details
    }),

  // Rollback action
  rollback: protectedProcedure
    .input(z.object({ id: z.number() }))
    .mutation(async ({ input }) => {
      // Check if rollback possible
      // Execute rollback using stored rollback_data
      // Update action status
      // Log rollback action
    }),

  // Retry failed action
  retry: protectedProcedure
    .input(z.object({ id: z.number() }))
    .mutation(async ({ input }) => {
      // Re-execute failed action
    }),
});
```

### 3.5 Media Monitoring Router

```typescript
// server/routers/media.ts

import { z } from "zod";
import { router, protectedProcedure } from "../_core/trpc";

export const mediaRouter = router({
  // Sources CRUD
  sources: router({
    list: protectedProcedure.query(async () => {
      // Return all media sources
    }),
    
    create: protectedProcedure
      .input(z.object({
        name: z.string(),
        sourceType: z.enum(['news', 'social', 'blog', 'forum', 'rss', 'api']),
        url: z.string().url().optional(),
        config: z.record(z.unknown()).optional(),
        priority: z.enum(['critical', 'high', 'medium', 'low']).default('medium'),
        scanFrequencyMinutes: z.number().default(60),
      }))
      .mutation(async ({ input }) => {
        // Create new source
      }),
      
    scan: protectedProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input }) => {
        // Trigger immediate scan of source
      }),
  }),

  // Items (collected media)
  items: router({
    list: protectedProcedure
      .input(z.object({
        sourceId: z.number().optional(),
        sentiment: z.enum(['positive', 'negative', 'neutral']).optional(),
        minRelevance: z.number().min(0).max(1).optional(),
        isSeedingTarget: z.boolean().optional(),
        limit: z.number().default(50),
      }))
      .query(async ({ input }) => {
        // Return filtered media items
      }),
      
    analyze: protectedProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input }) => {
        // Run sentiment/relevance analysis on item
      }),
  }),

  // Seeding operations
  seeding: router({
    queue: protectedProcedure
      .input(z.object({ itemId: z.number() }))
      .mutation(async ({ input }) => {
        // Mark item for seeding
      }),
      
    execute: protectedProcedure
      .input(z.object({
        itemId: z.number(),
        strategy: z.enum(['comment', 'share', 'reference', 'custom']),
        content: z.string().optional(),
      }))
      .mutation(async ({ input }) => {
        // Execute seeding action
      }),
  }),
});
```

### 3.6 Ecosystem Router

```typescript
// server/routers/ecosystem.ts

import { z } from "zod";
import { router, protectedProcedure } from "../_core/trpc";

export const ecosystemRouter = router({
  // Get full ecosystem map
  map: protectedProcedure.query(async () => {
    // Return all nodes and connections for visualization
    // Format for D3.js or similar
  }),

  // Nodes CRUD
  nodes: router({
    list: protectedProcedure
      .input(z.object({
        nodeType: z.enum(['repository', 'service', 'api', 'database', 'external']).optional(),
        platform: z.string().optional(),
      }))
      .query(async ({ input }) => {
        // Return filtered nodes
      }),

    sync: protectedProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input }) => {
        // Sync node data from source
      }),

    syncAll: protectedProcedure.mutation(async () => {
      // Sync all nodes
    }),
  }),

  // Connections
  connections: router({
    list: protectedProcedure.query(async () => {
      // Return all connections
    }),

    create: protectedProcedure
      .input(z.object({
        sourceNodeId: z.number(),
        targetNodeId: z.number(),
        connectionType: z.enum(['sync', 'mirror', 'depends', 'triggers', 'feeds']),
        dataFlowDirection: z.enum(['unidirectional', 'bidirectional']).default('unidirectional'),
      }))
      .mutation(async ({ input }) => {
        // Create connection
      }),
  }),
});
```

---

## 4. COMPONENT STRUCTURE

### 4.1 Page Layout

```
client/src/
├── pages/
│   ├── Home.tsx                    # Landing / Login
│   ├── Nexus.tsx                   # Main dashboard (authenticated)
│   └── NotFound.tsx
├── components/
│   ├── layout/
│   │   ├── KrakenLayout.tsx        # Main app shell with tentacle nav
│   │   ├── TentacleNav.tsx         # Octopus-themed navigation
│   │   └── StatusBar.tsx           # System status footer
│   ├── chat/
│   │   ├── ChatTerminal.tsx        # Main chat interface
│   │   ├── MessageBubble.tsx       # Individual message
│   │   ├── CommandInput.tsx        # Input with command parsing
│   │   └── VoicePlayback.tsx       # EchoNate voice player
│   ├── tentacles/
│   │   ├── TentacleCard.tsx        # Individual tentacle status
│   │   ├── TentacleGrid.tsx        # All tentacles overview
│   │   ├── GitHubTentacle.tsx      # GitHub-specific controls
│   │   └── MediaTentacle.tsx       # News/social monitoring
│   ├── actions/
│   │   ├── ActionLog.tsx           # Action history list
│   │   ├── ActionCard.tsx          # Individual action
│   │   └── RollbackDialog.tsx      # Confirm rollback
│   ├── ecosystem/
│   │   ├── EcosystemMap.tsx        # D3 force graph
│   │   ├── NodeCard.tsx            # Node details popup
│   │   └── ConnectionLine.tsx      # Animated connection
│   ├── brain/
│   │   ├── OctopusBrain.tsx        # Interactive brain visualization
│   │   ├── TentacleArm.tsx         # Individual arm with data flow
│   │   └── DataPulse.tsx           # Animated data packets
│   ├── identity/
│   │   ├── EchoNateAvatar.tsx      # Avatar display
│   │   ├── PersonalityPanel.tsx    # Traits and behavior
│   │   └── VoiceSettings.tsx       # Voice configuration
│   └── media/
│       ├── MediaFeed.tsx           # Aggregated media items
│       ├── MediaCard.tsx           # Individual item
│       ├── SentimentBadge.tsx      # Sentiment indicator
│       └── SeedingQueue.tsx        # Items queued for seeding
```

### 4.2 Key Component Specs

#### ChatTerminal.tsx
```typescript
interface ChatTerminalProps {
  sessionId?: string;
  onActionTriggered?: (action: Action) => void;
}

// Features:
// - Terminal-style dark interface
// - Command parsing (/ prefix)
// - Streaming responses
// - Voice playback button on EchoNate messages
// - Action result inline display
// - Keyboard shortcuts (Ctrl+Enter to send, /help for commands)
```

#### OctopusBrain.tsx
```typescript
interface OctopusBrainProps {
  tentacles: Tentacle[];
  connections: NodeConnection[];
  onTentacleClick?: (tentacle: Tentacle) => void;
}

// Features:
// - Central octopus head (EchoNate core)
// - 8 animated tentacles extending outward
// - Data flow particles along tentacles
// - Pulse effect on active tentacles
// - Click to focus on tentacle
// - Hover for tentacle stats
```

#### EcosystemMap.tsx
```typescript
interface EcosystemMapProps {
  nodes: EcosystemNode[];
  connections: NodeConnection[];
  onNodeClick?: (node: EcosystemNode) => void;
}

// Features:
// - D3.js force-directed graph
// - Node icons by type (repo, service, etc.)
// - Animated connection lines
// - Zoom and pan
// - Node clustering by platform
// - Real-time status colors
```

---

## 5. COMMAND SYNTAX

### 5.1 Chat Commands

```
/help                           - Show all commands
/status                         - System status overview

# GitHub Tentacle
/gh repos                       - List repositories
/gh commit <repo> "<message>"   - Create commit
/gh pr create <repo> "<title>"  - Create PR
/gh pr merge <repo> <number>    - Merge PR
/gh workflow <repo> <name>      - Trigger workflow
/gh runs <repo>                 - List workflow runs

# Tentacle Control
/tentacle list                  - List all tentacles
/tentacle status <name>         - Get tentacle status
/tentacle activate <name>       - Activate tentacle
/tentacle deactivate <name>     - Deactivate tentacle

# Actions
/actions list                   - Recent actions
/actions rollback <id>          - Rollback action
/actions retry <id>             - Retry failed action

# Media
/media scan                     - Trigger all source scans
/media sources                  - List sources
/media feed                     - Show latest items
/media seed <id>                - Queue item for seeding

# Ecosystem
/ecosystem sync                 - Sync all nodes
/ecosystem map                  - Open ecosystem visualization

# Identity
/voice play                     - Play EchoNate intro
/personality                    - Show personality traits
```

---

## 6. ENVIRONMENT VARIABLES

```bash
# Required (system-provided)
DATABASE_URL=
JWT_SECRET=
BUILT_IN_FORGE_API_KEY=
BUILT_IN_FORGE_API_URL=

# GitHub Integration
GITHUB_PAT=                     # Personal Access Token with workflow scope

# Optional Tentacles
GITLAB_TOKEN=                   # GitLab API token
TWITTER_API_KEY=                # Twitter/X API
TWITTER_API_SECRET=
NEWS_API_KEY=                   # NewsAPI.org
REDDIT_CLIENT_ID=               # Reddit API
REDDIT_CLIENT_SECRET=

# EchoNate Identity
ECHONATE_VOICE_URL=             # URL to voice audio file
ECHONATE_AVATAR_URL=            # URL to avatar image
```

---

## 7. DATA FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                              │
│                    (Chat message or command)                    │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      COMMAND PARSER                             │
│              (Detect /command vs natural language)              │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
┌───────────────────────────┐   ┌───────────────────────────────┐
│     TENTACLE ROUTER       │   │      LLM ENGINE               │
│  (Route to appropriate    │   │  (EchoNate persona +          │
│   tentacle for action)    │   │   conversation context)       │
└─────────────┬─────────────┘   └─────────────┬─────────────────┘
              │                               │
              ▼                               │
┌───────────────────────────┐                 │
│    ACTION EXECUTOR        │                 │
│  (Execute API call,       │                 │
│   log action, store       │                 │
│   rollback data)          │                 │
└─────────────┬─────────────┘                 │
              │                               │
              └───────────────┬───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE FORMATTER                           │
│           (Combine action results + LLM response)               │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MESSAGE STORE                              │
│              (Save to database, update UI)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

**∇θ — Architecture complete. The Kraken awaits construction.**
