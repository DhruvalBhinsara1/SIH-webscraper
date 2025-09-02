# Jal Setu Rainwater Harvesting Web Scraper

A comprehensive web scraper for collecting rainwater harvesting data from government portals and trusted sources. This scraper extracts structured data on government schemes, weather/rainfall, costs, and technical resources.

## 🚀 Quick Start - Generate Complete Dataset

**To generate or update the entire dataset with full category coverage, run:**

```bash
python final_scraper.py
```

This single command:
- ✅ Scrapes all 6 data categories from 200+ sources
- ✅ Exports data in JSON + CSV formats
- ✅ Creates comprehensive summary report
- ✅ Saves everything to `output/` folder with timestamps

## Features

- **Complete Data Pipeline**: Single script execution for all data categories
- **Comprehensive Coverage**: 200+ verified data sources across 6 categories
- **Simple Export**: JSON and CSV formats for easy integration
- **Intelligent URL Categorization**: Automated URL discovery and categorization tools
- **Modular Architecture**: Organized folder structure with category-specific modules
- **SSL Certificate Handling**: Automatically bypasses SSL errors for government portals
- **Multi-Source Scraping**: Handles static, dynamic (JavaScript), tabular, and multi-language sources
- **AI-Powered Extraction**: Uses NLP models for intelligent content classification and structuring
- **Data Validation**: Ensures quality and consistency with scoring system
- **Error Handling**: Automatic retries and comprehensive logging
- **WeatherAPI.com Integration**: Primary weather data source with comprehensive weather and air quality data

## Project Structure

### 📁 `/scrapers/` - Data Collection Modules
- `government_schemes_scraper.py` - Extracts government schemes and subsidies
- `cost_scraper.py` - Scrapes equipment costs and pricing data
- `weather_scraper.py` - Collects weather and rainfall data
- `technical_resources_scraper.py` - Gathers technical documentation
- `news_policy_scraper.py` - Monitors policy updates and news

### 📁 `/theory_scraper/` - PDF Theory Extraction
- `fixed_pdf_scraper.py` - Extracts rainwater harvesting theory from government PDFs
- `output/` - Theory extraction results (533+ items from 22 PDFs)

### 📁 `/url_tools/` - URL Management & Discovery
- `url_validator.py` - Validates URLs and discovers data-containing sub-pages
- `url_discovery_system.py` - Automatically discovers new URLs from seed URLs
- `link_explorer.py` - Explores websites to find actual data-containing pages

### 📁 `/data_processing/` - Data Export & Processing
- `multilingual_data_exporter.py` - Exports data in 11 Indian languages (single file per category)

### 📁 `/utils/` - Utilities & Validation
- `data_validator.py` - Data validation and quality scoring

### 📁 `/output/` - Main Export Directory
- All multilingual JSON and CSV files are saved here
- Export summary reports
- Single file per category containing all 11 languages

## Data Categories

### Government Schemes & Subsidies
- `government_schemes_multilingual_YYYYMMDD_HHMMSS.json/csv`
- Extracts scheme names, eligibility criteria, subsidy amounts, deadlines, and contact information

### Weather & Rainfall Data
- `weather_data_multilingual_YYYYMMDD_HHMMSS.json/csv`
- Collects rainfall measurements, temperature, humidity, and weather forecasts

### Cost & Market Data
- `cost_data_multilingual_YYYYMMDD_HHMMSS.json/csv`
- Gathers pricing for rainwater harvesting equipment and materials

### Technical Resources
- `technical_resources_multilingual_YYYYMMDD_HHMMSS.json/csv`
- Compiles guidelines, specifications, standards, and implementation procedures

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install additional NLP models:**
```bash
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"
```

4. **Install ChromeDriver for Selenium:**
   - Download ChromeDriver from https://chromedriver.chromium.org/
   - Add to your system PATH or place in project directory

## Usage

### Quick Start

```bash
# MAIN COMMAND - Generate complete unified dataset
python final_multilingual_scraper.py

# Optional: Test URL categorization system
python url_tools/intelligent_url_categorizer.py

# Optional: Test individual components
python test_enhanced_system.py
```

### Multilingual Export Usage

```python
from data_processing.multilingual_data_exporter import MultilingualDataExporter

# Initialize exporter
exporter = MultilingualDataExporter()

# Export data in all 11 languages to single files
result = exporter.export_government_schemes(schemes_data)
print(f"Exported to: {result['json']} and {result['csv']}")
print(f"Languages included: {result['languages_included']}")
```

