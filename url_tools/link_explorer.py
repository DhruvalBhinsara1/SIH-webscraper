#!/usr/bin/env python3
"""
Link Explorer - Discovers actual data-containing pages from government websites
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json
import time
from typing import List, Dict, Tuple

class LinkExplorer:
    """Explores websites to find actual data-containing pages"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Keywords that indicate valuable content
        self.valuable_keywords = {
            'schemes': ['scheme', 'subsidy', 'grant', 'funding', 'financial assistance', 'benefit', 'eligibility', 'application'],
            'documents': ['guideline', 'manual', 'notification', 'circular', 'order', 'resolution', 'policy'],
            'cost': ['rate', 'tariff', 'cost', 'price', 'schedule', 'tender', 'quotation', 'estimate'],
            'technical': ['specification', 'standard', 'procedure', 'design', 'construction', 'implementation']
        }
    
    def explore_page(self, url: str, max_depth: int = 2) -> Dict:
        """Explore a page and find valuable sub-links"""
        results = {
            'url': url,
            'status': 'unknown',
            'content_quality': 0,
            'pdf_documents': [],
            'scheme_pages': [],
            'data_pages': [],
            'errors': []
        }
        
        try:
            # Get main page
            verify_ssl = not any(domain in url.lower() for domain in ['gov.in', 'nic.in'])
            response = self.session.get(url, timeout=15, verify=verify_ssl)
            
            if response.status_code != 200:
                results['status'] = f'HTTP {response.status_code}'
                return results
            
            results['status'] = 'success'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Analyze main page content
            text_content = soup.get_text()
            results['content_quality'] = self._assess_content_quality(text_content)
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href')
                if not href:
                    continue
                
                full_url = urljoin(url, href)
                link_text = link.get_text().strip()
                
                # Skip external links and fragments
                if not self._is_same_domain(url, full_url) or '#' in href:
                    continue
                
                # Categorize links
                if self._is_pdf_document(full_url):
                    results['pdf_documents'].append({
                        'url': full_url,
                        'title': link_text,
                        'relevance': self._calculate_relevance(link_text, 'documents')
                    })
                
                elif self._is_scheme_page(link_text, full_url):
                    results['scheme_pages'].append({
                        'url': full_url,
                        'title': link_text,
                        'relevance': self._calculate_relevance(link_text, 'schemes')
                    })
                
                elif self._is_data_page(link_text, full_url):
                    results['data_pages'].append({
                        'url': full_url,
                        'title': link_text,
                        'relevance': self._calculate_relevance(link_text, 'cost')
                    })
            
            # Sort by relevance
            results['pdf_documents'].sort(key=lambda x: x['relevance'], reverse=True)
            results['scheme_pages'].sort(key=lambda x: x['relevance'], reverse=True)
            results['data_pages'].sort(key=lambda x: x['relevance'], reverse=True)
            
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(str(e))
        
        return results
    
    def _assess_content_quality(self, text: str) -> int:
        """Assess content quality based on keywords and structure"""
        score = 0
        
        # Length score
        if len(text) > 1000: score += 2
        if len(text) > 5000: score += 2
        
        # Keyword density
        scheme_mentions = len(re.findall(r'\b(?:scheme|subsidy|grant|funding)\b', text, re.I))
        cost_mentions = len(re.findall(r'\b(?:₹|rs\.?|rupees?|cost|price|rate)\b', text, re.I))
        
        if scheme_mentions > 5: score += 3
        if cost_mentions > 3: score += 2
        
        return score
    
    def _is_same_domain(self, base_url: str, check_url: str) -> bool:
        """Check if URLs are from same domain"""
        try:
            base_domain = urlparse(base_url).netloc
            check_domain = urlparse(check_url).netloc
            return base_domain == check_domain
        except:
            return False
    
    def _is_pdf_document(self, url: str) -> bool:
        """Check if URL points to a PDF document"""
        return '.pdf' in url.lower()
    
    def _is_scheme_page(self, link_text: str, url: str) -> bool:
        """Check if link is likely a scheme page"""
        text_lower = link_text.lower()
        url_lower = url.lower()
        
        scheme_indicators = ['scheme', 'subsidy', 'grant', 'program', 'policy', 'benefit']
        return any(indicator in text_lower or indicator in url_lower for indicator in scheme_indicators)
    
    def _is_data_page(self, link_text: str, url: str) -> bool:
        """Check if link is likely a data/cost page"""
        text_lower = link_text.lower()
        url_lower = url.lower()
        
        data_indicators = ['rate', 'tariff', 'cost', 'price', 'schedule', 'data', 'statistics']
        return any(indicator in text_lower or indicator in url_lower for indicator in data_indicators)
    
    def _calculate_relevance(self, text: str, category: str) -> int:
        """Calculate relevance score for a link"""
        text_lower = text.lower()
        keywords = self.valuable_keywords.get(category, [])
        
        score = 0
        for keyword in keywords:
            if keyword in text_lower:
                score += 1
        
        return score

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python link_explorer.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    explorer = LinkExplorer()
    
    print(f"Exploring: {url}")
    results = explorer.explore_page(url)
    
    print(f"\nStatus: {results['status']}")
    print(f"Content Quality: {results['content_quality']}")
    
    if results['pdf_documents']:
        print(f"\n📄 PDF Documents ({len(results['pdf_documents'])}):")
        for doc in results['pdf_documents'][:10]:  # Top 10
            print(f"  • {doc['title']} (relevance: {doc['relevance']})")
            print(f"    {doc['url']}")
    
    if results['scheme_pages']:
        print(f"\n🏛️ Scheme Pages ({len(results['scheme_pages'])}):")
        for page in results['scheme_pages'][:10]:  # Top 10
            print(f"  • {page['title']} (relevance: {page['relevance']})")
            print(f"    {page['url']}")
    
    if results['data_pages']:
        print(f"\n📊 Data Pages ({len(results['data_pages'])}):")
        for page in results['data_pages'][:10]:  # Top 10
            print(f"  • {page['title']} (relevance: {page['relevance']})")
            print(f"    {page['url']}")
    
    # Save results to JSON
    output_file = f"link_exploration_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
