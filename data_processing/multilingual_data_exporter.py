#!/usr/bin/env python3
"""
Multilingual Data Exporter
Exports scraped data in multiple Indian languages with single file per category
"""

import json
import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultilingualDataExporter:
    """Exports data in multiple Indian languages"""
    
    def __init__(self, output_dir: str = 'output'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Supported languages with their codes
        self.languages = {
            'en': 'English',
            'hi': 'Hindi',
            'bn': 'Bengali', 
            'te': 'Telugu',
            'mr': 'Marathi',
            'ta': 'Tamil',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'pa': 'Punjabi',
            'or': 'Odia'
        }
        
        # Field translations for different languages
        self.field_translations = {
            'en': {
                'name': 'Name',
                'description': 'Description',
                'eligibility': 'Eligibility',
                'benefits': 'Benefits',
                'cost': 'Cost',
                'location': 'Location',
                'source': 'Source',
                'category': 'Category',
                'price': 'Price',
                'supplier': 'Supplier',
                'specifications': 'Specifications',
                'temperature': 'Temperature',
                'humidity': 'Humidity',
                'rainfall': 'Rainfall',
                'forecast': 'Forecast'
            },
            'hi': {
                'name': 'नाम',
                'description': 'विवरण',
                'eligibility': 'पात्रता',
                'benefits': 'लाभ',
                'cost': 'लागत',
                'location': 'स्थान',
                'source': 'स्रोत',
                'category': 'श्रेणी',
                'price': 'मूल्य',
                'supplier': 'आपूर्तिकर्ता',
                'specifications': 'विशिष्टताएं',
                'temperature': 'तापमान',
                'humidity': 'आर्द्रता',
                'rainfall': 'वर्षा',
                'forecast': 'पूर्वानुमान'
            },
            'bn': {
                'name': 'নাম',
                'description': 'বিবরণ',
                'eligibility': 'যোগ্যতা',
                'benefits': 'সুবিধা',
                'cost': 'খরচ',
                'location': 'অবস্থান',
                'source': 'উৎস',
                'category': 'বিভাগ',
                'price': 'দাম',
                'supplier': 'সরবরাহকারী',
                'specifications': 'বিশেষত্ব',
                'temperature': 'তাপমাত্রা',
                'humidity': 'আর্দ্রতা',
                'rainfall': 'বৃষ্টিপাত',
                'forecast': 'পূর্বাভাস'
            }
            # Add more language translations as needed
        }
    
    def translate_field_names(self, data: List[Dict], lang_code: str) -> List[Dict]:
        """Translate field names to specified language"""
        if lang_code not in self.field_translations:
            return data
        
        translations = self.field_translations[lang_code]
        translated_data = []
        
        for item in data:
            translated_item = {}
            for key, value in item.items():
                translated_key = translations.get(key, key)
                translated_item[translated_key] = value
            translated_data.append(translated_item)
        
        return translated_data
    
    def export_data_multilingual(self, data: List[Dict], data_type: str) -> Dict[str, str]:
        """Export data in all languages to single JSON and CSV files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create combined data structure
        combined_data = {
            'metadata': {
                'export_timestamp': timestamp,
                'data_type': data_type,
                'total_records': len(data),
                'languages_included': list(self.languages.keys()),
                'export_format': 'Single file with all languages'
            },
            'data_by_language': {}
        }
        
        # Add data for each language
        for lang_code, lang_name in self.languages.items():
            translated_data = self.translate_field_names(data, lang_code)
            combined_data['data_by_language'][lang_code] = {
                'language_name': lang_name,
                'records': translated_data
            }
        
        # Export to JSON
        json_filename = f'{data_type}_multilingual_{timestamp}.json'
        json_path = os.path.join(self.output_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
        
        # Export to CSV (flatten structure)
        csv_data = []
        for lang_code, lang_data in combined_data['data_by_language'].items():
            for record in lang_data['records']:
                flattened_record = {
                    'language_code': lang_code,
                    'language_name': lang_data['language_name'],
                    **record
                }
                csv_data.append(flattened_record)
        
        csv_filename = f'{data_type}_multilingual_{timestamp}.csv'
        csv_path = os.path.join(self.output_dir, csv_filename)
        
        if csv_data:
            df = pd.DataFrame(csv_data)
            df.to_csv(csv_path, index=False, encoding='utf-8')
        
        logger.info(f"Exported {data_type} data to {json_filename} and {csv_filename}")
        
        return {
            'json': json_path,
            'csv': csv_path,
            'languages_included': list(self.languages.keys()),
            'total_records': len(data)
        }
    
    def export_government_schemes(self, schemes_data: List[Dict]) -> Dict[str, str]:
        """Export government schemes data in all languages to single files"""
        return self.export_data_multilingual(schemes_data, 'government_schemes')
    
    def export_cost_data(self, cost_data: List[Dict]) -> Dict[str, str]:
        """Export cost data in all languages to single files"""
        return self.export_data_multilingual(cost_data, 'cost_data')
    
    def export_weather_data(self, weather_data: List[Dict]) -> Dict[str, str]:
        """Export weather data in all languages to single files"""
        return self.export_data_multilingual(weather_data, 'weather_data')
    
    def export_technical_resources(self, tech_data: List[Dict]) -> Dict[str, str]:
        """Export technical resources in all languages to single files"""
        return self.export_data_multilingual(tech_data, 'technical_resources')
    
    def export_all_data(self, all_data: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """Export all data categories in multilingual format"""
        export_results = {}
        
        for data_type, data_list in all_data.items():
            if data_list:  # Only export if data exists
                export_results[data_type] = self.export_data_multilingual(data_list, data_type)
        
        # Create summary report
        summary_file = self.create_summary_report(export_results)
        logger.info(f"Created export summary: {summary_file}")
        
        return export_results
    
    def create_summary_report(self, export_results: Dict) -> str:
        """Create a summary report of all exports"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = os.path.join(self.output_dir, f'export_summary_{timestamp}.json')
        
        summary = {
            'export_timestamp': timestamp,
            'languages_supported': list(self.languages.keys()),
            'total_languages': len(self.languages),
            'export_format': 'Single file per category with all languages',
            'export_results': export_results,
            'files_created': []
        }
        
        # Count total files created (now just 2 per category: JSON + CSV)
        for data_type, files_info in export_results.items():
            if isinstance(files_info, dict) and 'json' in files_info:
                summary['files_created'].extend([files_info['json'], files_info['csv']])
        
        summary['total_files_created'] = len(summary['files_created'])
        summary['categories_exported'] = len(export_results)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        return summary_file

def main():
    """Main export function - processes all data types"""
    exporter = MultilingualDataExporter()
    
    # Sample data for testing
    sample_data = {
        'government_schemes': [
            {
                'name': 'Test Scheme',
                'description': 'Sample scheme for testing',
                'cost': '₹10,000',
                'location': 'All India'
            }
        ]
    }
    
    results = exporter.export_all_data(sample_data)
    print("Export completed:", results)

if __name__ == "__main__":
    main()
