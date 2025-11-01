# IntelliQuery Intent Agent

A comprehensive intent understanding system for IntelliQuery that analyzes user queries, extracts entities, identifies intent types, maps to workspaces, and returns structured JSON responses using advanced AI/ML techniques.

## 🚀 Features

- **Text Preprocessing**: Language detection, normalization, and cleaning
- **Entity Extraction**: spaCy-based NER with custom patterns for dates, locations, quantities, etc.
- **Embedding Retrieval**: Sentence-BERT embeddings with FAISS similarity search
- **Intent Classification**: Hybrid keyword-based and ML-powered classification
- **LLM Integration**: Google Gemini API for intelligent intent mapping
- **Schema Validation**: Pydantic-based validation with automatic repair
- **REST API**: Flask-based API with comprehensive endpoints
- **Comprehensive Testing**: Unit tests with mock implementations

## 📁 Project Structure

```
backend/services/intent_agent/
├── __init__.py
├── preprocessor.py              # Text preprocessing and normalization
├── embedding_retriever.py       # Sentence-BERT + FAISS retrieval
├── entity_extractor.py          # spaCy NER + custom entity extraction
├── classifier.py                # Intent type and workspace classification
├── llm_mapper.py               # Gemini API integration
├── schema_validator.py          # Pydantic schema validation
├── agent_orchestrator.py        # Main pipeline orchestrator
├── prompts/
│   ├── intent_system_prompt.txt # System prompt for Gemini
│   └── few_shot_examples.json   # Few-shot examples
├── config/
│   ├── workspace_catalog.json   # Workspace definitions
│   └── intent_schema.json       # Schema definition
└── tests/
    ├── test_intent_agent.py     # Comprehensive test suite
    └── __init__.py
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- pip or conda package manager

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd SQLGenerator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Install spaCy Model

```bash
# Download English language model
python -m spacy download en_core_web_sm
```

### Step 3: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# Required: GEMINI_API_KEY=your_google_api_key_here
```

### Step 4: Get Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

## 🚀 Quick Start

### Option 1: Using the Startup Script

```bash
python start_intent_agent.py
```

### Option 2: Direct Flask App

```bash
cd backend
python app.py
```

The server will start on `http://localhost:5000`

## 📖 API Usage

### Analyze Intent

```bash
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me sales in Mumbai for last month"}'
```

**Response:**
```json
{
  "success": true,
  "query": "Show me sales in Mumbai for last month",
  "intent_analysis": {
    "intent_type": "read",
    "workspaces": ["sales"],
    "entities": {
      "dates": ["last month"],
      "locations": ["Mumbai"],
      "quantities": [],
      "products": [],
      "organizations": [],
      "people": [],
      "custom": {}
    },
    "confidence": 0.95,
    "rationale": "Clear request for sales data with location and time",
    "query_type": "simple",
    "time_sensitivity": "historical"
  },
  "metadata": {
    "processing_time_seconds": 0.245,
    "timestamp": "2024-01-15T10:30:00",
    "pipeline_components": {
      "preprocessing": true,
      "embedding_retrieval": true,
      "entity_extraction": true,
      "classification": true,
      "llm_mapping": true,
      "schema_validation": true
    }
  }
}
```

### Check Status

```bash
curl http://localhost:5000/api/status
```

### Health Check

```bash
curl http://localhost:5000/api/health
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest backend/services/intent_agent/tests/ -v

# Run with coverage
python -m pytest backend/services/intent_agent/tests/ --cov=backend.services.intent_agent --cov-report=html

# Run specific test file
python -m pytest backend/services/intent_agent/tests/test_intent_agent.py -v
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Generative AI API key | Required |
| `EMBEDDING_MODEL` | Sentence-BERT model name | `all-MiniLM-L6-v2` |
| `FAISS_INDEX_PATH` | Path to FAISS index | `data/faiss_index/index.faiss` |
| `WORKSPACE_CATALOG_PATH` | Workspace catalog JSON path | `backend/services/intent_agent/config/workspace_catalog.json` |
| `SPACY_MODEL` | spaCy model name | `en_core_web_sm` |
| `PORT` | Flask server port | `5000` |
| `DEBUG` | Debug mode | `False` |

### Workspace Configuration

Edit `backend/services/intent_agent/config/workspace_catalog.json` to customize workspaces:

```json
[
  {
    "id": "sales",
    "name": "Sales Analytics",
    "description": "Sales and transaction data, revenue analysis",
    "keywords": ["sales", "revenue", "profit", "customer", "order"],
    "tables": ["sales_transactions", "products", "customers"]
  }
]
```

## 🏗️ Architecture

### Pipeline Flow

1. **Preprocessing**: Text normalization and language detection
2. **Embedding Generation**: Sentence-BERT embeddings
3. **Similarity Retrieval**: FAISS-based context retrieval
4. **Entity Extraction**: spaCy NER + custom patterns
5. **Classification**: Intent type and workspace prediction
6. **LLM Mapping**: Gemini-powered intent synthesis
7. **Schema Validation**: Pydantic validation and repair
8. **Response Generation**: Structured JSON output

### Components

- **TextPreprocessor**: Handles text cleaning and normalization
- **EmbeddingRetriever**: Manages embeddings and similarity search
- **EntityExtractor**: Extracts structured entities using spaCy
- **IntentClassifier**: Classifies intent types and workspaces
- **LLMMapper**: Uses Gemini for intelligent intent mapping
- **SchemaValidator**: Validates and repairs intent schemas
- **IntentAgentOrchestrator**: Orchestrates the complete pipeline

## 🔍 Supported Intent Types

- **read**: Simple data retrieval ("show me", "get", "find")
- **compare**: Comparative analysis ("compare", "vs", "difference")
- **update**: Data modification ("change", "update", "modify")
- **summarize**: Aggregation ("total", "average", "summary")
- **analyze**: Complex analysis ("trend", "pattern", "analysis")
- **predict**: Predictive queries ("forecast", "predict", "estimate")

## 🎯 Supported Workspaces

- **sales**: Sales and transaction data
- **support**: Customer feedback and complaints
- **marketing**: Campaign performance and metrics
- **hr**: Employee data and performance
- **finance**: Financial reports and budgets
- **operations**: Inventory and logistics

## 🐛 Troubleshooting

### Common Issues

1. **spaCy Model Not Found**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **Gemini API Key Missing**
   - Set `GEMINI_API_KEY` in your `.env` file
   - Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

3. **FAISS Index Issues**
   - Delete `data/faiss_index/` folder to regenerate
   - The system will create a new index automatically

4. **Memory Issues**
   - Reduce batch sizes in embedding generation
   - Use `faiss-cpu` instead of `faiss-gpu` if needed

### Logging

Check logs for detailed error information:
```bash
tail -f intent_agent.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Google Generative AI](https://ai.google.dev/) for Gemini API
- [spaCy](https://spacy.io/) for NLP processing
- [Sentence Transformers](https://www.sbert.net/) for embeddings
- [FAISS](https://github.com/facebookresearch/faiss) for similarity search
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test cases for usage examples
3. Open an issue on GitHub
4. Check the API documentation at `http://localhost:5000/`

---

**Built with ❤️ for IntelliQuery**
"# BE_Project" 
