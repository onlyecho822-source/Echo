// Service Reconstruction Backend Router
// Add to server/routers.ts

import { router, protectedProcedure } from './trpc';
import { z } from 'zod';
import { eq, and, desc } from 'drizzle-orm';
import { 
  serviceReconstruction,
  checklistCategories,
  checklistItems,
  dutyStationRecords,
  deploymentRecords,
  trainingRecords,
  naraRequests,
  hazardExposureDatabase,
  mosHazardMapping
} from '../db/schema';
import { generateId } from '../_core/utils';
import { extractDD214Data, generatePersonalizedChecklist } from '../_core/reconstruction';

export const reconstructionRouter = router({
  
  // ============================================================================
  // INITIALIZATION - Create reconstruction from DD214
  // ============================================================================
  
  initialize: protectedProcedure
    .input(z.object({
      dd214FileId: z.string()
    }))
    .mutation(async ({ ctx, input }) => {
      // Extract service data from DD214
      const dd214 = await extractDD214Data(input.dd214FileId);
      
      // Create main reconstruction record
      const reconstruction = await ctx.db.insert(serviceReconstruction).values({
        id: generateId(),
        userId: ctx.user.id,
        branch: dd214.branch,
        serviceNumber: dd214.serviceNumber,
        rank: dd214.finalRank,
        mos: dd214.primaryMOS,
        allMOS: dd214.allMOS,
        serviceDates: {
          enlistment: dd214.enlistmentDate,
          separation: dd214.separationDate,
          activeYears: dd214.activeYears,
          reserveYears: dd214.reserveYears
        },
        characterOfService: dd214.characterOfService
      });
      
      // Generate personalized checklist based on service
      const checklist = await generatePersonalizedChecklist({
        branch: dd214.branch,
        serviceDates: dd214.serviceDates,
        mos: dd214.allMOS,
        deployments: dd214.deploymentIndicators,
        specializations: dd214.specializations
      });
      
      // Create categories and items
      for (const category of checklist.categories) {
        const cat = await ctx.db.insert(checklistCategories).values({
          id: generateId(),
          reconstructionId: reconstruction.id,
          categoryName: category.name,
          categoryType: category.type,
          description: category.description,
          priority: category.priority,
          totalItems: category.items.length,
          displayOrder: category.order
        });
        
        for (const item of category.items) {
          await ctx.db.insert(checklistItems).values({
            id: generateId(),
            categoryId: cat.id,
            documentName: item.name,
            documentType: item.type,
            description: item.description,
            source: item.source,
            priority: item.priority,
            required: item.required ? 1 : 0
          });
        }
      }
      
      // Extract duty stations from DD214
      if (dd214.dutyStations && dd214.dutyStations.length > 0) {
        for (const station of dd214.dutyStations) {
          await ctx.db.insert(dutyStationRecords).values({
            id: generateId(),
            reconstructionId: reconstruction.id,
            stationName: station.name,
            baseName: station.baseName,
            location: station.location,
            dates: station.dates,
            unit: station.unit,
            mos: station.mos,
            rank: station.rank
          });
        }
      }
      
      return {
        reconstructionId: reconstruction.id,
        totalDocuments: checklist.totalItems,
        categories: checklist.categories.length
      };
    }),
  
  // ============================================================================
  // GET FULL CHECKLIST WITH PROGRESS
  // ============================================================================
  
  getChecklist: protectedProcedure
    .query(async ({ ctx }) => {
      const reconstruction = await ctx.db.query.serviceReconstruction.findFirst({
        where: eq(serviceReconstruction.userId, ctx.user.id),
        with: {
          categories: {
            with: {
              items: true
            },
            orderBy: [asc(checklistCategories.displayOrder)]
          },
          dutyStations: true,
          deployments: true,
          trainings: true
        }
      });
      
      if (!reconstruction) {
        throw new Error('No reconstruction found. Please initialize first.');
      }
      
      return reconstruction;
    }),
  
  // ============================================================================
  // UPDATE ITEM STATUS (when veteran uploads document)
  // ============================================================================
  
  updateItem: protectedProcedure
    .input(z.object({
      itemId: z.string(),
      status: z.enum(["missing", "uploaded", "requested", "processing", "verified", "auto_generated"]),
      fileId: z.string().optional(),
      s3Path: z.string().optional(),
      notes: z.string().optional()
    }))
    .mutation(async ({ ctx, input }) => {
      // Update the item
      await ctx.db.update(checklistItems)
        .set({
          status: input.status,
          fileId: input.fileId,
          s3Path: input.s3Path,
          notes: input.notes,
          receivedDate: input.status === "uploaded" ? new Date() : undefined,
          verifiedDate: input.status === "verified" ? new Date() : undefined,
          updatedAt: new Date()
        })
        .where(eq(checklistItems.id, input.itemId));
      
      // Recalculate completion percentages
      await updateCompletionPercentages(ctx.db, input.itemId);
      
      return { success: true };
    }),
  
  // ============================================================================
  // BULK UPDATE (mark multiple items at once)
  // ============================================================================
  
  bulkUpdateItems: protectedProcedure
    .input(z.object({
      itemIds: z.array(z.string()),
      status: z.enum(["missing", "uploaded", "requested", "verified"])
    }))
    .mutation(async ({ ctx, input }) => {
      for (const itemId of input.itemIds) {
        await ctx.db.update(checklistItems)
          .set({ status: input.status, updatedAt: new Date() })
          .where(eq(checklistItems.id, itemId));
      }
      
      // Recalculate for all affected items
      for (const itemId of input.itemIds) {
        await updateCompletionPercentages(ctx.db, itemId);
      }
      
      return { success: true, updated: input.itemIds.length };
    }),
  
  // ============================================================================
  // GET MISSING CRITICAL DOCUMENTS
  // ============================================================================
  
  getMissingCritical: protectedProcedure
    .query(async ({ ctx }) => {
      const reconstruction = await ctx.db.query.serviceReconstruction.findFirst({
        where: eq(serviceReconstruction.userId, ctx.user.id)
      });
      
      if (!reconstruction) return [];
      
      // Find all critical missing documents
      const missingCritical = await ctx.db.query.checklistItems.findMany({
        where: and(
          eq(checklistItems.status, "missing"),
          eq(checklistItems.priority, "critical")
        ),
        with: {
          category: true
        }
      });
      
      return missingCritical;
    }),
  
  // ============================================================================
  // AUTO-GENERATE NARA REQUEST (SF-180 Form)
  // ============================================================================
  
  generateNARARequest: protectedProcedure
    .input(z.object({
      requestType: z.enum(["ompf_full", "ompf_partial", "unit_records", "medical_records", "training_records"]),
      requestedDocs: z.array(z.string()).optional()
    }))
    .mutation(async ({ ctx, input }) => {
      const reconstruction = await ctx.db.query.serviceReconstruction.findFirst({
        where: eq(serviceReconstruction.userId, ctx.user.id)
      });
      
      if (!reconstruction) {
        throw new Error('No reconstruction found');
      }
      
      // Generate SF-180 form with veteran data
      const sf180 = await generateSF180Form({
        veteran: {
          name: ctx.user.name,
          ssn: reconstruction.serviceNumber, // encrypted
          branch: reconstruction.branch,
          serviceDates: reconstruction.serviceDates
        },
        requestType: input.requestType,
        documents: input.requestedDocs || ["all"]
      });
      
      // Calculate expected response date (120 days typical)
      const expectedDate = new Date();
      expectedDate.setDate(expectedDate.getDate() + 120);
      
      // Save request to database
      const request = await ctx.db.insert(naraRequests).values({
        id: generateId(),
        userId: ctx.user.id,
        reconstructionId: reconstruction.id,
        requestType: input.requestType,
        requestedDocuments: input.requestedDocs || [],
        sf180Form: sf180.s3Path,
        coverLetter: sf180.coverLetterPath,
        status: "ready_to_submit",
        expectedResponseDate: expectedDate,
        naraContactInfo: {
          office: "National Personnel Records Center",
          address: "1 Archives Drive, St. Louis, MO 63138",
          phone: "314-801-0800",
          fax: "314-801-9195"
        }
      });
      
      return {
        requestId: request.id,
        formUrl: sf180.downloadUrl,
        coverLetterUrl: sf180.coverLetterUrl,
        expectedResponseDate: expectedDate,
        instructions: [
          "1. Download the pre-filled SF-180 form",
          "2. Sign and date the form",
          "3. Mail to NARA at the address provided",
          "4. Or fax to 314-801-9195",
          "5. Typical response time: 90-120 days",
          "6. We'll track the request and notify you when records arrive"
        ]
      };
    }),
  
  // ============================================================================
  // MAP DUTY STATION TO HAZARDS
  // ============================================================================
  
  mapHazardExposure: protectedProcedure
    .input(z.object({
      dutyStationId: z.string()
    }))
    .mutation(async ({ ctx, input }) => {
      const station = await ctx.db.query.dutyStationRecords.findFirst({
        where: eq(dutyStationRecords.id, input.dutyStationId)
      });
      
      if (!station) {
        throw new Error('Duty station not found');
      }
      
      // Query hazard database for this location and time period
      const hazards = await ctx.db.query.hazardExposureDatabase.findMany({
        where: and(
          eq(hazardExposureDatabase.baseName, station.baseName),
          // Add date range filtering
        )
      });
      
      // Calculate exposure for each hazard
      const exposures = hazards.map(hazard => ({
        type: hazard.hazardType,
        source: hazard.locationName,
        distance: calculateDistance(station.location, hazard.coordinates),
        exposureDays: calculateExposureDays(station.dates, hazard.activePeriod),
        severity: hazard.severity,
        presumptive: hazard.presumptiveCondition === 1,
        pactActCovered: hazard.pactActCovered === 1
      }));
      
      // Update duty station with hazard data
      await ctx.db.update(dutyStationRecords)
        .set({
          hazardExposures: exposures,
          updatedAt: new Date()
        })
        .where(eq(dutyStationRecords.id, input.dutyStationId));
      
      return {
        hazards: exposures,
        totalExposures: exposures.length,
        presumptiveConditions: exposures.filter(e => e.presumptive).length
      };
    }),
  
  // ============================================================================
  // MAP ALL DUTY STATIONS (run after all stations created)
  // ============================================================================
  
  mapAllHazards: protectedProcedure
    .mutation(async ({ ctx }) => {
      const reconstruction = await ctx.db.query.serviceReconstruction.findFirst({
        where: eq(serviceReconstruction.userId, ctx.user.id),
        with: {
          dutyStations: true
        }
      });
      
      if (!reconstruction) {
        throw new Error('No reconstruction found');
      }
      
      const results = [];
      
      for (const station of reconstruction.dutyStations) {
        const hazards = await mapStationHazards(ctx.db, station);
        results.push({
          stationName: station.stationName,
          hazards: hazards.length
        });
      }
      
      return {
        stationsMapped: results.length,
        totalHazards: results.reduce((sum, r) => sum + r.hazards, 0),
        results
      };
    }),
  
  // ============================================================================
  // GET MOS HAZARD INFO
  // ============================================================================
  
  getMOSHazards: protectedProcedure
    .input(z.object({
      mosCode: z.string()
    }))
    .query(async ({ ctx, input }) => {
      const reconstruction = await ctx.db.query.serviceReconstruction.findFirst({
        where: eq(serviceReconstruction.userId, ctx.user.id)
      });
      
      if (!reconstruction) return null;
      
      const mosData = await ctx.db.query.mosHazardMapping.findFirst({
        where: and(
          eq(mosHazardMapping.branch, reconstruction.branch),
          eq(mosHazardMapping.mosCode, input.mosCode)
        )
      });
      
      return mosData;
    }),
  
  // ============================================================================
  // CHECK IF READY FOR AI PROCESSING
  // ============================================================================
  
  checkReadiness: protectedProcedure
    .query(async ({ ctx }) => {
      const reconstruction = await ctx.db.query.serviceReconstruction.findFirst({
        where: eq(serviceReconstruction.userId, ctx.user.id)
      });
      
      if (!reconstruction) return { ready: false, percentage: 0 };
      
      const ready = reconstruction.completionPercentage >= 80;
      
      return {
        ready,
        percentage: reconstruction.completionPercentage,
        totalDocuments: reconstruction.totalDocuments,
        uploadedDocuments: reconstruction.uploadedDocuments,
        missingCritical: reconstruction.missingDocuments,
        message: ready 
          ? "Ready for AI processing! You have sufficient records."
          : `Need ${80 - reconstruction.completionPercentage}% more documents before AI processing.`
      };
    }),
  
  // ============================================================================
  // TRACK NARA REQUEST STATUS
  // ============================================================================
  
  getNARARequests: protectedProcedure
    .query(async ({ ctx }) => {
      const requests = await ctx.db.query.naraRequests.findMany({
        where: eq(naraRequests.userId, ctx.user.id),
        orderBy: [desc(naraRequests.createdAt)]
      });
      
      return requests;
    }),
  
  updateNARAStatus: protectedProcedure
    .input(z.object({
      requestId: z.string(),
      status: z.enum(["submitted", "pending_review", "in_progress", "received", "denied"]),
      trackingNumber: z.string().optional(),
      notes: z.string().optional()
    }))
    .mutation(async ({ ctx, input }) => {
      await ctx.db.update(naraRequests)
        .set({
          status: input.status,
          trackingNumber: input.trackingNumber,
          submittedDate: input.status === "submitted" ? new Date() : undefined,
          receivedDate: input.status === "received" ? new Date() : undefined,
          updatedAt: new Date()
        })
        .where(eq(naraRequests.id, input.requestId));
      
      return { success: true };
    })
});

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

