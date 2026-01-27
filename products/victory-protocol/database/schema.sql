-- ============================================================================
-- ART OF PROOF: SERVICE RECONSTRUCTION DATABASE SCHEMA
-- Complete military service record reconstruction system
-- ============================================================================

-- Main reconstruction tracking table
CREATE TABLE service_reconstruction (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    
    -- Extracted from DD214
    branch ENUM('Army', 'Navy', 'Air Force', 'Marines', 'Coast Guard', 'Space Force'),
    service_start_date DATE,
    service_end_date DATE,
    primary_mos VARCHAR(10),
    rank_at_separation VARCHAR(10),
    
    -- Progress tracking
    total_documents INT DEFAULT 0,
    uploaded_documents INT DEFAULT 0,
    missing_documents INT DEFAULT 0,
    requested_documents INT DEFAULT 0,
    completion_percentage INT DEFAULT 0,
    
    -- Status
    status ENUM('initialized', 'in_progress', 'complete', 'ready_for_submission') DEFAULT 'initialized',
    
    -- Timeline
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_completion (completion_percentage)
);

-- Category tracking (14 categories)
CREATE TABLE checklist_categories (
    id VARCHAR(64) PRIMARY KEY,
    reconstruction_id VARCHAR(64) NOT NULL,
    
    category_name VARCHAR(100),
    category_type ENUM(
        'enlistment',
        'basic_training',
        'ait_training',
        'specialized_schools',
        'duty_stations',
        'deployments',
        'special_assignments',
        'awards_decorations',
        'disciplinary_records',
        'medical_records',
        'separation',
        'maps_geographic',
        'unit_history',
        'administrative'
    ),
    
    -- Category stats
    total_items INT DEFAULT 0,
    completed_items INT DEFAULT 0,
    completion_percentage INT DEFAULT 0,
    
    -- Priority
    priority ENUM('critical', 'high', 'medium', 'low') DEFAULT 'medium',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (reconstruction_id) REFERENCES service_reconstruction(id) ON DELETE CASCADE,
    INDEX idx_reconstruction (reconstruction_id),
    INDEX idx_category_type (category_type)
);

-- Individual checklist items (200+ potential documents)
CREATE TABLE checklist_items (
    id VARCHAR(64) PRIMARY KEY,
    category_id VARCHAR(64) NOT NULL,
    
    document_name VARCHAR(200),
    document_type VARCHAR(100),
    description TEXT,
    
    -- Status tracking
    status ENUM('missing', 'uploaded', 'requested', 'processing', 'verified', 'rejected') DEFAULT 'missing',
    
    -- Acquisition info
    source VARCHAR(200), -- "NARA", "Personal Files", "Unit S-1", "VA Blue Button"
    acquisition_method ENUM('veteran_upload', 'nara_request', 'unit_request', 'auto_generated', 'foia_request'),
    
    -- File reference
    file_id VARCHAR(64), -- Links to uploaded file
    file_path VARCHAR(500),
    
    -- Priority
    priority ENUM('critical', 'high', 'medium', 'low') DEFAULT 'medium',
    
    -- Request tracking
    requested_date TIMESTAMP NULL,
    expected_date TIMESTAMP NULL,
    received_date TIMESTAMP NULL,
    
    -- Notes
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (category_id) REFERENCES checklist_categories(id) ON DELETE CASCADE,
    INDEX idx_category (category_id),
    INDEX idx_status (status),
    INDEX idx_priority (priority)
);

