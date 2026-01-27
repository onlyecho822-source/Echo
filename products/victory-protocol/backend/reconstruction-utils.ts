// Core Reconstruction Utilities
// server/_core/reconstruction.ts

import { invokeLLM } from './llm';

// ============================================================================
// DD214 DATA EXTRACTION
// ============================================================================

export async function extractDD214Data(fileId: string) {
  // Get file from S3/database
  const fileContent = await getFileContent(fileId);
  
  // Use LLM to extract structured data from DD214
  const prompt = `
Extract the following information from this DD214 military discharge document:

1. Branch of Service (Army, Navy, Air Force, Marines, Coast Guard)
2. Service Number (or SSN if post-1974)
3. Final Rank
4. Primary MOS/Rating
5. All MOS/Ratings held
6. Enlistment Date
7. Separation Date
8. Years of Active Service
9. Years of Reserve Service (if any)
10. Character of Service (Honorable, General, etc.)
11. Duty Stations (extract all locations mentioned)
12. Deployments (any overseas or combat indicators)
13. Special Training/Schools
14. Awards and Decorations

Return as JSON with these exact fields.
`;

  const extraction = await invokeLLM({
    model: 'claude-sonnet-4-5-20250929',
    messages: [
      {
        role: 'user',
        content: [
          { type: 'text', text: prompt },
          { type: 'document', source: { type: 'base64', media_type: 'application/pdf', data: fileContent }}
        ]
      }
    ],
    max_tokens: 2000
  });
  
  const data = JSON.parse(extraction.content[0].text);
  
  return {
    branch: data.branch,
    serviceNumber: data.serviceNumber,
    finalRank: data.finalRank,
    primaryMOS: data.primaryMOS,
    allMOS: data.allMOS || [data.primaryMOS],
    enlistmentDate: data.enlistmentDate,
    separationDate: data.separationDate,
    activeYears: data.activeYears,
    reserveYears: data.reserveYears || 0,
    characterOfService: data.characterOfService,
    dutyStations: parseDutyStations(data.dutyStations),
    deploymentIndicators: data.deployments || [],
    specializations: data.specialTraining || [],
    awards: data.awards || []
  };
}

// ============================================================================
// GENERATE PERSONALIZED CHECKLIST
// ============================================================================

