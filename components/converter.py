import streamlit as st
import re
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import speech_recognition as sr
from .ui_components import UIComponents
from .unit_config import UnitCategories
from .chat import ChatInterface

class VoiceInterface:
    def __init__(self, converter):
        self.converter = converter

    def render_voice_button(self):
        st.markdown("""
            <style>
            .stButton > button {
                width: 38px !important;
                height: 38px !important;
                border-radius: 50% !important;
                border: 2px solid #FF6B00 !important;
                background: transparent !important;
                padding: 0 !important;
                transition: all 0.3s ease !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                font-size: 18px !important;
                color: #FF6B00 !important;
                line-height: 38px !important;
            }
            .stButton > button:hover {
                background: rgba(255, 107, 0, 0.1) !important;
            }
            </style>
        """, unsafe_allow_html=True)
        if st.button("⏺", key="voice_button", help="Click to speak"):
            text = self.listen_and_transcribe()
            if text:
                self.process_voice_command(text)

    def process_voice_command(self, text):
        """Handle conversion requests aur chat response trigger karo"""
        # Conversion handling
        conversion_data = self.parse_conversion_request(text)
        if conversion_data:
            value, from_unit, to_unit = conversion_data
            category = self.detect_category(from_unit)
            if category:
                result = self.converter.convert(value, from_unit, to_unit, category)
                if result is not None:
                    st.session_state['last_conversion'] = {
                        'value': value,
                        'from_unit': from_unit,
                        'to_unit': to_unit,
                        'result': result
                    }

        # Chat response ke liye voice input process karo
        if self.converter.chat:
            response = self.converter.chat.get_response(text)
            if response:
                st.session_state.setdefault('messages', []).extend([
                    {"role": "user", "content": text},
                    {"role": "assistant", "content": response}
                ])
            else:
                st.write("Debug: Voice input ke liye LLM se response nahi mila")
        else:
            st.error("Chat interface initialize nahi hua - .env mein API key check karo")

        st.session_state['voice_input'] = text
        st.write(f"Debug: Voice input saved - {text}")

    def detect_category(self, unit):
        categories = UnitCategories.get_categories()
        for cat, data in categories.items():
            if unit in [u.lower() for u in data['units']]:
                return cat
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

    def listen_and_transcribe(self):
        class AudioProcessor(AudioProcessorBase):
            def __init__(self):
                self.recognizer = sr.Recognizer()

            def recv(self, frame):
                audio_data = frame.to_ndarray()
                try:
                    with sr.AudioFile(audio_data) as source:
                        audio = self.recognizer.record(source)
                        text = self.recognizer.recognize_google(audio)
                        return text.lower()
                except Exception:
                    return None

        ctx = webrtc_streamer(
            key="audio",
            audio_processor_factory=AudioProcessor,
            mode=WebRtcMode.SENDONLY,
            media_stream_constraints={"audio": True, "video": False}
        )
        if ctx.audio_receiver:
            try:
                audio_frame = ctx.audio_receiver.get_frame(timeout=5)
                if audio_frame:
                    recognizer = sr.Recognizer()
                    audio = recognizer.record(audio_frame.to_audio_data())
                    text = recognizer.recognize_google(audio)
                    if text:
                        st.session_state['voice_input'] = text.lower()
                        return text.lower()
            except Exception as e:
                st.error(f"Error: {str(e)}")
        return None

