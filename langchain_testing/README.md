# LangChain Testing Module

This folder contains the implementation and testing framework for a Retrieval-Augmented Generation (RAG) system designed to generate personalized patient education materials for lower back pain (LBP) management.

## Overview

The RAG system uses LangChain, OpenAI's language models, and ChromaDB vector storage to retrieve relevant health information and generate tailored recommendations for patients based on their individual profiles and beliefs about back pain management.

## Project Architecture

The system implements a RAG pipeline that:
1. Loads XML-formatted health education documents
2. Splits documents into manageable chunks
3. Creates vector embeddings using OpenAI's embedding model
4. Stores embeddings in a ChromaDB vector database
5. Retrieves relevant context based on patient queries
6. Generates personalized education materials using various LLM configurations

## Files

### Python Scripts

#### `rag_model.py`
Implementation of a conversational RAG system with chat history support.

**Key Features:**
- **Conversational Memory**: Maintains chat history for multi-turn conversations
- **History-Aware Retrieval**: Reformulates queries based on conversation context
- **Multiple Model Support**: Tests GPT-4, GPT-3.5-turbo, GPT-4o-mini, GPT-4o, and Llama3
- **Three Configurations**:
  - `rag_few_shot`: RAG with few-shot examples for response formatting
  - `rag_no_few_shot`: RAG without few-shot examples
  - `no_rag`: LLM only (no retrieval)

**Key Functions:**
- `load_xml(folder_path)` - Loads XML documents with section-level parsing
- `calculate_folder_hash(folder_path)` - Creates hash for cache validation
- `recreate_vectorstore()` - Rebuilds vector store if source data changes
- `retriever(query)` - Custom retriever with similarity threshold filtering (≤0.4)
- `retrieval_details(query, session_id)` - Executes RAG chain with session history
- `write_to_csv_with_documents()` - Exports results with retrieved documents
- `write_to_csv()` - Exports results summary

**Configuration:**
- Chunk size: 1000 characters
- Chunk overlap: 100 characters
- Similarity threshold: 0.4
- Retrieved documents: Top 7 (filtered by threshold)
- Embedding model: `text-embedding-ada-002`

**Usage:**
```bash
python rag_model.py
```

Generates: `results_output_with_documents.csv` and `results_output.csv`

#### `testing.py`
Streamlined RAG testing script for generating patient education materials.

**Key Features:**
- **Simplified Pipeline**: Focuses on education material generation without chat history
- **LCEL (LangChain Expression Language)**: Uses modern chain composition syntax
- **Three Configurations**:
  - `_RAGFS`: RAG with few-shot prompting
  - `_RAGNFS`: RAG without few-shot prompting  
  - `_NRAG`: No RAG (LLM baseline)
- **Batch Processing**: Tests 30 synthetic patient profiles
- **Readability Focus**: Generates materials at 6th grade Flesch-Kincaid reading level

**Key Functions:**
- `format_docs(docs)` - Formats retrieved documents as context string
- `retrieval_details(chain, query, rag)` - Executes chain and handles RAG/non-RAG modes
- `write_to_csv()` - Exports results with model name, question, and answer

**Chain Architecture:**
```python
# RAG Chain (RAGFS/RAGNFS)
chain = (
    {"context": retriever | format_docs, "input": RunnablePassthrough()}
    | qa_prompt
    | llm 
    | StrOutputParser()
)

# Non-RAG Chain
chain = llm
```

**Usage:**
```bash
python testing.py
```

Generates: `education_materials_test.csv`

### Data Files

#### `synthetic_patients.txt`
Contains 21+ synthetic patient profiles used for testing the RAG system's ability to generate personalized recommendations.

