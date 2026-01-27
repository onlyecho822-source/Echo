/**
 * ART OF PROOF: HAZARD MAPPING SERVICE
 * Maps duty stations to known military hazard exposures
 */

import { db } from '../database';

// ============================================================================
// TYPES
// ============================================================================

interface Location {
  lat: number;
  lng: number;
}

interface DutyPeriod {
  start: string; // ISO date
  end: string;   // ISO date
}

interface HazardExposure {
  type: string;
  name: string;
  source: string;
  distance: number; // meters
  exposureDays: number;
  severity: 'low' | 'medium' | 'high' | 'extreme';
  presumptive: boolean;
  pactActCovered: boolean;
  documentationLevel: 'confirmed' | 'probable' | 'possible';
  evidenceSource: string;
}

// ============================================================================
// MAIN HAZARD QUERY FUNCTION
// ============================================================================

export async function queryHazardDatabases(params: {
  location: Location;
  baseName?: string;
  dates: DutyPeriod;
}): Promise<HazardExposure[]> {
  const hazards: HazardExposure[] = [];
  
  try {
    // Check burn pit registry
    const burnPits = await checkBurnPitProximity(params.location, params.dates);
    hazards.push(...burnPits);
    
    // Check Agent Orange zones (Vietnam era)
    if (isVietnamEra(params.dates)) {
      const agentOrange = await checkAgentOrangeZones(params.location, params.baseName);
      hazards.push(...agentOrange);
    }
    
    // Check Camp Lejeune contamination
    if (params.baseName?.toLowerCase().includes('lejeune')) {
      const contamination = await checkCampLejeuneContamination(params.dates);
      hazards.push(...contamination);
    }
    
    // Check radiation sites
    const radiation = await checkRadiationSites(params.location, params.dates);
    hazards.push(...radiation);
    
    // Check base hazard database
    const baseHazards = await checkBaseHazardDatabase(params.baseName, params.dates);
    hazards.push(...baseHazards);
    
    return hazards;
    
  } catch (error) {
    console.error('Error querying hazard databases:', error);
    return [];
  }
}

// ============================================================================
// BURN PIT PROXIMITY CHECK
// ============================================================================

async function checkBurnPitProximity(
  location: Location,
  dates: DutyPeriod
): Promise<HazardExposure[]> {
  const hazards: HazardExposure[] = [];
  
  // Query burn pit locations within 5km radius
  const burnPits = await db.query(`
    SELECT *,
      (6371000 * acos(
        cos(radians(?)) * cos(radians(latitude)) *
        cos(radians(longitude) - radians(?)) +
        sin(radians(?)) * sin(radians(latitude))
      )) AS distance
    FROM burn_pit_locations
    WHERE start_date <= ? AND (end_date >= ? OR end_date IS NULL)
    HAVING distance <= 5000
    ORDER BY distance
  `, [location.lat, location.lng, location.lat, dates.end, dates.start]);
  
  for (const pit of burnPits) {
    const exposureDays = calculateOverlapDays(
      dates,
      { start: pit.start_date, end: pit.end_date || dates.end }
    );
    
    // Determine severity based on distance
    let severity: 'low' | 'medium' | 'high' | 'extreme';
    if (pit.distance <= pit.extreme_zone_meters) severity = 'extreme';
    else if (pit.distance <= pit.high_zone_meters) severity = 'high';
    else if (pit.distance <= pit.medium_zone_meters) severity = 'medium';
    else severity = 'low';
    
    hazards.push({
      type: 'burn_pit',
      name: `Burn Pit at ${pit.location_name}`,
      source: `${pit.base_name} burn pit operations`,
      distance: Math.round(pit.distance),
      exposureDays,
      severity,
      presumptive: pit.va_recognized,
      pactActCovered: pit.pact_act_covered,
      documentationLevel: 'confirmed',
      evidenceSource: 'VA Burn Pit Registry'
    });
  }
  
  return hazards;
}

// ============================================================================
// AGENT ORANGE ZONES
// ============================================================================

