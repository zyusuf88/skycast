async function fetchWeather() {
    const city = getQueryParam('city');
    if (!city) {
        document.body.innerHTML = "<h2>City not found.</h2>";
        return;
    }

    document.getElementById('city-name').textContent = `Weather in ${city}`;

    try {
        const response = await fetch(`/weather?city=${city}`);
        const data = await response.json();

        if (data.error) {
            document.body.innerHTML = `<h2>Error: ${data.error}</h2>`;
            return;
        }

        // Display weather details
        document.getElementById('temperature').textContent = `Temperature: ${data.temp}°F`;
        document.getElementById('humidity').textContent = `Humidity: ${data.humidity}%`;
        document.getElementById('description').textContent = `Conditions: ${data.description}`;

        // Select correct weather icon based on description
        let iconUrl;
        const description = data.description.toLowerCase();

        if (description.includes("cloud")) {
            iconUrl = "images/cloudy.jpg";  // Updated to match your file extension
        } else if (description.includes("clear")) {
            iconUrl = "images/clear.png";
        } else if (description.includes("rain")) {
            iconUrl = "images/rain.png";
        } else {
            iconUrl = "images/default.png";  // Use default for unknown weather
        }

        document.getElementById('weather-icon').src = iconUrl;

    } catch (error) {
        console.error("Error fetching weather:", error);
        document.getElementById('weather-icon').src = "images/default.png"; // Fallback
    }
}

// Function to get query parameters
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

// Navigate back to home page
function goBack() {
    window.location.href = '/';
}

window.onload = fetchWeather;
