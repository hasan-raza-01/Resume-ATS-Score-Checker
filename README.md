# Resume-ATS-Score-Checker: AI-Powered Resume Optimization System

An end-to-end AI-powered resume optimization system designed to analyze and score resumes against job descriptions using advanced NLP techniques and semantic matching. By combining multi-format document parsing, OCR capabilities, and LangChain-integrated AI agents, this system empowers job seekers to optimize their resumes for Applicant Tracking Systems (ATS) and improve their interview chances.

---

## 📂 Repository Structure

```

├── src/
│   └── ats/
│       ├── cloud/                  \# GCS integration for cloud storage operations
│       ├── components/
│       │   ├── data_ingestion.py   \# Resume ingestion
│       │   ├── data_transformation.py  \# Text preprocessing and normalization
│       │   ├── job_description.py  \# Job description parsing and extraction
│       │   ├── scoring.py          \# ATS scoring orchestration
│       │   ├── cloud_push.py       \# GCS upload operations
│       │   ├── parsers/            \# Multi-format document parsers (PDF, DOCX, HTML)
│       │   ├── schema/             \# Pydantic models for data validation
│       │   └── scorers/            \# Semantic scoring models (MiniLM, MPNet, RoBERTa)
│       ├── config/
│       │   ├── builder/            \# Configuration builders
│       │   └── raw/
│       │       └── config.yaml     \# Application configuration
│       ├── constants/              \# Schema and value constants
│       ├── entity/                 \# Entity definitions
│       ├── exception/              \# Custom exceptions
│       ├── logger/                 \# Logging utilities
│       ├── pipeline/               \# Processing pipelines
│       └── utils/                  \# Helper utilities
├── notebook/
│   ├── data_ingestion.ipynb        \# Document parsing exploration
│   ├── data_transformation.ipynb   \# Text preprocessing workflows
│   ├── job_description.ipynb       \# Job description extraction patterns
│   ├── scorings.ipynb              \# Scoring algorithm development
│   └── test.py                     \# Notebook-based testing
├── resumes/                        \# Sample test resumes (PDF, DOCX, HTML formats)
├── Dockerfile                      \# Container image for GCP Compute Engine
├── app.py                          \# FastAPI application entry point
├── test.py                         \# Direct application testing script
├── requirements.txt                \# Python dependencies
├── pyproject.toml                  \# Project metadata and build configuration
├── uv.lock                         \# Locked dependency versions
├── secrets.example                 \# Service account key template
└── .github/workflows/deploy.yml    \# CI/CD pipeline for GCP deployment

```

---

## 🔧 Core Workflow

### 1. Resume Ingestion \& Validation

Accepts resume uploads at application startup through FastAPI endpoints. Performs basic validation checks including file format verification (PDF, DOCX, HTML), size limits, and MIME type detection. Validated resumes are stored in a local `artifacts/` directory for persistent access and simultaneously ingested into MongoDB collections for metadata tracking and retrieval. Each resume document is assigned a unique identifier and timestamp, enabling efficient query operations and workflow orchestration throughout the analysis pipeline.

### 2. Data Transformation \& Preprocessing

Normalizes extracted text through tokenization, cleaning, and structuring. Converts unstructured resume data into standardized schemas for consistent analysis using dedicated parsers (PyMuPDF for PDFs, python-docx for DOCX files, BeautifulSoup for HTML). Handles OCR processing via pytesseract for image-based content and table extraction through camelot-py for complex layouts.

### 3. Job Description Parsing \& Extraction

Retrieves job description URL from the `JD_URL` environment variable and extracts content from public web pages (excluding LinkedIn URLs due to access restrictions). Leverages web scraping tools including Firecrawl to handle JavaScript-heavy and dynamic content. Extracted job descriptions are parsed to identify key requirements, qualifications, and skill keywords, then persisted to local disk storage for reproducibility and audit trails. This extraction occurs after data transformation and immediately before semantic similarity scoring to ensure fresh, accurate job requirement matching.

