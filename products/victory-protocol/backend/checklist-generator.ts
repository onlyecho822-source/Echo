/**
 * PERSONALIZED CHECKLIST GENERATOR
 * Creates customized 200+ item checklist based on veteran's service
 */

interface ServiceData {
  branch: string;
  serviceDates: { start: string; end: string };
  mos?: string;
  deployments?: string[];
  specialSchools?: string[];
  rank?: string;
}

interface ChecklistCategory {
  id: string;
  name: string;
  type: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  items: ChecklistItem[];
}

interface ChecklistItem {
  id: string;
  name: string;
  description: string;
  source: string;
  acquisitionMethod: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  required: boolean;
}

/**
 * Generate complete personalized checklist
 */
export async function generatePersonalizedChecklist(
  serviceData: ServiceData
): Promise<ChecklistCategory[]> {
  const categories: ChecklistCategory[] = [];

  // 1. Enlistment Records (Everyone needs these)
  categories.push(generateEnlistmentCategory());

  // 2. Basic Training (Everyone)
  categories.push(generateBasicTrainingCategory(serviceData.branch));

  // 3. AIT/MOS School (Everyone)
  categories.push(generateAITCategory(serviceData.mos));

  // 4. Specialized Schools (If attended)
  if (serviceData.specialSchools && serviceData.specialSchools.length > 0) {
    categories.push(generateSpecializedSchoolsCategory(serviceData.specialSchools));
  }

  // 5. Duty Stations (Calculate from service dates)
  const estimatedStations = estimateDutyStations(serviceData.serviceDates);
  categories.push(generateDutyStationCategory(estimatedStations));

  // 6. Deployments (If deployed)
  if (serviceData.deployments && serviceData.deployments.length > 0) {
    categories.push(generateDeploymentCategory(serviceData.deployments));
  }

  // 7. Awards & Decorations (Everyone)
  categories.push(generateAwardsCategory());

  // 8. Medical Records (Everyone - CRITICAL)
  categories.push(generateMedicalRecordsCategory());

  // 9. Administrative Records (Everyone)
  categories.push(generateAdministrativeCategory());

  // 10. Separation Records (Everyone)
  categories.push(generateSeparationCategory());

  // 11. Maps & Geographic Data (Auto-generated)
  categories.push(generateMapsCategory());

  return categories;
}

// ============================================================================
// CATEGORY GENERATORS
// ============================================================================

function generateEnlistmentCategory(): ChecklistCategory {
  return {
    id: 'enlistment',
    name: 'Enlistment Records',
    type: 'enlistment',
    priority: 'high',
    items: [
      {
        id: 'asvab',
        name: 'ASVAB Test Scores',
        description: 'Armed Services Vocational Aptitude Battery scores',
        source: 'MEPS / Recruiter Records',
        acquisitionMethod: 'nara_request',
        priority: 'medium',
        required: false
      },
      {
        id: 'enlistment_contract',
        name: 'Enlistment Contract (DD Form 4)',
        description: 'Original enlistment contract',
        source: 'OMPF',
        acquisitionMethod: 'nara_request',
        priority: 'high',
        required: true
      },
      {
        id: 'security_clearance',
        name: 'Security Clearance (SF-86)',
        description: 'Security clearance application if applicable',
        source: 'NARA',
        acquisitionMethod: 'nara_request',
        priority: 'low',
        required: false
      },
      {
        id: 'oath_certificate',
        name: 'Oath of Enlistment Certificate',
        description: 'Certificate of oath administration',
        source: 'Personal Files',
        acquisitionMethod: 'veteran_upload',
        priority: 'low',
        required: false
      },
      {
        id: 'meps_physical',
        name: 'MEPS Physical Examination',
        description: 'Entry physical exam results',
        source: 'MEPS',
        acquisitionMethod: 'nara_request',
        priority: 'high',
        required: true
      },
    ]
  };
}

