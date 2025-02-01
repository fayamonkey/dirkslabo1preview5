import streamlit as st
import json
import os
from datetime import datetime
import markdown
from laboratory import AgentLaboratory
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Dirk's Agent Laboratory Research Lab",
    page_icon="🧪",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .header-container {
        display: flex;
        align-items: center;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .company-info {
        color: #666;
        font-size: 0.9rem;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 5px;
        margin-top: 2rem;
    }
    .company-info a {
        color: #0066cc;
        text-decoration: none;
    }
    .company-info a:hover {
        text-decoration: underline;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'research_results' not in st.session_state:
    st.session_state.research_results = {}
    # Load existing results if available
    results_file = Path("research_results.json")
    if results_file.exists():
        try:
            with open(results_file, "r") as f:
                st.session_state.research_results = json.load(f)
        except:
            # If there's an error reading the file, start with empty results
            pass

if 'api_key' not in st.session_state:
    st.session_state.api_key = None

def save_results():
    """Save research results to JSON file"""
    try:
        with open("research_results.json", "w") as f:
            json.dump(st.session_state.research_results, f, indent=4)
    except:
        # If we can't save to file (e.g., on Streamlit Cloud), just keep results in memory
        pass

# Header with corporate identity
st.markdown("""
    <div class="header-container">
        <div style="flex: 1">
            <h1>Dirk's Agent Laboratory Research Lab</h1>
            <p style="color: #666;">
                Advanced Research Assistant by 
                <a href="https://ai-engineering.ai" target="_blank" style="color: #0066cc; text-decoration: none;">AI Engineering</a>
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Sidebar for API key and controls
with st.sidebar:
    st.header("Research Projects")
    
    # API Key Input
    api_key = st.text_input("Enter your OpenAI API Key", type="password", key="api_key_input",
                           help="Your API key will not be stored between sessions")
    if api_key:
        st.session_state.api_key = api_key
        
    # Show API key status
    if st.session_state.api_key:
        st.success("✅ API Key set")
    else:
        st.warning("⚠️ Please enter your API key")
    
    # New Research button
    if st.button("New Research", type="primary"):
        st.session_state.current_view = "new_research"
    
    # List of existing research projects
    if st.session_state.research_results:
        st.subheader("Previous Research")
        for timestamp, research in st.session_state.research_results.items():
            if st.button(f"📑 {research['topic']}", key=timestamp):
                st.session_state.current_view = "view_research"
                st.session_state.selected_research = timestamp
    
    # Add company info in sidebar footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
        <div class="company-info">
            <p><strong>AI Engineering</strong></p>
            <p>Author: Dirk Wonhoefer<br>
            Email: <a href="mailto:dirk.wonhoefer@ai-engineering.ai">dirk.wonhoefer@ai-engineering.ai</a><br>
            Website: <a href="https://ai-engineering.ai" target="_blank">ai-engineering.ai</a></p>
        </div>
    """, unsafe_allow_html=True)

# Main content area
def conduct_research(topic, focus_areas):
    """Conduct new research using AgentLaboratory"""
    if not st.session_state.api_key:
        st.error("Please enter your OpenAI API key in the sidebar first!")
        return False, "API key required"
    
    try:
        # Initialize the laboratory with the API key
        lab = AgentLaboratory(api_key=st.session_state.api_key, model_name="gpt-4o")
        
        task_notes = {
            "focus_areas": [area.strip() for area in focus_areas.split(",")],
            "experiment_preferences": {
                "dataset_size": "small",
                "model_complexity": "medium",
                "evaluation_metrics": ["accuracy", "perplexity"]
            }
        }
        
        with st.spinner("Conducting research..."):
            results = lab.conduct_research(topic, task_notes)
            
        # Save results
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.research_results[timestamp] = {
            "topic": topic,
            "focus_areas": focus_areas,
            "results": results
        }
        save_results()
        
        # Immediately show the results by updating the view
        st.session_state.current_view = "view_research"
        st.session_state.selected_research = timestamp
        
        # Force a rerun to update the sidebar and show the new research
        st.rerun()
        
        return True, "Research completed successfully!"
    except Exception as e:
        return False, f"Error during research: {str(e)}"

# New Research Form
if not hasattr(st.session_state, 'current_view'):
    st.session_state.current_view = "new_research"

if st.session_state.current_view == "new_research":
    st.header("New Research")
    
    with st.form("research_form"):
        topic = st.text_input("Research Topic")
        focus_areas = st.text_area("Focus Areas (comma-separated)")
        submitted = st.form_submit_button("Start Research")
        
        if submitted:
            if not st.session_state.api_key:
                st.error("Please enter your OpenAI API key in the sidebar first!")
            elif topic and focus_areas:
                success, message = conduct_research(topic, focus_areas)
                if success:
                    st.success(message)
                else:
                    st.error(message)

# View Research Results
elif st.session_state.current_view == "view_research":
    if hasattr(st.session_state, 'selected_research'):
        research = st.session_state.research_results[st.session_state.selected_research]
        st.header(f"Research Results: {research['topic']}")
        st.subheader("Focus Areas")
        st.write(research['focus_areas'])
        
        st.subheader("Results")
        # Display results in an expandable container to handle long content
        with st.expander("View Full Results", expanded=True):
            st.json(research['results'])
        
        # Export options
        if st.button("Export as Markdown"):
            def dict_to_markdown(d, level=0):
                md = ""
                indent = "  " * level
                
                if isinstance(d, dict):
                    for key, value in d.items():
                        if isinstance(value, (dict, list)):
                            md += f"{indent}### {key}\n\n"
                            md += dict_to_markdown(value, level + 1)
                        else:
                            # Check if value is a string containing markdown
                            if isinstance(value, str) and any(marker in value for marker in ['###', '##', '#', '**', '-']):
                                md += f"{indent}### {key}\n\n{value}\n\n"
                            else:
                                md += f"{indent}### {key}\n\n```\n{value}\n```\n\n"
                elif isinstance(d, list):
                    for item in d:
                        if isinstance(item, (dict, list)):
                            md += dict_to_markdown(item, level)
                        else:
                            md += f"{indent}- {item}\n"
                    md += "\n"
                else:
                    md += f"{indent}{d}\n\n"
                return md
            
            # Create markdown content
            md_content = f"# Research Results: {research['topic']}\n\n"
            md_content += f"## Focus Areas\n{research['focus_areas']}\n\n"
            md_content += "## Results\n\n"
            md_content += dict_to_markdown(research['results'])
            
            # Create download button
            st.download_button(
                label="Download Markdown",
                data=md_content,
                file_name=f"research_{research['topic'].lower().replace(' ', '_')}.md",
                mime="text/markdown"
            )

# Footer
st.markdown("---")
st.markdown("""
    <div class="company-info" style="text-align: center;">
        <p>© 2024 AI Engineering. All rights reserved.</p>
        <p>
            <a href="https://ai-engineering.ai" target="_blank">Visit our website</a> | 
            <a href="mailto:dirk.wonhoefer@ai-engineering.ai">Contact us</a>
        </p>
    </div>
""", unsafe_allow_html=True) 