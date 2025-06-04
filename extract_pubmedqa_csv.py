import pandas as pd
import os
from tqdm import tqdm  # progress bar

BASE_DIR = "./PubMedQA"
OUTPUT_CSV = "cleaned_pubmedqa.csv"
folders = ["pqa_artificial", "pqa_labeled", "pqa_unlabeled"]

qa_pairs = []

print("Starting extraction from PubMedQA parquet files...")

# Count total files for tqdm
total_files = sum(len([f for f in os.listdir(os.path.join(BASE_DIR, folder)) if f.endswith(".parquet")]) for folder in folders)

file_counter = 0
for folder in folders:
    folder_path = os.path.join(BASE_DIR, folder)
    parquet_files = [f for f in os.listdir(folder_path) if f.endswith(".parquet")]
    
    for file in tqdm(parquet_files, desc=f"Processing {folder}", unit="file", total=len(parquet_files)):
        file_counter += 1
        full_path = os.path.join(folder_path, file)
        df = pd.read_parquet(full_path)

        if 'final_decision' in df.columns and 'question' in df.columns:
            for _, row in df.iterrows():
                question = str(row['question']).strip()
                answer = str(row['final_decision']).strip()
                if answer.lower() in ['yes', 'no', 'maybe']:
                    qa_pairs.append({
                        "question": question,
                        "answer": answer.capitalize()
                    })

print(f"\n✅ Extracted {len(qa_pairs)} QA pairs from {file_counter} files.")

df_qa = pd.DataFrame(qa_pairs)
df_qa.to_csv(OUTPUT_CSV, index=False)
print(f"📁 Saved cleaned data to '{OUTPUT_CSV}'")
