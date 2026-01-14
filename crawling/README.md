# Crawling Module

This folder contains web scraping and data collection tools for gathering information about lower back pain (LBP) from various health information sources.

## Overview

The crawling module is responsible for collecting health education materials, clinical practice guidelines, and research articles about lower back pain. The collected data is stored in XML format for further processing in the RAG (Retrieval-Augmented Generation) system.

## Files

### Python Scripts

#### `medline.py`
Main scraper for MedlinePlus health topics using the NLM (National Library of Medicine) search API.

**Key Functions:**
- `search_results(query)` - Searches MedlinePlus health topics database
- `parse_search_results(xml_data)` - Extracts URLs from search results
- `scrape_page(url)` - Scrapes main content from web pages
- `extract_pdf(url)` - Extracts text from PDF documents
- `extract_links(soup)` - Finds and filters relevant links from pages
- `save_page_to_xml(data, output_folder_path, filename)` - Saves content to XML format

**Usage:**
```bash
python medline.py
```

The script searches for terms like "lower back pain", "physical therapy", and "rehabilitation", then scrapes both main pages and linked subpages. PDF content is also extracted when encountered.

#### `scrape.py`
General-purpose web scraper for extracting content from various health websites.

**Key Functions:**
- `scrape_page(url)` - Scrapes web pages with random user agents and delays
- `extract_pdf(file)` - Extracts text from local PDF files
- `save_to_xml(data, output_folder_path, filename)` - Saves scraped content to XML
- `sanitize_filename(title)` - Cleans filenames for safe file system storage

**Usage:**
```bash
python scrape.py
```

This script processes:
- A predefined list of health website URLs (CDC, Cleveland Clinic, Penn Medicine, etc.)
- Clinical practice guidelines (PDFs in `clinical_practice_guide/`)
- Journal articles (PDFs in `journal_articles/`)

**Features:**
- Random delays between requests (1-3 seconds) to avoid overwhelming servers
- User agent rotation for better scraping reliability
- Handles both web pages and PDF documents
- Extracts image URLs from scraped pages
- Filters out non-English content (Spanish links)

### Configuration File

#### `medlineplus.xml`
Contains search results or configuration data for MedlinePlus scraping operations.

## Data Directories

### `data/`
Contains 100+ XML files with scraped health education content about lower back pain. Each XML file represents one web page or document with the following structure:
```xml
<page>
  <title>Page Title</title>
  <url>Source URL</url>
  <content>Main content text...</content>
  <images>
    <image>Image URL</image>
  </images>
</page>
```

**Topics include:**
- Back pain causes, symptoms, and treatments
- Physical therapy and rehabilitation
- Ergonomics and workplace health
- Pregnancy-related back pain
- Chiropractic care
- Pain management strategies
- Assistive devices and mobility aids

### `clinical_practice_guide/`
Contains clinical practice guideline PDFs from major health organizations:
- Academy of Orthopaedic Physical Therapy
- American Association of Family Physicians
- American College of Physicians
- Australian guidelines
- Canadian guidelines
- Kaiser Permanente
- North American Spine Society
- VA/Department of Defense
- World Health Organization

See [clinical_practice_guide/README.md](clinical_practice_guide/README.md) for details.

### `journal_articles/`
Contains peer-reviewed research articles in PDF format about lower back pain interventions and evidence-based treatments.

Articles include:
- Crowe et al. - Research on LBP interventions
- Geraghty et al. - Clinical studies
- Kongsted et al. - Treatment effectiveness
- Yang et al. - Evidence synthesis
- Support materials for back pain action programs

See [journal_articles/README.md](journal_articles/README.md) for details.

### `split_sections/`
Contains scripts to process and segment the scraped content into smaller sections for more granular retrieval in the RAG system.

### `removed_resources/`
Archive of resources that were removed from the main dataset, possibly due to quality issues, duplicates, or relevance filtering.

## Dependencies

Required Python packages:
```
requests
beautifulsoup4
PyPDF2
lxml (for XML processing)
```

Install with:
```bash
pip install requests beautifulsoup4 PyPDF2 lxml
```

## Data Collection Workflow

1. **Search Phase**: Query health databases for relevant topics
2. **Scraping Phase**: Extract content from identified web pages
3. **PDF Processing**: Extract text from clinical guidelines and research articles
4. **Link Following**: Recursively scrape linked pages (medline.py)
5. **Content Cleaning**: Remove navigation, headers, footers, scripts
6. **XML Storage**: Save structured data to XML files

## Best Practices

- **Rate Limiting**: Scripts include random delays to avoid overwhelming servers
- **User Agent Rotation**: Multiple user agents used to mimic normal browsing
- **Error Handling**: Graceful handling of PDF extraction errors and missing content
- **Filename Sanitization**: Automatic cleaning of filenames for cross-platform compatibility
- **Content Filtering**: Excludes non-English content and irrelevant sections

## Output

All scraped content is saved to the `data/` directory in XML format. The XML structure ensures:
- Easy parsing for downstream processing
- Preservation of source URLs for citation
- Separation of content from metadata
- Optional image URL tracking

## Notes

- The scrapers are designed to be respectful of source websites with appropriate delays
- PDF extraction requires PyPDF2 and may not work perfectly with all PDF formats
- Some content may require manual review for quality assurance
- The XML files are the input for the RAG system's document retrieval component
