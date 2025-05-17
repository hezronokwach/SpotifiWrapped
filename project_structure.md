# SpotifiWrapped Project Structure

```
SpotifiWrapped/
├── app.py                  # Main application entry point
├── .env                    # Environment variables (API keys)
├── data/                   # Data storage directory
├── modules/
│   ├── __init__.py         # Makes modules a package
│   ├── api.py              # Spotify API interaction
│   ├── data_processing.py  # Data processing functions
│   ├── visualizations.py   # Visualization components
│   └── layout.py           # Dashboard layout components
├── assets/                 # Static assets (CSS, images)
│   └── style.css           # Custom styling
└── README.md               # Project documentation
```

## Module Responsibilities

### app.py
- Application entry point
- Initializes and runs the Dash app
- Imports and uses the other modules

### modules/api.py
- Handles all Spotify API interactions
- Authentication
- Data fetching functions

### modules/data_processing.py
- Processes raw API data
- Creates and manages dataframes
- Handles data storage and retrieval

### modules/visualizations.py
- Creates all visualization components
- Chart callbacks
- Animation integration

### modules/layout.py
- Dashboard layout components
- UI elements
- Style definitions