-- Duty station records with geographic data
CREATE TABLE duty_station_records (
    id VARCHAR(64) PRIMARY KEY,
    reconstruction_id VARCHAR(64) NOT NULL,
    
    -- Station info
    station_name VARCHAR(200),
    base_name VARCHAR(200),
    
    -- Location
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Dates
    start_date DATE,
    end_date DATE,
    
    -- Unit info
    unit_name VARCHAR(200),
    unit_type VARCHAR(100), -- Battalion, Company, etc.
    mos VARCHAR(10),
    rank VARCHAR(10),
    
    -- Documents needed for this station
    pcs_orders_uploaded BOOLEAN DEFAULT FALSE,
    unit_roster_uploaded BOOLEAN DEFAULT FALSE,
    morning_reports_uploaded BOOLEAN DEFAULT FALSE,
    ncoers_uploaded BOOLEAN DEFAULT FALSE,
    medical_records_uploaded BOOLEAN DEFAULT FALSE,
    
    -- Completion
    documents_needed INT DEFAULT 18,
    documents_obtained INT DEFAULT 0,
    completion_percentage INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (reconstruction_id) REFERENCES service_reconstruction(id) ON DELETE CASCADE,
    INDEX idx_reconstruction (reconstruction_id),
    INDEX idx_dates (start_date, end_date),
    INDEX idx_location (latitude, longitude)
);

-- Hazard exposure tracking
CREATE TABLE hazard_exposures (
    id VARCHAR(64) PRIMARY KEY,
    duty_station_id VARCHAR(64) NOT NULL,
    
    -- Hazard type
    hazard_type ENUM(
        'burn_pit',
        'agent_orange',
        'contaminated_water',
        'radiation',
        'asbestos',
        'chemical_exposure',
        'noise_exposure',
        'particulate_matter',
        'depleted_uranium',
        'toxic_embedded_fragments',
        'other'
    ),
    
    -- Details
    hazard_name VARCHAR(200),
    hazard_source VARCHAR(500),
    
    -- Proximity/exposure
    distance_meters INT,
    exposure_days INT,
    severity ENUM('low', 'medium', 'high', 'extreme') DEFAULT 'medium',
    
    -- Presumptive status
    presumptive_condition BOOLEAN DEFAULT FALSE,
    pact_act_covered BOOLEAN DEFAULT FALSE,
    
    -- Evidence
    documentation_level ENUM('confirmed', 'probable', 'possible') DEFAULT 'possible',
    evidence_source VARCHAR(500),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (duty_station_id) REFERENCES duty_station_records(id) ON DELETE CASCADE,
    INDEX idx_duty_station (duty_station_id),
    INDEX idx_hazard_type (hazard_type),
    INDEX idx_presumptive (presumptive_condition)
);

-- Deployment records
CREATE TABLE deployment_records (
    id VARCHAR(64) PRIMARY KEY,
    reconstruction_id VARCHAR(64) NOT NULL,
    
    -- Operation info
    operation_name VARCHAR(200),
    theater VARCHAR(100), -- Iraq, Afghanistan, Kuwait, etc.
    
    -- Location
    location_name VARCHAR(200),
    country VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Dates
    deployment_start DATE,
    deployment_end DATE,
    
    -- Unit
    unit_name VARCHAR(200),
    
    -- Combat status
    combat_zone BOOLEAN DEFAULT FALSE,
    hostile_fire_pay BOOLEAN DEFAULT FALSE,
    combat_operations BOOLEAN DEFAULT FALSE,
    
    -- Documents
    deployment_orders_uploaded BOOLEAN DEFAULT FALSE,
    pdha_uploaded BOOLEAN DEFAULT FALSE,
    pdhra_uploaded BOOLEAN DEFAULT FALSE,
    after_action_reports_uploaded BOOLEAN DEFAULT FALSE,
    
    -- Awards from deployment
    awards_received JSON,
    
    -- Completion
    documents_needed INT DEFAULT 15,
    documents_obtained INT DEFAULT 0,
    completion_percentage INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (reconstruction_id) REFERENCES service_reconstruction(id) ON DELETE CASCADE,
    INDEX idx_reconstruction (reconstruction_id),
    INDEX idx_theater (theater),
    INDEX idx_combat (combat_zone)
);