### 4. AI-Powered Analysis \& Extraction

Leverages Google Gemini API via LangChain for intelligent resume evaluation, skill extraction, and semantic understanding. Generates structured insights aligned with job requirements.

### 5. Semantic Similarity Scoring

Computes ATS compatibility scores using multiple sentence transformer models (MiniLM, MPNet, RoBERTa). Calculates semantic similarity between resume content and job description keywords extracted in the previous step.

### 6. Cloud Storage \& Logging

Pushes processed artifacts, scoring results, and execution logs to Google Cloud Storage (GCS) buckets for persistence and audit trails. Supports async file operations for performance optimization and implements retry logic for reliability.

---

## 🎯 Scoring Mechanism

The Resume-ATS-Score-Checker implements a **three-tier progressive scoring system** that balances speed and accuracy through cascading semantic analysis. Each tier uses specialized transformer models optimized for different aspects of resume-job matching.

### Three-Tier Architecture

The scoring pipeline follows a progressive evaluation strategy where candidates pass through increasingly sophisticated analysis layers:

#### **Tier 1: Fast Filtering (MiniLM) - ~100ms**

The first-pass filter uses the lightweight `paraphrase-MiniLM-L6-v2` model for rapid candidate screening.

**Technical Specifications:**
- **Model**: `sentence-transformers/paraphrase-MiniLM-L6-v2`
- **Embedding Dimensions**: 384
- **Batch Size**: 32 (optimized for throughput)
- **Processing Speed**: Fast (<100ms per resume)

**Scoring Methodology:**
1. **Section Extraction**: Creates focused resume sections (skills, experience, professional summary)
2. **Cross-Similarity Matrix**: Generates embeddings for resume and job sections, computing cosine similarity across all combinations
3. **Section-Wise Scoring**:
   - **Skills-to-Requirements Matching**: Compares technical skills against job requirements
   - **Experience-to-Responsibilities Matching**: Aligns work experience with job responsibilities
4. **Overall Score**: Calculated as mean of maximum similarities across sections (0-100 scale)

**Threshold Logic:**
- **Score ≥ 30%**: Candidate proceeds to Tier 2 quality analysis
- **Score < 30%**: Candidate filtered out (not a sufficient match)

**Output Format:**
```

{
"overallScore": 72.5,
"sectionScores": {
"skillsToRequirements": 85.0,
"experienceToResponsibilities": 68.0
},
"confidence": "High",
"modelUsed": "paraphrase-MiniLM-L6-v2",
"processingSpeed": "Fast"
}

```

---

#### **Tier 2: Quality Semantic Matching (MPNet) - ~300ms**

Candidates passing Tier 1 undergo detailed semantic analysis using the balanced `all-mpnet-base-v2` model.

**Technical Specifications:**
- **Model**: `sentence-transformers/all-mpnet-base-v2`
- **Embedding Dimensions**: 768
- **Quality**: High-quality pre-trained model for nuanced understanding
- **Processing Speed**: Medium (~300ms per resume)

**Scoring Methodology:**
1. **Comprehensive Text Extraction**: Extracts detailed structured information:
   - Personal info and professional titles
   - Complete professional summary with experience years
   - Detailed work experience (positions, responsibilities, technologies)
   - Technical skills, certifications, and education
2. **Job Description Parsing**: Extracts job title, company, experience level, full description, requirements, and responsibilities
3. **Semantic Embedding**: Generates 768-dimensional embeddings capturing contextual meaning
4. **Cosine Similarity**: Computes similarity between resume and job embeddings (0-100 scale)
5. **Section-Wise Breakdown**:
   - **Skills Match**: Technical skills vs. job requirements
   - **Experience Match**: Work responsibilities vs. job responsibilities

**Threshold Logic:**
- **Score ≥ 50%**: Candidate proceeds to Tier 3 comprehensive scoring
- **Score < 50%**: Returns Tier 2 results as final evaluation

