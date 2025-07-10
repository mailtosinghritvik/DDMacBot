import streamlit as st
import pandas as pd
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Customize Proposal - DDMac Bot",
    page_icon="⚙️",
    layout="wide"
)

# Custom CSS
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
    
    .customize-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #1f4e79;
    }
    
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .info-box {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #bbdefb;
    }
    
    .warning-box {
        background: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #ffcc02;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for customizations
if 'proposal_customizations' not in st.session_state:
    st.session_state.proposal_customizations = {
        'excel_interpretations': {},
        'cost_mappings': {},
        'template_replacements': {},
        'custom_instructions': "",
        'exclude_sheets': [],
        'cost_categories': {}
    }

# Header
st.markdown("""
<div class="main-header">
    <h1>⚙️ Customize Proposal Generation</h1>
    <p>Tell the AI how to interpret your Excel data and customize your proposal documents</p>
</div>
""", unsafe_allow_html=True)

# Check if we have the necessary session state data
assistant_id = st.session_state.get('assistant_id')
thread_id = st.session_state.get('thread_id')

if not assistant_id or not thread_id:
    st.warning("⚠️ No active assistant found. Please upload and process an Excel file on the Home page first.")
    st.info("👉 Go to the Home page to upload your AccuBid Excel file and create a dedicated assistant.")
    
    if st.button("🏠 Go to Home Page", use_container_width=True):
        st.switch_page("Home.py")
    
    st.stop()

# Get project and sheet info from session state
project_info = st.session_state.get('project_info', {})
sheet_info = st.session_state.get('sheet_info', {})

if not sheet_info:
    st.warning("⚠️ No Excel sheet information found. Please process your Excel file on the Home page first.")
    if st.button("🏠 Go to Home Page", use_container_width=True, key="go_home_no_sheets"):
        st.switch_page("Home.py")
    st.stop()

# Display current project info
st.markdown("""
<div class="customize-card">
    <h3>📋 Current Project Information</h3>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Company", project_info.get('company_name', 'N/A'))
    st.metric("Project Type", project_info.get('project_type', 'N/A'))
with col2:
    st.metric("Project Name", project_info.get('project_name', 'N/A'))
    st.metric("Location", project_info.get('project_location', 'N/A') or 'Not specified')
with col3:
    st.metric("Excel Sheets", f"{len(sheet_info)} found")
    st.metric("Assistant Status", "✅ Active")

# Section 1: Excel Data Interpretation
st.markdown("""
<div class="section-header">
    <h3>📊 Excel Data Interpretation</h3>
    <p>Help the AI understand what your Excel columns and data mean</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <h4>💡 Why This Matters</h4>
    <p>Your Excel file contains specialized electrical data. By explaining what each column and sheet means, 
    the AI can make much better decisions about how to use this data in your proposal.</p>
</div>
""", unsafe_allow_html=True)

# Display sheets and allow customization
for sheet_name, info in sheet_info.items():
    with st.expander(f"📋 Customize Sheet: {sheet_name}", expanded=False):
        st.write(f"**Current Description:** {info.get('description', 'N/A')}")
        
        col1, col2 = st.columns(2)
        with col1:
            custom_description = st.text_area(
                f"Custom description for '{sheet_name}'",
                value=st.session_state.proposal_customizations['excel_interpretations'].get(f"{sheet_name}_description", ""),
                help="Explain what this sheet contains and how it should be used in the proposal",
                key=f"desc_{sheet_name}"
            )
            
            # Column interpretations
            st.write("**Column Interpretations:**")
            columns_info = st.text_area(
                f"Explain important columns in '{sheet_name}'",
                value=st.session_state.proposal_customizations['excel_interpretations'].get(f"{sheet_name}_columns", ""),
                help="Example: 'Total Cost column represents final price including labor. Material Cost is just parts.'",
                key=f"cols_{sheet_name}"
            )
            
        with col2:
            # Cost identification
            st.write("**Cost Data Handling:**")
            cost_handling = st.text_area(
                f"How to handle costs in '{sheet_name}'",
                value=st.session_state.proposal_customizations['cost_mappings'].get(sheet_name, ""),
                help="Example: 'Use Total Cost for main pricing. Exclude Tax columns. Labor hours should be multiplied by $75/hour.'",
                key=f"cost_{sheet_name}"
            )
            
            # Sheet inclusion
            include_sheet = st.checkbox(
                f"Include '{sheet_name}' in proposal generation",
                value=sheet_name not in st.session_state.proposal_customizations['exclude_sheets'],
                key=f"include_{sheet_name}"
            )
        
        # Save the customizations
        if custom_description:
            st.session_state.proposal_customizations['excel_interpretations'][f"{sheet_name}_description"] = custom_description
        if columns_info:
            st.session_state.proposal_customizations['excel_interpretations'][f"{sheet_name}_columns"] = columns_info
        if cost_handling:
            st.session_state.proposal_customizations['cost_mappings'][sheet_name] = cost_handling
        
        if not include_sheet and sheet_name not in st.session_state.proposal_customizations['exclude_sheets']:
            st.session_state.proposal_customizations['exclude_sheets'].append(sheet_name)
        elif include_sheet and sheet_name in st.session_state.proposal_customizations['exclude_sheets']:
            st.session_state.proposal_customizations['exclude_sheets'].remove(sheet_name)

# Section 2: Template Tag Customization
st.markdown("""
<div class="section-header">
    <h3>🏷️ Template Tag Customization</h3>
    <p>Customize how specific template tags are filled in your proposal</p>
</div>
""", unsafe_allow_html=True)

# Template tags that can be customized
template_tags = {
    'INSERT_TO_COMPANY': 'Client company name',
    'INSERT_NAME_OF_PERSON': 'Client contact person name', 
    'INSERT_PROJECT_NAME': 'Project name/title',
    'INSERT_ON_THE_BASIS_PARAGRAPH_HERE': 'Project description/basis paragraph',
    'PROJECT_ORGANISER_NAME': 'Your company name',
    'PROJECT_ORGANISER_TITLE': 'Your company title/role',
    'ITEM_NOT_INCLUDED_1': 'First item not included in quote',
    'ITEM_NOT_INCLUDED_2': 'Second item not included in quote',
    'QUALIFICATION_1': 'First qualification/condition',
    'QUALIFICATION_2': 'Second qualification/condition'
}

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Client Information Tags:**")
    for tag in ['INSERT_TO_COMPANY', 'INSERT_NAME_OF_PERSON', 'INSERT_PROJECT_NAME']:
        custom_value = st.text_input(
            f"{tag}",
            value=st.session_state.proposal_customizations['template_replacements'].get(tag, ""),
            help=template_tags[tag],
            key=f"tag_{tag}"
        )
        if custom_value:
            st.session_state.proposal_customizations['template_replacements'][tag] = custom_value

    st.markdown("**Your Company Tags:**")
    for tag in ['PROJECT_ORGANISER_NAME', 'PROJECT_ORGANISER_TITLE']:
        custom_value = st.text_input(
            f"{tag}",
            value=st.session_state.proposal_customizations['template_replacements'].get(tag, ""),
            help=template_tags[tag],
            key=f"tag_{tag}"
        )
        if custom_value:
            st.session_state.proposal_customizations['template_replacements'][tag] = custom_value

with col2:
    st.markdown("**Project Description:**")
    basis_paragraph = st.text_area(
        "INSERT_ON_THE_BASIS_PARAGRAPH_HERE",
        value=st.session_state.proposal_customizations['template_replacements'].get('INSERT_ON_THE_BASIS_PARAGRAPH_HERE', ""),
        help="Custom description of the project basis and scope",
        height=100,
        key="tag_basis"
    )
    if basis_paragraph:
        st.session_state.proposal_customizations['template_replacements']['INSERT_ON_THE_BASIS_PARAGRAPH_HERE'] = basis_paragraph

    st.markdown("**Exclusions & Qualifications:**")
    for tag in ['ITEM_NOT_INCLUDED_1', 'ITEM_NOT_INCLUDED_2', 'QUALIFICATION_1', 'QUALIFICATION_2']:
        custom_value = st.text_input(
            f"{tag}",
            value=st.session_state.proposal_customizations['template_replacements'].get(tag, ""),
            help=template_tags[tag],
            key=f"tag_{tag}"
        )
        if custom_value:
            st.session_state.proposal_customizations['template_replacements'][tag] = custom_value

# Section 3: Cost Categorization
st.markdown("""
<div class="section-header">
    <h3>💰 Cost Categorization</h3>
    <p>Define how costs should be categorized and presented in the proposal</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Cost Categories:**")
    cost_categories = {
        'COST_ONE': st.text_input("Primary Cost Category", 
                                 value=st.session_state.proposal_customizations['cost_categories'].get('COST_ONE', 'Labor Costs'),
                                 key="cost_cat_1"),
        'COST_TWO': st.text_input("Secondary Cost Category", 
                                 value=st.session_state.proposal_customizations['cost_categories'].get('COST_TWO', 'Material Costs'),
                                 key="cost_cat_2"),
        'COST_THREE': st.text_input("Third Cost Category", 
                                   value=st.session_state.proposal_customizations['cost_categories'].get('COST_THREE', 'Equipment Costs'),
                                   key="cost_cat_3"),
        'COST_FOUR': st.text_input("Fourth Cost Category", 
                                  value=st.session_state.proposal_customizations['cost_categories'].get('COST_FOUR', 'Other Costs'),
                                  key="cost_cat_4")
    }
    
    # Save cost categories
    for key, value in cost_categories.items():
        if value:
            st.session_state.proposal_customizations['cost_categories'][key] = value

with col2:
    st.markdown("**Cost Calculation Instructions:**")
    cost_instructions = st.text_area(
        "How should costs be calculated and formatted?",
        value=st.session_state.proposal_customizations.get('cost_calculation_instructions', ""),
        help="Example: 'Add 15% markup to material costs. Round to nearest $100. Exclude tax from totals.'",
        height=150,
        key="cost_calc_instructions"
    )
    if cost_instructions:
        st.session_state.proposal_customizations['cost_calculation_instructions'] = cost_instructions

# Section 4: Custom Instructions
st.markdown("""
<div class="section-header">
    <h3>📝 Custom Instructions</h3>
    <p>Additional instructions for the AI when generating your proposal</p>
</div>
""", unsafe_allow_html=True)

custom_instructions = st.text_area(
    "Additional instructions for proposal generation",
    value=st.session_state.proposal_customizations['custom_instructions'],
    help="Any specific requirements, formatting preferences, or special handling instructions",
    height=150,
    key="custom_instructions_main"
)

if custom_instructions:
    st.session_state.proposal_customizations['custom_instructions'] = custom_instructions

# Section 5: Preview and Save
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💾 Save Customizations", type="primary", use_container_width=True):
        st.success("✅ Customizations saved successfully!")
        st.balloons()

with col2:
    if st.button("🔄 Reset to Defaults", use_container_width=True, key="reset_customizations"):
        st.session_state.proposal_customizations = {
            'excel_interpretations': {},
            'cost_mappings': {},
            'template_replacements': {},
            'custom_instructions': "",
            'exclude_sheets': [],
            'cost_categories': {}
        }
        st.success("🔄 Reset to default settings!")
        st.rerun()

with col3:
    if st.button("📄 Generate Proposal", type="primary", use_container_width=True, key="generate_with_customizations"):
        st.success("🚀 Redirecting to document generation...")
        st.switch_page("pages/Dashboard.py")

# Preview Section
with st.expander("👀 Preview Current Customizations", expanded=False):
    st.markdown("**Excel Interpretations:**")
    if st.session_state.proposal_customizations['excel_interpretations']:
        for key, value in st.session_state.proposal_customizations['excel_interpretations'].items():
            if value:
                st.write(f"- **{key}**: {value}")
    else:
        st.write("No custom interpretations set")
    
    st.markdown("**Template Replacements:**")
    if st.session_state.proposal_customizations['template_replacements']:
        for key, value in st.session_state.proposal_customizations['template_replacements'].items():
            if value:
                st.write(f"- **{key}**: {value}")
    else:
        st.write("Using default template values")
    
    st.markdown("**Cost Categories:**")
    if st.session_state.proposal_customizations['cost_categories']:
        for key, value in st.session_state.proposal_customizations['cost_categories'].items():
            if value:
                st.write(f"- **{key}**: {value}")
    else:
        st.write("Using default cost categories")
    
    if st.session_state.proposal_customizations['custom_instructions']:
        st.markdown("**Custom Instructions:**")
        st.write(st.session_state.proposal_customizations['custom_instructions'])

# Help Section
with st.sidebar:
    st.header("💡 Customization Guide")
    
    st.markdown("""
    ### How to Use This Page
    
    **1. Excel Interpretation**
    - Explain what your sheets contain
    - Describe important columns
    - Specify cost handling rules
    
    **2. Template Tags**
    - Customize client information
    - Set your company details
    - Define project descriptions
    
    **3. Cost Categories**
    - Name your cost categories
    - Set calculation rules
    - Define formatting preferences
    
    **4. Custom Instructions**
    - Add specific requirements
    - Note formatting preferences
    - Include special handling
    
    ### Tips
    - Be specific about column meanings
    - Explain any special calculations
    - Use clear, descriptive language
    - Save before generating proposals
    """)
    
    st.markdown("---")
    
    if st.button("🏠 Back to Home", use_container_width=True, key="sidebar_home"):
        st.switch_page("Home.py")
    
    if st.button("📊 View Dashboard", use_container_width=True, key="sidebar_dashboard"):
        st.switch_page("pages/Dashboard.py")
