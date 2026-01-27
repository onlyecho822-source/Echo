/**
 * ART OF PROOF: SERVICE RECONSTRUCTION API ROUTER
 * Complete backend for military service record reconstruction
 */

import { z } from 'zod';
import { TRPCError } from '@trpc/server';
import { router, protectedProcedure } from '../trpc';
import { generateId } from '../utils/id';
import { extractDD214Data } from '../services/documentExtraction';
import { generatePersonalizedChecklist } from '../services/checklistGenerator';
import { queryHazardDatabases } from '../services/hazardMapping';
import { generateSF180Form } from '../services/naraRequest';
import { geocodeLocation } from '../services/geocoding';

// ============================================================================
// INPUT VALIDATION SCHEMAS
// ============================================================================

const InitializeReconstructionSchema = z.object({
  dd214FileId: z.string(),
  dd214Data: z.object({
    branch: z.enum(['Army', 'Navy', 'Air Force', 'Marines', 'Coast Guard', 'Space Force']),
    serviceStartDate: z.string(),
    serviceEndDate: z.string(),
    mos: z.string().optional(),
    rankAtSeparation: z.string().optional(),
  }).optional()
});

const UpdateChecklistItemSchema = z.object({
  itemId: z.string(),
  status: z.enum(['missing', 'uploaded', 'requested', 'processing', 'verified', 'rejected']),
  fileId: z.string().optional(),
  filePath: z.string().optional(),
  notes: z.string().optional()
});

const AddDutyStationSchema = z.object({
  reconstructionId: z.string(),
  stationName: z.string(),
  location: z.object({
    address: z.string(),
    city: z.string().optional(),
    state: z.string().optional(),
    country: z.string().optional()
  }),
  startDate: z.string(),
  endDate: z.string().optional(),
  unit: z.string().optional(),
  mos: z.string().optional()
});

const GenerateNARARequestSchema = z.object({
  requestType: z.enum(['ompf', 'unit_records', 'medical_records', 'personnel_records']),
  requestedDocuments: z.array(z.string()),
  veteranInfo: z.object({
    fullName: z.string(),
    ssn: z.string(),
    dateOfBirth: z.string(),
    branch: z.string(),
    serviceDates: z.object({
      start: z.string(),
      end: z.string()
    })
  })
});

// ============================================================================
// SERVICE RECONSTRUCTION ROUTER
// ============================================================================

