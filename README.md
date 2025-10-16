# Resume-ATS-Score-Checker

> **Status**: 🚧 Work in Progress | Currently under active development

An AI-powered resume optimization system designed to analyze and score resumes against job descriptions using advanced NLP techniques. This project aims to help job seekers optimize their resumes for Applicant Tracking Systems (ATS) and improve their chances of landing interviews.

---

## 🎯 Project Overview

This system leverages document parsing, OCR, AI-powered analysis, and semantic matching to provide comprehensive resume feedback and ATS compatibility scores.

### **Current Status**
- ✅ Core document processing pipeline implemented
- ✅ OCR and multi-format support (PDF, DOCX, HTML)
- ✅ AI-powered analysis using LangChain and Google Gemini
- ✅ Async file operations for performance optimization
- 🚧 Deployment pipeline in progress (planned for GCP)
- 📝 Full documentation to be released post-deployment

---

## 🛠️ Technology Stack

### **Document Processing**
- PyMuPDF - PDF parsing and manipulation
- python-docx - DOCX file processing
- pytesseract - OCR for image-based documents
- Pillow - Image processing
- camelot-py - Table extraction from PDFs

### **AI & NLP**
- LangChain - LLM orchestration framework
- langchain-google-genai - Google Gemini integration
- Sentence Transformers - Semantic similarity and embeddings
- scikit-learn - ML utilities and scoring

### **Web Scraping & Automation**
- BeautifulSoup4 - HTML parsing
- Selenium - Web automation
- firecrawl-py - Advanced web scraping
- requests - HTTP requests

### **Backend & API**
- FastAPI - Web framework
- fastapi[standard] - Additional FastAPI features
- Uvicorn - ASGI server
- aiofiles - Async file operations

### **Data Processing**
- pandas - Data manipulation
- jsonschema - JSON validation
- python-magic - File type detection

### **Development Tools**
- python-dotenv - Environment configuration
- python-box - Configuration management
- PyYAML, TOML - Config file handling
- ipykernel - Jupyter integration

---

## 📦 Installation

```
# Clone the repository

git clone https://github.com/hasan-raza-01/Resume-ATS-Score-Checker.git
cd Resume-ATS-Score-Checker

# Create virtual environment

pip install --upgrade pip uv
uv venv
.venv\Scripts\activate  \# Windows
source .venv/bin/activate  \# Linux/Mac

# Install dependencies

uv pip install -r requirements.txt

```

---

## 🚀 Quick Start

```
# Set up environment variables

cp .env.example .env

# Edit .env with your API keys

# Run the application (when ready)

# Details will be updated after deployment

```

---

## ✨ Key Features (In Development)

- **Multi-Format Support**: Process PDF, DOCX, and HTML resume files
- **OCR Capabilities**: Extract text from image-based documents
- **AI-Powered Analysis**: Leverage Google Gemini for intelligent resume evaluation
- **ATS Scoring**: Calculate compatibility scores based on job descriptions
- **Semantic Matching**: Use sentence transformers for contextual similarity analysis
- **Async Processing**: Fast, non-blocking file operations
- **Web Integration**: Extract job descriptions from URLs

---

## 📋 Planned Deployment

- **Platform**: Google Cloud Platform (GCP)
- **Architecture**: Containerized microservices
- **Status**: Deployment pipeline under development

---

## 🔧 Development Status

This project is actively being developed. Current focus areas:

1. ✅ Core processing pipeline
2. ✅ AI integration and scoring algorithms
4. 🚧 GCP deployment configuration
5. 📝 Complete API documentation
6. 📝 User guides and tutorials

---

## 📝 Requirements

See `requirements.txt` for full dependencies list.

**Key Dependencies:**
- Python 3.13+
- FastAPI
- LangChain
- PyMuPDF
- pytesseract
- Google Gemini API access

---

**Note**: This README will be updated with comprehensive documentation, setup instructions, and deployment details once the project reaches production readiness.

---
