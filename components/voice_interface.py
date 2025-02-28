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
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.subheader("🎤 Voice Commands")
            if st.button("🎤 Start Voice Command", use_container_width=True):
                with st.spinner("Initializing microphone..."):
                    text = self.listen_and_transcribe()
                    if text:
                        value, from_unit, to_unit = self.parse_conversion_request(text)
                        if all([value, from_unit, to_unit]):
                            # Find the appropriate category based on the units
                            category = self.find_category(from_unit, to_unit)
                            if category:
                                result = self.converter.convert(value, from_unit, to_unit, category)
                                if result is not None:
                                    result_text = f"{value} {from_unit} is equal to {result:.4f} {to_unit}"
                                    st.success(result_text)
                                    self.text_to_speech(result_text)
                            else:
                                st.error("Could not determine the conversion category. Please try again.", icon="❌")
                        else:
                            st.warning("Please use the format: 'Convert [number] [unit] to [unit]'", icon="⚠️")
        
        with col2:
            st.markdown("""
            <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px;">
                <h4 style="margin-top: 0;">💡 How to use voice commands:</h4>
                <ul>
                    <li>Click the "Start Voice Command" button</li>
                    <li>Speak naturally using the format:</li>
                    <li><i>"Convert [number] [unit] to [unit]"</i></li>
                    <li>Example: "Convert 10 kilometers to miles"</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    def find_category(self, from_unit, to_unit):
        for category, data in self.converter.categories.items():
            if from_unit.lower() in [u.lower() for u in data["units"]] and \
               to_unit.lower() in [u.lower() for u in data["units"]]:
                return category
        return None

    def listen_and_transcribe(self):
        """Listen for voice input and convert to text"""
        try:
            with sr.Microphone() as source:
                # Adjust for background noise silently
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                # Process audio to text without showing intermediate result
                text = self.recognizer.recognize_google(audio)
                return text.lower()
                
        except sr.UnknownValueError:
            st.error("Could not understand audio. Please speak clearly.")
        except sr.RequestError:
            st.error("Could not access speech recognition service.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
        return None