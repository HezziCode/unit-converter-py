# Main API configuration file that handles Gemini API setup and sidebar UI

import os
from dotenv import load_dotenv
import streamlit as st
import cohere
import datetime
import pytz

def setup_sidebar():
    """Setup the About Us sidebar with developer information"""
    with st.sidebar:
        st.title("ℹ️ About Us")
        
        # API Usage Meter
        if 'api_calls' not in st.session_state:
            st.session_state.api_calls = 0
            
        # Calculate percentage (assuming 60 calls per day limit)
        daily_limit = 60
        usage_percent = (st.session_state.api_calls / daily_limit) * 100
        
        # Show API Usage with progress bar
        st.markdown("### 📊 API Usage Today")
        progress_color = "green"
        if usage_percent > 80:
            progress_color = "red"
            st.warning("⚠️ API limit almost reached!")
        elif usage_percent > 60:
            progress_color = "orange"
            
        st.progress(usage_percent / 100, text=f"{usage_percent:.1f}%")
        
        if usage_percent >= 100:
            st.error("🚫 API limit reached for today! Try again tomorrow.")
            # Show countdown to reset (assuming PT midnight)
            pt = pytz.timezone('US/Pacific')
            now = datetime.datetime.now(pt)
            reset = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
            time_left = reset - now
            st.info(f"⏰ Resets in: {time_left.seconds//3600}h {(time_left.seconds//60)%60}m")
        
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
            raise ValueError("Cohere API key not found")
            
        # Initialize Cohere client
        co = cohere.Client(api_key)
        
        # Test the connection
        co.generate(prompt="Test", max_tokens=1)
        
        setup_sidebar()  # Setup the About Us sidebar
        return co
        
    except Exception as e:
        st.error(f"Failed to initialize Cohere: {str(e)}")
        return None 