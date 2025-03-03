import os
from dotenv import load_dotenv
import streamlit as st
import cohere

def get_api_key():
    load_dotenv()
    api_key = os.getenv('COHERE_API_KEY')
    if not api_key:
        st.error("CoHERE API key not found in .env file!")
    return api_key

def setup_sidebar():
    with st.sidebar:
        st.title("ℹ️ About Us")
        if st.session_state.get('api_calls', 0) > 0:
            daily_limit = 60
            usage_percent = (st.session_state.api_calls / daily_limit) * 100
            st.markdown("### 📊 API Usage Today")
            if usage_percent > 80:
                st.warning("⚠️ API limit almost reached!")
            st.progress(min(usage_percent / 100, 1.0), text=f"{usage_percent:.1f}%")
        st.markdown("""
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
    try:
        api_key = get_api_key()
        if not api_key:
            return None
        co = cohere.Client(api_key)
        st.session_state['cohere_client'] = co
        setup_sidebar()
        return co
    except Exception as e:
        st.error(f"Error setting up CoHERE model: {str(e)}")
        return None