async function checkAgentOrangeZones(
  location: Location,
  baseName?: string
): Promise<HazardExposure[]> {
  const hazards: HazardExposure[] = [];
  
  // Agent Orange presumptive locations
  const presumptiveLocations = [
    'Vietnam',
    'Thailand',
    'Laos',
    'Cambodia',
    'Korean DMZ',
    'Johnston Atoll'
  ];
  
  // Check if base name matches any presumptive location
  if (baseName) {
    for (const loc of presumptiveLocations) {
      if (baseName.toLowerCase().includes(loc.toLowerCase())) {
        hazards.push({
          type: 'agent_orange',
          name: 'Agent Orange Exposure',
          source: `Service in ${loc}`,
          distance: 0,
          exposureDays: 365, // Presumptive for entire period
          severity: 'high',
          presumptive: true,
          pactActCovered: true,
          documentationLevel: 'confirmed',
          evidenceSource: '38 CFR § 3.307(a)(6)'
        });
        break;
      }
    }
  }
  
  // Check geographic coordinates for Vietnam
  // Vietnam: roughly 8°N-24°N, 102°E-110°E
  if (location.lat >= 8 && location.lat <= 24 &&
      location.lng >= 102 && location.lng <= 110) {
    hazards.push({
      type: 'agent_orange',
      name: 'Agent Orange Exposure - Vietnam Service',
      source: 'Service in Republic of Vietnam',
      distance: 0,
      exposureDays: 365,
      severity: 'high',
      presumptive: true,
      pactActCovered: true,
      documentationLevel: 'confirmed',
      evidenceSource: '38 CFR § 3.307(a)(6)'
    });
  }
  
  return hazards;
}

// ============================================================================
// CAMP LEJEUNE CONTAMINATED WATER
// ============================================================================

async function checkCampLejeuneContamination(
  dates: DutyPeriod
): Promise<HazardExposure[]> {
  const hazards: HazardExposure[] = [];
  
  // Camp Lejeune contamination period: August 1953 - December 1987
  const contaminationStart = new Date('1953-08-01');
  const contaminationEnd = new Date('1987-12-31');
  const dutyStart = new Date(dates.start);
  const dutyEnd = new Date(dates.end);
  
  // Check if duty period overlaps with contamination period
  if (dutyStart <= contaminationEnd && dutyEnd >= contaminationStart) {
    const exposureDays = calculateOverlapDays(
      dates,
      { start: '1953-08-01', end: '1987-12-31' }
    );
    
    // Minimum 30 days for presumptive status
    if (exposureDays >= 30) {
      hazards.push({
        type: 'contaminated_water',
        name: 'Camp Lejeune Contaminated Water Exposure',
        source: 'Contaminated drinking water (TCE, PCE, Benzene)',
        distance: 0,
        exposureDays,
        severity: 'high',
        presumptive: true,
        pactActCovered: true,
        documentationLevel: 'confirmed',
        evidenceSource: 'Camp Lejeune Family Member Program (38 U.S.C. § 1787)'
      });
    }
  }
  
  return hazards;
}

// ============================================================================
// RADIATION SITES
// ============================================================================

async function checkRadiationSites(
  location: Location,
  dates: DutyPeriod
): Promise<HazardExposure[]> {
  const hazards: HazardExposure[] = [];
  
  // Nuclear testing sites
  const radiationSites = [
    {
      name: 'Nevada Test Site',
      lat: 37.1,
      lng: -116.0,
      radius: 100000, // 100km
      period: { start: '1951-01-01', end: '1992-12-31' }
    },
    {
      name: 'Marshall Islands - Enewetak',
      lat: 11.5,
      lng: 162.3,
      radius: 50000,
      period: { start: '1946-01-01', end: '1980-12-31' }
    },
    {
      name: 'Marshall Islands - Bikini Atoll',
      lat: 11.6,
      lng: 165.4,
      radius: 50000,
      period: { start: '1946-01-01', end: '1980-12-31' }
    }
  ];
  
  for (const site of radiationSites) {
    const distance = calculateDistance(location, { lat: site.lat, lng: site.lng });
    
    if (distance <= site.radius) {
      const exposureDays = calculateOverlapDays(dates, site.period);
      
      if (exposureDays > 0) {
        hazards.push({
          type: 'radiation',
          name: `Radiation Exposure - ${site.name}`,
          source: 'Atmospheric nuclear testing operations',
          distance: Math.round(distance),
          exposureDays,
          severity: distance < 10000 ? 'extreme' : 'high',
          presumptive: true,
          pactActCovered: true,
          documentationLevel: 'probable',
          evidenceSource: '38 CFR § 3.309'
        });
      }
    }
  }
  
  return hazards;
}

