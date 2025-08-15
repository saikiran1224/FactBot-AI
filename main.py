import streamlit as st
import json
import time
from datetime import datetime
from typing import Dict, Any

# importing crew module (ensure this path is correct for your project)
# Make sure 'trigger_crew.py' is accessible or adjust the import path
from trigger_crew import fact_check_crew 

# Configure page settings
st.set_page_config(
    page_title="FactBot AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Dark Theme Configuration ---
DARK_THEME = {
    "primary-color": "#4CAF50",  # Green - Success/Trust
    "secondary-color": "#2196F3",   # Lighter Blue
    "accent-color": "#FFD54F",       # Lighter Amber
    "success-color": "#8BC34A",
    "warning-color": "#FFD54F",
    "danger-color": "#E57373",       # Lighter Red
    "dark-bg": "#1E1E1E",            # Dark charcoal for components
    "light-bg": "#262730",           # Dark slate background for main content
    "main-bg": "#121212",            # Very dark gray overall background
    "text-color": "#E0E0E0",         # Light text
    "secondary-text-color": "#A0A0A0", # Medium light text
    "card-bg-gradient-light": "#2A2A2A",
    "card-bg-gradient-dark": "#333333",
}

# Initialize processing state
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

def apply_dark_theme():
    """Applies the dark theme's CSS variables."""
    theme_colors = DARK_THEME
    root_css_vars = ""
    for prop, value in theme_colors.items():
        root_css_vars += f"--{prop}: {value};\n"

    # Dynamic styling for result cards based on theme colors
    fake_result_bg = f"linear-gradient(135deg, {theme_colors['danger-color']}20, {theme_colors['card-bg-gradient-dark']})"
    true_result_bg = f"linear-gradient(135deg, {theme_colors['success-color']}20, {theme_colors['card-bg-gradient-dark']})"
    mixed_result_bg = f"linear-gradient(135deg, {theme_colors['warning-color']}20, {theme_colors['card-bg-gradient-dark']})"

    st.markdown(f"""
    <style>
        /* Google Fonts - Poppins for a modern, clean look */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

        :root {{
            {root_css_vars}
        }}

        /* Force dark theme on Streamlit elements */
        .stApp {{
            background-color: var(--main-bg) !important;
            color: var(--text-color) !important;
        }}

        body {{
            font-family: 'Poppins', sans-serif !important;
            background-color: var(--main-bg) !important;
            color: var(--text-color) !important;
        }}

        /* Hide default Streamlit styling */
        #MainMenu {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* General container styling */
        .main .block-container {{
            padding-top: 1rem;
            padding-right: 2rem;
            padding-left: 2rem;
            padding-bottom: 2rem;
            background-color: var(--main-bg) !important;
        }}
        
        /* Custom header */
        .main-header {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2.5rem;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            color: white;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .main-header h1 {{
            font-size: 3.5rem;
            font-weight: 700;
            margin: 0;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
            letter-spacing: -1px;
        }}
        
        .main-header p {{
            font-size: 1.3rem;
            opacity: 0.95;
            margin: 0.75rem 0 0 0;
            line-height: 1.5;
        }}

        /* Input section styling */
        .input-section {{
            background: var(--dark-bg) !important;
            padding: 2.5rem;
            border-radius: 18px;
            box-shadow: 0 6px 25px rgba(0,0,0,0.3);
            margin-bottom: 2.5rem;
            border: 1px solid var(--dark-bg);
            color: var(--text-color) !important;
        }}

        .input-section h3 {{
            color: var(--primary-color) !important;
            font-weight: 600;
            margin-bottom: 1.5rem;
        }}
        
        /* Text Area Styling */
        .stTextArea > div > div > textarea {{
            background-color: var(--dark-bg) !important;
            color: var(--text-color) !important;
            border: 2px solid var(--dark-bg) !important;
            border-radius: 15px !important;
            padding: 1rem !important;
            font-size: 1.1rem !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        }}
        .stTextArea > div > div > textarea:focus {{
            border-color: var(--secondary-color) !important;
            box-shadow: 0 0 0 0.2rem var(--secondary-color)40 !important;
        }}

        /* Results styling */
        .result-card {{
            padding: 2.5rem;
            border-radius: 18px;
            margin: 1.5rem 0;
            box-shadow: 0 6px 25px rgba(0,0,0,0.3);
            border-left: 8px solid;
            color: var(--text-color) !important;
            background-color: var(--light-bg) !important;
        }}
        
        .fake-result {{
            background: {fake_result_bg} !important;
            border-left-color: var(--danger-color);
        }}
        
        .true-result {{
            background: {true_result_bg} !important;
            border-left-color: var(--success-color);
        }}
        
        .mixed-result {{
            background: {mixed_result_bg} !important;
            border-left-color: var(--warning-color);
        }}
        
        /* Expander styling */
        .streamlit-expanderHeader {{
            background-color: var(--dark-bg) !important;
            color: var(--text-color) !important;
            border-radius: 10px !important;
        }}
        .streamlit-expanderContent {{
            background-color: var(--light-bg) !important;
            color: var(--text-color) !important;
            padding: 1.5rem !important;
            border-radius: 0 0 10px 10px !important;
        }}
        .stExpander {{
            border-radius: 10px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
            border: 1px solid var(--dark-bg) !important;
            margin-top: 1.5rem;
            overflow: hidden;
            background-color: var(--light-bg) !important;
        }}
        
        /* Citation cards */
        .citation-card {{
            background: var(--dark-bg) !important;
            padding: 1.2rem 1.5rem;
            border-radius: 12px;
            margin: 0.75rem 0;
            box-shadow: 0 3px 12px rgba(0,0,0,0.2);
            border-left: 4px solid var(--secondary-color);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            color: var(--text-color) !important;
        }}
        
        .citation-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }}
        .citation-card h4 {{
            color: var(--secondary-color) !important;
            font-weight: 600;
            margin-bottom: 0.4rem;
        }}
        .citation-card a {{
            color: var(--secondary-text-color) !important;
            font-size: 0.9rem;
            word-break: break-all;
            text-decoration: none;
        }}
        .citation-card a:hover {{
            text-decoration: underline;
            color: var(--secondary-color) !important;
        }}
        
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
            color: white !important;
            border: none !important;
            padding: 0.85rem 2.5rem !important;
            border-radius: 30px !important;
            font-weight: 600 !important;
            margin-top: 1.1rem !important;
            font-size: 1.15rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 5px 20px rgba(76, 175, 80, 0.3) !important;
            cursor: pointer !important;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4) !important;
            filter: brightness(1.05) !important;
            color: white !important;
        }}

        .stButton > button:disabled {{
            background: var(--secondary-text-color) !important;
            color: var(--dark-bg) !important;
            cursor: not-allowed !important;
            transform: none !important;
            box-shadow: none !important;
        }}

        .stDownloadButton > button {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
            color: white !important;
            border: none !important;
            padding: 0.85rem 2.5rem !important;
            border-radius: 30px !important;
            font-weight: 600 !important;
            margin-top: 1.1rem !important;
            font-size: 1.15rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 5px 20px rgba(76, 175, 80, 0.3) !important;
            cursor: pointer !important;
        }}

        /* Metric Cards */
        [data-testid="stMetric"] {{
            background-color: var(--dark-bg) !important;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.2);
            border-bottom: 5px solid var(--accent-color);
            text-align: center;
        }}
        [data-testid="stMetric"] label {{
            color: var(--secondary-text-color) !important;
            font-size: 1rem;
            font-weight: 600;
        }}
        [data-testid="stMetric"] div[data-testid="stMetricValue"] {{
            font-size: 2.2rem;
            color: var(--primary-color) !important;
            font-weight: 700;
        }}
        
        /* Progress bar styling */
        .stProgress > div > div > div > div {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        }}
        .stProgress > div > div {{
            background-color: var(--dark-bg) !important;
        }}
        
        /* Status badges */
        .status-badge {{
            display: inline-block;
            padding: 0.6rem 1.2rem;
            border-radius: 25px;
            font-weight: 700;
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.75px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}
        
        .fake-badge {{
            background: var(--danger-color) !important;
            color: white !important;
        }}
        
        .true-badge {{
            background: var(--success-color) !important;
            color: white !important;
        }}
        
        .mixed-badge {{
            background: var(--warning-color) !important;
            color: var(--dark-bg) !important;
        }}

        /* Success/Error/Info messages */
        .stAlert {{
            background-color: var(--dark-bg) !important;
            color: var(--text-color) !important;
            border-radius: 10px;
            border: 1px solid var(--secondary-text-color);
        }}

        /* Download Buttons */
        .stDownloadButton > button {{
            background: var(--secondary-color) !important;
            color: white !important;
            box-shadow: 0 4px 15px var(--secondary-color)30 !important;
        }}
        .stDownloadButton > button:hover {{
            box-shadow: 0 6px 20px var(--secondary-color)40 !important;
        }}

        /* Sidebar styling */
        .css-1d391kg {{
            background-color: var(--light-bg) !important;
        }}

        /* Force all text elements to use dark theme colors */
        .stMarkdown, .stText, p, div, span {{
            color: var(--text-color) !important;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-color) !important;
        }}

        /* Info box styling */
        .stInfo {{
            background-color: var(--dark-bg) !important;
            color: var(--text-color) !important;
            border-left: 4px solid var(--secondary-color) !important;
        }}

        /* Warning box styling */
        .stWarning {{
            background-color: var(--dark-bg) !important;
            color: var(--text-color) !important;
            border-left: 4px solid var(--warning-color) !important;
        }}

        /* Error box styling */
        .stError {{
            background-color: var(--dark-bg) !important;
            color: var(--text-color) !important;
            border-left: 4px solid var(--danger-color) !important;
        }}

        /* Success box styling */
        .stSuccess {{
            background-color: var(--dark-bg) !important;
            color: var(--text-color) !important;
            border-left: 4px solid var(--success-color) !important;
        }}
    </style>
    """, unsafe_allow_html=True)

def create_header():
    """Create the main application header with a modern design."""
    st.markdown("""
    <div class="main-header">
        <h1>🔍 FactBot AI</h1>
        <p>Your Intelligent Partner in Combating Misinformation</p>
    </div>
    """, unsafe_allow_html=True)

def display_results(result: Dict[str, Any], execution_time: str):
    """
    Display fact-checking results in a beautifully styled card format.
    Includes verdict, reasoning, recommendation, and sources.
    """
    verdict = result['final_verdict'].lower()
    
    # Determine card styling based on verdict
    card_class = ""
    badge_class = ""
    icon = ""
    verdict_color = ""

    if verdict == 'fake' or verdict == 'false':
        card_class = "fake-result"
        badge_class = "fake-badge"
        icon = "❌"
        verdict_color = "var(--danger-color)"
    elif verdict == 'true':
        card_class = "true-result"
        badge_class = "true-badge"
        icon = "✅"
        verdict_color = "var(--success-color)"
    else: # mixed or uncertain
        card_class = "mixed-result"
        badge_class = "mixed-badge"
        icon = "⚠️"
        verdict_color = "var(--warning-color)"
    
    # Main result card with animated verdict
    st.markdown(f"""
    <div class="result-card {card_class}">
        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
            <span style="font-size: 2.8rem; margin-right: 1.2rem; animation: bounceIn 0.8s ease-out;">{icon}</span>
            <div>
                <h2 style="margin: 0; color: {verdict_color}; font-weight: 700;">
                    VERDICT: <span class="status-badge {badge_class}">{result['final_verdict'].upper()}</span>
                </h2>
            </div>
        </div>
        <style>
            @keyframes bounceIn {{
                0% {{ transform: scale(0.1); opacity: 0; }}
                60% {{ transform: scale(1.1); opacity: 1; }}
                100% {{ transform: scale(1); }}
            }}
        </style>
    </div>
    """, unsafe_allow_html=True)
    
    # Reasoning section
    with st.expander("📝 Detailed Analysis & Reasoning", expanded=True):
        st.markdown(f"<p style='font-weight: 600; color: var(--secondary-color); font-size: 1.1rem;'>Reasoning:</p>", unsafe_allow_html=True)
        st.write(result.get('verdict_reasoning', 'No detailed reasoning provided.'))
        
        st.markdown(f"<p style='font-weight: 600; color: var(--secondary-color); font-size: 1.1rem;'>Recommendation:</p>", unsafe_allow_html=True)
        st.info(result.get('recommendation', 'No specific recommendation provided.'))
    
    # Sources section
    if result.get('supporting_citations'):
        with st.expander(f"📚 Supporting Sources ({len(result['supporting_citations'])} sources found)", expanded=True):
            for i, citation in enumerate(result['supporting_citations'], 1):
                st.markdown(f"""
                <div class="citation-card">
                    <h4 style="margin: 0 0 0.5rem 0;">
                        {i}. {citation.get('title', 'No Title Available')}
                    </h4>
                    <a href="{citation.get('url', '#')}" target="_blank">
                        🔗 {citation.get('url', 'URL Not Available')}
                    </a>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No specific supporting citations were found for this claim.")
    
    # Statistics Metrics
    st.markdown("---")
    st.markdown("<h3 style='text-align: center; color: var(--secondary-color);'>Performance Metrics</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Sources Checked", value=result.get('total_sources_checked', 'N/A'))
    with col2:
        st.metric(label="Analysis Time", value=execution_time)

def main():
    """Main application function to run the FactBot AI interface."""
    # Apply dark theme CSS
    apply_dark_theme()

    # --- Main Content ---
    create_header()

    st.markdown("### 📝 Enter News or Topic to Fact-Check")
    
    user_input = st.text_area(
        label="Please enter a claim or news headline to analyze:",
        label_visibility="collapsed",
        height=180,
        placeholder="e.g., 'A new study confirms that eating chocolate daily improves cognitive function.'",
        key="user_input_textarea",
        disabled=st.session_state.is_processing
    )

    # Initialize execution_time to ensure it's always defined
    execution_time_str = "0.00s"
    
    # Action button centered - only show when not processing
    col_empty1, col_btn, col_empty2 = st.columns([1, 2, 1])
    with col_btn:
        if not st.session_state.is_processing:
            analyze_button = st.button("Analyze Claim", use_container_width=True, key="analyze_claim_btn")
        else:
            st.button("🔍 Analyzing...", use_container_width=True, disabled=True, key="analyzing_btn")
            analyze_button = False
    
    # Process fact-checking
    if analyze_button and user_input.strip():
        st.session_state.is_processing = True
        st.rerun()
    
    if st.session_state.is_processing and user_input.strip():
        st.markdown("---")
        
        # Progress bar with status message
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Simulate progress updates
            progress_steps = [
                (20, "🔍 Searching for relevant sources..."),
                (40, "📊 Analyzing claim credibility..."),
                (60, "🧠 Processing with AI agents..."),
                (80, "📝 Generating detailed analysis..."),
                (100, "✅ Analysis complete!")
            ]
            
            # Record start time
            start_time = time.time()
            
            # Update progress bar in steps
            for progress, message in progress_steps:
                progress_bar.progress(progress)
                status_text.text(message)
                time.sleep(10.0)  # Small delay for visual effect
            
            # Call the fact-checking crew
            result = fact_check_crew(news_headline_or_topic=user_input)
            
            # Record end time and calculate duration
            end_time = time.time()
            execution_time_raw = end_time - start_time
            execution_time_str = f"{execution_time_raw:.2f}s"
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Reset processing state
            st.session_state.is_processing = False
            
            # Display results
            st.markdown("## 📋 Fact-Check Results")
            display_results(result, execution_time_str)
            
            # Export options
            st.markdown("---")
            st.markdown("<h3 style='text-align: center; color: var(--secondary-color);'>Export Results</h3>", unsafe_allow_html=True)
            col_json, col_report, col_copy = st.columns(3)
            
            with col_json:
                if result:
                    st.download_button(
                        label="📄 Export JSON",
                        data=json.dumps(result, indent=2),
                        file_name=f"factcheck_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        key="download_json_btn",
                        use_container_width=True
                    )
            
            with col_report:
                if result:
                    report = f"""FACTBOT AI - FACT CHECK REPORT
                        -------------------------------------------------
                        Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        Processing Time: {execution_time_str}

                        CLAIM:
                        {user_input}

                        -------------------------------------------------
                        VERDICT: {result.get('final_verdict', 'N/A')}

                        REASONING:
                        {result.get('verdict_reasoning', 'No detailed reasoning provided.')}

                        RECOMMENDATION:
                        {result.get('recommendation', 'No specific recommendation provided.')}

                        SOURCES CHECKED: {result.get('total_sources_checked', 'N/A')}

                        SUPPORTING CITATIONS:
                        """
                    if result.get('supporting_citations'):
                        for i, citation in enumerate(result['supporting_citations'], 1):
                            report += f"\n{i}. Title: {citation.get('title', 'N/A')}\n   URL: {citation.get('url', 'N/A')}\n"
                    else:
                        report += "\nNone\n"

                    st.download_button(
                        label="📊 Export Report",
                        data=report,
                        file_name=f"factcheck_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        key="download_report_btn",
                        use_container_width=True
                    )

            with col_copy:
                if result:
                    if st.button("📋 Copy JSON to Display", key="copy_clipboard_btn", use_container_width=True):
                        st.code(json.dumps(result, indent=2), language="json")
                        st.success("JSON result displayed above for manual copy!")

        except Exception as e:
            # Clear progress indicators on error
            progress_bar.empty()
            status_text.empty()
            st.session_state.is_processing = False
            
            st.error(f"An error occurred during fact-checking: {e}")
            st.warning("Please try again or refine your input.")
            st.exception(e)

    elif st.session_state.is_processing and not user_input.strip():
        st.session_state.is_processing = False
        st.warning("Please enter a claim or news headline to analyze.")

if __name__ == "__main__":
    main()