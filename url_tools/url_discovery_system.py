#!/usr/bin/env python3
"""
URL Discovery and Deduplication System
Automatically discovers new URLs from seed URLs and updates config.py with unique, accessible links
"""

import requests
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json
import time
from typing import List, Dict, Set, Tuple
import ast
import logging

# Disable SSL warnings for government sites
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class URLDiscoverySystem:
    """Discovers and manages URLs for the scraper configuration"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Keywords for identifying valuable content
        self.content_keywords = {
            'schemes': ['scheme', 'subsidy', 'grant', 'funding', 'financial assistance', 'benefit', 'yojana', 'program'],
            'documents': ['guideline', 'manual', 'notification', 'circular', 'order', 'policy', 'document'],
            'cost': ['rate', 'tariff', 'cost', 'price', 'schedule', 'tender', 'quotation', 'estimate', 'dsr'],
            'technical': ['specification', 'standard', 'procedure', 'design', 'construction', 'technical']
        }
        
        # File extensions that contain structured data
        self.valuable_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.zip']
        
        # Domains to prioritize for internal crawling
        self.priority_domains = ['gov.in', 'nic.in', 'pmksy.gov.in', 'jalshakti-dowr.gov.in', 'cgwb.gov.in']
    
    def load_existing_urls(self, config_file: str = '../config.py') -> Dict[str, Set[str]]:
        """Load existing URLs from config.py"""
        existing_urls = {
            'government_schemes': set(),
            'marketplace': set(),
            'technical_resources': set(),
            'weather': set()
        }
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract URL lists using regex
            patterns = {
                'government_schemes': r'GOVERNMENT_SCHEMES_URLS\s*=\s*\[(.*?)\]',
                'marketplace': r'MARKETPLACE_URLS\s*=\s*\[(.*?)\]',
                'technical_resources': r'TECHNICAL_RESOURCES_URLS\s*=\s*\[(.*?)\]',
                'weather': r'WEATHER_DATA_URLS\s*=\s*\[(.*?)\]'
            }
            
            for category, pattern in patterns.items():
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    urls_text = match.group(1)
                    # Extract URLs from the text
                    url_matches = re.findall(r"'([^']+)'", urls_text)
                    existing_urls[category] = set(url_matches)
            
            logger.info(f"Loaded existing URLs: {sum(len(urls) for urls in existing_urls.values())} total")
            return existing_urls
            
        except Exception as e:
            logger.error(f"Error loading existing URLs: {e}")
            return existing_urls
    
    def crawl_url(self, url: str, max_links: int = 50) -> Dict:
        """Crawl a URL and extract valuable sub-links"""
        result = {
            'url': url,
            'status': 'unknown',
            'accessible': False,
            'content_quality': 0,
            'discovered_links': [],
            'pdf_documents': [],
            'scheme_pages': [],
            'data_pages': [],
            'errors': []
        }
        
        try:
            # Handle government sites with SSL issues
            verify_ssl = not any(domain in url.lower() for domain in ['gov.in', 'nic.in'])
            
            response = self.session.get(url, timeout=15, verify=verify_ssl)
            result['status'] = response.status_code
            
            if response.status_code != 200:
                result['errors'].append(f"HTTP {response.status_code}")
                return result
            
            result['accessible'] = True
            
            # Parse content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove noise
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            text_content = soup.get_text()
            result['content_quality'] = self._assess_content_quality(text_content)
            
            # Extract links
            links = soup.find_all('a', href=True)
            discovered_links = []
            
            for link in links[:max_links]:  # Limit to prevent overwhelming
                href = link.get('href')
                if not href:
                    continue
                
                full_url = urljoin(url, href)
                link_text = link.get_text().strip()
                
                # Skip fragments and external links (except valuable external resources)
                if '#' in href and not self._is_valuable_external(full_url):
                    continue
                
                link_info = {
                    'url': full_url,
                    'title': link_text,
                    'type': self._classify_link(link_text, full_url),
                    'relevance': self._calculate_relevance(link_text, full_url)
                }
                
                discovered_links.append(link_info)
                
                # Categorize by type
                if link_info['type'] == 'pdf':
                    result['pdf_documents'].append(link_info)
                elif link_info['type'] == 'scheme':
                    result['scheme_pages'].append(link_info)
                elif link_info['type'] == 'data':
                    result['data_pages'].append(link_info)
            
            result['discovered_links'] = discovered_links
            
            # Sort by relevance
            for category in ['pdf_documents', 'scheme_pages', 'data_pages']:
                result[category].sort(key=lambda x: x['relevance'], reverse=True)
            
        except Exception as e:
            result['errors'].append(str(e))
            logger.error(f"Error crawling {url}: {e}")
        
        return result
    
    def _assess_content_quality(self, text: str) -> int:
        """Assess content quality based on keywords and structure"""
        score = 0
        
        # Length score
        word_count = len(text.split())
        if word_count > 500: score += 2
        if word_count > 2000: score += 2
        
        # Keyword density
        scheme_mentions = len(re.findall(r'\b(?:scheme|subsidy|grant|funding|yojana)\b', text, re.I))
        cost_mentions = len(re.findall(r'\b(?:₹|rs\.?|rupees?|cost|price|rate|amount)\b', text, re.I))
        technical_mentions = len(re.findall(r'\b(?:guideline|manual|specification|standard)\b', text, re.I))
        
        if scheme_mentions > 5: score += 3
        if cost_mentions > 3: score += 2
        if technical_mentions > 3: score += 2
        
        return score
    
    def _is_valuable_external(self, url: str) -> bool:
        """Check if external URL is valuable (e.g., government resources)"""
        valuable_domains = ['gov.in', 'nic.in', 'imd.gov.in', 'cgwb.gov.in']
        return any(domain in url.lower() for domain in valuable_domains)
    
    def _classify_link(self, link_text: str, url: str) -> str:
        """Classify link type based on text and URL"""
        text_lower = link_text.lower()
        url_lower = url.lower()
        
        # PDF documents
        if any(ext in url_lower for ext in self.valuable_extensions):
            return 'pdf'
        
        # Scheme pages
        if any(keyword in text_lower for keyword in self.content_keywords['schemes']):
            return 'scheme'
        
        # Data/cost pages
        if any(keyword in text_lower for keyword in self.content_keywords['cost']):
            return 'data'
        
        # Technical resources
        if any(keyword in text_lower for keyword in self.content_keywords['technical']):
            return 'technical'
        
        return 'general'
    
    def _calculate_relevance(self, link_text: str, url: str) -> int:
        """Calculate relevance score for a link"""
        score = 0
        text_lower = link_text.lower()
        url_lower = url.lower()
        
        # High-value keywords
        high_value = ['scheme', 'subsidy', 'grant', 'guideline', 'manual', 'pdf', 'document']
        medium_value = ['policy', 'program', 'notification', 'circular', 'rate', 'cost']
        
        for keyword in high_value:
            if keyword in text_lower or keyword in url_lower:
                score += 3
        
        for keyword in medium_value:
            if keyword in text_lower or keyword in url_lower:
                score += 2
        
        # Bonus for government domains
        if any(domain in url_lower for domain in self.priority_domains):
            score += 1
        
        return score
    
    def validate_url_simple(self, url: str) -> bool:
        """Simple URL validation for accessibility"""
        try:
            verify_ssl = not any(domain in url.lower() for domain in ['gov.in', 'nic.in'])
            response = self.session.get(url, timeout=10, verify=verify_ssl)
            return response.status_code == 200
        except:
            return False
    
    def discover_new_urls(self, seed_urls: List[str], existing_urls: Set[str], 
                         min_relevance: int = 2, validate_new: bool = True) -> List[Dict]:
        """Discover new URLs from seed URLs"""
        new_urls = []
        processed_seeds = set()
        
        for seed_url in seed_urls:
            if seed_url in processed_seeds:
                continue
            
            processed_seeds.add(seed_url)
            logger.info(f"Crawling seed URL: {seed_url}")
            
            crawl_result = self.crawl_url(seed_url)
            
            if not crawl_result['accessible']:
                logger.warning(f"Seed URL not accessible: {seed_url}")
                continue
            
            # Process discovered links
            for link_info in crawl_result['discovered_links']:
                link_url = link_info['url']
                
                # Skip if already exists
                if link_url in existing_urls or link_url in [u['url'] for u in new_urls]:
                    continue
                
                # Skip if relevance too low
                if link_info['relevance'] < min_relevance:
                    continue
                
                # Validate if requested
                if validate_new and not self.validate_url_simple(link_url):
                    logger.debug(f"Skipping invalid URL: {link_url}")
                    continue
                
                new_urls.append({
                    'url': link_url,
                    'title': link_info['title'],
                    'type': link_info['type'],
                    'relevance': link_info['relevance'],
                    'source_seed': seed_url
                })
                
                logger.info(f"Found new URL: {link_url} (relevance: {link_info['relevance']})")
            
            time.sleep(2)  # Rate limiting
        
        # Sort by relevance
        new_urls.sort(key=lambda x: x['relevance'], reverse=True)
        return new_urls

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python url_discovery_system.py <seed_url>")
        sys.exit(1)
    
    seed_url = sys.argv[1]
    discovery = URLDiscoverySystem()
    
    print(f"Discovering URLs from: {seed_url}")
    new_urls = discovery.discover_new_urls([seed_url])
    
    print(f"\n🔍 Found {len(new_urls)} new URLs:")
    for url_info in new_urls[:20]:  # Show top 20
        print(f"  • {url_info['title']} (relevance: {url_info['relevance']})")
        print(f"    {url_info['url']}")
        print(f"    Type: {url_info['type']}")
        print()
    
    # Save results
    output_file = f"discovered_urls_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(new_urls, f, indent=2)
    
    print(f"💾 Results saved to: {output_file}")
