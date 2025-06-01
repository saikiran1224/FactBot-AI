import streamlit as st
import json
import os
import time # For simulating loading animation
from trigger_crew import trigger_crew # Assuming your CrewAI code is in trigger_crew.py

# --- Page Configuration ---
st.set_page_config(
    page_title="FactBot AI: Your Clarity Companion",
    page_icon="🤖",
    layout="centered", # Or 'wide' for more horizontal space
    initial_sidebar_state="collapsed",
)

# --- Custom CSS for a modern, intuitive, and theme-friendly design ---
st.markdown("""
<style>
/* --- CSS Variables for better theme compatibility --- */
:root {
    /* Light Theme Defaults */
    --primary-green: #4CAF50;
    --dark-green: #2e7d32;
    --light-green: #e8f5e9; /* For light backgrounds */
    --border-green: #388e3c;

    --background-color-light: #f0f2f6; /* Very light grey */
    --card-background-light: #ffffff;
    --text-color-light: #333333;
    --subtle-text-color-light: #555555;
    --border-color-light: #e0e0e0;
    --shadow-color-light: rgba(0,0,0,0.1); /* Soft shadow */
    --accent-color-light: #007bff; /* For links etc. */
}

/* Dark Theme Overrides */
[data-theme="dark"] {
    --background-color-dark: #1a1a1a; /* Dark background */
    --card-background-dark: #2a2a2a;
    --text-color-dark: #e0e0e0; /* Light text */
    --subtle-text-color-dark: #b0b0b0;
    --border-color-dark: #3a3a3a;
    --shadow-color-dark: rgba(0,0,0,0.4); /* Darker shadow */
    --accent-color-dark: #8ab4f8; /* Lighter blue for dark theme links */

    /* Apply to main elements */
    --bg-color: var(--background-color-dark);
    --card-bg: var(--card-background-dark);
    --text-color: var(--text-color-dark);
    --subtle-text: var(--subtle-text-color-dark);
    --border-color: var(--border-color-dark);
    --shadow-color: var(--shadow-color-dark);
    --accent-color: var(--accent-color-dark);
}

/* Light Theme Application */
[data-theme="light"] {
    --bg-color: var(--background-color-light);
    --card-bg: var(--card-background-light);
    --text-color: var(--text-color-light);
    --subtle-text: var(--subtle-text-color-light);
    --border-color: var(--border-color-light);
    --shadow-color: var(--shadow-color-light);
    --accent-color: var(--accent-color-light);
}

/* --- General Body & Text Styling --- */
body {
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: var(--text-color);
    background-color: var(--bg-color);
}
.stApp {
    background-color: var(--bg-color);
    color: var(--text-color);
}
/* Ensure default markdown elements also pick up theme colors */
p, li {
    color: var(--text-color);
}

/* --- Typographical Hierarchy --- */
.main-header {
    font-size: 4.5em; /* Larger, more impactful */
    font-weight: 900; /* Ultra-bold */
    color: var(--dark-green);
    text-align: center;
    margin-bottom: 0.1em;
    text-shadow: 4px 4px 8px var(--shadow-color); /* More prominent shadow */
    letter-spacing: -2px; /* Tighter for modern feel */
}
.subheader {
    font-size: 1.8em; /* Slightly larger */
    color: var(--subtle-text);
    text-align: center;
    margin-bottom: 3.5em; /* More space */
    line-height: 1.4;
    max-width: 800px; /* Constrain width for readability */
    margin-left: auto;
    margin-right: auto;
}
.section-title {
    font-size: 2.8em; /* More prominent */
    font-weight: bold;
    color: var(--dark-green);
    text-align: center;
    margin-top: 4em; /* More vertical separation */
    margin-bottom: 2em;
    padding-bottom: 0.8em;
    border-bottom: 4px solid var(--border-color); /* Thicker underline */
}

/* --- Hero Section & Input --- */
.hero-section {
    background-color: var(--card-bg); /* Use card background for a distinct section */
    border-radius: 20px; /* More rounded corners */
    padding: 60px 40px; /* More padding */
    margin-top: 3em;
    margin-bottom: 4em;
    box-shadow: 0 10px 30px var(--shadow-color); /* Stronger shadow */
    text-align: center;
}
.hero-section .stTextArea label {
    font-size: 1.4em;
    font-weight: bold;
    color: var(--text-color);
    margin-bottom: 15px;
}
.hero-section .stTextArea textarea {
    border: 2px solid var(--primary-green);
    border-radius: 15px;
    padding: 20px;
    font-size: 1.1em;
    background-color: var(--bg-color); /* Slightly different background for input */
    color: var(--text-color);
    box-shadow: inset 2px 2px 8px rgba(0,0,0,0.05);
}
.hero-section .stButton > button {
    font-size: 1.8em; /* Larger button */
    padding: 15px 40px;
    margin-top: 25px;
    border-radius: 15px;
    box-shadow: 0 6px 15px rgba(0, 150, 0, 0.4);
}
.hero-image {
    border-radius: 15px; /* Rounded corners for image */
    margin-bottom: 3em;
    box-shadow: 0 8px 20px var(--shadow-color);
    transition: transform 0.3s ease;
}
.hero-image:hover {
    transform: scale(1.01);
}

/* --- "How it Works" Section --- */
.how-it-works-container {
    display: flex;
    justify-content: space-around;
    gap: 20px; /* Space between columns */
    margin-top: 2em;
    margin-bottom: 4em;
    flex-wrap: wrap; /* Allow wrapping on smaller screens */
}
.how-it-works-card {
    background-color: var(--card-bg);
    border-radius: 18px; /* More rounded */
    padding: 30px;
    box-shadow: 0 6px 20px var(--shadow-color);
    text-align: center;
    flex: 1; /* Distribute space evenly */
    min-width: 280px; /* Minimum width before wrapping */
    max-width: 32%; /* Max width for 3 columns */
    height: auto; /* Allow height to adjust */
    display: flex;
    flex-direction: column;
    justify-content: flex-start; /* Align content to top */
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    border: 1px solid var(--border-color);
}
.how-it-works-card:hover {
    transform: translateY(-10px); /* More pronounced lift */
    box-shadow: 0 10px 25px var(--shadow-color);
}
.how-it-works-card h4 {
    font-size: 1.8em; /* Larger icon/number */
    color: var(--primary-green);
    margin-bottom: 0.5em;
    font-weight: 800; /* Bolder for prominence */
}
.how-it-works-card h5 { /* For the text title like "You Ask FactBot" */
    font-size: 1.3em;
    color: var(--dark-green);
    margin-top: 0.5em;
    margin-bottom: 1em;
    font-weight: bold;
}
.how-it-works-card p {
    font-size: 1.05em;
    color: var(--subtle-text);
    line-height: 1.6;
}

/* --- Result Display --- */
.result-box {
    padding: 40px; /* More generous padding */
    border-radius: 20px; /* More rounded */
    margin-top: 4em;
    margin-bottom: 3em;
    box-shadow: 0 12px 30px var(--shadow-color); /* Stronger shadow */
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    background-color: var(--card-bg);
    border: 2px solid; /* Defined by specific verdict classes */
}
.result-box:hover {
    transform: translateY(-8px);
    box-shadow: 0 15px 35px var(--shadow-color);
}

/* Specific Verdict Colors - High contrast for both themes */
.verified { background-color: #d4edda; border-color: #28a745; color: #155724; } /* Light green, green border, dark green text */
.likely-verified { background-color: #fff3cd; border-color: #ffc107; color: #856404; } /* Light yellow, yellow border, dark yellow text */
.uncertain { background-color: #cce5ff; border-color: #007bff; color: #004085; } /* Light blue, blue border, dark blue text */
.likely-fake { background-color: #f8d7da; border-color: #dc3545; color: #721c24; } /* Light red, red border, dark red text */
.fake { background-color: #f8d7da; border-color: #dc3545; color: #721c24; } /* Same as likely-fake for clear warning */

/* Dark theme overrides for verdict boxes (if needed, but using universal colors is better) */
[data-theme="dark"] .verified { background-color: #215e21; border-color: #4CAF50; color: #e8f5e9; }
[data-theme="dark"] .likely-verified { background-color: #6a530e; border-color: #d39e00; color: #fff3cd; }
[data-theme="dark"] .uncertain { background-color: #0d47a1; border-color: #42a5f5; color: #e0f2f7; }
[data-theme="dark"] .likely-fake, [data-theme="dark"] .fake { background-color: #7f0000; border-color: #ff1744; color: #ffcdd2; }


.verdict-header {
    font-size: 3.2em; /* Even larger verdict text */
    font-weight: 900;
    text-align: center;
    margin-bottom: 0.8em;
    letter-spacing: 1.5px;
    text-shadow: 2px 2px 4px var(--shadow-color);
}
/* Specific verdict header colors - these use a more vibrant shade that works for text */
.verdict-header.fake-color { color: #dc3545; }
.verdict-header.verified-color { color: #28a745; }
.verdict-header.uncertain-color { color: #007bff; }

.verdict-reasoning-title {
    font-size: 1.5em;
    font-weight: bold;
    color: var(--dark-green);
    margin-top: 1.5em;
    margin-bottom: 0.8em;
}
.verdict-reasoning-text {
    font-size: 1.15em;
    line-height: 1.7;
    color: var(--text-color);
    margin-bottom: 1.5em;
}
.verdict-detail {
    font-size: 1.1em;
    margin-bottom: 0.8em;
    color: var(--subtle-text);
}
.verdict-detail strong {
    color: var(--text-color);
}

/* Citations and Sources */
.citation-section {
    margin-top: 3.5em;
    padding-top: 2em;
    border-top: 2px dashed var(--border-color); /* Thicker dashed line */
}
.citation-header {
    font-size: 1.8em;
    font-weight: bold;
    color: var(--dark-green);
    margin-bottom: 1.5em;
    text-align: center;
}
.citation-item {
    font-size: 1.1em;
    margin-bottom: 0.8em;
    line-height: 1.6;
    color: var(--subtle-text);
}
.citation-item a {
    color: var(--accent-color); /* Use theme-aware accent for links */
    text-decoration: none;
    transition: color 0.2s ease;
}
.citation-item a:hover {
    text-decoration: underline;
}

/* --- Footer --- */
.footer-info {
    margin-top: 5em;
    padding: 2.5em;
    background-color: var(--card-bg);
    border-radius: 15px;
    font-size: 1em;
    color: var(--subtle-text);
    text-align: center;
    box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
    border: 1px solid var(--border-color);
}
.footer-info p {
    color: var(--subtle-text); /* Ensure footer text is subtle */
}

/* --- Loading Animation --- */
.stSpinner > div > div {
    color: var(--primary-green) !important;
    font-size: 1.8em;
    font-weight: bold;
    margin-top: 1em; /* Adjust spacing */
}
.stProgress > div > div > div > div {
    background-color: var(--primary-green) !important;
}

/* --- Responsive Adjustments --- */
@media (max-width: 768px) {
    .main-header {
        font-size: 3.5em;
    }
    .subheader {
        font-size: 1.3em;
        margin-bottom: 2em;
    }
    .section-title {
        font-size: 2em;
        margin-top: 3em;
    }
    .how-it-works-card {
        max-width: 48%; /* Two columns on smaller screens */
    }
    .hero-section {
        padding: 40px 20px;
    }
    .hero-section .stButton > button {
        font-size: 1.4em;
        padding: 10px 25px;
    }
}

@media (max-width: 480px) {
    .main-header {
        font-size: 2.8em;
    }
    .subheader {
        font-size: 1.1em;
    }
    .how-it-works-card {
        max-width: 100%; /* Single column on very small screens */
    }
    .hero-section .stTextArea textarea {
        font-size: 1em;
        padding: 15px;
    }
}
</style>
""", unsafe_allow_html=True)

