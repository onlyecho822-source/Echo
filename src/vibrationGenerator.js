/**
 * Vibration Generator Module
 * Converts audio frequency and intensity data into vibration patterns
 * that can be sent to haptic devices or actuators
 */

class VibrationGenerator {
  constructor() {
    // Vibration intensity zones for different frequency ranges
    this.vibrationMap = {
      veryLow: {
        baseFrequency: 60,      // Vibration frequency for very low audio
        pattern: 'pulse',       // Pulsing pattern
        amplitude: 0.8,         // Strong amplitude
        location: 'chest',      // Body location
      },
      low: {
        baseFrequency: 80,
        pattern: 'continuous',
        amplitude: 0.75,
        location: 'wrist',
      },
      midLow: {
        baseFrequency: 100,
        pattern: 'rhythm',
        amplitude: 0.7,
        location: 'wrist',
      },
      mid: {
        baseFrequency: 120,
        pattern: 'rhythm',
        amplitude: 0.65,
        location: 'fingertip',
      },
      midHigh: {
        baseFrequency: 140,
        pattern: 'flutter',
        amplitude: 0.6,
        location: 'fingertip',
      },
      high: {
        baseFrequency: 160,
        pattern: 'flutter',
        amplitude: 0.5,
        location: 'temple',
      },
    };

    this.patterns = {
      pulse: this.generatePulsePattern,
      continuous: this.generateContinuousPattern,
      rhythm: this.generateRhythmPattern,
      flutter: this.generateFlutterPattern,
    };
  }

  /**
   * Convert audio frequency data to vibration command
   * @param {Object} frequencyData - Audio frequency analysis data
   * @param {number} amplitude - Overall audio amplitude
   */
  generateVibrationCommand(frequencyData, amplitude) {
    const dominantBand = this.findDominantBand(frequencyData);
    const vibrationConfig = this.vibrationMap[dominantBand];

    if (!vibrationConfig) {
      return this.getDefaultVibration();
    }

    const patternGenerator = this.patterns[vibrationConfig.pattern];
    const scaledAmplitude = vibrationConfig.amplitude * amplitude * frequencyData[dominantBand].intensity;

    return {
      band: dominantBand,
      frequency: vibrationConfig.baseFrequency,
      amplitude: Math.min(1, scaledAmplitude),
      pattern: vibrationConfig.pattern,
      location: vibrationConfig.location,
      duration: 100, // milliseconds
      sequence: patternGenerator.call(this, scaledAmplitude),
      timestamp: Date.now(),
    };
  }

  /**
   * Generate pulse vibration pattern
   */
  generatePulsePattern(amplitude) {
    return [
      { intensity: amplitude, duration: 50 },
      { intensity: 0, duration: 50 },
      { intensity: amplitude * 0.7, duration: 30 },
      { intensity: 0, duration: 50 },
    ];
  }

  /**
   * Generate continuous vibration pattern
   */
  generateContinuousPattern(amplitude) {
    return [{ intensity: amplitude, duration: 200 }];
  }

  /**
   * Generate rhythm vibration pattern
   */
  generateRhythmPattern(amplitude) {
    return [
      { intensity: amplitude, duration: 100 },
      { intensity: 0, duration: 50 },
      { intensity: amplitude * 0.8, duration: 100 },
      { intensity: 0, duration: 50 },
    ];
  }

  /**
   * Generate flutter vibration pattern
   */
  generateFlutterPattern(amplitude) {
    const flutters = [];
    for (let i = 0; i < 4; i++) {
      flutters.push(
        { intensity: amplitude, duration: 20 },
        { intensity: 0, duration: 20 }
      );
    }
    return flutters;
  }

  /**
   * Find the dominant frequency band
   */
  findDominantBand(frequencyData) {
    let maxEnergy = 0;
    let dominantBand = 'mid';

    for (const [band, data] of Object.entries(frequencyData)) {
      if (data.energy > maxEnergy) {
        maxEnergy = data.energy;
        dominantBand = band;
      }
    }

    return dominantBand;
  }

  /**
   * Get default vibration when no audio is detected
   */
  getDefaultVibration() {
    return {
      band: 'mid',
      frequency: 0,
      amplitude: 0,
      pattern: 'none',
      location: 'wrist',
      duration: 0,
      sequence: [],
      timestamp: Date.now(),
    };
  }

  /**
   * Adaptive vibration based on language learning mode
   * Emphasizes speech frequencies
   */
  generateLanguageLearningVibration(frequencyData, amplitude) {
    // Boost mid and midHigh frequencies for speech
    const enhancedData = { ...frequencyData };
    enhancedData.mid.intensity *= 1.5;
    enhancedData.midHigh.intensity *= 1.3;

    return this.generateVibrationCommand(enhancedData, amplitude);
  }

  /**
   * Get all vibration locations that can be activated
   */
  getActivationPoints() {
    const locations = new Set();
    Object.values(this.vibrationMap).forEach(config => {
      locations.add(config.location);
    });
    return Array.from(locations);
  }

  /**
   * Calculate total vibration intensity across all bands
   */
  calculateTotalIntensity(frequencyData) {
    let total = 0;
    for (const data of Object.values(frequencyData)) {
      total += data.intensity;
    }
    return total / Object.keys(frequencyData).length;
  }
}

module.exports = VibrationGenerator;
