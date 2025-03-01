# components/voice_interface.py
# Voice interface component for handling speech recognition and voice commands

import streamlit as st
import streamlit.components.v1 as components
import speech_recognition as sr
from gtts import gTTS
import os
import re
import base64
import json
import time

class VoiceInterface:
    """Handles voice input, recognition and command processing"""
    def __init__(self, converter):
        # Initialize voice interface with converter reference
        self.converter = converter
        self.recognizer = sr.Recognizer()
        
        # Initialize session state for recording status
        if 'recording' not in st.session_state:
            st.session_state.recording = False
        if 'recording_error' not in st.session_state:
            st.session_state.recording_error = None

    def render_voice_button(self):
        # Add custom JavaScript for browser microphone access
        self._inject_webrtc_audio_js()
        
        # Voice button with improved error handling
        if st.button("⏺", key="voice_button", help="Click to speak"):
            # Check if we're on HTTPS
            is_https = st.get_option("browser.serverAddress").startswith("https")
            is_localhost = "localhost" in st.get_option("browser.serverAddress") or "127.0.0.1" in st.get_option("browser.serverAddress")
            
            if not is_https and not is_localhost:
                st.warning("⚠️ Microphone access requires HTTPS. Please use the secure URL.")
                return
                
            # Try WebRTC approach first
            text = self._webrtc_listen()
            
            # Fall back to PyAudio if WebRTC fails
            if not text:
                text = self.listen_and_transcribe()
                
            if text:
                st.session_state.voice_input = text
                st.experimental_rerun()

    def _inject_webrtc_audio_js(self):
        """Inject JavaScript for WebRTC audio capture"""
        webrtc_js = """
        <script>
        // Function to handle WebRTC audio capture
        async function captureAudio() {
            try {
                // Request microphone access
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                
                // Create audio context and recorder
                const audioContext = new AudioContext();
                const source = audioContext.createMediaStreamSource(stream);
                const processor = audioContext.createScriptProcessor(4096, 1, 1);
                const chunks = [];
                
                // Set up recording
                source.connect(processor);
                processor.connect(audioContext.destination);
                
                // Start recording
                processor.onaudioprocess = function(e) {
                    const sample = e.inputBuffer.getChannelData(0);
                    chunks.push(new Float32Array(sample));
                };
                
                // Stop recording after 3 seconds
                await new Promise(resolve => setTimeout(resolve, 3000));
                
                // Clean up
                processor.disconnect();
                source.disconnect();
                stream.getTracks().forEach(track => track.stop());
                
                // Convert to WAV format
                const audioBlob = new Blob(chunks, { type: 'audio/wav' });
                
                // Send to Streamlit
                const reader = new FileReader();
                reader.readAsDataURL(audioBlob);
                reader.onloadend = function() {
                    const base64data = reader.result.split(',')[1];
                    // Store in sessionStorage for Streamlit to access
                    sessionStorage.setItem('audioData', base64data);
                    // Notify Streamlit
                    window.parent.postMessage({type: 'streamlit:setComponentValue', value: true}, '*');
                };
                
                return true;
            } catch (err) {
                console.error('Error accessing microphone:', err);
                sessionStorage.setItem('micError', err.toString());
                return false;
            }
        }
        
        // Execute when button is clicked
        if (window.captureAudioRequested) {
            captureAudio();
        }
        </script>
        """
        
        # Inject the JavaScript
        components.html(webrtc_js, height=0)

    def _webrtc_listen(self):
        """Use WebRTC to capture audio in the browser"""
        try:
            # Set flag to trigger JavaScript
            components.html("""
            <script>
            window.captureAudioRequested = true;
            </script>
            """, height=0)
            
            # Wait for audio capture
            with st.spinner("Listening..."):
                time.sleep(3.5)  # Allow time for recording
            
            # Try to get the audio data
            # This would need a custom component to fully implement
            # For now, we'll fall back to PyAudio
            return None
            
        except Exception as e:
            st.session_state.recording_error = str(e)
            return None

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
        except Exception:
            pass
        return None, None, None

    def text_to_speech(self, text):
        try:
            tts = gTTS(text=text, lang='en')
            tts.save("temp_result.mp3")
            st.audio("temp_result.mp3")
            if os.path.exists("temp_result.mp3"):
                os.remove("temp_result.mp3")
        except Exception:
            pass

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
                        st.write(f"{value} {from_unit} = {result} {to_unit}")
                else:
                    st.error("Invalid")  # Simple horizontal message
            else:
                st.error("Invalid")  # Simple horizontal message
        except Exception:
            st.error("Error")  # Simple horizontal message

    def find_category(self, from_unit, to_unit):
        """Find the category that contains both units"""
        for category, data in self.converter.categories.items():
            if from_unit.lower() in [u.lower() for u in data["units"]] and \
               to_unit.lower() in [u.lower() for u in data["units"]]:
                return category
        return None

    def listen_and_transcribe(self):
        """Listen for voice input and convert to text"""
        try:
            # Check if we're on HTTPS
            is_https = st.get_option("browser.serverAddress").startswith("https")
            is_localhost = "localhost" in st.get_option("browser.serverAddress") or "127.0.0.1" in st.get_option("browser.serverAddress")
            
            if not is_https and not is_localhost:
                st.warning("⚠️ Microphone access requires HTTPS. Please use the secure URL.")
                return None
                
            # Display recording indicator
            with st.spinner("🎤 Listening..."):
                # Try multiple microphone configurations
                success = False
                error_message = ""
                
                # Try with default microphone first
                try:
                    with sr.Microphone() as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                        audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
                        text = self.recognizer.recognize_google(audio)
                        if text:
                            return text.lower()
                        success = True
                except Exception as e:
                    error_message = str(e)
                
                # If default failed, try listing and using available microphones
                if not success:
                    try:
                        mics = sr.Microphone.list_microphone_names()
                        
                        # Try each microphone
                        for idx, mic_name in enumerate(mics):
                            try:
                                with sr.Microphone(device_index=idx) as source:
                                    self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
                                    text = self.recognizer.recognize_google(audio)
                                    if text:
                                        return text.lower()
                                    success = True
                                    break
                            except Exception:
                                continue
                    except Exception as e:
                        error_message += f" | {str(e)}"
                
                # If all attempts failed, show error
                if not success:
                    st.error("Microphone access failed. Please check your browser settings.")
                    # Add detailed error info in an expander
                    with st.expander("Troubleshooting"):
                        st.markdown("""
                        ### Microphone Troubleshooting:
                        
                        1. **Check browser permissions**: Click the lock icon in your address bar and ensure microphone access is allowed
                        2. **Use Chrome or Firefox**: These browsers have better support for microphone access
                        3. **Try HTTPS**: Make sure you're accessing the app via HTTPS
                        4. **Disable extensions**: Some privacy extensions might block microphone access
                        """)
                        st.code(error_message)
                
        except Exception as e:
            st.error("Please check your microphone settings and try again")
            with st.expander("Error details"):
                st.code(str(e))
        return None