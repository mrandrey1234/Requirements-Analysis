import subprocess
import sys
import os
import json
import pyaudio
import numpy as np
import librosa
import librosa.effects
from vosk import Model, KaldiRecognizer
from datetime import datetime
import signal
import webrtcvad
from sklearn.cluster import KMeans
from collections import deque
from docx import Document
import threading

def install_if_missing(package, module_name=None):
    if module_name is None:
        module_name = package
    try:
        __import__(module_name)
    except ImportError:
        print(f"Устанавливаем '{package}'...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_if_missing("webrtcvad")
install_if_missing("librosa")
install_if_missing("numpy")
install_if_missing("scikit-learn", "sklearn")
install_if_missing("vosk")
install_if_missing("python-docx", "docx")

def start_recording(speakers, stop_event=None):
    num_speakers = len(speakers)
    speaker_names = speakers[:]  # копия списка

    doc = Document()

    MODEL_PATH = "vosk-model-ru-0.42"
    if not os.path.exists(MODEL_PATH):
        sys.exit(f"Модель {MODEL_PATH} не найдена")

    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, 16000)

    vad = webrtcvad.Vad(3)

    p = pyaudio.PyAudio()
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 4000

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)

    FRAME_DURATION_MS = 30
    FRAME_SIZE = int(RATE * (FRAME_DURATION_MS / 1000.0)) * 2

    PAUSE_THRESHOLD = 1.0

    features_memory = deque(maxlen=50)

    def save_to_word(speaker, timestamp, text):
        doc.add_paragraph(f"[{timestamp}] {speaker}: {text}")
        doc.save("transcription.docx")

    def extract_features(audio):
        y = np.frombuffer(audio, dtype=np.int16).astype(np.float32)
        y = librosa.effects.preemphasis(y)
        if np.max(np.abs(y)) != 0:
            y /= np.max(np.abs(y))
        mfccs = librosa.feature.mfcc(y=y, sr=RATE, n_mfcc=13, n_fft=512)
        return np.mean(mfccs, axis=1)

    def get_speaker_name(feature):
        features_memory.append(feature)
        if len(features_memory) >= 3:
            features_array = np.array(features_memory)
            kmeans = KMeans(n_clusters=num_speakers, random_state=42, n_init=10)
            labels = kmeans.fit_predict(features_array)
            speaker_index = labels[-1]
            if speaker_index < len(speaker_names):
                return speaker_names[speaker_index]
            else:
                return f"Speaker_{speaker_index}"
        else:
            return speaker_names[0]

    audio_buffer = b""
    last_speech_time = None

    # Если функция запущена в главном потоке, регистрируем обработчик
    if threading.current_thread() == threading.main_thread():
        def signal_handler(sig, frame):
            print("\nЗавершение записи...")
            stream.close()
            p.terminate()
            sys.exit(0)
        import signal
        signal.signal(signal.SIGINT, signal_handler)

    print("Говорите... Для завершения записи нажмите кнопку 'Закончить запись' в интерфейсе.")

    try:
        while True:
            if stop_event and stop_event.is_set():
                print("Запись завершена по запросу.")
                break

            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_buffer += data

            while len(audio_buffer) >= FRAME_SIZE:
                frame = audio_buffer[:FRAME_SIZE]
                audio_buffer = audio_buffer[FRAME_SIZE:]

                if vad.is_speech(frame, RATE):
                    last_speech_time = datetime.now()
                    if recognizer.AcceptWaveform(frame):
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "").strip()
                        if text:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            mfcc_feat = extract_features(frame)
                            speaker = get_speaker_name(mfcc_feat)
                            save_to_word(speaker, timestamp, text)
                            print(f"[{timestamp}] {speaker}: {text}")
                    else:
                        partial = json.loads(recognizer.PartialResult())
                        if partial.get("partial", "").strip():
                            print(f"Распознается: {partial['partial']}", end="\r")

                if last_speech_time:
                    time_since_last_speech = (datetime.now() - last_speech_time).total_seconds()
                    if time_since_last_speech > PAUSE_THRESHOLD:
                        print("\n[Пауза] Возможна смена спикера.\n")
    except Exception as e:
        print(f"Ошибка: {e}")
    except KeyboardInterrupt:
        print("\nЗавершение записи (KeyboardInterrupt)")
    finally:
        stream.close()
        p.terminate()