// ============================================================================
// BASE HAZARD DATABASE
// ============================================================================

async function checkBaseHazardDatabase(
  baseName: string | undefined,
  dates: DutyPeriod
): Promise<HazardExposure[]> {
  if (!baseName) return [];
  
  const hazards: HazardExposure[] = [];
  
  // Query base hazard database
  const baseHazards = await db.query(`
    SELECT * FROM base_hazard_database
    WHERE base_name LIKE ?
      AND hazard_start_date <= ?
      AND (hazard_end_date >= ? OR hazard_end_date IS NULL)
  `, [`%${baseName}%`, dates.end, dates.start]);
  
  for (const record of baseHazards) {
    const hazardList = JSON.parse(record.hazards || '[]');
    
    for (const hazard of hazardList) {
      const exposureDays = calculateOverlapDays(
        dates,
        { start: record.hazard_start_date, end: record.hazard_end_date || dates.end }
      );
      
      hazards.push({
        type: hazard.type || 'other',
        name: hazard.name,
        source: hazard.source || record.base_name,
        distance: 0,
        exposureDays,
        severity: hazard.severity || 'medium',
        presumptive: record.va_presumptive || false,
        pactActCovered: hazard.pactActCovered || false,
        documentationLevel: 'confirmed',
        evidenceSource: record.source || 'Base Environmental Records'
      });
    }
  }
  
  return hazards;
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function isVietnamEra(dates: DutyPeriod): boolean {
  const vietnamStart = new Date('1961-01-01');
  const vietnamEnd = new Date('1975-04-30');
  const dutyStart = new Date(dates.start);
  const dutyEnd = new Date(dates.end);
  
  return dutyStart <= vietnamEnd && dutyEnd >= vietnamStart;
}

function calculateDistance(loc1: Location, loc2: Location): number {
  // Haversine formula for distance in meters
  const R = 6371000; // Earth radius in meters
  const φ1 = (loc1.lat * Math.PI) / 180;
  const φ2 = (loc2.lat * Math.PI) / 180;
  const Δφ = ((loc2.lat - loc1.lat) * Math.PI) / 180;
  const Δλ = ((loc2.lng - loc1.lng) * Math.PI) / 180;
  
  const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  
  return R * c;
}

function calculateOverlapDays(period1: DutyPeriod, period2: DutyPeriod): number {
  const start1 = new Date(period1.start);
  const end1 = new Date(period1.end);
  const start2 = new Date(period2.start);
  const end2 = new Date(period2.end);
  
  const overlapStart = start1 > start2 ? start1 : start2;
  const overlapEnd = end1 < end2 ? end1 : end2;
  
  if (overlapStart > overlapEnd) return 0;
  
  const diffTime = Math.abs(overlapEnd.getTime() - overlapStart.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  return diffDays;
}

// ============================================================================
// SEED DATA FOR BURN PIT REGISTRY
// ============================================================================

export const BURN_PIT_SEED_DATA = [
  {
    location_name: 'Balad Air Base',
    base_name: 'Balad Air Base',
    country: 'Iraq',
    latitude: 33.9402,
    longitude: 44.3616,
    start_date: '2003-03-01',
    end_date: '2011-12-31',
    pit_size_meters: 500,
    materials_burned: JSON.stringify(['Medical waste', 'Chemical waste', 'Plastics', 'Electronics', 'Human waste']),
    operating_hours: '24/7',
    extreme_zone_meters: 300,
    high_zone_meters: 1000,
    medium_zone_meters: 2000,
    va_recognized: true,
    pact_act_covered: true
  },
  {
    location_name: 'Joint Base Balad',
    base_name: 'Joint Base Balad',
    country: 'Iraq',
    latitude: 33.9408,
    longitude: 44.3619,
    start_date: '2003-04-01',
    end_date: '2011-12-15',
    pit_size_meters: 400,
    materials_burned: JSON.stringify(['Munitions', 'Tires', 'Batteries', 'Fuel']),
    operating_hours: '24/7',
    extreme_zone_meters: 300,
    high_zone_meters: 1000,
    medium_zone_meters: 2000,
    va_recognized: true,
    pact_act_covered: true
  },
  {
    location_name: 'Bagram Airfield',
    base_name: 'Bagram Airfield',
    country: 'Afghanistan',
    latitude: 34.9461,
    longitude: 69.2650,
    start_date: '2001-12-01',
    end_date: '2021-07-01',
    pit_size_meters: 600,
    materials_burned: JSON.stringify(['Medical waste', 'Plastics', 'Electronics', 'Food waste']),
    operating_hours: '24/7',
    extreme_zone_meters: 500,
    high_zone_meters: 1500,
    medium_zone_meters: 3000,
    va_recognized: true,
    pact_act_covered: true
  },
  {
    location_name: 'Camp Victory',
    base_name: 'Camp Victory',
    country: 'Iraq',
    latitude: 33.2850,
    longitude: 44.2300,
    start_date: '2003-05-01',
    end_date: '2011-12-01',
    pit_size_meters: 300,
    materials_burned: JSON.stringify(['General waste', 'Plastics', 'Wood']),
    operating_hours: 'Daylight only',
    extreme_zone_meters: 200,
    high_zone_meters: 800,
    medium_zone_meters: 1500,
    va_recognized: true,
    pact_act_covered: true
  }
];

// ============================================================================
// MOS HAZARD MAPPING DATA
// ============================================================================

export const MOS_HAZARD_DATA = {
  // Infantry
  '11B': {
    physical_demands: ['Heavy equipment carrying (60+ lbs)', 'Extended ruck marches', 'Combat operations'],
    noise_hazards: ['Small arms fire (140+ dB)', 'Artillery (180+ dB)', 'Explosive breaching'],
    chemical_hazards: ['CS gas training', 'Weapons cleaning solvents', 'Propellant residue'],
    injury_risks: ['Lower back strain', 'Knee injuries', 'Hearing loss', 'TBI', 'PTSD']
  },
  
  // Wheeled Vehicle Mechanic
  '63B': {
    physical_demands: ['Heavy tool use', 'Awkward working positions', 'Repetitive motion'],
    noise_hazards: ['Pneumatic tools (100+ dB)', 'Engine testing (90+ dB)'],
    chemical_hazards: ['Diesel fumes', 'Hydraulic fluid', 'Solvents', 'Asbestos (brake dust)'],
    injury_risks: ['Back strain', 'Carpal tunnel', 'Respiratory conditions', 'Hearing loss']
  },
  
  // Motor Transport Operator
  '88M': {
    physical_demands: ['Long-haul driving', 'Loading/unloading', 'Vehicle maintenance'],
    noise_hazards: ['Engine noise (85+ dB for 8+ hrs)', 'Air brake systems'],
    chemical_hazards: ['Diesel exhaust', 'Burn pit smoke (convoy routes)'],
    injury_risks: ['Lower back pain', 'Sleep disorders', 'Respiratory conditions', 'PTSD (IED exposure)']
  },
  
  // Military Police
  '31B': {
    physical_demands: ['Extended standing', 'Physical restraint', 'Equipment carrying'],
    noise_hazards: ['Small arms training', 'Patrol vehicle sirens'],
    chemical_hazards: ['OC spray exposure', 'Vehicle exhaust'],
    injury_risks: ['Knee injuries', 'PTSD', 'Hearing loss', 'Back strain']
  }
};
