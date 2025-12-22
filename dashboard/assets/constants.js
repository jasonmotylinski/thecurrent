// API and Plotly Configuration
const API_BASE_URL = '/api';
const PLOTLY_CONFIG = {
    displayModeBar: false,
    showLink: false,
    modeBarButtonsToRemove: ['toImage']
};

// Station Configuration
const STATIONS = [
    { id: 'kcmp', name: 'KCMP', logo: '/assets/kcmp.svg', style: 'button-style' },
    { id: 'kcrw', name: 'KCRW', logo: '/assets/KCRW_Logo_White.png', style: 'button-style' },
    { id: 'kexp', name: 'KEXP', logo: '/assets/kexp.svg', style: 'button-style' },
    { id: 'kutx', name: 'KUTX', logo: '/assets/kutx.svg', style: 'button-style' },
    { id: 'wfuv', name: 'WFUV', logo: '/assets/wfuv.png', style: 'button-style-wfuv' },
    { id: 'wxpn', name: 'WXPN', logo: '/assets/wxpn.png', style: 'button-style' },
    { id: 'kuom', name: 'KUOM', logo: '/assets/radiok.svg', style: 'button-style' },
    { id: 'kkxt', name: 'KKXT', logo: '/assets/kxt.png', style: 'button-style' },
    { id: 'wehm', name: 'WEHM', logo: '/assets/wehm.png', style: 'button-style' },
    { id: 'wnxp', name: 'WNXP', logo: '/assets/wnxp.png', style: 'button-style' },
    { id: 'wyep', name: 'WYEP', logo: '/assets/wyep.png', style: 'button-style' }
];

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
