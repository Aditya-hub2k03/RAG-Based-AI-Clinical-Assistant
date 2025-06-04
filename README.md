<i><b><h1>RAG-Based AI Clinical Assistant</h1></b></i>
<img src="https://www.medicaldevice-network.com/wp-content/uploads/sites/23/2023/11/pmcardio-queen-of-hearts.jpeg">
<p>The main goal of this project is to provide accurate, explainable answers to clinical questions using LLMs grounded in trusted sources like PubMed, NICE guidelines, UpToDate, or clinical trial data.</p>
The dataset used for this project is <a href="https://huggingface.co/datasets/qiaojin/PubMedQA/tree/main"><b><i>PubMedQA</b></i></a>
<p>As the dataset is of the format .parquet (which is a columnar data file format developed by Apache for efficient data storage and retrieval, particularly for large datasets), an extraction code "extract_pubmedqa_csv.py" is written for these files, and the foler structure must be in the format

PubMedQA/

├── pqa_artificial/

│   └── train-00000-of-00001.parquet

├── pqa_labeled/

│   └── train-00000-of-00001.parquet

├── pqa_unlabeled/

│   └── train-00000-of-00001.parquet
</p>

Once the data is extracted, it is saved in a .csv format 
<p>The extracted data is then loaded into the main.py file where the extracted data is kept as reference for the main script, the main script is run based on Gemma3 which is used from <a href="https://ollama.com/"><i><b>Ollama</b></i></a> where the Ollama hosts the LLM locally and the Ollama API is linked to the code.</p>
The requirements are given in thie "requirements.txt" file which can be installed using "pip install -r requirements.txt"
