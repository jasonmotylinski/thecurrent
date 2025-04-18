const { createApp, ref, onMounted, watch } = Vue

// Constants
const API_BASE_URL = '/api';
const PLOTLY_CONFIG = {
    displayModeBar: false,
    showLink: false,
    modeBarButtonsToRemove: ['toImage']
};

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

const DAYS_OF_WEEK = [
    'Sunday', 'Monday', 'Tuesday', 'Wednesday',
    'Thursday', 'Friday', 'Saturday'
];

// Utility Functions
const formatDate = (date) => date.toISOString().split('T')[0];
const getCurrentDayAndHour = () => {
    const now = new Date();
    return {
        dayOfWeek: now.toLocaleDateString('en-US', { weekday: 'long' }),
        hour: now.getHours(),
        hourLabel: now.toLocaleTimeString('en-US', { hour: 'numeric', hour12: true })
    };
};

createApp({
    setup() {
        // Reactive state
        const content = ref('Loading...');
        const lastUpdated = ref('Loading...');
        const currentStation = ref('kcmp');
        const popularSongs = ref([]);
        const popularDayHour = ref([]);
        const popularAllTime = ref([]);
        const dayOfWeek = ref('');
        const hourLabel = ref('');
        const stationTitle = ref('');

        // Station data
        const stations = ref(STATIONS);

        // API Functions
        const fetchData = async (endpoint) => {
            try {
                const response = await fetch(`${API_BASE_URL}/${endpoint}`);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                return await response.json();
            } catch (error) {
                console.error(`Error fetching ${endpoint}:`, error);
                throw error;
            }
        };

        const fetchStationData = async (stationId, endpoint) => {
            return fetchData(`${stationId}/${endpoint}`);
        };

        // Data loading functions
        const updateStationTitle = async (stationId) => {
            try {
                const data = await fetchData(stationId);
                stationTitle.value = data.title;
                document.title = `${stationTitle.value}`;
            } catch (error) {
                console.error('Error updating station title:', error);
            }
        };

        const updateLastUpdated = async () => {
            try {
                const data = await fetchData('last_updated');
                const date = new Date(data.last_updated);
                lastUpdated.value = formatDate(date);
            } catch (error) {
                console.error('Error fetching last updated date:', error);
            }
        };

        const createPopularSongs = async (stationId) => {
            try {
                const data = await fetchStationData(stationId, 'popular/last_week/artist_title');
                popularSongs.value = data;
                popularSongs.value.forEach(song => createGraph(song, stationId));
            } catch (error) {
                console.error('Error loading popular songs:', error);
                popularSongs.value = [];
            }
        };

        const createPopularAllTime = async (stationId) => {
            try {
                const data = await fetchStationData(stationId, 'popular/all_time/artist');
                popularAllTime.value = data;
            } catch (error) {
                console.error('Error loading popular all time data:', error);
                popularAllTime.value = [];
            }
        };

        // Graph Creation Functions
        const createGraph = async (song, stationId) => {
            try {
                const endDate = new Date();
                const startDate = new Date();
                startDate.setDate(startDate.getDate() - 7);
                
                const timeseriesData = await fetchStationData(
                    stationId,
                    `title_timeseries?artist=${encodeURIComponent(song.artist)}&title=${encodeURIComponent(song.title)}&start_date=${formatDate(startDate)}&end_date=${formatDate(endDate)}`
                );
                
                const graphId = `graph-${song.artist}-${song.title}`;
                const trace = {
                    x: timeseriesData.map(d => d.yw),
                    y: timeseriesData.map(d => d.ct),
                    type: 'scatter',
                    mode: 'lines',
                    line: { color: '#007bff', width: 2 }
                };
                
                const layout = {
                    margin: { l: 0, r: 0, t: 0, b: 0 },
                    ...PLOTLY_CONFIG,
                    height: 20,
                    showlegend: false,
                    xaxis: {
                        showgrid: false,
                        showticklabels: false,
                        fixedrange: true,
                        zeroline: false
                    },
                    yaxis: {
                        showgrid: false,
                        showticklabels: false,
                        fixedrange: true,
                        zeroline: false
                    }
                };
                
                Plotly.newPlot(graphId, [trace], layout, { displaylogo: false });
            } catch (error) {
                console.error('Error creating graph:', error);
            }
        };

        const createArtistTreemap = async (stationId) => {
            try {
                const data = await fetchStationData(stationId, 'popular/last_week/artist');
                
                const artistMap = new Map();
                data.forEach(item => {
                    if (!artistMap.has(item.artist)) {
                        artistMap.set(item.artist, {
                            plays: item.ct,
                            songs: []
                        });
                    } else {
                        artistMap.get(item.artist).plays += item.ct;
                    }
                    artistMap.get(item.artist).songs.push({
                        title: item.title,
                        plays: item.ct
                    });
                });
                
                const labels = ["All"];
                const parents = [""];
                const values = [Array.from(artistMap.values()).reduce((sum, artist) => sum + artist.plays, 0)];
                
                artistMap.forEach((artistData, artist) => {
                    labels.push(artist);
                    parents.push("All");
                    values.push(artistData.plays);
                    
                    artistData.songs.forEach(song => {
                        labels.push(song.title);
                        parents.push(artist);
                        values.push(song.plays);
                    });
                });

                const trace = [{
                    type: "treemap",
                    labels,
                    parents,
                    values,
                    branchvalues: "total",
                    textinfo: "label",
                    hovertemplate: "%{label}<br>Total Plays: %{value}<extra></extra>",
                    maxdepth: 2,
                    root: { color: "lightgrey" }
                }];

                const layout = {
                    margin: { l: 0, r: 0, t: 0, b: 0 },
                    showlegend: false,
                    ...PLOTLY_CONFIG,
                    colorway: TREEMAP_COLORWAY
                };

                Plotly.newPlot('popular-artists-last-week', trace, layout, { displaylogo: false });
            } catch (error) {
                console.error('Error creating artist treemap:', error);
            }
        };

        const createNewLast90DaysGraph = async (stationId) => {
            try {
                const data = await fetchStationData(stationId, 'new/last_90_days');
                
                const getHourlyCountByDay = (dayData, dayOfWeek) => {
                    return Array(24).fill(0).map((_, hour) => {
                        const hourData = dayData.find(d => d.day_of_week === dayOfWeek && d.hour === hour);
                        return hourData ? hourData.ct : 0;
                    });
                };
                
                const dayCounts = [
                    getHourlyCountByDay(data, "Sunday"),
                    getHourlyCountByDay(data, "Monday"),
                    getHourlyCountByDay(data, "Tuesday"),
                    getHourlyCountByDay(data, "Wednesday"),
                    getHourlyCountByDay(data, "Thursday"),
                    getHourlyCountByDay(data, "Friday"),
                    getHourlyCountByDay(data, "Saturday")
                ];
                
                const hours = Array.from({length: 24}, (_, i) => i.toString().padStart(2, '0'));
                const days = DAYS_OF_WEEK;
                
                const trace = {
                    z: dayCounts,
                    x: hours,
                    y: days,
                    type: 'heatmap',
                    colorscale: HEATMAP_COLORSCALE,
                    showscale: false,
                    hoverongaps: false,
                    hovertemplate: 'Day: %{y}<br>Hour: %{x}<br>Plays: %{z}<extra></extra>',
                    xgap: 1,
                    ygap: 1
                };
                
                const layout = {
                    margin: { l: 80, r: 0, t: 0, b: 40 },
                    height: 200,
                    ...PLOTLY_CONFIG,
                    xaxis: {
                        title: 'Hour',
                        showgrid: true,
                        showline: true,
                        showticklabels: true,
                        tickmode: 'array',
                        tickvals: ['00', '06', '12', '18', '23'],
                        ticktext: ['12 AM', '6 AM', '12 PM', '6 PM', '11 PM'],
                        zeroline: false,
                        fixedrange: true
                    },
                    yaxis: {
                        title: 'Day',
                        showgrid: true,
                        showline: true,
                        showticklabels: true,
                        autorange: 'reversed',
                        zeroline: false,
                        fixedrange: true
                    }
                };
                
                Plotly.newPlot('popular-songs-last-90-days', [trace], layout, { displaylogo: false });
            } catch (error) {
                console.error('Error creating last 90 days graph:', error);
            }
        };

        const createPopularDayHourGraph = async (stationId) => {
            try {
                const { dayOfWeek: newDayOfWeek, hour, hourLabel: newHourLabel } = getCurrentDayAndHour();
                
                const data = await fetchStationData(
                    stationId,
                    `popular/all_time/${newDayOfWeek}/${hour}`
                );
                
                dayOfWeek.value = newDayOfWeek;
                hourLabel.value = newHourLabel;
                popularDayHour.value = data;
            } catch (error) {
                console.error('Error creating popular day hour graph:', error);
                popularDayHour.value = [];
            }
        };

        const createPopularAllTimeGraph = async (stationId) => {
            try {
                const data = await fetchStationData(stationId, 'popular/all_time/artist_timeseries');
                
                const artistData = {};
                data.forEach(item => {
                    if (!artistData[item.artist]) {
                        artistData[item.artist] = {
                            x: [],
                            y: []
                        };
                    }
                    artistData[item.artist].x.push(item.year_month);
                    artistData[item.artist].y.push(item.ct);
                });
                
                const traces = Object.entries(artistData).map(([artist, data]) => ({
                    x: data.x,
                    y: data.y,
                    type: 'scatter',
                    mode: 'lines',
                    name: artist
                }));
                
                const layout = {
                    margin: { l: 0, r: 0, t: 0, b: 0 },
                    showlegend: true,
                    height: 300,
                    ...PLOTLY_CONFIG,
                    xaxis: { fixedrange: true },
                    yaxis: { fixedrange: true },
                    legend: {
                        orientation: 'h',
                        y: -0.2,
                        x: 0.5,
                        xanchor: 'center'
                    }
                };
                
                Plotly.newPlot('popular-all-time-graph', traces, layout, { displaylogo: false });
            } catch (error) {
                console.error('Error creating popular all time graph:', error);
            }
        };

        // Station change handler
        const setCurrentStation = async (station) => {
            currentStation.value = station;
            await Promise.all([
                updateStationTitle(station),
                createPopularSongs(station),
                createArtistTreemap(station),
                createNewLast90DaysGraph(station),
                createPopularAllTime(station),
                createPopularAllTimeGraph(station),
                createPopularDayHourGraph(station),
                updateLastUpdated()
            ]);
        };

        // Watchers
        watch(currentStation, () => {
            setCurrentStation(currentStation.value);
        });

        // Lifecycle hooks
        onMounted(async () => {
            await Promise.all([
                setCurrentStation(currentStation.value)
            ]);
        });

        return {
            content,
            lastUpdated,
            currentStation,
            stations,
            popularSongs,
            popularDayHour,
            popularAllTime,
            dayOfWeek,
            hourLabel,
            stationTitle,
            setCurrentStation
        };
    }
}).mount('#app') 