async function updateCompletionPercentages(db: any, itemId: string) {
  // Get the item to find its category
  const item = await db.query.checklistItems.findFirst({
    where: eq(checklistItems.id, itemId)
  });
  
  if (!item) return;
  
  // Get all items in this category
  const categoryItems = await db.query.checklistItems.findMany({
    where: eq(checklistItems.categoryId, item.categoryId)
  });
  
  const completed = categoryItems.filter(i => 
    i.status === "uploaded" || i.status === "verified" || i.status === "auto_generated"
  ).length;
  
  const percentage = Math.round((completed / categoryItems.length) * 100);
  
  // Update category
  await db.update(checklistCategories)
    .set({
      completedItems: completed,
      completionPercentage: percentage,
      updatedAt: new Date()
    })
    .where(eq(checklistCategories.id, item.categoryId));
  
  // Get category to find reconstruction
  const category = await db.query.checklistCategories.findFirst({
    where: eq(checklistCategories.id, item.categoryId)
  });
  
  // Get all categories for this reconstruction
  const allCategories = await db.query.checklistCategories.findMany({
    where: eq(checklistCategories.reconstructionId, category.reconstructionId)
  });
  
  const totalItems = allCategories.reduce((sum, cat) => sum + cat.totalItems, 0);
  const completedItems = allCategories.reduce((sum, cat) => sum + cat.completedItems, 0);
  const overallPercentage = Math.round((completedItems / totalItems) * 100);
  
  // Update reconstruction
  await db.update(serviceReconstruction)
    .set({
      totalDocuments: totalItems,
      uploadedDocuments: completedItems,
      completionPercentage: overallPercentage,
      readyForAIProcessing: overallPercentage >= 80 ? 1 : 0,
      minimumThresholdMet: overallPercentage >= 80 ? 1 : 0,
      updatedAt: new Date()
    })
    .where(eq(serviceReconstruction.id, category.reconstructionId));
}

