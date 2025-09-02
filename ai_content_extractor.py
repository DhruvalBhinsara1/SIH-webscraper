#!/usr/bin/env python3
"""
AI Content Extractor for Jal Setu Web Scraper
Handles intelligent content extraction, classification, and translation
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from langdetect import detect, DetectorFactory
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    try:
        from googletrans import Translator
        TRANSLATOR_AVAILABLE = True
        USE_DEEP_TRANSLATOR = False
    except ImportError:
        print("Warning: No translation library available. Translation features will be disabled.")
        TRANSLATOR_AVAILABLE = False
        GoogleTranslator = None
        Translator = None
    else:
        USE_DEEP_TRANSLATOR = False
else:
    USE_DEEP_TRANSLATOR = True
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
import spacy
from textblob import TextBlob
import pandas as pd
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# Set seed for consistent language detection
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

class AIContentExtractor:
    """AI-powered content extraction and processing"""
    
    def __init__(self):
        if TRANSLATOR_AVAILABLE:
            if USE_DEEP_TRANSLATOR:
                self.translator = GoogleTranslator(source='auto', target='en')
            else:
                self.translator = Translator()
        else:
            self.translator = None
        self.nlp = None
        self.translation_enabled = True  # Flag to disable translation if it keeps failing
        self.translation_failure_count = 0
        
        # Multi-language support
        self.target_languages = {
            'hi': 'Hindi',
            'bn': 'Bengali', 
            'mr': 'Marathi',
            'te': 'Telugu',
            'ta': 'Tamil',
            'gu': 'Gujarati',
            'ur': 'Urdu',
            'kn': 'Kannada',
            'or': 'Odia',
            'ml': 'Malayalam',
            'en': 'English'
        }
        
        self._setup_nlp()
        self._download_nltk_data()
        
        # Patterns for different content types
        self.scheme_patterns = {
            'scheme_name': r'(?:scheme|yojana|program|programme)[\s:]*([^\n\r]+)',
            'eligibility': r'(?:eligibility|eligible|criteria)[\s:]*([^\n\r]+)',
            'subsidy': r'(?:subsidy|grant|financial|amount|rs\.?\s*\d+|₹\s*\d+)',
            'deadline': r'(?:deadline|last date|apply by)[\s:]*([^\n\r]+)',
            'contact': r'(?:contact|phone|email|address)[\s:]*([^\n\r]+)'
        }
        
        self.weather_patterns = {
            'rainfall': r'(?:rainfall|precipitation|rain)[\s:]*(\d+(?:\.\d+)?)\s*(?:mm|millimeter)',
            'temperature': r'(?:temperature|temp)[\s:]*(\d+(?:\.\d+)?)\s*(?:°c|celsius|degree)',
            'humidity': r'(?:humidity|moisture)[\s:]*(\d+(?:\.\d+)?)\s*(?:%|percent)',
            'date': r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})'
        }
        
        self.cost_patterns = {
            'price': r'(?:rs\.?\s*|₹\s*|price\s*|cost\s*)(\d+(?:,\d+)*(?:\.\d+)?)',
            'unit': r'(?:per|/)\s*([a-zA-Z\s]+)',
            'material': r'(?:material|item|product)[\s:]*([^\n\r]+)',
            'supplier': r'(?:supplier|vendor|company)[\s:]*([^\n\r]+)'
        }
    
    def _setup_nlp(self):
        """Setup spaCy NLP pipeline"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy English model loaded successfully")
        except OSError:
            logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('taggers/averaged_perceptron_tagger')
            nltk.data.find('chunkers/maxent_ne_chunker')
            nltk.data.find('corpora/words')
        except LookupError:
            logger.info("Downloading NLTK data...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('maxent_ne_chunker', quiet=True)
            nltk.download('words', quiet=True)
    
    def detect_language(self, text: str) -> str:
        """Detect language of text"""
        try:
            if len(text.strip()) < 10:
                return 'en'  # Default to English for short text
            return detect(text)
        except:
            return 'en'
    
    def translate_to_english(self, text: str, source_lang: str = None) -> str:
        """Translate text to English with robust error handling"""
        if not TRANSLATOR_AVAILABLE or not self.translator or not self.translation_enabled:
            return text
            
        try:
            if not source_lang:
                source_lang = self.detect_language(text)
            
            if source_lang == 'en':
                return text
            
            # Skip translation for very short text or if it's mostly English
            if len(text.strip()) < 20:
                return text
                
            # Check if text is mostly English already
            english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
            word_count = len(text.split())
            english_word_count = sum(1 for word in text.lower().split() if word in english_words)
            if word_count > 0 and (english_word_count / word_count) > 0.3:
                return text  # Likely already in English
            
            # Disable translation if too many failures
            if self.translation_failure_count > 5:
                logger.info("Translation disabled due to repeated failures. Processing content in original language.")
                self.translation_enabled = False
                return text
            
            # Handle long text by splitting into chunks
            if len(text) > 3000:  # Reduced chunk size for better reliability
                chunks = self._split_text(text, 2000)
                translated_chunks = []
                for i, chunk in enumerate(chunks):
                    try:
                        # Add delay between translation requests
                        if i > 0:
                            import time
                            time.sleep(1)
                            
                        if USE_DEEP_TRANSLATOR:
                            translated_text = self.translator.translate(chunk)
                        else:
                            translated = self.translator.translate(chunk, src=source_lang, dest='en')
                            translated_text = translated.text
                        translated_chunks.append(translated_text)
                    except Exception as e:
                        self.translation_failure_count += 1
                        logger.debug(f"Translation failed for chunk {i+1}: {str(e)[:100]}")
                        # Return original chunk if translation fails
                        translated_chunks.append(chunk)
                return ' '.join(translated_chunks)
            else:
                try:
                    if USE_DEEP_TRANSLATOR:
                        return self.translator.translate(text)
                    else:
                        translated = self.translator.translate(text, src=source_lang, dest='en')
                        return translated.text
                except Exception as e:
                    self.translation_failure_count += 1
                    logger.debug(f"Translation failed for short text: {str(e)[:100]}")
                    return text
                
        except Exception as e:
            self.translation_failure_count += 1
            logger.debug(f"Translation process failed: {str(e)[:100]}")
            return text
    
    def disable_translation(self):
        """Disable translation functionality"""
        self.translation_enabled = False
        logger.info("Translation functionality disabled")
    
    def enable_translation(self):
        """Re-enable translation functionality"""
        self.translation_enabled = True
        self.translation_failure_count = 0
        logger.info("Translation functionality enabled")
    
    def translate_to_language(self, text: str, target_lang: str) -> str:
        """Translate text to a specific target language"""
        if not TRANSLATOR_AVAILABLE or not self.translator or not self.translation_enabled:
            return text
            
        if target_lang == 'en':
            return text
            
        try:
            # Detect source language
            source_lang = self.detect_language(text)
            
            # Skip if already in target language
            if source_lang == target_lang:
                return text
            
            # Handle long text by splitting into chunks
            if len(text) > 2000:
                chunks = self._split_text(text, 1500)
                translated_chunks = []
                for i, chunk in enumerate(chunks):
                    try:
                        if i > 0:
                            import time
                            time.sleep(1)
                            
                        if USE_DEEP_TRANSLATOR:
                            translator = GoogleTranslator(source='auto', target=target_lang)
                            translated_text = translator.translate(chunk)
                        else:
                            translated = self.translator.translate(chunk, src=source_lang, dest=target_lang)
                            translated_text = translated.text
                        translated_chunks.append(translated_text)
                    except Exception as e:
                        logger.debug(f"Translation to {target_lang} failed for chunk {i+1}: {str(e)[:100]}")
                        translated_chunks.append(chunk)
                return ' '.join(translated_chunks)
            else:
                try:
                    if USE_DEEP_TRANSLATOR:
                        translator = GoogleTranslator(source='auto', target=target_lang)
                        return translator.translate(text)
                    else:
                        translated = self.translator.translate(text, src=source_lang, dest=target_lang)
                        return translated.text
                except Exception as e:
                    logger.debug(f"Translation to {target_lang} failed: {str(e)[:100]}")
                    return text
                    
        except Exception as e:
            logger.debug(f"Translation process to {target_lang} failed: {str(e)[:100]}")
            return text
    
    def translate_data_to_all_languages(self, data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Translate extracted data to all target languages"""
        multilingual_data = {}
        
        for lang_code, lang_name in self.target_languages.items():
            logger.info(f"Translating data to {lang_name} ({lang_code})")
            multilingual_data[lang_code] = []
            
            for item in data:
                translated_item = {}
                for key, value in item.items():
                    if isinstance(value, str) and key in ['scheme_name', 'content', 'eligibility', 'contact', 'title', 'material', 'supplier']:
                        # Translate text fields
                        if lang_code == 'en':
                            translated_item[key] = self._safe_translate(value)  # Ensure English
                        else:
                            translated_item[key] = self.translate_to_language(value, lang_code)
                    else:
                        # Keep non-text fields as is
                        translated_item[key] = value
                
                # Add language metadata
                translated_item['language'] = lang_code
                translated_item['language_name'] = lang_name
                multilingual_data[lang_code].append(translated_item)
        
        return multilingual_data
    
    def save_multilingual_data(self, data: List[Dict[str, Any]], filename_prefix: str, data_type: str):
        """Save data in multiple languages to consolidated CSV and JSON files"""
        import csv
        import os
        
        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)
        
        # Translate data to all languages
        multilingual_data = self.translate_data_to_all_languages(data)
        
        # Consolidate all language data into single structures
        consolidated_json_data = []
        consolidated_csv_data = []
        
        for lang_code, lang_name in self.target_languages.items():
            if lang_code in multilingual_data and multilingual_data[lang_code]:
                lang_data = multilingual_data[lang_code]
                
                # Add to consolidated data
                for item in lang_data:
                    consolidated_json_data.append(item)
                    consolidated_csv_data.append(item)
        
        # Save consolidated JSON file
        if consolidated_json_data:
            json_filename = f"output/{filename_prefix}_{data_type}_multilingual.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(consolidated_json_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(consolidated_json_data)} multilingual records to {json_filename}")
        
        # Save consolidated CSV file
        if consolidated_csv_data:
            csv_filename = f"output/{filename_prefix}_{data_type}_multilingual.csv"
            try:
                with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                    if consolidated_csv_data:
                        writer = csv.DictWriter(f, fieldnames=consolidated_csv_data[0].keys())
                        writer.writeheader()
                        writer.writerows(consolidated_csv_data)
                logger.info(f"Saved {len(consolidated_csv_data)} multilingual records to {csv_filename}")
            except PermissionError:
                logger.warning(f"Cannot write to {csv_filename} - file may be open in Excel or another application")
                # Try alternative filename
                import time
                timestamp = int(time.time())
                alt_csv_filename = f"output/{filename_prefix}_{data_type}_multilingual_{timestamp}.csv"
                try:
                    with open(alt_csv_filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=consolidated_csv_data[0].keys())
                        writer.writeheader()
                        writer.writerows(consolidated_csv_data)
                    logger.info(f"Saved {len(consolidated_csv_data)} multilingual records to {alt_csv_filename}")
                except Exception as e:
                    logger.error(f"Failed to save CSV file: {e}")
            except Exception as e:
                logger.error(f"Failed to save CSV file: {e}")
            
        # Also save language-specific summary
        language_summary = {
            'total_records': len(data),
            'records_per_language': len(data),
            'total_multilingual_records': len(consolidated_json_data),
            'languages_included': list(self.target_languages.values()),
            'data_type': data_type,
            'creation_date': datetime.now().isoformat()
        }
        
        summary_filename = f"output/{filename_prefix}_{data_type}_language_summary.json"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            json.dump(language_summary, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved language summary to {summary_filename}")
    
    def _split_text(self, text: str, max_length: int) -> List[str]:
        """Split text into chunks of maximum length"""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) <= max_length:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _safe_translate(self, text: str) -> str:
        """Safely translate text with fallback to original"""
        if not self.translation_enabled:
            return text
        
        try:
            return self.translate_to_english(text)
        except Exception as e:
            self.translation_failure_count += 1
            logger.debug(f"Safe translation failed: {str(e)[:100]}")
            if self.translation_failure_count > 5:
                logger.info("Translation disabled due to repeated failures")
                self.translation_enabled = False
            return text
    
    def extract_government_schemes(self, text: str) -> List[Dict[str, Any]]:
        """Extract government scheme information from text"""
        text = self._safe_translate(text)
        schemes = []
        
        # Split text into potential scheme sections
        sections = re.split(r'\n\s*\n|\.\s*(?=[A-Z])', text)
        
        for section in sections:
            if len(section.strip()) < 50:
                continue
                
            scheme = {}
            
            # Extract scheme name
            name_match = re.search(self.scheme_patterns['scheme_name'], section, re.IGNORECASE)
            if name_match:
                scheme['scheme_name'] = name_match.group(1).strip()
            
            # Extract eligibility
            eligibility_match = re.search(self.scheme_patterns['eligibility'], section, re.IGNORECASE)
            if eligibility_match:
                scheme['eligibility'] = eligibility_match.group(1).strip()
            
            # Extract subsidy information
            subsidy_matches = re.findall(self.scheme_patterns['subsidy'], section, re.IGNORECASE)
            if subsidy_matches:
                scheme['subsidy_info'] = ', '.join(subsidy_matches)
            
            # Extract deadline
            deadline_match = re.search(self.scheme_patterns['deadline'], section, re.IGNORECASE)
            if deadline_match:
                scheme['deadline'] = deadline_match.group(1).strip()
            
            # Extract contact information
            contact_match = re.search(self.scheme_patterns['contact'], section, re.IGNORECASE)
            if contact_match:
                scheme['contact'] = contact_match.group(1).strip()
            
            # Extract key features using NLP
            if self.nlp:
                doc = self.nlp(section)
                features = []
                for sent in doc.sents:
                    if any(keyword in sent.text.lower() for keyword in ['benefit', 'feature', 'provide', 'offer']):
                        features.append(sent.text.strip())
                scheme['key_features'] = features[:3]  # Top 3 features
            
            scheme['content'] = section[:500] + "..." if len(section) > 500 else section
            scheme['extracted_date'] = datetime.now().isoformat()
            
            if len(scheme) > 2:  # Only add if we extracted meaningful data
                schemes.append(scheme)
        
        return schemes
    
    def extract_weather_data(self, text: str) -> List[Dict[str, Any]]:
        """Extract weather and rainfall data from text"""
        text = self._safe_translate(text)
        weather_data = []
        
        # Split into lines for better parsing
        lines = text.split('\n')
        
        for line in lines:
            if len(line.strip()) < 10:
                continue
                
            weather_record = {}
            
            # Extract rainfall
            rainfall_match = re.search(self.weather_patterns['rainfall'], line, re.IGNORECASE)
            if rainfall_match:
                weather_record['rainfall_mm'] = float(rainfall_match.group(1))
            
            # Extract temperature
            temp_match = re.search(self.weather_patterns['temperature'], line, re.IGNORECASE)
            if temp_match:
                weather_record['temperature_c'] = float(temp_match.group(1))
            
            # Extract humidity
            humidity_match = re.search(self.weather_patterns['humidity'], line, re.IGNORECASE)
            if humidity_match:
                weather_record['humidity_percent'] = float(humidity_match.group(1))
            
            # Extract date
            date_match = re.search(self.weather_patterns['date'], line)
            if date_match:
                weather_record['date'] = date_match.group(1)
            
            # Extract location using NLP
            if self.nlp:
                doc = self.nlp(line)
                locations = [ent.text for ent in doc.ents if ent.label_ in ['GPE', 'LOC']]
                if locations:
                    weather_record['location'] = locations[0]
            
            weather_record['source_text'] = line
            weather_record['extracted_date'] = datetime.now().isoformat()
            
            if len(weather_record) > 2:
                weather_data.append(weather_record)
        
        return weather_data
    
    def extract_cost_data(self, text: str) -> List[Dict[str, Any]]:
        """Extract cost and pricing information from text"""
        text = self._safe_translate(text)
        cost_data = []
        
        lines = text.split('\n')
        
        for line in lines:
            if len(line.strip()) < 10:
                continue
                
            cost_record = {}
            
            # Extract price
            price_matches = re.findall(self.cost_patterns['price'], line, re.IGNORECASE)
            if price_matches:
                # Convert to float, removing commas
                price_str = price_matches[0].replace(',', '')
                try:
                    cost_record['price'] = float(price_str)
                except ValueError:
                    cost_record['price_text'] = price_matches[0]
            
            # Extract unit
            unit_match = re.search(self.cost_patterns['unit'], line, re.IGNORECASE)
            if unit_match:
                cost_record['unit'] = unit_match.group(1).strip()
            
            # Extract material/item
            material_match = re.search(self.cost_patterns['material'], line, re.IGNORECASE)
            if material_match:
                cost_record['material'] = material_match.group(1).strip()
            
            # Extract supplier
            supplier_match = re.search(self.cost_patterns['supplier'], line, re.IGNORECASE)
            if supplier_match:
                cost_record['supplier'] = supplier_match.group(1).strip()
            
            cost_record['source_text'] = line
            cost_record['extracted_date'] = datetime.now().isoformat()
            
            if len(cost_record) > 2:
                cost_data.append(cost_record)
        
        return cost_data
    
    def extract_technical_resources(self, text: str) -> List[Dict[str, Any]]:
        """Extract technical guidelines and resources"""
        text = self._safe_translate(text)
        resources = []
        
        # Split into sections
        sections = re.split(r'\n\s*\n|\.\s*(?=[A-Z])', text)
        
        for section in sections:
            if len(section.strip()) < 100:
                continue
                
            resource = {}
            
            # Extract title/heading
            lines = section.split('\n')
            potential_title = lines[0].strip()
            if len(potential_title) < 100:
                resource['title'] = potential_title
            
            # Extract technical specifications
            if any(keyword in section.lower() for keyword in ['specification', 'requirement', 'standard', 'guideline']):
                resource['type'] = 'technical_specification'
            elif any(keyword in section.lower() for keyword in ['procedure', 'process', 'step', 'method']):
                resource['type'] = 'procedure'
            elif any(keyword in section.lower() for keyword in ['regulation', 'law', 'act', 'rule']):
                resource['type'] = 'regulation'
            else:
                resource['type'] = 'general'
            
            # Extract key points using sentence analysis
            if self.nlp:
                doc = self.nlp(section)
                key_points = []
                for sent in doc.sents:
                    if len(sent.text.strip()) > 20 and any(keyword in sent.text.lower() 
                                                          for keyword in ['must', 'should', 'required', 'important', 'ensure']):
                        key_points.append(sent.text.strip())
                resource['key_points'] = key_points[:5]  # Top 5 key points
            
            resource['content'] = section[:1000] + "..." if len(section) > 1000 else section
            resource['extracted_date'] = datetime.now().isoformat()
            
            if len(resource) > 2:
                resources.append(resource)
        
        return resources
    
    def classify_content_type(self, text: str) -> str:
        """Classify the type of content"""
        text_lower = text.lower()
        
        # Government schemes keywords
        scheme_keywords = ['scheme', 'yojana', 'subsidy', 'grant', 'eligibility', 'application']
        if sum(1 for keyword in scheme_keywords if keyword in text_lower) >= 2:
            return 'government_scheme'
        
        # Weather keywords
        weather_keywords = ['rainfall', 'temperature', 'weather', 'precipitation', 'humidity', 'forecast']
        if sum(1 for keyword in weather_keywords if keyword in text_lower) >= 2:
            return 'weather_data'
        
        # Cost keywords
        cost_keywords = ['price', 'cost', 'rate', 'amount', 'rs', '₹', 'supplier', 'vendor']
        if sum(1 for keyword in cost_keywords if keyword in text_lower) >= 2:
            return 'cost_data'
        
        # Technical keywords
        tech_keywords = ['guideline', 'specification', 'standard', 'procedure', 'technical', 'regulation']
        if sum(1 for keyword in tech_keywords if keyword in text_lower) >= 2:
            return 'technical_resource'
        
        return 'general'
    
    def extract_structured_data(self, text: str, content_type: str = None) -> List[Dict[str, Any]]:
        """Extract structured data based on content type"""
        if not content_type:
            content_type = self.classify_content_type(text)
        
        logger.info(f"Extracting {content_type} data")
        
        if content_type == 'government_scheme':
            return self.extract_government_schemes(text)
        elif content_type == 'weather_data':
            return self.extract_weather_data(text)
        elif content_type == 'cost_data':
            return self.extract_cost_data(text)
        elif content_type == 'technical_resource':
            return self.extract_technical_resources(text)
        else:
            # Generic extraction
            return [{'content': text[:1000], 'type': 'general', 'extracted_date': datetime.now().isoformat()}]

if __name__ == "__main__":
    # Test the AI content extractor
    extractor = AIContentExtractor()
    
    # Test text
    test_text = """
    Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)
    Eligibility: All farmers with valid land records
    Subsidy: Up to Rs. 50,000 per hectare for drip irrigation
    Deadline: Applications must be submitted by March 31, 2024
    Contact: District Collector Office
    """
    
    schemes = extractor.extract_government_schemes(test_text)
    print(f"Extracted {len(schemes)} government schemes")
    for scheme in schemes:
        print(json.dumps(scheme, indent=2))
