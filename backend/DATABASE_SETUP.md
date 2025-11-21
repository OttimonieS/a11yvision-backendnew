# Database Setup with Supabase

## ✅ Configuration Complete

Your Supabase database is already configured in the `.env` file.

## 🚀 Quick Start

### 1. Install Python Dependencies

```powershell
cd C:\Users\TestUser\LabNexus\VIsionAI\backend\app
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Initialize Database Tables

```powershell
python init_db.py
```

This will:

- Create all necessary tables (users, scans, issues, activity_logs, etc.)
- Optionally seed test data
- Test user: `test@example.com` / `password123`

### 3. Start the Backend Server

```powershell
uvicorn main:app --reload
```

## 📊 View Your Database

### Option 1: Supabase Dashboard (Easiest)

1. Go to https://xwngeybzalnemzlaedqu.supabase.co
2. Click **Table Editor** in the sidebar
3. You'll see all tables: users, scans, issues, activity_logs, etc.
4. Click any table to view/edit data directly

### Option 2: SQL Editor (Advanced)

1. In Supabase dashboard, click **SQL Editor**
2. Run queries like:

```sql
-- View all users
SELECT * FROM users;

-- View recent activity
SELECT * FROM activity_logs ORDER BY created_at DESC LIMIT 20;

-- View scans by user
SELECT s.*, u.email
FROM scans s
JOIN users u ON s.user_id = u.id
ORDER BY s.created_at DESC;

-- Activity stats
SELECT action, COUNT(*) as count
FROM activity_logs
GROUP BY action
ORDER BY count DESC;
```

## 📋 Database Schema

### Tables Created:

- **users** - User accounts (id, email, name, password_hash, created_at)
- **sessions** - Login sessions (token, user_id, expires_at)
- **scans** - Accessibility scans (scan_id, user_id, url, status, issues_count)
- **issues** - Individual issues found (id, scan_id, rule, severity, message)
- **user_settings** - User preferences (user_id, contrast_threshold, rescan_cadence)
- **api_keys** - API keys for programmatic access
- **activity_logs** - Complete audit trail of user actions

## 🔍 Tracking User Activity

Every action is logged automatically:

- `signup` - New user registration
- `login` / `logout` - Authentication
- `scan_created` - New scan started
- `scan_completed` - Scan finished
- `settings_updated` - Settings changed
- `api_key_created` / `api_key_deleted` - API key management

View in Supabase:

1. Go to **Table Editor** → **activity_logs**
2. See all user actions with timestamps, IP addresses, and details

## 🛠️ Useful Queries for Monitoring

### See all users and their scan counts:

```sql
SELECT
  u.email,
  u.name,
  COUNT(s.scan_id) as total_scans,
  u.created_at as joined_date
FROM users u
LEFT JOIN scans s ON u.id = s.user_id
GROUP BY u.id, u.email, u.name, u.created_at
ORDER BY total_scans DESC;
```

### See user activity by type:

```sql
SELECT
  u.email,
  a.action,
  COUNT(*) as count
FROM activity_logs a
JOIN users u ON a.user_id = u.id
GROUP BY u.email, a.action
ORDER BY u.email, count DESC;
```

### See recent scans with issues:

```sql
SELECT
  s.scan_id,
  u.email,
  s.url,
  s.status,
  s.issues_count,
  s.created_at
FROM scans s
JOIN users u ON s.user_id = u.id
ORDER BY s.created_at DESC
LIMIT 50;
```

## 🔐 Security Notes

- Database password is URL-encoded in connection string (# → %23)
- Supabase provides automatic SSL/TLS encryption
- Never commit `.env` file to git (already in .gitignore)
- Row Level Security (RLS) can be enabled in Supabase for additional protection

## 🎯 Next Steps

After running `python init_db.py`:

1. Check Supabase dashboard to verify tables were created
2. Test the application by signing up a new user
3. Monitor activity_logs table to see actions being tracked
4. Use SQL editor for custom queries and reporting
