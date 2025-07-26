# SpotifyWrappedRemix

SpotifyWrappedRemix is a Python-powered, interactive remake of Spotify Wrapped, transforming your music data into dynamic dashboards. Built with Dash, Plotly, and Spotipy, it visualizes top tracks, artists, and more with hover, click, and filter interactions for a personalized experience. A journey in Python and data viz! 🎶📊

## Features
- Interactive charts for top tracks, saved tracks, and playlists.
- Real-time display of currently playing track.
- Spotify API integration via Spotipy.
- Dark-themed dashboard inspired by Spotify’s aesthetic.

## Setup
1. Clone the repo: `git clone https://github.com/your-username/SpotifyWrappedRemix.git`
2. Create a virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
venv\Scripts\Activate.ps1
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file in the project root with your Spotify API credentials:
   ```
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   REDIRECT_URI = 'http://127.0.0.1:8000/callback' /
   ```
6. **Development**: Run `python app.py` and open `http://127.0.0.1:8000/`
7. **Production**: Run `python app_production_working_base.py` and open `http://127.0.0.1:8080/`

## 🚀 Production Deployment

For production deployment, use `app_production_working_base.py` which provides:
- Single-process architecture (no separate callback server needed)
- Production-ready OAuth handling
- Suitable for deployment on Railway, Render, Heroku, etc.

See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for detailed deployment instructions.

## Tech Stack
- **Dash**: Interactive web dashboard
- **Plotly**: Dynamic visualizations
- **Spotipy**: Spotify API access
- **pandas**: Data processing
- **python-dotenv**: Environment variable management

## Future Plans
- Add dropdowns for time ranges (e.g., last month, 6 months, all time).
- Include genre analysis and top artists.
- Embed animated visualizations with Manim.

## License
MIT License