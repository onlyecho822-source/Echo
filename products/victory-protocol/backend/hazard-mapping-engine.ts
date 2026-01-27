/**
 * HAZARD MAPPING ENGINE
 * Maps duty stations and deployments to known hazard exposures
 */

interface Location {
  lat: number;
  long: number;
  baseName?: string;
}

interface DateRange {
  start: string;
  end: string;
}

interface HazardExposure {
  type: string;
  source: string;
  distance: number;
  exposureDays: number;
  severity: 'low' | 'medium' | 'high' | 'extreme';
  presumptive: boolean;
  pactActCovered: boolean;
}

// ============================================================================
// BURN PIT DATABASE (Major locations in Iraq/Afghanistan)
// ============================================================================

const BURN_PIT_LOCATIONS = [
  {
    name: 'Balad Air Base Burn Pit',
    base: 'Balad Air Base',
    country: 'Iraq',
    coords: { lat: 33.9402, long: 44.3618 },
    active: { start: '2003-04-01', end: '2011-12-15' },
    severity: 'extreme' as const,
    distance: 800, // meters from main base
    conditions: ['Respiratory disease', 'Chronic bronchitis', 'Asthma', 'Rhinitis', 'Sinusitis']
  },
  {
    name: 'Bagram Airfield Burn Pit',
    base: 'Bagram Airfield',
    country: 'Afghanistan',
    coords: { lat: 34.9459, long: 69.2647 },
    active: { start: '2001-12-01', end: '2021-07-02' },
    severity: 'extreme' as const,
    distance: 500,
    conditions: ['Respiratory disease', 'Chronic bronchitis', 'Asthma']
  },
  {
    name: 'Camp Anaconda Burn Pit',
    base: 'Camp Anaconda',
    country: 'Iraq',
    coords: { lat: 33.7722, long: 44.3608 },
    active: { start: '2003-05-01', end: '2011-09-01' },
    severity: 'extreme' as const,
    distance: 1000,
    conditions: ['Respiratory disease', 'Chronic bronchitis']
  },
  {
    name: 'Camp Victory Burn Pit',
    base: 'Camp Victory',
    country: 'Iraq',
    coords: { lat: 33.2945, long: 44.2294 },
    active: { start: '2003-04-01', end: '2011-12-15' },
    severity: 'high' as const,
    distance: 1200,
    conditions: ['Respiratory disease']
  },
  {
    name: 'Kandahar Airfield Burn Pit',
    base: 'Kandahar Airfield',
    country: 'Afghanistan',
    coords: { lat: 31.5058, long: 65.8478 },
    active: { start: '2001-12-01', end: '2021-08-01' },
    severity: 'extreme' as const,
    distance: 600,
    conditions: ['Respiratory disease', 'Chronic bronchitis', 'Asthma']
  },
];

// ============================================================================
// CONTAMINATED WATER DATABASE
// ============================================================================

const CONTAMINATED_WATER_LOCATIONS = [
  {
    name: 'Camp Lejeune Water Contamination',
    base: 'Camp Lejeune',
    country: 'USA',
    coords: { lat: 34.7026, long: -77.3642 },
    active: { start: '1953-01-01', end: '1987-12-31' },
    severity: 'extreme' as const,
    contaminants: ['TCE', 'PCE', 'Benzene'],
    conditions: ['Kidney cancer', 'Liver cancer', 'Multiple myeloma', 'Leukemia', 'Bladder cancer']
  },
];

// ============================================================================
// AGENT ORANGE LOCATIONS (Vietnam)
// ============================================================================

const AGENT_ORANGE_LOCATIONS = [
  {
    name: 'Vietnam - Entire Country',
    country: 'Vietnam',
    active: { start: '1962-01-01', end: '1975-05-07' },
    severity: 'extreme' as const,
    conditions: ['Type 2 diabetes', 'Ischemic heart disease', 'Multiple cancers', 'Parkinson disease']
  },
  {
    name: 'Korea DMZ',
    country: 'South Korea',
    region: 'DMZ',
    active: { start: '1968-01-01', end: '1971-08-31' },
    severity: 'high' as const,
    conditions: ['Type 2 diabetes', 'Ischemic heart disease', 'Multiple cancers']
  },
];

// ============================================================================
// CORE FUNCTIONS
// ============================================================================

/**
 * Calculate distance between two coordinates (Haversine formula)
 */
function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371e3; // Earth's radius in meters
  const φ1 = lat1 * Math.PI / 180;
  const φ2 = lat2 * Math.PI / 180;
  const Δφ = (lat2 - lat1) * Math.PI / 180;
  const Δλ = (lon2 - lon1) * Math.PI / 180;

  const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
          Math.cos(φ1) * Math.cos(φ2) *
          Math.sin(Δλ/2) * Math.sin(Δλ/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

  return R * c; // Distance in meters
}

/**
 * Calculate overlap days between two date ranges
 */
