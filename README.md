# TrueTrace AI

TrueTrace AI is an agentic misinformation detection and verification ecosystem. The system automatically monitors global open-source information streams, detects emerging misinformation, and provides transparent, evidence-based fact-checking.

## Project Structure

```
truetrace-ai/
├── backend/          # FastAPI backend
│   ├── app/         # Application code
│   ├── requirements.txt
│   └── .env.example
├── frontend/        # Next.js frontend
│   ├── src/
│   │   ├── pages/   # Next.js pages
│   │   ├── components/  # React components
│   │   ├── lib/     # API client
│   │   └── styles/  # CSS styles
│   └── package.json
└── README.md
```

## Features

- **Real-Time Monitoring**: Continuously scans trusted news sources and social platforms
- **Intelligent Clustering**: Uses semantic analysis to identify rumor clusters
- **Evidence-Based Verification**: Retrieves evidence from authoritative sources
- **Transparent Results**: Provides confidence scores, volatility metrics, and detailed reasoning

## Technology Stack

### Backend
- FastAPI
- SQLAlchemy
- LangChain
- Google Gemini 2.5 Flash
- JWT Authentication

### Frontend
- Next.js 14
- React 18
- TypeScript
- Axios

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
cp .env.example .env
```

5. Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your-gemini-api-key-here
SECRET_KEY=your-secret-key-here
```

6. Run the backend server:
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

## Usage

1. **Register/Login**: Create an account or login to access the dashboard
2. **Trigger Pipeline**: Click "Trigger Pipeline" to start the misinformation detection process
3. **View Crises**: Browse detected crises in the sidebar
4. **Explore Claims**: View verified claims with verdicts, confidence scores, and evidence
5. **Filter Results**: Filter claims by crisis or verdict type

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token
- `GET /api/v1/auth/me` - Get current user info

### Crises
- `GET /api/v1/crises` - List all crises
- `GET /api/v1/crises/{id}` - Get specific crisis

### Claims
- `GET /api/v1/claims` - List all claims (with filters)
- `GET /api/v1/claims/{id}` - Get specific claim with cards

### Verification
- `POST /api/v1/verify` - Verify free-form text

### Pipeline
- `POST /api/v1/pipeline/trigger` - Trigger the radar pipeline
- `GET /api/v1/pipeline/status` - Get pipeline status

## Development

### Backend Development
- The backend uses SQLite by default (can be changed in `.env`)
- Database tables are created automatically on first run
- Use `--reload` flag for auto-reload during development

### Frontend Development
- Next.js hot-reload is enabled by default
- TypeScript is configured for type safety
- API client is configured to use `http://localhost:8000` by default

## Environment Variables

### Backend (.env)
- `SECRET_KEY`: Secret key for JWT tokens
- `GEMINI_API_KEY`: Google Gemini API key (required)
- `DATABASE_URL`: Database connection string
- `GEMINI_MODEL`: Gemini model to use (default: gemini-2.0-flash-exp)

### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

## License

This project is part of a hackathon submission.