**Patient Profile Structure:**
Each profile includes:
- **Work Status**: Employment situation (full-time, part-time, unemployed, not seeking work)
- **Daily Activity**: Time spent sitting vs. standing/moving
- **Lifts Objects**: Whether the patient regularly lifts objects
- **Aerobic Activity**: Days per week of aerobic exercise
- **Resistance Training**: Days per week of strength training
- **Beliefs** (5-point Likert scale):
  - Exercise makes back worse
  - Desk position confidence
  - Lifting technique confidence
  - Chiropractor/PT help beliefs
  - Injection help beliefs
  - X-ray/MRI necessity beliefs
  - Rest when painful beliefs

**Example:**
```
"Please give recommendations for Patient A: 
Work Status: Employed part-time
Daily Activity: More time sitting than standing/walking/moving around
Lifts Objects: Yes
Aerobic Activity: 3 days per week
Resistance Training: 1 day per week
Exercise Makes Back Worse: Somewhat agree
..."
```

**Purpose:**
- Test system's ability to personalize recommendations
- Evaluate model performance across diverse patient profiles
- Assess impact of different beliefs on education material content
- Compare RAG vs. non-RAG outputs

## Data Directories

### `data/`
Contains 200+ XML files with scraped health education content. This is a copy or symbolic link of the data from the `crawling/` folder, structured with sections for more granular retrieval.

**XML Structure:**
```xml
<page>
  <title>Document Title</title>
  <url>Source URL</url>
  <section>
    <sectionTitle>Section Title</sectionTitle>
    <sectionContent>Section content text...</sectionContent>
  </section>
  ...
</page>
```

### `chroma_db/`
ChromaDB vector database directory containing:
- Vector embeddings of document chunks
- Document metadata (titles, URLs, scores)
- Persistent storage for fast retrieval
- Hash file for cache validation (`hash.txt`)

**Persistence:**
- Vector store is saved to disk after initial creation
- Reloaded on subsequent runs if source data unchanged
- Automatically rebuilt if document hash changes

## System Prompts and Few-Shot Examples

### System Prompt
```
You are an assistant for physical therapists helping with lower back pain patients. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, say that you don't know.
```

### Few-Shot Examples

**Example 1 - Lifting Technique:**
- Input: "Can you explain how to lift properly to avoid excessive strain on the back?"
- Output: Structured 5-step lifting guide (get close, bend knees, breathe, lift with legs, pivot)

**Example 2 - Ergonomics:**
- Input: "How can a patient set up their desk ergonomically?"
- Output: 5-point ergonomic setup guide (chair, desk, monitor, keyboard/mouse, movement)

## Model Configurations

### Models Tested
1. **GPT-4**: OpenAI's most capable model (balanced performance/cost)
2. **GPT-3.5-turbo-0125**: Faster, more economical option
3. **GPT-4o-mini**: Compact version of GPT-4o
4. **GPT-4o**: Latest optimized GPT-4 variant
5. **Llama3** (commented out in `testing.py`): Open-source alternative via HuggingFace

### Configuration Comparison

| Configuration | Description | Use Case |
|--------------|-------------|----------|
| `rag_few_shot` / `_RAGFS` | RAG + few-shot examples | Structured, formatted outputs |
| `rag_no_few_shot` / `_RAGNFS` | RAG without examples | Natural language responses |
| `no_rag` / `_NRAG` | LLM baseline (no retrieval) | Baseline comparison |

## Retrieval Strategy

### Similarity Search
- **Method**: Cosine similarity on vector embeddings
- **Top K**: 7 documents retrieved
- **Threshold**: 0.4 (documents with score ≤0.4 are kept)
- **Scoring**: Lower scores indicate higher similarity

### Document Chunking
- **Splitter**: RecursiveCharacterTextSplitter
- **Chunk Size**: 1000 characters
- **Overlap**: 100 characters
- **Strategy**: Split by section for better semantic coherence

## Output Format

### CSV Files

#### `results_output_with_documents.csv` (from rag_model.py)
Complete results with retrieved context:
- Model name
- Configuration
- Question (patient profile)
- Generated answer
- Document title
- Document URL
- Similarity score
- Document content

#### `results_output.csv` (from rag_model.py)
Summary results:
- Model name
- Configuration
- Question
- Answer

