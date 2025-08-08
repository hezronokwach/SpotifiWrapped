# SpotifiWrapped

SpotifiWrapped is a comprehensive, AI-powered interactive remake of Spotify Wrapped that transforms your music data into stunning, dynamic dashboards. Built with Dash, Plotly, and advanced AI analytics, it provides deep insights into your listening habits, personality analysis, and music trends with beautiful visualizations and real-time interactions. 🎶📊✨

![SpotifiWrapped Dashboard](https://via.placeholder.com/800x400?text=SpotifiWrapped+Dashboard)

## ✨ Key Features

### 🎵 **Music Analytics**
- **Interactive Charts**: Top tracks, artists, albums, and playlists with hover effects
- **Real-time Playback**: Live display of currently playing track with progress
- **Audio Features Analysis**: Danceability, energy, valence, and tempo visualizations
- **Genre Evolution**: Track how your music taste changes over time
- **Listening History**: Comprehensive tracking and analysis of your music journey

### 🤖 **AI-Powered Insights**
- **Personality Analysis**: AI-driven insights into your music personality type
- **Wellness Tracking**: Analyze music's impact on your mental wellness
- **Stress Detection**: Advanced algorithms to detect stress patterns in listening habits
- **Mood Analysis**: Understand how your music reflects and influences your emotions
- **Smart Recommendations**: AI-generated insights about your listening patterns

### 🎨 **User Experience**
- **Demo Mode**: Try the app with realistic sample data (no Spotify account needed)
- **Dark Theme**: Beautiful Spotify-inspired aesthetic with smooth animations
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Real-time Updates**: Live data refresh and interactive components
- **Intuitive Navigation**: Easy-to-use interface with guided onboarding

## 🚀 Quick Start

### Option 1: Try Demo Mode (No Spotify Account Required)
1. Clone and set up the project (steps 1-4 below)
2. Run `python app.py`
3. Open `http://127.0.0.1:8080/`
4. Click **"Try Sample Data"** to explore with realistic demo data
5. **Note**: Demo mode uses randomized placeholder images, not actual album artwork

### Option 2: Connect Your Spotify Account

## 📦 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/hezronokwach/SpotifiWrapped.git
   cd SpotifiWrapped
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root by copying the example:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file with your Spotify API credentials:
   ```env
   CLIENT_ID=your_spotify_client_id
   CLIENT_SECRET=your_spotify_client_secret
   REDIRECT_URI=http://127.0.0.1:8000/callback
   GEMINI_API_KEY=your_gemini_api_key  # Optional for AI features
   ```

5. **Run the application**
   ```bash
   python3 app.py
   ```

6. **Open your browser**
   Navigate to `http://127.0.0.1:8080/`
   
7. **Run tests (optional)**
   ```bash
   python3 tests/test_runner.py
   ```

## 🔑 Getting Spotify API Credentials

To use your real Spotify data:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Create a new app (click "Create App")
4. Fill in the app details:
   - App name: SpotifiWrapped
   - App description: Personal Spotify data visualization
   - Website: http://localhost:8000
   - Redirect URI: http://127.0.0.1:8000/callback
5. Accept the terms and click "Create"
6. Once created, you'll see your Client ID on the dashboard
7. Click "Show Client Secret" to reveal your Client Secret
8. Copy both values to your `.env` file

## 🎭 Demo Mode Features

The demo mode provides a full experience without requiring Spotify credentials:

- **Realistic Sample Data**: 50+ sample tracks, 30+ artists, 3 months of listening history
- **All Features Available**: Every chart, analysis, and AI insight works in demo mode
- **Placeholder Images**: Uses randomized images from Picsum for visual variety
- **Separate Database**: Demo data is isolated from any real user data
- **Easy Switching**: Switch to real Spotify data anytime from the settings

## 🏗️ Architecture

### **Database Structure**
- **Real Data**: `data/spotify_data.db` - Your actual Spotify data
- **Sample Data**: `data/sample_spotify_data.db` - Demo mode data
- **Clean Separation**: No mixing of real and sample data

### **Key Components**
- **Frontend**: Dash + Plotly for interactive visualizations
- **Backend**: Python with SQLite for data storage
- **API Integration**: Spotipy for Spotify Web API
- **AI Analytics**: Custom algorithms for personality and wellness analysis
- **Real-time Updates**: Live data refresh and playback tracking

### **Project Structure**
```
SpotifiWrapped/
├── app.py                 # Main application entry point
├── callback_server.py     # OAuth callback server
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment variables
├── assets/                # Static assets (CSS, JS)
│   ├── style.css          # Custom styling
│   └── futuristic-interactions.js  # Custom JavaScript
├── data/                  # Data storage
│   ├── spotify_data.db    # Main SQLite database
│   └── sample_spotify_data.db  # Demo data
├── logs/                  # Application logs
├── modules/               # Application modules
│   ├── api.py             # Spotify API integration
│   ├── database.py        # Database operations
│   ├── data_collector.py  # Data collection logic
│   ├── data_processing.py # Data processing utilities
│   ├── logging_config.py  # Centralized logging configuration
│   └── ...                # Other modules
├── tests/                 # Test suite
│   ├── test_database.py   # Database tests
│   ├── test_genre_extractor.py # Genre extraction tests
│   └── test_runner.py     # Test runner
└── scripts/               # Utility scripts
```



## 🛠️ Tech Stack

### **Core Framework**
- **Dash**: Interactive web applications
- **Plotly**: Dynamic data visualizations
- **Flask**: Web server foundation

### **Data & APIs**
- **Spotipy**: Spotify Web API integration
- **SQLite**: Local database storage
- **Pandas**: Data processing and analysis
- **NumPy**: Numerical computations

### **AI & Analytics**
- **Custom AI Models**: Personality and wellness analysis
- **Gemini API**: Advanced AI insights (optional)
- **Statistical Analysis**: Music pattern recognition

### **UI/UX**
- **CSS3**: Custom styling and animations
- **JavaScript**: Interactive components
- **Responsive Design**: Mobile-friendly interface

## 📊 Available Visualizations

- **Top Tracks Soundwave**: Animated waveform of your favorite songs
- **Artist Network**: Interactive network of your top artists
- **Genre Evolution**: Timeline of your changing music taste
- **Audio Features Radar**: Multi-dimensional analysis of track characteristics
- **Listening Patterns**: Heatmaps of when and what you listen to
- **Mood Analysis**: Emotional journey through your music
- **Wellness Dashboard**: Impact of music on your mental health

## 🤖 AI Features

### **Personality Analysis**
- Sonic Explorer, Mood Curator, Genre Hopper, and more personality types
- Confidence scores and detailed descriptions
- Listening pattern analysis

### **Wellness Tracking**
- Stress level detection through music choices
- Mood correlation analysis
- Wellness score calculation
- Personalized insights and recommendations

### **Smart Insights**
- Automatic pattern recognition
- Trend analysis and predictions
- Personalized music recommendations
- Behavioral insights

## 🔧 Configuration

### **Environment Variables**
```env
# Spotify API (Optional - for real data)
CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret
REDIRECT_URI=http://127.0.0.1:8000/callback

# AI Features (Optional)
GEMINI_API_KEY=your_gemini_api_key

# Application Settings
DEBUG=False
PORT=8080
```

### **Database Settings**
- Automatic database creation and migration
- Configurable data retention periods
- Backup and restore functionality

## 🚨 Troubleshooting

### **Common Issues**

1. **"No module named 'modules'"**
   - Ensure you're running from the project root directory
   - Check that all dependencies are installed
   - Make sure your virtual environment is activated

2. **Spotify API errors**
   - Verify your credentials in `.env`
   - Check redirect URI matches exactly (http://127.0.0.1:8000/callback)
   - Ensure your Spotify app is not in development mode restrictions
   - Check the logs in `logs/spotifi_wrapped.log` and `spotify_oauth.log`

3. **Database errors**
   - Delete `data/*.db` files to reset: `rm data/*.db`
   - Check file permissions in the `data/` directory
   - Ensure SQLite is installed

4. **Port already in use**
   - Change the port in `.env` file or kill the existing process
   - Default ports: 8080 (main app), 8000 (OAuth callback)

## 🧪 Testing

The project includes a comprehensive test suite:

```bash
# Run all tests
python3 tests/test_runner.py

# Run specific test modules
python3 -m unittest tests.test_database
python3 -m unittest tests.test_genre_extractor
```

**Test Coverage:**
- Database operations (18 tests)
- Genre extraction (18 tests)
- Total: 36 tests with 100% success rateet: `rm data/*.db`
   - Check file permissions in the `data/` directory: `chmod 755 data`
   - Ensure SQLite is installed: `sqlite3 --version`

4. **Port already in use**
   - Change the port in the code or kill the existing process
   - Use `lsof -i :8000` to find processes using the port
   - Kill the process: `kill -9 <PID>`
   
5. **Callback server issues**
   - Check if the callback server is running: `ps aux | grep callback_server`
   - Ensure ports 8000 and 8080 are available
   - Check firewall settings if running on a remote server

6. **Authentication problems**
   - Clear browser cookies and cache
   - Try using incognito/private browsing mode
   - Check if your Spotify account has the necessary permissions

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Format code
black .
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Spotify** for their amazing Web API
- **Plotly/Dash** for the excellent visualization framework
- **The Python Community** for the incredible ecosystem
- **Contributors** who help make this project better

## 🔮 Future Roadmap

- [ ] **Social Features**: Share your wrapped with friends
- [ ] **Export Options**: PDF/PNG export of your wrapped
- [ ] **Advanced AI**: More sophisticated personality analysis
- [ ] **Mobile App**: Native mobile application
- [ ] **Collaborative Playlists**: AI-generated collaborative playlists
- [ ] **Music Discovery**: Advanced recommendation engine
- [ ] **Integration**: Last.fm, Apple Music, YouTube Music support

---

**Made with ❤️ and 🎵 by music lovers, for music lovers**

*Transform your music data into beautiful insights and discover the story your listening habits tell about you.*