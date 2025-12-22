// Date/Time Utility Functions
const formatDate = (date) => date.toISOString().split('T')[0];

const getCurrentDayAndHour = () => {
    const now = new Date();
    return {
        dayOfWeek: now.toLocaleDateString('en-US', { weekday: 'long' }),
        hour: now.getHours(),
        hourLabel: now.toLocaleTimeString('en-US', { hour: 'numeric', hour12: true })
    };
};

// API Utility Functions
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