#### `education_materials_test.csv` (from testing.py)
Education materials with model variants:
- Model (e.g., "GPT-4_RAGFS", "GPT-4O-MINI_NRAG")
- Question (patient profile)
- Generated education material

## Dependencies

Required Python packages:
```
langchain
langchain-chroma
langchain-community
langchain-openai
langchain-huggingface
langchain-text-splitters
langchain-core
openai
chromadb
PyPDF2 (indirect, from crawling module)
python-dotenv (optional, for environment variables)
```

Install with:
```bash
pip install langchain langchain-chroma langchain-community langchain-openai langchain-huggingface chromadb openai
```

## Environment Variables

Required API keys (currently hardcoded in scripts):
```python
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your_langchain_api_key"
os.environ["OPENAI_API_KEY"] = "your_openai_api_key"
```


## Workflow

### Initial Setup
1. Ensure `data/` folder contains XML files with health content
2. Install required dependencies
3. Set API keys in environment variables or script
4. Run either `rag_model.py` or `testing.py`

### First Run
1. Script calculates hash of `data/` folder
2. Loads XML documents with section-level parsing
3. Splits documents into 1000-character chunks
4. Generates embeddings using OpenAI's ada-002 model
5. Creates ChromaDB vector store
6. Saves hash and vector store to disk

### Subsequent Runs
1. Checks if data folder hash has changed
2. Loads existing vector store from disk (if hash matches)
3. Skips embedding generation for faster startup
4. Rebuilds vector store only if data has changed

### Query Processing
1. User query (patient profile) is embedded
2. Top 7 similar documents retrieved from vector store
3. Documents filtered by similarity threshold (≤0.4)
4. Context passed to LLM with system prompt
5. LLM generates personalized recommendation
6. Results logged and saved to CSV

## Use Cases

### Research Applications
- Compare RAG vs. non-RAG performance
- Evaluate impact of few-shot prompting
- Assess different LLM models for healthcare content
- Measure personalization quality across patient profiles
- Test readability and appropriateness of generated materials

### Clinical Applications
- Generate personalized patient education materials
- Provide evidence-based recommendations
- Tailor advice to patient beliefs and activity levels
- Support physical therapists with content generation
- Scale personalized education efficiently

## Performance Considerations

### Optimization Strategies
- **Caching**: Vector store persisted to avoid recomputation
- **Hash-based Validation**: Rebuild only when data changes
- **Batch Processing**: Documents processed in batches of 100
- **Similarity Filtering**: Only relevant documents passed to LLM

### Cost Management
- OpenAI embeddings: ~$0.0001 per 1K tokens
- GPT-4 inference: ~$0.03 per 1K input tokens
- GPT-3.5-turbo: ~$0.0015 per 1K input tokens
- Vector store: Local storage, no recurring costs

## Future Enhancements

Potential improvements:
- [ ] Move API keys to environment variables
- [ ] Add evaluation metrics (readability, accuracy, relevance)
- [ ] Implement hybrid search (semantic + keyword)
- [ ] Add re-ranking for improved retrieval
- [ ] Support for multi-modal inputs (images, PDFs)
- [ ] Real-time feedback collection
- [ ] A/B testing framework
- [ ] Production deployment configuration

## Related Folders

- [`../crawling/`](../crawling/README.md) - Source of health education content
- [`../evaluation/`](../evaluation/) - Evaluation metrics and analysis
- Data source: [`../crawling/data/`](../crawling/data/) or [`../crawling/split_sections/`](../crawling/)

## Notes

- The system is designed for research and development purposes
- Generated content should be reviewed by healthcare professionals before clinical use
- Patient profiles are synthetic and created for testing purposes
- API keys should be secured and not committed to version control
- ChromaDB storage grows with document count; monitor disk usage
- OpenAI rate limits may affect batch processing speed

## Citation

If using this system for research, ensure appropriate citation of:
- LangChain framework
- OpenAI models and embeddings
- Source health organizations (see crawling/README.md)
- Clinical practice guidelines used