**Output Format:**
```

{
"overallScore": 68.5,
"sectionsBreakdown": {
"skillsMatch": 78.0,
"experienceMatch": 65.0
},
"matchLevel": "Medium",
"modelUsed": "all-mpnet-base-v2"
}

```

---

#### **Tier 3: Comprehensive Hybrid Scoring (RoBERTa) - ~800ms**

Top candidates receive exhaustive hybrid analysis combining semantic understanding, keyword matching, TF-IDF analysis, and experience validation using `all-roberta-large-v1`.

**Technical Specifications:**
- **Model**: `sentence-transformers/all-roberta-large-v1`
- **Embedding Dimensions**: 1024 (highest quality)
- **Hybrid Approach**: Multi-factor scoring with weighted components
- **Processing Speed**: Slower (~800ms per resume, enterprise-grade)

**Scoring Methodology:**

**1. Semantic Similarity (40% weight)**
- Generates 1024-dimensional RoBERTa embeddings for comprehensive resume and job texts
- Computes cosine similarity for deep contextual understanding

**2. Keyword Overlap (30% weight)**
- **Technical Keyword Extraction**: Regex-based pattern matching for:
  - Programming languages (Python, JavaScript, React, etc.)
  - Cloud platforms (AWS, Azure, GCP)
  - ML/AI frameworks (TensorFlow, PyTorch, scikit-learn)
  - Tools and technologies (Docker, Kubernetes, Git, CI/CD)
  - Data science tools (pandas, NumPy, SQL, NoSQL)
  - Role-specific terms (Senior, Lead, Architect, Engineer, etc.)
- **Skill Phrase Extraction**: Identifies experience/skills/expertise mentions
- **Intersection Score**: `(Resume Keywords ∩ Job Keywords) / Job Keywords × 100`

**3. TF-IDF Similarity (20% weight)**
- Uses `TfidfVectorizer` with English stop words and n-grams (1-3)
- Measures term frequency importance for domain-specific jargon
- Identifies critical terminology alignment beyond semantic matching

**4. Experience Level Matching (10% weight)**
- **Entry-level**: ≤2 years → 100% if match
- **Junior**: 1-3 years → 100% if match
- **Mid-level**: 3-6 years → 100% if match
- **Senior**: ≥5 years → 100% if match
- **Partial scoring**: `max(0, 100 - |resume_exp - baseline_exp| × 10)` for near matches

**Weighted Hybrid Score Calculation:**
```

Hybrid Score = (Semantic × 0.4) + (Keyword × 0.3) + (TF-IDF × 0.2) + (Experience × 0.1)

```

**Match Quality Classification:**
- **Excellent**: Score ≥ 80%
- **Good**: 60% ≤ Score < 80%
- **Fair**: 40% ≤ Score < 60%
- **Poor**: Score < 40%

**Actionable Recommendations:**
- Score ≥ 80%: "Excellent match - Strong candidate for this position"
- Keyword Overlap < 30%: "Consider updating resume with more relevant technical keywords"
- Semantic Similarity < 50%: "Resume content doesn't align well with job responsibilities"
- Experience Match < 60%: "Experience level may not be optimal for this role"
- Default: "Good potential - consider for interview with some reservations"

**Output Format:**
```

{
"overallScore": 76.5,
"scoreBreakdown": {
"semanticSimilarity": 82.0,
"keywordOverlap": 68.0,
"tfidfSimilarity": 75.0,
"experienceMatch": 80.0
},
"matchQuality": "Good",
"modelUsed": "all-roberta-large-v1-hybrid",
"recommendation": "Excellent match - Strong candidate for this position"
}

```

---

### Progressive Evaluation Flow

