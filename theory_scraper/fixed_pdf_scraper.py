#!/usr/bin/env python3
"""
Fixed PDF Scraper for Rainwater Harvesting Theory Extraction
Robust implementation with detailed logging and improved text extraction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import io
import re
import json
import pandas as pd
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import warnings
from config import ScraperConfig

# Suppress PDF parsing warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pdfplumber")

try:
    import pdfplumber
except ImportError:
    print("pdfplumber not installed. Install with: pip install pdfplumber")
    pdfplumber = None

try:
    import PyPDF2
except ImportError:
    print("PyPDF2 not installed. Install with: pip install PyPDF2")
    PyPDF2 = None

# Suppress warnings more aggressively
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress specific PDF library warnings
logging.getLogger('pdfplumber').setLevel(logging.ERROR)
logging.getLogger('pypdfium2').setLevel(logging.ERROR)
logging.getLogger('fontTools').setLevel(logging.ERROR)

class FixedPDFScraper:
    """Simplified and robust PDF scraper for theory extraction"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Enhanced keywords for better content detection
        self.theory_keywords = [
            # Core water management
            'rainwater', 'harvesting', 'groundwater', 'recharge', 'conservation',
            'rooftop', 'catchment', 'collection', 'storage', 'tank', 'reservoir',
            'water', 'management', 'supply', 'quality', 'treatment', 'purification',
            
            # Technical aspects
            'filtration', 'capacity', 'design', 'specification', 'calculation',
            'pipe', 'diameter', 'flow', 'pressure', 'pump', 'system',
            'installation', 'construction', 'maintenance', 'operation',
            
            # Guidelines and regulations
            'guideline', 'procedure', 'standard', 'protocol', 'regulation',
            'policy', 'compliance', 'permit', 'approval', 'building', 'code',
            
            # Economic aspects
            'cost', 'price', 'budget', 'subsidy', 'scheme', 'benefit',
            'investment', 'financial', 'economic', 'funding',
            
            # Environmental
            'environment', 'sustainable', 'green', 'pollution', 'watershed'
        ]
        
        logger.info("Fixed PDF Scraper initialized")
    
    def extract_pdf_content(self, pdf_url: str) -> Dict[str, Any]:
        """Extract content from PDF with improved error handling"""
        logger.info(f"📄 Starting PDF processing: {pdf_url}")
        
        try:
            # Download PDF with retries
            logger.info("⬇️ Downloading PDF...")
            pdf_data = self._download_pdf(pdf_url)
            if not pdf_data:
                return self._create_error_result(pdf_url, "Failed to download PDF")
            logger.info(f"✅ PDF downloaded successfully ({len(pdf_data.getvalue())} bytes)")
            
            # Extract text using multiple methods
            logger.info("📝 Extracting text from PDF...")
            all_text = self._extract_all_text(pdf_data)
            
            if not all_text or len(all_text.strip()) < 100:
                return self._create_error_result(pdf_url, "No meaningful text extracted")
            logger.info(f"✅ Text extracted successfully ({len(all_text)} characters)")
            
            # Extract theory items from text
            logger.info("🔍 Analyzing content for theory items...")
            theory_items = self._process_text_for_theory(all_text, pdf_url)
            logger.info(f"✅ Found {len(theory_items)} theory items")
            
            return {
                'success': True,
                'url': pdf_url,
                'theory_items': theory_items,
                'text_length': len(all_text),
                'extraction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing {pdf_url}: {e}")
            return self._create_error_result(pdf_url, str(e))
    
    def _download_pdf(self, pdf_url: str) -> io.BytesIO:
        """Download PDF with retries and better error handling"""
        for attempt in range(3):
            try:
                logger.info(f"📡 Download attempt {attempt + 1}/3...")
                response = self.session.get(
                    pdf_url, 
                    timeout=30,  # Reduced timeout
                    verify=False,
                    stream=True,
                    allow_redirects=True
                )
                response.raise_for_status()
                logger.info(f"✅ Download successful on attempt {attempt + 1}")
                return io.BytesIO(response.content)
                
            except Exception as e:
                logger.warning(f"❌ Download attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    logger.info(f"⏳ Waiting 3 seconds before retry...")
                    time.sleep(3)
                else:
                    logger.error(f"💥 All download attempts failed for {pdf_url}")
                    return None
    
    def _extract_all_text(self, pdf_data: io.BytesIO) -> str:
        """Extract text using multiple methods and combine"""
        all_texts = []
        
        # Method 1: pdfplumber with detailed logging
        try:
            pdf_data.seek(0)
            logger.info("🔧 Starting pdfplumber extraction...")
            
            with pdfplumber.open(pdf_data) as pdf:
                logger.info(f"📖 PDF has {len(pdf.pages)} pages")
                text_parts = []
                
                for page_num, page in enumerate(pdf.pages):
                    logger.info(f"📄 Processing page {page_num + 1}/{len(pdf.pages)}...")
                    try:
                        # Simple extraction first
                        page_text = page.extract_text()
                        
                        if page_text and len(page_text.strip()) > 50:
                            text_parts.append(f"\n=== PAGE {page_num + 1} ===\n{page_text}")
                            logger.info(f"✅ Page {page_num + 1}: {len(page_text)} characters extracted")
                        else:
                            logger.warning(f"⚠️ Page {page_num + 1}: No text extracted")
                            
                    except Exception as page_error:
                        logger.warning(f"❌ Page {page_num + 1} extraction failed: {page_error}")
                        continue
                
                if text_parts:
                    combined_text = "\n".join(text_parts)
                    all_texts.append(combined_text)
                    logger.info(f"✅ pdfplumber: {len(combined_text)} total characters")
                else:
                    logger.warning("⚠️ pdfplumber: No text extracted")
                    
        except Exception as e:
            logger.error(f"💥 pdfplumber extraction failed: {e}")
        
        # Method 2: PyPDF2 with detailed logging
        try:
            pdf_data.seek(0)
            logger.info("🔧 Starting PyPDF2 extraction...")
            
            pdf_reader = PyPDF2.PdfReader(pdf_data)
            logger.info(f"📖 PyPDF2 detected {len(pdf_reader.pages)} pages")
            text_parts = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                logger.info(f"📄 PyPDF2 processing page {page_num + 1}...")
                try:
                    page_text = page.extract_text()
                    if page_text and len(page_text.strip()) > 50:
                        text_parts.append(f"\n=== PAGE {page_num + 1} ===\n{page_text}")
                        logger.info(f"✅ PyPDF2 Page {page_num + 1}: {len(page_text)} characters")
                    else:
                        logger.warning(f"⚠️ PyPDF2 Page {page_num + 1}: No text")
                except Exception as e:
                    logger.warning(f"❌ PyPDF2 page {page_num + 1} failed: {e}")
            
            if text_parts:
                combined_text = "\n".join(text_parts)
                all_texts.append(combined_text)
                logger.info(f"✅ PyPDF2: {len(combined_text)} total characters")
            else:
                logger.warning("⚠️ PyPDF2: No text extracted")
                
        except Exception as e:
            logger.error(f"💥 PyPDF2 extraction failed: {e}")
        
        # Return the longest extracted text
        if all_texts:
            best_text = max(all_texts, key=len)
            logger.info(f"🎯 Using best extraction: {len(best_text)} characters")
            return best_text
        else:
            logger.error("💥 No text extracted from any method")
            return ""
    
    def _extract_theory_items(self, text: str, source_url: str) -> List[Dict[str, Any]]:
        """Extract theory items using improved chunking and pattern matching"""
        theory_items = []
        
        # Split text into meaningful sections
        sections = self._split_into_sections(text)
        
        for section_index, section in enumerate(sections):
            if len(section.strip()) < 150:  # Skip very short sections
                continue
            
            # Count relevant keywords in section
            section_lower = section.lower()
            relevant_keywords = [kw for kw in self.theory_keywords if kw in section_lower]
            
            # Only include sections with multiple relevant keywords
            if len(relevant_keywords) >= 2:
                # Extract title from section
                title = self._extract_section_title(section)
                
                # Categorize content
                category = self._categorize_section(section)
                
                # Clean and format content
                clean_content = self._clean_content(section)
                
                theory_items.append({
                    'title': title,
                    'content': clean_content,
                    'category': category,
                    'keywords': relevant_keywords[:10],  # Limit keywords
                    'source_url': source_url,
                    'source_type': 'PDF Text',
                    'section_index': section_index,
                    'relevance_score': len(relevant_keywords),
                    'content_length': len(clean_content)
                })
        
        # Extract specific important patterns
        pattern_items = self._extract_important_patterns(text, source_url)
        theory_items.extend(pattern_items)
        
        # Remove duplicates and sort by relevance
        theory_items = self._deduplicate_items(theory_items)
        
        return theory_items
    
    def _split_into_sections(self, text: str) -> List[str]:
        """Split text into meaningful sections"""
        logger.info("✂️ Starting text splitting...")
        sections = []
        
        # Remove page markers first and split by them
        pages = re.split(r'=== PAGE \d+ ===', text)
        
        for page_num, page_content in enumerate(pages):
            if len(page_content.strip()) < 100:
                continue
                
            # Split each page into paragraphs
            paragraphs = re.split(r'\n\s*\n', page_content)
            current_section = ""
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if len(paragraph) > 80:  # Meaningful paragraphs only
                    # Check if this looks like a new section/heading
                    is_heading = (
                        paragraph.isupper() or 
                        re.match(r'^\d+\.', paragraph) or
                        re.match(r'^[A-Z][^.]*:$', paragraph) or
                        len(paragraph) < 200 and paragraph.count('\n') == 0
                    )
                    
                    if is_heading and current_section:
                        # Save current section and start new one
                        sections.append(current_section.strip())
                        current_section = paragraph
                    elif len(current_section + paragraph) > 1200:
                        # Section getting too long, split it
                        if current_section:
                            sections.append(current_section.strip())
                        current_section = paragraph
                    else:
                        # Add to current section
                        current_section += "\n\n" + paragraph if current_section else paragraph
            
            # Add final section from this page
            if current_section and len(current_section.strip()) > 150:
                sections.append(current_section.strip())
        
        # If still no good sections, do aggressive paragraph splitting
        if len(sections) < 3:
            sections = []
            all_paragraphs = re.split(r'\n\s*\n', text)
            
            for paragraph in all_paragraphs:
                paragraph = paragraph.strip()
                # Remove page markers
                paragraph = re.sub(r'=== PAGE \d+ ===', '', paragraph).strip()
                
                if len(paragraph) > 200:  # Substantial paragraphs only
                    sections.append(paragraph)
        
        return [s for s in sections if len(s.strip()) > 150]
    
    def _extract_section_title(self, section: str) -> str:
        """Extract meaningful title from section"""
        lines = section.split('\n')
        
        # Look for title-like lines
        for line in lines[:5]:
            line = line.strip()
            if 10 <= len(line) <= 100:
                # Check if it looks like a title
                if (line.isupper() or line.istitle() or 
                    re.match(r'^\d+\.\s+[A-Z]', line) or
                    any(word in line.lower() for word in ['chapter', 'section', 'part', 'guideline'])):
                    return line
        
        # Fallback: first sentence
        sentences = re.split(r'[.!?]', section)
        if sentences and len(sentences[0].strip()) > 10:
            return sentences[0].strip()[:80] + ('...' if len(sentences[0]) > 80 else '')
        
        # Final fallback
        return section[:60].strip() + '...'
    
    def _categorize_section(self, section: str) -> str:
        """Categorize section based on content"""
        section_lower = section.lower()
        
        # Category keywords
        categories = {
            'guidelines': ['guideline', 'procedure', 'step', 'instruction', 'protocol'],
            'specifications': ['specification', 'design', 'dimension', 'capacity', 'technical'],
            'economics': ['cost', 'price', 'budget', 'subsidy', 'financial', 'economic'],
            'maintenance': ['maintenance', 'cleaning', 'repair', 'operation', 'upkeep'],
            'quality': ['quality', 'testing', 'standard', 'purity', 'contamination'],
            'regulations': ['regulation', 'law', 'compliance', 'policy', 'permit', 'approval'],
            'systems': ['system', 'harvesting', 'collection', 'storage', 'recharge'],
            'components': ['tank', 'pipe', 'filter', 'pump', 'component', 'equipment']
        }
        
        # Count matches for each category
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in section_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        else:
            return 'general'
    
    def _clean_content(self, content: str) -> str:
        """Clean and format content"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Remove page markers
        content = re.sub(r'=== PAGE \d+ ===', '', content)
        
        # Remove common PDF artifacts
        content = re.sub(r'\s*\n\s*', ' ', content)  # Join broken lines
        content = re.sub(r'[^\w\s.,;:!?()-]', ' ', content)  # Remove special chars
        content = ' '.join(content.split())  # Normalize whitespace
        
        # Limit content length but keep complete sentences
        if len(content) > 1500:
            # Find last complete sentence within limit
            truncated = content[:1500]
            last_period = truncated.rfind('.')
            if last_period > 500:  # Ensure we keep substantial content
                content = content[:last_period + 1]
            else:
                content = content[:1500] + "..."
        
        return content.strip()
    
    def _extract_important_patterns(self, text: str, source_url: str) -> List[Dict[str, Any]]:
        """Extract specific important patterns"""
        pattern_items = []
        
        logger.info("🔍 Extracting specific patterns...")
        
        # Important patterns for rainwater harvesting theory
        important_patterns = [
            (r'(?:design|construction|installation)\s+(?:guidelines?|standards?|specifications?)', 'design_guidelines'),
            (r'(?:cost|price|budget|financial)\s+(?:analysis|estimation|calculation)', 'cost_analysis'),
            (r'(?:maintenance|operation|cleaning)\s+(?:procedures?|guidelines?|schedule)', 'maintenance'),
            (r'(?:quality|standards?|specifications?)\s+(?:requirements?|criteria)', 'quality_standards'),
            (r'(?:environmental|ecological)\s+(?:impact|benefits?|effects?)', 'environmental_impact'),
            (r'(?:government|policy|regulation)\s+(?:schemes?|programs?|initiatives?)', 'government_schemes'),
            (r'(?:technical|engineering)\s+(?:specifications?|requirements?|details?)', 'technical_specs'),
            (r'(?:case\s+studies?|examples?|implementations?)', 'case_studies')
        ]
        
        total_patterns = len(important_patterns)
        logger.info(f"📊 Processing {total_patterns} pattern types...")
        
        for i, (pattern, category) in enumerate(important_patterns, 1):
            logger.info(f"🔍 Pattern {i}/{total_patterns}: {category}")
            matches = re.finditer(pattern, text)
            match_count = 0
            for match in matches:
                sentence = match.group(0).strip()
                if 50 <= len(sentence) <= 500:  # Reasonable sentence length
                    pattern_items.append({
                        'title': f"{category.title()} - {sentence[:50]}...",
                        'content': sentence,
                        'category': category,
                        'keywords': [category],
                        'source_url': source_url,
                        'source_type': 'Pattern Match',
                        'extraction_method': 'regex_pattern',
                        'relevance_score': 5  # High relevance for pattern matches
                    })
                    match_count += 1
            logger.info(f"✅ Found {match_count} matches for {category}")
        
        return pattern_items
    
    def _deduplicate_items(self, theory_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates and rank by relevance"""
        # Remove duplicates based on content similarity
        unique_items = []
        seen_hashes = set()
        
        for item in theory_items:
            # Create hash from first 100 characters of content
            content_hash = hash(item['content'][:100].lower().strip())
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_items.append(item)
        
        # Sort by relevance score and content length
        unique_items.sort(key=lambda x: (x.get('relevance_score', 0), len(x['content'])), reverse=True)
        
        return unique_items
    
    def _process_text_for_theory(self, text: str, source_url: str) -> List[Dict[str, Any]]:
        """Extract theory items using improved chunking and pattern matching"""
        theory_items = []
        
        if not text or len(text.strip()) < 100:
            logger.warning("⚠️ Text too short for analysis")
            return theory_items
        
        logger.info(f"📊 Analyzing {len(text)} characters of text...")
        
        # Split text into meaningful sections
        logger.info("✂️ Splitting text into sections...")
        sections = self._split_into_sections(text)
        logger.info(f"📑 Found {len(sections)} sections to analyze")
        
        for section_index, section in enumerate(sections):
            logger.info(f"🔍 Analyzing section {section_index + 1}/{len(sections)} ({len(section)} chars)...")
            
            if len(section.strip()) < 150:  # Skip very short sections
                logger.info(f"⏭️ Skipping short section {section_index + 1}")
                continue
            
            # Count relevant keywords in section
            section_lower = section.lower()
            relevant_keywords = [kw for kw in self.theory_keywords if kw in section_lower]
            logger.info(f"🔑 Section {section_index + 1}: {len(relevant_keywords)} keywords found")
            
            # Only include sections with multiple relevant keywords
            if len(relevant_keywords) >= 2:
                logger.info(f"✅ Section {section_index + 1} qualifies for extraction")
                
                # Extract title from section
                title = self._extract_section_title(section)
                
                # Categorize content
                category = self._categorize_section(section)
                
                # Clean and format content
                clean_content = self._clean_content(section)
                
                theory_items.append({
                    'title': title,
                    'content': clean_content,
                    'category': category,
                    'keywords': relevant_keywords[:10],  # Limit keywords
                    'source_url': source_url,
                    'source_type': 'PDF Text',
                    'section_index': section_index,
                    'relevance_score': len(relevant_keywords),
                    'content_length': len(clean_content)
                })
                logger.info(f"📝 Added theory item: '{title[:50]}...' ({category})")
            else:
                logger.info(f"⏭️ Section {section_index + 1} doesn't meet keyword threshold")
        
        # Extract specific important patterns
        logger.info("🎯 Extracting specific patterns...")
        pattern_items = self._extract_important_patterns(text, source_url)
        logger.info(f"🎯 Found {len(pattern_items)} pattern matches")
        theory_items.extend(pattern_items)
        
        # Remove duplicates and sort by relevance
        logger.info("🔄 Deduplicating and ranking items...")
        theory_items = self._deduplicate_items(theory_items)
        logger.info(f"✨ Final result: {len(theory_items)} unique theory items")
        
        return theory_items
    
    def _create_error_result(self, url: str, error_msg: str) -> Dict[str, Any]:
        """Create standardized error result"""
        return {
            'success': False,
            'url': url,
            'error': error_msg,
            'theory_items': [],
            'extraction_timestamp': datetime.now().isoformat()
        }
    
    def save_results(self, results: List[Dict], filename_prefix: str = "fixed_pdf_extraction"):
        """Save extraction results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON
        json_file = self.output_dir / f"{filename_prefix}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Create CSV summary
        csv_data = []
        for result in results:
            if result['success']:
                for item in result['theory_items']:
                    csv_data.append({
                        'source_url': item['source_url'],
                        'title': item['title'],
                        'category': item['category'],
                        'content_preview': item['content'][:200] + '...' if len(item['content']) > 200 else item['content'],
                        'keywords': ', '.join(item['keywords'][:5]),  # Limit keywords in CSV
                        'relevance_score': item.get('relevance_score', 0),
                        'content_length': len(item['content'])
                    })
        
        if csv_data:
            csv_file = self.output_dir / f"{filename_prefix}_{timestamp}.csv"
            pd.DataFrame(csv_data).to_csv(csv_file, index=False, encoding='utf-8')
            logger.info(f"Results saved to {json_file} and {csv_file}")
        else:
            logger.info(f"Results saved to {json_file} (no CSV data)")
        
        return json_file

def extract_pdf_urls_from_config():
    """Extract all PDF URLs from the centralized configuration"""
    pdf_urls = []
    
    # Get all URL categories from config
    all_urls = ScraperConfig.get_all_urls()
    
    for category, urls in all_urls.items():
        for url in urls:
            if url.lower().endswith('.pdf'):
                pdf_urls.append(url)
    
    # Also check additional URL lists that might contain PDFs
    additional_url_lists = [
        getattr(ScraperConfig, 'ENVIRONMENTAL_IMPACT_URLS', []),
        getattr(ScraperConfig, 'COST_DATA_URLS', []),
        getattr(ScraperConfig, 'TECHNICAL_RESOURCES_URLS', [])
    ]
    
    for url_list in additional_url_lists:
        for url in url_list:
            if url.lower().endswith('.pdf'):
                pdf_urls.append(url)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in pdf_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    return unique_urls

def main():
    """Main function to run the PDF scraper with centralized config URLs"""
    scraper = FixedPDFScraper()
    
    # Extract all PDF URLs from config
    logger.info("🔍 Extracting PDF URLs from centralized config...")
    pdf_urls = extract_pdf_urls_from_config()
    
    logger.info(f"📄 Found {len(pdf_urls)} unique PDF URLs in config")
    for i, url in enumerate(pdf_urls, 1):
        logger.info(f"  {i}. {url}")
    
    # Process all PDFs with progress tracking
    results = []
    total_pdfs = len(pdf_urls)
    start_time = datetime.now()
    
    for i, url in enumerate(pdf_urls, 1):
        logger.info(f"🚀 Processing PDF {i}/{total_pdfs}: {url}")
        
        # Calculate ETA
        if i > 1:
            elapsed = (datetime.now() - start_time).total_seconds()
            avg_time_per_pdf = elapsed / (i - 1)
            remaining_pdfs = total_pdfs - i + 1
            eta_seconds = avg_time_per_pdf * remaining_pdfs
            eta_minutes = eta_seconds / 60
            logger.info(f"⏱️ ETA: {eta_minutes:.1f} minutes remaining ({avg_time_per_pdf:.1f}s per PDF)")
        
        result = scraper.extract_pdf_content(url)
        results.append(result)
        
        # Progress summary
        successful_so_far = sum(1 for r in results if r.get('success', False))
        logger.info(f"📊 Progress: {i}/{total_pdfs} PDFs processed ({successful_so_far} successful)")
        logger.info(f"{'='*50}")
    
    logger.info("🎉 PDF extraction completed!")
    logger.info(f"📊 Results: {len(results)} PDFs processed")
    
    # Count successful extractions
    successful = sum(1 for r in results if r.get('success', False))
    total_theory_items = sum(len(r.get('theory_items', [])) for r in results)
    
    logger.info(f"✅ Successful: {successful}/{len(results)} PDFs")
    logger.info(f"📚 Total theory items extracted: {total_theory_items}")
    
    # Save all results
    scraper.save_results(results, "fixed_pdf_extraction")
    
    print(f"\n📊 FIXED PDF EXTRACTION COMPLETE!")
    print(f"Successful extractions: {successful}/{len(results)}")
    print(f"Total theory items extracted: {total_theory_items}")
    
    # Show sample of extracted items
    if total_theory_items > 0:
        print(f"\n📋 SAMPLE EXTRACTED ITEMS:")
        item_count = 0
        for result in results:
            if result.get('success', False) and result.get('theory_items'):
                for item in result['theory_items'][:3]:  # Show first 3 items per PDF
                    print(f"  • {item['title']} ({item['category']})")
                    item_count += 1
                    if item_count >= 5:  # Limit total sample
                        break
                if item_count >= 5:
                    break

if __name__ == "__main__":
    main()
