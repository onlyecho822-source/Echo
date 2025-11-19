# 🎧 Echo - Hearing Aid Vibration Prototype

A medical device prototype that converts audio frequencies into vibration patterns, enabling users to perceive sound through tactile feedback. This device is designed to help users hear and learn language as if they were younger by providing real-time vibration-based audio representation.

## 🎯 Project Overview

Echo is an innovative hearing aid system that:
- **Processes audio in real-time** using frequency analysis (FFT)
- **Generates adaptive vibration patterns** that correspond to different frequency ranges
- **Supports multiple modes** including language learning mode optimized for speech perception
- **Provides configurable sensitivity levels** for personalized experience
- **Tracks session statistics** for medical monitoring and learning progress

## 🏥 Medical Applications

- **Hearing restoration**: Converts audio to tactile feedback for hearing-impaired individuals
- **Language learning**: Enhanced speech frequency perception for language acquisition
- **Auditory training**: Progressive hearing aid with adaptive difficulty
- **Accessibility**: Provides alternative sensory pathway for audio information

## 📋 Architecture

```
Echo Hearing Aid System
├── Audio Input
│   └── audioProcessor.js (Frequency Analysis)
├── Signal Processing
│   └── vibrationGenerator.js (Pattern Generation)
├── Device Control
│   └── deviceController.js (Orchestration)
└── Interface
    └── server.js (REST API & Web)
```

## 🚀 Quick Start

### Installation

```bash
cd /home/user/Echo
npm install
```

### Run Tests

```bash
npm test
```

This will run 12 comprehensive tests covering:
- Device initialization
- Audio frequency analysis
- Vibration pattern generation
- Mode switching (standard, language-learning, music)
- Sensitivity adjustment
- Multi-frequency processing
- Continuous operation
- Status and statistics reporting

### Start Web Server

```bash
npm start
```

The server will start on `http://localhost:3000`

## 📚 API Endpoints

### Audio Processing
- **POST** `/api/audio/process` - Process audio samples and get vibration command
- **POST** `/api/vibration/execute` - Execute vibration on device

### Device Control
- **GET** `/api/device/status` - Get current device status
- **GET** `/api/device/stats` - Get session statistics
- **POST** `/api/device/mode` - Set device mode
- **POST** `/api/device/sensitivity` - Set sensitivity level (0.1-3.0)
- **POST** `/api/device/vibration-toggle` - Enable/disable vibrations

### Information
- **GET** `/api/device/locations` - Get supported vibration locations
- **POST** `/api/device/test` - Run device self-test
- **GET** `/health` - Health check
- **GET** `/` - API documentation

## 🎛️ Device Modes

### Standard Mode
Normal audio processing with balanced frequency emphasis across all ranges.

### Language Learning Mode
Enhanced perception of speech frequencies (2000-5000 Hz) with boosted mid and mid-high frequency intensity. Ideal for:
- Learning new languages
- Speech clarity enhancement
- Auditory comprehension training

### Music Mode
Full frequency spectrum with emphasis on both low and high frequencies for comprehensive sound experience.

## 📊 Frequency Processing

The system analyzes audio across six frequency bands:

| Band | Frequency Range | Vibration Pattern | Location |
|------|-----------------|-------------------|----------|
| Very Low | 20-100 Hz | Pulse | Chest |
| Low | 100-500 Hz | Continuous | Wrist |
| Mid-Low | 500-2000 Hz | Rhythm | Wrist |
| Mid | 2000-5000 Hz | Rhythm | Fingertip |
| Mid-High | 5000-10000 Hz | Flutter | Fingertip |
| High | 10000-20000 Hz | Flutter | Temple |

## 🔧 Core Modules

### AudioProcessor (`src/audioProcessor.js`)
- Processes incoming audio samples
- Performs FFT-based frequency analysis
- Calculates amplitude envelope
- Detects dominant frequencies
- Supports configurable sample rates

### VibrationGenerator (`src/vibrationGenerator.js`)
- Maps audio frequencies to vibration patterns
- Generates pattern sequences (pulse, continuous, rhythm, flutter)
- Supports multiple vibration locations
- Implements adaptive language learning mode
- Calculates total intensity metrics

