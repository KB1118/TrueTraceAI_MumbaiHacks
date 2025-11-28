# TrueTrace AI - Setup Guide

## Quick Start

### Prerequisites
- Python 3.8+ 
- Node.js 18+
- npm or yarn
- Google Gemini API key

## Installation Commands

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Create virtual environment (Linux/Mac)
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
# Windows PowerShell
Copy-Item .env.example .env

# Windows CMD
copy .env.example .env

# Linux/Mac
cp .env.example .env

# Edit .env file and add your GEMINI_API_KEY
# Then run the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Run development server
npm run dev
```

## Environment Configuration

### Backend (.env file)

Create `backend/.env` with the following:

```env
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key-here
DATABASE_URL=sqlite:///./truetrace.db
GEMINI_MODEL=gemini-2.0-flash-exp
```

**Important**: 
- Generate a secure SECRET_KEY (e.g., using `openssl rand -hex 32`)
- Get your Gemini API key from https://makersuite.google.com/app/apikey

### Frontend

The frontend will automatically use `http://localhost:8000` as the API URL. To change this, set the environment variable:

```bash
# Windows PowerShell
$env:NEXT_PUBLIC_API_URL="http://localhost:8000"
npm run dev

# Linux/Mac
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## Running the Application

1. **Start Backend** (Terminal 1):
   ```bash
   cd backend
   venv\Scripts\activate  # Windows
   # or: source venv/bin/activate  # Linux/Mac
   uvicorn app.main:app --reload --port 8000
   ```

2. **Start Frontend** (Terminal 2):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## First Steps

1. Open http://localhost:3000
2. Click "Register" to create an account
3. Login with your credentials
4. Navigate to Dashboard
5. Click "Trigger Pipeline" to start the misinformation detection process

## Troubleshooting

### Backend Issues

- **Import errors**: Make sure virtual environment is activated
- **Database errors**: Delete `truetrace.db` and restart (will recreate)
- **API key errors**: Verify GEMINI_API_KEY in .env file

### Frontend Issues

- **API connection errors**: Verify backend is running on port 8000
- **Build errors**: Delete `node_modules` and `.next`, then `npm install` again
- **TypeScript errors**: Run `npm run build` to see detailed errors

## Production Deployment

For production:
1. Set `SECRET_KEY` to a strong random value
2. Use PostgreSQL instead of SQLite
3. Set up proper CORS origins
4. Use environment variables for all secrets
5. Build frontend: `npm run build` then `npm start`

