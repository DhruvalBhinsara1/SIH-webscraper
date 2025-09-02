#!/usr/bin/env python3
"""
Intelligent URL Categorization System for Jal Setu Web Scraper
Automatically categorizes pasted URLs into appropriate data categories
"""

import re
import requests
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Tuple, Optional
import json
import os
from bs4 import BeautifulSoup
import time

class IntelligentURLCategorizer:
    """Intelligent URL categorization system"""
    
    def __init__(self):
        self.categories = {
            'government_schemes': {
                'keywords': [
                    'scheme', 'subsidy', 'grant', 'policy', 'government', 'ministry',
                    'pmksy', 'jalshakti', 'dowr', 'mowr', 'myscheme', 'india.gov',
                    'state.gov', 'municipal', 'corporation', 'nagar', 'panchayat',
                    'benefit', 'eligibility', 'application', 'registration'
                ],
                'domains': [
                    'gov.in', 'nic.in', 'jalshakti-dowr.gov.in', 'pmksy.gov.in',
                    'myscheme.gov.in', 'india.gov.in', 'pib.gov.in', 'pmindia.gov.in'
                ],
                'url_patterns': [
                    r'/scheme', r'/subsidy', r'/grant', r'/policy', r'/benefit',
                    r'/application', r'/registration', r'/eligibility'
                ]
            },
            'weather_data': {
                'keywords': [
                    'weather', 'rainfall', 'precipitation', 'climate', 'meteorology',
                    'imd', 'mausam', 'forecast', 'monsoon', 'temperature', 'humidity',
                    'wind', 'pressure', 'data', 'statistics', 'historical'
                ],
                'domains': [
                    'mausam.imd.gov.in', 'imdpune.gov.in', 'weatherapi.com',
                    'accuweather.com', 'weather.com', 'open-meteo.com',
                    'indiawris.gov.in'
                ],
                'url_patterns': [
                    r'/weather', r'/rainfall', r'/forecast', r'/climate',
                    r'/meteorology', r'/data', r'/statistics'
                ]
            },
            'cost_information': {
                'keywords': [
                    'cost', 'price', 'rate', 'tariff', 'schedule', 'equipment',
                    'material', 'supplier', 'vendor', 'market', 'procurement',
                    'tender', 'quotation', 'estimate', 'budget', 'financial'
                ],
                'domains': [
                    'tradeindia.com', 'indiamart.com', 'cpwd.gov.in', 'uppwd.gov.in',
                    'sbi.co.in', 'cewacor.nic.in', 'scribd.com'
                ],
                'url_patterns': [
                    r'/price', r'/cost', r'/rate', r'/tariff', r'/schedule',
                    r'/equipment', r'/material', r'/supplier', r'/market'
                ]
            },
            'technical_resources': {
                'keywords': [
                    'technical', 'guideline', 'manual', 'specification', 'standard',
                    'design', 'construction', 'installation', 'maintenance',
                    'best practice', 'research', 'study', 'report', 'document'
                ],
                'domains': [
                    'cgwb.gov.in', 'cwas.org.in', 'nwm.gov.in', 'cpcb.nic.in',
                    'rainwaterharvesting.org', 'ircwash.org', 'unep.org',
                    'who.int', 'worldbank.org', 'fao.org'
                ],
                'url_patterns': [
                    r'/guideline', r'/manual', r'/specification', r'/standard',
                    r'/technical', r'/research', r'/study', r'/report'
                ]
            },
            'news_policy': {
                'keywords': [
                    'news', 'press', 'release', 'announcement', 'update',
                    'policy', 'notification', 'circular', 'order', 'gazette',
                    'latest', 'current', 'recent', 'today'
                ],
                'domains': [
                    'pib.gov.in', 'thehindu.com', 'timesofindia.com',
                    'downtoearth.org.in', 'thethirdpole.net', 'indiawaterportal.org',
                    'waterpowermagazine.com', 'waterworld.com'
                ],
                'url_patterns': [
                    r'/news', r'/press', r'/release', r'/announcement',
                    r'/update', r'/notification', r'/circular'
                ]
            },
            'environmental_impact': {
                'keywords': [
                    'environment', 'impact', 'sustainability', 'conservation',
                    'carbon', 'emission', 'reduction', 'efficiency', 'savings',
                    'recharge', 'groundwater', 'aquifer', 'ecosystem'
                ],
                'domains': [
                    'moef.gov.in', 'cpcb.nic.in', 'unep.org', 'worldbank.org',
                    'who.int', 'epa.gov', 'mdpi.com', 'sciencedirect.com',
                    'iwaponline.com'
                ],
                'url_patterns': [
                    r'/environment', r'/impact', r'/sustainability',
                    r'/conservation', r'/emission', r'/efficiency'
                ]
            }
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def categorize_url(self, url: str) -> Tuple[str, float, Dict[str, any]]:
        """
        Categorize a single URL and return category, confidence score, and analysis
        
        Args:
            url: URL to categorize
            
        Returns:
            Tuple of (category, confidence_score, analysis_details)
        """
        analysis = {
            'url': url,
            'domain': '',
            'path': '',
            'content_keywords': [],
            'title': '',
            'meta_description': '',
            'category_scores': {}
        }
        
        try:
            # Parse URL
            parsed = urlparse(url)
            analysis['domain'] = parsed.netloc.lower()
            analysis['path'] = parsed.path.lower()
            
            # Calculate scores for each category
            for category, criteria in self.categories.items():
                score = self._calculate_category_score(url, analysis, criteria)
                analysis['category_scores'][category] = score
            
            # Try to fetch content for better analysis
            try:
                content_score = self._analyze_content(url, analysis)
                # Boost scores based on content analysis
                for category in analysis['category_scores']:
                    analysis['category_scores'][category] += content_score.get(category, 0)
            except:
                pass  # Continue without content analysis if it fails
            
            # Determine best category
            best_category = max(analysis['category_scores'], key=analysis['category_scores'].get)
            confidence = analysis['category_scores'][best_category]
            
            return best_category, confidence, analysis
            
        except Exception as e:
            print(f"Error categorizing URL {url}: {e}")
            return 'unknown', 0.0, analysis
    
    def _calculate_category_score(self, url: str, analysis: Dict, criteria: Dict) -> float:
        """Calculate category score based on URL patterns and domain"""
        score = 0.0
        
        # Domain matching (high weight)
        for domain in criteria['domains']:
            if domain in analysis['domain']:
                score += 0.4
                break
        
        # URL path pattern matching (medium weight)
        for pattern in criteria['url_patterns']:
            if re.search(pattern, analysis['path']):
                score += 0.3
                break
        
        # Keyword matching in URL (low weight)
        url_lower = url.lower()
        keyword_matches = sum(1 for keyword in criteria['keywords'] if keyword in url_lower)
        if keyword_matches > 0:
            score += min(0.3, keyword_matches * 0.1)
        
        return min(score, 1.0)
    
    def _analyze_content(self, url: str, analysis: Dict) -> Dict[str, float]:
        """Analyze webpage content for better categorization"""
        content_scores = {}
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title and meta description
                title = soup.find('title')
                analysis['title'] = title.text.strip() if title else ''
                
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                analysis['meta_description'] = meta_desc.get('content', '') if meta_desc else ''
                
                # Extract text content
                text_content = soup.get_text().lower()
                
                # Calculate content scores for each category
                for category, criteria in self.categories.items():
                    keyword_count = sum(1 for keyword in criteria['keywords'] if keyword in text_content)
                    content_scores[category] = min(0.4, keyword_count * 0.05)
                
                # Store found keywords for analysis
                all_keywords = []
                for criteria in self.categories.values():
                    all_keywords.extend(criteria['keywords'])
                
                analysis['content_keywords'] = [kw for kw in all_keywords if kw in text_content]
        
        except Exception as e:
            print(f"Content analysis failed for {url}: {e}")
        
        return content_scores
    
    def categorize_multiple_urls(self, urls: List[str]) -> Dict[str, List[Dict]]:
        """Categorize multiple URLs and group by category"""
        results = {category: [] for category in self.categories.keys()}
        results['unknown'] = []
        
        for url in urls:
            if not url.strip():
                continue
                
            category, confidence, analysis = self.categorize_url(url.strip())
            
            url_info = {
                'url': url,
                'confidence': confidence,
                'analysis': analysis
            }
            
            results[category].append(url_info)
            
            # Add delay to be respectful
            time.sleep(0.5)
        
        return results
    
    def save_categorized_urls(self, results: Dict, output_file: str = 'categorized_urls.json'):
        """Save categorization results to JSON file"""
        output_path = os.path.join('output', output_file)
        os.makedirs('output', exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to {output_path}")
    
    def generate_config_updates(self, results: Dict) -> str:
        """Generate Python code to update config.py with new URLs"""
        config_updates = []
        
        for category, urls in results.items():
            if category == 'unknown' or not urls:
                continue
            
            config_updates.append(f"\n# New {category.replace('_', ' ').title()} URLs")
            
            # Map category to config variable name
            var_mapping = {
                'government_schemes': 'GOVERNMENT_SCHEMES_URLS',
                'weather_data': 'WEATHER_URLS', 
                'cost_information': 'COST_DATA_URLS',
                'technical_resources': 'TECHNICAL_RESOURCES_URLS',
                'news_policy': 'NEWS_POLICY_URLS',
                'environmental_impact': 'ENVIRONMENTAL_IMPACT_URLS'
            }
            
            var_name = var_mapping.get(category, f"{category.upper()}_URLS")
            
            config_updates.append(f"# Add to {var_name}:")
            for url_info in urls:
                confidence = url_info['confidence']
                url = url_info['url']
                config_updates.append(f"'{url}',  # Confidence: {confidence:.2f}")
        
        return '\n'.join(config_updates)
    
    def interactive_categorization(self):
        """Interactive mode for URL categorization"""
        print("=== Intelligent URL Categorization System ===")
        print("Paste URLs (one per line) and press Enter twice when done:")
        print("Categories: government_schemes, weather_data, cost_information,")
        print("           technical_resources, news_policy, environmental_impact")
        print()
        
        urls = []
        while True:
            try:
                line = input().strip()
                if not line:
                    break
                urls.append(line)
            except KeyboardInterrupt:
                break
        
        if not urls:
            print("No URLs provided.")
            return
        
        print(f"\nAnalyzing {len(urls)} URLs...")
        results = self.categorize_multiple_urls(urls)
        
        # Display results
        print("\n=== CATEGORIZATION RESULTS ===")
        for category, url_list in results.items():
            if url_list:
                print(f"\n{category.replace('_', ' ').title()} ({len(url_list)} URLs):")
                for url_info in url_list:
                    print(f"  • {url_info['url']} (confidence: {url_info['confidence']:.2f})")
        
        # Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = f"categorized_urls_{timestamp}.json"
        self.save_categorized_urls(results, output_file)
        
        # Generate config updates
        config_updates = self.generate_config_updates(results)
        if config_updates:
            config_file = f"config_updates_{timestamp}.txt"
            config_path = os.path.join('output', config_file)
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_updates)
            print(f"\nConfig updates saved to {config_path}")
        
        return results

def main():
    """Main function for command line usage"""
    categorizer = IntelligentURLCategorizer()
    
    # Check if URLs provided as command line arguments
    import sys
    if len(sys.argv) > 1:
        urls = sys.argv[1:]
        results = categorizer.categorize_multiple_urls(urls)
        
        for category, url_list in results.items():
            if url_list:
                print(f"{category}: {len(url_list)} URLs")
        
        categorizer.save_categorized_urls(results)
    else:
        # Interactive mode
        categorizer.interactive_categorization()

if __name__ == "__main__":
    main()
