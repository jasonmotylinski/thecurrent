// API and Plotly Configuration
const API_BASE_URL = '/api';
const PLOTLY_CONFIG = {
    displayModeBar: false,
    showLink: false,
    modeBarButtonsToRemove: ['toImage']
};

// Station Configuration (loaded from API)
let STATIONS = [];

// Fetch stations from config.py via API
async function loadStations() {
    try {
        const response = await fetch(`${API_BASE_URL}/stations`);
        if (!response.ok) {
            throw new Error(`Failed to load stations: ${response.statusText}`);
        }
        STATIONS = await response.json();
        return STATIONS;
    } catch (error) {
        console.error('Error loading stations:', error);
        // Fallback to empty array - app will handle gracefully
        STATIONS = [];
        return STATIONS;
    }
}

// Store the promise so other scripts can wait for it
const stationsLoaded = loadStations();

// Chart Color Schemes
const TREEMAP_COLORWAY = [
    "#67001f", "#b2182b", "#d6604d", "#f4a582", "#fddbc7",
    "#d1e5f0", "#92c5de", "#4393c3", "#2166ac", "#053061"
];

const HEATMAP_COLORSCALE = [
    [0, 'rgb(253, 253, 204)'],
    [0.1, 'rgb(201, 235, 177)'],
    [0.2, 'rgb(145, 216, 163)'],
    [0.3, 'rgb(102, 194, 163)'],
    [0.4, 'rgb(81, 168, 162)'],
    [0.5, 'rgb(72, 141, 157)'],
    [0.6, 'rgb(64, 117, 152)'],
    [0.7, 'rgb(61, 90, 146)'],
    [0.8, 'rgb(65, 64, 123)'],
    [1.0, 'rgb(37, 52, 81)']
];

// Time Constants
const DAYS_OF_WEEK = [
    'Sunday', 'Monday', 'Tuesday', 'Wednesday',
    'Thursday', 'Friday', 'Saturday'
];