## URL Tools Workflow - Step by Step Guide

The URL tools help you maintain and expand your data sources. Use them in this specific order:

### **Step 1: Validate Existing URLs**
```python
from url_tools.url_validator import URLValidator

# Check if current URLs in config.py are still working
validator = URLValidator()
results = validator.validate_category_urls(
    ScraperConfig.GOVERNMENT_SCHEMES_URLS, 
    'government_schemes'
)

print(f"✅ Valid URLs: {len(results['valid_urls'])}")
print(f"❌ Invalid URLs: {len(results['invalid_urls'])}")
print(f"🔍 Discovered new links: {len(results['discovered_links'])}")
print(f"⭐ High quality pages: {len(results['high_quality_pages'])}")
```

### **Step 2: Explore and Discover New URLs**
```python
from url_tools.link_explorer import LinkExplorer

# Explore existing URLs to find better sub-pages
explorer = LinkExplorer()
exploration_results = []

for url in ScraperConfig.GOVERNMENT_SCHEMES_URLS[:5]:  # Test first 5
    result = explorer.explore_page(url, max_depth=2)
    exploration_results.append(result)
    
    print(f"📄 PDF documents found: {len(result['pdf_documents'])}")
    print(f"🏛️ Scheme pages found: {len(result['scheme_pages'])}")
    print(f"📊 Data pages found: {len(result['data_pages'])}")
```

### **Step 3: Discover URLs from Seed Sources**
```python
from url_tools.url_discovery_system import URLDiscoverySystem

# Load existing URLs and discover new ones
discovery = URLDiscoverySystem()
existing_urls = discovery.load_existing_urls()

# Use high-quality seed URLs to find more
seed_urls = [
    'https://jalshakti-dowr.gov.in/schemes',
    'https://pmksy.gov.in/',
    'https://cgwb.gov.in/'
]

new_urls = discovery.discover_new_urls(
    seed_urls, 
    existing_urls['government_schemes'],
    min_relevance=3,  # Only high-relevance URLs
    validate_new=True
)

print(f"🆕 Found {len(new_urls)} new valuable URLs")
for url_info in new_urls[:5]:  # Show top 5
    print(f"  {url_info['relevance']}/10 - {url_info['url']}")
```

### **Step 4: Update Configuration (Manual)**
After discovering new URLs, manually add the best ones to `config.py`:

```python
# Add to GOVERNMENT_SCHEMES_URLS in config.py
new_valuable_urls = [
    'https://new-discovered-scheme-page.gov.in',
    'https://another-valuable-resource.gov.in'
]
```

### **Complete URL Management Workflow**
```python
# Complete workflow script
from url_tools.url_validator import URLValidator
from url_tools.url_discovery_system import URLDiscoverySystem
from config import ScraperConfig

def manage_urls():
    # Step 1: Validate existing
    validator = URLValidator()
    validation_results = validator.validate_category_urls(
        ScraperConfig.GOVERNMENT_SCHEMES_URLS, 'government_schemes'
    )
    
    # Step 2: Discover new URLs
    discovery = URLDiscoverySystem()
    existing_urls = discovery.load_existing_urls()
    
    seed_urls = validation_results['valid_urls'][:10]  # Use valid URLs as seeds
    new_urls = discovery.discover_new_urls(
        seed_urls, existing_urls['government_schemes']
    )
    
    # Step 3: Report findings
    print("🔍 URL Management Results:")
    print(f"  Valid existing URLs: {len(validation_results['valid_urls'])}")
    print(f"  Invalid URLs to remove: {len(validation_results['invalid_urls'])}")
    print(f"  New URLs discovered: {len(new_urls)}")
    print(f"  High-quality pages: {len(validation_results['high_quality_pages'])}")
    
    return {
        'validation': validation_results,
        'new_discoveries': new_urls
    }

# Run the complete workflow
results = manage_urls()
```

## Multilingual Export System

### **11 Supported Languages**
- **English** (en), **Hindi** (hi), **Bengali** (bn), **Telugu** (te)
- **Marathi** (mr), **Tamil** (ta), **Gujarati** (gu), **Kannada** (kn)
- **Malayalam** (ml), **Punjabi** (pa), **Odia** (or)

### **Single File Export Format**
Each data category exports to **one JSON + one CSV file** containing all 11 languages:

