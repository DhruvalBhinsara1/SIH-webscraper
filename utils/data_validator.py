#!/usr/bin/env python3
"""
Data Validator for Jal Setu Web Scraper
Handles data validation, quality scoring, and processing
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
from urllib.parse import urlparse
import hashlib

logger = logging.getLogger(__name__)

class DataValidator:
    """Data validation and quality scoring system"""
    
    def __init__(self):
        self.required_fields = {
            'government_schemes': ['scheme_name', 'content'],
            'weather_data': ['source_text'],
            'cost_information': ['source_text'],
            'technical_resources': ['content']
        }
        
        self.quality_weights = {
            'completeness': 0.3,
            'accuracy': 0.25,
            'freshness': 0.2,
            'relevance': 0.15,
            'structure': 0.1
        }
    
    def validate_record(self, record: Dict[str, Any], data_type: str) -> Tuple[bool, List[str]]:
        """
        Validate a single data record
        
        Args:
            record: Data record to validate
            data_type: Type of data (government_schemes, weather_data, etc.)
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        required = self.required_fields.get(data_type, [])
        for field in required:
            if field not in record or not record[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate specific data types
        if data_type == 'government_schemes':
            errors.extend(self._validate_government_scheme(record))
        elif data_type == 'weather_data':
            errors.extend(self._validate_weather_data(record))
        elif data_type == 'cost_information':
            errors.extend(self._validate_cost_data(record))
        elif data_type == 'technical_resources':
            errors.extend(self._validate_technical_resource(record))
        
        # General validations
        errors.extend(self._validate_general(record))
        
        return len(errors) == 0, errors
    
    def _validate_government_scheme(self, record: Dict[str, Any]) -> List[str]:
        """Validate government scheme specific fields"""
        errors = []
        
        # Validate scheme name
        if 'scheme_name' in record:
            name = record['scheme_name']
            if len(name) < 5 or len(name) > 200:
                errors.append("Scheme name length should be between 5-200 characters")
        
        # Validate subsidy information
        if 'subsidy_info' in record:
            subsidy = record['subsidy_info']
            if not re.search(r'(\d+|rs\.?|₹)', subsidy, re.IGNORECASE):
                errors.append("Subsidy information should contain numerical values")
        
        # Validate deadline format
        if 'deadline' in record:
            deadline = record['deadline']
            if not self._is_valid_date_format(deadline):
                errors.append("Invalid deadline format")
        
        return errors
    
    def _validate_weather_data(self, record: Dict[str, Any]) -> List[str]:
        """Validate weather data specific fields"""
        errors = []
        
        # Validate rainfall values
        if 'rainfall_mm' in record:
            try:
                rainfall = float(record['rainfall_mm'])
                if rainfall < 0 or rainfall > 10000:  # Reasonable limits
                    errors.append("Rainfall value out of reasonable range (0-10000mm)")
            except (ValueError, TypeError):
                errors.append("Invalid rainfall value format")
        
        # Validate temperature values
        if 'temperature_c' in record:
            try:
                temp = float(record['temperature_c'])
                if temp < -50 or temp > 60:  # Reasonable limits for India
                    errors.append("Temperature value out of reasonable range (-50 to 60°C)")
            except (ValueError, TypeError):
                errors.append("Invalid temperature value format")
        
        # Validate humidity values
        if 'humidity_percent' in record:
            try:
                humidity = float(record['humidity_percent'])
                if humidity < 0 or humidity > 100:
                    errors.append("Humidity value should be between 0-100%")
            except (ValueError, TypeError):
                errors.append("Invalid humidity value format")
        
        return errors
    
    def _validate_cost_data(self, record: Dict[str, Any]) -> List[str]:
        """Validate cost data specific fields"""
        errors = []
        
        # Validate price values
        if 'price' in record:
            try:
                price = float(record['price'])
                if price < 0:
                    errors.append("Price cannot be negative")
                if price > 10000000:  # 1 crore limit
                    errors.append("Price value seems unreasonably high")
            except (ValueError, TypeError):
                errors.append("Invalid price value format")
        
        # Validate material/item name
        if 'material' in record:
            material = record['material']
            if len(material) < 2 or len(material) > 100:
                errors.append("Material name length should be between 2-100 characters")
        
        return errors
    
    def _validate_technical_resource(self, record: Dict[str, Any]) -> List[str]:
        """Validate technical resource specific fields"""
        errors = []
        
        # Validate content length
        if 'content' in record:
            content = record['content']
            if len(content) < 50:
                errors.append("Technical resource content too short (minimum 50 characters)")
        
        # Validate type field
        if 'type' in record:
            valid_types = ['technical_specification', 'procedure', 'regulation', 'general']
            if record['type'] not in valid_types:
                errors.append(f"Invalid resource type. Must be one of: {valid_types}")
        
        return errors
    
    def _validate_general(self, record: Dict[str, Any]) -> List[str]:
        """General validations applicable to all record types"""
        errors = []
        
        # Validate extracted_date
        if 'extracted_date' in record:
            try:
                datetime.fromisoformat(record['extracted_date'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                errors.append("Invalid extracted_date format")
        
        # Check for empty or whitespace-only values
        for key, value in record.items():
            if isinstance(value, str) and not value.strip():
                errors.append(f"Field '{key}' contains only whitespace")
        
        return errors
    
    def _is_valid_date_format(self, date_str: str) -> bool:
        """Check if string contains a valid date format"""
        date_patterns = [
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
            r'\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{2,4}',
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2},?\s+\d{2,4}'
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, date_str, re.IGNORECASE):
                return True
        return False
    
    def calculate_quality_score(self, record: Dict[str, Any], data_type: str) -> float:
        """
        Calculate quality score for a data record
        
        Args:
            record: Data record
            data_type: Type of data
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        scores = {}
        
        # Completeness score
        scores['completeness'] = self._score_completeness(record, data_type)
        
        # Accuracy score
        scores['accuracy'] = self._score_accuracy(record, data_type)
        
        # Freshness score
        scores['freshness'] = self._score_freshness(record)
        
        # Relevance score
        scores['relevance'] = self._score_relevance(record, data_type)
        
        # Structure score
        scores['structure'] = self._score_structure(record)
        
        # Calculate weighted average
        total_score = sum(scores[metric] * self.quality_weights[metric] 
                         for metric in scores)
        
        return round(total_score, 3)
    
    def _score_completeness(self, record: Dict[str, Any], data_type: str) -> float:
        """Score based on completeness of required and optional fields"""
        required = self.required_fields.get(data_type, [])
        optional_fields = {
            'government_schemes': ['eligibility', 'subsidy_info', 'deadline', 'contact', 'key_features'],
            'weather_data': ['rainfall_mm', 'temperature_c', 'humidity_percent', 'location', 'date'],
            'cost_information': ['price', 'unit', 'material', 'supplier'],
            'technical_resources': ['title', 'type', 'key_points']
        }
        
        optional = optional_fields.get(data_type, [])
        
        # Required fields score (70% weight)
        required_score = sum(1 for field in required if field in record and record[field]) / max(len(required), 1)
        
        # Optional fields score (30% weight)
        optional_score = sum(1 for field in optional if field in record and record[field]) / max(len(optional), 1)
        
        return required_score * 0.7 + optional_score * 0.3
    
    def _score_accuracy(self, record: Dict[str, Any], data_type: str) -> float:
        """Score based on data accuracy and format correctness"""
        is_valid, errors = self.validate_record(record, data_type)
        
        if is_valid:
            return 1.0
        
        # Penalize based on number of errors
        error_penalty = min(len(errors) * 0.1, 0.8)
        return max(1.0 - error_penalty, 0.2)
    
    def _score_freshness(self, record: Dict[str, Any]) -> float:
        """Score based on how recent the data is"""
        if 'extracted_date' not in record:
            return 0.5  # Neutral score if no date
        
        try:
            extracted_date = datetime.fromisoformat(record['extracted_date'].replace('Z', '+00:00'))
            now = datetime.now()
            days_old = (now - extracted_date).days
            
            if days_old <= 1:
                return 1.0
            elif days_old <= 7:
                return 0.9
            elif days_old <= 30:
                return 0.7
            elif days_old <= 90:
                return 0.5
            else:
                return 0.3
        except:
            return 0.5
    
    def _score_relevance(self, record: Dict[str, Any], data_type: str) -> float:
        """Score based on relevance to rainwater harvesting"""
        relevant_keywords = {
            'government_schemes': ['rainwater', 'harvesting', 'water', 'conservation', 'irrigation', 'watershed'],
            'weather_data': ['rainfall', 'precipitation', 'monsoon', 'weather', 'climate'],
            'cost_information': ['tank', 'pipe', 'filter', 'pump', 'storage', 'installation'],
            'technical_resources': ['guideline', 'specification', 'standard', 'procedure', 'technical']
        }
        
        keywords = relevant_keywords.get(data_type, [])
        content = str(record.get('content', '') + ' ' + record.get('source_text', '')).lower()
        
        keyword_matches = sum(1 for keyword in keywords if keyword in content)
        return min(keyword_matches / max(len(keywords), 1), 1.0)
    
    def _score_structure(self, record: Dict[str, Any]) -> float:
        """Score based on data structure and organization"""
        structure_score = 0.0
        
        # Check for proper field naming
        if any(key.strip() != key or not key for key in record.keys()):
            structure_score += 0.2
        else:
            structure_score += 0.4
        
        # Check for consistent data types
        consistent_types = True
        for key, value in record.items():
            if key.endswith('_date') and not isinstance(value, str):
                consistent_types = False
            elif key.endswith('_mm') or key.endswith('_c') or key.endswith('_percent'):
                try:
                    float(value)
                except (ValueError, TypeError):
                    consistent_types = False
        
        if consistent_types:
            structure_score += 0.3
        
        # Check for nested structure where appropriate
        if any(isinstance(value, (list, dict)) for value in record.values()):
            structure_score += 0.3
        
        return min(structure_score, 1.0)
    
    def remove_duplicates(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate records based on content similarity"""
        if not records:
            return records
        
        unique_records = []
        seen_hashes = set()
        
        for record in records:
            # Create hash based on key content fields
            content_keys = ['scheme_name', 'content', 'source_text', 'material', 'title']
            content_parts = []
            
            for key in content_keys:
                if key in record and record[key]:
                    content_parts.append(str(record[key]).strip().lower())
            
            if content_parts:
                content_hash = hashlib.md5(''.join(content_parts).encode()).hexdigest()
                
                if content_hash not in seen_hashes:
                    seen_hashes.add(content_hash)
                    unique_records.append(record)
                else:
                    logger.info(f"Removed duplicate record: {record.get('scheme_name', record.get('title', 'Unknown'))}")
        
        logger.info(f"Removed {len(records) - len(unique_records)} duplicate records")
        return unique_records
    
    def filter_by_quality(self, records: List[Dict[str, Any]], data_type: str, min_score: float = 0.5) -> List[Dict[str, Any]]:
        """Filter records by minimum quality score"""
        filtered_records = []
        
        for record in records:
            quality_score = self.calculate_quality_score(record, data_type)
            record['quality_score'] = quality_score
            
            if quality_score >= min_score:
                filtered_records.append(record)
            else:
                logger.info(f"Filtered out low quality record (score: {quality_score})")
        
        logger.info(f"Filtered {len(records) - len(filtered_records)} records below quality threshold {min_score}")
        return filtered_records
    
    def process_data(self, records: List[Dict[str, Any]], data_type: str, min_quality: float = 0.5) -> List[Dict[str, Any]]:
        """
        Complete data processing pipeline
        
        Args:
            records: Raw data records
            data_type: Type of data
            min_quality: Minimum quality score threshold
            
        Returns:
            Processed and validated records
        """
        logger.info(f"Processing {len(records)} {data_type} records")
        
        # Remove duplicates
        records = self.remove_duplicates(records)
        
        # Filter by quality
        records = self.filter_by_quality(records, data_type, min_quality)
        
        # Final validation
        valid_records = []
        for record in records:
            is_valid, errors = self.validate_record(record, data_type)
            if is_valid:
                valid_records.append(record)
            else:
                logger.warning(f"Invalid record filtered out: {errors}")
        
        logger.info(f"Final processed records: {len(valid_records)}")
        return valid_records

if __name__ == "__main__":
    # Test the data validator
    validator = DataValidator()
    
    # Test government scheme validation
    test_scheme = {
        'scheme_name': 'Test Rainwater Harvesting Scheme',
        'content': 'This is a test scheme for rainwater harvesting with subsidies',
        'subsidy_info': 'Rs. 50,000 per beneficiary',
        'deadline': '31/03/2024',
        'extracted_date': datetime.now().isoformat()
    }
    
    is_valid, errors = validator.validate_record(test_scheme, 'government_schemes')
    quality_score = validator.calculate_quality_score(test_scheme, 'government_schemes')
    
    print(f"Validation result: {is_valid}")
    print(f"Errors: {errors}")
    print(f"Quality score: {quality_score}")
