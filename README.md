# 📚 PDF Flashcard Generator

Transform your PDF documents into interactive study flashcards using AI! This application uses Google's Gemini API to analyze PDF content and generate intelligent flashcards for effective learning.

## ✨ Features

- **PDF Upload**: Support for text-based PDFs up to 5 pages
- **AI-Powered**: Uses Gemini API to generate intelligent flashcards
- **Interactive Study Mode**: Flip cards with smooth animations
- **Keyboard Navigation**: Study efficiently with keyboard shortcuts
- **Progress Tracking**: Visual progress bar and completion stats
- **Mobile Friendly**: Responsive design with touch gestures
- **Card Overview**: Sidebar with all flashcards for quick navigation

## 🏗️ Project Structure

```
flashcard-app/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── routers/
│   │   ├── __init__.py
│   │   └── flashcards.py       # Upload & processing endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_processor.py    # PDF text extraction
│   │   └── gemini_client.py    # Gemini API integration
│   ├── templates/
│   │   ├── index.html          # Upload page
│   │   └── study.html          # Flashcard study interface
│   └── static/
│       ├── css/style.css       # Styling + animations
│       └── js/flashcards.js    # Study mode logic
├── Dockerfile
├── pyproject.toml              # uv dependencies
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Google Gemini API key (free tier available)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd flashcard-app

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip sync pyproject.toml
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Gemini API key
GEMINI_API_KEY=your_actual_api_key_here
```

**Getting a Gemini API Key:**
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

### 3. Run the Application

#### Development Mode
```bash
# Run with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
```

#### Production Mode
```bash
# Run with uv
uv run uvicorn app.main:app --host 0.0.0.0 --port 5000
```

### 4. Using Docker

```bash
# Build the image
docker build -t flashcard-generator .

# Run the container
docker run -p 5000:5000 --env-file .env flashcard-generator
```

## 📖 Usage

1. **Upload PDF**: Visit `http://localhost:5000` and upload a text-based PDF (max 5 pages)
2. **Processing**: The app extracts text and generates flashcards using Gemini AI
3. **Study**: Review flashcards with flip animations and navigation controls
4. **Keyboard Shortcuts**:
   - `SPACE` - Flip current card
   - `←/→` - Navigate between cards  
   - `ESC` - Close sidebar

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `LOG_LEVEL` | Application log level | `INFO` |
| `MAX_FILE_SIZE_MB` | Maximum PDF file size in MB | `10` |

### API Limits (Free Tier)

- **Rate Limit**: ~15 requests per minute
- **Daily Quota**: ~1 million tokens per day
- **Context Window**: ~1 million tokens per request

## 🛠️ Development

### Running Tests
```bash
uv run pytest
```

### Code Formatting
```bash
uv run black app/
uv run isort app/
```

### Adding Dependencies
```bash
# Add a new dependency
uv add package-name

# Add development dependency
uv add --dev package-name
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Upload page |
| `/upload` | POST | Process PDF and generate flashcards |
| `/study/{session_id}` | GET | Study interface |
| `/api/session/{session_id}` | GET | Get session data as JSON |
| `/api/session/{session_id}` | DELETE | Delete study session |
| `/health` | GET | Health check |

## 🔍 Troubleshooting

### Common Issues

**PDF Processing Fails**
- Ensure PDF contains extractable text (not scanned images)
- Check file size is under 10MB
- Verify PDF has 5 pages or fewer

**Gemini API Errors**
- Verify API key is correct in `.env`
- Check rate limits aren't exceeded
- Ensure sufficient quota remains

**No Flashcards Generated**
- PDF might not contain sufficient text content
- Content might be too technical for current prompt
- Try PDFs with clear concepts and definitions

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
```

## 🎯 Technical Details

### PDF Processing
- Uses PyMuPDF for reliable text extraction
- Handles multi-page documents
- Cleans and formats extracted text
- Validates content sufficiency

### AI Integration
- Structured prompts for consistent output
- JSON response parsing with fallbacks
- Error handling and retry logic
- Token usage optimization

### Frontend Features
- CSS3 animations for card flips
- Touch gesture support
- Responsive design
- Progressive enhancement

## 🚀 Deployment

### Docker Production
```bash
# Build production image
docker build -t flashcard-generator:latest .

# Run with restart policy
docker run -d --name flashcards \
  --restart unless-stopped \
  -p 5000:5000 \
  --env-file .env \
  flashcard-generator:latest
```

### Health Monitoring
The app includes a health check endpoint at `/health` for monitoring tools.

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review logs with `LOG_LEVEL=DEBUG`
3. Open an issue with error details
4. Include PDF characteristics and error messages

**[🎪 Demo Video](https://youtu.be/nHUIKiLdYmA)**

**Happy Learning! 📚✨**
