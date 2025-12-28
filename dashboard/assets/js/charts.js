// Plotly Chart Creation Functions
// Dependencies: constants.js (PLOTLY_CONFIG, TREEMAP_COLORWAY, HEATMAP_COLORSCALE, DAYS_OF_WEEK)

// Sparkline graph for popular songs table
const createSparklineGraph = (graphId, timeseriesData) => {
    try {
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
        console.error('Error creating sparkline graph:', error);
    }
};

// Artist treemap for popular artists
const createTreemap = (elementId, data) => {
    try {
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

        Plotly.newPlot(elementId, trace, layout, { displaylogo: false });
    } catch (error) {
        console.error('Error creating treemap:', error);
    }
};

// Heatmap for new music by day/hour
const createDayHourHeatmap = (elementId, data) => {
    try {
        const getHourlyCountByDay = (dayData, dayOfWeek) => {
            return Array(24).fill(0).map((_, hour) => {
                const hourData = dayData.find(d => d.day_of_week === dayOfWeek && d.hour === hour);
                return hourData ? hourData.ct : 0;
            });
        };

        const dayCounts = DAYS_OF_WEEK.map(day => getHourlyCountByDay(data, day));
        const hours = Array.from({length: 24}, (_, i) => i.toString().padStart(2, '0'));

        const trace = {
            z: dayCounts,
            x: hours,
            y: DAYS_OF_WEEK,
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

        Plotly.newPlot(elementId, [trace], layout, { displaylogo: false });
    } catch (error) {
        console.error('Error creating day/hour heatmap:', error);
    }
};

// Line chart for all-time popular artists
const createAllTimeLineChart = (elementId, data) => {
    try {
        const artistData = {};
        data.forEach(item => {
            if (!artistData[item.artist]) {
                artistData[item.artist] = { x: [], y: [] };
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

        Plotly.newPlot(elementId, traces, layout, { displaylogo: false });
    } catch (error) {
        console.error('Error creating all-time line chart:', error);
    }
};

// Multi-station timeseries for analytics view
const createAnalyticsTimeseries = (elementId, analytics) => {
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

    Plotly.newPlot(elementId, traces, layout, PLOTLY_CONFIG);
};

// Stacked bar chart for top songs timeseries
const createTopSongsTimeseries = (elementId, data) => {
    // Get all unique months and songs
    const monthsSet = new Set();
    const songsSet = new Set();

    data.forEach(item => {
        const monthStr = item.month.substring(0, 7);
        monthsSet.add(monthStr);
        songsSet.add(item.title);
    });

    const months = Array.from(monthsSet).sort();
    const songs = Array.from(songsSet);

    // Aggregate plays by song and month
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

    Plotly.newPlot(elementId, traces, layout, PLOTLY_CONFIG);
};

// Genre by hour heatmap
const createGenreByHourHeatmap = (elementId, data) => {
    try {
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
        }).slice(0, 15);

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
            },
            shapes: []
        };

        Plotly.newPlot(elementId, [trace], layout, { displaylogo: false });

        // Add column highlight on hover
        const plotElement = document.getElementById(elementId);
        plotElement.on('plotly_hover', (eventData) => {
            const hourIndex = parseInt(eventData.points[0].x);
            Plotly.relayout(elementId, {
                shapes: [{
                    type: 'rect',
                    x0: hourIndex - 0.5,
                    x1: hourIndex + 0.5,
                    y0: -0.5,
                    y1: genres.length - 0.5,
                    fillcolor: 'rgba(255, 255, 255, 0.15)',
                    line: { color: 'rgba(255, 255, 255, 0.5)', width: 2 }
                }]
            });
        });

        plotElement.on('plotly_unhover', () => {
            Plotly.relayout(elementId, { shapes: [] });
        });
    } catch (error) {
        console.error('Error creating genre by hour heatmap:', error);
    }
};
