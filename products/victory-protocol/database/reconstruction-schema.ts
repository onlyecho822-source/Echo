// Military Service Reconstruction Database Schema
// Add to existing drizzle/schema.ts

import { mysqlTable, varchar, int, timestamp, json, text, mysqlEnum } from 'drizzle-orm/mysql-core';

// ============================================================================
// MAIN RECONSTRUCTION RECORD
// ============================================================================

export const serviceReconstruction = mysqlTable("serviceReconstruction", {
  id: varchar("id", { length: 64 }).primaryKey(),
  userId: varchar("userId", { length: 64 }).notNull(),
  
  // Service Metadata (extracted from DD214)
  branch: mysqlEnum("branch", ["Army", "Navy", "Air Force", "Marines", "Coast Guard", "Space Force"]),
  serviceNumber: varchar("serviceNumber", { length: 50 }), // Old service numbers pre-SSN
  rank: varchar("rank", { length: 50 }),
  mos: varchar("mos", { length: 20 }), // Primary MOS
  allMOS: json("allMOS").$type<string[]>(), // All MOS held during service
  
  serviceDates: json("serviceDates").$type<{
    enlistment: string,
    separation: string,
    activeYears: number,
    reserveYears: number
  }>(),
  
  characterOfService: varchar("characterOfService", { length: 50 }), // Honorable, General, etc.
  
  // Completion Tracking
  totalDocuments: int("totalDocuments").default(0),
  uploadedDocuments: int("uploadedDocuments").default(0),
  missingDocuments: int("missingDocuments").default(0),
  requestedDocuments: int("requestedDocuments").default(0),
  verifiedDocuments: int("verifiedDocuments").default(0),
  completionPercentage: int("completionPercentage").default(0),
  
  // Readiness Flags
  readyForAIProcessing: int("readyForAIProcessing").default(0), // boolean
  minimumThresholdMet: int("minimumThresholdMet").default(0), // 80%+ complete
  
  // Timestamps
  createdAt: timestamp("createdAt").defaultNow(),
  updatedAt: timestamp("updatedAt").defaultNow()
});

// ============================================================================
// CHECKLIST CATEGORIES
// ============================================================================

export const checklistCategories = mysqlTable("checklistCategories", {
  id: varchar("id", { length: 64 }).primaryKey(),
  reconstructionId: varchar("reconstructionId", { length: 64 }).notNull(),
  
  categoryName: varchar("categoryName", { length: 100 }),
  categoryType: mysqlEnum("categoryType", [
    "enlistment",
    "basic_training",
    "ait",
    "specialized_schools",
    "duty_stations",
    "deployments",
    "special_assignments",
    "awards_decorations",
    "medical_records",
    "disciplinary",
    "administrative",
    "separation",
    "maps_geographic",
    "unit_history"
  ]),
  
  description: text("description"),
  priority: mysqlEnum("priority", ["critical", "high", "medium", "low"]).default("medium"),
  
  // Completion Stats
  totalItems: int("totalItems").default(0),
  completedItems: int("completedItems").default(0),
  missingItems: int("missingItems").default(0),
  completionPercentage: int("completionPercentage").default(0),
  
  // Display Order
  displayOrder: int("displayOrder").default(0),
  
  createdAt: timestamp("createdAt").defaultNow(),
  updatedAt: timestamp("updatedAt").defaultNow()
});

// ============================================================================
// CHECKLIST ITEMS (200+ documents)
// ============================================================================

