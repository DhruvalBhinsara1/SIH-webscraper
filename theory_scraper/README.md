# Theory Scraper - PDF Content Extraction

This module extracts rainwater harvesting theory and technical content from government PDF documents using advanced text processing and pattern matching.

## 🎯 Purpose

Extracts comprehensive theory content from government PDFs including:
- Technical guidelines and specifications
- Design and construction standards  
- Cost analysis and economic data
- Maintenance procedures and best practices
- Government regulations and policies

## 📁 Files

### Core Scripts
- `fixed_pdf_scraper.py` - Main PDF extraction engine with robust error handling
- `requirements_enhanced.txt` - Python dependencies for PDF processing

### Output Directory
- `output/` - Contains extracted theory data in JSON and CSV formats
- Latest extraction: `fixed_pdf_extraction_20250902_131343.*` (533 theory items)

## 🚀 Usage

```bash
# Run theory extraction from all config PDFs
cd theory_scraper
python fixed_pdf_scraper.py
```

## 📊 Results

**Latest Extraction (2025-09-02):**
- ✅ 22 PDFs processed from centralized config
- ✅ 12 successful extractions (54% success rate)
- ✅ 533 theory items extracted
- ✅ Categorized into: guidelines, systems, economics, maintenance, etc.

## 🔧 Features

- **Centralized Configuration**: Uses URLs from main `config.py`
- **Progress Tracking**: Real-time ETA and completion status
- **Robust Extraction**: Handles complex PDF layouts and formatting
- **Error Recovery**: Retries failed downloads with detailed logging
- **Content Categorization**: Automatically categorizes extracted content
- **Deduplication**: Removes duplicate content and ranks by relevance

## 📋 Output Format

### JSON Structure
```json
{
  "success": true,
  "url": "https://example.gov.in/manual.pdf",
  "theory_items": [
    {
      "title": "Rainwater Harvesting Guidelines",
      "content": "Detailed technical content...",
      "category": "guidelines",
      "keywords": ["harvesting", "guidelines", "technical"],
      "source_url": "https://example.gov.in/manual.pdf",
      "relevance_score": 8,
      "content_length": 1250
    }
  ]
}
```

## 🛠️ Dependencies

```bash
pip install requests pdfplumber PyPDF2 pandas
```

## 📈 Performance

- **Processing Speed**: ~12 seconds per PDF average
- **Extraction Quality**: 44+ theory items per successful PDF
- **Content Coverage**: Full sentences and paragraphs vs snippets
- **Success Rate**: 54% (limited by broken government links)
