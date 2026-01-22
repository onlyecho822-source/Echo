CREATE TABLE `signalAccuracy` (
	`id` int AUTO_INCREMENT NOT NULL,
	`signalType` enum('seismic','health','sentiment','solar','forex','crypto','geopolitical') NOT NULL,
	`priorAlpha` decimal(10,4) DEFAULT '1.0000',
	`priorBeta` decimal(10,4) DEFAULT '1.0000',
	`totalSignals` int DEFAULT 0,
	`correctSignals` int DEFAULT 0,
	`incorrectSignals` int DEFAULT 0,
	`pendingSignals` int DEFAULT 0,
	`currentAccuracy` decimal(5,4) DEFAULT '0.5000',
	`rolling30dCorrect` int DEFAULT 0,
	`rolling30dTotal` int DEFAULT 0,
	`rolling30dAccuracy` decimal(5,4) DEFAULT '0.5000',
	`confidenceLower` decimal(5,4) DEFAULT '0.0250',
	`confidenceUpper` decimal(5,4) DEFAULT '0.9750',
	`lastUpdated` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `signalAccuracy_id` PRIMARY KEY(`id`),
	CONSTRAINT `signalAccuracy_signalType_unique` UNIQUE(`signalType`)
);
--> statement-breakpoint
CREATE TABLE `signalValidations` (
	`id` int AUTO_INCREMENT NOT NULL,
	`signalId` int NOT NULL,
	`validatedAt` timestamp NOT NULL DEFAULT (now()),
	`outcome` enum('correct','incorrect','expired') NOT NULL,
	`priceAtSignal` decimal(12,4),
	`priceAtValidation` decimal(12,4),
	`actualReturn` decimal(8,4),
	`validationMethod` enum('auto','manual') DEFAULT 'auto',
	`notes` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `signalValidations_id` PRIMARY KEY(`id`)
);
