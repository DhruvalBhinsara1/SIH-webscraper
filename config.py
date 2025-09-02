#!/usr/bin/env python3
"""
Configuration file for Jal Setu Web Scraper
Contains all URLs, settings, and configuration parameters
"""

import os
from typing import Dict, List, Any

class ScraperConfig:
    """Configuration class for the Jal Setu scraper"""
    
    # Output settings
    OUTPUT_DIR = "output"
    LOG_LEVEL = "INFO"
    LOG_FILE = "scraper.log"
    
    # Rate limiting settings (seconds)
    RATE_LIMIT_DELAY = 2
    GOVERNMENT_SITE_DELAY = 3
    COMMERCIAL_SITE_DELAY = 1
    
    # Request settings
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    
    # Data quality settings
    MIN_QUALITY_SCORE = 0.3
    GOVERNMENT_SCHEMES_MIN_QUALITY = 0.4
    WEATHER_DATA_MIN_QUALITY = 0.3
    COST_DATA_MIN_QUALITY = 0.3
    TECHNICAL_RESOURCES_MIN_QUALITY = 0.4
    
    # Government Schemes URLs - Comprehensive List
    GOVERNMENT_SCHEMES_URLS = [
        # Ministry of Jal Shakti and Central Schemes
        'https://jalshakti-dowr.gov.in/programs',
        'https://www.jalshakti-dowr.gov.in/offerings?page=1/',
        'https://pmksy.gov.in/',
        'https://pmksy.gov.in/schemes',
        'https://pmksy.gov.in/Guidelines.aspx',
        'https://pmksy.gov.in/pdfLinks/PMKSY_UserManual.pdf',
        'https://pmksy.gov.in/pdfLinks/PMKSYMI_UserManual.pdf',
        'https://pmksy.gov.in/MicroIrrigation/Archive/Guideline_MIF03082018.pdf',
        'https://pmksy.gov.in/MicroIrrigation/Archive/GuidelinesMIRevised250817.pdf',
        'https://pmksy.gov.in/pdflinks/DBTCellGuidelinesforState.pdf',
        
        # MyScheme Portal and India.gov.in
        'https://www.myscheme.gov.in/schemes?sector=Water%20Resources',
        
        # State-wise Water Schemes
        'https://gsda.maharashtra.gov.in/en-atal-bhujal-project',
        'https://www.tn.gov.in/scheme/department/15',
        
        # Additional Central Government Portals
        'https://cgwb.gov.in/',
        'https://pib.gov.in/indexd.aspx'
    ]
    
    # Weather & Rainfall URLs - Enhanced with IMD and Research Sources
    WEATHER_URLS = [
        # IMD Official Sources
        "https://mausam.imd.gov.in/forecast",
        "https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html",
        "https://indiawris.gov.in/wris/#/dataCollection",
        "https://www.imdkol.gov.in/weathermanual/data/rainfall",
        "https://open-meteo.com/en/docs",
        "https://imdpune.gov.in/library/publication.html",
        "https://mausam.imd.gov.in/responsive/rainfallinformation_swd.php",
        "https://data.gov.in/catalog/rainfall-india",
        "https://mausam.imd.gov.in/"
    ]
    
    # Cost & Market Data URLs
    COST_URLS = [
        "https://tradeindia.com/",
        "https://mohua.gov.in/upload/uploadfiles/files/TERI_UC_Report26.pdf",
        "https://delhijalboard.delhi.gov.in/jalboard/water"
    ]
    
    # Technical Resources URLs
    TECHNICAL_URLS = [
    
        "https://jalshakti-dowr.gov.in/rwh",
        "http://www.rainwaterharvesting.org/",
        "https://cwas.org.in/resources/file_manager/module_3-3_1_rwh_guidelines.pdf",
        "https://www.nwm.gov.in/sites/default/files/RWH_Structures_final.pdf",
        "https://cpcb.nic.in/openpdffile.php?id=UHVibGljYXRpb25GaWxlLzc3MF8xNDU3OTMxNDc2X1B1YmxpY2F0aW9uXzI1MF9zZWMxMl82LnBkZg%3D%3D"
    ]
    
    # State-specific URLs
    STATE_URLS = {
        'delhi': [
            'https://delhijalboard.delhi.gov.in/jalboard/water'
        ],
        'maharashtra': [
            'https://www.maharashtra.gov.in/',
            'https://mahawrd.maharashtra.gov.in/'
        ],
        'karnataka': [
            'https://www.karnataka.gov.in/',
            'https://kwb.karnataka.gov.in/'
        ],
        'tamil_nadu': [
            'https://www.tn.gov.in/',
            'https://www.twad.tn.gov.in/'
        ],
        'gujarat': [
            'https://gujaratindia.gov.in/',
            'https://guj-nwrws.gujarat.gov.in/'
        ],
        'rajasthan': [
            'https://rajasthan.gov.in/',
            'https://water.rajasthan.gov.in/'
        ],
        'uttar_pradesh': [
            'https://up.gov.in/',
            'https://jalshakti.up.gov.in/'
        ],
        'west_bengal': [
            'https://wb.gov.in/',
            'https://wbphed.gov.in/'
        ]
    }
    
    # Major Indian cities for weather data with IMD station IDs
    CITIES = [
        'Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad',
        'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow', 'Kanpur', 'Nagpur',
        'Indore', 'Thane', 'Bhopal', 'Visakhapatnam', 'Pimpri', 'Patna',
        'Vadodara', 'Ghaziabad', 'Ludhiana', 'Agra', 'Nashik', 'Faridabad',
        'Meerut', 'Rajkot', 'Kalyan-Dombivali', 'Vasai-Virar', 'Varanasi'
    ]
    
    
    # Equipment categories for cost scraping
    EQUIPMENT_CATEGORIES = [
        'water tank', 'storage tank', 'pvc pipe', 'hdpe pipe', 'filter',
        'first flush diverter', 'leaf screen', 'gutter', 'downpipe',
        'pump', 'submersible pump', 'pressure tank', 'valve',
        'mesh filter', 'sand filter', 'carbon filter', 'uv sterilizer',
        'rooftop harvesting', 'underground tank', 'overhead tank',
        'rainwater harvesting system', 'collection tank', 'distribution system'
    ]
    
    # ===== COMPREHENSIVE DATA SOURCES =====
    
    # Government Schemes and Policy URLs
    GOVERNMENT_SCHEMES_URLS = [
        # Central Government Portals
        'https://www.jalshakti-dowr.gov.in/offerings?page=1/',
        'https://pmksy.gov.in/',
        'https://pmksy.gov.in/Guidelines.aspx',
        'https://pmksy.gov.in/pdfLinks/PMKSY_UserManual.pdf',
        'https://pmksy.gov.in/pdfLinks/PMKSYMI_UserManual.pdf',
        'https://pmksy.gov.in/MicroIrrigation/Archive/Guideline_MIF03082018.pdf',
        'https://pmksy.gov.in/MicroIrrigation/Archive/GuidelinesMIRevised250817.pdf',
        'https://pmksy.gov.in/pdflinks/DBTCellGuidelinesforState.pdf',
        'https://cgwb.gov.in/',
        'https://cgwb.gov.in/sites/default/files/2023-05/new-guideline_for-ground-water-regulation.pdf',
        'https://cgwb.gov.in/freewares-groundwater-data-analysis',
        'https://www.myscheme.gov.in/',
        'https://pib.gov.in/indexd.aspx',
        
        # State Government Portals - Comprehensive list of all Indian states and UTs
        'https://uk.gov.in/',
        'https://gujaratindia.gov.in/',
        'https://andaman.gov.in/',
        'https://ladakh.gov.in/',
        'https://www.maharashtra.gov.in/',
        'https://mizoram.nic.in/',
        'https://tripura.gov.in/',
        'https://punjab.gov.in/',
        'https://www.goa.gov.in/',
        'https://dnh.gov.in/',
        'https://www.karnataka.gov.in/english',
        'https://state.bihar.gov.in/main/CitizenHome.html',
        'https://www.cgstate.gov.in/',
        'https://wb.gov.in/',
        'https://www.jk.gov.in/',
        'https://www.ap.gov.in/',
        'https://lakshadweep.gov.in/',
        'http://assam.gov.in/',
        'http://www.telangana.gov.in/',
        'http://up.gov.in/',
        'https://www.py.gov.in/',
        'http://sikkim.gov.in/',
        'http://tn.gov.in/',
        'http://chandigarh.gov.in/',
        # Removed problematic URLs:
        # 'http://odisha.gov.in/', - Connection timeout
        # 'http://haryana.gov.in/', - 404 Not Found  
        # 'http://daman.nic.in/', - Connection timeout
        # 'http://rajasthan.gov.in/', - No data extracted
        # 'http://arunachalpradesh.gov.in/', - Connection timeout
        # 'http://mp.gov.in/', - Connection timeout
        'http://nagaland.gov.in/',
        'http://himachal.gov.in/',
        'http://meghalaya.gov.in/',
        'http://kerala.gov.in/',
        'http://manipur.gov.in/',
        'http://jharkhand.gov.in/',
        'http://delhi.gov.in/',
        
        # Municipal and City Portals
        'https://www.mcgm.gov.in/',
        'https://www.delhigovt.nic.in/',
        'https://www.bbmp.gov.in/',
        'https://www.chennaicorporation.gov.in/',
        'https://www.kmcgov.in/',
        'https://www.ghmc.gov.in/',
        'https://www.punecorporation.org/',
        'https://www.ahmedabadcity.gov.in/',
        'https://www.jaipurmc.org/',
        'https://www.suratmunicipal.gov.in/',
        'https://www.kanpurnagar.nic.in/',
        'https://www.lmc.up.nic.in/',
        'https://www.nmcnagpur.gov.in/',
        'https://www.indoremahanagar.org/',
        'https://www.thanecity.gov.in/',
        'https://www.bmcbhopal.gov.in/',
        'https://www.gvmc.gov.in/',
        'https://www.pmc.gov.in/',
        'https://www.vmc.gov.in/',
        'https://www.mcgurgaon.gov.in/',
        'https://www.mcludhiana.gov.in/',
        'https://www.agranagarnigam.up.nic.in/',
        'https://www.nashikcorporation.in/',
        'https://www.fdamcb.com/',
        'https://www.meerut.nic.in/',
        'https://www.rmc.gov.in/',
        'https://www.kdmc.gov.in/',
        'https://www.vvcmc.in/',
        'https://www.varanasi.nic.in/'
    ]
    
    # Cost Data and Equipment Pricing URLs
    COST_DATA_URLS = [
        # Government Rate Sources - Verified Working Documents
        'http://www.rwf.indianrailways.gov.in/uploads/DSR_%20Central%20Public%20Works%20Vol_2_2018.pdf',
        'https://www.scribd.com/document/861539737/DELHI-SCHEDULE-OF-RATES-E-M-VOLUME-II',
        'https://uppwd.gov.in/post/schedule-of-rates',
        'https://cewacor.nic.in/Docs/TendersArchieve/ArchieveTender2018/Scheduleofquantities%20_071218.pdf',
        'https://sbi.co.in/webfiles/uploads/files_2324/190620231821-price%20bid.pdf',
        
        # TradeIndia Working Product Pages with Actual Prices
        'https://www.tradeindia.com/manufacturers/hdpe-storage-tanks.html',
        'https://www.tradeindia.com/vadodara/rainwater-harvesting-systems-city-224495.html',
        'https://www.tradeindia.com/manufacturers/polyethylene-water-tank.html',
        'https://www.tradeindia.com/search.html?keyword=rainwater+harvesting',
        'https://www.tradeindia.com/search.html?keyword=water+tank',
        'https://www.tradeindia.com/search.html?keyword=storage+tank',
        'https://www.tradeindia.com/search.html?keyword=pvc+pipes',
        'https://www.tradeindia.com/search.html?keyword=water+pump',
        'https://www.tradeindia.com/search.html?keyword=filter+media',
        'https://www.tradeindia.com/search.html?keyword=concrete+rings',
        
        # IndiaMART Working Search URLs - Using dir subdomain for better results
        'https://dir.indiamart.com/search.mp?ss=water+storage+tank',
        'https://dir.indiamart.com/search.mp?ss=rainwater+harvesting+system',
        'https://dir.indiamart.com/search.mp?ss=hdpe+tank',
        'https://dir.indiamart.com/search.mp?ss=pvc+pipe+fittings',
        'https://dir.indiamart.com/search.mp?ss=submersible+pump',
        'https://dir.indiamart.com/search.mp?ss=sand+filter',
        
        # Research Papers with Cost Analysis
        'https://iwaponline.com/ws/article/21/8/4221/81851/Cost-effectiveness-of-rainwater-harvesting',
        'https://www.mdpi.com/2073-4441/13/21/3121/pdf',
        
        # Government Technical Reports
        'https://mohua.gov.in/upload/uploadfiles/files/TERI_UC_Report26.pdf'
    ]
    
    # Technical Resources and Guidelines URLs
    TECHNICAL_RESOURCES_URLS = [
        # Central Government Technical Resources
        'https://cgwb.gov.in/documents/Rainwater%20Harvesting.pdf',
        'https://jalshakti-dowr.gov.in/sites/default/files/Rainwater_Harvesting_Guidelines.pdf',
        'https://mowr.gov.in/sites/default/files/Rainwater_Harvesting_Manual.pdf',
        
        # Municipal Technical Resources
        'https://www.mcgm.gov.in/irj/go/km/docs/documents/MCGM%20Department%20List/Hydraulic%20Engineer/Deputy%20City%20Engineer%20(Planning%20and%20Design)/pdf/RWH_Guidelines.pdf',
        'https://www.delhigovt.nic.in/sites/default/files/All-PDF/RWH_Manual_Delhi.pdf',
        
        # State Technical Guidelines
        'https://www.wb.gov.in/portal/web/guest/rainwater-harvesting',
        
        # Research and Academic Resources
        'http://www.rainwaterharvesting.org/',
        'https://cwas.org.in/resources/file_manager/module_3-3_1_rwh_guidelines.pdf',
        'https://www.nwm.gov.in/sites/default/files/RWH_Structures_final.pdf',
        'https://cpcb.nic.in/openpdffile.php?id=UHVibGljYXRpb25GaWxlLzc3MF8xNDU3OTMxNDc2X1B1YmxpY2F0aW9uXzI1MF9zZWMxMl82LnBkZg%3D%3D',
        'https://www.ircwash.org/sites/default/files/rainwater_harvesting_manual.pdf',
        'https://www.unep.org/resources/report/rainwater-harvesting-guide',
        'https://www.who.int/water_sanitation_health/hygiene/emergencies/fs2_33.pdf',
        
        # International Best Practices
        'https://www.unwater.org/publications/rainwater-harvesting',
        'https://www.worldbank.org/en/topic/water/publication/rainwater-harvesting',
        'https://www.fao.org/3/u3160e/u3160e04.htm'
    ]
    
    # News and Policy Updates URLs
    NEWS_POLICY_URLS = [
        # Government Press Information Bureau
        'https://pib.gov.in/PressReleaseIframePage.aspx?PRID=1234567',
        'https://pib.gov.in/indexd.aspx',
        'https://www.pmindia.gov.in/en/news_updates/',
        
        # Ministry Specific News
        'https://jalshakti-dowr.gov.in/press-releases',
        'https://mowr.gov.in/press-releases',
        'https://pmksy.gov.in/news',
        
        # News Portals - Water and Environment Focus
        'https://www.downtoearth.org.in/news/water',
        'https://www.thethirdpole.net/en/water/',
        'https://www.indiawaterportal.org/news',
        'https://www.waterpowermagazine.com/news/',
        'https://www.waterworld.com/international/article/14283315/india-water-news',
        
        # RSS Feeds for Real-time Updates
        'https://pib.gov.in/rss/livefeeds.aspx',
        'https://www.downtoearth.org.in/rss/water.xml',
        'https://www.indiawaterportal.org/rss.xml'
    ]
    
    # Environmental Impact and Statistics URLs
    ENVIRONMENTAL_IMPACT_URLS = [
        # Research Papers and Studies
        'https://www.mdpi.com/2073-4441/13/21/3121/pdf',
        'https://iwaponline.com/ws/article/21/8/4221/81851/Cost-effectiveness-of-rainwater-harvesting',
        'https://www.sciencedirect.com/science/article/pii/S0048969721012134',
        
        # Government Environmental Reports
        'https://moef.gov.in/wp-content/uploads/2019/05/National-Water-Policy-2012.pdf',
        'https://cpcb.nic.in/uploads/Projects/Bio-Medical-Waste/BMW_ANNUAL_REPORT_2019-20.pdf',
        'https://cgwb.gov.in/sites/default/files/2023-05/national-compilation-on-dynamic-ground-water-resources-of-india-2022.pdf',
        
        # International Environmental Data
        'https://www.unep.org/resources/report/global-environment-outlook-6',
        'https://www.worldbank.org/en/topic/water/publication/water-scarce-cities',
        'https://www.who.int/news-room/fact-sheets/detail/drinking-water',
        'https://www.epa.gov/newsroom/newsreleases'
    ]
    
    # News and Policy Update URLs - Live News Feeds
    NEWS_POLICY_URLS = [
        # Current News Feed Pages (live, always updating)
        'https://www.thehindu.com/tag/rainwater-harvesting/',
        'https://timesofindia.indiatimes.com/topic/rainwater-harvesting',
        'https://www.downtoearth.org.in/tag/rainwater-harvesting',
        'https://pib.gov.in/indexd.aspx',
        'https://www.pmindia.gov.in/en/news_updates/',
        'https://jalshakti-dowr.gov.in/press-releases',
        'https://mowr.gov.in/press-releases',
        'https://pmksy.gov.in/news'
    ]
    
    # Technical resource categories
    TECHNICAL_CATEGORIES = [
        'design guidelines', 'construction standards', 'maintenance procedures',
        'quality standards', 'safety regulations', 'installation guidelines',
        'technical specifications', 'best practices', 'case studies',
        'research papers', 'implementation guides', 'troubleshooting'
    ]
    
    # Data validation settings
    REQUIRED_FIELDS = {
        'government_schemes': ['scheme_name', 'content'],
        'weather_data': ['source_text'],
        'cost_information': ['source_text'],
        'technical_resources': ['content']
    }
    
    # Quality scoring weights
    QUALITY_WEIGHTS = {
        'completeness': 0.3,
        'accuracy': 0.25,
        'freshness': 0.2,
        'relevance': 0.15,
        'structure': 0.1
    }
    
    # Selenium settings
    SELENIUM_SETTINGS = {
        'headless': True,
        'window_size': '1920,1080',
        'page_load_timeout': 30,
        'implicit_wait': 10
    }
    
    # API Configuration - WeatherAPI.com
    WEATHER_API_KEY = "25df4b3bce1c4470bcb173218250109"
    WEATHER_API_BASE_URL = "https://api.weatherapi.com/v1"
    
    # User agent for requests
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    # File output settings
    OUTPUT_FORMATS = ['json', 'csv']
    MAX_RECORDS_PER_FILE = 10000
    
    # Language settings
    DEFAULT_LANGUAGE = 'en'
    SUPPORTED_LANGUAGES = ['en', 'hi', 'mr', 'gu', 'ta', 'te', 'kn', 'bn']
    
    @classmethod
    def get_all_urls(cls) -> Dict[str, List[str]]:
        """Get all configured URLs by category"""
        return {
            'government_schemes': cls.GOVERNMENT_SCHEMES_URLS,
            'weather_data': cls.WEATHER_URLS,
            'cost_information': cls.COST_URLS,
            'technical_resources': cls.TECHNICAL_URLS
        }
    
    @classmethod
    def get_state_urls(cls, state: str) -> List[str]:
        """Get URLs for a specific state"""
        state_key = state.lower().replace(' ', '_')
        return cls.STATE_URLS.get(state_key, [])
    
    @classmethod
    def get_output_path(cls, filename: str) -> str:
        """Get full output path for a file"""
        return os.path.join(cls.OUTPUT_DIR, filename)
    
    @classmethod
    def create_output_directory(cls):
        """Create output directory if it doesn't exist"""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)

