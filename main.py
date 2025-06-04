import tkinter as tk
from tkinter import scrolledtext
import pandas as pd
import requests
import random

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3.2"

# Load sample medical QA dataset
df = pd.read_csv("cleaned_pubmedqa.csv")

def build_prompt(user_question, k=3):
    examples = df.sample(k)
    shots = "\n\n".join(
        f"Q: {row['question']}\nA: {row['answer']}" for _, row in examples.iterrows()
    )
    return f"""{shots}

Q: {user_question}
A:"""

def query_gemma(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False}
        )
        return response.json().get("response", "No response received.")
    except Exception as e:
        return f"❌ Error contacting Ollama: {e}"

def on_submit():
    user_question = input_box.get()
    if not user_question.strip():
        output_box.insert(tk.END, "Please enter a valid medical question.\n")
        return

    prompt = build_prompt(user_question)
    output_box.insert(tk.END, f"\n🔍 Question: {user_question}\n")
    output_box.insert(tk.END, "💡 Generating answer...\n")
    window.update_idletasks()

    answer = query_gemma(prompt)
    output_box.insert(tk.END, f"🧠 Answer: {answer}\n")
    output_box.insert(tk.END, "-"*60 + "\n")

# Create main window
window = tk.Tk()
window.title("🩺 AI Clinical Assistant - Gemma via Ollama")
window.geometry("1360x768")

# ✅ Set window icon (must be AFTER tk.Tk())
try:
    icon_image = tk.PhotoImage(file="icon.png")  # Make sure this file exists
    window.iconphoto(False, icon_image)
except Exception as e:
    print(f"⚠️ Could not set icon: {e}")

# GUI Layout
tk.Label(window, text="Enter your medical query:").pack(pady=5)
input_box = tk.Entry(window, width=120)
input_box.pack(pady=5)

submit_button = tk.Button(window, text="Submit", command=on_submit)
submit_button.pack(pady=5)

output_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=160, height=100)
output_box.pack(padx=10, pady=10)

window.mainloop()
