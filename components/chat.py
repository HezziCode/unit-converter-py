# Chat interface component that handles conversation with the AI

import streamlit as st
import time

class ChatInterface:
    """Handles chat functionality and conversation management"""
    def __init__(self, model):
        # Initialize chat with AI model
        self.model = model
        # Initialize chat history in session state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "response_cache" not in st.session_state:
            st.session_state.response_cache = {}

    def get_response(self, prompt):
        """Get AI response for user input with caching"""
        # Check cache first to avoid duplicate API calls
        if prompt in st.session_state.response_cache:
            return st.session_state.response_cache[prompt]

        # Enhanced context for better AI responses
        system_prompt = """You are a friendly and helpful AI assistant who specializes in unit conversions and measurements, 
        but can also engage in natural conversation. When asked about units or conversions, provide accurate technical information. 
        For general conversation, respond naturally while occasionally relating to measurement concepts when relevant."""
        
        full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
        
        # Add retry logic for rate limits
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(full_prompt)
                response_text = response.text
                # Cache the response for future use
                st.session_state.response_cache[prompt] = response_text
                return response_text
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    wait_time = int((attempt + 1) * 5)
                    with st.spinner(f"Rate limit hit. Waiting {wait_time} seconds..."):
                        time.sleep(wait_time)
                    continue
                return f"I apologize, but I encountered an error. Please try again in a moment."

    def render(self):
        """Render the chat interface"""
        st.subheader("Chat with Unit Conversion Expert")
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input handler
        if prompt := st.chat_input("Ask anything about units, conversions, or just chat!"):
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get and display AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = self.get_response(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response}) 