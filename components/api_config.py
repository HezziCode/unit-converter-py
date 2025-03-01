# Main API configuration file that handles Gemini API setup and sidebar UI

import os
from dotenv import load_dotenv
import streamlit as st
import cohere
import datetime
import pytz

# Load environment variables
load_dotenv()

# Get API key from environment
COHERE_API_KEY = os.getenv('COHERE_API_KEY')

def get_api_key():
    """Return the API key"""
    return COHERE_API_KEY

def setup_sidebar():
    """Setup the About Us sidebar with developer information"""
    with st.sidebar:
        st.title("ℹ️ About Us")
        
        # Only show API usage if we're actually using the API
        if st.session_state.get('api_calls', 0) > 0:
            # API Usage Meter
            if 'api_calls' not in st.session_state:
                st.session_state.api_calls = 0
                
            # Calculate percentage (assuming 60 calls per day limit)
            daily_limit = 60
            usage_percent = (st.session_state.api_calls / daily_limit) * 100
            
            # Show API Usage with progress bar
            st.markdown("### 📊 API Usage Today")
            if usage_percent > 80:
                st.warning("⚠️ API limit almost reached!")
            st.progress(usage_percent / 100, text=f"{usage_percent:.1f}%")
        
        # Rest of the sidebar content
        st.markdown("""
        ### 🎯 Our Mission
        Making unit conversions simple, fast, and accessible for everyone.
        
        ### 👨‍💻 Developer
        Muhammad Huzaifa
        💻 Full Stack Developer | 🤖 AI Developer
        
        ### 🌟 Features
        ✅ Multiple unit conversions
        🎙️ Voice command support
        🤖 AI-powered chatbot
        
        ### 📞 Contact
        🔗 [LinkedIn](http://linkedin.com/in/muhammad-huzaifa-9102282b7/) | [GitHub](https://github.com/HezziCode) | [Agentia website](http://agentic-ai-hezzi.vercel.app/)
        
        ---
        ### © 2025 Unit Converter Pro
        *Convert Smarter, Not Harder!*
        """)

def setup_model():
    """Initialize Cohere model"""
    try:
        load_dotenv()
        api_key = os.getenv('COHERE_API_KEY')
        
        if not api_key:
            # Return silently without error message
            return None
            
        # Initialize Cohere client without any test calls
        co = cohere.Client(api_key)
        
        setup_sidebar()  # Setup the About Us sidebar
        return co
        
    except Exception as e:
        # Silently handle any errors without showing messages
        return None 