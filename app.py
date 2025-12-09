import streamlit as st
import google.generativeai as genai

# Page config
st.set_page_config(page_title="AI Proofreader", page_icon="✍️", layout="centered")

# Title
st.title("✍️ AI Proofreader Chat")

# Sidebar for API key
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    st.markdown("[Get your API key here](https://aistudio.google.com/app/apikey)")
    
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = []
        st.session_state.waiting_for_correction = False
        st.rerun()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "waiting_for_correction" not in st.session_state:
    st.session_state.waiting_for_correction = False

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
if api_key and len(st.session_state.messages) == 0:
    st.markdown("""
    <div style='text-align: left; padding: 50px 20px;'>
        <h3>  Welcome to AI Proofreader!</h3>
        <p style='color: #888;'>Paste your text in the chat box below to get started.</p>
        <p style='color: #888;'>I'll find mistakes and help you fix them!</p>
    </div>
    """, unsafe_allow_html=True)

# Chat input
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    # Get user input
    user_input = st.chat_input("Paste your text here to proofread...")
    
    if user_input and not st.session_state.waiting_for_correction:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Show user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get AI feedback
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                prompt = f"""Analyze this text for grammar, spelling, and verb tense errors, do not try to change the tone etc. Proofreading is the job of yours.

Format your response EXACTLY like this - each mistake on its own line with a line break between them:

**Mistakes Found:**

1. "mistake" → "correction" (one line reason atleast)

2. "mistake" → "correction" (one line reason atleast)

Keep each mistake on ONE line. Use numbered list. Be brief.

Text: {user_input}"""
                
                response = model.generate_content(prompt)
                ai_response = response.text + "\n\n---\n\n**Would you like me to generate an error-free version of your text?**"
                st.markdown(ai_response)
        
        # Store AI message
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        st.session_state.waiting_for_correction = True
        st.session_state.original_text = user_input
        st.rerun()
    
    elif user_input and st.session_state.waiting_for_correction:
        # User responds to correction offer
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Check if user wants correction
        user_lower = user_input.lower()
        if any(word in user_lower for word in ["yes", "yeah", "sure", "ok", "okay", "yep", "please"]):
            with st.chat_message("assistant"):
                with st.spinner("Generating corrected version..."):
                    correction_prompt = f"""Provide ONLY the corrected version of this text and a short explanation of what did you change and why, with a bold explanation label, just the clean corrected text.

Original: {st.session_state.original_text}"""
                    
                    correction = model.generate_content(correction_prompt)
                    corrected_text = f"**Here's your error-free version:**\n\n{correction.text}"
                    st.markdown(corrected_text)
            
            st.session_state.messages.append({"role": "assistant", "content": corrected_text})
            st.session_state.waiting_for_correction = False
            st.rerun()
        else:
            # User doesn't want correction
            with st.chat_message("assistant"):
                response_text = "No problem! Feel free to paste new text whenever you're ready. 😊"
                st.markdown(response_text)
            
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            st.session_state.waiting_for_correction = False
            st.rerun()

else:
    st.info("👈 Please enter your Gemini API key in the sidebar to start chatting!")
    st.markdown("""
    **How it works:**
    1. Enter your API key in the sidebar
    2. Paste text in the chat box
    3. AI will find mistakes (briefly!)
    4. AI asks if you want the corrected version
    5. Reply "yes" or "no"
    """)