-- Training schools record
CREATE TABLE training_schools (
    id VARCHAR(64) PRIMARY KEY,
    reconstruction_id VARCHAR(64) NOT NULL,
    
    -- School info
    school_name VARCHAR(200),
    school_type ENUM('basic_training', 'ait', 'specialized', 'leadership', 'language', 'medical', 'aviation', 'other'),
    course_name VARCHAR(200),
    
    -- Location
    location VARCHAR(200),
    
    -- Dates
    start_date DATE,
    end_date DATE,
    
    -- Completion
    graduated BOOLEAN DEFAULT TRUE,
    certificate_uploaded BOOLEAN DEFAULT FALSE,
    test_scores_uploaded BOOLEAN DEFAULT FALSE,
    
    -- MOS/certification earned
    mos_awarded VARCHAR(10),
    certification_earned VARCHAR(200),
    
    -- Hazards during training
    physical_demands ENUM('minimal', 'moderate', 'high', 'extreme'),
    injury_risk TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (reconstruction_id) REFERENCES service_reconstruction(id) ON DELETE CASCADE,
    INDEX idx_reconstruction (reconstruction_id),
    INDEX idx_school_type (school_type)
);

-- MOS hazard mapping (occupational exposure)
CREATE TABLE mos_hazard_mapping (
    id VARCHAR(64) PRIMARY KEY,
    
    mos_code VARCHAR(10),
    branch ENUM('Army', 'Navy', 'Air Force', 'Marines', 'Coast Guard'),
    mos_title VARCHAR(200),
    
    -- Hazard categories
    physical_demands JSON, -- ["Heavy lifting", "Ruck marches", etc.]
    noise_hazards JSON, -- ["Small arms", "Artillery", etc.]
    chemical_hazards JSON, -- ["Solvents", "Fumes", etc.]
    injury_risks JSON, -- ["Back strain", "Hearing loss", etc.]
    
    -- Associated conditions
    common_conditions JSON, -- ["Lower back pain", "Tinnitus", etc.]
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_mos (mos_code),
    INDEX idx_branch (branch)
);

-- NARA/FOIA request tracking
CREATE TABLE nara_requests (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    reconstruction_id VARCHAR(64),
    
    -- Request info
    request_type ENUM('ompf', 'unit_records', 'medical_records', 'personnel_records'),
    requested_documents JSON, -- Array of document names
    
    -- SF-180 form
    sf180_form_path VARCHAR(500), -- S3 path to generated PDF
    
    -- Status
    status ENUM('draft', 'submitted', 'pending', 'received', 'denied', 'partially_received') DEFAULT 'draft',
    
    -- Timeline
    submitted_date TIMESTAMP NULL,
    expected_response_date TIMESTAMP NULL,
    received_date TIMESTAMP NULL,
    
    -- Tracking
    tracking_number VARCHAR(100),
    confirmation_email VARCHAR(500),
    
    -- Notes
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_expected_date (expected_response_date)
);

-- Unit history database (pre-populated reference data)
CREATE TABLE unit_history_database (
    id VARCHAR(64) PRIMARY KEY,
    
    unit_name VARCHAR(200),
    unit_designation VARCHAR(100),
    branch ENUM('Army', 'Navy', 'Air Force', 'Marines', 'Coast Guard'),
    
    -- Time period
    period_start DATE,
    period_end DATE,
    
    -- Operations
    operations JSON, -- Array of operation names
    
    -- Combat info
    combat_operations BOOLEAN DEFAULT FALSE,
    casualties JSON, -- {kia: number, wia: number}
    battles JSON, -- Array of battle names
    
    -- Living conditions
    living_conditions TEXT,
    sanitation_info TEXT,
    medical_support_level VARCHAR(100),
    
    -- Hazards
    known_hazards JSON,
    
    -- Source
    source VARCHAR(500), -- "Unit historical files", "After-action report", etc.
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_unit_name (unit_name),
    INDEX idx_period (period_start, period_end)
);

