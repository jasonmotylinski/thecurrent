// Main Vue Application
// Dependencies: constants.js, utils.js, charts.js (must be loaded first)

const { createApp, ref, onMounted, watch, nextTick } = Vue

const app = createApp({
    // Use custom delimiters to avoid conflict with Jinja2
    delimiters: ['${', '}'],
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
        const hiddenGems = ref([]);
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

        // View state (dashboard | analytics | top100)
        const currentView = ref('dashboard');

        // Top 100 state
        const top100Songs = ref([]);
        const top100Timeseries = ref([]);

        // Popular songs timeseries state
        const popularSongsTimeseries = ref([]);

        // Page loading state (for full-page loading overlay)
        const pageLoading = ref(false);

        // Menu state
        const menuOpen = ref(false);

        // Station data
        const stations = ref(STATIONS);

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
                popularSongsTimeseries.value = timeseriesData;
                await nextTick();

                // Group timeseries data by song
                const timeseriesBySong = {};
                timeseriesData.forEach(item => {
                    const key = `${item.artist}|||${item.title}`;
                    if (!timeseriesBySong[key]) timeseriesBySong[key] = [];
                    timeseriesBySong[key].push(item);
                });

                // Create all graphs in parallel using pre-fetched data
                await Promise.all(popularSongs.value.map(song => {
                    const graphId = `graph-${song.artist.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase()}-${song.title.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase()}`;
                    const songTimeseries = timeseriesBySong[`${song.artist}|||${song.title}`] || [];
                    createSparklineGraph(graphId, songTimeseries);
                }));
            } catch (error) {
                console.error('Error loading popular songs:', error);
                popularSongs.value = [];
                popularSongsTimeseries.value = [];
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

        const createArtistTreemap = async (stationId) => {
            try {
                const data = await fetchStationData(stationId, 'popular/last_week/artist');
                createTreemap('popular-artists-last-week', data);
            } catch (error) {
                console.error('Error creating artist treemap:', error);
            }
        };

        const createNewLast90DaysGraph = async (stationId) => {
            try {
                const data = await fetchStationData(stationId, 'new/last_90_days');
                createDayHourHeatmap('popular-songs-last-90-days', data);
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
                createAllTimeLineChart('popular-all-time-graph', data);
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

                createAnalyticsTimeseries('analytics-timeseries', data.analytics);
            } catch (error) {
                console.error('Error loading song analytics:', error);
            } finally {
                pageLoading.value = false;
            }
        };

        const closeAnalytics = async () => {
            currentView.value = 'dashboard';
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

        const loadTop100View = async (stationId) => {
            try {
                pageLoading.value = true;
                currentView.value = 'top100';
                analyticsView.value = false;

                // Fetch both in parallel
                const [songsData, timeseriesData] = await Promise.all([
                    fetchStationData(stationId, 'top-100/current-year'),
                    fetchStationData(stationId, 'top-100/current-year/timeseries')
                ]);

                top100Songs.value = songsData;
                top100Timeseries.value = timeseriesData;

                await nextTick();
                await renderTop100Sparklines();
            } catch (error) {
                console.error('Error loading top 100:', error);
                top100Songs.value = [];
                top100Timeseries.value = [];
            } finally {
                pageLoading.value = false;
            }
        };

        const renderTop100Sparklines = async () => {
            // Group timeseries by song
            const timeseriesBySong = {};
            top100Timeseries.value.forEach(item => {
                const key = `${item.artist}|||${item.title}`;
                if (!timeseriesBySong[key]) timeseriesBySong[key] = [];
                timeseriesBySong[key].push(item);
            });

            // Render all sparklines in parallel
            await Promise.all(top100Songs.value.map((song, index) => {
                const graphId = `top100-sparkline-${index}`;
                const songTimeseries = timeseriesBySong[`${song.artist}|||${song.title}`] || [];
                createTop100Sparkline(graphId, songTimeseries);
            }));
        };

        const calculateTrend = (timeseriesData) => {
            if (!timeseriesData || timeseriesData.length < 2) return '─';

            // Determine data type (weekly for popular songs, monthly for top100)
            const isWeekly = timeseriesData[0].yw !== undefined;

            let sorted;
            if (isWeekly) {
                // Sort by year-week
                sorted = [...timeseriesData].sort((a, b) =>
                    a.yw.localeCompare(b.yw)
                );
            } else {
                // Sort by month
                sorted = [...timeseriesData].sort((a, b) =>
                    a.month.localeCompare(b.month)
                );
            }

            // Split data in half
            const midpoint = Math.ceil(sorted.length / 2);
            const firstHalf = sorted.slice(0, midpoint);
            const secondHalf = sorted.slice(midpoint);

            // Calculate average plays for each half
            const firstHalfAvg = firstHalf.reduce((sum, item) => {
                const plays = item.ct !== undefined ? item.ct : item.plays;
                return sum + plays;
            }, 0) / firstHalf.length;

            const secondHalfAvg = secondHalf.reduce((sum, item) => {
                const plays = item.ct !== undefined ? item.ct : item.plays;
                return sum + plays;
            }, 0) / secondHalf.length;

            if (secondHalfAvg > firstHalfAvg) return '▲';
            if (secondHalfAvg < firstHalfAvg) return '▼';
            return '─';
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

        const loadHiddenGems = async (stationId) => {
            try {
                const data = await fetchStationData(stationId, 'hidden-gems');
                hiddenGems.value = data.slice(0, 20); // Show top 20
            } catch (error) {
                console.error('Error loading hidden gems:', error);
                hiddenGems.value = [];
            }
        };

        const loadGenreByHourHeatmap = async (stationId) => {
            try {
                const data = await fetchData(`genres/by-hour/${stationId}`);
                createGenreByHourHeatmap('genre-by-hour-heatmap', data);
            } catch (error) {
                console.error('Error creating genre by hour heatmap:', error);
            }
        };

        // Menu functions
        const toggleMenu = () => {
            menuOpen.value = !menuOpen.value;
        };

        const closeMenu = () => {
            menuOpen.value = false;
        };

        // Station change handler
        const setCurrentStation = async (station, showLoading = true) => {
            closeMenu(); // Auto-close menu when selecting station
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
                    loadHiddenGems(station),
                    loadGenreByHourHeatmap(station),
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
                currentView.value = 'analytics';
                await loadArtistAnalyticsFromUrl(artist);
            } else if (hash.startsWith('#/song/')) {
                // Show loading overlay for direct URL navigation
                pageLoading.value = true;
                currentView.value = 'analytics';
                const parts = hash.replace('#/song/', '').split('/');
                if (parts.length >= 2) {
                    const artist = decodeURIComponent(parts[0]);
                    const title = decodeURIComponent(parts.slice(1).join('/'));
                    await loadSongAnalytics(artist, title, false);
                }
            } else {
                // No hash or unrecognized - show dashboard
                if (currentView.value !== 'dashboard') {
                    currentView.value = 'dashboard';
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

                createAnalyticsTimeseries('analytics-timeseries', data.analytics);
                if (data.top_songs_timeseries) {
                    createTopSongsTimeseries('top-songs-timeseries', data.top_songs_timeseries);
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

            // Listen for ESC key to close menu
            window.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && menuOpen.value) {
                    closeMenu();
                }
            });

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
            popularSongsTimeseries,
            popularDayHour,
            popularAllTime,
            dayOfWeek,
            hourLabel,
            stationTitle,
            stationDisplayName,
            setCurrentStation,
            // Phase 1 Analytics
            stationExclusives,
            hiddenGems,
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
            // View state and Top 100
            currentView,
            top100Songs,
            top100Timeseries,
            loadTop100View,
            calculateTrend,
            // Page loading
            pageLoading,
            // Menu
            menuOpen,
            toggleMenu,
            closeMenu
        };
    }
})

// Wait for stations to load before mounting the app
stationsLoaded.then(() => {
    app.mount('#app');
});