# --- Hero Section: The "Beacon of Clarity" ---
st.markdown("<div class='hero-section'>", unsafe_allow_html=True)
st.markdown("<h1 class='main-header'>✨ FactBot AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>Your friendly AI assistant for quickly checking news and spotting misinformation. Say goodbye to confusion!</p>", unsafe_allow_html=True)

# Main image for the hero section - a friendly robot casting light (conceptually)
st.image("https://images.unsplash.com/photo-1596541223130-5d31a735b149?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w1MDcwMDV8MHwxfHNlYXJjaHw2fHxyb2JvdCUyMGZhY3RjaGVja2VyfGVufDB8fHx8MTcwOTAwNjU3Nnww&ixlib=rb-4.0.3&q=80&w=1080",
         caption="FactBot AI: Your Clarity Companion",
         use_container_width=True, # Ensure responsive image sizing
         output_format="auto", # Optimal format
         clamp=True, # Prevent image from going outside container
         )
st.markdown("<div class='hero-image'></div>", unsafe_allow_html=True) # A div to hold the image if st.image is too restrictive with CSS

st.markdown("<p style='font-size:1.4em; color:var(--text-color); margin-top: 2em; font-weight: bold;'>Ready to cut through the noise?</p>", unsafe_allow_html=True)
news_headline_or_topic = st.text_area(
    "Paste any news headline or topic you want to verify:",
    "India to host G20 summit in 2025", # Example default input
    height=100,
    placeholder="E.g., 'New study finds coffee cures all diseases!' or 'Is this news story true?'"
)

