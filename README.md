# Documents.AI - Intelligent Document Processing API

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org)

A production-ready document processing system with AI-powered translation and editing capabilities. Built with FastAPI and DeepSeek integration.

## Features

- **Document Translation**  
  Automatically detect language and translate documents between 50+ languages
- **Smart Editing**  
  PDF content modification with version history tracking
- **Multi-format Support**  
  Process both PDF and DOCX files
- **Secure Authentication**  
  JWT-based user system with optional endpoints
- **Version Control**  
  Full audit trail of document changes
- **Cloud Storage**  
  Integrated document storage system

## Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- DeepSeek API Key

### Setup
```bash
# Clone repository
git clone https://github.com/ifymatics/documents.ai.git
cd documents.ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env