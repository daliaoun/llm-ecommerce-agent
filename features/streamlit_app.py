import streamlit as st
import time
from agent import agent_executor

# Page Configuration
st.set_page_config(
    page_title="AI E-commerce Assistant", 
    page_icon="💻", 
    layout="wide"
)

# Custom CSS for improved styling
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 20px;
    }
    .chat-message {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .user-message {
        background-color: #E6F3FF;
        border-left: 4px solid #3498DB;
    }
    .assistant-message {
        background-color: #F0F4F8;
        border-left: 4px solid #2ECC71;
    }
    .stTextInput > div > div > input {
        background-color: #F8F9FA;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 10px;
    }
    .sidebar-info {
        margin-top: 2000000px; /* Adjust the value as needed */
    }
    </style>
    """, unsafe_allow_html=True)



# Page Title with Custom Styling
st.markdown('<h1 class="main-title">💻 Electronic E-commerce Shopping Assistant</h1>', unsafe_allow_html=True)

 #WelcomeBanner
st.markdown("""<div style="background-color: #f0f7ff; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; border-left: 4px solid #3498DB;"><h3 style="margin: 0; color: #2C3E50;">Welcome to Your Electronics Recommendation Hub!</h3><p style="margin: 0.5rem 0 0 0;">"Welcome to your personal shopping assistant! This chatbot helps you explore and find products from our e-commerce store by answering your questions about available items. Whether you're looking for smartphones, laptops, or any other category, it provides detailed information like prices, stock, and features. For <b>smartphones</b> and <b>laptops</b>, it also includes detailed specifications to help you make an informed choice.</p></div>""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "response_in_progress" not in st.session_state:
    st.session_state.response_in_progress = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to generate response
def generate_agent_response(user_input):
    try:
        result = agent_executor.invoke({
            "input": user_input, 
            "chat_history": st.session_state.chat_history
        })

        return (result.get("output", "I couldn't generate a response.") 
                if isinstance(result, dict) else 
                result if isinstance(result, str) else 
                "I encountered an error generating a response.")
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Main Chat Interface
def main_chat_interface():
    # Display existing messages
    for message in st.session_state.messages:
        css_class = "user-message" if message["role"] == "user" else "assistant-message"
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
            st.markdown(f'<div class="chat-message {css_class}">{message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    if not st.session_state.response_in_progress:
        user_input = st.chat_input("What can I help you with today?")
        if user_input:
            # Display user message immediately
            with st.chat_message("user", avatar="👤"):
                st.markdown(f'<div class="chat-message user-message">{user_input}</div>', unsafe_allow_html=True)
            
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "human", "content": user_input})
            st.session_state.response_in_progress = True
            
            # Generate and display assistant response
            with st.chat_message("assistant", avatar="🤖"):
                # Indicate processing phase
                with st.spinner("Processing your request..."):
                    response_text = generate_agent_response(user_input)
                
                # Stop spinner and start rendering response
                message_placeholder = st.empty()
                full_response = ""
                if response_text.count("\n")>1:
                    for chunk in response_text.split("\n"):
                        full_response += chunk + "\n"
                        time.sleep(0.4)
                        message_placeholder.markdown(
                            f'<div class="chat-message assistant-message">{full_response}▌</div>', 
                            unsafe_allow_html=True
                        )
                elif response_text.count("\n")==0:
                    for chunk in response_text.split():
                        full_response += chunk + " "
                        time.sleep(0.05)
                        message_placeholder.markdown(
                            f'<div class="chat-message assistant-message">{full_response}▌</div>', 
                            unsafe_allow_html=True
                        )
                elif response_text.count("\n")==1:
                    
                    for chunk in response_text.split("\n"):
                        full_response += chunk + " "
                        time.sleep(0.05)
                        message_placeholder.markdown(
                            f'<div class="chat-message assistant-message">{full_response}▌</div>', 
                            unsafe_allow_html=True
                        )                    
                # Finalize response
                message_placeholder.markdown(
                    f'<div class="chat-message assistant-message">{full_response}</div>', 
                    unsafe_allow_html=True
                )
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.chat_history.append({"role": "ai", "content": full_response})
            
            st.session_state.response_in_progress = False
    else:
        st.chat_input("Processing response, please wait...", disabled=True)

# Sidebar with Conversation History and Quick Actions
def sidebar_interface():
    with st.sidebar:
        col1, col2 = st.columns(2)

        # Display the images in each column
        with col1:
            st.image("Umanlink-Group-Logo-Header.png", width=100)

        with col2:
            st.image("gsm_arena-removebg-preview.png", width=300)

        with st.sidebar.expander("Conversation History"):
        
            if st.session_state.chat_history:
                user_inputs = [entry['content'] for entry in st.session_state.chat_history if entry["role"] == "human"]
                for i, user_input in enumerate(user_inputs, start=1):
                    st.markdown(f"**{i}.** {user_input}")
            else:
                st.write("No recent conversations")

        st.sidebar.info("""

      This assistant can help you with:
    - Product Suggestions
    - Order Status & Management
    - Frequently Asked Questions (FAQs)
    """)



# Main App Flow
def main():
    
    main_chat_interface()
    sidebar_interface()

if __name__ == "__main__":
    main()