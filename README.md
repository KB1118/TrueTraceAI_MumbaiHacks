# TrueTrace AI

TrueTrace AI is an agentic misinformation detection and verification ecosystem. The system automatically monitors global open-source information streams, detects emerging misinformation, and provides transparent, evidence-based fact-checking powered by Google Gemini 2.5 Flash and advanced AI reasoning.

##  Overview

TrueTrace AI combines real-time social media monitoring, intelligent clustering, and evidence-based verification to combat misinformation. The platform features:

- **Automated Crisis Detection**: Uses Gemini-powered web search to identify emerging global crises
- **Social Media Monitoring**: Scrapes Reddit and Telegram for crisis-related content
- **Intelligent Clustering**: Semantic analysis groups similar rumors and claims
- **Evidence-Based Verification**: Grounded Google Search verification with detailed reasoning
- **Multimodal Fact-Checking**: Analyze images, videos, and audio with contextual verification
- **Interactive Dashboard**: Real-time visualization of crises, claims, and verification results

##  Project Structure

```
full_app/
├── backend/                    # FastAPI backend server
│   ├── app/
│   │   ├── services/          # Core service modules
│   │   │   ├── data_extraction_service.py    # CrisisMonitor, ClaimBot, GeminiVerifier
│   │   │   └── multimodal_fact_checker.py    # Multimodal analysis service
│   │   ├── pipeline.py        # Main radar pipeline orchestrator
│   │   ├── routes.py          # API endpoints
│   │   ├── models.py          # SQLAlchemy database models
│   │   ├── auth.py            # JWT authentication
│   │   ├── llm.py             # LLM utilities for claim generation
│   │   ├── config.py          # Configuration management
│   │   └── database.py        # Database connection
│   ├── requirements.txt
│   └── env.template
├── frontend/                   # Next.js frontend application
│   ├── src/
│   │   ├── pages/             # Next.js pages
│   │   │   ├── dashboard.tsx         # Main dashboard (MVP branch)
│   │   │   ├── multimodal-check.tsx   # Multimodal fact-checker (MVP branch)
│   │   │   ├── index.tsx              # Landing page
│   │   │   ├── login.tsx              # Authentication
│   │   │   └── register.tsx           # User registration
│   │   ├── components/        # React components
│   │   │   ├── ClaimVerdictCard.tsx   # Claim display cards
│   │   │   ├── CrisisList.tsx       # Crisis sidebar
│   │   │   ├── RumorClusters.tsx     # Cluster visualization
│   │   │   └── Navbar.tsx            # Navigation bar
│   │   ├── lib/               # API client utilities
│   │   └── styles/            # CSS stylesheets
│   └── package.json
└── README.md
```

##  Branch Information

This repository contains multiple components across different branches:

- **`MVP`** (Current Branch): Contains the main dashboard and multimodal fact-checker interface
  - Full-featured Next.js dashboard for viewing crises, claims, and verification results
  - Multimodal fact-checking page for analyzing images, videos, and audio files
  - Complete backend API with pipeline orchestration

- **`chrome_extension`**: Browser extension for real-time fact-checking
  - Chrome extension that allows users to verify claims directly from web pages
  - Integrates with the TrueTrace AI backend API
  - Provides instant fact-checking results while browsing

##  Core Components

### Backend Components

#### 1. **Data Extraction Service** (`services/data_extraction_service.py`)

The core data extraction and verification engine:

- **`CrisisMonitor`**: Main orchestrator for crisis detection and monitoring
  - Extracts crisis keywords using Gemini web search
  - Discovers relevant Reddit subreddits and Telegram channels
  - Scrapes social media content for crisis-related posts
  - Groups posts by keyword and performs semantic clustering
  - Uses Sentence Transformers for embedding-based clustering

- **`ClaimBot`**: Extracts canonical claims from document clusters
  - Uses Ollama LLM (gpt-oss:20b-cloud) to extract verifiable claims
  - Filters out personal/private information
  - Focuses on public, news-verifiable factual claims
  - Outputs numbered list of claims per cluster

- **`GeminiVerifier`**: Performs grounded fact-checking
  - Uses Gemini 2.5 Flash with Google Search grounding
  - Returns structured verdicts: `supports`, `contradicts`, or `unrelated`
  - Provides detailed reasoning and source citations
  - Handles JSON parsing with fallback mechanisms

- **`WebSearchBot`**: Gemini-powered web search utility
  - Performs real-time grounded web searches
  - Used for crisis keyword extraction and verification

#### 2. **Multimodal Fact Checker** (`services/multimodal_fact_checker.py`)

Advanced multimodal analysis service:

- Analyzes images, videos, and audio files using Gemini 2.5 Flash
- Extracts factual claims from multimedia content
- Performs grounded Google Search verification
- Returns detailed analysis with source citations
- Handles file uploads, processing, and cleanup automatically

#### 3. **Pipeline Orchestrator** (`pipeline.py`)

The main pipeline that coordinates the entire verification workflow:

1. **Crisis Detection**: Extracts crisis keywords using Gemini web search
2. **Source Discovery**: Auto-discovers relevant Reddit subreddits and Telegram channels
3. **Data Collection**: Scrapes social media posts for each keyword
4. **Deduplication**: Removes duplicate posts by URL
5. **Clustering**: Groups posts by keyword and performs semantic clustering
6. **Claim Extraction**: Extracts canonical claims from each cluster using ClaimBot
7. **Verification**: Verifies claims using GeminiVerifier with grounded search
8. **Persistence**: Saves crises, clusters, claims, and result cards to database
9. **Result Generation**: Creates audience-specific result cards (general, journalist, researcher)

#### 4. **Database Models** (`models.py`)

SQLAlchemy models for data persistence:

- **`User`**: User authentication and profiles
- **`Crisis`**: Detected crisis events with metadata
- **`RumorCluster`**: Clustered groups of related posts
- **`Claim`**: Extracted and verified claims with verdicts
- **`ResultCard`**: Audience-specific formatted results

#### 5. **API Routes** (`routes.py`)

RESTful API endpoints:

- **Authentication**: Register, login, user management
- **Crises**: List and retrieve crisis information
- **Claims**: Query claims with filtering and pagination
- **Verification**: Free-form text verification endpoint
- **Multimodal**: File upload and analysis endpoint
- **Pipeline**: Trigger and monitor pipeline execution

### Frontend Components

#### 1. **Dashboard** (`pages/dashboard.tsx`) - MVP Branch

Main interactive dashboard featuring:

- **Crisis Sidebar**: Lists all detected crises with filtering
- **Claim Cards**: Displays verified claims with verdicts, confidence scores, and reasoning
- **Rumor Clusters**: Visualizes clustered posts by topic
- **Pipeline Controls**: Trigger and monitor pipeline execution
- **Real-time Updates**: Auto-refreshes to show latest results

#### 2. **Multimodal Checker** (`pages/multimodal-check.tsx`) - MVP Branch

Standalone multimodal fact-checking interface:

- **File Upload**: Supports images, videos, and audio files
- **Text Input**: Optional text description/context
- **Context Field**: Provenance information (e.g., "Forwarded on WhatsApp")
- **Analysis Results**: Displays verdict, reasoning, and source citations
- **File Metadata**: Shows processed file information

#### 3. **Reusable Components**

- **`ClaimVerdictCard`**: Displays individual claim with verdict badge and evidence
- **`CrisisList`**: Sidebar component for crisis navigation
- **`RumorClusters`**: Visual representation of post clusters
- **`Navbar`**: Top navigation with theme switching

##  Features

### Real-Time Monitoring
- Continuously scans Reddit and Telegram for crisis-related content
- Auto-discovers relevant subreddits and channels
- Filters and deduplicates posts automatically

### Intelligent Clustering
- Uses Sentence Transformers (all-MiniLM-L6-v2) for semantic embeddings
- Dynamic K-means clustering based on post volume
- Groups similar rumors and claims together

### Evidence-Based Verification
- Grounded Google Search via Gemini 2.5 Flash
- Retrieves evidence from authoritative sources
- Provides confidence scores and volatility metrics
- Detailed reasoning paths for every verdict

### Multimodal Analysis
- Supports images, videos, and audio files
- Automatic transcription and content extraction
- Context-aware verification with provenance tracking
- Source citations with rendered content

### Transparent Results
- Three verdict types: `True`, `False`, `Uncertain`
- Confidence scores (0.0 - 1.0)
- Volatility metrics for claim stability
- Audience-specific result cards (general, journalist, researcher)

##  Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **Google Gemini 2.5 Flash**: LLM for verification and analysis
- **Ollama**: Local LLM for claim extraction (gpt-oss:20b-cloud)
- **Sentence Transformers**: Semantic embeddings for clustering
- **JWT**: Secure authentication
- **Pydantic**: Data validation and settings management

### Frontend
- **Next.js 14**: React framework with SSR
- **React 18**: UI library
- **TypeScript**: Type-safe development
- **Axios**: HTTP client for API calls
- **CSS Modules**: Scoped styling

### Data Sources
- **Reddit**: RSS feed scraping for crisis-related posts
- **Telegram**: Public channel web preview scraping
- **Google Search**: Grounded search for evidence retrieval

##  Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Ollama installed locally (for ClaimBot)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from template:
```bash
# Windows
copy env.template .env
# Linux/Mac
cp env.template .env
```

5. Configure environment variables in `.env`:
```env
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key-here
DATABASE_URL=sqlite:///./truetrace.db
GEMINI_MODEL=gemini-2.5-flash
OLLAMA_MODEL=gpt-oss:20b-cloud
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
```

6. Start Ollama (if using ClaimBot):
```bash
ollama serve
ollama pull gpt-oss:20b-cloud
```