### DeviceController (`src/deviceController.js`)
- Orchestrates audio processing and vibration generation
- Manages device configuration and modes
- Tracks session statistics
- Provides device self-testing
- Handles graceful shutdown

### Server (`src/server.js`)
- Express.js REST API server
- CORS support for web clients
- Real-time device control
- Session management and statistics
- Health monitoring

## 💻 Usage Example

```javascript
const HearingAidDevice = require('./src/deviceController');

// Initialize device
const device = new HearingAidDevice({
  mode: 'language-learning',
  sensitivity: 1.2,
  vibrationEnabled: true,
});

device.initialize();

// Process audio
const audioSamples = new Float32Array([...]);
const result = device.processAudio(audioSamples);

console.log('Vibration command:', result.vibrationCommand);

// Execute vibration
device.executeVibration(result.vibrationCommand);

// Get statistics
const stats = device.getSessionStats();
console.log('Session duration:', stats.sessionDuration);
```

## 🧪 Testing

The prototype includes comprehensive testing (`src/test.js`):

```bash
npm test
```

Tests cover:
1. Device initialization
2. Self-test diagnostics
3. Audio processing with simulated speech
4. Mode switching
5. Sensitivity adjustment
6. Multi-frequency processing
7. Vibration execution
8. Language learning mode
9. Status and statistics
10. Vibration locations
11. Continuous processing
12. Device shutdown

## 📈 Performance Metrics

- **Sample Rate**: 44100 Hz (standard audio)
- **Buffer Size**: 4096 samples
- **Frequency Bands**: 6 analyzed bands
- **Vibration Patterns**: 4 pattern types
- **Supported Locations**: 4 vibration points (chest, wrist, fingertip, temple)
- **Sensitivity Range**: 0.1 - 3.0

## 🔐 Medical Device Considerations

This prototype demonstrates core functionality for a medical hearing aid device:
- ✅ Real-time audio processing
- ✅ Configurable sensitivity and feedback
- ✅ Session tracking and statistics
- ✅ Multiple operational modes
- ✅ Comprehensive self-testing
- ✅ Graceful error handling

For production use, additional considerations would include:
- Medical certification and compliance (FDA, CE mark)
- Hardware integration with haptic actuators
- User safety limits and thresholds
- Clinical validation with users
- Battery optimization
- Data privacy and security

## 📝 Configuration

### Device Config Options

```javascript
{
  sampleRate: 44100,              // Audio sample rate (Hz)
  mode: 'language-learning',      // Device mode
  vibrationEnabled: true,         // Enable vibration feedback
  audioEnabled: true,             // Enable audio processing
  sensitivity: 1.2,               // Sensitivity multiplier (0.1-3.0)
}
```

## 🎓 Learning Path

The device supports progressive learning:
1. Start with **standard mode** at lower sensitivity
2. Progress to **language-learning mode** with enhanced speech
3. Gradually increase sensitivity as user adapts
4. Monitor progress through session statistics
5. Adjust based on dominant frequency feedback

## 📦 Project Structure

```
Echo/
├── src/
│   ├── audioProcessor.js      # Audio frequency analysis
│   ├── vibrationGenerator.js  # Vibration pattern creation
│   ├── deviceController.js    # Main device orchestrator
│   ├── server.js              # Web API server
│   └── test.js                # Comprehensive test suite
├── package.json               # Project dependencies
├── .gitignore                 # Git configuration
└── README.md                  # This file
```

## 🤝 Contributing

This is a prototype for medical device research. Any modifications should:
- Maintain safety thresholds
- Include comprehensive testing
- Document changes clearly
- Consider medical implications

## ⚠️ Disclaimer

This is a research prototype for demonstrating hearing aid vibration technology. It is not a certified medical device and should not be used for diagnosis or treatment of medical conditions without proper validation and approval.

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

Echo Medical Device Team
Prototype Version: 0.1.0
Date: 2025

---

**Status**: Active Development ✓
**Last Updated**: November 19, 2025