# Environment-specific configurations
class DevelopmentConfig(ScraperConfig):
    """Development environment configuration"""
    LOG_LEVEL = "DEBUG"
    RATE_LIMIT_DELAY = 1
    MAX_RETRIES = 2

class ProductionConfig(ScraperConfig):
    """Production environment configuration"""
    LOG_LEVEL = "INFO"
    RATE_LIMIT_DELAY = 3
    MAX_RETRIES = 5
    MIN_QUALITY_SCORE = 0.5

class TestingConfig(ScraperConfig):
    """Testing environment configuration"""
    OUTPUT_DIR = "test_output"
    LOG_LEVEL = "DEBUG"
    RATE_LIMIT_DELAY = 0.5
    MAX_RETRIES = 1
    
    # Reduced URLs for testing
    GOVERNMENT_SCHEMES_URLS = [
        "https://jalshakti-dowr.gov.in/",
        "https://pmksy.gov.in/"
    ]
    
    WEATHER_URLS = [
        "https://mausam.imd.gov.in/"
    ]
    
    COST_URLS = [
        "https://delhijalboard.delhi.gov.in/jalboard/water",
        "https://djb.gov.in/StaticContent/Tarrif.pdf",
        "https://djb.gov.in/DJBRMSPortal/portal/downloadCircular.html",
        "https://delhijalboard.delhi.gov.in/sites/default/files/Jalboard/generic_multiple_files/budget_file_2024-25.pdf"
    ]
    
    TECHNICAL_URLS = [
        "https://jalshakti-dowr.gov.in/rwh",
        "http://www.rainwaterharvesting.org/",
        "https://cwas.org.in/resources/file_manager/module_3-3_1_rwh_guidelines.pdf"
    ]

# Configuration factory
def get_config(environment: str = 'production') -> ScraperConfig:
    """Get configuration based on environment"""
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    config_class = configs.get(environment.lower(), ProductionConfig)
    return config_class()

if __name__ == "__main__":
    # Test configuration
    config = get_config('production')
    print(f"Output directory: {config.OUTPUT_DIR}")
    print(f"Total government scheme URLs: {len(config.GOVERNMENT_SCHEMES_URLS)}")
    print(f"Total weather URLs: {len(config.WEATHER_URLS)}")
    print(f"Total cost URLs: {len(config.COST_URLS)}")
    print(f"Total technical URLs: {len(config.TECHNICAL_URLS)}")
    print(f"Total cities: {len(config.CITIES)}")
    print(f"Total equipment categories: {len(config.EQUIPMENT_CATEGORIES)}")