7. Run the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`  
API documentation at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

##  Usage

### Dashboard Workflow

1. **Register/Login**: Create an account or login to access the dashboard
2. **Trigger Pipeline**: Click "Trigger Pipeline" to start the misinformation detection process
   - The pipeline will:
     - Extract crisis keywords using Gemini
     - Discover and scrape Reddit/Telegram sources
     - Cluster posts by semantic similarity
     - Extract claims from clusters
     - Verify claims with grounded search
     - Generate result cards
3. **View Crises**: Browse detected crises in the sidebar
4. **Explore Claims**: View verified claims with verdicts, confidence scores, and evidence
5. **Filter Results**: Filter claims by crisis or verdict type
6. **View Clusters**: Explore rumor clusters to see grouped posts

### Multimodal Fact-Checking

1. Navigate to `/multimodal-check`
2. Upload an image, video, or audio file (optional)
3. Add text description if needed
4. Provide context/provenance information
5. Click "Verify content"
6. Review the analysis, verdict, and source citations

### Free-Form Verification

Use the `/api/v1/verify` endpoint to verify any text claim:
```bash
curl -X POST http://localhost:8000/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"text": "Your claim here"}'
```

##  API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token
- `GET /api/v1/auth/me` - Get current user info

### Crises
- `GET /api/v1/crises` - List all crises (with pagination)
- `GET /api/v1/crises/{id}` - Get specific crisis with clusters

### Claims
- `GET /api/v1/claims` - List all claims (with filters: `crisis_id`, `verdict`, `limit`, `offset`)
- `GET /api/v1/claims/{id}` - Get specific claim with result cards

### Verification
- `POST /api/v1/verify` - Verify free-form text claim
  - Request: `{"text": "claim to verify"}`
  - Response: Verdict, reasoning, evidence citations

### Multimodal
- `POST /api/v1/multimodal/analyze` - Analyze multimedia content
  - Form data: `file` (optional), `text` (optional), `context` (optional)
  - Response: Analysis text, verdict summary, sources, file metadata

### Pipeline
- `POST /api/v1/pipeline/trigger` - Trigger the radar pipeline (requires auth)
- `GET /api/v1/pipeline/status` - Get pipeline execution status

##  Environment Variables

### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Secret key for JWT tokens | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///./truetrace.db` |
| `GEMINI_MODEL` | Gemini model name | `gemini-2.5-flash` |
| `OLLAMA_MODEL` | Ollama model for claim extraction | `gpt-oss:20b-cloud` |
| `SENTENCE_TRANSFORMER_MODEL` | Embedding model | `all-MiniLM-L6-v2` |
| `MAX_PIPELINE_CLUSTERS` | Max clusters per keyword | `10` |
| `SCRAPE_KEYWORD_LIMIT` | Keywords to scrape | `2` |
| `REDDIT_POST_LIMIT` | Posts per keyword | `15` |
| `TELEGRAM_POST_LIMIT` | Messages per channel | `50` |
| `CLAIMS_PER_CLUSTER` | Claims to extract | `5` |

### Frontend

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

##  Development

### Backend Development
- Database tables are created automatically on first run
- Use `--reload` flag for auto-reload during development
- Check `backend/app/config.py` for all configuration options
- Logging is configured with DEBUG level for detailed pipeline tracking

### Frontend Development
- Next.js hot-reload is enabled by default
- TypeScript provides type safety
- API client is in `src/lib/api.ts`
- Theme context supports dark/light mode switching

### Testing the Pipeline
1. Ensure Ollama is running with the required model
2. Set `GEMINI_API_KEY` in backend `.env`
3. Trigger pipeline via dashboard or API
4. Monitor logs for detailed execution steps
5. Check database for persisted results

##  Data Flow

```
1. Pipeline Trigger
   ↓
2. Gemini Web Search → Extract Crisis Keywords
   ↓
3. Discover Sources → Reddit Subreddits + Telegram Channels
   ↓
4. Scrape Content → Posts filtered by keywords
   ↓
5. Deduplicate → Remove duplicate URLs
   ↓
6. Group by Keyword → Organize posts
   ↓
7. Semantic Clustering → K-means on embeddings
   ↓
8. Claim Extraction → Ollama LLM extracts claims
   ↓
9. Verification → Gemini + Google Search fact-checking
   ↓
10. Persistence → Save to database
   ↓
11. Result Cards → Generate audience-specific cards
```

##  Troubleshooting

### Pipeline Issues
- **No keywords extracted**: Check Gemini API key and quota
- **No posts scraped**: Verify Reddit/Telegram sources are accessible
- **Claims empty**: Ensure Ollama is running and model is pulled
- **Verification fails**: Check Gemini API key and Google Search grounding

### Frontend Issues
- **API connection errors**: Verify backend is running on port 8000
- **Authentication fails**: Check JWT secret key configuration
- **Multimodal upload fails**: Verify file size limits and Gemini API quota

## License

All rights are owned by Power Buff Gurls.
This project is not open-source and may not be redistributed, modified, or used commercially without explicit permission.



---

**Note**: The dashboard and multimodal detector are available on the `MVP` branch. The Chrome extension is available on the `chrome_extension` branch.
