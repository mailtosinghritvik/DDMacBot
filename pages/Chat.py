"""
DDMacBot Chat Page - Simplified Implementation

This page follows the aceofSpades minimal chat pattern with only essential features:
1. Thread management (create, select, delete)
2. File upload to vector store
3. Simple chat interface with OpenAI Assistant

Commented out features (following aceofSpades approach):
- Chat settings (temperature, max_tokens)
- Quick prompts
- Export functionality  
- Tools button
- File context selection
- Complex CSS styling
- Thread message tracking

The chat integrates with the main workflow by using the project's dedicated assistant
when available (from Home.py processing), otherwise falls back to default assistant.
"""

import streamlit as st
import os
from datetime import datetime
from openai import OpenAI
import tempfile
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="AI Chat - AccuBid Converter",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'threads' not in st.session_state:
    st.session_state.threads = {}
if 'current_thread_id' not in st.session_state:
    st.session_state.current_thread_id = None
if 'current_thread_name' not in st.session_state:
    st.session_state.current_thread_name = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Vector Store ID (same as Home.py)
VECTOR_STORE_ID = 'vs_qUspcB7VllWXM4z7aAEdIK9L'

# Create upload directory
UPLOAD_FOLDER = os.path.join(os.getcwd(), "temp")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_client():
    """Get or create OpenAI client"""
    if 'openai_client' not in st.session_state:
        try:
            st.session_state.openai_client = OpenAI(
                api_key=os.getenv('OPENAI_API_KEY'),
                max_retries=3,
                timeout=20.0
            )
        except Exception as e:
            st.error(f"Error initializing OpenAI client: {str(e)}")
            return None
    return st.session_state.openai_client

def create_thread(name=""):
    """Create a new thread with OpenAI"""
    try:
        client = get_client()
        if not client:
            return None, None
            
        # Set default name if not provided
        if not name or name.strip() == '':
            name = f"Thread {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Create thread using OpenAI API
        thread = client.beta.threads.create()
        
        # Store thread info
        st.session_state.threads[thread.id] = {
            'thread': thread,
            'name': name
        }
        
        return thread.id, name
    except Exception as e:
        st.error(f"Error creating thread: {str(e)}")
        return None, None

def delete_thread(thread_id):
    """Delete a thread"""
    try:
        if thread_id in st.session_state.threads:
            del st.session_state.threads[thread_id]
            if st.session_state.current_thread_id == thread_id:
                st.session_state.current_thread_id = None
                st.session_state.current_thread_name = None
                st.session_state.messages = []
            return True
        return False
    except Exception as e:
        st.error(f"Error deleting thread: {str(e)}")
        return False

def get_threads():
    """Get list of all threads"""
    return [
        {'id': thread_id, 'name': info['name']} 
        for thread_id, info in st.session_state.threads.items()
    ]