```

Resume Upload
↓
┌─────────────────────────────────────────┐
│   Tier 1: MiniLM Fast Filter (~100ms)   │
│   Threshold: Score ≥ 30%                 │
└─────────────────────────────────────────┘
↓ (Pass)                    ↓ (Fail)
┌─────────────────────────────────────────┐
│   Tier 2: MPNet Quality (~300ms)        │  → Return Tier 1 Results
│   Threshold: Score ≥ 50%                 │
└─────────────────────────────────────────┘
↓ (Pass)                    ↓ (Fail)
┌─────────────────────────────────────────┐
│   Tier 3: RoBERTa Hybrid (~800ms)       │  → Return Tier 2 Results
│   Comprehensive Analysis                 │
└─────────────────────────────────────────┘
↓
Final Detailed Score Report

```

### Performance Optimization

**Speed vs. Accuracy Trade-off:**
- **Low-match candidates** (< 30%): Filtered in <100ms, avoiding expensive processing
- **Medium-match candidates** (30-50%): Evaluated in ~400ms total (Tier 1 + Tier 2)
- **High-potential candidates** (≥ 50%): Receive full ~1.2s analysis (all three tiers)

**Batch Processing:**
- MiniLM supports batch size of 32 for high-throughput scenarios
- Async/await implementation enables concurrent resume processing
- GCS integration ensures results persist across sessions

### Model Selection Rationale

|    Model    |      Use Case      |                   Strengths                 | Speed |
|-------------|--------------------|---------------------------------------------|-------|
| **MiniLM**  | Initial screening  | Ultra-fast, section-wise analysis           | 100ms |
| **MPNet**   | Quality assessment | Balanced accuracy/speed, detailed breakdown | 300ms |
| **RoBERTa** |  Final evaluation  | Hybrid scoring, keyword+semantic+TF-IDF     | 800ms |

### Usage in API

The three-tier system is automatically orchestrated by the `ResumeScorer` class:

```

from src.ats.components.scorers import ResumeScorer

scorer = ResumeScorer()
result = await scorer.score(resume_data, job_data)

# Returns the appropriate tier result based on progressive thresholds

```

**API Response Structure:**
```

{
"tier": 3,
"model": "all-roberta-large-v1-hybrid",
"overallScore": 76.5,
"scoreBreakdown": {
"semanticSimilarity": 82.0,
"keywordOverlap": 68.0,
"tfidfSimilarity": 75.0,
"experienceMatch": 80.0
},
"matchQuality": "Good",
"recommendation": "Excellent match - Strong candidate for this position",
"processingTimeMs": 1150
}

```

---

## ✅ Key Capabilities

* **Multi-Format Resume Support**
  Parses PDF, DOCX, and HTML resumes with OCR fallback for image-based content. Extracts text, tables, and structured data from complex layouts.

* **AI-Driven Resume Analysis**
  Utilizes Google Gemini for intelligent skill extraction, experience summarization, and job alignment assessment. Provides actionable feedback for resume optimization.

* **ATS Scoring Engine**
  Calculates compatibility scores using semantic embeddings from pre-trained transformer models. Identifies missing keywords and skills for targeted improvements.

* **Job Description Integration**
  Extracts requirements, qualifications, and key skills from job descriptions via web scraping (Firecrawl) or direct input. Normalizes job specifications for accurate matching.

* **Production-Ready Architecture**
  Dockerized deployment on Google Compute Engine with async processing for scalability. Structured logging, error handling, and GCS integration for reliability.

* **Extensible AI Stack**
  Configurable scoring models (MiniLM, MPNet, RoBERTa) and LLM providers. Modular component architecture enables easy customization and enhancement.

---

## 🛠️ Technology Stack

### Document Processing
- **PyMuPDF** - PDF parsing and text extraction
- **python-docx** - DOCX file processing
- **pytesseract** - OCR for image-based documents
- **Pillow** - Image processing and manipulation
- **camelot-py** - Table extraction from PDFs
- **BeautifulSoup4** - HTML parsing and extraction

### AI & NLP
- **LangChain** - LLM orchestration and agent framework
- **langchain-google-genai** - Google Gemini integration
- **Sentence Transformers** - Semantic similarity and embeddings (MiniLM, MPNet, RoBERTa)
- **scikit-learn** - ML utilities and scoring calculations

