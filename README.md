# RAG System for Lower Back Pain Patient Education

A Retrieval-Augmented Generation (RAG) system that generates personalized, evidence-based patient education materials for lower back pain management using large language models and clinical knowledge bases.

## Project Overview

This research project develops and evaluates an AI-powered system to create tailored patient education materials for individuals with lower back pain (LBP). The system combines:
- **Evidence-based health content** from trusted medical sources
- **Large language models** (GPT-4, GPT-3.5, GPT-4o, Llama3 variants)
- **Retrieval-augmented generation** to ground responses in clinical guidelines
- **Rigorous evaluation** by physical therapy domain experts

**Goal:** Generate high-quality, personalized education materials that are accurate, complete, readable, and tailored to individual patient characteristics and beliefs about back pain.

## Repository Structure

This repository contains three main modules that form a complete pipeline from data collection to evaluation:

```
rag-for-lbp-github/
├── crawling/              # Data collection and knowledge base creation
├── langchain_testing/     # RAG system implementation and testing
├── evaluation/            # Quality assessment and statistical analysis
└── README.md             # This file
```

## Module Tour

### 1. Crawling Module ([`crawling/`](crawling/README.md))

**What it does:** Collects and processes health education content about lower back pain from authoritative sources.

**Key Components:**
- **Web scrapers** (`medline.py`, `scrape.py`) - Automated collection of health information from MedlinePlus, CDC, medical organizations
- **Clinical practice guidelines** - Evidence-based recommendations from major healthcare organizations (WHO, VA/DoD, APTA, etc.)
- **Journal articles** - Peer-reviewed research on LBP interventions and treatments
- **Data processing** - Converts raw content to structured XML format

**Data Sources:**
- 200+ health education documents
- 10 clinical practice guidelines from international health organizations
- 5 peer-reviewed journal articles
- Topics: back pain management, ergonomics, physical therapy, pain science, exercise

**Output:** Structured XML files ready for embedding and retrieval

[View Crawling Module Details](crawling/README.md)

---

### 2. LangChain Testing Module ([`langchain_testing/`](langchain_testing/README.md))

**What it does:** Implements the RAG system that generates personalized patient education materials.

**Key Components:**
- **Document Processing** - Loads XML files, splits into chunks, creates vector embeddings
- **Vector Database** - ChromaDB stores embeddings for semantic search
- **RAG Pipeline** - Retrieves relevant content and generates responses using LLMs
- **Model Configurations**:
  - **RAGFS** (RAG + Few-Shot): Retrieval with example-based formatting
  - **RAGNFS** (RAG No Few-Shot): Retrieval without examples
  - **NRAG** (No RAG): LLM baseline for comparison

**Models Tested:**
- GPT-4 (all configurations)
- GPT-4o and GPT-4o-mini variants
- GPT-3.5-turbo
- Llama3 (optional)

**Testing Approach:**
- 30 synthetic patient profiles with varying:
  - Work status and activity levels
  - Exercise habits
  - Beliefs about back pain treatments
  - Confidence in ergonomics and lifting techniques
- Generates personalized recommendations for each profile
- Compares quality across models and configurations

**Key Files:**
- `rag_model.py` - Conversational RAG with chat history
- `testing.py` - Batch testing and education material generation
- `synthetic_patients.txt` - Patient profiles for testing
- `.env.example` - Configuration template (API keys)

**Output:** CSV files with generated education materials for evaluation

[View LangChain Testing Module Details](langchain_testing/README.md)

---

### 3. Evaluation Module ([`evaluation/`](evaluation/README.md))

**What it does:** Assesses the quality of generated education materials through expert evaluation and readability analysis.

**Evaluation Dimensions:**

**1. Content Quality (Expert Review)**
- **Redundancy** - Unnecessary repetition (lower is better)
- **Accuracy** - Medical correctness (higher is better)
- **Completeness** - Coverage of relevant topics (higher is better)
- Two independent physical therapist evaluators
- Blinded assessment process

