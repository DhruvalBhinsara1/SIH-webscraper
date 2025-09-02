# URL Tools - URL Management & Discovery System

This module provides intelligent URL management, validation, and discovery tools for maintaining and expanding the scraper's data sources.

## 🎯 Purpose

The URL tools help you:
- **Validate existing URLs** to ensure they're still working and contain data
- **Discover new URLs** from seed sources to expand data collection
- **Categorize URLs** automatically based on content type and relevance
- **Explore websites** to find the best data-containing sub-pages

## 📁 Files

### Core Tools
- `url_validator.py` - Validates URLs and discovers data-containing sub-pages
- `url_discovery_system.py` - Automatically discovers new URLs from seed URLs  
- `link_explorer.py` - Explores websites to find actual data-containing pages
- `intelligent_url_categorizer.py` - AI-powered URL categorization system

### Configuration & Data
- `existing_urls.json` - Database of known URLs by category
- `__init__.py` - Package initialization

## 🚀 Usage

### 1. Validate Existing URLs
```python
from url_tools.url_validator import URLValidator

validator = URLValidator()
results = validator.validate_category_urls(
    ScraperConfig.GOVERNMENT_SCHEMES_URLS, 
    'government_schemes'
)

print(f"✅ Valid URLs: {len(results['valid_urls'])}")
print(f"❌ Invalid URLs: {len(results['invalid_urls'])}")
print(f"🔍 Discovered links: {len(results['discovered_links'])}")
```

### 2. Discover New URLs
```python
# In config.py - Add to appropriate category
GOVERNMENT_SCHEMES_URLS = [
    # ... existing URLs ...
    'https://new-government-portal.gov.in/schemes',  # ✅ Validated
    'https://another-source.gov.in/subsidies',       # ✅ Validated
]
```

### **Scenario 2: Discovering URLs from Existing Sources**

**Step 1: Load Current Configuration**
```bash
python url_tools/url_discovery_system.py
```
```python
from url_tools.url_discovery_system import URLDiscoverySystem

discovery = URLDiscoverySystem()

# Load existing URLs from config.py
existing_urls = discovery.load_existing_urls()
print("📋 Current URL counts:")
for category, urls in existing_urls.items():
    print(f"  {category}: {len(urls)} URLs")
```

**Step 2: Discover New URLs from Seeds**
```python
# Use existing valid URLs as seeds to find more
seed_urls = list(existing_urls['government_schemes'])[:10]  # Use first 10 as seeds

new_discoveries = discovery.discover_new_urls(
    seed_urls=seed_urls,
    existing_urls=existing_urls['government_schemes'],
    min_relevance=3,  # Only high-quality URLs
    validate_new=True
)

print(f"🆕 Discovered {len(new_discoveries)} new URLs:")
for discovery in new_discoveries[:5]:  # Show top 5
    print(f"  {discovery['relevance']}/10 - {discovery['type']} - {discovery['url']}")
    print(f"      Source: {discovery['source_seed']}")
```

**Step 3: Validate Discoveries**
```python
from url_tools.url_validator import URLValidator

validator = URLValidator()

# Validate the discovered URLs
validated_discoveries = []
for discovery in new_discoveries:
    is_valid, content_type, sub_links = validator.validate_url(discovery['url'])
    if is_valid:
        discovery['validated'] = True
        discovery['sub_links_count'] = len(sub_links)
        validated_discoveries.append(discovery)

print(f"✅ {len(validated_discoveries)} URLs validated successfully")
```

**Step 4: Update Config with Best URLs**
```python
# Add best validated URLs to config.py
best_urls = [d['url'] for d in validated_discoveries if d['relevance'] >= 5]
print(f"🎯 Recommended URLs to add to config: {len(best_urls)}")
for url in best_urls:
    print(f"  {url}")
```

## 🚀 Quick Commands

### **Validate All Current URLs**
```bash
# Check if all URLs in config.py are still working
python -c "
from url_tools.url_validator import URLValidator
from config import ScraperConfig

validator = URLValidator()
categories = ['government_schemes', 'marketplace', 'technical_resources', 'weather']

for category in categories:
    urls = getattr(ScraperConfig, f'{category.upper()}_URLS', [])
    if urls:
        results = validator.validate_category_urls(urls, category)
        print(f'{category}: {len(results[\"valid_urls\"])}/{len(urls)} valid')
"
```

### **Discover URLs from Best Sources**
```bash
# Discover new URLs from high-quality seed sources
python -c "
from url_tools.url_discovery_system import URLDiscoverySystem

discovery = URLDiscoverySystem()
existing = discovery.load_existing_urls()

seeds = [
    'https://jalshakti-dowr.gov.in/schemes',
    'https://pmksy.gov.in/',
    'https://cgwb.gov.in/'
]

new_urls = discovery.discover_new_urls(seeds, existing['government_schemes'])
print(f'Found {len(new_urls)} new URLs')
for url in new_urls[:5]:
    print(f'  {url[\"relevance\"]}/10 - {url[\"url\"]}')
"
```

### **Complete URL Audit**
```bash
# Run complete URL management workflow
python -c "
from url_tools.url_validator import URLValidator
from url_tools.url_discovery_system import URLDiscoverySystem
from config import ScraperConfig

# Validate existing
validator = URLValidator()
validation = validator.validate_category_urls(ScraperConfig.GOVERNMENT_SCHEMES_URLS, 'government_schemes')

# Discover new
discovery = URLDiscoverySystem()
existing = discovery.load_existing_urls()
new_urls = discovery.discover_new_urls(validation['valid_urls'][:5], existing['government_schemes'])

print('🔍 URL Audit Results:')
print(f'  Valid existing: {len(validation[\"valid_urls\"])}')
print(f'  Invalid to remove: {len(validation[\"invalid_urls\"])}')
print(f'  New discoveries: {len(new_urls)}')
print(f'  High-quality pages: {len(validation[\"high_quality_pages\"])}')
"
```

## 🎯 Best Practices

### **When to Use Each Tool**

1. **`url_validator.py`** - Use when:
   - Adding new URLs to config
   - Checking if existing URLs still work
   - Finding sub-pages from known URLs

2. **`link_explorer.py`** - Use when:
   - Exploring a specific website in detail
   - Finding PDF documents and resources
   - Analyzing content quality of pages

3. **`url_discovery_system.py`** - Use when:
   - Expanding your URL collection
   - Finding new data sources automatically
   - Regular maintenance of URL lists

### **Recommended Schedule**

- **Weekly**: Run `url_validator.py` to check existing URLs
- **Monthly**: Run `url_discovery_system.py` to find new sources
- **As needed**: Use `link_explorer.py` for specific site exploration

### **Quality Filters**

- **Minimum relevance score**: 3/10 for auto-discovery
- **Content quality threshold**: 5/10 for high-quality pages
- **Validation required**: Always validate before adding to config

## 🔧 Integration with Main Scraper

After using URL tools to update `config.py`, run the main scraper:

```bash
# After updating URLs in config.py
python final_multilingual_scraper.py
```

The scraper will automatically use the updated URLs from your configuration file.