export const checklistItems = mysqlTable("checklistItems", {
  id: varchar("id", { length: 64 }).primaryKey(),
  categoryId: varchar("categoryId", { length: 64 }).notNull(),
  
  // Document Details
  documentName: varchar("documentName", { length: 200 }),
  documentType: varchar("documentType", { length: 100 }),
  description: text("description"),
  
  // Status Tracking
  status: mysqlEnum("status", [
    "missing",
    "uploaded",
    "requested",
    "processing",
    "verified",
    "auto_generated"
  ]).default("missing"),
  
  // Acquisition Info
  source: varchar("source", { length: 200 }), // "NARA", "Personal Files", "Unit S-1", "VA Blue Button"
  acquisitionMethod: mysqlEnum("acquisitionMethod", [
    "veteran_upload",
    "nara_request",
    "unit_request",
    "va_download",
    "auto_generated",
    "manual_entry"
  ]),
  
  // Link to Actual File
  fileId: varchar("fileId", { length: 64 }), // Links to profileDocuments or evidence table
  s3Path: varchar("s3Path", { length: 500 }),
  
  // Priority and Requirements
  priority: mysqlEnum("priority", ["critical", "high", "medium", "low"]).default("medium"),
  required: int("required").default(0), // boolean - can we launch without this?
  
  // Request Tracking
  requestedDate: timestamp("requestedDate"),
  expectedDate: timestamp("expectedDate"),
  receivedDate: timestamp("receivedDate"),
  verifiedDate: timestamp("verifiedDate"),
  
  // Notes
  notes: text("notes"),
  
  createdAt: timestamp("createdAt").defaultNow(),
  updatedAt: timestamp("updatedAt").defaultNow()
});

// ============================================================================
// DUTY STATIONS (One per permanent station)
// ============================================================================

export const dutyStationRecords = mysqlTable("dutyStationRecords", {
  id: varchar("id", { length: 64 }).primaryKey(),
  reconstructionId: varchar("reconstructionId", { length: 64 }).notNull(),
  
  // Station Info
  stationName: varchar("stationName", { length: 200 }), // "Fort Bragg", "Camp Lejeune"
  baseName: varchar("baseName", { length: 200 }),
  
  location: json("location").$type<{
    address: string,
    city: string,
    state: string,
    country: string,
    lat: number,
    long: number
  }>(),
  
  dates: json("dates").$type<{
    arrival: string,
    departure: string,
    durationDays: number
  }>(),
  
  // Assignment Details
  unit: varchar("unit", { length: 200 }), // "3rd Battalion, 7th Infantry Regiment"
  commandLevel: varchar("commandLevel", { length: 100 }), // Company, Battalion, Brigade
  mos: varchar("mos", { length: 20 }), // MOS at this station
  rank: varchar("rank", { length: 50 }), // Rank at this station
  
  // Hazard Exposure Data
  hazardExposures: json("hazardExposures").$type<Array<{
    type: string, // "burn_pit", "agent_orange", "asbestos", "radiation"
    source: string,
    distance: number, // meters
    exposureDays: number,
    severity: "low" | "medium" | "high",
    presumptive: boolean, // VA presumptive condition?
    pactActCovered: boolean
  }>>(),
  
  // Environmental Conditions
  environmentalFactors: json("environmentalFactors").$type<{
    climate: string,
    terrain: string,
    livingConditions: string[],
    specialHazards: string[]
  }>(),
  
  // Documents Specific to This Station
  documentsNeeded: json("documentsNeeded").$type<string[]>(),
  documentsObtained: json("documentsObtained").$type<string[]>(),
  
  // Completion
  completionPercentage: int("completionPercentage").default(0),
  
  createdAt: timestamp("createdAt").defaultNow(),
  updatedAt: timestamp("updatedAt").defaultNow()
});

// ============================================================================
// DEPLOYMENTS
// ============================================================================