**2. Readability Analysis**
- Flesch Reading Ease scores
- Flesch-Kincaid Grade Level
- Target: 6th grade reading level for health literacy
- Automated analysis using `fkscore` library

**3. Statistical Analysis**
- **ANOVA** - Tests for significant differences between models
- **ICC** (Intraclass Correlation) - Inter-rater reliability measurement
- **Standard Deviation** - Evaluator consistency assessment

**4. Visualization**
- Radar plots comparing models across all dimensions
- Interactive plots using Plotly
- Normalized metrics for fair comparison

**Key Scripts:**
- `evaluation_metrics.py` - Combines evaluator data
- `readability_test.py` - Calculates readability scores
- `anova.py` - Statistical significance testing
- `icc.py` - Inter-rater reliability
- `radar_plot.py` - Multi-dimensional visualization

**Output:** Statistical reports, visualization plots, aggregated metrics

[View Evaluation Module Details](evaluation/README.md)

---

## Quick Start

### Prerequisites

```bash
# Python 3.8+
pip install langchain langchain-chroma langchain-openai langchain-community
pip install openai chromadb pandas plotly statsmodels pingouin fkscore
pip install beautifulsoup4 requests PyPDF2 python-dotenv
```

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/rag-for-lbp-github.git
cd rag-for-lbp-github
```

2. **Set up API keys:**
```bash
cd langchain_testing
cp .env.example .env
# Edit .env and add your API keys
```

3. **Ensure data is available:**
```bash
# The crawling/data/ folder should contain XML files
# If not, run the crawlers to collect data
cd ../crawling
python scrape.py
```

### Run the System

**Generate education materials:**
```bash
cd langchain_testing
python testing.py
```

**Evaluate outputs:**
```bash
cd ../evaluation
python readability_test.py
python evaluation_metrics.py
python radar_plot.py
```

## Research Workflow

### End-to-End Pipeline

```
1. Data Collection (crawling/)
   └─> Scrape health websites
   └─> Process clinical guidelines
   └─> Convert to structured XML
          ↓
2. RAG System (langchain_testing/)
   └─> Load and chunk documents
   └─> Create vector embeddings
   └─> Build retrieval system
   └─> Generate personalized content
          ↓
3. Evaluation (evaluation/)
   └─> Expert quality assessment
   └─> Readability analysis
   └─> Statistical testing
   └─> Visualization and reporting