export const reconstructionRouter = router({
  
  /**
   * Initialize service reconstruction from DD214
   * Extracts service data and generates personalized checklist
   */
  initialize: protectedProcedure
    .input(InitializeReconstructionSchema)
    .mutation(async ({ ctx, input }) => {
      try {
        // Extract data from DD214
        let serviceData;
        if (input.dd214Data) {
          serviceData = input.dd214Data;
        } else {
          serviceData = await extractDD214Data(input.dd214FileId);
        }
        
        // Create reconstruction record
        const reconstructionId = generateId();
        await ctx.db.insert('service_reconstruction', {
          id: reconstructionId,
          user_id: ctx.user.id,
          branch: serviceData.branch,
          service_start_date: serviceData.serviceStartDate,
          service_end_date: serviceData.serviceEndDate,
          primary_mos: serviceData.mos,
          rank_at_separation: serviceData.rankAtSeparation,
          status: 'initialized'
        });
        
        // Generate personalized checklist based on service
        const checklist = await generatePersonalizedChecklist({
          reconstructionId,
          branch: serviceData.branch,
          serviceDates: {
            start: serviceData.serviceStartDate,
            end: serviceData.serviceEndDate
          },
          mos: serviceData.mos
        });
        
        // Create categories
        for (const category of checklist.categories) {
          const categoryId = generateId();
          await ctx.db.insert('checklist_categories', {
            id: categoryId,
            reconstruction_id: reconstructionId,
            category_name: category.name,
            category_type: category.type,
            total_items: category.items.length,
            priority: category.priority
          });
          
          // Create checklist items
          for (const item of category.items) {
            await ctx.db.insert('checklist_items', {
              id: generateId(),
              category_id: categoryId,
              document_name: item.name,
              document_type: item.type,
              description: item.description,
              source: item.source,
              acquisition_method: item.acquisitionMethod,
              priority: item.priority,
              status: 'missing'
            });
          }
        }
        
        // Update total documents count
        await ctx.db.update('service_reconstruction', {
          total_documents: checklist.totalDocuments
        }).where({ id: reconstructionId });
        
        return {
          reconstructionId,
          totalDocuments: checklist.totalDocuments,
          categories: checklist.categories.length,
          message: 'Service reconstruction initialized successfully'
        };
        
      } catch (error) {
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: `Failed to initialize reconstruction: ${error.message}`
        });
      }
    }),
  
  /**
   * Get full reconstruction with all data
   */
  getReconstruction: protectedProcedure
    .query(async ({ ctx }) => {
      try {
        const reconstruction = await ctx.db.query(`
          SELECT sr.*,
            (SELECT COUNT(*) FROM checklist_categories WHERE reconstruction_id = sr.id) as categories_count,
            (SELECT COUNT(*) FROM duty_station_records WHERE reconstruction_id = sr.id) as duty_stations_count,
            (SELECT COUNT(*) FROM deployment_records WHERE reconstruction_id = sr.id) as deployments_count,
            (SELECT COUNT(*) FROM training_schools WHERE reconstruction_id = sr.id) as training_schools_count
          FROM service_reconstruction sr
          WHERE sr.user_id = ?
          ORDER BY sr.created_at DESC
          LIMIT 1
        `, [ctx.user.id]);
        
        if (!reconstruction) {
          return null;
        }
        
        // Get categories with items
        const categories = await ctx.db.query(`
          SELECT cc.*,
            (SELECT JSON_ARRAYAGG(
              JSON_OBJECT(
                'id', ci.id,
                'documentName', ci.document_name,
                'documentType', ci.document_type,
                'description', ci.description,
                'status', ci.status,
                'source', ci.source,
                'acquisitionMethod', ci.acquisition_method,
                'priority', ci.priority,
                'fileId', ci.file_id,
                'requestedDate', ci.requested_date,
                'expectedDate', ci.expected_date,
                'receivedDate', ci.received_date
              )
            ) FROM checklist_items ci WHERE ci.category_id = cc.id) as items
          FROM checklist_categories cc
          WHERE cc.reconstruction_id = ?
          ORDER BY 
            CASE cc.priority
              WHEN 'critical' THEN 1
              WHEN 'high' THEN 2
              WHEN 'medium' THEN 3
              WHEN 'low' THEN 4
            END
        `, [reconstruction.id]);
        
        // Get duty stations
        const dutyStations = await ctx.db.query(`
          SELECT ds.*,
            (SELECT JSON_ARRAYAGG(
              JSON_OBJECT(
                'id', he.id,
                'hazardType', he.hazard_type,
                'hazardName', he.hazard_name,
                'severity', he.severity,
                'exposureDays', he.exposure_days,
                'presumptive', he.presumptive_condition,
                'pactActCovered', he.pact_act_covered
              )
            ) FROM hazard_exposures he WHERE he.duty_station_id = ds.id) as hazardExposures
          FROM duty_station_records ds
          WHERE ds.reconstruction_id = ?
          ORDER BY ds.start_date
        `, [reconstruction.id]);
        
        // Get deployments
        const deployments = await ctx.db.query(`
          SELECT * FROM deployment_records
          WHERE reconstruction_id = ?
          ORDER BY deployment_start
        `, [reconstruction.id]);
        
        // Get training schools
        const trainingSchools = await ctx.db.query(`
          SELECT * FROM training_schools
          WHERE reconstruction_id = ?
          ORDER BY start_date
        `, [reconstruction.id]);
        
        return {
          ...reconstruction,
          categories: categories.map(cat => ({
            ...cat,
            items: JSON.parse(cat.items || '[]')
          })),
          dutyStations: dutyStations.map(ds => ({
            ...ds,
            hazardExposures: JSON.parse(ds.hazardExposures || '[]')
          })),
          deployments,
          trainingSchools
        };
        
      } catch (error) {
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: `Failed to fetch reconstruction: ${error.message}`
        });
      }
    }),
  
  /**
   * Update checklist item status
   */
  updateChecklistItem: protectedProcedure
    .input(UpdateChecklistItemSchema)
    .mutation(async ({ ctx, input }) => {
      try {
        // Update item
        await ctx.db.update('checklist_items', {
          status: input.status,
          file_id: input.fileId,
          file_path: input.filePath,
          notes: input.notes,
          received_date: input.status === 'uploaded' || input.status === 'verified' 
            ? new Date() 
            : null
        }).where({ id: input.itemId });
        
        // Get category to recalculate completion
        const item = await ctx.db.queryFirst(`
          SELECT category_id FROM checklist_items WHERE id = ?
        `, [input.itemId]);
        
        if (item) {
          await recalculateCategoryCompletion(ctx.db, item.category_id);
          
          // Get reconstruction ID to update overall completion
          const category = await ctx.db.queryFirst(`
            SELECT reconstruction_id FROM checklist_categories WHERE id = ?
          `, [item.category_id]);
          
          if (category) {
            await recalculateReconstructionCompletion(ctx.db, category.reconstruction_id);
          }
        }
        
        return { success: true };
        
      } catch (error) {
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: `Failed to update checklist item: ${error.message}`
        });
      }
    }),
  
  /**
   * Add duty station and map hazards
   */
  addDutyStation: protectedProcedure
    .input(AddDutyStationSchema)
    .mutation(async ({ ctx, input }) => {
      try {
        // Geocode the location
        const geocoded = await geocodeLocation(input.location.address);
        
        const stationId = generateId();
        await ctx.db.insert('duty_station_records', {
          id: stationId,
          reconstruction_id: input.reconstructionId,
          station_name: input.stationName,
          base_name: geocoded.baseName,
          address: input.location.address,
          city: input.location.city || geocoded.city,
          state: input.location.state || geocoded.state,
          country: input.location.country || geocoded.country,
          latitude: geocoded.lat,
          longitude: geocoded.lng,
          start_date: input.startDate,
          end_date: input.endDate,
          unit_name: input.unit,
          mos: input.mos,
          documents_needed: 18
        });
        
        // Query hazard databases
        const hazards = await queryHazardDatabases({
          location: { lat: geocoded.lat, lng: geocoded.lng },
          baseName: geocoded.baseName,
          dates: {
            start: input.startDate,
            end: input.endDate || input.startDate
          }
        });
        
        // Insert hazard exposures
        for (const hazard of hazards) {
          await ctx.db.insert('hazard_exposures', {
            id: generateId(),
            duty_station_id: stationId,
            hazard_type: hazard.type,
            hazard_name: hazard.name,
            hazard_source: hazard.source,
            distance_meters: hazard.distance,
            exposure_days: hazard.exposureDays,
            severity: hazard.severity,
            presumptive_condition: hazard.presumptive,
            pact_act_covered: hazard.pactActCovered,
            documentation_level: hazard.documentationLevel,
            evidence_source: hazard.evidenceSource
          });
        }
        
        return {
          stationId,
          hazardsFound: hazards.length,
          location: geocoded
        };
        
      } catch (error) {
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: `Failed to add duty station: ${error.message}`
        });
      }
    }),
  
  /**
   * Generate NARA SF-180 request form
   */
  generateNARARequest: protectedProcedure
    .input(GenerateNARARequestSchema)
    .mutation(async ({ ctx, input }) => {
      try {
        // Generate SF-180 PDF
        const sf180Result = await generateSF180Form({
          requestType: input.requestType,
          veteranInfo: input.veteranInfo,
          requestedDocuments: input.requestedDocuments
        });
        
        // Save request to database
        const requestId = generateId();
        const expectedDate = new Date();
        expectedDate.setDate(expectedDate.getDate() + 120); // 120 days typical
        
        await ctx.db.insert('nara_requests', {
          id: requestId,
          user_id: ctx.user.id,
          request_type: input.requestType,
          requested_documents: JSON.stringify(input.requestedDocuments),
          sf180_form_path: sf180Result.s3Path,
          status: 'draft',
          expected_response_date: expectedDate
        });
        
        return {
          requestId,
          formDownloadUrl: sf180Result.downloadUrl,
          expectedResponseDate: expectedDate,
          instructions: `
            1. Download the pre-filled SF-180 form
            2. Sign and date the form
            3. Mail to: National Personnel Records Center
                       1 Archives Drive
                       St. Louis, MO 63138
            4. Typical response time: 90-120 days
            5. Track status in your dashboard
          `
        };
        
      } catch (error) {
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: `Failed to generate NARA request: ${error.message}`
        });
      }
    }),
  
  /**
   * Get completion statistics
   */
  getStatistics: protectedProcedure
    .query(async ({ ctx }) => {
      try {
        const stats = await ctx.db.queryFirst(`
          SELECT 
            sr.total_documents,
            sr.uploaded_documents,
            sr.missing_documents,
            sr.requested_documents,
            sr.completion_percentage,
            (SELECT COUNT(*) FROM checklist_items ci
             JOIN checklist_categories cc ON ci.category_id = cc.id
             WHERE cc.reconstruction_id = sr.id AND ci.priority = 'critical' AND ci.status = 'missing') as critical_missing,
            (SELECT COUNT(DISTINCT ds.id) FROM duty_station_records ds WHERE ds.reconstruction_id = sr.id) as duty_stations,
            (SELECT COUNT(DISTINCT dr.id) FROM deployment_records dr WHERE dr.reconstruction_id = sr.id) as deployments,
            (SELECT COUNT(DISTINCT he.id) FROM hazard_exposures he
             JOIN duty_station_records ds ON he.duty_station_id = ds.id
             WHERE ds.reconstruction_id = sr.id AND he.presumptive_condition = TRUE) as presumptive_exposures
          FROM service_reconstruction sr
          WHERE sr.user_id = ?
          ORDER BY sr.created_at DESC
          LIMIT 1
        `, [ctx.user.id]);
        
        return stats || {
          total_documents: 0,
          uploaded_documents: 0,
          missing_documents: 0,
          requested_documents: 0,
          completion_percentage: 0,
          critical_missing: 0,
          duty_stations: 0,
          deployments: 0,
          presumptive_exposures: 0
        };
        
      } catch (error) {
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: `Failed to fetch statistics: ${error.message}`
        });
      }
    })
});

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

