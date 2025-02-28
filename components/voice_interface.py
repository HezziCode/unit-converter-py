# components/voice_interface.py
# Voice interface component for handling speech recognition and voice commands

import streamlit as st
import streamlit.components.v1 as components
import speech_recognition as sr
from gtts import gTTS
import os
import re
import unicodedata

class VoiceInterface:
    """Handles voice input, recognition and command processing"""
    def __init__(self, converter):
        # Initialize voice interface with converter reference
        self.converter = converter
        self.recognizer = sr.Recognizer()

    def render_voice_button(self):
        # Add Font Awesome and custom styling

        # Voice button with Font Awesome icon
        if st.button("⏺", key="voice_button", help="Click to speak"):
            text = self.listen_and_transcribe()
            if text:
                st.session_state.voice_input = text
                st.experimental_rerun()
    
    def handle_voice_input(self):
        if 'voice_text' in st.session_state:
            return st.session_state.voice_text
        return None

    def parse_conversion_request(self, text):
        """Parse voice command for conversion parameters"""
        try:
            # Extract numbers and units from voice command
            pattern = r"convert (\d+\.?\d*) (\w+) to (\w+)"
            match = re.search(pattern, text.lower())
            if match:
                return float(match.group(1)), match.group(2), match.group(3)
        except Exception as e:
            st.error(f"Could not parse conversion request: {str(e)}")
        return None, None, None

    def text_to_speech(self, text):
        try:
            tts = gTTS(text=text, lang='en')
            tts.save("temp_result.mp3")
            st.audio("temp_result.mp3")
            if os.path.exists("temp_result.mp3"):
                os.remove("temp_result.mp3")
        except Exception:
            st.warning("Could not play audio response.", icon="🔊")

    def render(self):
        st.markdown("""
            <style>
            .voice-container {
                display: flex;
                align-items: center;
                gap: 20px;
                padding: 15px;
                background: #1E1E1E;
                border-radius: 10px;
                border: 2px solid #FF6B00;
                margin: 10px 0;
            }
            .voice-status {
                flex: 1;
                text-align: center;
            }
            </style>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.subheader("🎤 Voice Commands")
            if st.button("Start Voice Command", use_container_width=True):
                with st.spinner(""):  # Empty spinner to avoid vertical messages
                    text = self.listen_and_transcribe()
                    if text:
                        st.markdown(f"""
                            <div class="voice-container">
                                <div class="voice-status">✅ "{text}"</div>
                            </div>
                        """, unsafe_allow_html=True)
                        # Process the command...

    def find_category(self, from_unit, to_unit):
        for category, data in self.converter.categories.items():
            if from_unit.lower() in [u.lower() for u in data["units"]] and \
               to_unit.lower() in [u.lower() for u in data["units"]]:
                return category
        return None

    def listen_and_transcribe(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    st.success(f"Recognized: {text}")
                    return text.lower()
                except sr.UnknownValueError:
                    st.warning("Could not understand", icon="🎤")
                except sr.RequestError:
                    st.error("Service error", icon="⚠️")
                
        except Exception as e:
            st.error("Device error", icon="🎤")
        return None