```

### Research Questions Addressed

1. **Does RAG improve content quality?**
   - Compare RAGFS/RAGNFS vs. NRAG configurations
   - Measure accuracy and completeness

2. **Do few-shot examples enhance outputs?**
   - Compare RAGFS vs. RAGNFS
   - Assess formatting consistency

3. **Which model performs best?**
   - Cross-model comparison (GPT-4, GPT-4o, GPT-3.5)
   - Multi-objective optimization

4. **Is there a quality-readability trade-off?**
   - Correlation between comprehensiveness and reading ease
   - Balance expert content with accessibility

5. **Are evaluations reliable?**
   - ICC calculation for inter-rater agreement
   - Consistency analysis

## Key Findings (Preliminary)

Based on radar plot analysis:

**Best Overall Performers:**
- **GPT-4o + RAGFS**: Highest accuracy (73.6), excellent readability (95.73)
- **GPT-4 + RAGFS**: Most balanced across all metrics

**Trade-offs:**
- RAG configurations improve accuracy and completeness
- Non-RAG tends to have lower redundancy
- Few-shot examples enhance readability consistency

**Readability Leaders:**
- GPT-4 RAGFS: 103.33 (extremely readable)
- GPT-4o RAGFS: 95.73 (6th-7th grade level)

## Technical Stack

- **Language Models:** OpenAI GPT-4, GPT-4o, GPT-3.5-turbo, Llama3
- **Framework:** LangChain (RAG orchestration)
- **Vector Database:** ChromaDB (semantic search)
- **Embeddings:** OpenAI text-embedding-ada-002
- **Web Scraping:** BeautifulSoup, Requests
- **Analysis:** Pandas, Statsmodels, Pingouin
- **Visualization:** Plotly
- **Readability:** fkscore (Flesch-Kincaid)

## Documentation

Each module has detailed documentation:
- [Crawling Module README](crawling/README.md) - Data collection pipeline
- [LangChain Testing README](langchain_testing/README.md) - RAG implementation
- [Evaluation Module README](evaluation/README.md) - Assessment framework

## Security & Privacy

- API keys stored in `.env` files (not committed to repository)
- `.gitignore` prevents accidental key exposure
- Synthetic patient profiles used for testing (no real patient data)
- Health information sourced from public, authoritative websites

## Data Sources

Content is collected from trusted health organizations:
- **MedlinePlus** (U.S. National Library of Medicine)
- **CDC** (Centers for Disease Control and Prevention)
- **WHO** (World Health Organization)
- **VA/DoD** Clinical Practice Guidelines
- **Cleveland Clinic, Penn Medicine, Kaiser Permanente**
- Peer-reviewed journals and professional societies

All sources are properly cited and URLs preserved in metadata.

## Contributing

This is a research project. For questions or collaboration inquiries, please open an issue or contact the repository maintainers.

## Disclaimer

This system is designed for research purposes. Generated patient education materials should be reviewed by qualified healthcare professionals before clinical use. The system does not provide medical advice, diagnosis, or treatment.

## File Structure Overview

```
rag-for-lbp-github/
│
├── crawling/                          # Data Collection Module
│   ├── medline.py                     # MedlinePlus scraper
│   ├── scrape.py                      # General web scraper
│   ├── data/                          # 200+ XML health documents
│   ├── clinical_practice_guide/       # 10 CPG PDFs
│   ├── journal_articles/              # 5 research PDFs
│   └── README.md                      # Module documentation
│
├── langchain_testing/                 # RAG System Module
│   ├── rag_model.py                   # Conversational RAG
│   ├── testing.py                     # Batch testing script
│   ├── synthetic_patients.txt         # Test patient profiles
│   ├── data/                          # XML documents (from crawling)
│   ├── chroma_db/                     # Vector database
│   ├── .env.example                   # API key template
│   └── README.md                      # Module documentation
│
├── evaluation/                        # Evaluation Module
│   ├── evaluation_metrics.py          # Aggregate expert scores
│   ├── readability_test.py            # FK analysis
│   ├── readability_metrics.py         # Average readability
│   ├── anova.py                       # Statistical testing
│   ├── icc.py                         # Inter-rater reliability
│   ├── evaluator_sd.py                # Consistency analysis
│   ├── radar_plot.py                  # Visualization
│   ├── james_hill_evaluation.csv      # Evaluator 1 scores
│   ├── dave_thompson_evaluation.csv   # Evaluator 2 scores
│   ├── outputs/                       # Analysis results
│   └── README.md                      # Module documentation
│
└── README.md                          # This file (Project Overview)
```

## Typical Use Case

**Scenario:** Generate personalized back pain education for a patient who:
- Works full-time at a desk job
- Lifts heavy objects occasionally
- Does aerobic exercise 3x/week
- Believes exercise might worsen back pain
- Lacks confidence in proper lifting technique

**System Response:**
1. Retrieves relevant content about ergonomics, safe lifting, exercise benefits
2. Addresses misconceptions about exercise and pain
3. Provides specific desk setup recommendations
4. Offers confidence-building lifting technique guidance
5. Delivers content at 6th grade reading level
6. Cites evidence from clinical guidelines

**Result:** Personalized, evidence-based education that addresses the patient's specific situation and beliefs.

---

**For detailed information about each module, please refer to their respective README files linked throughout this document.**
