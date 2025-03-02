def render_voice_button(self):
    st.markdown("""
        <style>
        .stButton > button {
            width: 38px !important;
            height: 38px !important;
            border-radius: 50% !important;
            border: 2px solid #FF6B00 !important;
            background: transparent !important;
            padding: 0 !important;
            margin-top: -5px !important; /* Adjust this value to align with chat input */
            transition: all 0.3s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 18px !important;
            color: #FF6B00 !important;
            line-height: 38px !important;
            vertical-align: middle !important;
        }
        .stButton > button:hover {
            background: rgba(255, 107, 0, 0.1) !important;
        }
        .stTextInput > div > div > input {
            margin-right: 50px !important; /* Adjust this value to make space for the button */
        }
        </style>
    """, unsafe_allow_html=True)
    
    if st.button("⏺", key="voice_button", help="Click to speak"):
        text = self.listen_and_transcribe()
        if text:
            st.write(f"Debug: Voice input saved - {text}")
            self.process_voice_input(text)
