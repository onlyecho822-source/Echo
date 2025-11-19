/**
 * Audio Processor Module
 * Processes incoming audio signals and prepares them for vibration conversion
 */

class AudioProcessor {
  constructor(sampleRate = 44100) {
    this.sampleRate = sampleRate;
    this.bufferSize = 4096;
    this.frequencyBands = {
      veryLow: [20, 100],      // Very low frequency (sub-bass)
      low: [100, 500],         // Low frequency (bass)
      midLow: [500, 2000],     // Mid-low frequency
      mid: [2000, 5000],       // Mid frequency (speech)
      midHigh: [5000, 10000],  // Mid-high frequency
      high: [10000, 20000],    // High frequency
    };
    this.audioBuffer = [];
  }

  /**
   * Add audio samples to the processing buffer
   * @param {Float32Array} samples - Audio samples
   */
  addSamples(samples) {
    this.audioBuffer.push(...Array.from(samples));

    // Keep buffer size manageable
    if (this.audioBuffer.length > this.bufferSize * 2) {
      this.audioBuffer = this.audioBuffer.slice(-this.bufferSize);
    }
  }

  /**
   * Perform FFT (Fast Fourier Transform) on audio buffer
   * Simplified FFT using basic frequency analysis
   */
  performFFT() {
    const buffer = this.audioBuffer.slice(0, this.bufferSize);

    if (buffer.length === 0) return {};

    const frequencyData = {};

    // Analyze each frequency band
    for (const [band, [minFreq, maxFreq]] of Object.entries(this.frequencyBands)) {
      const minBin = Math.floor((minFreq / this.sampleRate) * this.bufferSize);
      const maxBin = Math.floor((maxFreq / this.sampleRate) * this.bufferSize);

      let energy = 0;
      for (let i = minBin; i < maxBin && i < buffer.length; i++) {
        energy += Math.abs(buffer[i]) ** 2;
      }

      frequencyData[band] = {
        frequency: (minFreq + maxFreq) / 2,
        minFreq,
        maxFreq,
        energy: Math.sqrt(energy / (maxBin - minBin || 1)),
        intensity: this.normalizeIntensity(energy / (maxBin - minBin || 1)),
      };
    }

    return frequencyData;
  }

  /**
   * Normalize intensity to 0-1 range
   */
  normalizeIntensity(value) {
    return Math.min(1, value / 0.1);
  }

  /**
   * Get amplitude envelope of audio
   */
  getAmplitudeEnvelope() {
    const buffer = this.audioBuffer.slice(0, this.bufferSize);
    let rms = 0;
    for (let sample of buffer) {
      rms += sample * sample;
    }
    rms = Math.sqrt(rms / buffer.length);
    return Math.min(1, rms * 3); // Scale for better perception
  }

  /**
   * Detect dominant frequency
   */
  getDominantFrequency() {
    const freqData = this.performFFT();
    let maxEnergy = 0;
    let dominantBand = 'mid';

    for (const [band, data] of Object.entries(freqData)) {
      if (data.energy > maxEnergy) {
        maxEnergy = data.energy;
        dominantBand = band;
      }
    }

    return {
      band: dominantBand,
      frequency: freqData[dominantBand].frequency,
      intensity: freqData[dominantBand].intensity,
    };
  }

  /**
   * Clear the audio buffer
   */
  clearBuffer() {
    this.audioBuffer = [];
  }

  /**
   * Get current buffer state
   */
  getBufferState() {
    return {
      bufferLength: this.audioBuffer.length,
      maxBufferSize: this.bufferSize,
      sampleRate: this.sampleRate,
    };
  }
}

module.exports = AudioProcessor;
