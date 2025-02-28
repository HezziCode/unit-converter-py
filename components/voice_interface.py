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
        """Render minimal voice interface"""
        st.markdown("""
            <style>
            .input-container {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 10px 0;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        
        input_type = st.radio(
            "Choose input method:",
            ["💬 Text Input", "🎤 Voice Input"],
            index=0
        )
        
        if input_type == "💬 Text Input":
            text = st.text_input(
                "Enter conversion command:",
                placeholder="Example: convert 5 kilometers to miles"
            )
            if text:
                self.process_command(text)
        else:
            if st.button("Start Voice Command", use_container_width=True):
                text = self.listen_and_transcribe()
                if text:
                    self.process_command(text)
                
        st.markdown('</div>', unsafe_allow_html=True)

    def process_command(self, text):
        """Process voice or text command"""
        try:
            value, from_unit, to_unit = self.parse_conversion_request(text)
            if value and from_unit and to_unit:
                category = self.find_category(from_unit, to_unit)
                if category:
                    result = self.converter.convert(value, from_unit, to_unit, category)
                    if result:
                        st.success(f"{value} {from_unit} = {result} {to_unit}")
                else:
                    st.warning("Could not determine conversion category")
            else:
                st.info("Please use format: convert [number] [unit] to [unit]")
        except Exception as e:
            st.error("Could not process command")

    def find_category(self, from_unit, to_unit):
        for category, data in self.converter.categories.items():
            if from_unit.lower() in [u.lower() for u in data["units"]] and \
               to_unit.lower() in [u.lower() for u in data["units"]]:
                return category
        return None

    def listen_and_transcribe(self):
        try:
            with sr.Microphone() as source:
                # Silently adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Listen without showing status
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    return text.lower() if text else None
                except (sr.UnknownValueError, sr.RequestError):
                    return None
                
        except Exception:
            return None  # Silently handle all errors