async function recalculateCategoryCompletion(db, categoryId) {
  const stats = await db.queryFirst(`
    SELECT 
      COUNT(*) as total,
      SUM(CASE WHEN status IN ('uploaded', 'verified') THEN 1 ELSE 0 END) as completed
    FROM checklist_items
    WHERE category_id = ?
  `, [categoryId]);
  
  const percentage = stats.total > 0 
    ? Math.round((stats.completed / stats.total) * 100)
    : 0;
  
  await db.update('checklist_categories', {
    total_items: stats.total,
    completed_items: stats.completed,
    completion_percentage: percentage
  }).where({ id: categoryId });
}

async function recalculateReconstructionCompletion(db, reconstructionId) {
  const stats = await db.queryFirst(`
    SELECT 
      COUNT(*) as total,
      SUM(CASE WHEN status IN ('uploaded', 'verified') THEN 1 ELSE 0 END) as uploaded,
      SUM(CASE WHEN status = 'missing' THEN 1 ELSE 0 END) as missing,
      SUM(CASE WHEN status = 'requested' THEN 1 ELSE 0 END) as requested
    FROM checklist_items ci
    JOIN checklist_categories cc ON ci.category_id = cc.id
    WHERE cc.reconstruction_id = ?
  `, [reconstructionId]);
  
  const percentage = stats.total > 0 
    ? Math.round((stats.uploaded / stats.total) * 100)
    : 0;
  
  // Determine status
  let status = 'in_progress';
  if (percentage === 0) status = 'initialized';
  else if (percentage >= 80) status = 'ready_for_submission';
  else if (percentage === 100) status = 'complete';
  
  await db.update('service_reconstruction', {
    total_documents: stats.total,
    uploaded_documents: stats.uploaded,
    missing_documents: stats.missing,
    requested_documents: stats.requested,
    completion_percentage: percentage,
    status: status
  }).where({ id: reconstructionId });
}