-- Burn pit registry (reference database)
CREATE TABLE burn_pit_locations (
    id VARCHAR(64) PRIMARY KEY,
    
    location_name VARCHAR(200),
    base_name VARCHAR(200),
    country VARCHAR(100),
    
    -- Coordinates
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Operating dates
    start_date DATE,
    end_date DATE,
    
    -- Details
    pit_size_meters INT,
    materials_burned JSON,
    operating_hours VARCHAR(100), -- "24/7", "Daylight only", etc.
    
    -- Proximity zones
    extreme_zone_meters INT DEFAULT 500,
    high_zone_meters INT DEFAULT 1000,
    medium_zone_meters INT DEFAULT 2000,
    
    -- VA recognition
    va_recognized BOOLEAN DEFAULT TRUE,
    pact_act_covered BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_location (latitude, longitude),
    INDEX idx_base (base_name),
    INDEX idx_dates (start_date, end_date)
);

-- Base hazard database (reference data for all military installations)
CREATE TABLE base_hazard_database (
    id VARCHAR(64) PRIMARY KEY,
    
    base_name VARCHAR(200),
    location VARCHAR(200),
    country VARCHAR(100),
    
    -- Coordinates
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Hazards present
    hazards JSON, -- Array of hazard objects
    
    -- Time period
    hazard_start_date DATE,
    hazard_end_date DATE,
    
    -- Presumptive status
    va_presumptive BOOLEAN DEFAULT FALSE,
    
    -- Documentation
    source VARCHAR(500),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_base (base_name),
    INDEX idx_location (latitude, longitude)
);

-- Audit log for PHI access
CREATE TABLE reconstruction_audit_log (
    id VARCHAR(64) PRIMARY KEY,
    
    user_id VARCHAR(64) NOT NULL,
    reconstruction_id VARCHAR(64),
    
    action VARCHAR(100), -- "view_documents", "upload_file", "request_records", etc.
    resource_type VARCHAR(100),
    resource_id VARCHAR(64),
    
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    phi_accessed BOOLEAN DEFAULT FALSE,
    access_reason VARCHAR(500),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user (user_id),
    INDEX idx_reconstruction (reconstruction_id),
    INDEX idx_action (action),
    INDEX idx_created (created_at)
);

-- ============================================================================
-- VIEWS FOR REPORTING
-- ============================================================================

-- Overall completion status view
CREATE VIEW v_reconstruction_progress AS
SELECT 
    sr.id,
    sr.user_id,
    sr.branch,
    sr.completion_percentage as overall_completion,
    COUNT(DISTINCT cc.id) as total_categories,
    COUNT(DISTINCT ds.id) as total_duty_stations,
    COUNT(DISTINCT dr.id) as total_deployments,
    COUNT(DISTINCT he.id) as total_hazard_exposures,
    sr.status,
    sr.created_at
FROM service_reconstruction sr
LEFT JOIN checklist_categories cc ON sr.id = cc.reconstruction_id
LEFT JOIN duty_station_records ds ON sr.id = ds.reconstruction_id
LEFT JOIN deployment_records dr ON sr.id = dr.reconstruction_id
LEFT JOIN hazard_exposures he ON ds.id = he.duty_station_id
GROUP BY sr.id;

-- Missing critical documents view
CREATE VIEW v_critical_missing_documents AS
SELECT 
    ci.reconstruction_id,
    cc.category_name,
    ci.document_name,
    ci.source,
    ci.priority,
    ci.acquisition_method
FROM checklist_items ci
JOIN checklist_categories cc ON ci.category_id = cc.id
WHERE ci.status = 'missing'
  AND ci.priority IN ('critical', 'high')
ORDER BY 
    CASE ci.priority
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
    END;

-- Hazard exposure summary view
CREATE VIEW v_hazard_exposure_summary AS
SELECT 
    sr.id as reconstruction_id,
    sr.user_id,
    ds.station_name,
    he.hazard_type,
    he.hazard_name,
    he.severity,
    he.presumptive_condition,
    he.pact_act_covered,
    he.exposure_days
FROM service_reconstruction sr
JOIN duty_station_records ds ON sr.id = ds.reconstruction_id
JOIN hazard_exposures he ON ds.id = he.duty_station_id
WHERE he.severity IN ('high', 'extreme')
   OR he.presumptive_condition = TRUE
ORDER BY he.severity DESC, he.exposure_days DESC;
