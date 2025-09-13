# Educational Knowledge Graph Generator

A system for automated processing of educational module descriptions and generation of comprehensive knowledge graphs with ESCO (European Skills, Competences, Qualifications and Occupations) skill mappings.

## Abstract

This project implements an automated pipeline for transforming educational module descriptions from PDF documents into structured knowledge graphs. The system leverages Large Language Models (Claude AI) for intelligent text processing, skill extraction, and competency mapping to the standardized ESCO taxonomy. The resulting knowledge graphs can be imported into graph databases for further analysis and visualization.

## System Overview

The Educational Knowledge Graph Generator processes educational module PDFs through a seven-stage pipeline, extracting structured information about learning objectives, competencies, and skills. These are then mapped to the European ESCO skills framework and transformed into graph database-compatible formats.

### Key Capabilities

- Automated extraction of structured data from educational module PDFs
- AI-powered analysis and categorization of learning competencies
- Integration with the ESCO skills database for standardized skill mapping
- Generation of Neo4j-compatible knowledge graphs
- Web-based interface for workflow management and monitoring
- Batch processing optimization for efficient AI API usage

## Architecture

### Processing Pipeline

The system implements a seven-step processing workflow:

1. **ESCO Database Setup**: Import and configure the ESCO skills database from CSV files
2. **PDF Extraction**: Process educational module PDFs and extract structured content according to predefined templates
3. **Graph Creation**: Generate initial knowledge graph structures from extracted data
4. **ESCO Labels Export**: Export ESCO preferred labels for subsequent skill matching operations
5. **Graph Merging**: Merge and deduplicate similar nodes using AI-powered clustering algorithms
6. **ESCO Connection**: Establish connections between extracted skills and ESCO database entries
7. **Cipher Generation**: Create Neo4j Cypher queries for graph database import

### Technology Stack

**Backend Infrastructure**
- Python 3.x with Flask web framework
- PostgreSQL database (Docker containerized)
- SQLAlchemy for database operations

**AI Processing**
- Claude API (Anthropic) with batch processing capabilities
- Custom prompt engineering for educational content analysis
- Token usage optimization and rate limiting

**Data Processing**
- PDFMiner for PDF text extraction and structure analysis
- Pandas for data manipulation and CSV processing
- Custom graph algorithms for node merging and relationship detection

**User Interface**
- Bootstrap 5-based responsive web interface
- JavaScript with Server-Sent Events for real-time progress monitoring
- File upload and management system

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- Claude API key from Anthropic

### Environment Configuration

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GtaphWithLLM
   ```

2. **Install Python dependencies or use venv**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database environment setup**
   Create a `.env` file in the `DB_Setup/` directory with the following configuration:
   ```env
   POSTGRES_USER=your_database_user
   POSTGRES_PASSWORD=your_database_password
   POSTGRES_DB=esco_skills
   POSTGRES_PORT=5432
   DB_HOST=localhost
   CLAUDE_KEY=your_claude_api_key
   ```

4. **Initialize the database**
   ```bash
   cd DB_Setup
   docker-compose up -d
   ```

5. **Start the application**
   ```bash
   python main.py
   ```

The web interface will be accessible at `http://localhost:8888`.

## Project Structure

```
├── AI/                     # AI processing modules
│   ├── AI.py              # Core AI functions for content processing
│   └── AIConnector.py     # Claude API integration with batch processing
├── DB/                    # Database components
│   └── DBEngine.py        # PostgreSQL connection management
├── DB_Setup/              # Database configuration
│   ├── docker-compose.yml # PostgreSQL Docker configuration
│   ├── init.sql          # Database schema definition
│   └── .env              # Environment variables (user-created)
├── Graph/                 # Graph processing modules
│   ├── Graph.py          # Graph generation and Cypher query creation
│   ├── ESCO.py           # ESCO skills integration
│   └── MergeGraphs.py    # Graph merging and deduplication algorithms
├── Helper/                # Utility modules
│   ├── Files.py          # File operations and configuration management
│   └── csvFile.py        # CSV processing and ESCO data import
├── Pdf/                   # PDF processing
│   └── pdfFile.py        # PDF extraction and content structuring
├── Server/                # Web application
│   ├── app.py            # Flask web server and API endpoints
│   └── templates/        # HTML templates for web interface
├── src/                   # Source data and configuration
│   ├── Cache/            # Processing cache and intermediate results
│   ├── ESCO/             # ESCO skills CSV data files
│   ├── Prompts/          # AI prompts for different processing tasks
│   └── config/           # System configuration files
└── main.py               # Application entry point
```