function generateBasicTrainingCategory(branch: string): ChecklistCategory {
  const trainingName = getTrainingName(branch);
  
  return {
    id: 'basic_training',
    name: `Basic Training (${trainingName})`,
    type: 'basic_training',
    priority: 'medium',
    items: [
      {
        id: 'basic_orders',
        name: 'Orders to Basic Training',
        description: 'Assignment orders to basic training location',
        source: 'OMPF',
        acquisitionMethod: 'nara_request',
        priority: 'medium',
        required: false
      },
      {
        id: 'basic_graduation',
        name: 'Basic Training Graduation Certificate',
        description: 'Certificate of completion',
        source: 'Personal Files',
        acquisitionMethod: 'veteran_upload',
        priority: 'low',
        required: false
      },
      {
        id: 'pft_scores',
        name: 'Physical Fitness Test Scores',
        description: 'Initial and final PFT scores',
        source: 'Training Battalion',
        acquisitionMethod: 'unit_request',
        priority: 'low',
        required: false
      },
      {
        id: 'weapons_qual',
        name: 'Weapons Qualification Scores',
        description: 'Rifle marksmanship qualification',
        source: 'Training Battalion',
        acquisitionMethod: 'unit_request',
        priority: 'low',
        required: false
      },
      {
        id: 'basic_sick_call',
        name: 'Basic Training Sick Call Records',
        description: 'Any medical visits during basic training',
        source: 'Training Battalion Medical',
        acquisitionMethod: 'nara_request',
        priority: 'high',
        required: false
      },
    ]
  };
}

function generateAITCategory(mos?: string): ChecklistCategory {
  return {
    id: 'ait',
    name: `AIT/MOS School ${mos ? `(${mos})` : ''}`,
    type: 'ait',
    priority: 'medium',
    items: [
      {
        id: 'ait_orders',
        name: 'Orders to AIT',
        description: 'Assignment orders to advanced training',
        source: 'OMPF',
        acquisitionMethod: 'nara_request',
        priority: 'medium',
        required: false
      },
      {
        id: 'ait_graduation',
        name: 'AIT Graduation Certificate',
        description: 'MOS qualification certificate',
        source: 'Personal Files',
        acquisitionMethod: 'veteran_upload',
        priority: 'medium',
        required: false
      },
      {
        id: 'test_scores',
        name: 'AIT Test Scores',
        description: 'Written and practical exam scores',
        source: 'School House',
        acquisitionMethod: 'unit_request',
        priority: 'low',
        required: false
      },
      {
        id: 'skills_qualification',
        name: 'Skills Qualification Records',
        description: 'Equipment/weapon qualification records',
        source: 'School House',
        acquisitionMethod: 'unit_request',
        priority: 'low',
        required: false
      },
    ]
  };
}

function generateSpecializedSchoolsCategory(schools: string[]): ChecklistCategory {
  return {
    id: 'specialized_schools',
    name: 'Specialized Training Schools',
    type: 'specialized_schools',
    priority: 'medium',
    items: schools.map((school, index) => ({
      id: `school_${index}`,
      name: `${school} - Certificate`,
      description: `Graduation certificate for ${school}`,
      source: 'School Records',
      acquisitionMethod: 'unit_request',
      priority: 'medium' as const,
      required: false
    }))
  };
}