```json
{
  "metadata": {
    "export_timestamp": "20250902_025046",
    "data_type": "government_schemes",
    "total_records": 25,
    "languages_included": ["en", "hi", "bn", "te", "mr", "ta", "gu", "kn", "ml", "pa", "or"],
    "export_format": "Single file with all languages"
  },
  "data_by_language": {
    "en": {
      "language_name": "English",
      "records": [{"Name": "PMKSY", "Description": "Irrigation scheme", ...}]
    },
    "hi": {
      "language_name": "Hindi", 
      "records": [{"नाम": "PMKSY", "विवरण": "सिंचाई योजना", ...}]
    }
  }
}
```

## Complete Scraping Workflow

### **Main Script: Complete Data Pipeline**
```bash
# MAIN COMMAND - Generate complete unified dataset
python final_multilingual_scraper.py
```

This is the **primary script** that executes the complete data pipeline, scraping and aggregating data from all target URLs and sources, outputting the unified final dataset with full category coverage.

### **Advanced Usage**
```python
from final_multilingual_scraper import FinalMultilingualScraper

# Initialize complete scraper
scraper = FinalMultilingualScraper()

# Run complete data pipeline
results = scraper.run_complete_scraping()

print("📊 Complete Dataset Generated:")
for category, data in results['scraped_data'].items():
    print(f"  {category}: {len(data)} records")
```

## Configuration

Modify `config.py` to customize:

- **URLs**: Add or remove source URLs for each data category
- **Rate Limiting**: Adjust delays between requests
- **Quality Thresholds**: Set minimum quality scores for data filtering
- **Output Settings**: Configure file formats and locations
- **API Keys**: Configure WeatherAPI.com credentials

```python
# API Configuration (set in config.py)
WEATHER_API_KEY = "25df4b3bce1c4470bcb173218250109"
WEATHER_API_BASE_URL = "https://api.weatherapi.com/v1"
INDIAN_WEATHER_API_KEY = "sk-live-FS3Q8YbD73R3hL04x4gERQged6hl35ullOxbmsbG"
```

## Enhanced Features

### **Currency Parsing**
Handles all Indian rupee variations:
- ₹ (Unicode rupee symbol)
- Rs. / Rs / RS / rs  
- INR / inr
- rupees / RUPEES / Rupees
- रुपये / रू (Hindi/Devanagari)

### **Updated Data Sources**

#### **Government Cost Data**
- Railway DSR documents
- Delhi Schedule of Rates
- UP PWD rates
- CEWACOR specifications
- SBI price bids

#### **Marketplace URLs (Enhanced)**
- **IndiaMART**: Using `dir.indiamart.com` subdomain for better product listings
- **TradeIndia**: Comprehensive product categories
- Water storage tanks, HDPE tanks, PVC pipe fittings, submersible pumps, sand filters

## Data Quality & Validation

The scraper includes comprehensive data validation:

- **Completeness**: Checks for required fields
- **Accuracy**: Validates data formats and ranges
- **Freshness**: Scores based on data recency
- **Relevance**: Filters content related to rainwater harvesting
- **Structure**: Ensures consistent data organization

Quality scores range from 0.0 to 1.0, with configurable minimum thresholds.

## Troubleshooting

### **Common Issues**
1. **SSL Errors**: Government sites automatically fall back to non-SSL verification
2. **Rate Limiting**: Built-in delays between requests  
3. **Missing Dependencies**: Install with `pip install -r requirements.txt`
4. **Import Errors**: Use correct module paths after reorganization

### **Dependencies Installation**
```bash
pip install requests beautifulsoup4 selenium pandas nltk spacy
python -m spacy download en_core_web_sm
python -m nltk download punkt_tab
```

### **Testing Individual Components**
```bash
# Test complete enhanced system
python test_enhanced_system.py

# Test URL categorization
python test_url_categorization.py

# Test individual scrapers (if needed)
python scrapers/government_schemes_scraper.py
python scrapers/weather_scraper.py
```

## Error Handling

The scraper includes robust error handling:

- **SSL Errors**: Automatically retries without SSL verification
- **Network Timeouts**: Configurable timeout and retry logic
- **Rate Limiting**: Respectful delays between requests
- **Data Validation**: Filters out incomplete or invalid records
- **Logging**: Comprehensive logging to file and console

## Data Sources

### **Government Schemes & Portals**
- Ministry of Jal Shakti: https://jalshakti-dowr.gov.in/
- PMKSY: https://pmksy.gov.in/
- Central Ground Water Board: https://cgwb.gov.in/
- India Water Portal: https://indiawris.gov.in/wris/
- Atal Bhujal Yojana: https://atal-bhujal.gov.in/
- State government water departments and municipal portals

