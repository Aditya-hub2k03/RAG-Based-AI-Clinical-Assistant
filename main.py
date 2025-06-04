import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk
import pandas as pd
import requests
import threading
import time
import json
import pyttsx3
import subprocess
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Load QA dataset
CSV_PATH = "cleaned_pubmedqa.csv"
df = pd.read_csv(CSV_PATH)

# TTS Engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 170)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
spinner_running = threading.Event()
theme_state = {"dark": False}

# Store last answer for TTS
last_answer = ""

# Control flags for TTS playback
tts_playing = False
tts_paused = False
tts_thread = None

# Prompt builder
def build_prompt(user_question, k=3):
    examples = df.sample(k)
    shots = "\n\n".join(f"Q: {row['question']}\nA: {row['answer']}" for _, row in examples.iterrows())
    return f"""{shots}\n\nQ: {user_question}\nA:"""

# Spinner animation
def spinner_animation():
    spinner_chars = ["◐", "◓", "◑", "◒"]
    if spinner_running.is_set():
        idx = spinner_animation.index
        spinner_label.config(text=f"⏳ Generating... {spinner_chars[idx % len(spinner_chars)]}")
        spinner_animation.index += 1
        window.after(150, spinner_animation)
spinner_animation.index = 0

# Fetch installed models from Ollama
def get_available_models():
    try:
        result = subprocess.run(["ollama", "list", "--json"], capture_output=True, text=True)
        if result.returncode == 0:
            models_info = json.loads(result.stdout)
            return [model["name"] for model in models_info.get("models", [])]
    except Exception as e:
        print(f"❌ Error fetching models: {e}")
    # fallback models if command fails
    return ["gemma3", "llama3", "mistral"]

# Model querying
def query_model(prompt, selected_model):
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": selected_model, "prompt": prompt, "stream": True},
            stream=True
        )
        full_response = ""
        output_box.insert(tk.END, "🧠 Answer: ", "bold")
        output_box.see(tk.END)
        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8").strip()
                if line.startswith("data:"):
                    line = line[len("data:"):].strip()
                try:
                    data = json.loads(line)
                    content = data.get("response", "")
                    output_box.insert(tk.END, content)
                    output_box.see(tk.END)
                    window.update_idletasks()
                    full_response += content
                except Exception as e:
                    print(f"⚠️ Stream error: {e}")
        return full_response or "No response received."
    except Exception as e:
        return f"❌ Error contacting Ollama: {e}"

# Threaded execution
def generate_answer():
    global last_answer
    user_q = input_box.get()
    selected_model = model_var.get()
    if not user_q.strip():
        output_box.insert(tk.END, "⚠️ Please enter a valid medical question.\n", "warn")
        return

    output_box.insert(tk.END, f"\n🔍 Question ({selected_model}): {user_q}\n", "bold")
    output_box.insert(tk.END, "💡 Generating answer...\n")
    prompt = build_prompt(user_q)
    spinner_running.set()
    spinner_animation()
    answer = query_model(prompt, selected_model)
    spinner_running.clear()
    spinner_label.config(text="✅ Done.")
    output_box.insert(tk.END, "\n" + "-" * 60 + "\n")
    last_answer = answer  # Save answer for TTS

def on_submit():
    threading.Thread(target=generate_answer, daemon=True).start()

# TTS play function with chunking and pause/resume control
def tts_play():
    global tts_playing, tts_paused
    tts_playing = True
    tts_paused = False
    words = last_answer.split()
    chunk_size = 15
    idx = 0

    while idx < len(words) and tts_playing:
        if tts_paused:
            time.sleep(0.1)
            continue
        chunk = " ".join(words[idx:idx+chunk_size])
        tts_engine.say(chunk)
        tts_engine.runAndWait()
        idx += chunk_size

    tts_playing = False
    tts_paused = False

def start_tts():
    global tts_thread
    if not last_answer.strip():
        output_box.insert(tk.END, "⚠️ No answer available to read.\n", "warn")
        return
    if tts_playing:
        output_box.insert(tk.END, "⚠️ TTS already playing.\n", "warn")
        return
    tts_thread = threading.Thread(target=tts_play, daemon=True)
    tts_thread.start()

