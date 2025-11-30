# MySQL Database Setup Guide

This guide will help you migrate from SQLite to MySQL for the TrueTrace AI backend.

## Prerequisites

1. **MySQL Server** installed and running
   - Download from: https://dev.mysql.com/downloads/mysql/
   - Or use a cloud service like AWS RDS, Google Cloud SQL, etc.

2. **Python MySQL Driver** installed
   ```bash
   pip install pymysql
   # OR
   pip install mysql-connector-python
   ```

## Setup Steps

### 1. Create MySQL Database

Connect to your MySQL server and create the database:

```sql
CREATE DATABASE truetrace CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Create MySQL User (Optional but Recommended)

Create a dedicated user for the application:

```sql
CREATE USER 'truetrace_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON truetrace.* TO 'truetrace_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Configure Environment Variables

Copy the template file and fill in your MySQL credentials:

```bash
cp env.template .env
```

Edit `.env` and update the MySQL configuration:

```env
# Database - MySQL Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=truetrace_user  # or 'root' if using root user
DB_PASSWORD=your_secure_password
DB_NAME=truetrace
DB_DRIVER=pymysql  # or 'mysqlconnector' if using mysql-connector-python
```

### 4. Install Dependencies

Make sure you have the MySQL driver installed:

```bash
pip install -r requirements.txt
```

### 5. Initialize Database Tables

The application will automatically create tables on first run. However, if you want to create them manually:

```python
from app.database import engine, Base
from app.models import User, Crisis, RumorCluster, Claim, ResultCard

# Create all tables
Base.metadata.create_all(bind=engine)
```

Or run the FastAPI server - it will create tables automatically:

```bash
uvicorn app.main:app --reload
```

## Migration from SQLite (Optional)

If you have existing data in SQLite and want to migrate:

1. Export data from SQLite
2. Import into MySQL
3. Or use a migration tool like `sqlalchemy-migrate` or `alembic`

## Connection String Format

The application constructs the MySQL connection string automatically from environment variables:

- **pymysql**: `mysql+pymysql://user:password@host:port/database?charset=utf8mb4`
- **mysqlconnector**: `mysql+mysqlconnector://user:password@host:port/database?charset=utf8mb4`

## Troubleshooting

### Connection Refused
- Check MySQL server is running: `mysql -u root -p`
- Verify host and port in `.env`

### Access Denied
- Verify username and password
- Check user has privileges on the database

### Database Does Not Exist
- Create the database first: `CREATE DATABASE truetrace;`

### Character Encoding Issues
- Ensure database uses `utf8mb4` charset
- The connection string includes `charset=utf8mb4` parameter

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | MySQL server hostname | `localhost` |
| `DB_PORT` | MySQL server port | `3306` |
| `DB_USER` | MySQL username | `root` |
| `DB_PASSWORD` | MySQL password | (empty) |
| `DB_NAME` | Database name | `truetrace` |
| `DB_DRIVER` | Driver to use: `pymysql` or `mysqlconnector` | `pymysql` |