### Web Scraping & Automation
- **Selenium** - Browser automation for dynamic content
- **firecrawl-py** - Advanced web scraping and content extraction
- **requests** - HTTP requests for APIs

### Backend & API
- **FastAPI** - Async web framework
- **fastapi[standard]** - Enhanced FastAPI features
- **Uvicorn** - ASGI server
- **aiofiles** - Async file I/O operations

### Cloud & Storage
- **google-cloud-storage** - GCS client for artifact storage
- **google-auth** - GCP authentication and credentials

### Data Processing
- **pandas** - Data manipulation and analysis
- **jsonschema** - JSON schema validation
- **python-magic** - File type detection

### Development Tools
- **python-dotenv** - Environment variable management
- **python-box** - Configuration management
- **PyYAML, TOML** - Configuration file parsing
- **ipykernel** - Jupyter notebook support

---

## 🚀 Deployment Architecture

### Cloud Infrastructure
- **Compute**: Google Compute Engine VM instances
- **Container Registry**: Google Artifact Registry for Docker images
- **Storage**: Google Cloud Storage (GCS) for artifacts, logs, and results
- **Authentication**: Service accounts with granular IAM permissions

### CI/CD Pipeline
- **GitHub Actions** (`.github/workflows/deploy.yml`): Automated testing, building, and deployment
- **Workload Identity Federation**: Secures GitHub Actions-to-GCP authentication
- **Docker**: Multi-stage builds optimized for production deployments

### Environment Configuration
- **Local Development**: `gcloud auth application-default login` for ADC (Application Default Credentials)
- **Docker Local**: Service account JSON via `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- **CI/CD & GCP**: Service accounts with `roles/storage.admin` or `roles/storage.objectAdmin` permissions
- **.env Management**: Secrets stored in `.env` file or Google Secret Manager

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.13+
- Docker and Docker Compose
- Google Cloud Project with APIs enabled:
  - Cloud Storage API
  - Cloud Compute API
- Service account key with Storage permissions
- `gcloud` CLI installed and configured

### Local Development Setup

1. **Clone the repository**
```

git clone https://github.com/hasan-raza-01/Resume-ATS-Score-Checker.git
cd Resume-ATS-Score-Checker

```

2. **Create virtual environment**
```

pip install --upgrade pip uv
uv venv
.venv\Scripts\activate  \# Windows
source .venv/bin/activate  \# Linux/Mac

```

3. **Install dependencies**
```

uv pip install -r requirements.txt

```

4. **Configure Google Cloud credentials**
```


# For local development with Application Default Credentials

gcloud auth application-default login

# Verify authentication

gcloud auth list

```

5. **Set up environment variables**
```

# copy content of .env.example to .env
cp .env.example .env

# Edit .env with your configuration

```

6. **Run the FastAPI server with uv/python**
```

uv run app.py  |  python app.py 

```

The API will be available at `http://localhost:8080` with interactive docs at `/docs`.

7. **Test the application**
```


# With server running, execute test script


uv run test.py  |  python test.py

# Or run tests directly

python -m pytest

```

### Docker Setup (Local)

1. **Build Docker image**
```

docker build -t resume-ats-checker:latest .

```

2. **Create service account key** (if using Docker locally instead of ADC)
```


# Download service account JSON from GCP Console

# Place in repository root: service-account-key.json

```

3. **Run container with credentials**
```

docker run -p 8080:8080 \
-v \$(pwd)/service-account-key.json:/app/service-account-key.json \
-e GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json \
--env-file .env \
resume-ats-checker:latest

```

---

## 🔄 CI/CD Pipeline & GCP Deployment

### GitHub Actions Workflow

The `.github/workflows/deploy.yml` automates testing, building, and deployment:

1. **Build Stage**: Runs tests, builds Docker image
2. **Push Stage**: Pushes image to Google Artifact Registry
3. **Deploy Stage**: Deploys to Google Compute Engine with:
- Workload Identity Federation authentication
- Service account(storage-sa)
    - roles/storage.admin (Storage Admin permissions)
