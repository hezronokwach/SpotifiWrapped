# 🚀 Spotify Wrapped Remix - Hosting Guidelines

## 📋 Overview

This document provides comprehensive guidelines for hosting the Spotify Wrapped Remix platform using free-tier services with SQLite3 database.

## 🏗️ Platform Architecture

- **Backend**: Python Flask/Dash application
- **Database**: SQLite3 (file-based, no external database required)
- **Frontend**: Dash/React components with Bootstrap styling
- **Storage**: Local file system for database and cache files

## 🆓 Best Free Hosting Options

### 1. **Railway** ⭐ **RECOMMENDED**
- **Free Tier**: $5 credit monthly (usually covers small apps)
- **Pros**:
  - Easy deployment from GitHub
  - Automatic HTTPS
  - Custom domains
  - Persistent storage for SQLite
  - Good performance
- **Cons**: Credit-based (not truly unlimited)
- **Setup**: Connect GitHub repo, auto-deploy

### 2. **Render**
- **Free Tier**: 750 hours/month
- **Pros**:
  - Automatic deployments
  - Custom domains
  - HTTPS included
  - Good documentation
- **Cons**: 
  - Spins down after 15 minutes of inactivity
  - Limited persistent storage
- **Setup**: Connect GitHub, configure build commands

### 3. **Fly.io**
- **Free Tier**: 3 shared-cpu-1x VMs
- **Pros**:
  - Good performance
  - Global deployment
  - Persistent volumes
- **Cons**: More complex setup
- **Setup**: CLI-based deployment

### 4. **PythonAnywhere** (Limited)
- **Free Tier**: 1 web app
- **Pros**: Python-focused, easy setup
- **Cons**: Very limited resources, custom domains require paid plan

## 🔧 Deployment Configuration

### Required Files for Deployment

1. **requirements.txt**
```txt
dash==2.17.1
dash-bootstrap-components==1.5.0
plotly==5.17.0
pandas==2.1.4
spotipy==2.23.0
python-dotenv==1.0.0
google-generativeai==0.3.2
```

2. **Procfile** (for Railway/Render)
```
web: python app.py
```

3. **runtime.txt** (optional)
```
python-3.11.7
```

### Environment Variables Setup

Set these in your hosting platform:
```bash
# Spotify API (users will input these via UI)
# CLIENT_ID=your_spotify_client_id
# CLIENT_SECRET=your_spotify_client_secret
# REDIRECT_URI=https://yourdomain.com/callback

# AI Features (optional)
GEMINI_API_KEY=your_gemini_api_key

# App Configuration
PORT=8051
DEBUG=False
```

## 🗄️ Database Configuration

### SQLite3 Setup
- **File**: `data/spotify_data.db`
- **Advantages**: 
  - No external database required
  - Zero configuration
  - Perfect for single-user or small multi-user apps
  - Persistent storage

### Data Directory Structure
```
data/
├── spotify_data.db          # Main SQLite database
├── *.csv                    # Cache files (optional)
└── wrapped_summary.json     # Summary cache
```

### Persistent Storage Requirements
- Ensure your hosting platform supports persistent file storage
- Database file must persist between deployments
- Recommended: 1GB storage minimum

## 🚀 Step-by-Step Deployment (Railway)

### 1. Prepare Repository
```bash
# Clone your repository
git clone https://github.com/yourusername/SpotifiWrapped
cd SpotifiWrapped

# Ensure all required files exist
ls requirements.txt Procfile app.py
```

