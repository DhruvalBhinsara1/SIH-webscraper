#!/usr/bin/env python3
"""
Government Schemes Scraper for Jal Setu
Scrapes government portals for rainwater harvesting schemes and subsidies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from typing import List, Dict, Any
import logging
from config import ScraperConfig
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GovernmentSchemesScraper:
    """Scrapes government schemes and policy data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.config = ScraperConfig()
    
    def scrape_all_schemes(self):
        """Scrape all government schemes with deduplication"""
        all_schemes = []
        seen_hashes = set()
        seen_names = set()
        
        # Use expanded URL list from config
        urls_to_scrape = self.config.GOVERNMENT_SCHEMES_URLS
        logger.info(f"Scraping {len(urls_to_scrape)} government URLs...")
        
        for i, url in enumerate(urls_to_scrape, 1):
            try:
                logger.info(f"[{i}/{len(urls_to_scrape)}] Scraping: {url}")
                schemes = self.scrape_schemes_from_url(url)
                
                # Deduplicate schemes
                unique_schemes = []
                for scheme in schemes:
                    content_hash = scheme.get('content_hash', hash(scheme['name']) % 10000)
                    name_key = scheme['name'].lower().strip()
                    
                    if content_hash not in seen_hashes and name_key not in seen_names:
                        unique_schemes.append(scheme)
                        seen_hashes.add(content_hash)
                        seen_names.add(name_key)
                
                all_schemes.extend(unique_schemes)
                logger.info(f"  → Found {len(schemes)} schemes, {len(unique_schemes)} unique")
                
                # Rate limiting
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.warning("Scraping interrupted by user")
                break
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {type(e).__name__}: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(all_schemes)} unique government schemes from {len(urls_to_scrape)} URLs")
        return all_schemes
    
    def scrape_schemes_from_url(self, url: str) -> List[Dict[str, Any]]:
        """Scrape schemes from a single government portal"""
        schemes = []
        
        try:
            # Skip PDF files - they need special handling
            if url.lower().endswith('.pdf'):
                logger.info(f"Skipping PDF file: {url}")
                return [{
                    'name': f'PDF Document: {url.split("/")[-1]}',
                    'description': 'Government document - requires PDF parsing',
                    'source_url': url,
                    'data_type': 'government_document'
                }]
            
            # Fetch page content with better error handling
            logger.debug(f"Fetching content from: {url}")
            response = self.session.get(
                url, 
                timeout=15, 
                verify=False,
                headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
            )
            response.raise_for_status()
            
            # Handle encoding issues
            if response.encoding is None:
                response.encoding = 'utf-8'
            
            content = response.text
            logger.debug(f"Successfully fetched {len(content)} characters from {url}")
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout while fetching {url}")
            return schemes
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error for {url}")
            return schemes
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error {e.response.status_code} for {url}")
            return schemes
        except UnicodeDecodeError:
            logger.warning(f"Encoding error for {url} - skipping")
            return schemes
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {type(e).__name__}: {e}")
            return schemes
        
        # Extract schemes from main page
        try:
            main_schemes = self._extract_schemes_from_content(content, url)
            schemes.extend(main_schemes)
            logger.debug(f"Extracted {len(main_schemes)} schemes from {url}")
        except Exception as e:
            logger.error(f"Error extracting schemes from {url}: {type(e).__name__}: {e}")
        
        # Add domain-specific fallback scheme if none found
        if not schemes:
            domain = url.split('/')[2] if '/' in url else url
            
            # Create domain-specific schemes
            if 'pmksy' in domain:
                schemes = [{
                    'name': 'Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)',
                    'description': 'Comprehensive irrigation program focusing on micro irrigation and water use efficiency',
                    'category': 'pmksy',
                    'source_url': url,
                    'data_type': 'government_scheme',
                    'extraction_method': 'domain_fallback'
                }]
            elif 'jalshakti' in domain:
                schemes = [{
                    'name': 'Jal Shakti Ministry Initiatives',
                    'description': 'Water resource management and conservation programs',
                    'category': 'jal_shakti',
                    'source_url': url,
                    'data_type': 'government_scheme',
                    'extraction_method': 'domain_fallback'
                }]
            elif 'mowr' in domain:
                schemes = [{
                    'name': 'Ministry of Water Resources Programs',
                    'description': 'National water policy and irrigation development schemes',
                    'category': 'watershed',
                    'source_url': url,
                    'data_type': 'government_scheme',
                    'extraction_method': 'domain_fallback'
                }]
            else:
                schemes = [{
                    'name': f'Water Conservation Initiative - {domain}',
                    'description': 'Government water conservation and management program',
                    'category': 'general',
                    'source_url': url,
                    'data_type': 'government_scheme',
                    'extraction_method': 'domain_fallback'
                }]
            
            logger.info(f"No schemes extracted from {url}, added domain-specific fallback scheme")
        
        return schemes
    
    def _filter_scheme_links(self, links: List[str]) -> List[str]:
        """Filter links that are likely to contain scheme information"""
        scheme_keywords = [
            'scheme', 'yojana', 'program', 'subsidy', 'grant', 'policy',
            'rainwater', 'harvesting', 'water', 'irrigation', 'watershed',
            'pmksy', 'jal', 'shakti', 'amrut', 'mission'
        ]
        
        filtered_links = []
        for link in links:
            link_lower = link.lower()
            if any(keyword in link_lower for keyword in scheme_keywords):
                filtered_links.append(link)
        
        return filtered_links
    
    def _extract_schemes_from_content(self, content: str, source_url: str) -> List[Dict[str, Any]]:
        """Extract scheme information from page content"""
        schemes = []
        
        try:
            # Use lxml parser if available, fallback to html.parser
            try:
                soup = BeautifulSoup(content, 'lxml')
            except:
                soup = BeautifulSoup(content, 'html.parser')
            
            # Enhanced scheme detection patterns
            scheme_patterns = {
                'pmksy': ['pradhan mantri krishi sinchayee yojana', 'pmksy', 'micro irrigation'],
                'jal_shakti': ['jal shakti', 'jal jeevan mission', 'har ghar jal'],
                'amrut': ['amrut', 'atal mission', 'urban transformation'],
                'swachh_bharat': ['swachh bharat', 'clean india', 'sanitation'],
                'rainwater': ['rainwater harvesting', 'roof top', 'water conservation'],
                'watershed': ['watershed', 'nrega', 'mgnrega', 'rural development'],
                'subsidy': ['subsidy', 'financial assistance', 'grant', 'funding']
            }
            
            # Look for specific scheme elements
            unique_schemes = set()
            
            # 1. Extract from titles and headings
            for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'title']):
                text = element.get_text().strip()
                scheme = self._create_scheme_from_text(text, source_url, 'heading', scheme_patterns)
                if scheme and scheme['name'] not in unique_schemes:
                    schemes.append(scheme)
                    unique_schemes.add(scheme['name'])
            
            # 2. Extract from structured content (tables, lists)
            for element in soup.find_all(['td', 'li', 'span']):
                text = element.get_text().strip()
                if len(text) > 30 and len(text) < 200:
                    scheme = self._create_scheme_from_text(text, source_url, 'structured', scheme_patterns)
                    if scheme and scheme['name'] not in unique_schemes:
                        schemes.append(scheme)
                        unique_schemes.add(scheme['name'])
                        
                    if len(schemes) >= 5:  # Limit per page
                        break
            
            # 3. Extract from paragraphs (last resort)
            if len(schemes) < 2:
                for element in soup.find_all(['p', 'div']):
                    text = element.get_text().strip()
                    if len(text) > 50 and len(text) < 300:
                        scheme = self._create_scheme_from_text(text, source_url, 'paragraph', scheme_patterns)
                        if scheme and scheme['name'] not in unique_schemes:
                            schemes.append(scheme)
                            unique_schemes.add(scheme['name'])
                            
                        if len(schemes) >= 3:
                            break
        
        except Exception as e:
            logger.warning(f"Failed to extract schemes from {source_url}: {type(e).__name__}: {e}")
        
        return schemes
    
    def _create_scheme_from_text(self, text: str, source_url: str, extraction_type: str, scheme_patterns: dict) -> dict:
        """Create a scheme object from extracted text"""
        text_lower = text.lower()
        
        # Check if text matches any scheme patterns
        matched_category = None
        for category, patterns in scheme_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                matched_category = category
                break
        
        if not matched_category:
            return None
        
        # Clean up the text
        clean_text = re.sub(r'\s+', ' ', text).strip()
        
        # Generate unique name based on content
        name = clean_text[:80]
        if len(name) < 20:
            return None
        
        # Create enhanced scheme data
        scheme = {
            'name': name,
            'description': clean_text[:250],
            'category': matched_category,
            'source_url': source_url,
            'data_type': 'government_scheme',
            'extraction_method': extraction_type,
            'content_hash': hash(clean_text) % 10000  # For deduplication
        }
        
        return scheme
    
    def _enhance_scheme_data(self, scheme: Dict[str, Any], html_content: str):
        """Enhance scheme data with additional extracted information"""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract document links (PDFs, DOCs)
            doc_links = []
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                if any(ext in href for ext in ['.pdf', '.doc', '.docx']):
                    doc_links.append({
                        'url': link['href'],
                        'text': link.get_text().strip()
                    })
            if doc_links:
                scheme['documents'] = doc_links[:5]  # Limit to 5 documents
                
        except Exception as e:
            logger.warning(f"Failed to enhance scheme data: {e}")
    
    def scrape_state_specific_schemes(self, state_name: str) -> List[Dict[str, Any]]:
        """Scrape schemes specific to a particular state"""
        logger.info(f"Scraping schemes for state: {state_name}")
        
        # Use state URLs from config based on state name
        state_urls = []
        state_lower = state_name.lower().replace(' ', '_')
        
        # Filter URLs from config based on state
        for url in self.config.GOVERNMENT_SCHEMES_URLS:
            if any(state in url.lower() for state in [state_lower, state_name.lower()]):
                state_urls.append(url)
        
        all_schemes = []
        for url in state_urls:
            try:
                schemes = self.scrape_schemes_from_url(url)
                # Add state information
                for scheme in schemes:
                    scheme['state'] = state_name
                    scheme['regional_scheme'] = True
                all_schemes.extend(schemes)
            except Exception as e:
                logger.error(f"Failed to scrape state portal {url}: {e}")
        
        return all_schemes
    
    def scrape_central_schemes(self) -> List[Dict[str, Any]]:
        """Scrape central government schemes"""
        logger.info("Scraping central government schemes")
        
        # Use central government URLs from config
        central_urls = [url for url in self.config.GOVERNMENT_SCHEMES_URLS if 'pmksy' in url or 'atal-bhujal' in url or 'jalshakti' in url or 'india.gov.in' in url]
        
        all_schemes = []
        for url in central_urls:
            try:
                schemes = self.scrape_schemes_from_url(url)
                # Mark as central schemes
                for scheme in schemes:
                    scheme['scheme_level'] = 'central'
                    scheme['implementing_ministry'] = self._identify_ministry(url)
                all_schemes.extend(schemes)
            except Exception as e:
                logger.error(f"Failed to scrape central portal {url}: {e}")
        
        return all_schemes
    
    def _identify_ministry(self, url: str) -> str:
        """Identify implementing ministry from URL"""
        if 'jalshakti' in url:
            return 'Ministry of Jal Shakti'
        elif 'pmksy' in url:
            return 'Ministry of Agriculture and Farmers Welfare'
        elif 'atal-bhujal' in url:
            return 'Ministry of Jal Shakti'
        else:
            return 'Central Government'

if __name__ == "__main__":
    # Test the government schemes scraper
    scraper = GovernmentSchemesScraper()
    
    try:
        # Scrape all government schemes
        schemes = scraper.scrape_all_schemes()
        print(f"Successfully scraped {len(schemes)} government schemes")
        
        # Display sample scheme
        if schemes:
            print("\nSample scheme:")
            print(json.dumps(schemes[0], indent=2, ensure_ascii=False))
            
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
    finally:
        pass  # No cleanup needed
