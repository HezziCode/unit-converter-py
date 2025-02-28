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
        system_prompt = """You are a friendly and helpful AI assistant who specializes in unit conversions and measurements. 
        When asked about units or conversions, provide accurate technical information. 
        For general conversation, respond naturally while occasionally relating to measurement concepts when relevant."""
        
        full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
        
        # Add retry logic for rate limits
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.model.generate(
                    prompt=full_prompt,
                    max_tokens=150,
                    temperature=0.7,
                    return_likelihoods='NONE'
                )
                response_text = response.generations[0].text
                
                # Update API call counter
                if 'api_calls' in st.session_state:
                    st.session_state.api_calls += 1
                
                # Cache the response for future use
                st.session_state.response_cache[prompt] = response_text
                return response_text
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    with st.spinner(f"Rate limit hit. Waiting {wait_time} seconds..."):
                        time.sleep(wait_time)
                    continue
                return "I apologize, but I encountered an error. Please try again."

    def render(self):
        """Render the chat interface"""
        st.markdown("""
            <style>
            /* Chat specific styles */
            .chat-container {
                max-width: 800px;
                margin: 0 auto;
            }
            
            .chat-message {
                padding: 0.8rem;
                margin: 0.5rem 0;
                border-radius: 12px;
                word-wrap: break-word;
            }
            
            .user-message {
                background: #e3f2fd;
                margin-left: 1rem;
                margin-right: 0;
            }
            
            .assistant-message {
                background: #f5f5f5;
                margin-right: 1rem;
                margin-left: 0;
            }
            
            @media (max-width: 768px) {
                .chat-message {
                    margin: 0.5rem;
                    font-size: 0.9rem;
                }
                
                .chat-input {
                    padding: 0.5rem;
                }
            }
            </style>
        """, unsafe_allow_html=True)
        
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