export const deploymentRecords = mysqlTable("deploymentRecords", {
  id: varchar("id", { length: 64 }).primaryKey(),
  reconstructionId: varchar("reconstructionId", { length: 64 }).notNull(),
  
  // Deployment Details
  operationName: varchar("operationName", { length: 200 }), // "Operation Desert Storm", "OEF", "OIF"
  theater: varchar("theater", { length: 100 }), // "Iraq", "Afghanistan", "Kuwait"
  
  location: json("location").$type<{
    country: string,
    region: string,
    baseOrFOB: string,
    lat: number,
    long: number
  }>(),
  
  dates: json("dates").$type<{
    deployment: string,
    redeployment: string,
    durationDays: number,
    combatDays: number
  }>(),
  
  // Combat Details
  combatIntensity: mysqlEnum("combatIntensity", ["none", "low", "medium", "high", "extreme"]),
  combatOperations: json("combatOperations").$type<Array<{
    operation: string,
    date: string,
    description: string
  }>>(),
  
  // Unit Info During Deployment
  unit: varchar("unit", { length: 200 }),
  role: varchar("role", { length: 200 }),
  
  // Hazard Exposures
  hazardExposures: json("hazardExposures").$type<Array<{
    type: string,
    source: string,
    proximity: number,
    duration: number,
    severity: string,
    presumptive: boolean
  }>>(),
  
  // Medical/Mental Health
  fieldMedicalTreatment: json("fieldMedicalTreatment").$type<Array<{
    date: string,
    condition: string,
    provider: string
  }>>(),
  
  combatStressEvents: json("combatStressEvents").$type<Array<{
    date: string,
    type: string,
    description: string
  }>>(),
  
  // Awards from Deployment
  awardsReceived: json("awardsReceived").$type<string[]>(),
  
  // Pre/Post Deployment Health
  pdha: int("pdha").default(0), // Post-Deployment Health Assessment completed
  pdhra: int("pdhra").default(0), // Post-Deployment Health Reassessment completed
  
  // Documents
  documentsNeeded: json("documentsNeeded").$type<string[]>(),
  documentsObtained: json("documentsObtained").$type<string[]>(),
  completionPercentage: int("completionPercentage").default(0),
  
  createdAt: timestamp("createdAt").defaultNow(),
  updatedAt: timestamp("updatedAt").defaultNow()
});

// ============================================================================
// TRAINING RECORDS
// ============================================================================

export const trainingRecords = mysqlTable("trainingRecords", {
  id: varchar("id", { length: 64 }).primaryKey(),
  reconstructionId: varchar("reconstructionId", { length: 64 }).notNull(),
  
  // Training Details
  trainingType: mysqlEnum("trainingType", [
    "basic_training",
    "ait",
    "leadership_course",
    "specialized_school",
    "certification",
    "deployment_training"
  ]),
  
  courseName: varchar("courseName", { length: 200 }),
  schoolName: varchar("schoolName", { length: 200 }),
  location: varchar("location", { length: 200 }),
  
  dates: json("dates").$type<{
    start: string,
    end: string,
    durationWeeks: number
  }>(),
  
  // Course Details
  curriculum: text("curriculum"),
  physicalDemands: mysqlEnum("physicalDemands", ["low", "moderate", "high", "extreme"]),
  
  // Hazards Associated with Training
  trainingHazards: json("trainingHazards").$type<Array<{
    type: string,
    description: string,
    injuryRisk: string
  }>>(),
  
  // Completion Status
  graduated: int("graduated").default(1),
  certificateIssued: int("certificateIssued").default(0),
  skillsQualified: json("skillsQualified").$type<string[]>(),
  
  // Documents
  documentIds: json("documentIds").$type<string[]>(),
  
  createdAt: timestamp("createdAt").defaultNow()
});

// ============================================================================
// NARA REQUESTS (FOIA for records)
// ============================================================================

export const naraRequests = mysqlTable("naraRequests", {
  id: varchar("id", { length: 64 }).primaryKey(),
  userId: varchar("userId", { length: 64 }).notNull(),
  reconstructionId: varchar("reconstructionId", { length: 64 }),
  
  // Request Type
  requestType: mysqlEnum("requestType", [
    "ompf_full",
    "ompf_partial",
    "unit_records",
    "medical_records",
    "training_records"
  ]),
  
  requestedDocuments: json("requestedDocuments").$type<string[]>(),
  
  // Generated Forms
  sf180Form: varchar("sf180Form", { length: 500 }), // S3 path to generated SF-180
  coverLetter: varchar("coverLetter", { length: 500 }), // S3 path to cover letter
  
  // Status Tracking
  status: mysqlEnum("status", [
    "draft",
    "ready_to_submit",
    "submitted",
    "pending_review",
    "in_progress",
    "received",
    "denied",
    "cancelled"
  ]).default("draft"),
  
  // Dates
  submittedDate: timestamp("submittedDate"),
  expectedResponseDate: timestamp("expectedResponseDate"), // Usually 90-120 days
  receivedDate: timestamp("receivedDate"),
  
  // Tracking
  trackingNumber: varchar("trackingNumber", { length: 100 }),
  naraContactInfo: json("naraContactInfo").$type<{
    office: string,
    address: string,
    phone: string,
    fax: string
  }>(),
  
  // Response
  responseReceived: int("responseReceived").default(0),
  documentsReceived: json("documentsReceived").$type<string[]>(),
  denialReason: text("denialReason"),
  
  // Follow-up
  followUpRequired: int("followUpRequired").default(0),
  followUpDate: timestamp("followUpDate"),
  
  createdAt: timestamp("createdAt").defaultNow(),
  updatedAt: timestamp("updatedAt").defaultNow()
});

