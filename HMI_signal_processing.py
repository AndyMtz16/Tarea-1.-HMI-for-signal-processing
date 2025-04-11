import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy import signal
import librosa
import soundfile as sf
import pygame
import os
import tempfile

class AudioProcessingApp:
    # Inicializa la app, configura la ventana y variables básicas.
    def __init__(self, root):
        self.root = root
        self.root.title("Procesador de Audio HMI")
        self.root.geometry("1200x700")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.audio_data = None
        self.sample_rate = None
        self.processed_audio = None

        self.playing_original = False
        self.playing_filtered = False
        self.temp_original = None
        self.temp_filtered = None

        pygame.mixer.init()

        self.filter_colors = {"Pasa-bajas": "red", "Pasa-altas": "green", "Pasa-banda": "purple"}
        self.current_filter_type = None

        self.configure_styles()
        self.init_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # Configura los estilos de los widgets de la UI.
    def configure_styles(self):
        style = ttk.Style()
        style.configure('Large.TButton', padding=(10, 5), font=('Arial', 10, 'bold'))
        style.configure('Play.TButton', padding=(20, 10), font=('Arial', 11, 'bold'))
        style.configure('Large.TLabel', font=('Arial', 10))
        style.configure('Large.TCombobox', padding=(5, 5))
        style.configure('Large.TSpinbox', padding=(5, 5))
        style.configure('Playback.TFrame', relief='groove', padding=10)
        style.configure('Playback.TLabel', font=('Arial', 11, 'bold'))

    # Crea la interfaz gráfica con botones, gráficos y controles de reproducción.
    def init_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)

        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky=(tk.W, tk.E))
        self.load_button = ttk.Button(controls_frame, text="Cargar archivo", command=self.load_audio, style='Large.TButton')
        self.load_button.grid(row=0, column=0, padx=5)
        ttk.Label(controls_frame, text="Tipo de Filtro:", style='Large.TLabel').grid(row=0, column=1, padx=5)
        self.filter_type = ttk.Combobox(controls_frame, values=list(self.filter_colors.keys()), state="readonly", style='Large.TCombobox', width=15)
        self.filter_type.current(0)
        self.filter_type.grid(row=0, column=2, padx=5)
        ttk.Label(controls_frame, text="Frecuencia de Corte (Hz):", style='Large.TLabel').grid(row=0, column=3, padx=5)
        self.cutoff_freq = ttk.Spinbox(controls_frame, from_=20, to=20000, increment=100, width=10, style='Large.TSpinbox')
        self.cutoff_freq.set(1000)
        self.cutoff_freq.grid(row=0, column=4, padx=5)
        ttk.Label(controls_frame, text="Orden del Filtro:", style='Large.TLabel').grid(row=0, column=5, padx=5)
        self.filter_order = ttk.Spinbox(controls_frame, from_=1, to=10, width=5, style='Large.TSpinbox')
        self.filter_order.set(4)
        self.filter_order.grid(row=0, column=6, padx=5)
        self.apply_filter_button = ttk.Button(controls_frame, text="Aplicar Filtro", command=self.apply_filter, style='Large.TButton')
        self.apply_filter_button.grid(row=0, column=7, padx=5)
        self.reset_button = ttk.Button(controls_frame, text="Resetear", command=self.reiniciar_signal, style='Large.TButton')
        self.reset_button.grid(row=0, column=8, padx=5)
        self.save_button = ttk.Button(controls_frame, text="Guardar Resultado", command=self.save_audio, style='Large.TButton')
        self.save_button.grid(row=0, column=9, padx=5)

        plots_frame = ttk.Frame(main_frame)
        plots_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        plots_frame.rowconfigure(0, weight=3)
        plots_frame.rowconfigure(1, weight=2)
        plots_frame.columnconfigure(0, weight=1)
        plots_frame.columnconfigure(1, weight=1)

        playback_frame = ttk.Frame(main_frame, style='Playback.TFrame')
        playback_frame.grid(row=1, column=1, padx=10, sticky=(tk.N, tk.E))
        ttk.Label(playback_frame, text="Reproducción", style='Playback.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 10))
        ttk.Label(playback_frame, text="Audio Original:", style='Large.TLabel').grid(row=1, column=0, pady=5)
        self.play_original_button = ttk.Button(playback_frame, text="▶ Play", command=self.toggle_play_original, style='Play.TButton')
        self.play_original_button.grid(row=2, column=0, pady=(0, 15))
        ttk.Label(playback_frame, text="Audio Filtrado:", style='Large.TLabel').grid(row=3, column=0, pady=5)
        self.play_filtered_button = ttk.Button(playback_frame, text="▶ Play", command=self.toggle_play_filtered, style='Play.TButton')
        self.play_filtered_button.grid(row=4, column=0, pady=(0, 15))
        self.play_filtered_button.state(['disabled'])

        self.figure = plt.Figure(figsize=(12, 4))
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Señal de Audio")
        self.canvas = FigureCanvasTkAgg(self.figure, master=plots_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.figure.tight_layout()

        self.figure_fft_original = plt.Figure(figsize=(6, 3))
        self.ax_fft_original = self.figure_fft_original.add_subplot(111)
        self.ax_fft_original.set_title("FFT - Señal Original")
        self.canvas_fft_original = FigureCanvasTkAgg(self.figure_fft_original, master=plots_frame)
        self.canvas_fft_original.get_tk_widget().grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.figure_fft_original.subplots_adjust(left=0.15, right=0.95, bottom=0.2, top=0.9)

        self.figure_fft_filtered = plt.Figure(figsize=(6, 3))
        self.ax_fft_filtered = self.figure_fft_filtered.add_subplot(111)
        self.ax_fft_filtered.set_title("FFT - Señal Filtrada")
        self.canvas_fft_filtered = FigureCanvasTkAgg(self.figure_fft_filtered, master=plots_frame)
        self.canvas_fft_filtered.get_tk_widget().grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.figure_fft_filtered.subplots_adjust(left=0.15, right=0.95, bottom=0.2, top=0.9)

    # ==================== Grupo 1: Funciones de graficar ====================
    # Grafica la signal en el gráfico principal.
    def graficar_signal(self):
        self.ax.clear()
        tiempo = np.arange(len(self.audio_data)) / self.sample_rate
        self.ax.plot(tiempo, self.audio_data, 'b-', label='Señal Original', alpha=0.7)
        if self.processed_audio is not None and self.current_filter_type:
            color = self.filter_colors[self.current_filter_type]
            self.ax.plot(tiempo, self.processed_audio, color=color, label=f'Filtro {self.current_filter_type}', alpha=0.7)
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Amplitud")
        self.ax.set_title("Señal de Audio")
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()

    # Grafica la FFT de la signal pasada y le pone un título.
    def graficar_fft(self, signal, titulo):
        if signal is self.audio_data:
            eje_fft, fig_fft, lienzo_fft = self.ax_fft_original, self.figure_fft_original, self.canvas_fft_original
            color, etiqueta = "blue", "FFT Original"
        else:
            eje_fft, fig_fft, lienzo_fft = self.ax_fft_filtered, self.figure_fft_filtered, self.canvas_fft_filtered
            color, etiqueta = self.filter_colors[self.current_filter_type], f"FFT {self.current_filter_type}"
        eje_fft.clear()
        transformada = np.fft.fft(signal)
        frec = np.fft.fftfreq(len(signal), 1 / self.sample_rate)
        mascara = frec >= 0
        frec, magnitud = frec[mascara], np.abs(transformada)[mascara]
        eje_fft.plot(frec, magnitud, color=color, label=etiqueta, alpha=0.7)
        eje_fft.set_xlabel("Frecuencia (Hz)", fontsize=10, labelpad=8)
        eje_fft.set_ylabel("Magnitud", fontsize=10, labelpad=8)
        eje_fft.set_title(titulo, pad=10, fontsize=11)
        eje_fft.set_xlim(0, self.sample_rate / 2)
        eje_fft.tick_params(axis='both', which='major', labelsize=9)
        eje_fft.legend(loc='upper right', fontsize=9)
        eje_fft.grid(True, alpha=0.3, linestyle='--')
        fig_fft.tight_layout()
        lienzo_fft.draw()

    # ================= Grupo 2: Funciones para carga y descarga =================
    # Carga un audio desde un archivo y actualiza las gráficas.
    def load_audio(self):
        archivo = filedialog.askopenfilename(
            title="Cargar archivo de audio",
            filetypes=[("Archivos de audio", "*.wav *.mp3 *.aac"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            try:
                self.audio_data, self.sample_rate = librosa.load(archivo, sr=None)
                if self.temp_original:
                    os.unlink(self.temp_original)
                self.temp_original = self.create_temp_audio_file(self.audio_data, self.sample_rate)
                self.graficar_signal()
                self.processed_audio = None
                self.current_filter_type = None
                self.graficar_fft(self.audio_data, "Transformada de Fourier - Señal Original")
                self.play_original_button.state(['!disabled'])
                self.play_filtered_button.state(['disabled'])
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo: {str(e)}")

    # Guarda el audio procesado en un archivo WAV.
    def save_audio(self):
        if self.processed_audio is None:
            messagebox.showwarning("Advertencia", "No hay audio procesado para guardar.")
            return
        archivo_guardar = filedialog.asksaveasfilename(
            title="Guardar audio procesado",
            defaultextension=".wav",
            filetypes=[("Archivos WAV", "*.wav")]
        )
        if archivo_guardar:
            try:
                sf.write(archivo_guardar, self.processed_audio, self.sample_rate)
                messagebox.showinfo("Éxito", "Archivo guardado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar el archivo: {str(e)}")

    # ============== Grupo 3: Funciones para filtros y FFT (actualización) ==============
    # Aplica el filtro seleccionado a la signal y actualiza las gráficas.
    def apply_filter(self):
        if self.audio_data is None:
            messagebox.showwarning("Advertencia", "Por favor, cargue un archivo de audio primero.")
            return
        try:
            nyquist = self.sample_rate / 2
            corte = float(self.cutoff_freq.get()) / nyquist
            orden = int(self.filter_order.get())
            self.current_filter_type = self.filter_type.get()
            if self.current_filter_type == "Pasa-bajas":
                b, a = signal.butter(orden, corte, btype='low')
            elif self.current_filter_type == "Pasa-altas":
                b, a = signal.butter(orden, corte, btype='high')
            elif self.current_filter_type == "Pasa-banda":
                b, a = signal.butter(orden, [0.5 * corte, corte], btype='band')
            self.processed_audio = signal.filtfilt(b, a, self.audio_data)
            if self.temp_filtered:
                os.unlink(self.temp_filtered)
            self.temp_filtered = self.create_temp_audio_file(self.processed_audio, self.sample_rate)
            self.graficar_signal()
            self.graficar_fft(self.processed_audio, f"Transformada de Fourier - {self.current_filter_type}")
            self.play_filtered_button.state(['!disabled'])
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos para los parámetros del filtro.")

    # Reinicia la signal filtrada y restablece la vista a la original.
    def reiniciar_signal(self):
        if self.audio_data is None:
            messagebox.showwarning("Advertencia", "No hay señal cargada para resetear.")
            return
        if pygame.mixer.get_busy():
            pygame.mixer.stop()
            self.playing_original = False
            self.playing_filtered = False
            self.play_original_button.configure(text="▶ Play")
            self.play_filtered_button.configure(text="▶ Play")
        self.processed_audio = None
        self.current_filter_type = None
        if self.temp_filtered:
            os.unlink(self.temp_filtered)
            self.temp_filtered = None
        self.graficar_signal()
        self.ax_fft_filtered.clear()
        self.ax_fft_filtered.set_title("FFT - Señal Filtrada")
        self.ax_fft_filtered.set_xlabel("Frecuencia (Hz)", fontsize=10)
        self.ax_fft_filtered.set_ylabel("Magnitud", fontsize=10)
        self.ax_fft_filtered.grid(True, alpha=0.3, linestyle='--')
        self.canvas_fft_filtered.draw()
        self.play_filtered_button.state(['disabled'])
        messagebox.showinfo("Reseteo", "Gráficas reseteadas a la señal original.")

    # ================= Grupo 4: Funciones para reproducir el audio =================
    # Crea un archivo temporal para reproducir el audio.
    def create_temp_audio_file(self, datos_audio, tasa):
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        sf.write(temp_file.name, datos_audio, tasa)
        return temp_file.name

    # Alterna entre reproducir y detener el audio original.
    def toggle_play_original(self):
        if not self.playing_original:
            if pygame.mixer.get_busy():
                pygame.mixer.stop()
                self.playing_filtered = False
                self.play_filtered_button.configure(text="▶ Play")
            if self.temp_original:
                pygame.mixer.music.load(self.temp_original)
                pygame.mixer.music.play()
                self.playing_original = True
                self.play_original_button.configure(text="■ Stop")
        else:
            pygame.mixer.music.stop()
            self.playing_original = False
            self.play_original_button.configure(text="▶ Play")

    # Alterna entre reproducir y detener el audio filtrado.
    def toggle_play_filtered(self):
        if not self.playing_filtered:
            if pygame.mixer.get_busy():
                pygame.mixer.stop()
                self.playing_original = False
                self.play_original_button.configure(text="▶ Play")
            if self.temp_filtered:
                pygame.mixer.music.load(self.temp_filtered)
                pygame.mixer.music.play()
                self.playing_filtered = True
                self.play_filtered_button.configure(text="■ Stop")
        else:
            pygame.mixer.music.stop()
            self.playing_filtered = False
            self.play_filtered_button.configure(text="▶ Play")

    # Al cerrar la app, limpia recursos y cierra la ventana.
    def on_closing(self):
        pygame.mixer.quit()
        if self.temp_original:
            os.unlink(self.temp_original)
        if self.temp_filtered:
            os.unlink(self.temp_filtered)
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = AudioProcessingApp(root)
    root.mainloop()
