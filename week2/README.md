# Action Item Extractor

A FastAPI-based web application that extracts actionable items from free-form notes using both heuristic-based and LLM-powered extraction methods.

## Overview

This application helps users convert unstructured notes into organized, actionable task lists. It supports two extraction methods:

1. **Heuristic-based extraction**: Uses pattern matching and keyword detection to identify action items
2. **LLM-powered extraction**: Uses Ollama with llama3.1:8b model for intelligent, context-aware extraction

## Features

- 📝 **Dual Extraction Methods**: Choose between fast heuristic or intelligent LLM-based extraction
- 💾 **Note Persistence**: Save notes to SQLite database for future reference
- ✅ **Task Management**: Mark action items as done/undone
- 📋 **Note History**: View all previously saved notes
- 🎨 **Clean UI**: Minimal, responsive HTML interface
- 🔒 **Type Safety**: Pydantic schemas for API validation
- 📚 **API Documentation**: Auto-generated OpenAPI/Swagger docs

## Tech Stack

- **Backend**: FastAPI 0.111.0+
- **Database**: SQLite with connection pooling
- **LLM Integration**: Ollama (llama3.1:8b)
- **Validation**: Pydantic 2.0+
- **Testing**: pytest
- **Code Quality**: Black, Ruff

## Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)
- Ollama (for LLM-based extraction)
- Conda (recommended for environment management)

## Setup

### 1. Install Ollama

Download and install Ollama from [https://ollama.com/download](https://ollama.com/download)

Pull the required model:
```bash
ollama pull llama3.1:8b
```

### 2. Create Conda Environment

```bash
conda create -n cs146s python=3.10
conda activate cs146s
```

### 3. Install Dependencies

```bash
poetry install
```

### 4. Run the Application

From the project root directory:

```bash
poetry run uvicorn week2.app.main:app --reload
```

The application will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Project Structure

```
week2/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── db.py                # Database layer (SQLite operations)
│   ├── schemas.py           # Pydantic models for API validation
│   ├── routers/
│   │   ├── action_items.py  # Action items endpoints
│   │   └── notes.py         # Notes endpoints
│   └── services/
│       └── extract.py       # Extraction logic (heuristic + LLM)
├── frontend/
│   └── index.html           # Web interface
├── tests/
│   └── test_extract.py      # Unit tests for extraction functions
└── data/
    └── app.db               # SQLite database (auto-created)
```

## API Endpoints

### Action Items

#### Extract (Heuristic)
```http
POST /action-items/extract
Content-Type: application/json

{
  "text": "- Add user authentication\n- Create database schema",
  "save_note": true
}
```

#### Extract (LLM)
```http
POST /action-items/extract-llm
Content-Type: application/json

{
  "text": "We need to improve performance. First, profile the code. Then optimize queries.",
  "save_note": true
}
```

#### List Action Items
```http
GET /action-items?note_id=1
```

#### Mark as Done
```http
POST /action-items/{action_item_id}/done
Content-Type: application/json

{
  "done": true
}
```

### Notes

#### Create Note
```http
POST /notes
Content-Type: application/json

{
  "content": "Meeting notes from standup"
}
```

#### List All Notes
```http
GET /notes
```

#### Get Single Note
```http
GET /notes/{note_id}
```

### Health Check
```http
GET /health
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Running Tests

### Run All Tests
```bash
poetry run pytest week2/tests/ -v
```

### Run Specific Test
```bash
poetry run pytest week2/tests/test_extract.py::TestExtractActionItemsLLM::test_bullet_list -v
```

### Run with Coverage
```bash
poetry run pytest week2/tests/ --cov=week2.app --cov-report=html
```

## Extraction Methods Comparison

### Heuristic-based Extraction

**Pros:**
- Fast and lightweight
- No external dependencies
- Deterministic results
- Works offline

**Cons:**
- Limited to predefined patterns
- May miss context-dependent items
- Requires explicit formatting

**Supported Patterns:**
- Bullet points: `- item`, `* item`, `• item`
- Numbered lists: `1. item`, `2. item`
- Checkboxes: `- [ ] item`, `[todo] item`
- Keywords: `TODO:`, `ACTION:`, `NEXT:`

### LLM-powered Extraction

**Pros:**
- Context-aware understanding
- Handles natural language
- Extracts implicit action items
- More flexible with formatting

**Cons:**
- Requires Ollama running
- Slower (5-10 seconds)
- Non-deterministic
- Requires internet for model download

**Example:**
```
Input: "We should improve the performance. First, let's profile the code to find bottlenecks."
Output: ["profile the code", "improve the performance"]
```

## Database Schema

### Notes Table
```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
```

### Action Items Table
```sql
CREATE TABLE action_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id INTEGER,
    text TEXT NOT NULL,
    done INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
);

CREATE INDEX idx_action_items_note_id ON action_items(note_id);
```

## Development

### Code Formatting
```bash
poetry run black week2/
```

### Linting
```bash
poetry run ruff check week2/
```

### Type Checking
```bash
poetry run mypy week2/
```

## Configuration

### Environment Variables

Create a `.env` file in the project root (optional):

```env
# Database
DATABASE_PATH=week2/data/app.db

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Logging
LOG_LEVEL=INFO
```

## Troubleshooting

### Ollama Connection Error

If you get "Failed to connect to Ollama":

1. Check if Ollama is running:
   ```bash
   ollama list
   ```

2. Verify the model is available:
   ```bash
   ollama run llama3.1:8b
   ```

3. Check Ollama service:
   ```bash
   # On macOS
   brew services restart ollama
   ```

### Database Locked Error

If you get "database is locked":

1. Close any other connections to the database
2. Delete `week2/data/app.db` and restart the server (will recreate tables)

### Port Already in Use

If port 8000 is already in use:

```bash
poetry run uvicorn week2.app.main:app --reload --port 8001
```

## Performance Considerations

- **Heuristic extraction**: ~10-50ms per request
- **LLM extraction**: ~5-10 seconds per request (depends on text length)
- **Database queries**: Indexed for optimal performance
- **Connection pooling**: SQLite with WAL mode for concurrent reads

## Future Enhancements

- [ ] User authentication and multi-tenancy
- [ ] Real-time collaboration
- [ ] Export to various formats (JSON, CSV, Markdown)
- [ ] Integration with task management tools (Jira, Trello)
- [ ] Custom extraction rules/patterns
- [ ] Batch processing for multiple notes
- [ ] API rate limiting
- [ ] Caching layer for LLM responses

## License

This project is part of the Modern Software Development course assignments.

## Contributing

This is a course assignment project. For questions or issues, please contact the course staff.

## Acknowledgments

- FastAPI for the excellent web framework
- Ollama for local LLM inference
- llama3.1 model by Meta AI
