# Main application file that initializes and runs the converter

import streamlit as st
from components.api_config import setup_gemini
from components.converter import UnitConverter
import time

# Initialize session state for API call tracking
if 'api_call_count' not in st.session_state:
    st.session_state.api_call_count = 0
    st.session_state.last_call_time = time.time()

def handle_conversion(model, prompt):
    """Handle conversion requests with rate limiting"""
    try:
        # Check and update rate limits
        current_time = time.time()
        if current_time - st.session_state.last_call_time > 60:
            st.session_state.api_call_count = 0
        
        # Enforce rate limits
        if st.session_state.api_call_count >= 10:
            time_to_wait = 60 - (current_time - st.session_state.last_call_time)
            if time_to_wait > 0:
                st.warning(f"Please wait {int(time_to_wait)} seconds before making more conversions")
                return None
            
        # Make API request
        response = model.generate_content(prompt)
        
        # Update API call tracking
        st.session_state.api_call_count += 1
        st.session_state.last_call_time = current_time
        
        return response.text
        
    except Exception as e:
        # Handle API errors
        if "429" in str(e):
            st.warning("Taking a quick break to ensure smooth service.")
        else:
            st.error("Something went wrong. Please try again.")
        return None

def main():
    """Main application entry point"""
    try:
        # Initialize components
        model = setup_gemini()
        converter = UnitConverter(model)
        converter.render()
        
    except Exception as e:
        st.error("An error occurred. Please try again later.")
        st.info("⏳ Taking a quick break to refresh...")

if __name__ == "__main__":
    main() 