## Configuration

### System Configuration

The main configuration file is located at `src/config/general.yml`. This file contains all system settings including AI model parameters, module structure definitions, and processing options.

#### LLM Configuration

```yaml
LLM:
  Model: claude-sonnet-4-20250514
  Temperature: 0.85
  Top_p: 0.75
  Max_Output_Tokens: 50000
  Max_Tokens_Per_Minute: 50000
  Rate_Limit_Buffer: 0.6
```

#### Module Structure Recognition

Define how the system recognizes different sections in PDF modules:

```yaml
Modulestructure:
  FormalDetails:
    - "Formal Details of the Module"
    - "FORMALE ANGABEN ZUM MODUL"
  Competences:
    - "Qualification Goals and Competences"
    - "QUALIFIKATIONSZIELE UND KOMPETENZEN"
  UnitsAndContents:
    - "Learning Units and Contents"
    - "LERNEINHEITEN UND INHALTE"
```

#### Graph Schema Definition

The knowledge graph structure is defined in the `LLM_Structure` section:

```yaml
LLM_Structure:
  Nodes:
    - Name: Module
      Properties: [code, name, year, mandatory, ETCS, language]
      Edges:
        - Target: Unit
          Properties: [consists_of]
    - Name: Skill
      Properties: [name, description, proficiencyLevel, URL]
      Edges:
        - Target: Skill
          Properties: [builds_on]
```

### Caching Configuration

Configure file names and locations for intermediate processing results:

```yaml
Caching:
  Cache_Directory: /src/Cache
  Graph_JSON: Graph_JSON.json
  Merged_Graph_JSON: Merged_Graph_JSON.json
  ESCO_preferred_label: preferred_label.csv
  LLM_Graph: LLM_Graph.txt
```

## Usage Guide

### Data Preparation

1. **ESCO Skills Data**: Place ESCO skills CSV files in the `src/ESCO/` directory. The system will automatically import all CSV files found in this location.

2. **Educational Module PDFs**: Prepare PDF files containing educational module descriptions. Ensure PDFs start with the first module content (table of contents cannot be automatically detected).

### Web Interface Operation

1. **Access the Dashboard**: Navigate to `http://localhost:8888` after starting the server.

2. **Cache Folder Management**: 
   - Select an existing cache folder or create a new one
   - Each cache folder maintains separate processing results
   - Folder names should not contain special characters

3. **Processing Workflow**:
   - **Step 1 - ESCO Database**: Import ESCO skills data into PostgreSQL
   - **Step 2 - PDF Extraction**: Upload and process educational module PDFs
   - **Step 3 - Graph Creation**: Generate initial knowledge graph structures
   - **Step 4 - ESCO Labels**: Export ESCO preferred labels for matching
   - **Step 5 - Graph Merging**: Merge duplicate nodes and optimize graph structure
   - **Step 6 - ESCO Connection**: Link extracted skills to ESCO entries
   - **Step 7 - Cipher Generation**: Create Neo4j import queries

### File Management

**PDF Upload**: Use the file upload interface in Step 2 to add educational module PDFs. Supported formats:
- PDF files up to 50MB
- Multiple files can be uploaded per session

**Result Monitoring**: Each processing step provides:
- Real-time logging with timestamp information
- Progress indicators and status updates
- Text editor for reviewing and modifying intermediate results

## Prompt Engineering

### Prompt Structure

The system uses specialized prompts for different processing tasks, located in `src/Prompts/`:

- `Simplify.txt`: Converts complex competency descriptions into simple, structured sentences
- `Translate.txt`: Translates content while preserving JSON structure
- `ConnectESCO.txt`: Maps extracted skills to ESCO database entries
- `Graph_JSON.txt`: Creates knowledge graph structures from processed content
- `Matrix.txt`: Generates comprehensive skill matrices for analysis
- `Graph.txt`: Produces Neo4j Cypher queries from graph structures

### Customizing Prompts

To modify AI processing behavior:

1. Edit the appropriate prompt file in `src/Prompts/`
2. Test changes with sample data
3. Monitor processing results through the web interface