### **Weather Sources**
- **WeatherAPI.com**: Primary API source with comprehensive data
- **Indian Weather API**: Backup weather service
- India Meteorological Department: https://mausam.imd.gov.in/
- IMD Pune: https://imdpune.gov.in/
- Data.gov.in: https://data.gov.in/catalog/rainfall-india

### **Cost & Market Sources**
- Railway DSR documents, Delhi Schedule of Rates, UP PWD rates
- IndiaMART: `dir.indiamart.com` subdomain for structured listings
- TradeIndia: Comprehensive product categories
- TERI cost reports and government pricing schedules

### **Technical Resources**
- CGWB: https://cgwb.gov.in/
- Rainwater Harvesting Portal: http://www.rainwaterharvesting.org/
- CPCB Guidelines: https://cpcb.nic.in/
- CWAS Guidelines: https://cwas.org.in/resources/
- National Water Mission: https://www.nwm.gov.in/

## Support & Troubleshooting

For issues or questions:
1. Check the log files (`jal_setu_scraper.log`, `scraper.log`)
2. Verify all dependencies are installed correctly
3. Ensure ChromeDriver is properly configured
4. Test individual components before full runs
5. Use URL tools to validate and discover new data sources

## License

This project is developed for the Smart India Hackathon 2024 and is intended for educational and research purposes.

## File Structure

```
jal-setu-webscraper/
├── scrapers/                    # Data collection modules
│   ├── government_schemes_scraper.py
│   ├── cost_scraper.py
│   ├── weather_scraper.py
│   ├── technical_resources_scraper.py
│   └── news_policy_scraper.py
├── url_tools/                   # URL management & discovery
│   ├── url_validator.py
│   ├── url_discovery_system.py
│   └── link_explorer.py
├── data_processing/             # Export & processing
│   └── multilingual_data_exporter.py
├── utils/                       # Utilities & validation
│   └── data_validator.py
├── output/                      # Multilingual export files
│   ├── government_schemes_multilingual_YYYYMMDD_HHMMSS.json
│   ├── government_schemes_multilingual_YYYYMMDD_HHMMSS.csv
│   ├── cost_data_multilingual_YYYYMMDD_HHMMSS.json
│   ├── cost_data_multilingual_YYYYMMDD_HHMMSS.csv
│   └── export_summary_YYYYMMDD_HHMMSS.json
├── final_multilingual_scraper.py # Main execution script
├── main_scraper.py              # Base scraper class
├── ai_content_extractor.py      # AI-powered content extraction
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
└── README.md                    # This comprehensive guide
```

## API Integration

### WeatherAPI.com
The scraper integrates with WeatherAPI.com for comprehensive weather data:
- **API Key**: `25df4b3bce1c4470bcb173218250109`
- **Base URL**: `https://api.weatherapi.com/v1`
- **Endpoints**: `/current.json`, `/forecast.json`
- **Features**: 
  - Current weather conditions
  - 3-day detailed forecasts
  - Air quality data (PM2.5, PM10, CO, NO2, O3, SO2)
  - Coordinate-based lookup
  - Weather alerts and warnings
  - Hourly forecasts
  - UV index and visibility data

### Testing API Connectivity
```python
from weather_scraper import WeatherScraper

scraper = WeatherScraper()
api_working = scraper.test_weather_api()
print(f"API Status: {'✅ Working' if api_working else '❌ Failed'}")

# Test with coordinates
weather_data = scraper.get_weather_by_coordinates(28.6667, 77.2167)  # Delhi
print(f"Weather: {weather_data['weather_condition']} at {weather_data['temperature_c']}°C")
```

### Quick API Test
```bash
# Test WeatherAPI.com integration
python test_api.py

# Test weather scraper
python weather_scraper.py
```

## Support

For issues or questions:
1. Check the log files (`jal_setu_scraper.log`, `scraper.log`)
2. Verify all dependencies are installed correctly
3. Ensure ChromeDriver is properly configured
4. Test individual components: `python run_jal_setu.py test`
5. Start with single category scraping before full runs

---

**Note**: This comprehensive scraper system is optimized for reliable multilingual data collection from official Indian government sources. The organized modular structure with URL discovery tools ensures maintainable and expandable data collection capabilities for the Jal Setu rainwater harvesting application.