- Service Account: github-actions-deployer
    - roles/artifactregistry.writer (Artifact Registry Writer)

    - roles/compute.instanceAdmin.v1 (Compute Instance Admin v1)

    - roles/iam.serviceAccountUser (Service Account User)

    - roles/secretmanager.secretAccessor (Secret Manager Secret Accessor)

    - roles/storage.admin (Storage Admin permissions)
- Service Account: compute-instance-sa
    - roles/artifactregistry.reader (Artifact Registry Reader)

    - roles/logging.logWriter (Logging Writer)

    - roles/monitoring.metricWriter (Monitoring Metric Writer)

    - roles/secretmanager.secretAccessor (Secret Manager Secret Accessor)

    - roles/storage.objectAdmin (Storage Object Admin)
- Environment variables via Secret Manager(GCP)

### Deployment Environment Variables

**For GitHub Actions CI/CD:**
```

PROJECT_ID: your-project-id(GCP_PROJECT_ID)
REGION: us-central1(GCP_REGION)
GAR_REPOSITORY: resume-ats-checker(ARTIFACT_REGISTRY_REPO)
INSTANCE_NAME: resume-ats-instance(COMPUTE_INSTANCE_NAME)
PROJECT_NUMBER: 123456789012(GCP_PROJECT_NUMBER)
SERVICE_ACCOUNT: SERVICE-ACCOUNT-ID@YOUR-PROJECT-ID.iam.gserviceaccount.com(SERVICE ACCOUNT EMAIL)
WORKLOAD_IDENTITY_PROVIDER: projects/PROJECT-NUMBER/locations/global/workloadIdentityPools/POOL-ID/providers/PROVIDER-ID(WORKLOAD IDENTITY PROVIDER PATH)
ZONE: us-central1(COMPUTE INSTANCE ZONE)

```

**For Service Account Permissions:**
- `roles/artifactregistry.writer` - Push images to Artifact Registry
- `roles/compute.instanceAdmin.v1` - Compute Instance Admin v1
- `roles/iam.serviceAccountUser` - Service Account User
- `roles/secretmanager.secretAccessor` - Secret Manager Secret Accessor
- `roles/storage.admin` - Full GCS access

### Local Testing Before Deployment

1. **Authenticate with gcloud**
```

gcloud auth application-default login
gcloud config set project your-project-id

```

2. **Test GCS connectivity**
```


# From Python

from google.cloud import storage
client = storage.Client()
buckets = list(client.list_buckets())
print([b.name for b in buckets])

```

3. **Build and test locally**
```

docker build -t resume-ats-checker:test .
docker run -p 8080:8080 \
-v \$(pwd)/service-account-key.json:/app/service-account-key.json \
-e GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json \
--env-file .env \
resume-ats-checker:latest
uv run test.py

```

---

## 📋 Testing

### Running Tests Locally

**With FastAPI server running**
```

python test.py

```
Uses sample resumes from the `resumes/` directory to test endpoints.

### Sample Resumes for Testing

The `resumes/` directory contains test data in multiple formats:
- **1.pdf, 1.docx, 1.html** - Standard resume format
- **2.pdf, 2.docx, 2.html** - Alternative resume format
- **3.pdf, 3.docx, 3.html** - Standard format
- **3_images.pdf, 3_images.docx** - Resumes with embedded images
- **3_js_heavy.html** - JavaScript-heavy HTML resume

---

## 🔧 Configuration

### Application Configuration

Edit `src/ats/config/raw/config.yaml` to customize:

```


# Document processing settings

parsers:
pdf_timeout: 30
ocr_enabled: true
table_extraction: true

# Scoring models

scorers:
models:
- minilm  \# Lightweight, fast
- mpnet   \# Balanced accuracy/speed
- roberta \# High accuracy

# Cloud storage

gcs:
bucket_name: \${GCP_BUCKET}
upload_artifacts: true
upload_logs: true

# AI/LLM settings

gemini:
model: gemini-2.5-pro
```

