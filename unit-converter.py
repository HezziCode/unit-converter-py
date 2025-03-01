# Main application file that initializes and runs the converter

import streamlit as st
from components.unit_config import UnitCategories
from components.converter import UnitConverter
from components.api_config import setup_model
import time

# Initialize session state for API call tracking
if 'api_call_count' not in st.session_state:
    st.session_state.api_call_count = 0
    st.session_state.last_call_time = time.time()

def main():
    st.set_page_config(
        page_title="Unit Converter Pro",
        page_icon="🔄",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Check if running on Streamlit Cloud
    server_address = st.get_option("browser.serverAddress")
    is_cloud = not ("localhost" in server_address or "127.0.0.1" in server_address)
    st.session_state.is_streamlit_cloud = is_cloud
    
    st.markdown("""
        <style>
        /* Global Responsive Styles */
        @media (max-width: 768px) {
            .stMarkdown h1 { font-size: 1.5rem !important; }
            .stMarkdown h2 { font-size: 1.3rem !important; }
            .stMarkdown h3 { font-size: 1.1rem !important; }
            
            .element-container, .stButton, .stSelectbox {
                width: 100% !important;
            }
            
            .block-container {
                padding: 1rem !important;
            }
            
            [data-testid="column"] {
                width: 100% !important;
                margin-bottom: 1rem;
            }
        }
        
        .stNumberInput input, .stSelectbox select {
            min-height: 40px;
            border-radius: 8px !important;
        }
        
        .stButton button {
            width: 100%;
            height: 40px;
            border-radius: 8px !important;
            transition: all 0.3s ease;
        }
        
        .stChatMessage {
            max-width: 90% !important;
            margin: 0.5rem 0;
        }
        
        .css-1d391kg {
            width: 100% !important;
            max-width: 300px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize model
    model = setup_model()
    
    if model:
        # Initialize and render converter
        converter = UnitConverter(model)
        converter.render()

    # Simplified message for non-HTTPS connections
    if is_cloud and not server_address.startswith("https"):
        st.info("⚠️ For full functionality, please use the secure (HTTPS) URL.")

if __name__ == "__main__":
    main()