def process_excel_to_markdown(uploaded_file):
    """Convert Excel file to markdown for vector store upload with chunking strategy"""
    try:
        # Read Excel file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            sheet_data = {'Sheet1': df}
        else:
            xls = pd.ExcelFile(uploaded_file)
            sheet_data = {}
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                sheet_data[sheet_name] = df
        
        # Chunking strategy
        markdown_content = ""
        char_count = 0
        chunk_size = 1000
        
        def add_context_marker():
            return f"\n\n<!-- CONTEXT: File: {uploaded_file.name} | Type: {'CSV' if uploaded_file.name.endswith('.csv') else 'Excel'} | Uploaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->\n\n"
        
        # Generate header
        header = f"""# {uploaded_file.name} - Data Analysis

**Uploaded:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**File Type:** {'CSV' if uploaded_file.name.endswith('.csv') else 'Excel'}
**Total Sheets:** {len(sheet_data)}

---

"""
        
        markdown_content += header
        char_count += len(header)
        
        if char_count >= chunk_size:
            markdown_content += add_context_marker()
            char_count = 0
        
        # Process each sheet
        for sheet_name, df in sheet_data.items():
            sheet_section = f"""## {sheet_name}

### Data Summary
- **Total Rows:** {len(df)}
- **Total Columns:** {len(df.columns)}
- **Columns:** {', '.join(df.columns.tolist())}

### Data Content

"""
            markdown_content += sheet_section
            char_count += len(sheet_section)
            
            if char_count >= chunk_size:
                markdown_content += add_context_marker()
                char_count = 0
            
            # Convert DataFrame to markdown table with chunking
            try:
                df_clean = df.fillna('')
                
                if len(df_clean) <= 50:
                    # Small table - include everything
                    table_markdown = df_clean.to_markdown(index=False)
                    markdown_content += table_markdown + "\n\n"
                    char_count += len(table_markdown) + 2
                    
                    if char_count >= chunk_size:
                        markdown_content += add_context_marker()
                        char_count = 0
                else:
                    # Large table - chunk it into smaller pieces
                    chunk_rows = 25
                    total_rows = len(df_clean)
                    
                    for start_idx in range(0, total_rows, chunk_rows):
                        end_idx = min(start_idx + chunk_rows, total_rows)
                        df_chunk = df_clean.iloc[start_idx:end_idx]
                        
                        chunk_header = f"\n**Rows {start_idx + 1} to {end_idx} of {total_rows}:**\n\n"
                        markdown_content += chunk_header
                        char_count += len(chunk_header)
                        
                        chunk_markdown = df_chunk.to_markdown(index=False)
                        markdown_content += chunk_markdown + "\n\n"
                        char_count += len(chunk_markdown) + 2
                        
                        if char_count >= chunk_size or end_idx < total_rows:
                            markdown_content += add_context_marker()
                            char_count = 0
                
            except Exception as e:
                error_msg = f"*Error converting table to markdown: {str(e)}*\n\n"
                markdown_content += error_msg
                char_count += len(error_msg)
            
            # Add numeric summary if applicable
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                stats_section = f"""### {sheet_name} - Numeric Summary

"""
                for col in numeric_cols:
                    try:
                        stats = f"""**{col}:**
- Sum: {df[col].sum():,.2f}
- Average: {df[col].mean():.2f}
- Min: {df[col].min():.2f}
- Max: {df[col].max():.2f}

"""
                        stats_section += stats
                    except:
                        continue
                
                markdown_content += stats_section
                char_count += len(stats_section)
                
                if char_count >= chunk_size:
                    markdown_content += add_context_marker()
                    char_count = 0
            
            markdown_content += "---\n\n"
            char_count += 5
        
        # Add final context marker if needed
        if char_count > 0:
            markdown_content += add_context_marker()
        
        return markdown_content
        
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        return None

def process_uploaded_file(uploaded_file):
    """Handle file upload and vector store integration"""
    try:
        if uploaded_file is None:
            return False
            
        client = get_client()
        if not client:
            return False
        
        # Check if it's an Excel/CSV file that needs conversion
        if uploaded_file.name.endswith(('.xlsx', '.xls', '.csv')):
            # Convert to markdown first
            markdown_content = process_excel_to_markdown(uploaded_file)
            if not markdown_content:
                return False
            
            # Save markdown temporarily
            temp_path = os.path.join(UPLOAD_FOLDER, f"{uploaded_file.name}.md")
            with open(temp_path, "w", encoding='utf-8') as f:
                f.write(markdown_content)
            
            # Upload markdown to vector store
            with open(temp_path, "rb") as f:
                file_batch = client.vector_stores.file_batches.upload_and_poll(
                    vector_store_id=VECTOR_STORE_ID,
                    files=[f]
                )
        else:
            # Handle other file types (PDF, TXT, MD) directly
            temp_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Upload to vector store
            with open(temp_path, "rb") as f:
                file_batch = client.vector_stores.file_batches.upload_and_poll(
                    vector_store_id=VECTOR_STORE_ID,
                    files=[f]
                )

        # Clean up
        os.remove(temp_path)
        
        if file_batch.status == "completed":
            return True
        return False

    except Exception as e:
        st.error(f"Error uploading file: {str(e)}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return False

def ask_question(question, thread_id):
    """Send question to assistant and get response"""
    try:
        if not question or not thread_id:
            return None
        if thread_id not in st.session_state.threads:
            return None

        client = get_client()
        if not client:
            return None

        thread = st.session_state.threads[thread_id]['thread']
        
        # Create message
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        # Run assistant (using same assistant as aceofSpades)
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id="asst_Wk1Ue0iDYkhbdiXXDPPJsvAV",
        )

        # Get final response
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        
        return messages.data[0].content[0].text.value

    except Exception as e:
        st.error(f"Error processing question: {str(e)}")
        return None

