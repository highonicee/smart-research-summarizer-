import streamlit as st
from datetime import datetime
import os

# NLTK setup with proper error handling
try:
    import nltk

    # Download required NLTK data
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords

    NLTK_AVAILABLE = True
except ImportError:
    st.warning("NLTK not available. Please install with: pip install nltk")
    NLTK_AVAILABLE = False


    # Fallback tokenization
    def sent_tokenize(text):
        return text.split('.')


    def word_tokenize(text):
        return text.split()


    stopwords = None

# Try importing PyMuPDF with error handling
try:
    import fitz  # PyMuPDF

    PDF_AVAILABLE = True
except ImportError as import_error:
    fitz = None
    st.error(f"PyMuPDF import error: {import_error}")
    st.error("Please install PyMuPDF using: pip install PyMuPDF")
    PDF_AVAILABLE = False

# Import theme toggle
try:
    from theme_toggle import create_theme_toggle, apply_theme_styles, get_current_theme

    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False


    # Define fallback functions
    def create_theme_toggle():
        pass


    def apply_theme_styles():
        pass


    def get_current_theme():
        return "light"


    st.warning("Theme toggle not available. Please ensure theme_toggle.py is in the same directory.")


# Basic summarization function (fallback if transformers not available)
def basic_summarize(text, max_sentences=5):
    """Basic extractive summarization using sentence scoring"""
    if not NLTK_AVAILABLE:
        # Very basic fallback
        sentences = text.split('.')[:max_sentences]
        return '. '.join(sentences) + '.'

    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())

    if stopwords and NLTK_AVAILABLE:
        try:
            stop_words = set(stopwords.words('english'))
            words = [word for word in words if word not in stop_words and word.isalnum()]
        except:
            words = [word for word in words if word.isalnum()]

    # Simple frequency-based scoring
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1

    sentence_scores = {}
    for sentence in sentences:
        sentence_words = word_tokenize(sentence.lower())
        score = 0
        word_count = 0
        for word in sentence_words:
            if word in word_freq:
                score += word_freq[word]
                word_count += 1
        if word_count > 0:
            sentence_scores[sentence] = score / word_count

    # Get top sentences
    top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
    summary_sentences = [sent[0] for sent in top_sentences[:max_sentences]]

    return ' '.join(summary_sentences)