// ============================================================================
// HAZARD EXPOSURE MASTER DATABASE
// ============================================================================

export const hazardExposureDatabase = mysqlTable("hazardExposureDatabase", {
  id: varchar("id", { length: 64 }).primaryKey(),
  
  // Hazard Type
  hazardType: mysqlEnum("hazardType", [
    "burn_pit",
    "agent_orange",
    "contaminated_water",
    "radiation",
    "asbestos",
    "lead",
    "depleted_uranium",
    "chemical_weapons",
    "noise",
    "particulate_matter"
  ]),
  
  // Location
  locationName: varchar("locationName", { length: 200 }),
  baseName: varchar("baseName", { length: 200 }),
  country: varchar("country", { length: 100 }),
  
  coordinates: json("coordinates").$type<{
    lat: number,
    long: number
  }>(),
  
  // Time Period
  activePeriod: json("activePeriod").$type<{
    start: string,
    end: string
  }>(),
  
  // Hazard Details
  description: text("description"),
  severity: mysqlEnum("severity", ["low", "moderate", "high", "extreme"]),
  
  // VA Recognition
  presumptiveCondition: int("presumptiveCondition").default(0), // VA recognizes this
  pactActCovered: int("pactActCovered").default(0),
  agentOrangeList: int("agentOrangeList").default(0),
  
  // Associated Conditions
  knownConditions: json("knownConditions").$type<string[]>(), // Medical conditions linked to this hazard
  
  // Source Documentation
  sourceDocuments: json("sourceDocuments").$type<Array<{
    type: string,
    url: string,
    title: string
  }>>(),
  
  createdAt: timestamp("createdAt").defaultNow(),
  updatedAt: timestamp("updatedAt").defaultNow()
});

// ============================================================================
// MOS HAZARD MAPPING
// ============================================================================

export const mosHazardMapping = mysqlTable("mosHazardMapping", {
  id: varchar("id", { length: 64 }).primaryKey(),
  
  // MOS Details
  branch: mysqlEnum("branch", ["Army", "Navy", "Air Force", "Marines", "Coast Guard", "Space Force"]),
  mosCode: varchar("mosCode", { length: 20 }),
  mosTitle: varchar("mosTitle", { length: 200 }),
  
  // Occupational Hazards
  physicalDemands: json("physicalDemands").$type<{
    heavyLifting: boolean,
    repetitiveMotion: boolean,
    awkwardPositions: boolean,
    prolongedStanding: boolean,
    description: string
  }>(),
  
  noiseExposure: json("noiseExposure").$type<{
    level: "low" | "moderate" | "high" | "extreme",
    sources: string[],
    duration: string
  }>(),
  
  chemicalExposure: json("chemicalExposure").$type<{
    chemicals: string[],
    exposureLevel: string
  }>(),
  
  injuryRisks: json("injuryRisks").$type<Array<{
    condition: string,
    likelihood: string,
    mechanism: string
  }>>(),
  
  // Common Conditions
  commonServiceConnectedConditions: json("commonServiceConnectedConditions").$type<string[]>(),
  
  createdAt: timestamp("createdAt").defaultNow()
});
