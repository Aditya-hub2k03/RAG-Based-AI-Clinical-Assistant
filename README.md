# RAG-Based AI Clinical Assistant  
*Explainable clinical answers powered by LLMs and trusted sources*

[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)  
[![Ollama](https://img.shields.io/badge/Ollama-LLM-green)](https://ollama.com/)  
[![Dataset: PubMedQA](https://img.shields.io/badge/Dataset-PubMedQA-yellow)](https://huggingface.co/datasets/pubmedqa)

---

## Table of Contents

- [Overview](#overview)  
- [Getting Started](#getting-started)  
  - [Prerequisites](#prerequisites)  
  - [Installation](#installation)  
- [Usage](#usage)  
- [Project Structure](#project-structure)  
- [Contributing](#contributing)  
- [License](#license)

---

## Overview  
The **RAG-Based AI Clinical Assistant** provides accurate and explainable answers to clinical questions by combining **Retrieval-Augmented Generation (RAG)** with a locally hosted LLM via **Ollama**.  

It retrieves data from trusted sources like **PubMed**, **NICE guidelines**, and clinical trial reports, and integrates with the **PubMedQA** dataset to ensure responses are grounded in verified medical knowledge.  

**Key Features:**
- Retrieval-augmented LLM answering for transparency.
- Supports **PubMedQA** dataset ingestion and processing.
- Local LLM inference with **Ollama** for privacy and performance.
- Modular scripts for dataset extraction and querying.

---

## Getting Started

### Prerequisites
- **Python 3.x** — for running the project  
- **Ollama** — for hosting the local language model via API  
- **Pip** — for installing dependencies  

---

### Installation
```bash
# Clone the repository
git clone https://github.com/Aditya-hub2k03/RAG-Based-AI-Clinical-Assistant.git
cd RAG-Based-AI-Clinical-Assistant

# Install required packages
pip install -r requirements.txt
```

---

## Usage
1. **Prepare the dataset**:
   ```bash
   python extract_pubmedqa_csv.py
   ```
2. **Start the Ollama server**:
   Make sure your Ollama model is downloaded and running locally.
3. **Run the assistant**:
   ```bash
   python main.py
   ```
4. **Ask clinical questions** and receive fact-grounded answers with citations.

---

## Project Structure
```
├── cleaned_pubmedqa.csv           # Processed dataset ready for RAG
├── extract_pubmedqa_csv.py        # Script to convert Parquet files to CSV
├── main.py                        # Core script integrating Ollama LLM for Q&A
├── requirements.txt               # Python dependencies
└── icon.png                       # Project icon
```

---

## Contributing
Contributions are welcome!  
If you have ideas for improvements, feel free to:
- Open an **issue**
- Submit a **pull request**
- Suggest enhancements

---

## License
This project is licensed under the terms specified in the repository’s LICENSE file. Please check it for details.
