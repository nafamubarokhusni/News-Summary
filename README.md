# News Summary AI

An intelligent web application that uses AI to generate concise summaries of news articles from any URL. Simply paste a news article link and get an AI-powered summary in seconds.

## Features

- **Smart Content Extraction**: Automatically extracts article content from news URLs
- **AI-Powered Summarization**: Uses IBM Granite-3.3-8B-Instruct for intelligent summarization (with fallback)
- **Clean Modern UI**: Responsive design that works on all devices
- **Fast Processing**: Quick article analysis and summary generation
- **Copy & Share**: Easy copy-to-clipboard functionality
- **Error Handling**: Robust error handling for invalid URLs and processing failures

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **AI**: IBM Granite-3.3-8B-Instruct API (optional)
- **Content Extraction**: BeautifulSoup4, Requests
- **Styling**: CSS Grid/Flexbox, Google Fonts, Font Awesome

## Quick Start

### Prerequisites

- Python 3.7+
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/nafamubarokhusni/News-Summary.git
cd News-Summary
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up Replicate API:
```bash
cp .env.example .env
# Edit .env and add your Replicate API key
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Usage

1. **Enter URL**: Paste any news article URL into the input field
2. **Get Summary**: Click "Summarize" or press Ctrl+Enter
3. **Read Results**: View the AI-generated summary
4. **Copy & Share**: Use the copy button to share the summary

### Supported News Sources

The application works with most news websites including:
- BBC News
- CNN
- Reuters
- The Guardian
- Associated Press
- And many more!

## Configuration

### Environment Variables

- `REPLICATE_API_TOKEN`: Your Replicate API key (optional)
- `FLASK_ENV`: Flask environment (development/production)
- `FLASK_DEBUG`: Enable debug mode (True/False)

### Without Replicate API

The application includes a fallback summarization method that works without the Replicate API key. It will use extractive summarization techniques to generate basic summaries.

## API Endpoints

### POST /api/summarize
Summarize a news article from URL.

**Request Body:**
```json
{
  "url": "https://example.com/news-article"
}
```

**Response:**
```json
{
  "success": true,
  "title": "Article Title",
  "summary": "AI-generated summary...",
  "url": "https://example.com/news-article"
}
```

### GET /api/health
Health check endpoint.

## Development

### Project Structure
```
News-Summary/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env.example       # Environment configuration template
├── templates/
│   └── index.html     # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css  # Stylesheet
│   └── js/
│       └── script.js  # Frontend JavaScript
└── README.md          # Documentation
```

### Running in Development Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

### Production Deployment

For production deployment with Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

Built with ❤️ using Python Flask and AI technology.
