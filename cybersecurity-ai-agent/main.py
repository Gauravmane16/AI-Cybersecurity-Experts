import streamlit as st
import os
from ui.sidebar import render_sidebar
from ui.main_interface import render_main_interface
from agents.cybersecurity_agent import CybersecurityAgent

# Page configuration
st.set_page_config(
    page_title="AI Cybersecurity Expert",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

## Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #1e3c72;
    }
    
    .threat-high {
        border-left-color: #dc3545;
    }
    
    .threat-medium {
        border-left-color: #ffc107;
    }
    
    .threat-low {
        border-left-color: #28a745;
    }
    
    .code-container {
        background: #1e1e1e;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Initialize session state
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    
    # Render sidebar and get configuration
    sidebar_data = render_sidebar()
    
    # Initialize agent if API key is provided
    if sidebar_data['api_key'] and st.session_state.agent is None:
        try:
            st.session_state.agent = CybersecurityAgent(sidebar_data['api_key'])
        except Exception as e:
            st.error(f"Error initializing AI agent: {str(e)}")
    
    # Render main interface
    render_main_interface(sidebar_data, st.session_state.agent)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "🔒 AI Cybersecurity Expert | Built with Streamlit, LangChain & OpenAI | "
        "Always obtain proper authorization before security testing"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()