class UnitConverter:
    def __init__(self, model):
        self.model = model
        self.categories = UnitCategories.get_categories()
        self.ui = UIComponents(self.categories)
        self.chat = ChatInterface(model) if model else None
        self.voice = VoiceInterface(self)

    def convert(self, value, from_unit, to_unit, category):
        try:
            prompt = f"""Convert {value} {from_unit} to {to_unit}. 
            Return ONLY the numerical value without ANY text or explanations.
            Example: If converting 1 kilometer to miles, return 0.621371
            """
            
            response = self.model.chat(
                model='command',
                message=prompt,
                temperature=0
            )
            
            match = re.search(r"\d+\.?\d*", response.text)
            if not match:
                raise ValueError("Response mein numerical value nahi mila")
            
            result = float(match.group())
            if 'api_calls' in st.session_state:
                st.session_state.api_calls += 1
            return result
            
        except Exception as e:
            if "429" in str(e):
                st.warning("⏳ Too many requests! Please wait.", icon="⌛")
            else:
                st.error(f"Conversion Error: {str(e)}")
            return None

    def render(self):
        st.markdown("""
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp {background-color: #1E1E1E !important;}
            .main-header {
                color: #FF6B00;
                font-size: min(2.8rem, 8vw);
                text-align: center;
                margin-bottom: 2rem;
                padding: 1.5rem;
                background: #1E1E1E;
                border-radius: 12px;
                border: 2px solid #FF6B00;
            }
            .converter-container, .chat-container {
                background: #1E1E1E;
                padding: clamp(1rem, 3vw, 2rem);
                border-radius: 12px;
                border: 2px solid #FF6B00;
                margin-bottom: 1rem;
                width: 100%;
            }
            .voice-button {
                background-color: transparent !important;
                border: 2px solid #FF6B00 !important;
                border-radius: 50% !important;
                color: #FF6B00 !important;
                width: 40px !important;
                height: 40px !important;
                line-height: 40px !important;
                text-align: center !important;
                cursor: pointer !important;
                transition: all 0.3s ease !important;
            }
            .voice-button:hover {
                background-color: rgba(255, 107, 0, 0.1) !important;
                transform: scale(1.05);
            }
            .stButton > button {
                background-color: #FF6B00;
                color: #FFFFFF !important;
                font-size: clamp(1rem, 2.5vw, 1.3rem) !important;
                font-weight: 700 !important;
                padding: clamp(0.5rem, 2vw, 0.8rem) clamp(1rem, 4vw, 2rem);
                border-radius: 8px;
                border: none;
                width: 100%;
            }
            h3 {
                font-size: clamp(1.1rem, 3vw, 1.3rem) !important;
                margin-bottom: clamp(0.5rem, 2vw, 1rem);
            }
            .stSelectbox > div > div > div {
                font-size: clamp(0.9rem, 2.5vw, 1.1rem);
            }
            .stNumberInput input {
                font-size: clamp(0.9rem, 2.5vw, 1.1rem);
            }
            .stMarkdown ul {
                list-style: none;
                padding-left: 0;
            }
            .stMarkdown li {
                color: #FF6B00 !important;
                padding: clamp(0.3rem, 1.5vw, 0.5rem) 0;
                font-size: clamp(0.9rem, 2.5vw, 1rem);
                cursor: pointer;
            }
            @media (max-width: 768px) {
                .main .block-container {padding: 1rem;}
                [data-testid="column"] {width: 100% !important; flex: 1 1 auto !important; min-width: 100% !important;}
                .stButton > button {margin-top: 1rem;}
                .result-container {margin-top: 1rem;}
                .chat-container {margin-top: 1rem;}
            }
            @media (max-width: 480px) {
                .main-header {padding: 1rem; margin-bottom: 1rem;}
                .converter-container, .chat-container {padding: 0.8rem;}
                h3 {margin-bottom: 0.5rem;}
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<h1 class='main-header'>🈲 Unit Converter</h1>", unsafe_allow_html=True)

        left_col, right_col = st.columns([1, 1], gap="large")

        with left_col:
            st.markdown("<div class='converter-container'>", unsafe_allow_html=True)
            st.markdown("### 📊 Select Category")
            category = self.ui.render_category_selector()
            st.markdown("### 🈴 Choose Units")
            col1, col2 = st.columns(2)
            with col1:
                from_unit = st.selectbox("From", self.categories[category]["units"])
            with col2:
                to_unit = st.selectbox("To", self.categories[category]["units"])
            st.markdown("### 📝 Enter Value")
            value = st.number_input("", value=1.0, format="%f", step=0.1)
            st.markdown("""
            <style>
            .convert-button {
                background-color: #FF6B00 !important;
                color: white !important;
                border-radius: 8px !important;
                padding: 0.5rem 2rem !important;
                font-size: 1.2rem !important;
                font-weight: 600 !important;
                border: none !important;
                width: 100% !important;
                cursor: pointer !important;
                transition: all 0.3s ease !important;
                margin-top: 1rem !important;
                text-align: center !important;
            }
            .convert-button:hover {
                background-color: #FF8533 !important;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(255, 107, 0, 0.2);
            }
            .convert-button:active {transform: translateY(0);}
            .result-container {text-align: center; padding: 1rem 0; animation: fadeIn 0.5s ease;}
            .from-value {font-size: 1.4rem; color: #FFFFFF; font-weight: 500; letter-spacing: 0.5px;}
            .arrow {font-size: 1.6rem; color: #FF6B00; margin: 0.8rem 0; font-weight: bold;}
            .to-value {font-size: 2.2rem; color: #FF6B00; font-weight: 700; letter-spacing: 1px;}
            @keyframes fadeIn {from {opacity: 0; transform: translateY(10px);} to {opacity: 1; transform: translateY(0);}}
            </style>
            """, unsafe_allow_html=True)
            if st.markdown('<button class="convert-button">Convert ➜</button>', unsafe_allow_html=True):
                with st.spinner("Converting..."):
                    if self.model:
                        result = self.convert(value, from_unit, to_unit, category)
                        if result is not None:
                            st.markdown(f"""
                            <div class="result-container">
                                <div class="from-value">{value} {from_unit}</div>
                                <div class="arrow">↓</div>
                                <div class="to-value">{result:.4f} {to_unit}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.error("CoHERE model initialize nahi hua - .env mein API key check karo")

        with right_col:
            st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
            st.markdown("### 💬 Ask Me Anything")
            st.markdown("""
            - How to convert units
            - Explain measurement systems
            - Get conversion help
            - Usage examples
            """)

            chat_col, voice_col = st.columns([8, 1])
            with chat_col:
                prompt = st.chat_input("Ask about units or say...")
            with voice_col:
                self.voice.render_voice_button()

            # Voice input handle karo
            if 'voice_input' in st.session_state:
                voice_prompt = st.session_state.pop('voice_input')
                st.write(f"Debug: Voice input received - {voice_prompt}")
                if self.chat:
                    with st.spinner("Thinking..."):
                        response = self.chat.get_response(voice_prompt)
                        if response:
                            st.session_state.setdefault('messages', []).extend([
                                {"role": "user", "content": voice_prompt},
                                {"role": "assistant", "content": response}
                            ])

            # Text input handle karo
            if prompt and 'voice_input' not in st.session_state:
                st.write(f"Debug: Text input received - {prompt}")
                if self.chat:
                    with st.spinner("Thinking..."):
                        response = self.chat.get_response(prompt)
                        if response:
                            st.session_state.setdefault('messages', []).extend([
                                {"role": "user", "content": prompt},
                                {"role": "assistant", "content": response}
                            ])

            # Chat history display karo
            for message in st.session_state.get('messages', []):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if 'last_conversion' in st.session_state:
                conv = st.session_state['last_conversion']
                st.markdown(f"""
                <div class="result-container">
                    <div class="from-value">{conv['value']} {conv['from_unit']}</div>
                    <div class="arrow">↓</div>
                    <div class="to-value">{conv['result']:.4f} {conv['to_unit']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)