# Page UI
st.title("🤖 AI Chat Assistant")
st.caption("Chat with your AccuBid documents using AI")

# Sidebar
with st.sidebar:
    st.header("💬 Chat Management")
    
    # Thread Management
    st.subheader("Conversation Threads")
    new_thread_name = st.text_input("New Thread Name (optional)")
    
    if st.button("➕ Create New Thread", use_container_width=True):
        thread_id, thread_name = create_thread(new_thread_name)
        if thread_id:
            st.session_state.current_thread_id = thread_id
            st.session_state.current_thread_name = thread_name
            st.success(f"Created thread: {thread_name}")
            st.session_state.messages = []

    # Display existing threads
    threads = get_threads()
    if threads:
        st.subheader("Select Thread")
        thread_options = {thread['name']: thread['id'] for thread in threads}
        selected_thread = st.selectbox(
            "Choose a thread",
            options=list(thread_options.keys()),
            key="thread_selector"
        )
        
        if selected_thread:
            st.session_state.current_thread_id = thread_options[selected_thread]
            st.session_state.current_thread_name = selected_thread

        if st.button("🗑️ Delete Current Thread", use_container_width=True):
            if st.session_state.current_thread_id:
                if delete_thread(st.session_state.current_thread_id):
                    st.success("Thread deleted")
                    st.rerun()

    # File Upload
    st.markdown("---")
    st.subheader("📁 File Upload")
    uploaded_file = st.file_uploader("Upload Document", type=['pdf', 'xlsx', 'xls', 'csv', 'txt', 'md'])
    if uploaded_file:
        if process_uploaded_file(uploaded_file):
            st.success("File uploaded successfully!")
        else:
            st.error("Failed to upload file")

# Main chat interface
if st.session_state.current_thread_id:
    st.write(f"**Current Thread:** {st.session_state.current_thread_name}")
    
    # Display message history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about your AccuBid files or upload documents..."):
        # Show user message
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get and show assistant response
        with st.spinner("🤖 AI is thinking..."):
            if response := ask_question(prompt, st.session_state.current_thread_id):
                with st.chat_message("assistant"):
                    st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("👈 Please select or create a thread to start chatting.")
    
    # Welcome message
    st.markdown("""
    ## Welcome to AI Chat Assistant! 🤖
    
    **Getting Started:**
    1. Create a new conversation thread in the sidebar
    2. Upload documents to add them to your knowledge base
    3. Start asking questions about your AccuBid files!
    
    **What you can do:**
    - Ask questions about uploaded documents
    - Get cost breakdowns and project insights
    - Analyze electrical estimation data
    - Upload additional files to expand the knowledge base
    
    💡 **Tip:** Upload documents here to add them to your knowledge base for AI analysis!
    """)

# # Commented out non-essential features:
# # - Chat Settings (temperature, max_tokens)
# # - Quick Prompts
# # - Export functionality
# # - Tools button
# # - File context selection with multiselect
# # - Complex CSS styling
# # - Thread message count tracking
# # - Welcome screen with examples
