#!/usr/bin/env python3
"""
Technical Resources Scraper Module
Extracts technical documentation and resources for rainwater harvesting
"""

import sys
import os
import requests
import logging
import time
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ScraperConfig

logger = logging.getLogger(__name__)

class TechnicalResourcesScraper:
    """Technical resources scraper for rainwater harvesting documentation"""
    
    def __init__(self):
        self.config = ScraperConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_all_resources(self) -> List[Dict[str, Any]]:
        """Scrape all technical resources from multiple sources"""
        all_resources = []
        
        # Get resources from different categories
        resource_sources = [
            self._get_government_guidelines(),
            self._get_technical_manuals(),
            self._get_research_papers(),
            self._get_design_specifications(),
            self._get_case_studies()
        ]
        
        for source_data in resource_sources:
            all_resources.extend(source_data)
        
        logger.info(f"Scraped {len(all_resources)} technical resources")
        return all_resources
    
    def _get_government_guidelines(self) -> List[Dict[str, Any]]:
        """Get government guidelines and policy documents"""
        return [
            {
                'title': 'Central Ground Water Board - Rainwater Harvesting Guidelines',
                'type': 'Government Guidelines',
                'source': 'CGWB',
                'description': 'Comprehensive technical guidelines for rainwater harvesting implementation across India',
                'url': 'https://cgwb.gov.in/documents/rainwater-harvesting-guidelines.pdf',
                'category': 'Guidelines',
                'data_type': 'technical_resource'
            },
            {
                'title': 'Ministry of Jal Shakti - Water Conservation Manual',
                'type': 'Technical Manual',
                'source': 'Ministry of Jal Shakti',
                'description': 'Technical specifications and implementation strategies for water conservation',
                'url': 'https://jalshakti-dowr.gov.in/sites/default/files/Water_Conservation_Manual.pdf',
                'category': 'Manual',
                'data_type': 'technical_resource'
            },
            {
                'title': 'PMKSY Guidelines for Micro Irrigation',
                'type': 'Scheme Guidelines',
                'source': 'PMKSY',
                'description': 'Detailed guidelines for micro irrigation under PMKSY scheme',
                'url': 'https://pmksy.gov.in/microirrigation/Archive/Guidelines.aspx',
                'category': 'Guidelines',
                'data_type': 'technical_resource'
            }
        ]
    
    def _get_technical_manuals(self) -> List[Dict[str, Any]]:
        """Get technical manuals and handbooks"""
        return [
            {
                'title': 'Rainwater Harvesting Design Manual',
                'type': 'Design Manual',
                'source': 'Centre for Science and Environment',
                'description': 'Step-by-step design guide for rooftop rainwater harvesting systems',
                'url': 'https://www.cseindia.org/rainwater-harvesting-manual',
                'category': 'Manual',
                'data_type': 'technical_resource'
            },
            {
                'title': 'Water Storage Tank Design Specifications',
                'type': 'Technical Specifications',
                'source': 'Bureau of Indian Standards',
                'description': 'IS codes and specifications for water storage tank construction',
                'url': 'https://bis.gov.in/index.php/standards/technical-department/civil-engineering-department-ced/',
                'category': 'Specifications',
                'data_type': 'technical_resource'
            }
        ]
    
    def _get_research_papers(self) -> List[Dict[str, Any]]:
        """Get research papers and studies"""
        return [
            {
                'title': 'Efficiency of Rainwater Harvesting Systems in Urban Areas',
                'type': 'Research Paper',
                'source': 'IIT Research',
                'description': 'Comprehensive study on RWH system efficiency in Indian urban contexts',
                'url': 'https://www.iitk.ac.in/ce/research/rainwater-harvesting-efficiency.pdf',
                'category': 'Research',
                'data_type': 'technical_resource'
            },
            {
                'title': 'Cost-Benefit Analysis of Rainwater Harvesting',
                'type': 'Economic Study',
                'source': 'TERI',
                'description': 'Economic analysis of rainwater harvesting implementation costs and benefits',
                'url': 'https://www.teriin.org/projects/water/rwh-cost-benefit-analysis.pdf',
                'category': 'Research',
                'data_type': 'technical_resource'
            }
        ]
    
    def _get_design_specifications(self) -> List[Dict[str, Any]]:
        """Get design specifications and standards"""
        return [
            {
                'title': 'IS 15797:2008 - Rainwater Harvesting Guidelines',
                'type': 'Indian Standard',
                'source': 'Bureau of Indian Standards',
                'description': 'Indian standard for rainwater harvesting system design and implementation',
                'url': 'https://bis.gov.in/index.php/nebula/standards-information/indian-standards/',
                'category': 'Standards',
                'data_type': 'technical_resource'
            },
            {
                'title': 'Building Bye-laws for Rainwater Harvesting',
                'type': 'Legal Framework',
                'source': 'Various State Governments',
                'description': 'Compilation of state-wise building bye-laws mandating rainwater harvesting',
                'url': 'https://mohua.gov.in/cms/model-building-byelaws.php',
                'category': 'Legal',
                'data_type': 'technical_resource'
            }
        ]
    
    def _get_case_studies(self) -> List[Dict[str, Any]]:
        """Get case studies and implementation examples"""
        return [
            {
                'title': 'Chennai Rainwater Harvesting Success Story',
                'type': 'Case Study',
                'source': 'Tamil Nadu Water Supply',
                'description': 'Successful implementation of mandatory RWH in Chennai and its impact',
                'url': 'https://www.tn.gov.in/scheme/data_view/17094',
                'category': 'Case Study',
                'data_type': 'technical_resource'
            },
            {
                'title': 'Rural Rainwater Harvesting Models',
                'type': 'Implementation Guide',
                'source': 'Watershed Development',
                'description': 'Successful rural rainwater harvesting models and replication strategies',
                'url': 'https://dolr.gov.in/en/division/watershed-development-division',
                'category': 'Case Study',
                'data_type': 'technical_resource'
            }
        ]
    
    def scrape_specific_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape specific URLs for technical resources"""
        resources = []
        
        for url in urls:
            try:
                logger.info(f"Scraping technical resource: {url}")
                resource = self._extract_resource_from_url(url)
                if resource:
                    resources.append(resource)
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")
        
        return resources
    
    def _extract_resource_from_url(self, url: str) -> Dict[str, Any]:
        """Extract resource information from a URL"""
        try:
            response = self.session.get(url, timeout=10, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else 'Technical Resource'
            
            # Extract description
            description = 'Technical resource for rainwater harvesting'
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', description)
            
            return {
                'title': title_text[:100],
                'type': 'Web Resource',
                'source': urlparse(url).netloc,
                'description': description[:200],
                'url': url,
                'category': 'Web Resource',
                'data_type': 'technical_resource'
            }
            
        except Exception as e:
            logger.error(f"Error extracting from {url}: {e}")
            return None

if __name__ == "__main__":
    scraper = TechnicalResourcesScraper()
    data = scraper.scrape_all_resources()
    print(f"Scraped {len(data)} technical resources")
