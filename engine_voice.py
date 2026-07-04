# engine_voice.py - Offline Text-to-Speech (TTS) engine
import pyttsx3
import threading

class VoiceEngine:
    def __init__(self):
        self.enabled = True
        try:
            # Test initialization
            engine = pyttsx3.init()
            engine.setProperty('rate', 165)
            # Try to get voices
            voices = engine.getProperty('voices')
            if voices:
                # Default to female voice if available, otherwise native default
                for voice in voices:
                    if "female" in voice.name.lower() or "zira" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
        except Exception as e:
            print(f"Voice engine warning: Offline TTS init failed: {e}. Falling back to visual indicators only.")
            self.enabled = False

    def speak(self, text: str):
        """Speak output text in a separate background thread to avoid execution blocking."""
        if not self.enabled:
            return
        
        def _speech_worker(phrase):
            try:
                # Clean text of emojis and special characters for clearer pronunciation
                clean_phrase = phrase.replace("✅", "").replace("⚠️", "").replace("🔌", "").strip()
                if not clean_phrase:
                    return
                # Re-initialize within the worker thread for clean COM lifecycle on Windows
                th_engine = pyttsx3.init()
                th_engine.setProperty('rate', 165)
                th_engine.say(clean_phrase)
                th_engine.runAndWait()
            except Exception as ex:
                print(f"TTS Worker Error: {ex}")

        threading.Thread(target=_speech_worker, args=(text,), daemon=True).start()
