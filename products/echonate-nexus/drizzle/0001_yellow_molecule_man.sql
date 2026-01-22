CREATE TABLE `alertLogs` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int NOT NULL,
	`signalId` int NOT NULL,
	`deliveryMethod` enum('email','api','webhook') NOT NULL,
	`deliveredAt` timestamp NOT NULL DEFAULT (now()),
	`status` enum('sent','failed','bounced') DEFAULT 'sent',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `alertLogs_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `alertPreferences` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int NOT NULL,
	`enableSeismic` boolean DEFAULT true,
	`enableHealth` boolean DEFAULT true,
	`enableSentiment` boolean DEFAULT true,
	`enableSolar` boolean DEFAULT true,
	`enableForex` boolean DEFAULT true,
	`enableCrypto` boolean DEFAULT true,
	`enableGeopolitical` boolean DEFAULT true,
	`minConfidence` decimal(4,2) DEFAULT '0.60',
	`emailEnabled` boolean DEFAULT true,
	`emailAddress` varchar(320),
	`digestFrequency` enum('instant','hourly','daily') DEFAULT 'instant',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `alertPreferences_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `apiUsage` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int NOT NULL,
	`endpoint` varchar(255) NOT NULL,
	`method` varchar(10) NOT NULL,
	`calledAt` timestamp NOT NULL DEFAULT (now()),
	`responseTime` int,
	`statusCode` int,
	CONSTRAINT `apiUsage_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `signals` (
	`id` int AUTO_INCREMENT NOT NULL,
	`signalType` enum('seismic','health','sentiment','solar','forex','crypto','geopolitical') NOT NULL,
	`source` varchar(100) NOT NULL,
	`sourceUrl` text,
	`targetTicker` varchar(20),
	`targetSector` varchar(100),
	`direction` enum('bullish','bearish','neutral') NOT NULL,
	`strength` decimal(4,2) NOT NULL,
	`confidence` decimal(4,2) NOT NULL,
	`title` varchar(255) NOT NULL,
	`summary` text NOT NULL,
	`rationale` text NOT NULL,
	`rawData` json,
	`detectedAt` timestamp NOT NULL DEFAULT (now()),
	`expiresAt` timestamp,
	`actualOutcome` enum('correct','incorrect','pending') DEFAULT 'pending',
	`actualReturn` decimal(8,4),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `signals_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `subscriptions` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int NOT NULL,
	`tier` enum('free','pro','enterprise') NOT NULL DEFAULT 'free',
	`stripeCustomerId` varchar(255),
	`stripeSubscriptionId` varchar(255),
	`status` enum('active','canceled','past_due','trialing') NOT NULL DEFAULT 'active',
	`currentPeriodStart` timestamp,
	`currentPeriodEnd` timestamp,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `subscriptions_id` PRIMARY KEY(`id`)
);
