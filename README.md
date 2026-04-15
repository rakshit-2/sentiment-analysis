# Sentiment Analysis System

A sentiment analysis system that integrates with OpenAI for LLM-powered analysis, AWS S3 for transcript storage, and MongoDB for data persistence.

## 🏗️ Project Structure

```
sentiment-analysis/
├── README.md
└── backend/
    ├── requirements.txt          # Python dependencies
    ├── .env.example             # Environment variables template
    ├── .gitignore               # Git ignore rules
    └── app/
        ├── __init__.py
        ├── main.py              # FastAPI application entry point
        ├── config.py            # Configuration & environment variables
        ├── models/              # Pydantic models & schemas
        │   ├── __init__.py
        │   ├── transcript.py    # Transcript model
        │   └── analysis.py      # Analysis & feedback model
        ├── database/            # Database connection
        │   ├── __init__.py
        │   └── connection.py    # MongoDB setup
        ├── services/            # Business logic layer
        │   ├── __init__.py
        │   ├── s3_service.py           # AWS S3 operations
        │   ├── openai_service.py       # OpenAI API integration
        │   └── transcript_service.py   # Transcript business logic
        └── routes/              # API endpoints
            ├── __init__.py
            ├── transcript.py    # Transcript endpoints
            └── analysis.py      # Analysis & feedback endpoints
```

## 🚀 Tech Stack

- **Backend Framework:** FastAPI
- **Database:** MongoDB
- **Storage:** AWS S3
- **LLM:** OpenAI API
- **Language:** Python 3.9+

## 📋 Prerequisites

- Python 3.9 or higher
- MongoDB (local or Atlas)
- AWS Account (S3 access)
- OpenAI API Key

## 🔧 Setup Instructions

### 1. Clone the repository
```bash
git clone <repository-url>
cd sentiment-analysis
```

### 2. Create virtual environment
```bash
cd backend
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### 5. Run the application
```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`
API Documentation (Swagger UI): `http://localhost:8000/docs`

## 📊 MongoDB Collections

### `transcripts`
Stores transcript metadata and content
- `transcript_id`: Unique identifier
- `s3_key`: S3 file path
- `s3_bucket`: S3 bucket name
- `content`: Transcript text
- `uploaded_at`: Upload timestamp
- `metadata`: Additional information

### `analyses`
Stores sentiment analysis results and feedback
- `analysis_id`: Unique identifier
- `transcript_id`: Reference to transcript
- `sentiment_result`: Analysis output from OpenAI
- `analyzed_at`: Analysis timestamp
- `feedback`: User feedback on analysis

## 🔌 API Endpoints

- `POST /api/transcripts/upload` - Upload transcript file
- `POST /api/transcripts/{transcript_id}/analyze` - Analyze transcript sentiment
- `GET /api/transcripts/{transcript_id}` - Get transcript details
- `GET /api/analyses/{analysis_id}` - Get analysis results
- `POST /api/analyses/{analysis_id}/feedback` - Add/update feedback
- `GET /api/transcripts` - List all transcripts
- `GET /api/analyses` - List all analyses

## 🔐 Environment Variables

See `.env.example` for required configuration:
- MongoDB connection string
- AWS credentials & S3 bucket
- OpenAI API key
- Application settings
