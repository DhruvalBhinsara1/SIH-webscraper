# Scrapers - Data Collection Modules

This folder contains 5 specialized scraper modules for collecting rainwater harvesting data from different source categories.

## 📁 Actual Files in This Folder

| File | Size | Purpose |
|------|------|---------|
| `government_schemes_scraper.py` | 16.4 KB | Government schemes & subsidies scraper |
| `cost_scraper.py` | 9.1 KB | Equipment pricing & costs scraper |
| `weather_scraper.py` | 8.2 KB | Weather data scraper using WeatherAPI.com |
| `technical_resources_scraper.py` | 9.6 KB | Technical documentation scraper |
| `news_policy_scraper.py` | 7.0 KB | Policy updates & news scraper |
| `__init__.py` | 18 bytes | Package initialization |

## 🚀 Quick Usage - Individual Scrapers

### Test Individual Scrapers
```bash
# Test government schemes scraper
cd scrapers
python government_schemes_scraper.py

# Test weather data collection  
python weather_scraper.py

# Test cost data extraction
python cost_scraper.py

# Test technical resources
python technical_resources_scraper.py

# Test news and policy updates
python news_policy_scraper.py
```

## 🚀 Quick Usage

### Individual Scraper Testing
```bash
# Test government schemes scraper
python government_schemes_scraper.py

# Test weather data collection
python weather_scraper.py

# Test cost data extraction
python cost_scraper.py
```

### Programmatic Usage
```python
from scrapers.government_schemes_scraper import GovernmentSchemesScraper
from scrapers.weather_scraper import WeatherScraper

# Initialize scrapers
gov_scraper = GovernmentSchemesScraper()
weather_scraper = WeatherScraper()

# Collect data
schemes = gov_scraper.scrape_all_schemes()
weather_data = weather_scraper.scrape_city('Delhi')
```

## 📊 Data Collection Details

### Government Schemes Scraper
- **Sources**: Ministry of Jal Shakti, PMKSY, state portals, municipal websites
- **Data Extracted**: Scheme names, descriptions, eligibility criteria, subsidy amounts, application deadlines
- **Coverage**: Central, state, and municipal level schemes across all Indian states
- **Rate Limiting**: 3-second delay for government sites

### Weather Scraper
- **Primary API**: WeatherAPI.com with API key integration
- **Coverage**: 65+ Indian cities including metros, state capitals, tier-2 cities
- **Data Fields**: Temperature, humidity, rainfall, wind speed, pressure, UV index, visibility
- **Rate Limiting**: 5 requests per second to respect API limits

### Cost Scraper
- **Sources**: Government rate schedules, TradeIndia, IndiaMART, CPWD documents
- **Equipment Categories**: Water tanks, pumps, pipes, filters, installation materials
- **Price Patterns**: Supports ₹, Rs., INR formats with range detection
- **Validation**: Filters realistic price ranges and verifies supplier information

### Technical Resources Scraper
- **Sources**: CGWB, state technical departments, research institutions
- **Document Types**: PDFs, technical manuals, implementation guidelines
- **Content Extraction**: Uses BeautifulSoup and PDF parsing for structured data
- **Quality Scoring**: Validates technical relevance and completeness

## 🔧 Configuration

All scrapers use settings from `../config.py`:

```python
# Rate limiting settings
RATE_LIMIT_DELAY = 2  # seconds between requests
GOVERNMENT_SITE_DELAY = 3  # extra delay for government sites

# Quality thresholds
MIN_QUALITY_SCORE = 0.3
GOVERNMENT_SCHEMES_MIN_QUALITY = 0.4

# API configuration
WEATHER_API_KEY = "25df4b3bce1c4470bcb173218250109"
WEATHER_API_BASE_URL = "https://api.weatherapi.com/v1"
```

## 🛠️ Error Handling

Each scraper includes robust error handling:

- **SSL Certificate Issues**: Automatic fallback to unverified requests for government sites
- **Network Timeouts**: Configurable timeout with retry logic
- **Rate Limiting**: Built-in delays to respect server limits
- **Data Validation**: Quality scoring and filtering of incomplete records
- **Logging**: Comprehensive logging for debugging and monitoring

## 📈 Performance

- **Government Schemes**: ~60 URLs processed in 3-5 minutes
- **Weather Data**: 65+ cities processed in 1-2 minutes
- **Cost Data**: 20+ sources processed in 2-3 minutes
- **Technical Resources**: 40+ documents processed in 4-6 minutes

## 🔍 Troubleshooting

### Common Issues

1. **SSL Errors**: Government sites automatically use `verify=False`
2. **Rate Limiting**: Increase delays in config.py if getting blocked
3. **API Failures**: Check WeatherAPI.com key and quota
4. **Import Errors**: Ensure all dependencies installed: `pip install -r ../requirements.txt`

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run scraper with detailed logging
scraper = GovernmentSchemesScraper()
data = scraper.scrape_all_schemes()
```

## 📝 Adding New Scrapers

To add a new scraper module:

1. **Create new file**: `new_category_scraper.py`
2. **Inherit base patterns**: Follow existing scraper structure
3. **Add to config**: Include URLs in `../config.py`
4. **Update main script**: Add to `../final_multilingual_scraper.py`
5. **Test thoroughly**: Create test cases and validate output

### Template Structure
```python
class NewCategoryScraper:
    def __init__(self):
        self.config = ScraperConfig()
        self.session = requests.Session()
    
    def scrape_all_data(self):
        # Main scraping logic
        pass
    
    def _parse_content(self, content):
        # Content parsing logic
        pass
```

## 🔗 Integration

These scrapers are automatically used by:
- `../final_multilingual_scraper.py` (main execution script)
- `../test_enhanced_system.py` (testing framework)

For manual integration, import and use individual scrapers as needed.
