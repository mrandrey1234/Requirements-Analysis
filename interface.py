import tkinter as tk
from tkinter import messagebox
import os
import threading
from speech_to_text import start_recording as stt_start_recording

recording_stop_event = None
recording_thread = None

def start_recording():
    global recording_stop_event, recording_thread
    try:
        num_speakers = int(num_speakers_entry.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректное число участников.")
        return

    speakers = []
    for i in range(num_speakers):
        name = speaker_entries[i].get().strip()
        if not name:
            name = f"Speaker_{i+1}"
        speakers.append(name)
    
    messagebox.showinfo("Запись", f"Начинается запись для участников: {', '.join(speakers)}")
    
    # Инициализируем событие остановки и запускаем запись в отдельном потоке
    recording_stop_event = threading.Event()
    recording_thread = threading.Thread(target=stt_start_recording, args=(speakers, recording_stop_event))
    recording_thread.daemon = True
    recording_thread.start()

def stop_recording():
    global recording_stop_event, recording_thread
    if recording_stop_event:
        recording_stop_event.set()
        messagebox.showinfo("Запись", "Запись завершена.")
    else:
        messagebox.showwarning("Предупреждение", "Запись не запущена.")

def open_docx():
    file_path = "transcription.docx"
    if os.path.exists(file_path):
        os.startfile(file_path)
    else:
        messagebox.showerror("Ошибка", "Файл не найден!")

def update_speaker_entries():
    for widget in speakers_frame.winfo_children():
        widget.destroy()
    speaker_entries.clear()
    try:
        n = int(num_speakers_entry.get())
    except ValueError:
        n = 1
    for i in range(n):
        lbl = tk.Label(speakers_frame, text=f"Имя участника {i+1}:")
        lbl.grid(row=i, column=0, padx=5, pady=2, sticky="e")
        entry = tk.Entry(speakers_frame)
        entry.grid(row=i, column=1, padx=5, pady=2)
        speaker_entries.append(entry)

root = tk.Tk()
root.title("Speech-to-Text")

rec_frame = tk.Frame(root, bd=2, relief="groove", padx=10, pady=10)
rec_frame.pack(padx=10, pady=10, fill="x")

rec_label = tk.Label(rec_frame, text="Рекомендации по микрофону:\n"
                                     "- Частота дискретизации не менее 16 кГц\n"
                                     "- Оптимальное расстояние до микрофона: 20–50 см\n"
                                     "- Используйте микрофон с хорошей чувствительностью")
rec_label.pack()

settings_frame = tk.Frame(root, bd=2, relief="groove", padx=10, pady=10)
settings_frame.pack(padx=10, pady=10, fill="x")

num_speakers_label = tk.Label(settings_frame, text="Количество участников:")
num_speakers_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

num_speakers_entry = tk.Entry(settings_frame, width=5)
num_speakers_entry.grid(row=0, column=1, padx=5, pady=5)
num_speakers_entry.insert(0, "1")

update_btn = tk.Button(settings_frame, text="Обновить список участников", command=update_speaker_entries)
update_btn.grid(row=0, column=2, padx=5, pady=5)

speakers_frame = tk.Frame(root, bd=2, relief="groove", padx=10, pady=10)
speakers_frame.pack(padx=10, pady=10, fill="x")
speaker_entries = []
update_speaker_entries()

buttons_frame = tk.Frame(root, padx=10, pady=10)
buttons_frame.pack(padx=10, pady=10)

start_btn = tk.Button(buttons_frame, text="Начать запись", command=start_recording, width=20)
start_btn.grid(row=0, column=0, padx=5, pady=5)

stop_btn = tk.Button(buttons_frame, text="Закончить запись", command=stop_recording, width=20)
stop_btn.grid(row=0, column=1, padx=5, pady=5)

open_btn = tk.Button(buttons_frame, text="Открыть файл", command=open_docx, width=20)
open_btn.grid(row=0, column=2, padx=5, pady=5)

root.mainloop()