### 2. Railway Deployment
1. Visit [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your SpotifiWrapped repository
5. Railway auto-detects Python and deploys

### 3. Configure Environment
1. Go to your project → Variables tab
2. Add environment variables (optional for Gemini AI)
3. Set custom domain (optional)

### 4. Database Initialization
- SQLite database will be created automatically on first run
- No manual database setup required

## 🔒 Security Considerations

### 1. Environment Variables
- Never commit API keys to repository
- Use platform environment variables
- Users input their own Spotify credentials via UI

### 2. HTTPS
- All recommended platforms provide automatic HTTPS
- Required for Spotify OAuth callbacks

### 3. Domain Configuration
- Update Spotify app redirect URI to match your domain
- Example: `https://yourapp.railway.app/callback`

## 📊 Resource Requirements

### Minimum Specifications
- **RAM**: 512MB (1GB recommended)
- **Storage**: 1GB for database and cache
- **CPU**: 1 shared vCPU sufficient
- **Bandwidth**: ~10GB/month for moderate usage

### Performance Optimization
```python
# In app.py, add for production:
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8051))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run_server(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
```

## 🔄 Deployment Workflow

### Automatic Deployment
1. Push code to GitHub main branch
2. Platform automatically detects changes
3. Rebuilds and redeploys application
4. Database persists through deployments

### Manual Deployment Commands
```bash
# For Railway CLI
railway login
railway link
railway up

# For Render
# Use GitHub integration (recommended)

# For Fly.io
fly deploy
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Not Persisting**
   - Ensure persistent storage is enabled
   - Check data directory permissions

2. **Spotify OAuth Errors**
   - Verify redirect URI matches exactly
   - Check HTTPS is enabled

3. **Memory Issues**
   - Reduce cache size in configuration
   - Optimize database queries

4. **Port Binding Issues**
```python
# Ensure app binds to correct port
port = int(os.environ.get('PORT', 8051))
app.run_server(host='0.0.0.0', port=port)
```

## 📈 Scaling Considerations

### Free Tier Limitations
- **Railway**: $5 credit/month (~750 hours)
- **Render**: 750 hours/month, sleeps after 15min
- **Fly.io**: 3 VMs, limited resources

### When to Upgrade
- High traffic (>1000 users/month)
- Need 24/7 uptime
- Require custom domains
- Need more storage/bandwidth

## 🔧 Production Optimizations

### 1. Caching
```python
# Enable caching for better performance
import functools
import time

@functools.lru_cache(maxsize=128)
def cached_spotify_call(user_id, endpoint):
    # Cache expensive API calls
    pass
```

### 2. Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_listening_history_user_time 
ON listening_history (user_id, played_at);

CREATE INDEX IF NOT EXISTS idx_tracks_artist 
ON tracks (artist);
```

### 3. Error Handling
```python
# Add comprehensive error handling
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## 📞 Support & Monitoring

### Health Checks
- Most platforms provide automatic health monitoring
- App includes built-in error handling
- Database integrity checks on startup

### Logs
- Access logs through platform dashboard
- Monitor for Spotify API rate limits
- Track user authentication issues

## 🎯 Recommended Setup: Railway

For the best free hosting experience:

1. **Use Railway** for hosting
2. **Enable persistent storage** for SQLite
3. **Set up automatic deployments** from GitHub
4. **Configure custom domain** (optional)
5. **Monitor usage** to stay within free tier

This setup provides the best balance of features, performance, and ease of use for the Spotify Wrapped Remix platform.

## 📋 Pre-Deployment Checklist

### Code Preparation
- [ ] Remove any hardcoded API keys
- [ ] Update redirect URIs for production domain
- [ ] Test application locally
- [ ] Ensure requirements.txt is up to date
- [ ] Add Procfile for web process
- [ ] Configure production settings

### Platform Setup
- [ ] Create account on chosen platform
- [ ] Connect GitHub repository
- [ ] Configure environment variables
- [ ] Set up custom domain (optional)
- [ ] Enable persistent storage
- [ ] Test deployment

### Post-Deployment
- [ ] Verify application loads correctly
- [ ] Test Spotify OAuth flow
- [ ] Check database creation
- [ ] Monitor logs for errors
- [ ] Test all major features
- [ ] Set up monitoring/alerts

## 🔗 Quick Start Commands

### Create Production-Ready Files

1. **Create Procfile**:
```bash
echo "web: python app.py" > Procfile
```

2. **Update app.py for production**:
```python
# Add at the end of app.py
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8051))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'

    app.run_server(
        host='0.0.0.0',
        port=port,
        debug=debug,
        dev_tools_hot_reload=False
    )
```

3. **Generate requirements.txt**:
```bash
pip freeze > requirements.txt
```

## 🌐 Domain & SSL Configuration

### Custom Domain Setup
1. **Railway**: Project Settings → Domains → Add Custom Domain
2. **Render**: Dashboard → Settings → Custom Domains
3. **Fly.io**: `fly certs add yourdomain.com`

### Spotify App Configuration
Update your Spotify Developer Dashboard:
- **Redirect URIs**: `https://yourdomain.com/callback`
- **Website**: `https://yourdomain.com`

## 💰 Cost Estimation

### Free Tier Usage (Monthly)
- **Railway**: $5 credit (usually sufficient for small apps)
- **Render**: 750 hours (31 days if always running)
- **Fly.io**: 3 VMs with 160GB-hours

### Typical Usage Patterns
- **Light usage** (1-10 users): Stays within free tier
- **Medium usage** (10-50 users): May need paid tier
- **Heavy usage** (50+ users): Definitely needs paid tier

## 🚨 Important Notes

### Spotify API Limitations
- **Rate Limits**: 100 requests per minute per user
- **Scope Requirements**: User must grant appropriate permissions
- **Token Expiry**: Tokens refresh automatically

### Data Privacy
- User data stored locally in SQLite
- No data shared with third parties
- Users control their own data
- GDPR compliant with proper usage

### Backup Strategy
```bash
# Regular database backups (if needed)
cp data/spotify_data.db backups/spotify_data_$(date +%Y%m%d).db
```

This comprehensive guide should help you successfully deploy and maintain your Spotify Wrapped Remix platform! 🎉
