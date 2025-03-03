import streamlit as st
from .api_config import get_api_key

class ChatInterface:
    def __init__(self, model):
        self.model = model
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "response_cache" not in st.session_state:
            st.session_state.response_cache = {}

    def get_response(self, prompt):
        """Get AI response for user input, only responds the first time"""
        # Check if prompt has been processed before
        if prompt.lower() in st.session_state.response_cache:
            return None
        
        try:
            system_prompt = """You are a friendly and helpful AI assistant who specializes in unit conversions and measurements. 
            When asked about units or conversions, provide accurate technical information. 
            For general conversation, respond naturally while occasionally relating to measurement concepts when relevant."""
            
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
            
            response = self.model.chat(
                model='command',
                message=full_prompt,
                temperature=0.7
            )
            
            response_text = response.text.strip()
            
            # Mark prompt as processed in cache (case-insensitive)
            st.session_state.response_cache[prompt.lower()] = True
            if 'api_calls' in st.session_state:
                st.session_state.api_calls += 1
            return response_text
            
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return "I'm having temporary connection issues. Please try again!"

    def render(self):
        st.markdown("""
            <style>
            .chat-container {max-width: 800px; margin: 0 auto;}
            .chat-message {padding: 0.8rem; margin: 0.5rem 0; border-radius: 12px; word-wrap: break-word;}
            .user-message {background: #e3f2fd; margin-left: 1rem; margin-right: 0;}
            .assistant-message {background: #f5f5f5; margin-right: 1rem; margin-left: 0;}
            @media (max-width: 768px) {
                .chat-message {margin: 0.5rem; font-size: 0.9rem;}
                .chat-input {padding: 0.5rem;}
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.subheader("Chat with Unit Conversion Expert")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask anything about units, conversions, or just chat!"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = self.get_response(prompt)
                    if response:
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})