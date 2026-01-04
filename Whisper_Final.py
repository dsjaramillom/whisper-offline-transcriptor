import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import subprocess
import os
import tempfile
from faster_whisper import WhisperModel
import time
import re
from datetime import datetime
import winsound

class TranscriptorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Transcriptor de Audio/Video")
        self.root.geometry("500x390")

        self.label = tk.Label(root, text="Selecciona un archivo de audio o video para transcribir")
        self.label.pack(pady=10)

        # Menú desplegable para elegir el modelo de Whisper
        self.label_modo = tk.Label(root, text="Nivel de transcripción")
        self.label_modo.pack()
        self.modo_var = tk.StringVar()
        self.menu_modelo = ttk.Combobox(root, textvariable=self.modo_var, state="readonly")
        self.menu_modelo['values'] = [
            "Básica (tiny)",
            "Media (base)",
            "Avanzada (small)",
            "Muy precisa (medium)"
        ]
        self.menu_modelo.current(0)
        self.menu_modelo.pack(pady=5)

        self.boton = tk.Button(root, text="Seleccionar archivo", command=self.seleccionar_archivo)
        self.boton.pack(pady=5)

        self.progress_label_audio = tk.Label(root, text="Extrayendo audio (0%)")
        self.progress_label_audio.pack()
        self.progress_audio = ttk.Progressbar(root, length=400, mode='determinate')
        self.progress_audio.pack(pady=5)

        self.progress_label_model = tk.Label(root, text="Cargando modelo Whisper (0%)")
        self.progress_label_model.pack()
        self.progress_model = ttk.Progressbar(root, length=400, mode='determinate')
        self.progress_model.pack(pady=5)

        self.progress_label_trans = tk.Label(root, text="Transcribiendo (0%)")
        self.progress_label_trans.pack()
        self.progress_trans = ttk.Progressbar(root, length=400, mode='determinate')
        self.progress_trans.pack(pady=5)

    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Multimedia", "*.mp3 *.wav *.flac *.ogg *.mp4 *.mov *.mkv")]
        )
        if archivo:
            hilo = threading.Thread(target=self.procesar_archivo, args=(archivo,))
            hilo.start()

    def actualizar_progreso(self, barra, etiqueta, texto, valor):
        porcentaje = int(valor)
        barra["value"] = porcentaje
        etiqueta.config(text=f"{texto} ({porcentaje}%)")
        self.root.update_idletasks()
        print(f"{texto}: {porcentaje}%")

    def guardar_log_error(self, contenido, tipo, carpeta):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_log = f"error_{tipo}_{timestamp}.log"
        ruta_log = os.path.join(carpeta, nombre_log)
        with open(ruta_log, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"[ERROR] Log guardado en: {ruta_log}")

    def obtener_duracion_video(self, archivo_video):
        try:
            resultado = subprocess.run([
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of",
                "default=noprint_wrappers=1:nokey=1", archivo_video
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            duracion = float(resultado.stdout.decode().strip())
            return duracion
        except:
            return None

    def extraer_audio(self, archivo_video):
        temp_dir = tempfile.mkdtemp()
        archivo_audio = os.path.join(temp_dir, "extraido.mp3")
        duracion_total = self.obtener_duracion_video(archivo_video)
        if not duracion_total:
            return None

        comando = ["ffmpeg", "-i", archivo_video, "-vn", "-acodec", "mp3", "-y", archivo_audio]
        proceso = subprocess.Popen(comando, stderr=subprocess.PIPE, text=True)

        for linea in proceso.stderr:
            match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', linea)
            if match:
                h, m, s = match.groups()
                tiempo_actual = int(h)*3600 + int(m)*60 + float(s)
                porcentaje = min((tiempo_actual / duracion_total) * 100, 100)
                self.actualizar_progreso(self.progress_audio, self.progress_label_audio, "Extrayendo audio", porcentaje)

        proceso.wait()
        self.actualizar_progreso(self.progress_audio, self.progress_label_audio, "Extrayendo audio", 100)
        return archivo_audio if os.path.exists(archivo_audio) else None

    def cargar_modelo_whisper(self):
        try:
            self.actualizar_progreso(self.progress_model, self.progress_label_model, "Cargando modelo Whisper", 0)

            texto_modelo = self.modo_var.get()
            if "base" in texto_modelo:
                nombre_modelo = "base"
            elif "small" in texto_modelo:
                nombre_modelo = "small"
            elif "medium" in texto_modelo:
                nombre_modelo = "medium"
            else:
                nombre_modelo = "tiny"

            model = WhisperModel(nombre_modelo, device="cpu", compute_type="int8")
            for p in range(1, 101):
                self.actualizar_progreso(self.progress_model, self.progress_label_model, "Cargando modelo Whisper", p)
                time.sleep(0.01)
            return model
        except Exception:
            return None

    def dividir_audio_en_chunks(self, archivo_audio, duracion_total):
        chunks = []
        carpeta_temp = tempfile.mkdtemp()
        total_chunks = 100
        chunk_duracion = duracion_total / total_chunks

        for i in range(total_chunks):
            inicio = i * chunk_duracion
            nombre_chunk = os.path.join(carpeta_temp, f"chunk_{i}.mp3")
            comando = [
                "ffmpeg", "-y", "-i", archivo_audio,
                "-ss", str(inicio), "-t", str(chunk_duracion),
                "-acodec", "copy", nombre_chunk
            ]
            subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            chunks.append(nombre_chunk)

        return chunks

    def transcribir_audio_por_chunks(self, archivo_audio, modelo):
        duracion_total = self.obtener_duracion_video(archivo_audio)
        chunks = self.dividir_audio_en_chunks(archivo_audio, duracion_total)

        resultado = ""
        total = len(chunks)
        progreso_actual = 0

        for i, chunk in enumerate(chunks):
            segments, info = modelo.transcribe(chunk, beam_size=5)
            for segment in segments:
                resultado += f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}\n"
            progreso = ((i + 1) / total) * 100
            if progreso > progreso_actual:
                progreso_actual = progreso
                self.actualizar_progreso(self.progress_trans, self.progress_label_trans, "Transcribiendo", progreso_actual)

        return resultado

    def procesar_archivo(self, archivo):
        inicio = datetime.now()
        carpeta_script = os.path.dirname(os.path.abspath(__file__))
        carpeta_trans = os.path.join(carpeta_script, "transcripciones")
        os.makedirs(carpeta_trans, exist_ok=True)

        nombre_original = os.path.splitext(os.path.basename(archivo))[0]
        archivo_salida = os.path.join(carpeta_trans, f"transcripcion_{nombre_original}.txt")

        ext = os.path.splitext(archivo)[1].lower()
        if ext in [".mp4", ".mov", ".mkv"]:
            archivo_audio = self.extraer_audio(archivo)
            if not archivo_audio:
                self.guardar_log_error("Error extrayendo audio", "ffmpeg", carpeta_trans)
                messagebox.showerror("Error", "Error extrayendo audio del video.")
                return
        else:
            archivo_audio = archivo
            self.actualizar_progreso(self.progress_audio, self.progress_label_audio, "Extrayendo audio", 100)

        modelo = self.cargar_modelo_whisper()
        if modelo is None:
            self.guardar_log_error("Error al cargar modelo", "modelo", carpeta_trans)
            messagebox.showerror("Error", "No se pudo cargar el modelo.")
            return

        texto = self.transcribir_audio_por_chunks(archivo_audio, modelo)

        if texto is None:
            self.guardar_log_error("Transcripción vacía", "transcripcion", carpeta_trans)
            messagebox.showerror("Error", "No se generó texto.")
            return

        try:
            with open(archivo_salida, "w", encoding="utf-8") as f:
                f.write(texto)
            self.actualizar_progreso(self.progress_trans, self.progress_label_trans, "Transcribiendo", 100)
            fin = datetime.now()
            duracion = fin - inicio
            minutos = duracion.total_seconds() // 60
            segundos = int(duracion.total_seconds() % 60)
            tiempo_str = f"{int(minutos)} min {segundos} s"
            messagebox.showinfo("Finalizado", f"Transcripción guardada en:\n{archivo_salida}\n\nTiempo de operación: {tiempo_str}")
            print(f"\n✅ Transcripción completada en {tiempo_str}")
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            os.startfile(carpeta_trans)
        except Exception as e:
            self.guardar_log_error(str(e), "guardado", carpeta_trans)
            messagebox.showerror("Error", f"Error al guardar archivo:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TranscriptorApp(root)
    root.mainloop()