function calculateOverlapDays(range1: DateRange, range2: DateRange): number {
  const start1 = new Date(range1.start);
  const end1 = new Date(range1.end);
  const start2 = new Date(range2.start);
  const end2 = new Date(range2.end);

  const overlapStart = start1 > start2 ? start1 : start2;
  const overlapEnd = end1 < end2 ? end1 : end2;

  if (overlapStart > overlapEnd) return 0;

  const diffTime = Math.abs(overlapEnd.getTime() - overlapStart.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  return diffDays;
}

/**
 * Check if veteran served during Vietnam era
 */
function isVietnamEra(dates: DateRange): boolean {
  const vietnamStart = new Date('1962-01-01');
  const vietnamEnd = new Date('1975-05-07');
  const serviceStart = new Date(dates.start);
  const serviceEnd = new Date(dates.end);

  return (serviceStart <= vietnamEnd && serviceEnd >= vietnamStart);
}

/**
 * Query burn pit exposures for a location
 */
export async function checkBurnPitProximity(
  location: Location, 
  dates: DateRange
): Promise<HazardExposure[]> {
  const hazards: HazardExposure[] = [];

  for (const burnPit of BURN_PIT_LOCATIONS) {
    // Check if base name matches (if provided)
    if (location.baseName) {
      const baseMatch = location.baseName.toLowerCase().includes(burnPit.base.toLowerCase()) ||
                       burnPit.base.toLowerCase().includes(location.baseName.toLowerCase());
      
      if (!baseMatch) continue;
    } else {
      // Calculate distance if coordinates provided
      const distance = calculateDistance(
        location.lat,
        location.long,
        burnPit.coords.lat,
        burnPit.coords.long
      );

      // If > 10km away, skip
      if (distance > 10000) continue;
    }

    // Calculate exposure days
    const exposureDays = calculateOverlapDays(dates, burnPit.active);
    
    if (exposureDays > 0) {
      hazards.push({
        type: 'burn_pit',
        source: burnPit.name,
        distance: burnPit.distance,
        exposureDays,
        severity: burnPit.severity,
        presumptive: true, // PACT Act coverage
        pactActCovered: true
      });
    }
  }

  return hazards;
}

/**
 * Check Agent Orange exposure
 */
export async function checkAgentOrangeExposure(
  location: { country: string },
  dates: DateRange
): Promise<HazardExposure[]> {
  const hazards: HazardExposure[] = [];

  for (const agentOrange of AGENT_ORANGE_LOCATIONS) {
    if (location.country.toLowerCase() !== agentOrange.country.toLowerCase()) {
      continue;
    }

    const exposureDays = calculateOverlapDays(dates, agentOrange.active);
    
    if (exposureDays > 0) {
      hazards.push({
        type: 'agent_orange',
        source: agentOrange.name,
        distance: 0, // In-zone
        exposureDays,
        severity: agentOrange.severity,
        presumptive: true, // VA presumptive list
        pactActCovered: false // Different program
      });
    }
  }

  return hazards;
}

/**
 * Check Camp Lejeune contamination
 */
export async function checkCampLejeuneContamination(
  location: { baseName?: string },
  dates: DateRange
): Promise<HazardExposure | null> {
  const campLejeune = CONTAMINATED_WATER_LOCATIONS[0];
  
  if (!location.baseName) return null;
  
  const isLejeune = location.baseName.toLowerCase().includes('lejeune') ||
                   location.baseName.toLowerCase().includes('camp lejeune');
  
  if (!isLejeune) return null;

  const exposureDays = calculateOverlapDays(dates, campLejeune.active);
  
  if (exposureDays > 0) {
    return {
      type: 'contaminated_water',
      source: campLejeune.name,
      distance: 0,
      exposureDays,
      severity: campLejeune.severity,
      presumptive: true,
      pactActCovered: false
    };
  }

  return null;
}

/**
 * MAIN FUNCTION: Query all hazard databases for a duty station
 */
export async function queryHazardDatabases(params: {
  location: Location;
  dates: DateRange;
}): Promise<HazardExposure[]> {
  const hazards: HazardExposure[] = [];

  // Check burn pits (Iraq/Afghanistan)
  if (params.location.baseName) {
    const iraq = params.location.baseName.toLowerCase().includes('iraq');
    const afghanistan = params.location.baseName.toLowerCase().includes('afghan');
    
    if (iraq || afghanistan) {
      const burnPits = await checkBurnPitProximity(params.location, params.dates);
      hazards.push(...burnPits);
    }
  }

  // Check Agent Orange (Vietnam era)
  if (isVietnamEra(params.dates)) {
    const agentOrange = await checkAgentOrangeExposure(
      { country: 'Vietnam' },
      params.dates
    );
    hazards.push(...agentOrange);
  }

  // Check Camp Lejeune
  const lejeune = await checkCampLejeuneContamination(params.location, params.dates);
  if (lejeune) {
    hazards.push(lejeune);
  }

  return hazards;
}

/**
 * Get MOS-specific hazards
 */
export async function getMOSHazards(mosCode: string): Promise<{
  physical: string[];
  noise: string[];
  chemical: string[];
  conditions: string[];
}> {
  // Common MOS hazards (this would be expanded to 800+ codes)
  const mosDatabase: Record<string, any> = {
    '11B': { // Infantry
      physical: ['Heavy lifting (60+ lbs)', 'Ruck marches', 'Combat operations'],
      noise: ['Small arms fire', 'Artillery', 'Explosives'],
      chemical: ['CS gas training', 'Weapons cleaning solvents'],
      conditions: ['Back strain', 'Knee injuries', 'Hearing loss', 'Tinnitus', 'PTSD']
    },
    '63B': { // Wheeled Vehicle Mechanic
      physical: ['Heavy tool use', 'Awkward positions', 'Repetitive motion'],
      noise: ['Pneumatic tools', 'Engine testing'],
      chemical: ['Diesel fumes', 'Hydraulic fluid', 'Solvents', 'Asbestos'],
      conditions: ['Back strain', 'Carpal tunnel', 'Respiratory issues', 'Hearing loss']
    },
    '88M': { // Motor Transport Operator
      physical: ['Long-haul driving', 'Loading/unloading'],
      noise: ['Engine noise (8+ hrs/day)', 'Air brakes'],
      chemical: ['Diesel exhaust'],
      conditions: ['Back strain', 'Sleep disorders', 'Respiratory issues']
    },
  };

  return mosDatabase[mosCode] || {
    physical: [],
    noise: [],
    chemical: [],
    conditions: []
  };
}