### Environment Variables

Create `.env` file (copy from `.env.example`):

```


# Google Cloud Configuration

PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json  \# Only if not using ADC
GCP_BUCKET=your-gcs-bucket

# API Keys

GOOGLE_API_KEY=your-gemini-api-key

# Application Settings

LOG_LEVEL=INFO
ASYNC_WORKERS=4

```

---

## 📊 API Endpoints

### Resume Analysis

**POST** `/upload`

upload resumes.

**Request:**
```

{
  files: [
    ('files', bytes_of_file_1.pdf),
    ('files', bytes_of_file_1.docx),
    ('files', bytes_of_file_1.html),
  ],
}

```

**Response:**
```

{
  "info":exec_info,
  "scorings":scorings_output
}
# info of files till which step of applicaiton file have been processed
exec_info = {
  "file.ext": src.ats.components.FileInfo(...),
  ...
},
# dict output with detailed scores, match quality, model used and recommendation if file passes first two level of simantic matching
scorings_output = {
  "file.ext": {
    "overallScore": 76.5,
    "scoreBreakdown": {
    "semanticSimilarity": 82.0,
    "keywordOverlap": 68.0,
    "tfidfSimilarity": 75.0,
    "experienceMatch": 80.0
    },
    "matchQuality": "Good",
    "modelUsed": "all-roberta-large-v1-hybrid",
    "recommendation": "Excellent match - Strong candidate for this position"
    },
  ...
}

```

### Health Check

**GET** `/health`

Verify service availability and GCS connectivity.

**Response:**
```

{
"status": "healthy",
"timestamp": datetime.now(),
}

```

---

## 🔐 Security Best Practices

1. **Never commit service account keys**: Use `.gitignore` to exclude `service-account-key.json`
2. **Use Application Default Credentials**: Prefer `gcloud auth application-default login` for local development
3. **Limit service account permissions**: Grant only necessary roles (Storage Admin for artifacts)
4. **Rotate credentials regularly**: Implement key rotation policies in GCP
5. **Use Secret Manager**: Store sensitive config in Google Cloud Secret Manager for production
6. **Environment isolation**: Keep dev, staging, and production GCP projects separate

---

## 📝 Development Status

This project is actively developed and production-ready:

- ✅ Core processing pipeline with multi-format support
- ✅ AI integration with Google Gemini and LangChain
- ✅ GCP deployment on Compute Engine with Artifact Registry
- ✅ Async FastAPI backend with comprehensive error handling
- ✅ GCS integration for artifact storage and logging
- ✅ CI/CD pipeline via GitHub Actions with Workload Identity
- 📝 Comprehensive API documentation

---

## 📦 Dependencies

See `requirements.txt` and `pyproject.toml` for complete dependencies.

**Key Requirements:**
- Python 3.13+
- FastAPI 0.104+
- LangChain 0.1+
- google-cloud-storage
- google-auth
- PyMuPDF
- pytesseract
- sentence-transformers

---

**Problem**: `DefaultCredentialsError` or permission denied errors

**Solution**:
```


# Verify ADC is configured

gcloud auth application-default login
gcloud auth list

# Or explicitly set service account

export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

```

### OCR Not Working

**Problem**: Text not extracted from image-based resumes

**Solution**:
```


# Install tesseract (system dependency)

# Ubuntu/Debian

sudo apt-get install tesseract-ocr

# macOS

brew install tesseract

# Verify pytesseract config

python -c "import pytesseract; print(pytesseract.pytesseract.pytesseract_path)"

```

### Docker Build Failures

**Problem**: Image build fails with dependency errors

**Solution**:
```


# Clear Docker cache and rebuild

docker build --no-cache -t resume-ats-checker:latest .

# Check Python version

docker run resume-ats-checker:latest python --version

```

---
