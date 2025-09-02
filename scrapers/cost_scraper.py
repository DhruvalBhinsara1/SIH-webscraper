#!/usr/bin/env python3
"""
Cost Scraper Module
Extracts cost and pricing data for rainwater harvesting equipment
"""

import sys
import os
import requests
import time
import logging
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ScraperConfig

logger = logging.getLogger(__name__)

class CostScraper:
    """Cost scraper for rainwater harvesting equipment pricing"""
    
    def __init__(self):
        self.config = ScraperConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_all_cost_data(self) -> List[Dict[str, Any]]:
        """Scrape cost data from multiple sources including expanded URL list"""
        all_cost_data = []
        
        # Scrape from expanded URL list in config
        logger.info(f"Scraping {len(self.config.COST_DATA_URLS)} cost data URLs...")
        for i, url in enumerate(self.config.COST_DATA_URLS, 1):
            try:
                logger.info(f"[{i}/{len(self.config.COST_DATA_URLS)}] Scraping: {url}")
                cost_data = self._scrape_cost_from_url(url)
                all_cost_data.extend(cost_data)
                time.sleep(self.config.RATE_LIMIT_DELAY)
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue
        
        # Add comprehensive cost data from known sources
        cost_sources = [
            self._get_water_tank_costs(),
            self._get_pump_costs(),
            self._get_pipe_costs(),
            self._get_filter_costs(),
            self._get_installation_costs()
        ]
        
        for source_data in cost_sources:
            all_cost_data.extend(source_data)
        
        logger.info(f"Scraped {len(all_cost_data)} cost items")
        return all_cost_data
    
    def _scrape_cost_from_url(self, url: str) -> List[Dict[str, Any]]:
        """Scrape cost data from a specific URL"""
        cost_data = []
        
        try:
            response = self.session.get(url, timeout=30, verify=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text_content = soup.get_text()
                
                # Extract price patterns
                price_patterns = [
                    r'₹\s*[\d,]+(?:\.\d{2})?',
                    r'Rs\.?\s*[\d,]+(?:\.\d{2})?',
                    r'INR\s*[\d,]+(?:\.\d{2})?',
                    r'Price:\s*₹?\s*[\d,]+',
                    r'Cost:\s*₹?\s*[\d,]+'
                ]
                
                found_prices = []
                for pattern in price_patterns:
                    matches = re.findall(pattern, text_content, re.IGNORECASE)
                    found_prices.extend(matches)
                
                if found_prices:
                    cost_data.append({
                        'source_url': url,
                        'source_text': text_content[:500],
                        'prices_found': found_prices[:10],  # Limit to first 10 prices
                        'item_type': 'equipment',
                        'category': 'rainwater_harvesting',
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                
        except Exception as e:
            logger.error(f"Error scraping cost data from {url}: {e}")
        
        return cost_data
    
    def _get_water_tank_costs(self) -> List[Dict[str, Any]]:
        """Get water storage tank costs"""
        return [
            {
                'name': 'PVC Water Tank 500L',
                'price': '₹8,000 - ₹12,000',
                'price_min': 8000,
                'price_max': 12000,
                'supplier': 'Local Manufacturers',
                'category': 'Storage Tank',
                'specifications': '500L capacity, UV resistant, food grade',
                'data_type': 'cost_data'
            },
            {
                'name': 'PVC Water Tank 1000L',
                'price': '₹15,000 - ₹22,000',
                'price_min': 15000,
                'price_max': 22000,
                'supplier': 'Sintex, Supreme, Penguin',
                'category': 'Storage Tank',
                'specifications': '1000L capacity, 3-layer construction',
                'data_type': 'cost_data'
            },
            {
                'name': 'Concrete Water Tank 5000L',
                'price': '₹45,000 - ₹65,000',
                'price_min': 45000,
                'price_max': 65000,
                'supplier': 'Local Contractors',
                'category': 'Storage Tank',
                'specifications': 'RCC construction, underground installation',
                'data_type': 'cost_data'
            }
        ]
    
    def _get_pump_costs(self) -> List[Dict[str, Any]]:
        """Get water pump costs"""
        return [
            {
                'name': 'Submersible Pump 0.5HP',
                'price': '₹3,500 - ₹6,000',
                'price_min': 3500,
                'price_max': 6000,
                'supplier': 'Kirloskar, Crompton, V-Guard',
                'category': 'Water Pump',
                'specifications': '0.5HP, 25mm outlet, 50ft head',
                'data_type': 'cost_data'
            },
            {
                'name': 'Pressure Pump 1HP',
                'price': '₹8,000 - ₹15,000',
                'price_min': 8000,
                'price_max': 15000,
                'supplier': 'Shakti, Kirloskar, CRI',
                'category': 'Water Pump',
                'specifications': '1HP, automatic pressure control',
                'data_type': 'cost_data'
            }
        ]
    
    def _get_pipe_costs(self) -> List[Dict[str, Any]]:
        """Get piping system costs"""
        return [
            {
                'name': 'PVC Pipe 4 inch (per meter)',
                'price': '₹180 - ₹250',
                'price_min': 180,
                'price_max': 250,
                'supplier': 'Finolex, Supreme, Astral',
                'category': 'Piping',
                'specifications': '4 inch diameter, ISI marked',
                'data_type': 'cost_data'
            },
            {
                'name': 'Drip Irrigation Kit (1 acre)',
                'price': '₹25,000 - ₹40,000',
                'price_min': 25000,
                'price_max': 40000,
                'supplier': 'Netafim, Jain Irrigation, Rain Bird',
                'category': 'Irrigation',
                'specifications': 'Complete drip system with timers',
                'data_type': 'cost_data'
            }
        ]
    
    def _get_filter_costs(self) -> List[Dict[str, Any]]:
        """Get water filtration costs"""
        return [
            {
                'name': 'First Flush Diverter',
                'price': '₹2,500 - ₹4,500',
                'price_min': 2500,
                'price_max': 4500,
                'supplier': 'Local Fabricators',
                'category': 'Filtration',
                'specifications': 'Automatic first flush diversion',
                'data_type': 'cost_data'
            },
            {
                'name': 'Sand & Gravel Filter',
                'price': '₹8,000 - ₹15,000',
                'price_min': 8000,
                'price_max': 15000,
                'supplier': 'Water Treatment Companies',
                'category': 'Filtration',
                'specifications': 'Multi-stage filtration system',
                'data_type': 'cost_data'
            }
        ]
    
    def _get_installation_costs(self) -> List[Dict[str, Any]]:
        """Get installation and labor costs"""
        return [
            {
                'name': 'Rooftop RWH System Installation',
                'price': '₹15,000 - ₹35,000',
                'price_min': 15000,
                'price_max': 35000,
                'supplier': 'RWH Contractors',
                'category': 'Installation',
                'specifications': 'Complete rooftop system setup',
                'data_type': 'cost_data'
            },
            {
                'name': 'Borewell Recharge System',
                'price': '₹25,000 - ₹50,000',
                'price_min': 25000,
                'price_max': 50000,
                'supplier': 'Groundwater Specialists',
                'category': 'Installation',
                'specifications': 'Recharge pit with filtration',
                'data_type': 'cost_data'
            }
        ]
    
    def scrape_marketplace_data(self):
        """Scrape marketplace data (placeholder for future enhancement)"""
        # Future: Scrape from IndiaMART, TradeIndia, etc.
        return []

if __name__ == "__main__":
    scraper = CostScraper()
    data = scraper.scrape_all_cost_data()
    print(f"Scraped {len(data)} cost entries")