# Advanced summarization with transformers (if available)
def advanced_summarize(text, min_length=50, max_length=200):
    """Advanced summarization using transformers"""
    try:
        from transformers import pipeline
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

        # Split text into chunks if too long
        max_chunk_length = 1024
        if len(text) > max_chunk_length:
            chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]
            summaries = []
            for chunk in chunks:
                if len(chunk.strip()) > 50:  # Only summarize substantial chunks
                    chunk_summary = summarizer(chunk,
                                               min_length=min(30, len(chunk.split()) // 4),
                                               max_length=min(100, len(chunk.split()) // 2),
                                               do_sample=False)[0]['summary_text']
                    summaries.append(chunk_summary)

            # Combine and re-summarize if needed
            combined_summary = ' '.join(summaries)
            if len(combined_summary.split()) > max_length:
                final_summary = summarizer(combined_summary,
                                           min_length=min_length,
                                           max_length=max_length,
                                           do_sample=False)[0]['summary_text']
                return final_summary
            return combined_summary
        else:
            summary = summarizer(text,
                                 min_length=min_length,
                                 max_length=max_length,
                                 do_sample=False)[0]['summary_text']
            return summary

    except ImportError:
        st.warning("Transformers not available. Using basic summarization.")
        return basic_summarize(text, max_sentences=max_length // 20)
    except Exception as e:
        st.warning(f"Advanced summarization failed: {e}. Using basic method.")
        return basic_summarize(text, max_sentences=max_length // 20)


def generate_word_frequency_chart(text):
    """Generate word frequency chart using Plotly"""
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        from collections import Counter
        import re

        # Clean and tokenize text
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

        # Remove common stop words
        common_stops = {'the', 'and', 'are', 'for', 'with', 'this', 'that', 'from', 'they', 'have', 'been', 'will',
                        'would', 'could', 'should'}
        words = [word for word in words if word not in common_stops]

        # Get top 15 most frequent words
        word_freq = Counter(words).most_common(15)

        if not word_freq:
            st.warning("No significant words found for visualization.")
            return

        words, frequencies = zip(*word_freq)

        # Create interactive bar chart
        fig = px.bar(
            x=list(frequencies),
            y=list(words),
            orientation='h',
            title="Top 15 Most Frequent Words",
            labels={'x': 'Frequency', 'y': 'Words'},
            color=list(frequencies),
            color_continuous_scale='Viridis'
        )

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_x=0.5,
            height=500,
            yaxis={'categoryorder': 'total ascending'}
        )

        st.plotly_chart(fig, use_container_width=True)

        # Word cloud alternative using bar chart
        st.markdown("##### Word Frequency Distribution")
        fig2 = go.Figure(data=[go.Scatter(
            x=list(frequencies),
            y=list(words),
            mode='markers',
            marker=dict(
                size=[f * 2 for f in frequencies],
                color=list(frequencies),
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Frequency")
            ),
            text=list(words),
            textposition="middle center",
            hovertemplate="<b>%{text}</b><br>Frequency: %{x}<extra></extra>"
        )])

        fig2.update_layout(
            title="Word Frequency Bubble Chart",
            xaxis_title="Frequency",
            yaxis_title="Words",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=400
        )

        st.plotly_chart(fig2, use_container_width=True)

    except ImportError:
        st.info("📊 Install Plotly for interactive visualizations: pip install plotly")
    except Exception as e:
        st.error(f"Visualization error: {e}")


def load_css():
    """Load custom CSS for the professional landing page"""
    css = """
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* Hide Streamlit default elements completely */
        .stApp > header {visibility: hidden !important; height: 0px !important;}
        .stApp > footer {visibility: hidden !important; height: 0px !important;}
        #MainMenu {visibility: hidden !important;}
        .stDeployButton {display: none !important;}
        footer {visibility: hidden !important;}
        .stDecoration {display: none !important;}
        header[data-testid="stHeader"] {display: none !important;}
        .stToolbar {display: none !important;}

        /* Remove default Streamlit padding/margins */
        .main .block-container {
            padding-top: 0rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            padding-bottom: 1rem !important;
            max-width: 100% !important;
        }

        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #334155 50%, #1e293b 75%, #0f172a 100%);
            background-size: 400% 400%;
            animation: gradient-flow 20s ease infinite;
            min-height: 100vh;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            position: relative;
            overflow-x: hidden;
        }

        @keyframes gradient-flow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Enhanced visual effects */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 120%;
            height: 120%;
            background-image: 
                radial-gradient(ellipse 900px 500px at 15% 20%, rgba(6, 182, 212, 0.4) 0%, rgba(14, 165, 233, 0.3) 30%, rgba(34, 197, 94, 0.2) 50%, transparent 80%),
                radial-gradient(ellipse 700px 900px at 85% 80%, rgba(16, 185, 129, 0.35) 0%, rgba(6, 182, 212, 0.25) 25%, rgba(59, 130, 246, 0.15) 60%, transparent 85%);
            animation: nebula-drift 30s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }

        @keyframes nebula-drift {
            0%, 100% { transform: translateX(0) translateY(0) rotate(0deg); opacity: 0.8; }
            50% { transform: translateX(-15px) translateY(-25px) rotate(-1deg); opacity: 0.75; }
        }

        /* TOP NAVBAR STYLES */
        .top-navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 50%, rgba(51, 65, 85, 0.85) 100%);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(6, 182, 212, 0.3);
            box-shadow: 0 4px 25px rgba(0, 0, 0, 0.4);
            z-index: 1000;
            height: 80px;
        }

        .navbar-content {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }

        .nav-brand {
            font-size: 1.8rem;
            font-weight: 900;
            background: linear-gradient(135deg, #06b6d4, #10b981, #14b8a6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            display: flex;
            align-items: center;
            gap: 0.7rem;
        }

        .nav-brand-icon {
            font-size: 2rem;
            animation: logo-glow 3s ease-in-out infinite;
        }

        @keyframes logo-glow {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }

        /* Add top margin to main content */
        .stApp > div:first-child {
            margin-top: 80px;
        }

        /* Hero section */
        .hero-section {
            text-align: center;
            padding: 4rem 0;
            position: relative;
            z-index: 2;
            margin-top: 2rem;
        }

        .hero-badge {
            display: inline-block;
            padding: 0.75rem 2rem;
            background: rgba(6, 182, 212, 0.2);
            color: #06b6d4;
            border-radius: 50px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 2rem;
            border: 1px solid rgba(6, 182, 212, 0.4);
            animation: pulse-glow 4s ease-in-out infinite;
        }

        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 0 25px rgba(6, 182, 212, 0.4); transform: scale(1); }
            50% { box-shadow: 0 0 35px rgba(6, 182, 212, 0.6); transform: scale(1.05); }
        }

        .main-title {
            font-size: clamp(3rem, 8vw, 5.5rem);
            font-weight: 900;
            color: white;
            line-height: 1.1;
            margin-bottom: 2rem;
            letter-spacing: -0.02em;
        }

        .subtitle {
            font-size: clamp(1.2rem, 3vw, 1.8rem);
            color: white;
            font-weight: 500;
            margin-bottom: 1.5rem;
            line-height: 1.4;
        }

        .description {
            font-size: clamp(1rem, 2.5vw, 1.3rem);
            color: white;
            margin-bottom: 3rem;
            line-height: 1.6;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }

        /* Make all text white */
        h1, h2, h3, h4, h5, h6, p, div, span, li {
            color: white !important;
        }

        .stMarkdown, .stMarkdown * {
            color: white !important;
        }

        /* Enhanced button styling */
        .stButton > button {
            background: linear-gradient(135deg, #06b6d4 0%, #10b981 50%, #14b8a6 100%) !important;
            border: none !important;
            color: white !important;
            padding: 1.25rem 3rem !important;
            border-radius: 16px !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            transition: all 0.4s ease !important;
            box-shadow: 0 10px 40px rgba(6, 182, 212, 0.5) !important;
            min-width: 250px !important;
            height: 60px !important;
        }

        .stButton > button:hover {
            transform: translateY(-3px) scale(1.05) !important;
            box-shadow: 0 15px 50px rgba(6, 182, 212, 0.7) !important;
        }

        /* File uploader styling */
        .stFileUploader > div > div {
            background: rgba(255, 255, 255, 0.95) !important;
            border: 2px dashed #06b6d4 !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            text-align: center !important;
            transition: all 0.3s ease !important;
        }

        .stFileUploader > div > div:hover {
            background: rgba(255, 255, 255, 1) !important;
            border-color: #10b981 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(6, 182, 212, 0.3) !important;
        }

        /* Cards and feature styling */
        .feature-card {
            background: rgba(6, 182, 212, 0.05);
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 2rem;
            border: 1px solid rgba(6, 182, 212, 0.2);
            transition: all 0.4s ease;
            text-align: center;
            height: 100%;
            position: relative;
            z-index: 2;
        }

        .feature-card:hover {
            background: rgba(6, 182, 212, 0.1);
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(6, 182, 212, 0.3);
            border-color: rgba(6, 182, 212, 0.4);
        }

        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            display: block;
        }

        .feature-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: #06b6d4;
            margin-bottom: 1rem;
        }

        .feature-text {
            color: white;
            line-height: 1.6;
        }

        /* Metrics styling */
        .stMetric {
            background: rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            border: 1px solid rgba(6, 182, 212, 0.2) !important;
        }

        .stMetric label {
            color: #06b6d4 !important;
            font-weight: 600 !important;
        }

        .stMetric div {
            color: white !important;
            font-weight: 700 !important;
        }

        /* LinkedIn link styling */
        .linkedin-link {
            color: #06b6d4 !important;
            text-decoration: none !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }

        .linkedin-link:hover {
            color: #10b981 !important;
            text-decoration: underline !important;
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
            .nav-brand {
                font-size: 1.6rem;
            }
            .stButton > button {
                min-width: 200px !important;
                padding: 1rem 2rem !important;
            }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_streamlit_navbar():
    """Render navbar with just the brand name"""
    st.markdown("""
    <div class="top-navbar">
        <div class="navbar-content">
            <div class="nav-brand">
                <span class="nav-brand-icon">🧠</span>
                <span>Smart Research Summarizer</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_landing_page():
    """Render the landing page using pure Streamlit components"""

    # Show status messages
    if not PDF_AVAILABLE:
        st.error("⚠️ PDF processing is currently unavailable. Please install PyMuPDF.")
        st.code("pip install PyMuPDF", language="bash")

    if not NLTK_AVAILABLE:
        st.warning("⚠️ NLTK not available. Install for better text processing.")
        st.code("pip install nltk", language="bash")

    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-badge">🚀 AI-Powered Research Analysis with Interactive Visualizations</div>
        <h1 class="main-title">Smart Research Summarizer</h1>
        <p class="subtitle">Transform PDFs into intelligent summaries with stunning interactive charts</p>
        <div style="text-align: center; max-width: 800px; margin: 0 auto;">
            <p class="description">Upload any PDF research paper and get comprehensive summaries with beautiful interactive visualizations including word frequency charts, summary statistics, and data analytics.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA Button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button(" Start Analyzing", key="main_cta", use_container_width=True):
            st.session_state.show_app = True
            st.rerun()

    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

    # Features Section
    st.markdown("##  Key Features")

    feature_cols = st.columns(2)

    with feature_cols[0]:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3 class="feature-title">Interactive Visualizations</h3>
            <p class="feature-text">Beautiful word frequency charts and summary analytics with hover effects, zoom, and export capabilities.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3 class="feature-title">AI-Powered Analysis</h3>
            <p class="feature-text">Advanced AI models extract key insights and findings from complex academic papers with precision.</p>
        </div>
        """, unsafe_allow_html=True)

    with feature_cols[1]:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <h3 class="feature-title">Smart Summarization</h3>
            <p class="feature-text">Choose from short, medium, or long summaries tailored to your needs with advanced text processing.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💾</div>
            <h3 class="feature-title">Export & Download</h3>
            <p class="feature-text">Download complete analysis of generated reports with metadata, statistics, and visualizations included.</p>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: white;">
        <p><strong>© 2025 Ritika Yadav Smart Research Summarizer. All rights reserved.</strong></p>
        <p style="margin: 1rem 0; font-size: 0.9rem;">Empowering research through AI and interactive visualization</p>
        <p style="margin: 0.5rem 0; font-size: 0.9rem;">
            <a href="https://www.linkedin.com/in/ritika-yadav-b27344286/" target="_blank" class="linkedin-link">Connect</a>
        </p>
    </div>
    """, unsafe_allow_html=True)


def run_summarizer_app():
    """Run the main summarizer application"""

    # Status checks
    if not PDF_AVAILABLE:
        st.error("❌ PDF processing unavailable. Please install PyMuPDF.")
        st.code("pip install PyMuPDF", language="bash")
        if st.button("← Back to Landing Page", key="back_to_landing_error"):
            st.session_state.show_app = False
            st.rerun()
        return

    # Theme handling
    if THEME_AVAILABLE:
        create_theme_toggle()
        apply_theme_styles()
    else:
        if "dark_mode" not in st.session_state:
            st.session_state.dark_mode = False

        col1, col2 = st.columns([9, 1])
        with col2:
            st.markdown("### ")
            if st.toggle("🌓", value=st.session_state.dark_mode, help="Toggle Dark/Light Mode"):
                st.session_state.dark_mode = True
            else:
                st.session_state.dark_mode = False

    # Back button
    if st.button("← Back to Landing Page", key="back_to_landing"):
        st.session_state.show_app = False
        st.rerun()

    # App Title
    st.title("🧠 Smart Research Summarizer")

    # Status indicator
    status_text = " Ready" if PDF_AVAILABLE else "⚠️ Limited (PDF unavailable)"
    if not NLTK_AVAILABLE:
        status_text += " | Basic tokenization"
    st.markdown(f"### Upload a PDF research paper for AI analysis | Status: {status_text}")

    # Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### 📄 Upload Your Document")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf",
                                         help="Upload a research paper in PDF format")

    with col2:
        st.markdown("#### ⚙️ Settings")
        summary_length = st.radio(
            "Summary Length:",
            ["Short", "Medium", "Long"],
            help="Short: ~5 sentences, Medium: ~8 sentences, Long: ~12 sentences"
        )

        show_graphs = st.checkbox("Generate Visualizations", value=True,
                                  help="Create word frequency charts and analytics")

    if uploaded_file is not None:
        try:
            # Process PDF
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            full_text = ""
            for page in doc:
                full_text += page.get_text()

            st.markdown("#### 📖 Document Preview")

            with st.expander("Click to view extracted text", expanded=False):
                preview_text = full_text[:2000] + "..." if len(full_text) > 2000 else full_text
                st.text_area("", value=preview_text, height=200, disabled=True)

            # Document stats
            word_count = len(full_text.split())
            char_count = len(full_text)
            estimated_read_time = max(1, round(word_count / 250))

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Word Count", f"{word_count:,}")
            with col2:
                st.metric("Characters", f"{char_count:,}")
            with col3:
                st.metric("Est. Read Time", f"{estimated_read_time} min")

            # Generate button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                button_text = "🤖 Generate Summary + 📊 Visualizations" if show_graphs else "🤖 Generate Summary"
                if st.button(button_text, type="primary", use_container_width=True):

                    progress_text = f"🔄 Generating {summary_length.lower()} summary"
                    if show_graphs:
                        progress_text += " with visualizations"

                    with st.spinner(progress_text):
                        try:
                            # Length mapping
                            length_map = {
                                "Short": {"sentences": 5, "min_len": 50, "max_len": 120},
                                "Medium": {"sentences": 8, "min_len": 120, "max_len": 200},
                                "Long": {"sentences": 12, "min_len": 200, "max_len": 350}
                            }

                            params = length_map[summary_length]

                            # Try advanced summarization first, fallback to basic
                            try:
                                summary = advanced_summarize(full_text,
                                                             min_length=params["min_len"],
                                                             max_length=params["max_len"])
                            except:
                                summary = basic_summarize(full_text,
                                                          max_sentences=params["sentences"])

                            st.balloons()

                            success_msg = f"✅ {summary_length} summary generated!"
                            if show_graphs:
                                success_msg += " Visualizations created!"
                            st.success(success_msg)

                            # Summary stats
                            summary_word_count = len(summary.split())
                            compression_ratio = round((1 - summary_word_count / word_count) * 100)

                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Summary Words", summary_word_count)
                            with col2:
                                st.metric("Compression", f"{compression_ratio}%")
                            with col3:
                                st.metric("Summary Type", summary_length)

                            # Display summary with dynamic theming
                            st.markdown("#### 📝 Generated Summary")

                            # Dynamic styling based on theme
                            if st.session_state.get("dark_mode", False):
                                box_bg = "linear-gradient(135deg, #2d3748 0%, #374151 100%)"
                                text_color = "#e2e8f0"
                                border_color = "#06b6d4"
                                shadow_color = "rgba(6, 182, 212, 0.2)"
                                box_border = "1px solid rgba(255, 255, 255, 0.1)"
                            else:
                                box_bg = "linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)"
                                text_color = "#2d3748"
                                border_color = "#06b6d4"
                                shadow_color = "rgba(6, 182, 212, 0.1)"
                                box_border = "1px solid rgba(0, 0, 0, 0.1)"

                            st.markdown(f"""
                            <div style="
                                background: {box_bg};
                                padding: 25px;
                                border-radius: 20px;
                                border-left: 4px solid {border_color};
                                margin: 15px 0;
                                box-shadow: 0 10px 30px {shadow_color};
                                backdrop-filter: blur(10px);
                                border: {box_border};
                            ">
                                <p style="margin: 0; line-height: 1.7; font-size: 16px; color: {text_color};">{summary}</p>
                            </div>
                            """, unsafe_allow_html=True)

                            # Show visualizations if enabled
                            if show_graphs:
                                st.markdown("---")
                                st.markdown("#### 📊 Interactive Analysis & Visualizations")
                                st.markdown("*Hover over charts for interactive features*")

                                # Create tabs for different visualizations
                                tab1, tab2 = st.tabs(["📊 Word Frequency", "📈 Summary Analytics"])

                                with tab1:
                                    st.markdown("##### Most Frequent Terms Analysis")
                                    generate_word_frequency_chart(summary)

                                with tab2:
                                    st.markdown("##### Document & Summary Statistics")

                                    try:
                                        import plotly.graph_objects as go
                                        import plotly.express as px

                                        # Summary comparison chart
                                        fig_comparison = px.bar(
                                            x=['Original Document', 'Generated Summary'],
                                            y=[word_count, summary_word_count],
                                            title="Word Count Comparison",
                                            color=['Original Document', 'Generated Summary'],
                                            color_discrete_sequence=['#06b6d4', '#10b981']
                                        )
                                        fig_comparison.update_layout(
                                            plot_bgcolor='rgba(0,0,0,0)',
                                            paper_bgcolor='rgba(0,0,0,0)',
                                            font_color='white',
                                            showlegend=False
                                        )
                                        st.plotly_chart(fig_comparison, use_container_width=True)

                                        # Compression gauge
                                        fig_gauge = go.Figure(go.Indicator(
                                            mode="gauge+number+delta",
                                            value=compression_ratio,
                                            domain={'x': [0, 1], 'y': [0, 1]},
                                            title={'text': "Compression Efficiency %"},
                                            delta={'reference': 50},
                                            gauge={
                                                'axis': {'range': [None, 100]},
                                                'bar': {'color': "#10b981"},
                                                'steps': [
                                                    {'range': [0, 25], 'color': "#ef4444"},
                                                    {'range': [25, 50], 'color': "#f59e0b"},
                                                    {'range': [50, 75], 'color': "#06b6d4"},
                                                    {'range': [75, 100], 'color': "#10b981"}
                                                ],
                                                'threshold': {
                                                    'line': {'color': "white", 'width': 4},
                                                    'thickness': 0.75,
                                                    'value': 80
                                                }
                                            }
                                        ))

                                        fig_gauge.update_layout(
                                            plot_bgcolor='rgba(0,0,0,0)',
                                            paper_bgcolor='rgba(0,0,0,0)',
                                            font_color='white',
                                            height=400
                                        )
                                        st.plotly_chart(fig_gauge, use_container_width=True)

                                        # Reading time comparison
                                        original_read_time = max(1, round(word_count / 250))
                                        summary_read_time = max(1, round(summary_word_count / 250))
                                        time_saved = max(0, original_read_time - summary_read_time)

                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("Original Read Time", f"{original_read_time} min")
                                        with col2:
                                            st.metric("Summary Read Time", f"{summary_read_time} min")
                                        with col3:
                                            st.metric("Time Saved", f"{time_saved} min")

                                    except ImportError:
                                        st.info("📈 Install Plotly for advanced visualizations: pip install plotly")
                                    except Exception as e:
                                        st.warning(f"Visualization error: {e}")

                            # Download section
                            st.markdown("---")
                            st.markdown("#### 💾 Download Your Analysis")

                            filename = f"{summary_length.lower()}_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

                            download_content = f"""Smart Research Summarizer - Analysis Report
{'=' * 50}
Summary Type: {summary_length}
Original Word Count: {word_count:,}
Summary Word Count: {summary_word_count}
Compression Ratio: {compression_ratio}%
Time Saved: {max(0, round(word_count / 250) - round(summary_word_count / 250))} minutes
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Visualizations: {'Enabled' if show_graphs else 'Disabled'}

{'=' * 50}
SUMMARY:
{'=' * 50}

{summary}

{'=' * 50}
Generated by Smart Research Summarizer
AI-Powered Analysis with Interactive Visualizations
{'=' * 50}
"""

                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col2:
                                st.download_button(
                                    "📥 Download Complete Report",
                                    data=download_content,
                                    file_name=filename,
                                    mime="text/plain",
                                    use_container_width=True,
                                    help="Download summary with metadata and statistics"
                                )

                        except Exception as e:
                            st.error(f"❌ Error generating summary: {str(e)}")
                            st.info("Please try again or check if all dependencies are installed.")

        except Exception as e:
            st.error(f"❌ Error processing PDF: {str(e)}")
            st.info("Please try uploading a different PDF file.")

    else:
        # Welcome section
        st.markdown("### 👋 Welcome to Smart Research Summarizer!")
        st.markdown("Get started by uploading a PDF research paper above.")

        # Info about features
        info_text = f"""
**📊 Summary Options:**

• **Short:** Quick insights (~5 sentences)

• **Medium:** Balanced overview (~8 sentences) 

• **Long:** Comprehensive summary (~12 sentences)

**📈 Visualization Features:** {' Available' if True else '⚠️ Limited'}

• **Word Frequency Charts:** Interactive bar and bubble charts

• **Summary Statistics:** Compression metrics and analytics

• **Export Options:** Download reports with full analysis

**🔧 Current Status:**

• PDF Processing: {' Ready' if PDF_AVAILABLE else '❌ Unavailable'}
• Text Processing: {'Enhanced (NLTK)' if NLTK_AVAILABLE else '⚠️ Basic'}
• Visualizations:  Available (Plotly)
        """
        st.info(info_text)

        # Installation help
        if not PDF_AVAILABLE or not NLTK_AVAILABLE:
            st.markdown("#### 🔧 Setup Instructions")
            if not PDF_AVAILABLE:
                st.code("pip install PyMuPDF", language="bash")
            if not NLTK_AVAILABLE:
                st.code("pip install nltk", language="bash")

    # Footer
    st.markdown(f"""
    <div style="text-align: center; margin-top: 50px; padding: 20px; color: white; border-top: 1px solid #4a5568;">
        <p style="margin: 0; font-size: 12px; font-weight: 500;">© 2025 Smart Research Summarizer. All rights reserved.</p>
        <p style="margin: 5px 0 0 0; font-size: 10px;">AI-Powered Analysis with Interactive Visualizations</p>
        <p style="margin: 5px 0 0 0; font-size: 10px;">
            <a href="https://www.linkedin.com/in/ritika-yadav-b27344286/" target="_blank" class="linkedin-link">Connect</a>
        </p>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="🧠 Smart Research Summarizer - AI Analysis with Interactive Visualizations",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Initialize session state
    if 'show_app' not in st.session_state:
        st.session_state.show_app = False

    # Load CSS
    load_css()
    render_streamlit_navbar()

    # Route to appropriate page
    if st.session_state.show_app:
        try:
            with st.spinner("🚀 Loading Smart Research Summarizer..."):
                import time
                time.sleep(1)
            run_summarizer_app()
        except Exception as e:
            st.error(f"❌ Error loading application: {str(e)}")
            st.info("Please ensure all dependencies are properly installed.")

            if st.button("← Back to Landing Page", key="error_back"):
                st.session_state.show_app = False
                st.rerun()
    else:
        render_landing_page()


if __name__ == "__main__":
    main()