export async function generatePersonalizedChecklist(params: {
  branch: string,
  serviceDates: any,
  mos: string[],
  deployments: string[],
  specializations: string[]
}) {
  const categories: any[] = [];
  let totalItems = 0;
  
  // CATEGORY 1: ENLISTMENT RECORDS (everyone needs these)
  categories.push({
    name: 'Enlistment Records',
    type: 'enlistment',
    description: 'Documents from your initial entry into service',
    priority: 'critical',
    order: 1,
    items: [
      {
        name: 'ASVAB Test Scores',
        type: 'test_results',
        description: 'Armed Services Vocational Aptitude Battery scores',
        source: 'MEPS or Recruiting Station',
        priority: 'medium',
        required: false
      },
      {
        name: 'MEPS Physical Examination',
        type: 'medical',
        description: 'Initial physical exam results',
        source: 'MEPS Station',
        priority: 'high',
        required: true
      },
      {
        name: 'Enlistment Contract (DD Form 4)',
        type: 'contract',
        description: 'Your enlistment or reenlistment contract',
        source: 'OMPF',
        priority: 'critical',
        required: true
      },
      {
        name: 'Security Clearance Application (SF-86)',
        type: 'security',
        description: 'If you had a security clearance',
        source: 'NARA',
        priority: 'medium',
        required: false
      },
      {
        name: 'Oath of Enlistment Certificate',
        type: 'certificate',
        description: 'Certificate from swearing-in ceremony',
        source: 'Personal files or recruiting station',
        priority: 'low',
        required: false
      },
      {
        name: 'Orders to Basic Training',
        type: 'orders',
        description: 'Assignment orders to initial training',
        source: 'OMPF',
        priority: 'high',
        required: true
      }
    ]
  });
  totalItems += 6;
  
  // CATEGORY 2: BASIC TRAINING
  categories.push({
    name: 'Basic Training Records',
    type: 'basic_training',
    description: 'Records from Basic Combat Training or Boot Camp',
    priority: 'high',
    order: 2,
    items: [
      {
        name: 'Training Orders',
        type: 'orders',
        description: 'Orders assigning you to basic training',
        source: 'OMPF',
        priority: 'high',
        required: true
      },
      {
        name: 'Training Company Roster',
        type: 'roster',
        description: 'List of trainees in your company',
        source: 'Training Battalion',
        priority: 'low',
        required: false
      },
      {
        name: 'Physical Fitness Test Scores',
        type: 'test_results',
        description: 'Initial and final PFT/APFT scores',
        source: 'Training records',
        priority: 'medium',
        required: false
      },
      {
        name: 'Weapons Qualification Scores',
        type: 'qualification',
        description: 'Rifle marksmanship qualification',
        source: 'Training records',
        priority: 'medium',
        required: false
      },
      {
        name: 'Sick Call Records',
        type: 'medical',
        description: 'Any injuries or medical treatment during training',
        source: 'Training battalion medical records',
        priority: 'high',
        required: true
      },
      {
        name: 'Graduation Certificate',
        type: 'certificate',
        description: 'Basic training completion certificate',
        source: 'Personal files or training battalion',
        priority: 'medium',
        required: false
      }
    ]
  });
  totalItems += 6;
  
  // CATEGORY 3: AIT/TECHNICAL TRAINING
  categories.push({
    name: 'Advanced Individual Training (AIT)',
    type: 'ait',
    description: 'Military Occupational Specialty training',
    priority: 'high',
    order: 3,
    items: [
      {
        name: 'AIT Orders',
        type: 'orders',
        description: 'Orders to MOS school',
        source: 'OMPF',
        priority: 'high',
        required: true
      },
      {
        name: 'MOS Training Curriculum',
        type: 'curriculum',
        description: 'Course outline and training plan',
        source: 'School house',
        priority: 'low',
        required: false
      },
      {
        name: 'Test Scores',
        type: 'test_results',
        description: 'Written and practical exam scores',
        source: 'School records',
        priority: 'medium',
        required: false
      },
      {
        name: 'Skills Qualification Records',
        type: 'qualification',
        description: 'Certification of MOS qualification',
        source: 'School house',
        priority: 'high',
        required: true
      },
      {
        name: 'AIT Graduation Certificate',
        type: 'certificate',
        description: 'MOS school completion certificate',
        source: 'Personal files or school house',
        priority: 'medium',
        required: false
      }
    ]
  });
  totalItems += 5;
  
  // CATEGORY 4: SPECIALIZED SCHOOLS (if applicable)
  if (params.specializations.length > 0) {
    categories.push({
      name: 'Specialized Training Schools',
      type: 'specialized_schools',
      description: 'Airborne, Ranger, Special Forces, or other specialized training',
      priority: 'high',
      order: 4,
      items: params.specializations.flatMap(school => [
        {
          name: `${school} - Assignment Orders`,
          type: 'orders',
          description: `Orders to ${school}`,
          source: 'OMPF',
          priority: 'high',
          required: true
        },
        {
          name: `${school} - Graduation Certificate`,
          type: 'certificate',
          description: `Completion certificate`,
          source: 'Personal files or school',
          priority: 'medium',
          required: false
        },
        {
          name: `${school} - Training Records`,
          type: 'training_records',
          description: `Test scores and performance evaluations`,
          source: 'School house',
          priority: 'low',
          required: false
        }
      ])
    });
    totalItems += params.specializations.length * 3;
  }
  
  // CATEGORY 5: DUTY STATIONS (critical - generates 18 items per station)
  const estimatedStations = Math.ceil((params.serviceDates.activeYears || 4) / 2); // ~2 years per station
  categories.push({
    name: 'Duty Station Records',
    type: 'duty_stations',
    description: 'Records from each permanent duty station',
    priority: 'critical',
    order: 5,
    items: [
      // These are template items - will be multiplied per duty station
      {
        name: 'PCS Orders (Permanent Change of Station)',
        type: 'orders',
        description: 'Orders assigning you to this station',
        source: 'OMPF or Unit S-1',
        priority: 'critical',
        required: true
      },
      {
        name: 'Unit Assignment Orders',
        type: 'orders',
        description: 'Assignment to specific unit/company',
        source: 'Unit S-1',
        priority: 'high',
        required: true
      },
      {
        name: 'Morning Reports',
        type: 'unit_records',
        description: 'Daily unit status reports showing your presence',
        source: 'Unit records or NARA',
        priority: 'high',
        required: true
      },
      {
        name: 'NCOER/OER (Evaluation Reports)',
        type: 'performance',
        description: 'Performance evaluation reports',
        source: 'OMPF',
        priority: 'critical',
        required: true
      },
      {
        name: 'Counseling Statements',
        type: 'administrative',
        description: 'Positive and negative counseling',
        source: 'Personnel file',
        priority: 'medium',
        required: false
      },
      {
        name: 'Awards/Commendations',
        type: 'awards',
        description: 'Any medals or awards earned at this station',
        source: 'OMPF',
        priority: 'medium',
        required: false
      },
      {
        name: 'Medical Records - Sick Call',
        type: 'medical',
        description: 'All medical visits while at this station',
        source: 'Base medical facility',
        priority: 'critical',
        required: true
      },
      {
        name: 'Physical Therapy Records',
        type: 'medical',
        description: 'PT for any injuries',
        source: 'Base medical facility',
        priority: 'high',
        required: false
      },
      {
        name: 'Line of Duty Determinations',
        type: 'medical',
        description: 'LOD investigations for injuries',
        source: 'Unit commander or JAG',
        priority: 'critical',
        required: true
      },
      {
        name: 'Training Records',
        type: 'training',
        description: 'Range qualifications, certifications',
        source: 'Unit S-3 training office',
        priority: 'medium',
        required: false
      },
      {
        name: 'Hazard Exposure Map',
        type: 'map',
        description: 'Geographic map showing proximity to burn pits, contamination',
        source: 'Auto-generated by system',
        priority: 'critical',
        required: true
      }
    ]
  });
  totalItems += 11 * estimatedStations;
  
  // CATEGORY 6: DEPLOYMENTS (if applicable)
  if (params.deployments.length > 0) {
    categories.push({
      name: 'Deployment Records',
      type: 'deployments',
      description: 'Combat and overseas deployment documentation',
      priority: 'critical',
      order: 6,
      items: params.deployments.flatMap(deployment => [
        {
          name: `${deployment} - Deployment Orders`,
          type: 'orders',
          description: 'Orders to deploy',
          source: 'Unit S-1 or theater command',
          priority: 'critical',
          required: true
        },
        {
          name: `${deployment} - Pre-Deployment Health Assessment`,
          type: 'medical',
          description: 'Medical screening before deployment',
          source: 'Medical facility',
          priority: 'high',
          required: true
        },
        {
          name: `${deployment} - After-Action Reports`,
          type: 'unit_records',
          description: 'Unit operations reports',
          source: 'Unit S-3 or command',
          priority: 'high',
          required: false
        },
        {
          name: `${deployment} - Field Medical Records`,
          type: 'medical',
          description: 'Any medical treatment while deployed',
          source: 'Theater medical command',
          priority: 'critical',
          required: true
        },
        {
          name: `${deployment} - Post-Deployment Health Assessment (PDHA)`,
          type: 'medical',
          description: 'Medical screening upon return',
          source: 'Medical facility',
          priority: 'critical',
          required: true
        },
        {
          name: `${deployment} - Post-Deployment Health Reassessment (PDHRA)`,
          type: 'medical',
          description: '90-180 days after return',
          source: 'Medical facility',
          priority: 'critical',
          required: true
        },
        {
          name: `${deployment} - Combat Awards`,
          type: 'awards',
          description: 'CIB, CAB, BSM, etc.',
          source: 'OMPF',
          priority: 'high',
          required: false
        },
        {
          name: `${deployment} - Burn Pit Registry`,
          type: 'exposure',
          description: 'Documentation of burn pit proximity',
          source: 'VA Burn Pit Registry or system-generated',
          priority: 'critical',
          required: true
        }
      ])
    });
    totalItems += params.deployments.length * 8;
  }
  
  // CATEGORY 7: MEDICAL RECORDS (everyone)
  categories.push({
    name: 'Complete Medical Records',
    type: 'medical_records',
    description: 'All medical documentation from enlistment to separation',
    priority: 'critical',
    order: 7,
    items: [
      {
        name: 'Enlistment Physical (MEPS)',
        type: 'medical',
        description: 'Initial entry physical',
        source: 'MEPS',
        priority: 'critical',
        required: true
      },
      {
        name: 'Annual Physical Exams',
        type: 'medical',
        description: 'Yearly physicals',
        source: 'Base medical facilities',
        priority: 'high',
        required: true
      },
      {
        name: 'All Sick Call Records',
        type: 'medical',
        description: 'Every medical visit during service',
        source: 'All medical facilities',
        priority: 'critical',
        required: true
      },
      {
        name: 'Hospital Records',
        type: 'medical',
        description: 'Inpatient stays',
        source: 'Military hospitals',
        priority: 'critical',
        required: true
      },
      {
        name: 'Surgical Records',
        type: 'medical',
        description: 'Any surgeries',
        source: 'Military hospitals',
        priority: 'critical',
        required: true
      },
      {
        name: 'Radiology Reports',
        type: 'medical',
        description: 'X-rays, MRIs, CT scans',
        source: 'Medical facilities',
        priority: 'high',
        required: false
      },
      {
        name: 'Laboratory Results',
        type: 'medical',
        description: 'Blood work, tests',
        source: 'Medical facilities',
        priority: 'medium',
        required: false
      },
      {
        name: 'Dental Records',
        type: 'medical',
        description: 'All dental treatment',
        source: 'Dental clinics',
        priority: 'low',
        required: false
      },
      {
        name: 'Mental Health Records',
        type: 'medical',
        description: 'Behavioral health visits',
        source: 'Mental health clinics',
        priority: 'critical',
        required: true
      },
      {
        name: 'Separation Physical Exam',
        type: 'medical',
        description: 'Final physical before discharge',
        source: 'Separation facility',
        priority: 'critical',
        required: true
      },
      {
        name: 'VA Blue Button Records',
        type: 'medical',
        description: 'All post-service VA medical records',
        source: 'VA.gov Blue Button',
        priority: 'critical',
        required: true
      }
    ]
  });
  totalItems += 11;
  
  // CATEGORY 8: SEPARATION RECORDS
  categories.push({
    name: 'Separation/Retirement Records',
    type: 'separation',
    description: 'Final discharge or retirement documentation',
    priority: 'critical',
    order: 8,
    items: [
      {
        name: 'DD Form 214 (Report of Separation)',
        type: 'discharge',
        description: 'Your discharge paperwork',
        source: 'Personal copy',
        priority: 'critical',
        required: true
      },
      {
        name: 'DD Form 215 (Corrections to DD214)',
        type: 'discharge',
        description: 'If your DD214 was corrected',
        source: 'Personal files',
        priority: 'high',
        required: false
      },
      {
        name: 'Separation Orders',
        type: 'orders',
        description: 'Orders authorizing your discharge',
        source: 'OMPF',
        priority: 'high',
        required: true
      },
      {
        name: 'Transition Assistance Program (TAP) Certificate',
        type: 'certificate',
        description: 'Proof of TAP completion',
        source: 'Personal files',
        priority: 'low',
        required: false
      },
      {
        name: 'VA Benefits Briefing Attendance',
        type: 'certificate',
        description: 'Pre-separation VA briefing',
        source: 'Personal files',
        priority: 'medium',
        required: false
      }
    ]
  });
  totalItems += 5;
  
  return {
    categories,
    totalItems,
    estimatedCompletionTime: `${Math.ceil(totalItems / 10)} weeks` // ~10 docs per week
  };
}

