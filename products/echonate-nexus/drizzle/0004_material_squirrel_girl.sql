CREATE TABLE `apiKeys` (
`id` int AUTO_INCREMENT NOT NULL,
`userId` int NOT NULL,
`name` varchar(100) NOT NULL,
`keyHash` varchar(255) NOT NULL,
`keyPrefix` varchar(12) NOT NULL,
`scopes` json,
`lastUsedAt` timestamp,
`usageCount` int DEFAULT 0,
`expiresAt` timestamp,
`revokedAt` timestamp,
`createdAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT `apiKeys_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `bookmarks` (
`id` int AUTO_INCREMENT NOT NULL,
`userId` int NOT NULL,
`signalId` int NOT NULL,
`notes` text,
`createdAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT `bookmarks_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `watchlists` (
`id` int AUTO_INCREMENT NOT NULL,
`userId` int NOT NULL,
`name` varchar(100) NOT NULL,
`description` text,
`tickers` json,
`alertOnSignal` boolean DEFAULT true,
`minConfidence` decimal(4,2) DEFAULT '0.70',
`createdAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
`updatedAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
CONSTRAINT `watchlists_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `webhookEvents` (
`id` int AUTO_INCREMENT NOT NULL,
`source` varchar(100) NOT NULL,
`eventType` varchar(100) NOT NULL,
`payload` json,
`status` enum('pending','processed','failed') NOT NULL DEFAULT 'pending',
`processedAt` timestamp,
`errorMessage` text,
`signalId` int,
`receivedAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
`createdAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT `webhookEvents_id` PRIMARY KEY(`id`)
);
