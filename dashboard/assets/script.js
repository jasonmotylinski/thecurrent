const { createApp, ref, onMounted, watch, nextTick } = Vue

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
        const stationDisplayName = ref('');

        // Phase 1 Analytics state
        const stationExclusives = ref([]);
        const deepCuts = ref([]);
        const genreByHour = ref([]);

        // Search state
        const searchQuery = ref('');
        const searchResults = ref([]);
        const showSearchResults = ref(false);
        const searchLoading = ref(false);
        let searchDebounceTimer = null;

        // Analytics state
        const analyticsView = ref(false);
        const analyticsType = ref('');
        const analyticsTitle = ref('');
        const analyticsArtist = ref('');
        const analyticsTopSongs = ref([]);
        const analyticsLoading = ref(false);

        // Page loading state (for full-page loading overlay)
        const pageLoading = ref(false);

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

        const updateStationDisplayName = async (stationId) => {
            try {
                const data = await fetchData(stationId);
                stationDisplayName.value = data.display_name;
            } catch (error) {
                console.error('Error updating station display name:', error);
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
                // Fetch songs and timeseries in parallel (reduces 11 API calls to 2)
                const [songsData, timeseriesData] = await Promise.all([
                    fetchStationData(stationId, 'popular/last_week/artist_title'),
                    fetchStationData(stationId, 'popular/last_week/artist_title_timeseries')
                ]);

                popularSongs.value = songsData;
                await nextTick();

                // Group timeseries data by song
                const timeseriesBySong = {};
                timeseriesData.forEach(item => {
                    const key = `${item.artist}|||${item.title}`;
                    if (!timeseriesBySong[key]) timeseriesBySong[key] = [];
                    timeseriesBySong[key].push(item);
                });

                // Create all graphs in parallel using pre-fetched data
                await Promise.all(popularSongs.value.map(song =>
                    createGraphFromData(song, timeseriesBySong[`${song.artist}|||${song.title}`] || [])
                ));
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
        const createGraphFromData = async (song, timeseriesData) => {
            try {
                const graphId = `graph-${song.artist.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase()}-${song.title.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase()}`;
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

        // Search functions
        const onSearchInput = () => {
            if (searchDebounceTimer) {
                clearTimeout(searchDebounceTimer);
            }

            if (searchQuery.value.length < 2) {
                searchResults.value = [];
                showSearchResults.value = false;
                searchLoading.value = false;
                return;
            }

            searchLoading.value = true;
            showSearchResults.value = true;

            searchDebounceTimer = setTimeout(async () => {
                try {
                    const response = await fetch(
                        `${API_BASE_URL}/search?q=${encodeURIComponent(searchQuery.value)}`
                    );
                    if (response.ok) {
                        const data = await response.json();
                        searchResults.value = data;
                    } else {
                        searchResults.value = [];
                    }
                } catch (error) {
                    console.error('Search error:', error);
                    searchResults.value = [];
                } finally {
                    searchLoading.value = false;
                }
            }, 300);
        };

        const hideSearchResultsDelayed = () => {
            setTimeout(() => {
                showSearchResults.value = false;
            }, 200);
        };

        const selectSearchResult = (result) => {
            searchQuery.value = '';
            searchResults.value = [];
            showSearchResults.value = false;
            // Show loading overlay immediately
            pageLoading.value = true;
            // Update URL and load analytics
            window.location.hash = `/artist/${encodeURIComponent(result.artist)}`;
        };

        // Analytics functions
        const loadArtistAnalytics = (artist) => {
            // Show loading overlay immediately
            pageLoading.value = true;
            // Update URL - hashchange handler will load the data
            window.location.hash = `/artist/${encodeURIComponent(artist)}`;
        };

        const loadSongAnalytics = async (artist, title, updateUrl = true) => {
            try {
                // Update URL if requested
                if (updateUrl) {
                    // Show loading overlay immediately
                    pageLoading.value = true;
                    window.location.hash = `/song/${encodeURIComponent(artist)}/${encodeURIComponent(title)}`;
                    return; // hashchange handler will call this function again with updateUrl=false
                }

                analyticsLoading.value = true;
                const response = await fetch(
                    `${API_BASE_URL}/song/analytics?artist=${encodeURIComponent(artist)}&title=${encodeURIComponent(title)}`
                );
                if (!response.ok) throw new Error('Failed to fetch song analytics');

                analyticsView.value = true;
                analyticsType.value = 'song';
                analyticsTitle.value = `${artist} - ${title}`;
                analyticsArtist.value = artist;
                analyticsTopSongs.value = [];
                const data = await response.json();

                // Set analyticsLoading to false before nextTick so chart divs are rendered
                analyticsLoading.value = false;
                await nextTick();

                createAnalyticsTimeseries(data.analytics);
            } catch (error) {
                console.error('Error loading song analytics:', error);
            } finally {
                pageLoading.value = false;
            }
        };

        const createAnalyticsTimeseries = (analytics) => {
            const stationData = {};

            analytics.forEach(item => {
                const stationName = item.station_name || 'Unknown';
                if (!stationData[stationName]) {
                    stationData[stationName] = { x: [], y: [] };
                }
                stationData[stationName].x.push(item.month);
                stationData[stationName].y.push(item.plays);
            });

            const traces = Object.entries(stationData).map(([station, data]) => ({
                x: data.x,
                y: data.y,
                type: 'scatter',
                mode: 'lines',
                name: station
            }));

            const layout = {
                margin: { l: 50, r: 20, t: 20, b: 50 },
                height: 350,
                showlegend: true,
                legend: {
                    orientation: 'h',
                    y: -0.2,
                    x: 0.5,
                    xanchor: 'center'
                },
                xaxis: {
                    title: 'Month',
                    fixedrange: true
                },
                yaxis: {
                    title: 'Plays',
                    fixedrange: true
                }
            };

            Plotly.newPlot('analytics-timeseries', traces, layout, PLOTLY_CONFIG);
        };

        const createTopSongsTimeseries = (data) => {
            // Get all unique months and songs
            const monthsSet = new Set();
            const songsSet = new Set();

            data.forEach(item => {
                // Format month as YYYY-MM for grouping
                const monthStr = item.month.substring(0, 7);
                monthsSet.add(monthStr);
                songsSet.add(item.title);
            });

            const months = Array.from(monthsSet).sort();
            const songs = Array.from(songsSet);

            // Aggregate plays by song and month (sum across all stations)
            const songMonthPlays = {};
            songs.forEach(song => {
                songMonthPlays[song] = {};
                months.forEach(month => {
                    songMonthPlays[song][month] = 0;
                });
            });

            data.forEach(item => {
                const monthStr = item.month.substring(0, 7);
                songMonthPlays[item.title][monthStr] += item.plays;
            });

            // Create traces - one per song (stacked)
            const traces = songs.map(song => ({
                x: months,
                y: months.map(month => songMonthPlays[song][month]),
                type: 'bar',
                name: song
            }));

            const layout = {
                margin: { l: 50, r: 20, t: 20, b: 80 },
                height: 400,
                barmode: 'stack',
                showlegend: true,
                legend: {
                    orientation: 'h',
                    y: -0.25,
                    x: 0.5,
                    xanchor: 'center'
                },
                xaxis: {
                    title: 'Month',
                    fixedrange: true,
                    tickangle: -45
                },
                yaxis: {
                    title: 'Plays',
                    fixedrange: true
                }
            };

            Plotly.newPlot('top-songs-timeseries', traces, layout, PLOTLY_CONFIG);
        };

        const closeAnalytics = async () => {
            analyticsView.value = false;
            analyticsType.value = '';
            analyticsTitle.value = '';
            analyticsArtist.value = '';
            analyticsTopSongs.value = [];
            // Clear URL hash
            history.pushState(null, '', window.location.pathname);
            // Reload dashboard data to repopulate charts (with loading screen)
            await setCurrentStation(currentStation.value);
        };

        // Phase 1 Analytics Functions
        const loadStationExclusives = async (stationId) => {
            try {
                const data = await fetchStationData(stationId, 'exclusives');
                stationExclusives.value = data.slice(0, 20); // Show top 20
            } catch (error) {
                console.error('Error loading station exclusives:', error);
                stationExclusives.value = [];
            }
        };

        const loadDeepCuts = async () => {
            try {
                const data = await fetchData('deep-cuts');
                deepCuts.value = data.slice(0, 20); // Show top 20
            } catch (error) {
                console.error('Error loading deep cuts:', error);
                deepCuts.value = [];
            }
        };

        const createGenreByHourHeatmap = async () => {
            try {
                const data = await fetchData('genres/by-hour');

                // Group data by genre and hour
                const genreMap = {};
                data.forEach(item => {
                    if (!genreMap[item.genre]) {
                        genreMap[item.genre] = Array(24).fill(0);
                    }
                    genreMap[item.genre][item.hour] = item.plays;
                });

                // Sort genres by total plays
                const genres = Object.keys(genreMap).sort((a, b) => {
                    const sumA = genreMap[a].reduce((sum, val) => sum + val, 0);
                    const sumB = genreMap[b].reduce((sum, val) => sum + val, 0);
                    return sumB - sumA;
                }).slice(0, 15); // Top 15 genres

                const hours = Array.from({length: 24}, (_, i) => i.toString());
                const zData = genres.map(genre => genreMap[genre]);

                const trace = {
                    z: zData,
                    x: hours,
                    y: genres,
                    type: 'heatmap',
                    colorscale: HEATMAP_COLORSCALE,
                    hovertemplate: 'Genre: %{y}<br>Hour: %{x}:00<br>Plays: %{z}<extra></extra>'
                };

                const layout = {
                    margin: { l: 120, r: 0, t: 0, b: 50 },
                    height: 500,
                    xaxis: {
                        title: 'Hour of Day',
                        fixedrange: true
                    },
                    yaxis: {
                        fixedrange: true
                    }
                };

                Plotly.newPlot('genre-by-hour-heatmap', [trace], layout, { displaylogo: false });
            } catch (error) {
                console.error('Error creating genre by hour heatmap:', error);
            }
        };

        // Station change handler
        const setCurrentStation = async (station, showLoading = true) => {
            if (showLoading) {
                pageLoading.value = true;
            }
            try {
                currentStation.value = station;
                await Promise.all([
                    updateStationTitle(station),
                    updateStationDisplayName(station),
                    createPopularSongs(station),
                    createArtistTreemap(station),
                    createNewLast90DaysGraph(station),
                    createPopularAllTime(station),
                    createPopularAllTimeGraph(station),
                    createPopularDayHourGraph(station),
                    loadStationExclusives(station),
                    loadDeepCuts(),
                    createGenreByHourHeatmap(),
                    updateLastUpdated()
                ]);
            } finally {
                if (showLoading) {
                    pageLoading.value = false;
                }
            }
        };

        // Watchers
        watch(currentStation, () => {
            setCurrentStation(currentStation.value, false);
        });

        // URL routing
        const handleRoute = async () => {
            const hash = window.location.hash;

            if (hash.startsWith('#/artist/')) {
                // Show loading overlay for direct URL navigation
                pageLoading.value = true;
                const artist = decodeURIComponent(hash.replace('#/artist/', ''));
                await loadArtistAnalyticsFromUrl(artist);
            } else if (hash.startsWith('#/song/')) {
                // Show loading overlay for direct URL navigation
                pageLoading.value = true;
                const parts = hash.replace('#/song/', '').split('/');
                if (parts.length >= 2) {
                    const artist = decodeURIComponent(parts[0]);
                    const title = decodeURIComponent(parts.slice(1).join('/'));
                    await loadSongAnalytics(artist, title, false);
                }
            } else {
                // No hash or unrecognized - show dashboard
                if (analyticsView.value) {
                    analyticsView.value = false;
                    analyticsType.value = '';
                    analyticsTitle.value = '';
                    analyticsArtist.value = '';
                    analyticsTopSongs.value = [];
                }
            }
        };

        // Load artist analytics from URL (doesn't update URL again)
        const loadArtistAnalyticsFromUrl = async (artist) => {
            try {
                analyticsLoading.value = true;
                const response = await fetch(
                    `${API_BASE_URL}/artist/${encodeURIComponent(artist)}/analytics`
                );
                if (!response.ok) throw new Error('Failed to fetch artist analytics');

                analyticsView.value = true;
                analyticsType.value = 'artist';
                analyticsTitle.value = artist;
                analyticsArtist.value = artist;

                const data = await response.json();
                analyticsTopSongs.value = data.top_songs || [];

                // Set analyticsLoading to false before nextTick so chart divs are rendered
                analyticsLoading.value = false;
                await nextTick();

                createAnalyticsTimeseries(data.analytics);
                if (data.top_songs_timeseries) {
                    createTopSongsTimeseries(data.top_songs_timeseries);
                }
            } catch (error) {
                console.error('Error loading artist analytics:', error);
            } finally {
                pageLoading.value = false;
            }
        };

        // Lifecycle hooks
        onMounted(async () => {
            // Listen for hash changes (browser back/forward)
            window.addEventListener('hashchange', handleRoute);

            // Load initial station data
            await setCurrentStation(currentStation.value);

            // Handle initial URL
            await handleRoute();
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
            stationDisplayName,
            setCurrentStation,
            // Phase 1 Analytics
            stationExclusives,
            deepCuts,
            genreByHour,
            // Search
            searchQuery,
            searchResults,
            showSearchResults,
            searchLoading,
            onSearchInput,
            hideSearchResultsDelayed,
            selectSearchResult,
            // Analytics
            analyticsView,
            analyticsType,
            analyticsTitle,
            analyticsArtist,
            analyticsTopSongs,
            analyticsLoading,
            loadArtistAnalytics,
            loadSongAnalytics,
            closeAnalytics,
            // Page loading
            pageLoading
        };
    }
}).mount('#app')