**Example Prompt Structure**:
```
Find an ESCO label for each skill from the csv file. Do not invent new ones, do not combine them. Use exactly the csv file and nothing else. If no ESCO skill can be assigned: No ESCO. The output structure should look like this:
[["Skill1Id", "ESCO1preferredlabel", "Type1"], ["Skill2Id", "ESCO2preferredlabel", "Type2"], ...]
```

## API Integration

### Claude AI Batch Processing

The system implements efficient batch processing for the Claude API:

**Rate Limiting**: Automatic token usage tracking and request limiting
```python
max_tokens_per_minute = 50000
safety_buffer = 0.6  # Use 60% of limit
```

**Batch Job Management**: Asynchronous processing with status monitoring
- Request batching for cost optimization
- Automatic retry logic for failed requests
- Token usage reporting and optimization

### Database Operations

**PostgreSQL Integration**: 
- Automatic schema creation via `DB_Setup/init.sql`
- ESCO data import from CSV files
- Skill matching and relationship queries

**Connection Management**:
```python
def get_engine():
    db_url = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    return create_engine(db_url)
```

## Output Formats

### Knowledge Graph JSON

```json
{
  "nodes": [
    {
      "id": 1,
      "label": "Module",
      "properties": {
        "code": "CS101",
        "name": "Introduction to Computer Science",
        "ETCS": "6",
        "language": "English"
      }
    }
  ],
  "relationships": [
    {
      "startNode": "1",
      "endNode": "2", 
      "type": "consists_of",
      "properties": {}
    }
  ]
}
```

### Neo4j Cypher Queries

```cypher
CALL apoc.create.node(['Module'], {
  code: 'CS101', 
  name: 'Introduction to Computer Science', 
  ETCS: '6', 
  language: 'English'
}) YIELD node AS n1
```

### ESCO Skill Mappings

```json
{
  "skills": [
    ["skill_123", "programming concepts", "equivalent"],
    ["skill_124", "algorithm design", "partOf"]
  ]
}
```

## Development and Extension

### Adding New Module Structures

1. Update the `Modulestructure` section in `src/config/general.yml`
2. Add corresponding section recognition patterns
3. Test with sample PDF modules
4. Verify extraction accuracy through the web interface

### Extending Graph Schema

1. Modify the `LLM_Structure` configuration to include new node types or properties
2. Update corresponding prompts in `src/Prompts/`
3. Adjust graph processing logic in `Graph/Graph.py` if necessary
4. Test graph generation with modified schema

### Custom AI Processing Functions

To add new AI processing capabilities:

1. Create new prompt files in `src/Prompts/`
2. Implement processing functions in `AI/AI.py`
3. Add API integration in `AI/AIConnector.py`
4. Update web interface workflow if required

### Alternative AI Provider Integration

While the system is designed specifically for Claude AI, it is theoretically possible to integrate alternative AI providers by replacing the connector module:

**Connector Replacement**:
- Replace or modify `AI/AIConnector.py` with custom API integration
- Maintain the same function signatures and return formats expected by the system
- Implement equivalent batch processing, rate limiting, and error handling mechanisms

**Important Limitations and Considerations**:
- **No Functional Guarantee**: The system's response parsing logic is specifically designed for Claude AI's output format. Other AI providers may produce different response structures, leading to processing failures.
- **Custom Implementation Responsibility**: When using alternative providers, developers are fully responsible for implementing:
  - Rate limiting and API quota management
  - Batch processing optimization
  - Error handling and retry logic
  - Token usage tracking and cost optimization
  - Response format standardization

**Technical Requirements for Alternative Providers**:
- Must support JSON output format as specified in prompts
- Should handle complex prompt instructions for educational content analysis
- Must provide consistent response formatting for downstream processing
- Requires sufficient context window for processing complete module descriptions

**Compatibility Assessment**: Before implementing an alternative provider, thoroughly test with sample data to ensure response formats are compatible with the existing parsing logic in the Graph and Processing modules.

## Troubleshooting

### Common Issues

**Database Connection Errors**: Verify Docker container is running and environment variables are correct

**API Rate Limiting**: Check Claude API key validity and adjust rate limiting parameters in configuration

**PDF Processing Failures**: Ensure PDF files are text-based (not scanned images) and follow expected structure patterns

**Memory Issues**: For large PDF files, monitor system memory usage and consider processing files individually

### Log Analysis

The system provides comprehensive logging through the web interface:
- Real-time processing logs with timestamps
- Error messages with context information
- Token usage statistics for cost monitoring
- Processing step completion indicators