# Echo Fact-Check

**Real-time truth verification for audio, video, and documents**

Echo Fact-Check is a live fact-checking application that can analyze any content - text, audio, video, or documents - and verify factual claims in real-time. Perfect for watching live broadcasts, analyzing speeches, or verifying any content you encounter.

## Features

- **Live Fact-Checking** - Stream audio from your microphone and get real-time fact verification
- **Multi-Format Support** - Analyze audio (MP3, WAV), video (MP4, MOV), documents (PDF, DOCX), and images (PNG, JPG)
- **AI-Powered Verification** - Uses OpenAI GPT-4 or Anthropic Claude for intelligent claim extraction and verification
- **Real-Time WebSocket Updates** - Get results as claims are verified, not after
- **Credibility Scoring** - Overall content credibility score based on verified claims
- **Source References** - Links to sources that support or contradict claims
- **Modern Web Interface** - Beautiful, responsive UI that works on desktop and mobile

## Quick Start

### Prerequisites

- Python 3.9+
- FFmpeg (for audio/video processing)
- Tesseract OCR (for image text extraction)
- OpenAI API key or Anthropic API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/onlyecho822-source/Echo.git
   cd Echo
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install system dependencies**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg tesseract-ocr

   # macOS
   brew install ffmpeg tesseract

   # Windows - Download from official websites
   ```

5. **Configure API keys**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

6. **Run the application**
   ```bash
   python -m app.main
   ```

7. **Open in browser**
   ```
   http://localhost:8000
   ```

## Configuration

Edit `.env` file to configure:

```env
# Required - At least one AI API key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Optional
MAX_UPLOAD_SIZE_MB=100
WHISPER_MODEL=base  # tiny, base, small, medium, large
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/factcheck/text` | POST | Fact-check text content |
| `/api/factcheck/file` | POST | Upload and fact-check a file |
| `/api/audio/transcribe` | POST | Transcribe audio to text |
| `/api/video/ocr` | POST | Extract text from images |
| `/api/documents/extract` | POST | Extract text from documents |
| `/api/ws/live` | WebSocket | Live streaming fact-check |

### Example: Fact-check text

```bash
curl -X POST http://localhost:8000/api/factcheck/text \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "text",
    "text_content": "The Earth is approximately 4.5 billion years old."
  }'
```

### Example: Upload file

```bash
curl -X POST http://localhost:8000/api/factcheck/file \
  -F "file=@speech.mp3"
```

## How It Works

1. **Content Ingestion** - Upload files or stream audio
2. **Text Extraction** - Transcribe audio (Whisper), OCR images (Tesseract), parse documents
3. **Claim Extraction** - AI identifies factual claims in the text
4. **Verification** - Each claim is checked against knowledge and sources
5. **Results** - Claims marked as True, False, Partially True, Misleading, or Unverifiable

## Architecture

```
app/
├── main.py              # FastAPI application
├── config.py            # Configuration
├── api/
│   └── routes/          # API endpoints
│       ├── factcheck.py
│       ├── audio.py
│       ├── video.py
│       ├── documents.py
│       └── websocket.py
├── services/
│   ├── audio_processor.py    # Whisper transcription
│   ├── video_processor.py    # Video/image analysis
│   ├── document_processor.py # PDF/DOCX extraction
│   ├── claim_extractor.py    # AI claim extraction
│   └── fact_checker.py       # AI verification engine
└── models/
    └── schemas.py       # Pydantic models

frontend/
├── index.html           # Main UI
├── css/styles.css       # Styling
└── js/app.js           # Frontend logic
```

## Supported Formats

| Type | Formats |
|------|---------|
| Audio | MP3, WAV, M4A, OGG, FLAC, WebM |
| Video | MP4, AVI, MOV, MKV, WebM |
| Documents | PDF, DOCX, DOC, TXT, MD |
| Images | PNG, JPG, JPEG, GIF, BMP, TIFF |

## Verification Statuses

| Status | Description |
|--------|-------------|
| ✅ TRUE | Claim is accurate and well-supported |
| ❌ FALSE | Claim is inaccurate or contradicted by evidence |
| ⚠️ PARTIALLY TRUE | Claim has some truth but lacks context |
| ⚠️ MISLEADING | Technically true but presented deceptively |
| ❓ UNVERIFIABLE | Cannot be verified with available sources |
| 💭 OPINION | Subjective statement, not a factual claim |

## Development

### Run in development mode

```bash
DEBUG=true python -m app.main
```

### Run tests

```bash
pytest tests/
```

### Code formatting

```bash
black app/
ruff check app/
```

## Limitations

- AI verification is not 100% accurate - always verify important claims manually
- Real-time streaming requires stable internet connection
- Large files may take longer to process
- Some languages may have reduced accuracy for transcription

## Roadmap

- [ ] Database for storing results
- [ ] User authentication
- [ ] URL/webpage fact-checking
- [ ] Browser extension
- [ ] Mobile app
- [ ] Multi-language support
- [ ] Custom fact-check databases
- [ ] Streaming from external sources (TV, radio)

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## License

MIT License - see LICENSE file for details.

---

**Echo Fact-Check** - Know the truth, instantly.
