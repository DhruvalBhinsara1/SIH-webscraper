#!/usr/bin/env python3
"""
Weather Scraper Module
Extracts weather data for rainwater harvesting planning using WeatherAPI.com
"""

import sys
import os
import requests
import logging
import time
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ScraperConfig

logger = logging.getLogger(__name__)

class WeatherScraper:
    """Weather scraper using WeatherAPI.com"""
    
    def __init__(self):
        self.config = ScraperConfig()
        self.api_key = "25df4b3bce1c4470bcb173218250109"
        self.base_url = "http://api.weatherapi.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_all_weather_data(self) -> List[Dict[str, Any]]:
        """Scrape weather data for all major Indian cities"""
        all_weather_data = []
        
        # Comprehensive list of Indian cities for weather data
        cities = [
            # Metro cities
            'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune',
            
            # State capitals
            'Ahmedabad', 'Jaipur', 'Lucknow', 'Bhopal', 'Gandhinagar', 'Thiruvananthapuram',
            'Panaji', 'Shimla', 'Chandigarh', 'Dehradun', 'Ranchi', 'Patna', 'Raipur',
            'Bhubaneswar', 'Guwahati', 'Imphal', 'Aizawl', 'Kohima', 'Gangtok', 'Agartala',
            'Shillong', 'Itanagar', 'Dispur', 'Amaravati', 'Bengaluru', 'Panaji',
            
            # Major tier-2 cities
            'Surat', 'Kanpur', 'Nagpur', 'Indore', 'Thane', 'Visakhapatnam', 'Vadodara',
            'Faridabad', 'Ghaziabad', 'Ludhiana', 'Rajkot', 'Agra', 'Nashik', 'Kalyan',
            'Vasai-Virar', 'Varanasi', 'Srinagar', 'Aurangabad', 'Dhanbad', 'Amritsar',
            'Navi Mumbai', 'Allahabad', 'Howrah', 'Gwalior', 'Jabalpur', 'Coimbatore',
            'Vijayawada', 'Jodhpur', 'Madurai', 'Raipur', 'Kota', 'Chandigarh',
            
            # Important agricultural centers
            'Mysore', 'Tiruchirappalli', 'Salem', 'Tirunelveli', 'Erode', 'Vellore',
            'Thoothukudi', 'Dindigul', 'Thanjavur', 'Ranchi', 'Jamshedpur', 'Bokaro',
            'Durgapur', 'Siliguri', 'Asansol', 'Cuttack', 'Rourkela', 'Berhampur',
            'Sambalpur', 'Brahmapur', 'Guntur', 'Nellore', 'Kurnool', 'Rajahmundry',
            'Kadapa', 'Tirupati', 'Anantapur', 'Chittoor', 'Ongole', 'Nizamabad',
            
            # Northern cities
            'Meerut', 'Bareilly', 'Aligarh', 'Moradabad', 'Saharanpur', 'Gorakhpur',
            'Firozabad', 'Jhansi', 'Muzaffarnagar', 'Mathura', 'Rampur', 'Shahjahanpur',
            'Farrukhabad', 'Mau', 'Hapur', 'Etawah', 'Mirzapur', 'Bulandshahr',
            'Sambhal', 'Amroha', 'Hardoi', 'Fatehpur', 'Raebareli', 'Orai',
            
            # Western cities
            'Jodhpur', 'Bikaner', 'Udaipur', 'Ajmer', 'Bhilwara', 'Alwar', 'Bharatpur',
            'Sikar', 'Pali', 'Sri Ganganagar', 'Kishangarh', 'Baran', 'Jhunjhunu',
            'Tonk', 'Beawar', 'Hanumangarh'
        ]
        
        # Process cities in batches to avoid overwhelming the API
        batch_size = 20
        total_cities = len(cities)
        
        logger.info(f"Processing {total_cities} cities in batches of {batch_size}")
        
        for i in range(0, total_cities, batch_size):
            batch = cities[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_cities + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} cities)")
            
            for city in batch:
                try:
                    logger.debug(f"Fetching weather data for {city}")
                    weather_data = self.scrape_city(city)
                    if weather_data:
                        all_weather_data.append(weather_data)
                    time.sleep(0.5)  # Reduced rate limiting for efficiency
                    
                except Exception as e:
                    logger.error(f"Failed to fetch weather for {city}: {e}")
                    # Add basic fallback data
                    all_weather_data.append(self._get_basic_fallback(city))
            
            # Longer pause between batches
            if i + batch_size < total_cities:
                logger.info(f"Completed batch {batch_num}, pausing before next batch...")
                time.sleep(2)
        
        logger.info(f"Scraped weather data for {len(all_weather_data)} cities")
        return all_weather_data
    
    def scrape_city(self, city: str) -> Dict[str, Any]:
        """Scrape weather for specific city using WeatherAPI.com"""
        try:
            # Current weather endpoint
            current_url = f"{self.base_url}/current.json"
            params = {
                'key': self.api_key,
                'q': city,
                'aqi': 'no'
            }
            
            response = self.session.get(current_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_weather_data(data, city)
            else:
                logger.warning(f"API error for {city}: {response.status_code}")
                return self._get_basic_fallback(city)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {city}: {e}")
            return self._get_basic_fallback(city)
        except Exception as e:
            logger.error(f"Unexpected error for {city}: {e}")
            return self._get_basic_fallback(city)
    
    def _parse_weather_data(self, api_data: dict, city: str) -> Dict[str, Any]:
        """Parse WeatherAPI.com response into standardized format"""
        try:
            current = api_data.get('current', {})
            location = api_data.get('location', {})
            condition = current.get('condition', {})
            
            return {
                'city': location.get('name', city),
                'temperature': f"{current.get('temp_c', 'N/A')}°C",
                'humidity': f"{current.get('humidity', 'N/A')}%",
                'rainfall': f"{current.get('precip_mm', 0)}mm",
                'forecast': condition.get('text', 'No forecast'),
                'wind_speed': f"{current.get('wind_kph', 'N/A')} km/h",
                'pressure': f"{current.get('pressure_mb', 'N/A')} mb",
                'uv_index': current.get('uv', 'N/A'),
                'visibility': f"{current.get('vis_km', 'N/A')} km",
                'feels_like': f"{current.get('feelslike_c', 'N/A')}°C",
                'data_type': 'weather_data',
                'source': 'WeatherAPI.com',
                'last_updated': current.get('last_updated', 'N/A'),
                'coordinates': {
                    'lat': location.get('lat', 'N/A'),
                    'lon': location.get('lon', 'N/A')
                }
            }
        except Exception as e:
            logger.error(f"Error parsing weather data for {city}: {e}")
            return self._get_basic_fallback(city)
    
    def _get_basic_fallback(self, city: str) -> Dict[str, Any]:
        """Return basic fallback data when API fails"""
        return {
            'city': city,
            'temperature': 'N/A',
            'humidity': 'N/A',
            'rainfall': 'N/A',
            'forecast': 'Weather data unavailable',
            'wind_speed': 'N/A',
            'pressure': 'N/A',
            'uv_index': 'N/A',
            'visibility': 'N/A',
            'feels_like': 'N/A',
            'data_type': 'weather_data',
            'source': 'Data Unavailable',
            'last_updated': 'N/A',
            'coordinates': {
                'lat': 'N/A',
                'lon': 'N/A'
            }
        }

if __name__ == "__main__":
    scraper = WeatherScraper()
    data = scraper.scrape_all_weather_data()
    print(f"Scraped weather data for {len(data)} locations")
