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
    
    st.markdown("""
        <style>
        /* Global Responsive Styles */
        @media (max-width: 768px) {
            /* Smaller text on mobile */
            .stMarkdown h1 { font-size: 1.5rem !important; }
            .stMarkdown h2 { font-size: 1.3rem !important; }
            .stMarkdown h3 { font-size: 1.1rem !important; }
            
            /* Full width containers */
            .element-container, .stButton, .stSelectbox {
                width: 100% !important;
            }
            
            /* Better spacing */
            .block-container {
                padding: 1rem !important;
            }
            
            /* Stack columns on mobile */
            [data-testid="column"] {
                width: 100% !important;
                margin-bottom: 1rem;
            }
        }
        
        /* Better input fields */
        .stNumberInput input, .stSelectbox select {
            min-height: 40px;
            border-radius: 8px !important;
        }
        
        /* Improved buttons */
        .stButton button {
            width: 100%;
            height: 40px;
            border-radius: 8px !important;
            transition: all 0.3s ease;
        }
        
        /* Chat improvements */
        .stChatMessage {
            max-width: 90% !important;
            margin: 0.5rem 0;
        }
        
        /* Sidebar improvements */
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

if __name__ == "__main__":
    main() 