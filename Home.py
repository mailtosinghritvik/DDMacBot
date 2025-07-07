import streamlit as st
import time
import os
from datetime import datetime
from openai import OpenAI
import pandas as pd
import tempfile

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Vector Store ID for main RAG system (replace with your actual vector store ID)
VECTOR_STORE_ID = 'vs_qUspcB7VllWXM4z7aAEdIK9L'

# Set page configuration
st.set_page_config(
    page_title="AccuBid Converter",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Assistant Helper Functions
def process_excel_file(file):
    """Process Excel file and return sheet data"""
    try:
        xls = pd.ExcelFile(file)
        sheet_data = {}
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            sheet_data[sheet_name] = df
        return sheet_data, xls.sheet_names
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        return None, []

def collect_sheet_info_simple(sheet_names):
    """Collect sheet information with simple UI and store in session state"""
    sheet_info = {}
    
    for sheet_name in sheet_names:
        col1, col2 = st.columns(2)
        with col1:
            # Use session state to maintain values across reruns
            default_meaning = st.session_state.sheet_info.get(sheet_name, {}).get('meaning', '')
            meaning = st.text_input(f"What is '{sheet_name}'?", 
                                   value=default_meaning,
                                   key=f"meaning_{sheet_name}", 
                                   placeholder="e.g., Material costs, Labor hours...")
        with col2:
            # Use session state to maintain values across reruns
            default_description = st.session_state.sheet_info.get(sheet_name, {}).get('description', '')
            description = st.text_input(f"Description of '{sheet_name}'", 
                                       value=default_description,
                                       key=f"desc_{sheet_name}",
                                       placeholder="e.g., Detailed material breakdown...")
        
        sheet_info[sheet_name] = {"meaning": meaning, "description": description}
        
        # Store in session state immediately
        if sheet_name not in st.session_state.sheet_info:
            st.session_state.sheet_info[sheet_name] = {}
        st.session_state.sheet_info[sheet_name]['meaning'] = meaning
        st.session_state.sheet_info[sheet_name]['description'] = description
    
    return sheet_info

def generate_markdown_from_excel(sheet_data, sheet_info, project_info):
    """Generate markdown with chunking strategy"""
    markdown_content = ""
    char_count = 0
    chunk_size = 1000
    
    def add_context_marker():
        return f"\n\n<!-- CONTEXT: Project: {project_info.get('project_name', 'Unknown')} | Company: {project_info.get('company_name', 'Unknown')} | File: {project_info.get('file_name', 'Excel File')} | Description: {project_info.get('short_description', 'AccuBid project data')} -->\n\n"
    
    # Add header
    header = f"""# {project_info.get('project_name', 'Project Analysis')}

**Company:** {project_info.get('company_name', 'Unknown Company')}  
**Project Type:** {project_info.get('project_type', 'Unknown')}  
**Generated Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**File:** {project_info.get('file_name', 'Excel File')}  

## Project Overview
{project_info.get('short_description', 'No description provided')}

{project_info.get('additional_info', '')}

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

**Purpose:** {sheet_info.get(sheet_name, {}).get('meaning', 'Not specified')}  
**Description:** {sheet_info.get(sheet_name, {}).get('description', 'Not specified')}

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
                table_markdown = df_clean.to_markdown(index=False)
                markdown_content += table_markdown + "\n\n"
                char_count += len(table_markdown) + 2
                
                if char_count >= chunk_size:
                    markdown_content += add_context_marker()
                    char_count = 0
            else:
                # Large table - chunk it
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
        
        # Add numeric summary
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
    
    if char_count > 0:
        markdown_content += add_context_marker()
    
    return markdown_content

def upload_to_vector_store(markdown_content, filename):
    """Upload markdown content to vector store"""
    try:
        # Debug: Check if vector store ID is set
        if not VECTOR_STORE_ID:
            return False, "❌ Vector Store ID not configured"
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(markdown_content)
            temp_file_path = temp_file.name

        with open(temp_file_path, "rb") as f:
            file_batch = client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=VECTOR_STORE_ID,
                files=[f]
            )

        os.remove(temp_file_path)
        
        if file_batch.status == "completed":
            return True, "Successfully uploaded to vector store"
        else:
            return False, f"Upload failed with status: {file_batch.status}"
            
    except Exception as e:
        return False, f"Error uploading to vector store: {str(e)}"

def create_assistant_thread_with_excel(uploaded_file):
    """Create a new Assistant with code interpreter and upload the Excel file to it"""
    try:
        # Debug: Check OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, None, None, "❌ OpenAI API key not found in environment variables"
        
        # Save Excel file temporarily
        temp_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Upload Excel file to OpenAI for assistant use
        with open(temp_path, "rb") as f:
            file_obj = client.files.create(
                file=f,
                purpose='assistants'
            )

        # Clean up temp file
        os.remove(temp_path)
        
        # Create a new Assistant with code_interpreter and the Excel file
        project_info = st.session_state.project_info
        assistant_name = f"DDMac Bot - {project_info.get('project_name', 'Project')} Analyzer"
        assistant_description = f"""DDMac Bot expert for electrical estimation analysis.

Project: {project_info.get('project_name', 'Unknown')} | Company: {project_info.get('company_name', 'Unknown')} | Type: {project_info.get('project_type', 'Unknown')}

Analyzes Excel data for costs, materials, labor, timelines. Provides detailed answers, summaries, charts, and identifies optimization opportunities. Uses code interpreter for calculations and visualizations."""
        
        assistant = client.beta.assistants.create(
            name=assistant_name,
            description=assistant_description,
            model="gpt-4o",
            tools=[{"type": "code_interpreter"}],
            tool_resources={
                "code_interpreter": {
                    "file_ids": [file_obj.id]
                }
            }
        )
        
        # Create a thread for this assistant
        thread = client.beta.threads.create()
        
        return thread.id, file_obj.id, assistant.id, "Assistant and thread created successfully"
        
    except Exception as e:
        return None, None, None, f"Error creating assistant: {str(e)}"

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1f4e79 0%, #2e7d32 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .upload-zone {
        border: 3px dashed #cccccc;
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        background-color: #f8f9fa;
        margin: 2rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-zone:hover {
        border-color: #1f4e79;
        background-color: #e3f2fd;
    }
    
    .feature-box {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #1f4e79;
    }
    
    .result-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    
    .floating-chat {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(90deg, #1f4e79 0%, #2e7d32 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 25px;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        font-weight: bold;
        z-index: 1000;
    }
    
    .status-indicator {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    
    .status-ready { background-color: #d4edda; color: #155724; }
    .status-processing { background-color: #fff3cd; color: #856404; }
    .status-complete { background-color: #d1ecf1; color: #0c5460; }
    .status-error { background-color: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = 'ready'
if 'conversion_results' not in st.session_state:
    st.session_state.conversion_results = []
if 'project_info' not in st.session_state:
    st.session_state.project_info = None
if 'chat_open' not in st.session_state:
    st.session_state.chat_open = False
# Assistant API integration session state
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = None
if 'file_id' not in st.session_state:
    st.session_state.file_id = None
if 'markdown_content' not in st.session_state:
    st.session_state.markdown_content = None
if 'vector_upload_success' not in st.session_state:
    st.session_state.vector_upload_success = False
if 'sheet_info' not in st.session_state:
    st.session_state.sheet_info = {}
if 'sheet_names' not in st.session_state:
    st.session_state.sheet_names = []
if 'proceed_with_processing' not in st.session_state:
    st.session_state.proceed_with_processing = False
if 'floating_chat_open' not in st.session_state:
    st.session_state.floating_chat_open = False
if 'floating_chat_messages' not in st.session_state:
    st.session_state.floating_chat_messages = []
if 'assistant_id' not in st.session_state:
    st.session_state.assistant_id = None

# Header
st.markdown("""
<div class="main-header">
    <h1>⚡ AccuBid Document Converter</h1>
    <p>Transform your AccuBid files with AI-powered analysis and Assistant API integration</p>
</div>
""", unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # File Upload Section
    st.markdown("""
    <div class="upload-zone">
        <h2>📁 Upload Your AccuBid File</h2>
        <p>Drag and drop your Excel file (.xlsx, .csv) or click browse</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose your AccuBid file",
        type=['xlsx', 'xls', 'csv'],
        help="Upload Excel files from AccuBid software"
    )
    
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        
        # File details
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.1f} KB",
            "File type": uploaded_file.type
        }
        
        for key, value in file_details.items():
            st.write(f"**{key}:** {value}")
        
        st.markdown("---")
        
        # Project Information Form
        st.markdown("### 📋 Project Information")
        st.markdown("Please provide additional details about this project to enhance AI processing:")
        
        with st.form("project_info_form"):
            col_form1, col_form2 = st.columns(2)
            
            with col_form1:
                company_name = st.text_input(
                    "Company Name *",
                    placeholder="e.g., ABC Electrical Contractors",
                    help="Name of the electrical contractor or company"
                )
                
                project_name = st.text_input(
                    "Project Name *", 
                    placeholder="e.g., Downtown Office Complex Phase 2",
                    help="Specific name or identifier for this project"
                )
                
                project_type = st.selectbox(
                    "Project Type",
                    ["Commercial", "Residential", "Industrial", "Institutional", "Other"],
                    help="Type of electrical project"
                )
            
            with col_form2:
                project_location = st.text_input(
                    "Project Location",
                    placeholder="e.g., Seattle, WA",
                    help="City, state or general location"
                )
                
                contract_terms = st.text_area(
                    "Contract Terms & Conditions",
                    placeholder="e.g., Net 30 payment terms, warranty period, special requirements...",
                    height=100,
                    help="Any specific terms, payment conditions, or requirements"
                )
            
            additional_info = st.text_area(
                "Additional Project Information",
                placeholder="e.g., Special equipment requirements, timeline constraints, client preferences, project scope details...",
                height=120,
                help="Any other relevant information that would help in document generation"
            )
            
            submitted = st.form_submit_button("📝 Process with AI Enhancement", type="primary", use_container_width=True)
            
            if submitted:
                if not company_name or not project_name:
                    st.error("⚠️ Company Name and Project Name are required fields!")
                else:
                    # Store form data in session state
                    st.session_state.project_info = {
                        "company_name": company_name,
                        "project_name": project_name,
                        "project_type": project_type,
                        "project_location": project_location,
                        "contract_terms": contract_terms,
                        "additional_info": additional_info,
                        "short_description": f"{project_type} electrical project for {company_name}",
                        "file_name": uploaded_file.name
                    }
                    st.session_state.processing_status = 'processing'
                    st.rerun()
    
    # REAL PROCESSING IMPLEMENTATION
    if st.session_state.uploaded_file and hasattr(st.session_state, 'project_info'):
        if st.session_state.processing_status == 'processing':
            st.markdown('<div class="status-indicator status-processing">🤖 AI Processing Pipeline Active...</div>', unsafe_allow_html=True)
            
            # Step 1: Parse Excel file
            with st.spinner("📊 Parsing AccuBid Excel data structure..."):
                sheet_data, sheet_names = process_excel_file(st.session_state.uploaded_file)
                if not sheet_data:
                    st.error("Failed to process Excel file")
                    st.session_state.processing_status = 'error'
                    st.stop()

                # Store sheet names in session state
                st.session_state.sheet_names = sheet_names

            # ...existing code...

                # Check if processing button was clicked and all sheet info is available
                if st.session_state.get('proceed_with_processing', False):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        # Step 3: Create Assistant with code_interpreter and Excel file
                        progress_bar.progress(20)
                        status_text.text('🤖 Creating dedicated AI assistant with code interpreter for your Excel data...')
                        thread_id, file_id, assistant_id, assistant_msg = create_assistant_thread_with_excel(st.session_state.uploaded_file)
                        
                        if not thread_id:
                            st.error(f"❌ Assistant Creation Failed: {assistant_msg}")
                            st.error("🔍 Check your OpenAI API key and permissions")
                            st.session_state.processing_status = 'error'
                            st.session_state.proceed_with_processing = False
                            st.stop()
                        
                        # Step 4: Generate markdown document using session state data
                        progress_bar.progress(50)
                        status_text.text('📝 Creating comprehensive markdown document...')
                        
                        # Use sheet info from session state for processing
                        session_sheet_info = {
                            sheet_name: {
                                'meaning': st.session_state.sheet_info.get(sheet_name, {}).get('meaning', ''),
                                'description': st.session_state.sheet_info.get(sheet_name, {}).get('description', '')
                            }
                            for sheet_name in st.session_state.sheet_names
                        }
                        
                        markdown_content = generate_markdown_from_excel(
                            sheet_data, session_sheet_info, st.session_state.project_info
                        )
                        
                        # Step 5: Upload to vector store
                        progress_bar.progress(80)
                        status_text.text('🗄️ Uploading to vector store for future reference...')
                        upload_success, upload_msg = upload_to_vector_store(
                            markdown_content, 
                            f"{st.session_state.project_info['company_name']}_{st.session_state.project_info['project_name']}_enhanced.md"
                        )
                        
                        if not upload_success:
                            st.warning(f"⚠️ Vector Store Upload Failed: {upload_msg}")
                            st.warning("🔍 Check your Vector Store ID and API permissions")
                        
                        # Step 6: Complete processing - ONLY clear flag on success
                        progress_bar.progress(100)
                        status_text.text('✅ Processing complete! Ready for chat and document generation...')
                        time.sleep(1)
                        
                        # Store results
                        st.session_state.thread_id = thread_id
                        st.session_state.file_id = file_id
                        st.session_state.assistant_id = assistant_id
                        st.session_state.markdown_content = markdown_content
                        st.session_state.vector_upload_success = upload_success
                        
                        # Create results for display
                        project_info = st.session_state.project_info
                        st.session_state.conversion_results = [
                            {
                                "type": "Enhanced Project Data", 
                                "filename": f"{project_info['company_name']}_{project_info['project_name']}_enhanced.md",
                                "icon": "📄",
                                "description": "AI-enhanced project data with context markers"
                            },
                            {
                                "type": "RAG Vector Store Entry", 
                                "filename": f"Vector embedding for {project_info['project_name']}",
                                "icon": "🧠",
                                "description": "Added to knowledge base for chat queries",
                                "status": "Success" if upload_success else "Failed"
                            },
                            {
                                "type": "Assistant Thread", 
                                "filename": f"Assistant ID: {assistant_id}",
                                "icon": "🤖",
                                "description": "Dedicated AI assistant with Excel file and code interpreter"
                            }
                        ]
                        
                        # Clear the flag only on successful completion
                        st.session_state.proceed_with_processing = False
                        st.session_state.processing_status = 'complete'
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Processing Failed: {str(e)}")
                        st.error("🔍 Check your OpenAI API key, Vector Store ID, and network connection")
                        st.session_state.processing_status = 'error'
                        st.session_state.proceed_with_processing = False
                        st.stop()
                
                else:
                    # Step 2: Collect sheet information only if processing hasn't been triggered
                    st.markdown("### 📋 Sheet Context Required")
                    st.write("Please provide context for each sheet in your Excel file:")
                    
                    sheet_info = collect_sheet_info_simple(st.session_state.sheet_names)
                    
                    # Check if all sheet info is provided using session state data
                    all_info_provided = all(
                        st.session_state.sheet_info.get(sheet_name, {}).get('meaning', '').strip() and 
                        st.session_state.sheet_info.get(sheet_name, {}).get('description', '').strip()
                        for sheet_name in st.session_state.sheet_names
                    )
                    
                    if not all_info_provided:
                        st.warning("⚠️ Please provide meaning and description for all sheets before continuing.")
                        if st.button("⏹️ Cancel Processing"):
                            st.session_state.processing_status = 'ready'
                            st.rerun()
                    else:
                        if st.button("🚀 Continue with AI Processing", type="primary"):
                            # Set flag to proceed with processing on next rerun
                            st.session_state.proceed_with_processing = True
                            st.rerun()
                
        elif st.session_state.processing_status == 'complete':
            st.markdown('<div class="status-indicator status-complete">🎉 AI Enhancement Complete!</div>', unsafe_allow_html=True)
            
            # Show project summary
            if hasattr(st.session_state, 'project_info'):
                project_info = st.session_state.project_info
                st.markdown("### 📋 Processed Project Summary")
                
                col_summary1, col_summary2 = st.columns(2)
                with col_summary1:
                    st.metric("Company", project_info['company_name'])
                    st.metric("Project Type", project_info['project_type'])
                with col_summary2:
                    st.metric("Project", project_info['project_name'])
                    st.metric("Location", project_info['project_location'] or "Not specified")
                
                st.success("✅ Project data has been enhanced with AI and added to your knowledge base!")
                st.info("💬 You can now chat with this project data using the Chat page, or generate documents from the enhanced information.")
    
    # Results Section
    if st.session_state.conversion_results:
        st.markdown("## 🎯 Processing Results")
        
        for result in st.session_state.conversion_results:
            with st.container():
                st.markdown(f"""
                <div class="result-card">
                    <h4>{result['icon']} {result['type']}</h4>
                    <p><strong>Output:</strong> {result['filename']}</p>
                    <p><em>{result.get('description', '')}</em></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Different actions based on result type
                if result['type'] == "Enhanced Project Data":
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"📄 View Markdown", key=f"view_{result['type']}", use_container_width=True):
                            if st.session_state.markdown_content:
                                with st.expander("📄 Generated Markdown Content", expanded=True):
                                    st.markdown(st.session_state.markdown_content)
                            else:
                                st.info("Markdown content not available")
                    with col_b:
                        if st.button(f"⬇️ Download Markdown", key=f"download_{result['type']}", use_container_width=True):
                            if st.session_state.markdown_content:
                                st.download_button(
                                    label="💾 Download Markdown File",
                                    data=st.session_state.markdown_content,
                                    file_name=f"{st.session_state.project_info['company_name']}_{st.session_state.project_info['project_name']}_enhanced.md",
                                    mime="text/markdown",
                                    key=f"download_md_{result['type']}"
                                )
                            else:
                                st.info("Markdown content not available")
                
                elif result['type'] == "RAG Vector Store Entry":
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"💬 Chat with Vector Store", key=f"chat_{result['type']}", use_container_width=True):
                            st.info("Navigate to Chat page to query the vector store about this project!")
                    with col_b:
                        status_color = "🟢" if result.get('status') == 'Success' else "🔴"
                        st.write(f"Status: {status_color} {result.get('status', 'Unknown')}")
                
                elif result['type'] == "Assistant Thread":
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"🤖 Chat with Assistant", key=f"assistant_{result['type']}", use_container_width=True):
                            st.info(f"Use the floating chat widget below to chat with your dedicated assistant!")
                    with col_b:
                        if st.button(f"📋 Copy Assistant ID", key=f"copy_{result['type']}", use_container_width=True):
                            st.code(st.session_state.assistant_id)
                            st.success("Assistant ID displayed above - copy manually")

with col2:
    # Quick Actions Panel
    st.markdown("""
    <div class="feature-box">
        <h3>⚡ Next Steps</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.conversion_results:
        st.markdown("**🎯 What you can do now:**")
        
        if st.button("💬 Start Chatting", use_container_width=True):
            st.info("Navigate to Chat page to ask questions about your project")
        
        if st.button("📄 Generate Documents", use_container_width=True):
            st.info("Use chat to request Word docs, PDFs, or custom reports")
        
        if st.button("📧 Email Results", use_container_width=True):
            st.success("Email integration will be implemented in backend phase")
        
        if st.button("📅 Schedule Meeting", use_container_width=True):
            st.success("Calendar integration will be implemented in backend phase")
        
        if st.button("🔗 Share Link", use_container_width=True):
            st.success("Share functionality will be implemented in backend phase")
    else:
        st.info("Upload and convert a file to see quick actions")
    
    # File Statistics
    st.markdown("""
    <div class="feature-box">
        <h3>📊 File Statistics</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.uploaded_file:
        st.metric("File Size", f"{st.session_state.uploaded_file.size / 1024:.1f} KB")
        st.metric("Processing Time", "Real-time" if st.session_state.processing_status == 'complete' else "Pending")
        if st.session_state.vector_upload_success:
            st.metric("Vector Store", "✅ Uploaded")
        elif st.session_state.processing_status == 'complete':
            st.metric("Vector Store", "❌ Failed")
    else:
        st.info("Upload a file to see statistics")

# Floating Chat Widget - Enhanced for Assistant API with actual chat
if st.session_state.conversion_results and st.session_state.thread_id and st.session_state.assistant_id:
    project_name = st.session_state.project_info.get('project_name', 'this project') if st.session_state.project_info else 'this project'
    
    # Toggle chat widget
    if st.button("💬 Chat with Dedicated Assistant", help=f"Your personal AI assistant for {project_name} with code interpreter"):
        st.session_state.floating_chat_open = not st.session_state.floating_chat_open
    
    # Show chat interface if open
    if st.session_state.floating_chat_open:
        st.markdown("### 🤖 Dedicated Assistant Chat")
        st.write(f"**Assistant ID:** `{st.session_state.assistant_id}`")
        st.write(f"**Thread ID:** `{st.session_state.thread_id}`")
        st.write(f"**Project:** {project_name}")
        st.info("💡 This assistant can run Python code on your Excel data for detailed analysis!")
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.floating_chat_messages:
                if message['role'] == 'user':
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"**Assistant:** {message['content']}")
                    
                    # Display any images generated by Code Interpreter
                    if message.get('images'):
                        for image_file_id in message['images']:
                            try:
                                # Download and display the image
                                image_data = client.files.content(image_file_id)
                                image_bytes = image_data.read()
                                st.image(image_bytes, caption=f"Generated by Code Interpreter", use_column_width=True)
                            except Exception as img_error:
                                st.error(f"Could not display image {image_file_id}: {str(img_error)}")
        
        # Chat input
        user_message = st.text_input("Ask about your project...", key="floating_chat_input", placeholder="e.g., What is the total cost in this estimate?")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Send", key="send_chat"):
                if user_message.strip():
                    # Add user message to chat
                    st.session_state.floating_chat_messages.append({
                        'role': 'user',
                        'content': user_message
                    })
                    
                    try:
                        # Create message in the thread
                        client.beta.threads.messages.create(
                            thread_id=st.session_state.thread_id,
                            role="user",
                            content=user_message
                        )
                        
                        # Run the assistant
                        run = client.beta.threads.runs.create(
                            thread_id=st.session_state.thread_id,
                            assistant_id=st.session_state.assistant_id
                        )
                        
                        # Wait for completion (simple polling)
                        with st.spinner("Assistant is thinking..."):
                            while run.status in ['queued', 'in_progress']:
                                time.sleep(1)
                                run = client.beta.threads.runs.retrieve(thread_id=st.session_state.thread_id, run_id=run.id)
                        
                        if run.status == 'completed': 
                            # Get the assistant's response
                            messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
                            
                            # Process the message content - handle both text and images
                            assistant_content = ""
                            images = []
                            
                            for content_block in messages.data[0].content:
                                if hasattr(content_block, 'text'):
                                    # Text content
                                    assistant_content += content_block.text.value + "\n"
                                elif hasattr(content_block, 'image_file'):
                                    # Image content from Code Interpreter
                                    file_id = content_block.image_file.file_id
                                    images.append(file_id)
                                    assistant_content += f"[Generated Image: file-{file_id}]\n"
                            
                            # Store the message with both text and image info
                            message_data = {
                                'role': 'assistant', 
                                'content': assistant_content.strip(),
                                'images': images if images else None
                            }
                            
                            st.session_state.floating_chat_messages.append(message_data)
                            st.rerun()
                        else:
                            st.error(f"Assistant run failed with status: {run.status}")
                            
                    except Exception as e:
                        st.error(f"Chat error: {str(e)}")
                        st.session_state.floating_chat_messages.append({
                            'role': 'assistant',
                            'content': f"Sorry, I encountered an error: {str(e)}"
                        })
        
        with col2:
            if st.button("Close Chat", key="close_chat"):
                st.session_state.floating_chat_open = False
                st.rerun()

elif st.session_state.conversion_results:
    project_name = st.session_state.project_info.get('project_name', 'this project') if st.session_state.project_info else 'this project'
    st.markdown(f"""
    <div class="floating-chat" onclick="alert('Navigate to Chat page to ask questions about {project_name}!')">
        💬 Chat about {project_name}...
    </div>
    """, unsafe_allow_html=True)

# Reset button in sidebar
with st.sidebar:
    st.header("🛠️ Controls")
    
    if st.button("🔄 Reset & Start New Project", use_container_width=True):
        st.session_state.uploaded_file = None
        st.session_state.processing_status = 'ready'
        st.session_state.conversion_results = []
        st.session_state.project_info = None
        st.session_state.thread_id = None
        st.session_state.file_id = None
        st.session_state.assistant_id = None
        st.session_state.markdown_content = None
        st.session_state.vector_upload_success = False
        st.session_state.sheet_info = {}
        st.session_state.sheet_names = []
        st.session_state.proceed_with_processing = False
        st.session_state.floating_chat_open = False
        st.session_state.floating_chat_messages = []
        st.rerun()
    
    # Assistant Thread Info
    if st.session_state.thread_id and st.session_state.assistant_id:
        st.markdown("---")
        st.markdown("### 🤖 Dedicated Assistant")
        st.code(f"Assistant ID: {st.session_state.assistant_id}")
        st.code(f"Thread ID: {st.session_state.thread_id}")
        st.write(f"📁 File attached: {st.session_state.project_info.get('file_name', 'Excel file')}")
        st.write("🔧 **Tools:** Code Interpreter (can run Python on your Excel data)")
        if st.session_state.vector_upload_success:
            st.success("✅ Also available in main vector store")
        else:
            st.warning("⚠️ Vector store upload failed")
    
    st.markdown("---")
    st.markdown("### 📈 Usage Stats")
    st.metric("Files Processed Today", "12")
    st.metric("Total Conversions", "1,247")
    st.metric("Average Processing Time", "Real-time")
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("AccuBid Document Converter transforms electrical estimation files into professional documents using AI-powered formatting and Assistant API integration.")
