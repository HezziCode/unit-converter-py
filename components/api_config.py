# Main API configuration file that handles Gemini API setup and sidebar UI

import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st

class APIHandler:
    """Handles API requests, rate limiting, and model initialization"""
    def __init__(self):
        # Initialize API handler with configuration
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.model = None
        # Rate limiting parameters
        self.last_request_time = 0
        self.requests_in_minute = 0
        self.MAX_REQUESTS_PER_MINUTE = 10
        self.COOLDOWN_PERIOD = 60  # seconds

    def initialize_model(self):
        """Initialize the Gemini model with API key"""
        if not self.api_key:
            st.error("API key not found. Please check your .env file")
            return False

        try:
            # Configure and select appropriate model
            genai.configure(api_key=self.api_key)
            models = genai.list_models()
            
            for m in models:
                # Try to use experimental model first
                if 'gemini-2.0-pro-exp' in m.name:
                    self.model = genai.GenerativeModel(m.name)
                    return True
                    
            # Fallback to stable model if experimental not found
            st.warning("Preferred model not found, using alternative model")
            self.model = genai.GenerativeModel('gemini-pro')
            return True

        except Exception as e:
            st.error(f"Model initialization error: {str(e)}")
            return False

    def can_make_request(self):
        """Check if we can make a request based on rate limits"""
        current_time = time.time()
        
        # Reset counter if cooldown period has passed
        if current_time - self.last_request_time >= self.COOLDOWN_PERIOD:
            self.requests_in_minute = 0
            self.last_request_time = current_time
            return True
            
        # Check if within rate limits
        if self.requests_in_minute < self.MAX_REQUESTS_PER_MINUTE:
            return True
            
        return False

    def make_request(self, prompt):
        """Make an API request with rate limiting and error handling"""
        if not self.model:
            if not self.initialize_model():
                return None

        # Check rate limits before making request
        if not self.can_make_request():
            remaining_time = int(self.COOLDOWN_PERIOD - (time.time() - self.last_request_time))
            st.warning(f"Please wait {remaining_time} seconds before making another request")
            return None

        try:
            # Make the API request
            self.requests_in_minute += 1
            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            # Handle rate limiting and other errors
            if "429" in str(e):
                st.warning("Rate limit reached. Taking a short break...")
                time.sleep(2)
            else:
                st.error(f"Error: {str(e)}")
            return None

# Create a singleton instance for global use
api_handler = APIHandler()

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
            import datetime
            import pytz
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

def setup_gemini():
    """Initialize Gemini API and setup sidebar"""
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        raise ValueError("API key not found. Please check your .env file")
    
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # List available models and find suitable one
        models = genai.list_models()
        for m in models:
            if 'gemini-2.0-pro-exp' in m.name:  # Use experimental model
                model = genai.GenerativeModel(m.name)
                setup_sidebar()  # Setup the About Us sidebar
                return model
                
        raise ValueError("No suitable Gemini model found")
        
    except Exception as e:
        raise Exception(f"Failed to initialize Gemini: {str(e)}") 