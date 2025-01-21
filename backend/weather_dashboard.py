from flask import Flask, request, jsonify, send_from_directory
import os
import requests
import boto3
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../src')

API_KEY = os.getenv('OPENWEATHER_API_KEY')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

@app.route('/')
def home():
    return send_from_directory('../src', 'index.html')

@app.route('/city')
def city_page():
    return send_from_directory('../src', 'city.html')

@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City is required'}), 400

    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "imperial"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        weather_data = response.json()

        formatted_data = {
            'city': city,
            'temp': weather_data['main']['temp'],
            'feels_like': weather_data['main']['feels_like'],
            'humidity': weather_data['main']['humidity'],
            'description': weather_data['weather'][0]['description'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Save to S3
        save_to_s3(formatted_data, city)

        return jsonify(formatted_data)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Failed to fetch weather data', 'details': str(e)}), 500

def save_to_s3(weather_data, city):
    """Save weather data to AWS S3 bucket."""
    file_name = f"weather-data/{city}-{weather_data['timestamp'].replace(' ', '_')}.json"
    
    try:
        s3_client.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=file_name,
            Body=str(weather_data),
            ContentType='application/json'
        )
        print(f"Successfully saved weather data for {city} to S3")
    except Exception as e:
        print(f"Error saving to S3: {e}")

# Serve static files (CSS, JS, Images)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../src', filename)

if __name__ == '__main__':
    app.run(debug=True)
