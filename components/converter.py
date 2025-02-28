import streamlit as st
from .ui_components import UIComponents
from .unit_config import UnitCategories
from .chat import ChatInterface
from .voice_interface import VoiceInterface

class UnitConverter:
    """Main converter class that integrates all components"""
    def __init__(self, model):
        # Initialize all components
        self.model = model
        self.categories = UnitCategories.get_categories()
        self.ui = UIComponents(self.categories)
        self.chat = ChatInterface(model)
        self.voice = VoiceInterface(self)

    def convert(self, value, from_unit, to_unit, category):
        """Perform unit conversion using AI model"""
        try:
            prompt = f"""
            Task: Unit conversion
            Convert: {value} {from_unit} to {to_unit}
            Category: {category}
            Instructions: Return only the numerical result without any text or units.
            Example: If converting 1 kilometer to miles, just return 0.621371
            """
            
            response = self.model.generate(
                prompt=prompt,
                max_tokens=20,
                temperature=0,
                return_likelihoods='NONE'
            )
            
            # Extract numerical result
            result = float(response.generations[0].text.strip())
            
            # Update API counter
            if 'api_calls' in st.session_state:
                st.session_state.api_calls += 1
            
            return result
            
        except Exception as e:
            if "429" in str(e):
                st.warning("⏳ Please wait a moment, we're experiencing high traffic.", icon="⌛")
            else:
                st.error(f"Conversion error: {str(e)}")
            return None

    def render(self):
        """Render the main converter interface"""
        st.markdown("""
            <style>
            /* Converter specific styles */
            .converter-container {
                background: #f8f9fa;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            @media (max-width: 768px) {
                .converter-container {
                    padding: 1rem;
                }
                
                /* Stack inputs on mobile */
                .conversion-inputs {
                    flex-direction: column;
                    gap: 0.5rem;
                }
            }
            </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="converter-container">', unsafe_allow_html=True)
            
            # Mobile-friendly layout
            if st.session_state.get('mobile_view', True):
                # Single column layout for mobile
                category = self.ui.render_category_selector()
                from_unit = self.ui.render_unit_selector("From", category)
                to_unit = self.ui.render_unit_selector("To", category)
                value = self.ui.render_value_input()
            else:
                # Two column layout for desktop
                col1, col2 = st.columns([1, 1])
                with col1:
                    category = self.ui.render_category_selector()
                    from_unit = self.ui.render_unit_selector("From", category)
                with col2:
                    value = self.ui.render_value_input()
                    to_unit = self.ui.render_unit_selector("To", category)
            
            if value and from_unit and to_unit:
                result = self.convert(value, from_unit, to_unit, category)
                if result:
                    self.ui.render_result(value, from_unit, to_unit, result)
            
            st.markdown('</div>', unsafe_allow_html=True)

    def render(self):
        st.markdown("""
            <style>
            /* Hide Streamlit elements */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* Global theme */
            .stApp {
                background-color: #1E1E1E !important;
            }
            
            /* Main header */
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
            
            /* Containers */
            .converter-container, .chat-container {
                background: #1E1E1E;
                padding: clamp(1rem, 3vw, 2rem);
                border-radius: 12px;
                border: 2px solid #FF6B00;
                margin-bottom: 1rem;
                width: 100%;
            }
            
            /* Voice button */
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
            
            /* Convert button */
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
            
            /* Text and inputs */
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
            
            /* Chat elements */
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
            
            /* Responsive layout */
            @media (max-width: 768px) {
                .main .block-container {
                    padding: 1rem;
                }
                
                [data-testid="column"] {
                    width: 100% !important;
                    flex: 1 1 auto !important;
                    min-width: 100% !important;
                }
                
                .stButton > button {
                    margin-top: 1rem;
                }
                
                .result-container {
                    margin-top: 1rem;
                }
                
                .chat-container {
                    margin-top: 1rem;
                }
            }
            
            /* Extra small screens */
            @media (max-width: 480px) {
                .main-header {
                    padding: 1rem;
                    margin-bottom: 1rem;
                }
                
                .converter-container, .chat-container {
                    padding: 0.8rem;
                }
                
                h3 {
                    margin-bottom: 0.5rem;
                }
            }
            </style>
        """, unsafe_allow_html=True)

        # Main Header
        st.markdown("<h1 class='main-header'>🈲 Unit Converter</h1>", unsafe_allow_html=True)

        # Main content columns with responsive layout
        left_col, right_col = st.columns([1, 1], gap="large")

        with left_col:
            st.markdown("<div class='converter-container'>", unsafe_allow_html=True)
            
            # Category Selection
            st.markdown("### 📊 Select Category")
            category = self.ui.render_category_selector()

            # Unit Selection
            st.markdown("### 🈴 Choose Units")
            col1, col2 = st.columns(2)
            with col1:
                from_unit = st.selectbox("From", self.categories[category]["units"])
            with col2:
                to_unit = st.selectbox("To", self.categories[category]["units"])

            # Value Input
            st.markdown("### 📝 Enter Value")
            value = st.number_input("", value=1.0, format="%f", step=0.1)

            # Convert Button with original styling
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

            .convert-button:active {
                transform: translateY(0);
            }

            .result-container {
                text-align: center;
                padding: 1rem 0;
                animation: fadeIn 0.5s ease;
            }

            .from-value {
                font-size: 1.4rem;
                color: #FFFFFF;
                font-weight: 500;
                letter-spacing: 0.5px;
            }

            .arrow {
                font-size: 1.6rem;
                color: #FF6B00;
                margin: 0.8rem 0;
                font-weight: bold;
            }

            .to-value {
                font-size: 2.2rem;
                color: #FF6B00;
                font-weight: 700;
                letter-spacing: 1px;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            </style>
            """, unsafe_allow_html=True)

            if st.markdown('<button class="convert-button">Convert ➜</button>', unsafe_allow_html=True):
                with st.spinner("Converting..."):
                    result = self.convert(value, from_unit, to_unit, category)
                    if result is not None:
                        st.markdown(f"""
                        <div class="result-container">
                            <div class="from-value">
                                {value} {from_unit}
                            </div>
                            <div class="arrow">
                                ↓
                            </div>
                            <div class="to-value">
                                {result:.4f} {to_unit}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

        with right_col:
            st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
            st.markdown("### 💬 Ask Me Anything")
            st.markdown("""
            - How to convert units
            - Explain measurement systems
            - Get conversion help
            - Usage examples
            """)

            # Chat interface with voice button
            chat_col, voice_col = st.columns([8, 1])
            with chat_col:
                prompt = st.chat_input("Ask about units or say...")
            with voice_col:
                self.voice.render_voice_button()

            # Handle voice input if present
            if 'voice_input' in st.session_state:
                prompt = st.session_state.voice_input
                del st.session_state.voice_input

            if prompt:
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        # Check if it's a conversion request
                        if prompt.lower().startswith('convert'):
                            try:
                                value, from_unit, to_unit = self.voice.parse_conversion_request(prompt.lower())
                                if all([value, from_unit, to_unit]):
                                    # Find category
                                    category = None
                                    for cat, data in self.categories.items():
                                        if from_unit in [u.lower() for u in data["units"]] and \
                                           to_unit in [u.lower() for u in data["units"]]:
                                            category = cat
                                            break
                                    
                                    if category:
                                        result = self.convert(value, from_unit, to_unit, category)
                                        if result is not None:
                                            st.markdown(f"{value} {from_unit} = {result:.4f} {to_unit}")
                                        else:
                                            st.error("Conversion failed. Please try again.")
                                    else:
                                        st.error("Could not determine the conversion category.")
                                else:
                                    response = self.chat.get_response(prompt)
                                    st.markdown(response)
                            except Exception as e:
                                response = self.chat.get_response(prompt)
                                st.markdown(response)
                        else:
                            response = self.chat.get_response(prompt)
                            st.markdown(response)

            for message in st.session_state.get('messages', []):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            st.markdown("</div>", unsafe_allow_html=True) 

            