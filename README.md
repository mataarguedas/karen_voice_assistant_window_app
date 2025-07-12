Karen - A Personal Voice Assistant

A desktop voice assistant with a clean graphical user interface built using Python. Karen listens for a wake word, responds to commands in both English and Spanish, and provides visual feedback for an interactive experience.

Features

    Bilingual Support: Fully functional in both English and Spanish, from wake word to command processing.

    Wake Word Detection: Utilizes the powerful and lightweight Porcupine wake word engine to listen for "Hey Karen" (English) or "Ey Karen" (Spanish).

    Core Voice Commands:

        Time & Date: Get the current time and date.

        Location: Instantly find out your current country.

        Timers: Set timers with simple voice commands.

        Web Search: Search for anything on Google.

        YouTube Integration: Play your favorite videos directly on YouTube.

    Graphical User Interface (GUI): A sleek and modern UI built with PyQt5 that displays a log of interactions and provides a circular visual indicator that animates when Karen is actively listening.

    Text-to-Speech Feedback: Karen communicates back, confirming actions and delivering information clearly.

Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

Prerequisites

    Python 3.8+

    A Picovoice Access Key. You can get one for free from the Picovoice Console.

    For some operating systems, PyAudio requires the portaudio library to be installed.

        On Debian/Ubuntu: sudo apt-get install portaudio19-dev

        On macOS (using Homebrew): brew install portaudio

Installation

    The easy-peasy-sneaky-peaky-lemon-squeezy way, download karen.exe and run it.

    Nevertheless, the hardy-farty-chili-spicy way:
    
    1. Clone the Repository
    git clone https://github.com/your-username/karen-voice-assistant.git
    cd karen-voice-assistant

    2. Project Structure
    Ensure all the necessary asset files are placed in the root directory of the project alongside the script. The application depends on these files to function correctly.
    
    /karen-voice-assistant
    ├── karen_ui.py               # Main application script
    ├── requirements.txt          # List of project dependencies
    ├── hey_karen_en.ppn          # English wake word model
    ├── hey_karen_es.ppn          # Spanish wake word model
    ├── porcupine_params_es.pv    # Porcupine Spanish language parameters
    ├── karenPic.jpeg             # Image used for the UI voice indicator
    ├── karenCirclePic.png        # Icon for the application window
    └── Roboto-Regular.ttf        # Custom font file

    3. Set Up a Virtual Environment
    It is highly recommended to use a virtual environment to manage dependencies and avoid conflicts.

    # Create the virtual environment
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate

    4. Install Dependencies
    A requirements.txt file is included to simplify the installation of all required Python libraries.

        requirements.txt:
          PyQt5
          pvporcupine
          pyaudio
          pyautogui
          pyttsx3
          pywhatkit
          SpeechRecognition
          geocoder
          Pillow

    Installation command:
    pip install -r requirements.txt

    5. Configure API Keys
    Open the karen_ui.py script and insert your Picovoice Access Key(s) into the Backend class.
    # in karen_ui.py:
    class Backend(QObject):
        def __init__(self):
            super().__init__()
            # Replace these placeholder strings with your actual key
            self.PICOVOICE_ACCESS_KEY_EN = "YOUR_PICOVOICE_ACCESS_KEY"
            self.PICOVOICE_ACCESS_KEY_ES = "YOUR_PICOVOICE_ACCESS_KEY"

Usage
    
    After completing the installation, you can launch the application by running the main script from your terminal:
    python karen_ui.py

    The application window will appear, and Karen will be passively listening for the wake word.

    Voice Commands
    Activate Karen with the wake word ("Hey Karen" or "Ey Karen") and then issue one of the following commands:

      1. "What time is it?" or "¿Qué hora es?" tells you the current time.
      2. "What's the date?" or "¿Qué día es hoy?" tells you the current date.
      3. "Where are we?" or "¿Dónde estamos?" identifies your current country via your IP.
      4. "Set a timer for X minutes" or "Pon un temporizador de X minutos" sets a timer for the specified X minutes.
      5. "Search for ____________________" or "Busca ____________________" opens a new browser tab with Google search results.
      6. "Play video name on YouTube" or "Reproduce video name en YouTube" finds and plays the requested video on YouTube.

License
    
    This project is distributed under the MIT License. See the LICENSE.md file for more details.
    
Acknowledgments
    
    A big thank you to Picovoice for providing the accurate and efficient Porcupine wake word engine.
    This assistant uses the Google Speech Recognition API via the versatile SpeechRecognition library.
