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

# ---------- SETTINGS ----------
CSV_PATH = "cleaned_pubmedqa.csv"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# ---------- DATA & TTS ----------
df = pd.read_csv(CSV_PATH)
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 170)

# ---------- GLOBAL STATE ----------
spinner_running = threading.Event()
theme_state = {"dark": False}
last_answer = ""
tts_playing = False
tts_paused = False
tts_thread = None

# ---------- BUILD PROMPT ----------
def build_prompt(user_question):
    return f"Q: {user_question}\nA:"

# ---------- SPINNER ANIMATION ----------
def spinner_animation():
    spinner_chars = ["◐", "◓", "◑", "◒"]
    if spinner_running.is_set():
        idx = spinner_animation.index
        spinner_label.config(text=f"⏳ Generating... {spinner_chars[idx % len(spinner_chars)]}")
        spinner_animation.index += 1
        window.after(150, spinner_animation)
spinner_animation.index = 0

# ---------- MODEL DETECTION ----------
def get_available_models():
    try:
        result = subprocess.run(["ollama", "list", "--json"], capture_output=True, text=True)
        if result.returncode == 0:
            models_info = json.loads(result.stdout)
            return [model["name"] for model in models_info.get("models", [])]
    except Exception as e:
        print(f"❌ Error fetching models: {e}")
    return ["gemma3", "llama3", "mistral"]

# ---------- QUERY MODEL ----------
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

# ---------- GENERATE THREAD ----------
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
    last_answer = answer

# ---------- SUBMIT ----------
def on_submit():
    threading.Thread(target=generate_answer, daemon=True).start()

# ---------- TTS CONTROLS ----------
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

# ---------- THEME TOGGLE ----------
def toggle_theme():
    theme_state["dark"] = not theme_state["dark"]
    dark = theme_state["dark"]
    bg_color = "#1e1e1e" if dark else "#f0f0f0"
    fg_color = "white" if dark else "black"
    window.config(bg=bg_color)

    safe_config(input_box, bg="#333" if dark else "white", fg=fg_color, insertbackground=fg_color)
    safe_config(output_box, bg="#282828" if dark else "white", fg=fg_color)
    safe_config(spinner_label, bg=bg_color, fg=fg_color)

    for widget in window.winfo_children():
        if widget.winfo_class() in ["Label", "Button"]:
            safe_config(widget, bg=bg_color, fg=fg_color)

    theme_btn.config(text="🌞 Light Mode" if dark else "🌙 Dark Mode")

def safe_config(widget, **kwargs):
    try:
        widget.config(**kwargs)
    except:
        pass

# ---------- SAVE FUNCTIONS ----------
def save_as_text():
    content = output_box.get("1.0", tk.END).strip()
    if not content:
        return
    path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

def save_as_pdf():
    content = output_box.get("1.0", tk.END).strip()
    if not content:
        return
    path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if path:
        c = canvas.Canvas(path, pagesize=letter)
        width, height = letter
        y = height - 50
        for line in content.splitlines():
            c.drawString(40, y, line)
            y -= 15
            if y < 50:
                c.showPage()
                y = height - 50
        c.save()

# ---------- GUI LAYOUT ----------
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

tk.Button(window, text="Submit", command=on_submit).pack(pady=5)

spinner_label = tk.Label(window, text="")
spinner_label.pack(pady=5)

# TTS Controls
tts_frame = tk.Frame(window)
tts_frame.pack(pady=5)
tk.Button(tts_frame, text="🔊 Read Aloud", command=start_tts).pack(side=tk.LEFT, padx=5)
tk.Button(tts_frame, text="⏸️ Pause", command=pause_tts).pack(side=tk.LEFT, padx=5)
tk.Button(tts_frame, text="▶️ Resume", command=resume_tts).pack(side=tk.LEFT, padx=5)
tk.Button(tts_frame, text="⏹️ Stop", command=stop_tts).pack(side=tk.LEFT, padx=5)

# Theme and Export
theme_btn = tk.Button(window, text="🌙 Dark Mode", command=toggle_theme)
theme_btn.pack(pady=5)
tk.Button(window, text="💾 Save as Text", command=save_as_text).pack(pady=2)
tk.Button(window, text="📄 Export as PDF", command=save_as_pdf).pack(pady=2)

# Output Box
output_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=160, height=100)
output_box.pack(padx=10, pady=10)
output_box.tag_config("bold", font=("Segoe UI", 10, "bold"))
output_box.tag_config("warn", foreground="red")

toggle_theme()
window.mainloop()