// ============================================================================
// GENERATE SF-180 FORM FOR NARA REQUEST
// ============================================================================

export async function generateSF180Form(params: {
  veteran: any,
  requestType: string,
  documents: string[]
}) {
  // Generate pre-filled SF-180 form as PDF
  // This would use a PDF generation library like pdf-lib or pdfmake
  
  const formData = {
    veteranName: params.veteran.name,
    ssn: params.veteran.ssn, // Encrypted
    branch: params.veteran.branch,
    serviceDates: `${params.veteran.serviceDates.enlistment} to ${params.veteran.serviceDates.separation}`,
    requestType: params.requestType,
    documents: params.documents.join(', '),
    requestDate: new Date().toLocaleDateString(),
    naraAddress: '1 Archives Drive, St. Louis, MO 63138',
    instructions: [
      'Complete sections 1-3 of this form',
      'Sign and date section 5',
      'Mail or fax to NARA',
      'Include copy of DD214 if available',
      'Typical response time: 90-120 days'
    ]
  };
  
  // Generate PDF (pseudo-code)
  const pdfBuffer = await createSF180PDF(formData);
  
  // Upload to S3
  const s3Path = await uploadToS3(pdfBuffer, `nara-requests/${params.veteran.id}/sf180.pdf`);
  
  // Generate cover letter
  const coverLetter = await generateCoverLetter(formData);
  const coverLetterPath = await uploadToS3(coverLetter, `nara-requests/${params.veteran.id}/cover-letter.pdf`);
  
  return {
    s3Path,
    coverLetterPath,
    downloadUrl: `https://s3.amazonaws.com/victory-protocol/${s3Path}`,
    coverLetterUrl: `https://s3.amazonaws.com/victory-protocol/${coverLetterPath}`
  };
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function parseDutyStations(rawData: any[]): any[] {
  return rawData.map(station => ({
    name: station.name,
    baseName: extractBaseName(station.name),
    location: parseLocation(station.location),
    dates: {
      arrival: station.arrivalDate,
      departure: station.departureDate,
      durationDays: calculateDays(station.arrivalDate, station.departureDate)
    },
    unit: station.unit,
    mos: station.mos,
    rank: station.rank
  }));
}

function extractBaseName(fullName: string): string {
  // Extract just the base name without "Fort", "Camp", etc.
  return fullName.replace(/^(Fort|Camp|Naval Base|Air Force Base|Marine Corps Base)\s+/i, '');
}

function parseLocation(locationString: string): any {
  // Parse location string into structured data
  // This would use geocoding API
  return {
    address: locationString,
    city: '',
    state: '',
    country: 'USA',
    lat: 0,
    long: 0
  };
}

function calculateDays(start: string, end: string): number {
  const startDate = new Date(start);
  const endDate = new Date(end);
  const diffTime = Math.abs(endDate.getTime() - startDate.getTime());
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

async function getFileContent(fileId: string): Promise<string> {
  // Retrieve file from S3 and convert to base64
  // Implementation depends on your file storage system
  return '';
}

async function createSF180PDF(data: any): Promise<Buffer> {
  // Generate PDF using pdf-lib or similar
  // This would fill out the actual SF-180 form
  return Buffer.from('');
}

async function generateCoverLetter(data: any): Promise<Buffer> {
  // Generate cover letter explaining the request
  return Buffer.from('');
}

async function uploadToS3(buffer: Buffer, path: string): Promise<string> {
  // Upload to S3 and return path
  return path;
}