if st.button("Ask FactBot AI! 🚀"):
    if not news_headline_or_topic:
        st.warning("Oops! Please type something for FactBot AI to analyze.")
    else:
        # Custom loading animation with progress bar
        progress_text = "FactBot AI's agents are on the case! Analyzing facts..."
        my_bar = st.progress(0, text=progress_text)

        for percent_complete in range(100):
            time.sleep(0.05) # Simulate AI processing time
            my_bar.progress(percent_complete + 1, text=f"{progress_text} {percent_complete + 1}%")
        my_bar.empty() # Clear the progress bar after completion

        # Placeholder for actual crew execution
        with st.spinner("FactBot AI is synthesizing results... Just a moment! ✨"):
            try:
                final_report = trigger_crew(news_headline_or_topic=news_headline_or_topic)

                if final_report:
                    st.success("Analysis Complete! Here's what FactBot AI found. 🎉")

                    # Extract details safely
                    verdict = final_report.get('final_verdict', 'Uncertain')
                    verdict_reasoning = final_report.get('verdict_reasoning', 'No specific reasoning provided.')
                    total_sources_checked = final_report.get('total_sources_checked', 'N/A')
                    recommendation = final_report.get('recommendation', 'No specific recommendation provided.')
                    supporting_citations = final_report.get('supporting_citations', [])

                    # Apply conditional styling based on verdict
                    verdict_class = verdict.lower().replace(" ", "-") # e.g., "likely-fake"
                    verdict_color_class = ""
                    if verdict == "Fake":
                        verdict_color_class = "fake-color"
                    elif verdict == "Verified":
                        verdict_color_class = "verified-color"
                    elif verdict == "Uncertain":
                        verdict_color_class = "uncertain-color"
                    # Add more for Likely Verified, Likely Fake if you want distinct colors

                    # --- Display Results Dashboard ---
                    st.markdown(f"<div class='result-box {verdict_class}'>", unsafe_allow_html=True)
                    st.markdown(f"<p class='verdict-header {verdict_color_class}'>Verdict: {verdict}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='verdict-reasoning-title'>Why FactBot AI says this: 💡</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='verdict-reasoning-text'>{verdict_reasoning}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='verdict-detail'><strong>Total Sources FactBot Examined:</strong> {total_sources_checked} 📚</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='verdict-detail'><strong>FactBot's Recommendation:</strong> {recommendation} ✅</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                    # --- Display Citations ---
                    if supporting_citations:
                        st.markdown("<div class='citation-section'>", unsafe_allow_html=True)
                        st.markdown("<p class='citation-header'>🔍 Sources FactBot AI Consulted:</p>", unsafe_allow_html=True)
                        for i, citation in enumerate(supporting_citations):
                            title = citation.get('title', f"Source {i+1}")
                            url = citation.get('url', '#')
                            if url and url != '#':
                                st.markdown(f"<p class='citation-item'>- [{title}]({url})</p>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<p class='citation-item'>- {title} (URL not available)</p>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.info("FactBot AI couldn't find specific supporting citations for this analysis.")

            except Exception as e:
                st.error(f"Uh oh! FactBot AI encountered an error during analysis: {e}. Please try again or check your API keys.")
                st.exception(e) # Display full exception for debugging

st.markdown("</div>", unsafe_allow_html=True) # Close hero-section div

st.write("---")

# --- How FactBot AI Works Section ---
st.markdown("<h2 class='section-title'>How FactBot AI Brings You Clarity 🤖</h2>", unsafe_allow_html=True)
st.markdown("""
<div style="font-size: 1.15em; line-height: 1.8; text-align: center; margin-bottom: 2em; color: var(--subtle-text);">
    FactBot AI uses a team of smart AI agents working together to cross-reference, analyze, and understand information from the web.
    <br>
    It's like having a super-efficient research team at your fingertips, turning confusion into clear understanding!
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='how-it-works-container'>", unsafe_allow_html=True)
st.markdown("""
    <div class='how-it-works-card'>
        <h4>1. 💬</h4>
        <h5>You Ask FactBot</h5>
        <p>Type in any news headline or topic you want FactBot AI to check. It's simple and intuitive!</p>
    </div>
    <div class='how-it-works-card'>
        <h4>2. 🧠</h4>
        <h5>AI Agents Uncover</h5>
        <p>Our smart AI team instantly researches reliable sources across the web, digging for facts, context, and potential misinformation.</p>
    </div>
    <div class='how-it-works-card'>
        <h4>3. ✅❌</h4>
        <h5>Truth Revealed</h5>
        <p>FactBot AI delivers a crystal-clear verdict, a simple explanation, and links to all the original sources it used. No more guessing!</p>
    </div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True) # Close how-it-works-container

st.write("---")

# --- "Why Trust FactBot AI?" Section ---
st.markdown("<h2 class='section-title'>Why Trust FactBot AI? 🤔</h2>", unsafe_allow_html=True)
st.markdown("""
<div style="font-size: 1.15em; line-height: 1.8; text-align: center; margin-bottom: 2em; color: var(--subtle-text);">
    FactBot AI is designed to be your intelligent ally in a world filled with information overload.
</div>
""", unsafe_allow_html=True)

col_trust1, col_trust2 = st.columns(2)

with col_trust1:
    st.markdown("""
    <div class='how-it-works-card' style='height: auto; max-width: 100%;'>
        <h4>🚀</h4>
        <h5>Powered by Advanced AI</h5>
        <p>We leverage cutting-edge AI technology, including models like Gemini and CrewAI, to bring you accurate and rapid verification.</p>
    </div>
    """, unsafe_allow_html=True)
with col_trust2:
    st.markdown("""
    <div class='how-it-works-card' style='height: auto; max-width: 100%;'>
        <h4>✅</h4>
        <h5>Transparent & Objective</h5>
        <p>FactBot AI provides factual analysis based on verifiable data, aiming for objectivity and always showing its sources.</p>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- Footer ---
st.markdown("""
<div class='footer-info'>
    <p>FactBot AI is a powerful tool designed to assist in news verification. While highly capable,
    AI can sometimes have limitations. Always apply your critical thinking and consult diverse, reputable sources for important decisions.
    <br>
    🤖 Built with ❤️ and AI. © 2025 FactBot AI. All rights reserved.
    </p>
</div>
""", unsafe_allow_html=True)