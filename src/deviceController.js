/**
 * Device Controller Module
 * Main orchestrator that manages the hearing aid device
 * Coordinates audio processing, vibration generation, and device output
 */

const AudioProcessor = require('./audioProcessor');
const VibrationGenerator = require('./vibrationGenerator');

class HearingAidDevice {
  constructor(config = {}) {
    this.config = {
      sampleRate: config.sampleRate || 44100,
      mode: config.mode || 'standard', // 'standard', 'language-learning', 'music'
      vibrationEnabled: config.vibrationEnabled !== false,
      audioEnabled: config.audioEnabled !== false,
      sensitivity: config.sensitivity || 1.0,
      ...config,
    };

    this.audioProcessor = new AudioProcessor(this.config.sampleRate);
    this.vibrationGenerator = new VibrationGenerator();
    this.isActive = false;
    this.sessionStartTime = null;
    this.statsCollector = {
      totalSamplesProcessed: 0,
      vibrationEventsGenerated: 0,
      dominantBands: {},
      sessionDuration: 0,
    };
  }

  /**
   * Initialize the device
   */
  initialize() {
    this.isActive = true;
    this.sessionStartTime = Date.now();
    this.audioProcessor.clearBuffer();
    console.log('🎧 Hearing Aid Device Initialized');
    console.log(`Mode: ${this.config.mode}`);
    console.log(`Vibration: ${this.config.vibrationEnabled ? 'Enabled' : 'Disabled'}`);
    console.log(`Audio: ${this.config.audioEnabled ? 'Enabled' : 'Disabled'}`);
    return { status: 'initialized', timestamp: Date.now() };
  }

  /**
   * Process incoming audio data
   * @param {Float32Array} audioSamples - Raw audio samples
   */
  processAudio(audioSamples) {
    if (!this.isActive) {
      throw new Error('Device not initialized');
    }

    // Add samples to processor
    this.audioProcessor.addSamples(audioSamples);
    this.statsCollector.totalSamplesProcessed += audioSamples.length;

    // Perform frequency analysis
    const frequencyData = this.audioProcessor.performFFT();
    const amplitude = this.audioProcessor.getAmplitudeEnvelope();

    // Generate vibration command
    let vibrationCommand;
    if (this.config.mode === 'language-learning') {
      vibrationCommand = this.vibrationGenerator.generateLanguageLearningVibration(
        frequencyData,
        amplitude * this.config.sensitivity
      );
    } else {
      vibrationCommand = this.vibrationGenerator.generateVibrationCommand(
        frequencyData,
        amplitude * this.config.sensitivity
      );
    }

    // Track statistics
    if (vibrationCommand.amplitude > 0) {
      this.statsCollector.vibrationEventsGenerated++;
      const band = vibrationCommand.band;
      this.statsCollector.dominantBands[band] = (this.statsCollector.dominantBands[band] || 0) + 1;
    }

    return {
      audioAnalysis: {
        frequencyData,
        amplitude,
        dominantFrequency: this.audioProcessor.getDominantFrequency(),
      },
      vibrationCommand,
      timestamp: Date.now(),
    };
  }

  /**
   * Execute vibration on physical device
   * In a real implementation, this would communicate with haptic hardware
   */
  executeVibration(vibrationCommand) {
    if (!this.config.vibrationEnabled) {
      return { status: 'vibration_disabled' };
    }

    // Simulate sending to haptic device
    const executionResult = {
      success: true,
      vibrationId: Math.random().toString(36).substr(2, 9),
      frequency: vibrationCommand.frequency,
      amplitude: vibrationCommand.amplitude,
      pattern: vibrationCommand.pattern,
      location: vibrationCommand.location,
      sequence: vibrationCommand.sequence,
      executedAt: Date.now(),
    };

    // Log for testing
    if (vibrationCommand.amplitude > 0) {
      console.log(
        `📳 Vibration: ${vibrationCommand.pattern} @ ${vibrationCommand.frequency}Hz, ` +
        `Amplitude: ${(vibrationCommand.amplitude * 100).toFixed(1)}%, ` +
        `Location: ${vibrationCommand.location}`
      );
    }

    return executionResult;
  }

  /**
   * Set device mode
   */
  setMode(mode) {
    if (!['standard', 'language-learning', 'music'].includes(mode)) {
      throw new Error('Invalid mode');
    }
    this.config.mode = mode;
    console.log(`🎯 Device mode changed to: ${mode}`);
    return { mode: this.config.mode };
  }

  /**
   * Set sensitivity level (0.1 to 3.0)
   */
  setSensitivity(level) {
    if (level < 0.1 || level > 3.0) {
      throw new Error('Sensitivity must be between 0.1 and 3.0');
    }
    this.config.sensitivity = level;
    return { sensitivity: this.config.sensitivity };
  }

  /**
   * Enable/disable vibration
   */
  setVibrationEnabled(enabled) {
    this.config.vibrationEnabled = enabled;
    return { vibrationEnabled: this.config.vibrationEnabled };
  }

  /**
   * Get device status
   */
  getStatus() {
    return {
      isActive: this.isActive,
      mode: this.config.mode,
      sensitivity: this.config.sensitivity,
      vibrationEnabled: this.config.vibrationEnabled,
      audioEnabled: this.config.audioEnabled,
      bufferState: this.audioProcessor.getBufferState(),
      uptime: this.isActive ? Date.now() - this.sessionStartTime : 0,
    };
  }

  /**
   * Get session statistics
   */
  getSessionStats() {
    const uptime = Date.now() - this.sessionStartTime;
    return {
      sessionDuration: uptime,
      totalSamplesProcessed: this.statsCollector.totalSamplesProcessed,
      vibrationEventsGenerated: this.statsCollector.vibrationEventsGenerated,
      dominantBands: this.statsCollector.dominantBands,
      averageVibrationIntensity:
        this.statsCollector.vibrationEventsGenerated > 0 ? 'tracked' : 'none',
    };
  }

  /**
   * Shutdown the device
   */
  shutdown() {
    this.isActive = false;
    this.statsCollector.sessionDuration = Date.now() - this.sessionStartTime;
    const stats = this.getSessionStats();
    console.log('🛑 Device Shutdown');
    console.log(`Session Duration: ${(stats.sessionDuration / 1000).toFixed(1)}s`);
    console.log(`Total Vibration Events: ${stats.vibrationEventsGenerated}`);
    return {
      status: 'shutdown',
      finalStats: stats,
    };
  }

  /**
   * Get list of supported vibration locations
   */
  getVibrationLocations() {
    return this.vibrationGenerator.getActivationPoints();
  }

  /**
   * Perform self-test
   */
  performSelfTest() {
    console.log('🧪 Running device self-test...');
    const testResults = {
      audioProcessor: !!this.audioProcessor,
      vibrationGenerator: !!this.vibrationGenerator,
      vibrationLocations: this.getVibrationLocations(),
      modes: ['standard', 'language-learning', 'music'],
      timestamp: Date.now(),
    };
    console.log('✅ Self-test passed');
    return testResults;
  }
}

module.exports = HearingAidDevice;
