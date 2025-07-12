import datetime
import geocoder
import os
import pvporcupine
import pyaudio
import pyautogui
import pyttsx3
import pywhatkit
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QColor, QFont, QPainterPath, QIcon, QFontDatabase, QPen
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
import re
import speech_recognition as sr
import struct
import sys
import threading
import time
import webbrowser

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Backend(QObject):
    update_text = pyqtSignal(str)
    voice_activity = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        ## Here you must insert your own private keys. Follow the instructions:
        ## go to picovoice.ai/ > Sign In > Continue with Google > Enter your Google account > 
        ## Enter your first, last name and github profile > In console.picovoice.ai/ >> copy and paste the AccessKey.
        ## Then in the navbar, go to Porcupine > Select a language > English > Wake Word > "Hey Karen" > select the microphone icon
        ## After recognized, select Train > Platform > Windows (x86_64.arm64) > Select Download > Will download a .zip with a .ppn file
        ## Paste that .ppn file to the project folder.

        ## Do this procedure for each access key

        self.PICOVOICE_ACCESS_KEY_EN = "[Insert your own]"
        self.PICOVOICE_ACCESS_KEY_ES = "[Insert your own]"
        
        self.WAKE_WORD_PATH_EN = resource_path("[insert your .ppn file name here]")
        self.WAKE_WORD_PATH_ES = resource_path("[insert your .ppn file name here]")
        self.MODEL_PATH_ES = resource_path("porcupine_params_es.pv")

        self.update_text.emit(f"English wake word path: {self.WAKE_WORD_PATH_EN}")
        self.update_text.emit(f"Spanish wake word path: {self.WAKE_WORD_PATH_ES}")
        self.update_text.emit(f"Spanish model path: {self.MODEL_PATH_ES}")
        
        if not os.path.exists(self.WAKE_WORD_PATH_EN):
            self.update_text.emit(f"ERROR: English wake word file not found at {self.WAKE_WORD_PATH_EN}")
        if not os.path.exists(self.WAKE_WORD_PATH_ES):
            self.update_text.emit(f"ERROR: Spanish wake word file not found at {self.WAKE_WORD_PATH_ES}")
        if not os.path.exists(self.MODEL_PATH_ES):
            self.update_text.emit(f"ERROR: Spanish model file not found at {self.MODEL_PATH_ES}")

        self.MESSAGES = {
            'en': { "listening": "Listening for your command...", "unintelligible": "Sorry, I did not understand that.", "service_down": "Sorry, my speech service is down.", "playing_youtube": "Playing {} on YouTube...", "ask_youtube": "What video would you like me to play?", "searching_google": "Searching Google for: {}", "ask_search": "What would you like to search for?", "unrecognized": "Command not recognized.", "wake_detected": "Wake word detected!", "timer_set": "Okay, setting a timer for {} minutes.", "timer_done": "Your timer is up!", "timer_no_number": "Sorry, I couldn't determine the duration for the timer." },
            'es': { "listening": "Escuchando tu comando...", "unintelligible": "Disculpa, no entendí eso.", "service_down": "Disculpa, el servicio de voz no está disponible.", "playing_youtube": "Reproduciendo {} en YouTube...", "ask_youtube": "¿Qué video te gustaría reproducir?", "searching_google": "Buscando en Google: {}", "ask_search": "¿Qué te gustaría buscar?", "unrecognized": "Comando no reconocido.", "wake_detected": "¡Palabra de activación detectada!", "timer_set": "Ok, iniciando un temporizador de {} minutos.", "timer_done": "¡Se acabó el tiempo!", "timer_no_number": "Disculpa, no pude determinar la duración del temporizador." }
        }
        self._is_running = True

    def stop(self):
        self._is_running = False

    def speak_in_thread(self, text, lang_choice):
        try:
            engine = pyttsx3.init()
            if lang_choice == 'es':
                voices = engine.getProperty('voices')
                es_voice = next((v for v in voices if 'spanish' in v.name.lower()), None)
                if es_voice:
                    engine.setProperty('voice', es_voice.id)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            self.update_text.emit(f"TTS Error: {e}")

    def speak(self, text, lang_choice='en'):
        if text == self.MESSAGES[lang_choice]["wake_detected"]:
            return
        self.update_text.emit(f"Karen: {text}")
        threading.Thread(target=self.speak_in_thread, args=(text, lang_choice), daemon=True).start()

    def listen_for_command(self, language_code='en-US', lang_choice='en'):
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                self.update_text.emit(self.MESSAGES[lang_choice]["listening"])
                self.voice_activity.emit(True)
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                self.voice_activity.emit(False)
            
            command = r.recognize_google(audio, language=language_code).lower()
            self.update_text.emit(f"You said: {command}")
            return command
        except sr.WaitTimeoutError:
            self.update_text.emit("Listening timeout - no speech detected")
            self.voice_activity.emit(False)
            return None
        except sr.UnknownValueError:
            self.speak(self.MESSAGES[lang_choice]["unintelligible"], lang_choice)
            return None
        except sr.RequestError:
            self.speak(self.MESSAGES[lang_choice]["service_down"], lang_choice)
            return None
        except Exception as e:
            self.update_text.emit(f"Speech recognition error: {e}")
            self.voice_activity.emit(False)
            return None

    def process_command(self, command, lang_choice='en'):
        if command is None:
            return
        
        timer_en_pattern = r"set a timer for (\d+) minutes"
        timer_es_pattern = r"pon un temporizador de (\d+) minutos"
        match_en = re.search(timer_en_pattern, command)
        match_es = re.search(timer_es_pattern, command)

        if match_en and lang_choice == 'en':
            self.set_timer(match_en.group(1), lang_choice)
        elif match_es and lang_choice == 'es':
            self.set_timer(match_es.group(1), lang_choice)
        elif ("what time is it" in command and lang_choice == 'en') or ("qué hora es" in command and lang_choice == 'es'):
            self.speak(self.get_current_time(lang_choice), lang_choice)
        elif ("what's the date" in command and lang_choice == 'en') or ("qué día es hoy" in command and lang_choice == 'es'):
            self.speak(self.get_current_date(lang_choice), lang_choice)
        elif ("where are we" in command and lang_choice == 'en') or ("dónde estamos" in command and lang_choice == 'es'):
            self.speak("We are in " + self.get_current_location() if lang_choice == 'en' else "Estamos en " + self.get_current_location(), lang_choice)
        elif ("search for" in command and lang_choice == 'en') or ("busca" in command and lang_choice == 'es'):
            query = command.split("search for" if lang_choice == 'en' else "busca", 1)[1].strip()
            if query: self.search_google(query, lang_choice)
            else: self.speak(self.MESSAGES[lang_choice]["ask_search"], lang_choice)
        elif (("play" in command and "on youtube" in command) and lang_choice == 'en') or (("reproduce" in command and "en youtube" in command) and lang_choice == 'es'):
            video_name = command.split("play", 1)[1].split("on youtube", 1)[0].strip() if lang_choice == 'en' else command.split("reproduce", 1)[1].split("en youtube", 1)[0].strip()
            if video_name: self.play_on_youtube(video_name, lang_choice)
            else: self.speak(self.MESSAGES[lang_choice]["ask_youtube"], lang_choice)
        else:
            self.speak(self.MESSAGES[lang_choice]["unrecognized"], lang_choice)

    def set_timer(self, duration_minutes, lang_choice='en'):
        def timer_finished(): self.speak(self.MESSAGES[lang_choice]['timer_done'], lang_choice)
        try:
            threading.Timer(int(duration_minutes) * 60, timer_finished).start()
            self.speak(self.MESSAGES[lang_choice]['timer_set'].format(duration_minutes), lang_choice)
        except ValueError: self.speak(self.MESSAGES[lang_choice]['timer_no_number'], lang_choice)

    def get_current_time(self, lang_choice='en'):
        return datetime.datetime.now().strftime("The time is %I:%M %p" if lang_choice == 'en' else "La hora es %I:%M %p")

    def get_current_date(self, lang_choice='en'):
        now = datetime.datetime.now()
        if lang_choice == 'es': return now.strftime(f"Hoy es %A, %d de %B de %Y")
        def suffix(d): return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')
        return now.strftime(f"Today is %A, %B {now.day}{suffix(now.day)}, %Y")

    def get_current_location(self): return geocoder.ip('me').country
    
    def search_google(self, q, l): self.speak(self.MESSAGES[l]["searching_google"].format(q),l); webbrowser.open(f"https://google.com/search?q={q.replace(' ','+')}")

    def play_on_youtube(self, v, l):
        try:
            self.speak(self.MESSAGES[l]["playing_youtube"].format(v),l); pywhatkit.playonyt(v); time.sleep(3); pyautogui.click(pyautogui.size().width/2, pyautogui.size().height/2)
        except Exception as e: self.update_text.emit(f"YouTube Error: {e}")

    def run(self):
        porcupine_en, porcupine_es, pa, audio_stream = None, None, None, None
        try:
            while self._is_running:
                try:
                    porcupine_en = pvporcupine.create(access_key=self.PICOVOICE_ACCESS_KEY_EN, keyword_paths=[self.WAKE_WORD_PATH_EN])
                    porcupine_es = pvporcupine.create(access_key=self.PICOVOICE_ACCESS_KEY_ES, keyword_paths=[self.WAKE_WORD_PATH_ES], model_path=self.MODEL_PATH_ES)
                    pa = pyaudio.PyAudio()
                    audio_stream = pa.open(
                        rate=porcupine_en.sample_rate,
                        channels=1,
                        format=pyaudio.paInt16,
                        input=True,
                        frames_per_buffer=porcupine_en.frame_length
                    )
                    while self._is_running:
                        pcm = audio_stream.read(porcupine_en.frame_length, exception_on_overflow=False)
                        pcm = struct.unpack_from("h" * porcupine_en.frame_length, pcm)
                        keyword_index_en = porcupine_en.process(pcm)
                        keyword_index_es = porcupine_es.process(pcm)
                        lang_choice = None
                        if keyword_index_en >= 0:
                            lang_choice = 'en'
                        elif keyword_index_es >= 0:
                            lang_choice = 'es'
                        if lang_choice:
                            try:
                                audio_stream.stop_stream()
                                audio_stream.close()
                            except:
                                pass
                            try:
                                pa.terminate()
                            except:
                                pass
                            try:
                                porcupine_en.delete()
                            except:
                                pass
                            try:
                                porcupine_es.delete()
                            except:
                                pass
                            audio_stream = None
                            pa = None
                            porcupine_en = None
                            porcupine_es = None
                            lang_code = 'en-US' if lang_choice == 'en' else 'es-CR'
                            self.update_text.emit(f"\n--- {self.MESSAGES[lang_choice]['wake_detected']} ---")
                            time.sleep(0.1)
                            command = self.listen_for_command(language_code=lang_code, lang_choice=lang_choice)
                            self.process_command(command, lang_choice=lang_choice)
                            break
                except Exception as e:
                    self.update_text.emit(f"Audio processing error: {e}")
                    time.sleep(0.1)
                finally:
                    if audio_stream:
                        try:
                            audio_stream.stop_stream()
                            audio_stream.close()
                        except:
                            pass
                        audio_stream = None
                    if pa:
                        try:
                            pa.terminate()
                        except:
                            pass
                        pa = None
                    if porcupine_en:
                        try:
                            porcupine_en.delete()
                        except:
                            pass
                        porcupine_en = None
                    if porcupine_es:
                        try:
                            porcupine_es.delete()
                        except:
                            pass
                        porcupine_es = None
        except Exception as e:
            self.update_text.emit(f"A critical error occurred: {e}")

class CircleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(150, 150)
        self.active = False
        self.image_path = resource_path("karenPic.jpeg")
        self.pixmap = QPixmap(self.image_path)
        
    def set_active(self, active):
        self.active = active
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.addEllipse(0, 0, self.width(), self.height())
        painter.setClipPath(path)

        scaled_pixmap = self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        x = (self.width() - scaled_pixmap.width()) / 2
        y = (self.height() - scaled_pixmap.height()) / 2

        painter.drawPixmap(self.rect(), self.pixmap)

        if self.active:
            pen_width = 4
            painter.setPen(QPen(QColor(0, 150, 255, 180), pen_width))
            painter.drawEllipse(
                int(pen_width / 2),
                int(pen_width / 2),
                int(self.width() - pen_width),
                int(self.height() - pen_width)
            )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Karen")
        self.setFixedSize(300, 600)
        self.setWindowIcon(QIcon(resource_path("karenCirclePic.png")))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.initial_full_text = "Karen"
        self.initial_current_text = ""
        self.initial_char_index = 0
        self.initial_message = QLabel(self.initial_current_text, self)
        self.set_roboto_font(self.initial_message, size=16, bold=True)
        self.initial_message.setAlignment(Qt.AlignCenter)
        self.initial_message.setWordWrap(True)
        self.initial_message.setStyleSheet("color: #7691ac;")
        self.initial_message.setGeometry(20, 250, self.width() - 40, 100)
        

        self.listening_full_text = "Listening for a wake word ('Hey Karen' or 'Ey Karen')..."
        self.listening_current_text = ""
        self.listening_char_index = 0

        self.voice_indicator = CircleWidget()
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setLineWrapMode(QTextEdit.WidgetWidth)
        self.set_roboto_font(self.console_output, size=10)
        self.console_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.palette().window().color().name()};
                color: #7792ad;
                border: none;
            }}
        """)

        sys.stdout = self
        sys.stderr = self

        self.start_initial_animation()

    def set_roboto_font(self, widget, size=10, bold=False):
        font_path = resource_path("Roboto-Regular.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            font = QFont(families[0], size)
        else:
            font = QFont("Arial", size)
        
        if bold:
            font.setBold(True)
        
        widget.setFont(font)

    def start_initial_animation(self):
        self.initial_message.show()
        self.initial_timer = QTimer(self)
        self.initial_timer.timeout.connect(self.update_initial_text)
        self.initial_timer.start(100)

    def update_initial_text(self):
        if self.initial_char_index < len(self.initial_full_text):
            self.initial_current_text += self.initial_full_text[self.initial_char_index]
            self.initial_message.setText(self.initial_current_text)
            self.initial_char_index += 1
        else:
            self.initial_timer.stop()
            QTimer.singleShot(2000, self.show_main_ui_and_start_second_animation)

    def show_main_ui_and_start_second_animation(self):
        self.initial_message.hide()
        
        self.main_layout.addWidget(self.voice_indicator, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(self.console_output)
        self.main_layout.addStretch()

        self.start_listening_animation()

    def start_listening_animation(self):
        self.listening_timer = QTimer(self)
        self.listening_timer.timeout.connect(self.update_listening_text)
        self.listening_timer.start(20)

    def update_listening_text(self):
        if self.listening_char_index < len(self.listening_full_text):
            self.listening_current_text += self.listening_full_text[self.listening_char_index]
            self.console_output.setText(self.listening_current_text)
            self.listening_char_index += 1
        else:
            self.listening_timer.stop()
            self.start_backend()

    def write(self, text):
        self.console_output.moveCursor(self.console_output.textCursor().End)
        self.console_output.insertPlainText(text)

    def flush(self):
        pass

    def start_backend(self):
        import traceback
        self.backend = Backend()
        self.backend.update_text.connect(self.update_console_from_backend)
        self.backend.voice_activity.connect(self.voice_indicator.set_active)
        def backend_thread_wrapper():
            try:
                self.backend.run()
            except Exception as e:
                tb = traceback.format_exc()
                self.update_console_from_backend(f"[CRITICAL] Backend thread exception: {e}\nTraceback:\n{tb}")
        self.backend_thread = threading.Thread(target=backend_thread_wrapper)
        self.backend_thread.daemon = True
        self.backend_thread.start()

    def update_console_from_backend(self, text):
        self.console_output.append(text)
        
    def closeEvent(self, event):
        if hasattr(self, 'backend'):
            self.backend.stop()
        event.accept()

if __name__ == "__main__":
    if not os.path.exists(resource_path("voice_indicator.png")):
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (150, 150), color = 'lightgray')
        draw = ImageDraw.Draw(img)
        draw.ellipse((10, 10, 140, 140), fill='gray')
        img.save(resource_path("voice_indicator.png"))

    import sys
    import traceback
    def excepthook(type, value, tb):
        err = ''.join(traceback.format_exception(type, value, tb))
        print(f"[UNHANDLED EXCEPTION]\n{err}")
        
        try:
            if hasattr(window, 'update_console_from_backend'):
                window.update_console_from_backend(f"[UNHANDLED EXCEPTION]\n{err}")
        except:
            pass
    sys.excepthook = excepthook
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())