def pause_tts():
    global tts_paused
    if tts_playing and not tts_paused:
        tts_paused = True

def resume_tts():
    global tts_paused
    if tts_playing and tts_paused:
        tts_paused = False

def stop_tts():
    global tts_playing, tts_paused
    if tts_playing:
        tts_playing = False
        tts_paused = False
        tts_engine.stop()

# Theme toggle with safe widget config
def toggle_theme():
    theme_state["dark"] = not theme_state["dark"]
    dark = theme_state["dark"]

    bg_color = "#1e1e1e" if dark else "#f0f0f0"
    fg_color = "white" if dark else "black"
    window.config(bg=bg_color)

    input_box.config(bg="#333" if dark else "white", fg=fg_color, insertbackground=fg_color)
    output_box.config(bg="#282828" if dark else "white", fg=fg_color)
    spinner_label.config(bg=bg_color, fg=fg_color)

    for widget in window.winfo_children():
        wclass = widget.winfo_class()
        if wclass in ["Label", "Button"]:
            widget.config(bg=bg_color, fg=fg_color)

    theme_btn.config(text="🌞 Light Mode" if dark else "🌙 Dark Mode")

# Save to text file
def save_as_text():
    content = output_box.get("1.0", tk.END).strip()
    if not content:
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", title="Save As Text File",
                                             filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

# Save to PDF
def save_as_pdf():
    content = output_box.get("1.0", tk.END).strip()
    if not content:
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", title="Export as PDF",
                                             filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter
        lines = content.splitlines()
        y = height - 50
        for line in lines:
            c.drawString(40, y, line)
            y -= 15
            if y < 50:
                c.showPage()
                y = height - 50
        c.save()

# GUI setup
window = tk.Tk()
window.title("🩺 AI Clinical Assistant - Ollama Multi-Model")
window.geometry("1360x768")

try:
    icon = tk.PhotoImage(file="icon.png")
    window.iconphoto(False, icon)
except:
    pass

tk.Label(window, text="Enter your medical query:").pack(pady=5)
input_box = tk.Entry(window, width=120)
input_box.pack(pady=5)

tk.Label(window, text="Select Model:").pack()
model_var = tk.StringVar()
model_dropdown = ttk.Combobox(window, textvariable=model_var, values=get_available_models(), width=30)
model_dropdown.set(model_dropdown["values"][0] if model_dropdown["values"] else "gemma3")
model_dropdown.pack(pady=5)

submit_button = tk.Button(window, text="Submit", command=on_submit)
submit_button.pack(pady=5)

spinner_label = tk.Label(window, text="")
spinner_label.pack(pady=5)

# TTS Controls: Play, Pause, Resume, Stop buttons
tts_frame = tk.Frame(window)
tts_frame.pack(pady=5)

play_btn = tk.Button(tts_frame, text="🔊 Read Aloud", command=start_tts)
play_btn.pack(side=tk.LEFT, padx=5)

pause_btn = tk.Button(tts_frame, text="⏸️ Pause", command=pause_tts)
pause_btn.pack(side=tk.LEFT, padx=5)

resume_btn = tk.Button(tts_frame, text="▶️ Resume", command=resume_tts)
resume_btn.pack(side=tk.LEFT, padx=5)

stop_btn = tk.Button(tts_frame, text="⏹️ Stop", command=stop_tts)
stop_btn.pack(side=tk.LEFT, padx=5)

theme_btn = tk.Button(window, text="🌙 Dark Mode", command=toggle_theme)
theme_btn.pack(pady=5)

tk.Button(window, text="💾 Save as Text", command=save_as_text).pack(pady=2)
tk.Button(window, text="📄 Export as PDF", command=save_as_pdf).pack(pady=2)

output_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=160, height=100)
output_box.pack(padx=10, pady=10)

output_box.tag_config("bold", font=("Segoe UI", 10, "bold"))
output_box.tag_config("warn", foreground="red")

toggle_theme()

window.mainloop()