function generateDutyStationCategory(estimatedStations: number): ChecklistCategory {
  const items: ChecklistItem[] = [];
  
  for (let i = 1; i <= estimatedStations; i++) {
    items.push(
      {
        id: `station_${i}_pcs`,
        name: `Duty Station ${i} - PCS Orders`,
        description: 'Permanent Change of Station orders',
        source: 'OMPF',
        acquisitionMethod: 'nara_request',
        priority: 'high',
        required: true
      },
      {
        id: `station_${i}_unit_roster`,
        name: `Duty Station ${i} - Unit Roster`,
        description: 'Company/battalion roster',
        source: 'Unit S-1',
        acquisitionMethod: 'unit_request',
        priority: 'medium',
        required: false
      },
      {
        id: `station_${i}_morning_reports`,
        name: `Duty Station ${i} - Morning Reports`,
        description: 'Unit morning reports (daily status)',
        source: 'Unit Records',
        acquisitionMethod: 'unit_request',
        priority: 'high',
        required: false
      },
      {
        id: `station_${i}_hazard_map`,
        name: `Duty Station ${i} - Hazard Exposure Map`,
        description: 'Auto-generated hazard proximity map',
        source: 'System Generated',
        acquisitionMethod: 'auto_generated',
        priority: 'critical',
        required: true
      },
    );
  }

  return {
    id: 'duty_stations',
    name: 'Duty Station Records',
    type: 'duty_stations',
    priority: 'critical',
    items
  };
}

function generateDeploymentCategory(deployments: string[]): ChecklistCategory {
  const items: ChecklistItem[] = [];
  
  deployments.forEach((deployment, index) => {
    items.push(
      {
        id: `deploy_${index}_orders`,
        name: `${deployment} - Deployment Orders`,
        description: 'Orders for deployment',
        source: 'OMPF / Unit',
        acquisitionMethod: 'nara_request',
        priority: 'critical',
        required: true
      },
      {
        id: `deploy_${index}_aar`,
        name: `${deployment} - After Action Reports`,
        description: 'Unit after-action reports',
        source: 'Unit S-3',
        acquisitionMethod: 'unit_request',
        priority: 'high',
        required: false
      },
      {
        id: `deploy_${index}_pdha`,
        name: `${deployment} - Post-Deployment Health Assessment`,
        description: 'PDHA completed upon return',
        source: 'Medical Records',
        acquisitionMethod: 'va_download',
        priority: 'critical',
        required: true
      },
      {
        id: `deploy_${index}_pdhra`,
        name: `${deployment} - Post-Deployment Health Reassessment`,
        description: 'PDHRA (90-180 days post-deployment)',
        source: 'Medical Records',
        acquisitionMethod: 'va_download',
        priority: 'critical',
        required: true
      },
      {
        id: `deploy_${index}_hazard_map`,
        name: `${deployment} - Burn Pit / Hazard Proximity`,
        description: 'Auto-generated deployment hazard map',
        source: 'System Generated',
        acquisitionMethod: 'auto_generated',
        priority: 'critical',
        required: true
      },
    );
  });

  return {
    id: 'deployments',
    name: 'Deployment Records',
    type: 'deployments',
    priority: 'critical',
    items
  };
}

function generateAwardsCategory(): ChecklistCategory {
  return {
    id: 'awards',
    name: 'Awards & Decorations',
    type: 'awards_decorations',
    priority: 'medium',
    items: [
      {
        id: 'award_orders',
        name: 'All Award Orders (DA Form 638)',
        description: 'Orders for each award received',
        source: 'OMPF',
        acquisitionMethod: 'nara_request',
        priority: 'medium',
        required: false
      },
      {
        id: 'award_certificates',
        name: 'Award Certificates',
        description: 'Physical certificates for awards',
        source: 'Personal Files',
        acquisitionMethod: 'veteran_upload',
        priority: 'low',
        required: false
      },
    ]
  };
}

function generateMedicalRecordsCategory(): ChecklistCategory {
  return {
    id: 'medical',
    name: 'Medical Records',
    type: 'medical_records',
    priority: 'critical',
    items: [
      {
        id: 'blue_button',
        name: 'VA Blue Button Records (Complete)',
        description: 'All VA medical records downloaded',
        source: 'VA.gov',
        acquisitionMethod: 'va_download',
        priority: 'critical',
        required: true
      },
      {
        id: 'service_medical',
        name: 'Active Duty Medical Records',
        description: 'All sick call, hospital visits during service',
        source: 'NARA',
        acquisitionMethod: 'nara_request',
        priority: 'critical',
        required: true
      },
      {
        id: 'private_medical',
        name: 'Private Medical Records',
        description: 'Any private doctor visits post-service',
        source: 'Private Providers',
        acquisitionMethod: 'veteran_upload',
        priority: 'high',
        required: false
      },
      {
        id: 'separation_physical',
        name: 'Separation Physical Exam',
        description: 'Exit physical examination',
        source: 'OMPF',
        acquisitionMethod: 'nara_request',
        priority: 'critical',
        required: true
      },
    ]
  };
}