async function mapStationHazards(db: any, station: any) {
  const hazards = await db.query.hazardExposureDatabase.findMany({
    where: eq(hazardExposureDatabase.baseName, station.baseName)
  });
  
  const exposures = hazards.map(h => ({
    type: h.hazardType,
    source: h.locationName,
    distance: 0, // Calculate actual distance
    exposureDays: calculateExposureDays(station.dates, h.activePeriod),
    severity: h.severity,
    presumptive: h.presumptiveCondition === 1,
    pactActCovered: h.pactActCovered === 1
  }));
  
  await db.update(dutyStationRecords)
    .set({ hazardExposures: exposures })
    .where(eq(dutyStationRecords.id, station.id));
  
  return exposures;
}

function calculateDistance(loc1: any, loc2: any): number {
  // Haversine formula for distance between two lat/long points
  const R = 6371e3; // Earth radius in meters
  const φ1 = loc1.lat * Math.PI/180;
  const φ2 = loc2.lat * Math.PI/180;
  const Δφ = (loc2.lat - loc1.lat) * Math.PI/180;
  const Δλ = (loc2.long - loc1.long) * Math.PI/180;
  
  const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
           Math.cos(φ1) * Math.cos(φ2) *
           Math.sin(Δλ/2) * Math.sin(Δλ/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  
  return R * c; // Distance in meters
}

function calculateExposureDays(stationDates: any, hazardPeriod: any): number {
  // Calculate overlap between station dates and hazard active period
  const stationStart = new Date(stationDates.arrival);
  const stationEnd = new Date(stationDates.departure);
  const hazardStart = new Date(hazardPeriod.start);
  const hazardEnd = new Date(hazardPeriod.end);
  
  const overlapStart = stationStart > hazardStart ? stationStart : hazardStart;
  const overlapEnd = stationEnd < hazardEnd ? stationEnd : hazardEnd;
  
  if (overlapStart > overlapEnd) return 0;
  
  const diffTime = Math.abs(overlapEnd.getTime() - overlapStart.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  return diffDays;
}
