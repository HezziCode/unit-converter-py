import streamlit as st
import speech_recognition as sr
import re
from gtts import gTTS
import os
import time

class VoiceInterface:
    def __init__(self, converter):
        self.converter = converter
        self.recognizer = sr.Recognizer()

    def render_voice_button(self):
        if st.button("⏺", key="voice_button", help="Click to speak"):
            text = self.listen_and_transcribe()
            if text:
                st.session_state.voice_input = text
                st.experimental_rerun()

    def listen_and_transcribe(self):
        try:
            with st.spinner("🎤 Listening..."):
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                text = self.recognizer.recognize_google(audio)
                return text.lower()
        except sr.RequestError:
            st.error("Unable to access the speech recognition service. Please try again later.")
        except sr.UnknownValueError:
            st.error("Sorry, I couldn't understand that. Please try again.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        return None

    def parse_conversion_request(self, text):
        try:
            pattern = r"convert (\d+\.?\d*) (\w+) to (\w+)"
            match = re.search(pattern, text.lower())
            if match:
                return float(match.group(1)), match.group(2), match.group(3)
        except Exception:
            pass
        return None, None, None

    def process_command(self, text):
        value, from_unit, to_unit = self.parse_conversion_request(text)
        if value and from_unit and to_unit:
            category = self.find_category(from_unit, to_unit)
            if category:
                result = self.converter.convert(value, from_unit, to_unit, category)
                if result:
                    response = f"{value} {from_unit} is equal to {result:.4f} {to_unit}"
                    st.success(response)
                    self.text_to_speech(response)
                else:
                    st.error("Conversion failed. Please try again.")
            else:
                st.error("Couldn't find matching units. Please try again.")
        else:
            st.error("Couldn't understand the command. Please try again.")

    def find_category(self, from_unit, to_unit):
        for category, data in self.converter.categories.items():
            if from_unit.lower() in [u.lower() for u in data["units"]] and \
               to_unit.lower() in [u.lower() for u in data["units"]]:
                return category
        return None

    def text_to_speech(self, text):
        try:
            tts = gTTS(text=text, lang='en')
            tts.save("temp_result.mp3")
            st.audio("temp_result.mp3")
            time.sleep(1)  # Give the audio player a moment to load
            if os.path.exists("temp_result.mp3"):
                os.remove("temp_result.mp3")
        except Exception as e:
            st.error(f"Text-to-speech error: {str(e)}")

    def handle_voice_input(self):
        if 'voice_input' in st.session_state:
            text = st.session_state.voice_input
            st.write(f"You said: {text}")
            self.process_command(text)
            del st.session_state.voice_input