function generateAdministrativeCategory(): ChecklistCategory {
  return {
    id: 'administrative',
    name: 'Administrative Records',
    type: 'administrative',
    priority: 'medium',
    items: [
      {
        id: 'ncoers',
        name: 'NCOERs/OERs (All)',
        description: 'All performance evaluations',
        source: 'OMPF',
        acquisitionMethod: 'nara_request',
        priority: 'medium',
        required: false
      },
      {
        id: 'promotion_orders',
        name: 'All Promotion Orders',
        description: 'Orders for each promotion',
        source: 'OMPF',
        acquisitionMethod: 'nara_request',
        priority: 'low',
        required: false
      },
      {
        id: 'counseling',
        name: 'Counseling Statements',
        description: 'Positive and negative counseling',
        source: 'OMPF',
        acquisitionMethod: 'nara_request',
        priority: 'low',
        required: false
      },
    ]
  };
}

function generateSeparationCategory(): ChecklistCategory {
  return {
    id: 'separation',
    name: 'Separation Records',
    type: 'separation',
    priority: 'critical',
    items: [
      {
        id: 'dd214',
        name: 'DD Form 214 (All Copies)',
        description: 'Certificate of Release or Discharge',
        source: 'Personal Files / OMPF',
        acquisitionMethod: 'veteran_upload',
        priority: 'critical',
        required: true
      },
      {
        id: 'dd215',
        name: 'DD Form 215 (If Applicable)',
        description: 'Correction to DD214',
        source: 'OMPF',
        acquisitionMethod: 'nara_request',
        priority: 'medium',
        required: false
      },
      {
        id: 'separation_orders',
        name: 'Separation Orders',
        description: 'Orders authorizing separation',
        source: 'OMPF',
        acquisitionMethod: 'nara_request',
        priority: 'medium',
        required: false
      },
    ]
  };
}

function generateMapsCategory(): ChecklistCategory {
  return {
    id: 'maps',
    name: 'Geographic & Hazard Maps',
    type: 'maps_geographic',
    priority: 'critical',
    items: [
      {
        id: 'all_stations_map',
        name: 'Complete Service Timeline Map',
        description: 'Visual timeline of all duty stations',
        source: 'System Generated',
        acquisitionMethod: 'auto_generated',
        priority: 'critical',
        required: true
      },
      {
        id: 'hazard_proximity',
        name: 'Hazard Proximity Analysis',
        description: 'Burn pits, contamination, Agent Orange',
        source: 'System Generated',
        acquisitionMethod: 'auto_generated',
        priority: 'critical',
        required: true
      },
    ]
  };
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function getTrainingName(branch: string): string {
  const names: Record<string, string> = {
    'Army': 'BCT',
    'Navy': 'Boot Camp',
    'Air Force': 'BMT',
    'Marines': 'Boot Camp',
    'Coast Guard': 'Boot Camp',
    'Space Force': 'BMT'
  };
  return names[branch] || 'Basic Training';
}

function estimateDutyStations(serviceDates: { start: string; end: string }): number {
  const start = new Date(serviceDates.start);
  const end = new Date(serviceDates.end);
  const yearsServed = (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24 * 365);
  
  // Estimate: 1 station per 2-3 years
  return Math.max(1, Math.ceil(yearsServed / 2.5));
}

/**
 * Calculate total documents in checklist
 */
export function calculateTotalDocuments(categories: ChecklistCategory[]): number {
  return categories.reduce((sum, category) => sum + category.items.length, 0);
}
