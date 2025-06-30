import streamlit as st
import time
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="AI Chat - AccuBid Converter",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS (reusing from AceBot design)
st.markdown("""
<style>
    .chat-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .user-message {
        background: #007bff;
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
        text-align: right;
    }
    
    .assistant-message {
        background: #f8f9fa;
        color: #333;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border-left: 4px solid #1f4e79;
    }
    
    .chat-input {
        position: sticky;
        bottom: 0;
        background: white;
        padding: 1rem;
        border-top: 1px solid #dee2e6;
    }
    
    .thread-item {
        background: #f8f9fa;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        cursor: pointer;
        border-left: 3px solid #1f4e79;
    }
    
    .thread-item:hover {
        background: #e9ecef;
    }
    
    .active-thread {
        background: #e3f2fd !important;
        border-left-color: #007bff !important;
    }
    
    .tool-calling {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'current_thread_id' not in st.session_state:
    st.session_state.current_thread_id = None
if 'current_thread_name' not in st.session_state:
    st.session_state.current_thread_name = None
if 'threads' not in st.session_state:
    st.session_state.threads = {}
if 'selected_files' not in st.session_state:
    st.session_state.selected_files = []

# Page Header
st.title("🤖 AI Chat Assistant")
st.caption("Chat with your AccuBid documents using advanced AI")

# Sidebar for thread management and file selection
with st.sidebar:
    st.header("💬 Chat Management")
    
    # Thread Management Section
    st.subheader("Conversation Threads")
    new_thread_name = st.text_input("New Thread Name (optional)", placeholder="e.g., Project ABC Discussion")
    
    if st.button("➕ Create New Thread", use_container_width=True):
        thread_id = f"thread_{len(st.session_state.threads) + 1}_{int(time.time())}"
        thread_name = new_thread_name if new_thread_name else f"Thread {len(st.session_state.threads) + 1}"
        
        st.session_state.threads[thread_id] = {
            'name': thread_name,
            'created_at': datetime.now(),
            'message_count': 0
        }
        st.session_state.current_thread_id = thread_id
        st.session_state.current_thread_name = thread_name
        st.session_state.chat_messages = []
        st.success(f"Created thread: {thread_name}")
        st.rerun()
    
    # Display existing threads
    if st.session_state.threads:
        st.markdown("**Active Threads:**")
        for thread_id, thread_data in st.session_state.threads.items():
            is_active = thread_id == st.session_state.current_thread_id
            css_class = "thread-item active-thread" if is_active else "thread-item"
            
            if st.button(
                f"💬 {thread_data['name']} ({thread_data['message_count']} messages)",
                key=f"thread_{thread_id}",
                use_container_width=True
            ):
                st.session_state.current_thread_id = thread_id
                st.session_state.current_thread_name = thread_data['name']
                # In real implementation, would load messages for this thread
                st.session_state.chat_messages = []
                st.rerun()
    
    # File Context Selection
    st.markdown("---")
    st.subheader("📁 File Context")
    st.info("Select which files to reference in your conversation")
    
    # Mock file selection (would be populated from uploaded files)
    available_files = [
        "Project_A_AccuBid.xlsx",
        "Commercial_Estimate_B.xlsx", 
        "Residential_Quote_C.csv"
    ]
    
    selected_files = st.multiselect(
        "Choose files to reference:",
        available_files,
        default=st.session_state.selected_files,
        help="AI will have context from these files"
    )
    st.session_state.selected_files = selected_files
    
    # Chat Settings
    st.markdown("---")
    st.subheader("⚙️ Chat Settings")
    
    temperature = st.slider("AI Creativity", 0.0, 1.0, 0.7, 0.1)
    max_tokens = st.slider("Response Length", 100, 2000, 500, 100)
    
    # Prompt Templates
    st.markdown("---")
    st.subheader("📝 Quick Prompts")
    
    prompt_templates = [
        "Summarize the key electrical components in this project",
        "What's the total estimated cost breakdown?",
        "Identify any potential cost-saving opportunities",
        "Generate a client-friendly project overview",
        "List all materials with quantities",
        "Create a project timeline estimate"
    ]
    
    for template in prompt_templates:
        if st.button(f"💡 {template[:30]}...", use_container_width=True, key=f"prompt_{template[:20]}"):
            st.session_state.chat_messages.append({
                "role": "user",
                "content": template,
                "timestamp": datetime.now()
            })
            st.rerun()

# Main chat area
if st.session_state.current_thread_id:
    st.markdown(f"**Current Thread:** {st.session_state.current_thread_name}")
    
    # File context indicator
    if st.session_state.selected_files:
        st.info(f"📁 Context: {', '.join(st.session_state.selected_files)}")
    else:
        st.warning("⚠️ No files selected for context. Choose files in the sidebar for better responses.")
    
    # Chat messages display
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong>You:</strong><br>
                    {message["content"]}
                    <br><small>{message["timestamp"].strftime("%H:%M:%S")}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-message">
                    <strong>🤖 AI Assistant:</strong><br>
                    {message["content"]}
                    <br><small>{message["timestamp"].strftime("%H:%M:%S")}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_area(
            "Type your message:",
            placeholder="Ask about your AccuBid files, request document formatting, or get project insights...",
            height=100,
            key="chat_input"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button("📤 Send", use_container_width=True, type="primary"):
            if user_input.strip():
                # Add user message
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now()
                })
                
                # Simulate AI response
                with st.spinner("🤖 AI is thinking..."):
                    time.sleep(2)  # Simulate processing time
                    
                    # Mock AI response based on input
                    if "cost" in user_input.lower():
                        ai_response = "Based on your AccuBid file, I can see the total project cost is $45,230. This includes $28,500 for materials, $12,800 for labor, and $3,930 for overhead. Would you like me to break this down by electrical systems?"
                    elif "summary" in user_input.lower():
                        ai_response = "This is a commercial electrical project with 3 main systems: Lighting (40%), Power Distribution (35%), and Security/Communications (25%). The project spans 15,000 sq ft with an estimated 120 hours of labor required."
                    else:
                        ai_response = f"I understand you're asking about: '{user_input}'. In a fully implemented system, I would analyze your selected AccuBid files and provide detailed insights. This response would be generated using the selected files as context."
                    
                    # Add AI response
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": ai_response,
                        "timestamp": datetime.now()
                    })
                    
                    # Update thread message count
                    if st.session_state.current_thread_id in st.session_state.threads:
                        st.session_state.threads[st.session_state.current_thread_id]['message_count'] += 2
                
                st.rerun()
        
        if st.button("🔧 Tools", use_container_width=True):
            st.info("Tool calling features (email, calendar, export) will be implemented in backend phase")
    
    # Export conversation
    st.markdown("---")
    col_export1, col_export2, col_export3 = st.columns(3)
    
    with col_export1:
        if st.button("📄 Export as Word", use_container_width=True):
            st.success("Conversation export feature will be implemented in backend phase")
    
    with col_export2:
        if st.button("📧 Email Conversation", use_container_width=True):
            st.success("Email export feature will be implemented in backend phase")
    
    with col_export3:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

else:
    # No thread selected
    st.info("👈 Create or select a conversation thread from the sidebar to start chatting")
    
    # Welcome message
    st.markdown("""
    ## Welcome to AI Chat Assistant! 🤖
    
    This intelligent chat interface allows you to:
    
    - **📁 Analyze AccuBid Files:** Upload your files on the main page, then reference them here
    - **💬 Multi-threaded Conversations:** Organize different projects or topics in separate threads  
    - **🔧 Smart Tools:** Access email, calendar, and export functions through AI commands
    - **📝 Quick Prompts:** Use pre-built templates for common electrical estimation questions
    - **🎯 Context-Aware:** AI understands your specific project files and provides relevant insights
    
    ### Getting Started:
    1. Create a new thread or select an existing one
    2. Choose which AccuBid files to reference (sidebar)
    3. Start asking questions about your projects!
    
    ### Example Questions:
    - "What's the total material cost for this commercial project?"
    - "Create a client presentation summary"
    - "Email the cost breakdown to the project manager"
    - "Schedule a review meeting for next Tuesday"
    """)
    
    # Quick start button
    if st.button("🚀 Create Your First Thread", type="primary", use_container_width=True):
        thread_id = f"thread_1_{int(time.time())}"
        thread_name = "My First Conversation"
        
        st.session_state.threads[thread_id] = {
            'name': thread_name,
            'created_at': datetime.now(),
            'message_count': 0
        }
        st.session_state.current_thread_id = thread_id
        st.session_state.current_thread_name = thread_name
        st.session_state.chat_messages = []
        st.rerun()
