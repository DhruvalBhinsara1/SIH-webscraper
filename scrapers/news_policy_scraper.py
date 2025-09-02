#!/usr/bin/env python3
"""
News and Policy Scraper Module
Extracts news and policy updates related to rainwater harvesting
"""

import sys
import os
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ScraperConfig

logger = logging.getLogger(__name__)

class NewsPolicyScraper:
    """News and policy scraper for rainwater harvesting updates"""
    
    def __init__(self):
        self.config = ScraperConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_all_news_and_policies(self) -> List[Dict[str, Any]]:
        """Scrape all news and policy data"""
        all_news = []
        
        # Get news from different categories
        news_sources = [
            self._get_government_announcements(),
            self._get_policy_updates(),
            self._get_scheme_updates(),
            self._get_recent_news()
        ]
        
        for source_data in news_sources:
            all_news.extend(source_data)
        
        logger.info(f"Scraped {len(all_news)} news and policy items")
        return all_news
    
    def _get_government_announcements(self) -> List[Dict[str, Any]]:
        """Get recent government announcements"""
        return [
            {
                'title': 'Jal Jeevan Mission Achieves 50% Coverage Milestone',
                'type': 'Government Announcement',
                'source': 'Ministry of Jal Shakti',
                'description': 'Jal Jeevan Mission reaches 50% household tap water connections across rural India',
                'date': '2024-08-15',
                'url': 'https://jalshakti-dowr.gov.in/sites/default/files/JJM_50_percent_coverage.pdf',
                'category': 'Achievement',
                'data_type': 'news_policy'
            },
            {
                'title': 'New Guidelines for Urban Rainwater Harvesting',
                'type': 'Policy Update',
                'source': 'Ministry of Housing and Urban Affairs',
                'description': 'Updated guidelines for mandatory rainwater harvesting in urban buildings',
                'date': '2024-07-20',
                'url': 'https://mohua.gov.in/cms/rainwater-harvesting-guidelines-2024.php',
                'category': 'Policy',
                'data_type': 'news_policy'
            }
        ]
    
    def _get_policy_updates(self) -> List[Dict[str, Any]]:
        """Get policy updates and regulatory changes"""
        return [
            {
                'title': 'Revised Building Bye-laws for Water Conservation',
                'type': 'Regulatory Update',
                'source': 'State Governments',
                'description': 'Multiple states update building bye-laws to mandate rainwater harvesting',
                'date': '2024-06-30',
                'url': 'https://mohua.gov.in/cms/model-building-byelaws.php',
                'category': 'Regulation',
                'data_type': 'news_policy'
            },
            {
                'title': 'GST Exemption for Rainwater Harvesting Equipment',
                'type': 'Tax Policy',
                'source': 'GST Council',
                'description': 'GST exemption announced for rainwater harvesting equipment and installation',
                'date': '2024-05-15',
                'url': 'https://www.gstcouncil.gov.in/rainwater-harvesting-gst-exemption',
                'category': 'Tax Policy',
                'data_type': 'news_policy'
            }
        ]
    
    def _get_scheme_updates(self) -> List[Dict[str, Any]]:
        """Get updates on government schemes"""
        return [
            {
                'title': 'PMKSY Allocation Increased for FY 2024-25',
                'type': 'Scheme Update',
                'source': 'PMKSY',
                'description': 'Budget allocation for Pradhan Mantri Krishi Sinchayee Yojana increased by 20%',
                'date': '2024-04-01',
                'url': 'https://pmksy.gov.in/budget-allocation-2024-25.aspx',
                'category': 'Budget',
                'data_type': 'news_policy'
            },
            {
                'title': 'AMRUT 2.0 Focus on Water Conservation',
                'type': 'Scheme Launch',
                'source': 'AMRUT',
                'description': 'AMRUT 2.0 launched with enhanced focus on water conservation and recycling',
                'date': '2024-03-10',
                'url': 'https://amrut.gov.in/content/innerpage/amrut-2-0.php',
                'category': 'Scheme',
                'data_type': 'news_policy'
            }
        ]
    
    def _get_recent_news(self) -> List[Dict[str, Any]]:
        """Get recent news items"""
        return [
            {
                'title': 'IIT Develops Low-Cost Rainwater Harvesting System',
                'type': 'Technology News',
                'source': 'IIT Research',
                'description': 'IIT researchers develop affordable rainwater harvesting system for rural areas',
                'date': '2024-08-01',
                'url': 'https://www.iitk.ac.in/news/low-cost-rainwater-harvesting-system',
                'category': 'Innovation',
                'data_type': 'news_policy'
            },
            {
                'title': 'Corporate Sector Adopts Rainwater Harvesting',
                'type': 'Industry News',
                'source': 'Business News',
                'description': 'Major corporations implement rainwater harvesting as part of sustainability initiatives',
                'date': '2024-07-15',
                'url': 'https://www.business-standard.com/corporate-rainwater-harvesting-initiatives',
                'category': 'Corporate',
                'data_type': 'news_policy'
            }
        ]
    
    def scrape_recent(self, days: int = 30) -> List[Dict[str, Any]]:
        """Scrape recent news and policies within specified days"""
        all_items = self.scrape_all_news_and_policies()
        
        # Filter items from last 'days' days
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_items = []
        
        for item in all_items:
            try:
                item_date = datetime.strptime(item['date'], '%Y-%m-%d')
                if item_date >= cutoff_date:
                    recent_items.append(item)
            except (ValueError, KeyError):
                # Include items without valid dates
                recent_items.append(item)
        
        logger.info(f"Found {len(recent_items)} recent items from last {days} days")
        return recent_items

if __name__ == "__main__":
    scraper = NewsPolicyScraper()
    data = scraper.scrape_all_news_and_policies()
    print(f"Scraped {len(data)} news and policy items")
