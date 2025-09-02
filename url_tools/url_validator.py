#!/usr/bin/env python3
"""
URL Validator and Link Discovery System
Validates URLs and discovers data-containing sub-pages
"""

import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import time
from typing import List, Dict, Set, Tuple
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class URLValidator:
    """Validates URLs and discovers data-containing pages"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Keywords that indicate data-containing pages
        self.data_keywords = {
            'schemes': ['scheme', 'subsidy', 'grant', 'funding', 'financial', 'benefit', 'amount', 'cost', 'price', 'rate', 'tariff'],
            'cost': ['price', 'cost', 'rate', 'tariff', 'schedule', 'dsr', 'tender', 'quotation', 'estimate'],
            'technical': ['guideline', 'manual', 'specification', 'standard', 'procedure', 'technical', 'design'],
            'weather': ['rainfall', 'weather', 'forecast', 'precipitation', 'monsoon', 'climate']
        }
        
        # File extensions that likely contain structured data
        self.data_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv']
    
    def validate_url(self, url: str) -> Tuple[bool, str, List[str]]:
        """Validate URL and return status, content type, and discovered links"""
        try:
            # Handle government sites with SSL issues
            verify_ssl = not any(domain in url.lower() for domain in ['gov.in', 'nic.in'])
            
            response = self.session.get(url, timeout=15, verify=verify_ssl)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            
            # If it's HTML, discover links
            discovered_links = []
            if 'text/html' in content_type:
                discovered_links = self.discover_data_links(response.text, url)
            
            return True, content_type, discovered_links
            
        except Exception as e:
            logger.warning(f"URL validation failed for {url}: {str(e)}")
            return False, str(e), []
    
    def discover_data_links(self, html_content: str, base_url: str) -> List[str]:
        """Discover links that likely contain actual data"""
        soup = BeautifulSoup(html_content, 'html.parser')
        data_links = []
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href')
            if not href:
                continue
            
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, href)
            
            # Check if link text or URL contains data indicators
            link_text = link.get_text().lower()
            url_lower = full_url.lower()
            
            # Check for document files
            if any(ext in url_lower for ext in self.data_extensions):
                data_links.append(full_url)
                continue
            
            # Check for data-related keywords in link text or URL
            for category, keywords in self.data_keywords.items():
                if any(keyword in link_text or keyword in url_lower for keyword in keywords):
                    data_links.append(full_url)
                    break
        
        # Remove duplicates and sort
        return sorted(list(set(data_links)))
    
    def analyze_page_content(self, url: str) -> Dict[str, any]:
        """Analyze page content to determine data quality"""
        try:
            verify_ssl = not any(domain in url.lower() for domain in ['gov.in', 'nic.in'])
            response = self.session.get(url, timeout=15, verify=verify_ssl)
            response.raise_for_status()
            
            if 'text/html' in response.headers.get('content-type', ''):
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove scripts and styles
                for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                    element.decompose()
                
                text_content = soup.get_text()
                
                # Analyze content quality
                analysis = {
                    'url': url,
                    'word_count': len(text_content.split()),
                    'has_tables': len(soup.find_all('table')) > 0,
                    'has_forms': len(soup.find_all('form')) > 0,
                    'has_downloads': len(soup.find_all('a', href=re.compile(r'\.(pdf|doc|xls)', re.I))) > 0,
                    'scheme_mentions': len(re.findall(r'\b(?:scheme|subsidy|grant|funding)\b', text_content, re.I)),
                    'cost_mentions': len(re.findall(r'\b(?:₹|rs\.?|rupees?|cost|price|rate)\b', text_content, re.I)),
                    'data_score': 0
                }
                
                # Calculate data score
                score = 0
                if analysis['word_count'] > 500: score += 2
                if analysis['has_tables']: score += 3
                if analysis['has_downloads']: score += 4
                if analysis['scheme_mentions'] > 5: score += 3
                if analysis['cost_mentions'] > 3: score += 2
                
                analysis['data_score'] = score
                return analysis
                
        except Exception as e:
            return {'url': url, 'error': str(e), 'data_score': 0}
    
    def validate_category_urls(self, urls: List[str], category: str) -> Dict[str, any]:
        """Validate all URLs in a category and discover better alternatives"""
        results = {
            'valid_urls': [],
            'invalid_urls': [],
            'discovered_links': [],
            'high_quality_pages': []
        }
        
        logger.info(f"Validating {len(urls)} URLs for category: {category}")
        
        for url in urls:
            logger.info(f"Checking: {url}")
            
            is_valid, status, discovered = self.validate_url(url)
            
            if is_valid:
                results['valid_urls'].append(url)
                results['discovered_links'].extend(discovered)
                
                # Analyze content quality
                analysis = self.analyze_page_content(url)
                if analysis.get('data_score', 0) >= 5:
                    results['high_quality_pages'].append(analysis)
                
            else:
                results['invalid_urls'].append({'url': url, 'error': status})
            
            time.sleep(2)  # Rate limiting
        
        # Remove duplicate discovered links
        results['discovered_links'] = list(set(results['discovered_links']))
        
        logger.info(f"Category {category} results:")
        logger.info(f"  Valid: {len(results['valid_urls'])}")
        logger.info(f"  Invalid: {len(results['invalid_urls'])}")
        logger.info(f"  Discovered: {len(results['discovered_links'])}")
        logger.info(f"  High Quality: {len(results['high_quality_pages'])}")
        
        return results
