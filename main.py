import streamlit as st
from datetime import datetime

# Predefine all variables to avoid PyCharm warnings
nltk = None
sent_tokenize = None
word_tokenize = None
stopwords = None
NLTK_AVAILABLE = False

# Optional: import Streamlit if you're using it
try:
    import streamlit as st
except ImportError:
    st = None

# Try to import nltk
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords

    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

    NLTK_AVAILABLE = True

except ImportError:
    # Provide fallback methods
    def sent_tokenize(text):
        return text.split('.')


    def word_tokenize(text):
        return text.split()


    class MockStopwords:
        @staticmethod
        def words(lang):
            return {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}


    stopwords = MockStopwords()

    if st:
        st.warning("⚠️ NLTK not installed. Please run: pip install nltk")
    else:
        print("⚠️ NLTK not installed. Please run: pip install nltk")

# Try importing PyMuPDF with error handling
try:
    import fitz  # PyMuPDF

    PDF_AVAILABLE = True
except ImportError as import_error:
    # Define fallback when PyMuPDF is not available
    class MockFitz:
        @staticmethod
        def open(*args, **kwargs):
            raise ImportError("PyMuPDF not available")


    fitz = MockFitz()
    PDF_AVAILABLE = False

# Import theme toggle with fallback
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
        return "dark"  # Changed to dark as default

# Try importing visualization libraries with fallbacks
try:
    import plotly.express as px
    import plotly.graph_objects as go

    PLOTLY_AVAILABLE = True
except ImportError:
    # Define fallback classes when Plotly is not available
    class MockPx:
        @staticmethod
        def bar(*args, **kwargs):
            raise ImportError("Plotly not available")


    class MockGo:
        class Figure:
            def __init__(self, *args, **kwargs):
                raise ImportError("Plotly not available")

        class Indicator:
            def __init__(self, *args, **kwargs):
                pass


    px = MockPx()
    go = MockGo()
    PLOTLY_AVAILABLE = False

# Import the CSS handler with error handling
try:
    from css_handler import (
        load_cross_browser_css,
        create_safe_chart_container,
        create_safe_metrics,
        create_safe_summary_box,
        create_safe_download_button,
        get_plotly_light_theme,
        get_plotly_dark_theme,
        apply_cross_browser_fixes,
        initialize_cross_browser_support
    )

    CSS_HANDLER_AVAILABLE = True
except ImportError:
    CSS_HANDLER_AVAILABLE = False


    # Define fallback functions
    def load_cross_browser_css():
        return False


    def create_safe_chart_container(content_func, is_light_mode=True):
        content_func()


    def create_safe_metrics(value, label, is_light_mode=True):
        st.metric(label, value)


    def create_safe_summary_box(summary_text, is_light_mode=True):
        st.info(summary_text)


    def create_safe_download_button(label, data, filename, mime_type="text/plain", help_text=None):
        st.download_button(label, data, filename, mime_type, help=help_text)


    def get_plotly_light_theme():
        return {}


    def get_plotly_dark_theme():
        return {}


    def apply_cross_browser_fixes():
        pass


    def initialize_cross_browser_support():
        return False


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
    """Generate word frequency chart using Plotly with cross-browser compatibility"""
    if not PLOTLY_AVAILABLE:
        st.info("📊 Install Plotly for interactive visualizations: pip install plotly")
        return

    try:
        from collections import Counter
        import re
        import numpy as np

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

        words_list, frequencies = zip(*word_freq)

        # Check if we're in light mode (dark mode is now default)
        is_light_mode = st.session_state.get("light_mode", False)

        # Create interactive bar chart with cross-browser compatibility
        fig = px.bar(
            x=list(frequencies),
            y=list(words_list),
            orientation='h',
            title="Top 15 Most Frequent Words",
            labels={'x': 'Frequency', 'y': 'Words'},
            color=list(frequencies),
            color_continuous_scale='Greens' if is_light_mode else 'Viridis'
        )

        # Apply cross-browser compatible theme
        if is_light_mode:
            theme_config = get_plotly_light_theme()
            fig.update_layout(**theme_config['layout'])
            fig.update_layout(
                title_font_color='#059669',
                yaxis={'categoryorder': 'total ascending'},
                height=500,
                title_x=0.5,
                title_font_size=18,
                title_font_weight='bold'
            )
        else:
            theme_config = get_plotly_dark_theme()
            fig.update_layout(**theme_config['layout'])
            fig.update_layout(
                title_font_color='white',
                yaxis={'categoryorder': 'total ascending'},
                height=500,
                title_x=0.5,
                title_font_size=18,
                title_font_weight='bold'
            )

        # Use safe chart container
        def create_bar_chart():
            st.plotly_chart(fig, use_container_width=True)

        create_safe_chart_container(create_bar_chart, is_light_mode)

        # Word frequency bubble chart
        st.markdown("##### Word Frequency Bubble Chart")

        # Create positions for bubbles
        n_words = len(words_list)
        grid_size = int(np.ceil(np.sqrt(n_words)))

        # Create grid positions with some randomness
        positions_x = []
        positions_y = []

        for i in range(n_words):
            row = i // grid_size
            col = i % grid_size
            # Add jitter for organic look
            x_pos = col + np.random.uniform(-0.3, 0.3)
            y_pos = row + np.random.uniform(-0.3, 0.3)
            positions_x.append(x_pos)
            positions_y.append(y_pos)

        # Create bubble chart
        fig2 = go.Figure()

        # Use appropriate colors based on theme
        if is_light_mode:
            bubble_colors = [f'rgba({34 + min(i * 15, 100)}, {197 - min(i * 10, 80)}, {94 + min(i * 5, 50)}, 0.8)'
                             for i in range(len(frequencies))]
            line_color = 'rgba(22, 163, 74, 0.8)'
            text_color = '#166534'
        else:
            bubble_colors = list(frequencies)
            line_color = 'rgba(255,255,255,0.8)'
            text_color = 'white'

        fig2.add_trace(go.Scatter(
            x=positions_x,
            y=positions_y,
            mode='markers+text',
            marker=dict(
                size=[freq * 6 + 25 for freq in frequencies],
                color=bubble_colors,
                colorscale='Greens' if is_light_mode else 'Viridis',
                showscale=not is_light_mode,
                colorbar=dict(title="Frequency") if not is_light_mode else None,
                line=dict(width=2, color=line_color),
                opacity=0.8
            ),
            text=list(words_list),
            textposition="middle center",
            textfont=dict(
                size=[min(18, 10 + freq * 2) for freq in frequencies],
                color=text_color
            ),
            hovertemplate="<b>%{text}</b><br>Frequency: %{marker.color}<extra></extra>",
            showlegend=False
        ))

        # Apply theme to bubble chart
        if is_light_mode:
            theme_config = get_plotly_light_theme()
            fig2.update_layout(**theme_config['layout'])
            fig2.update_layout(title_font_color='#059669')
        else:
            theme_config = get_plotly_dark_theme()
            fig2.update_layout(**theme_config['layout'])
            fig2.update_layout(title_font_color='white')

        fig2.update_layout(
            title="Word Frequency Bubble Visualization",
            title_font_size=18,
            title_font_weight='bold',
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                range=[-1, grid_size]
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                range=[-1, grid_size]
            ),
            height=500,
            showlegend=False
        )

        # Use safe chart container for bubble chart
        def create_bubble_chart():
            st.plotly_chart(fig2, use_container_width=True)

        create_safe_chart_container(create_bubble_chart, is_light_mode)

    except Exception as e:
        st.error(f"Visualization error: {e}")
        st.info("Unable to generate visualizations. Please check if all dependencies are installed.")


def load_css():
    """Load custom CSS for the professional landing page"""
    # Initialize cross-browser support if available
    if CSS_HANDLER_AVAILABLE:
        initialize_cross_browser_support()

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
                <span> 🧠 Smart Research Summarizer</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_landing_page():
    """Render the landing page using pure Streamlit components"""

    # Show status messages only for critical errors
    if not PDF_AVAILABLE:
        st.error("⚠️ PDF processing is currently unavailable. Please install PyMuPDF.")
        st.code("pip install PyMuPDF", language="bash")

    if not NLTK_AVAILABLE:
        st.warning("⚠️ NLTK not available. Install for better text processing.")
        st.code("pip install nltk", language="bash")

    if not PLOTLY_AVAILABLE:
        st.warning("⚠️ Plotly not available. Install for interactive visualizations.")
        st.code("pip install plotly", language="bash")

    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-badge"> AI-Powered Research Analysis with Interactive Visualizations</div>
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
        if st.button("Start Analyzing", key="main_cta", use_container_width=True):
            st.session_state.show_app = True
            # Set dark mode as default when entering the app
            st.session_state.light_mode = False  # Ensures dark mode loads first
            st.rerun()

    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

    # Features Section
    st.markdown("## 🌟 Key Features")

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
            <a href="https://www.linkedin.com/in/ritika-yadav-b27344286/" target="_blank" class="linkedin-link">Connect on LinkedIn</a>
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

    # Ensure dark mode is default when app loads
    if "light_mode" not in st.session_state:
        st.session_state.light_mode = False  # Dark mode default

    # Theme handling - Dark mode is now default
    if THEME_AVAILABLE:
        create_theme_toggle()
        apply_theme_styles()
    else:
        col1, col2 = st.columns([9, 1])
        with col2:
            st.markdown("### ")
            if st.toggle("☀️", value=st.session_state.light_mode, help="Toggle Light/Dark Mode"):
                st.session_state.light_mode = True
            else:
                st.session_state.light_mode = False

    # Back button
    if st.button("← Back to Landing Page", key="back_to_landing"):
        st.session_state.show_app = False
        st.rerun()

    # App Title
    st.title("🧠 Smart Research Summarizer")

    # Simple status - removed all the extra text
    st.markdown("### Upload a PDF research paper for AI analysis")

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

        show_graphs = st.checkbox("Generate Visualizations", value=PLOTLY_AVAILABLE,
                                  disabled=not PLOTLY_AVAILABLE,
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

                # Apply appropriate styling based on theme for text area
                is_light_mode = st.session_state.get("light_mode", False)
                if not is_light_mode:  # Dark mode
                    st.markdown("""
                    <style>
                    .stTextArea textarea {
                        background: rgba(30, 41, 59, 0.8) !important;
                        border: 1px solid rgba(6, 182, 212, 0.3) !important;
                        border-radius: 10px !important;
                        color: white !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <style>
                    .stTextArea textarea {
                        background-color: #ffffff !important;
                        border: 2px solid #e5e7eb !important;
                        border-radius: 8px !important;
                        color: #111827 !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                st.text_area("", value=preview_text, height=200, disabled=True)

            # Document stats with cross-browser safe styling
            word_count = len(full_text.split())
            char_count = len(full_text)
            estimated_read_time = max(1, round(word_count / 250))

            # Use cross-browser safe metrics
            is_light_mode = st.session_state.get("light_mode", False)

            col1, col2, col3 = st.columns(3)
            with col1:
                create_safe_metrics(f"{word_count:,}", "Word Count", is_light_mode)
            with col2:
                create_safe_metrics(f"{char_count:,}", "Characters", is_light_mode)
            with col3:
                create_safe_metrics(f"{estimated_read_time}", "Est. Read Time (min)", is_light_mode)

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

                            success_msg = f" {summary_length} summary generated!"
                            if show_graphs:
                                success_msg += " Visualizations created!"
                            st.success(success_msg)

                            # Summary stats with cross-browser safe styling
                            summary_word_count = len(summary.split())
                            compression_ratio = round((1 - summary_word_count / word_count) * 100)

                            # Use cross-browser safe summary metrics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                create_safe_metrics(f"{summary_word_count}", "Summary Words", is_light_mode)
                            with col2:
                                create_safe_metrics(f"{compression_ratio}%", "Compression", is_light_mode)
                            with col3:
                                create_safe_metrics(f"{summary_length}", "Summary Type", is_light_mode)

                            # Display summary with cross-browser safe styling
                            st.markdown("#### 📝 Generated Summary")
                            create_safe_summary_box(summary, is_light_mode)

                            # Show visualizations if enabled
                            if show_graphs and PLOTLY_AVAILABLE:
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
                                        # Summary comparison chart with cross-browser safe styling
                                        fig_comparison = px.bar(
                                            x=['Original Document', 'Generated Summary'],
                                            y=[word_count, summary_word_count],
                                            title="Word Count Comparison",
                                            color=['Original Document', 'Generated Summary'],
                                            color_discrete_sequence=['#22c55e', '#16a34a'] if is_light_mode else [
                                                '#06b6d4', '#10b981']
                                        )

                                        # Apply theme configuration
                                        if is_light_mode:
                                            theme_config = get_plotly_light_theme()
                                            fig_comparison.update_layout(**theme_config['layout'])
                                            fig_comparison.update_layout(
                                                title_font_color='#16a34a',
                                                showlegend=False
                                            )
                                        else:
                                            theme_config = get_plotly_dark_theme()
                                            fig_comparison.update_layout(**theme_config['layout'])
                                            fig_comparison.update_layout(
                                                title_font_color='white',
                                                showlegend=False
                                            )

                                        # Use safe chart container
                                        def create_comparison_chart():
                                            st.plotly_chart(fig_comparison, use_container_width=True)

                                        create_safe_chart_container(create_comparison_chart, is_light_mode)

                                        # Compression gauge
                                        fig_gauge = go.Figure(go.Indicator(
                                            mode="gauge+number+delta",
                                            value=compression_ratio,
                                            domain={'x': [0, 1], 'y': [0, 1]},
                                            title={'text': "Compression Efficiency %"},
                                            delta={'reference': 50},
                                            gauge={
                                                'axis': {'range': [None, 100]},
                                                'bar': {'color': "#22c55e" if is_light_mode else "#06b6d4"},
                                                'steps': [
                                                    {'range': [0, 25], 'color': "#fca5a5"},
                                                    {'range': [25, 50], 'color': "#fde047"},
                                                    {'range': [50, 75], 'color': "#86efac"},
                                                    {'range': [75, 100],
                                                     'color': "#22c55e" if is_light_mode else "#06b6d4"}
                                                ],
                                                'threshold': {
                                                    'line': {'color': "#374151" if is_light_mode else "white",
                                                             'width': 4},
                                                    'thickness': 0.75,
                                                    'value': 80
                                                }
                                            }
                                        ))

                                        # Apply theme to gauge
                                        if is_light_mode:
                                            theme_config = get_plotly_light_theme()
                                            fig_gauge.update_layout(**theme_config['layout'])
                                        else:
                                            theme_config = get_plotly_dark_theme()
                                            fig_gauge.update_layout(**theme_config['layout'])

                                        fig_gauge.update_layout(height=400)

                                        # Use safe chart container for gauge
                                        def create_gauge_chart():
                                            st.plotly_chart(fig_gauge, use_container_width=True)

                                        create_safe_chart_container(create_gauge_chart, is_light_mode)

                                        # Reading time comparison with cross-browser safe metrics
                                        original_read_time = max(1, round(word_count / 250))
                                        summary_read_time = max(1, round(summary_word_count / 250))
                                        time_saved = max(0, original_read_time - summary_read_time)

                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            create_safe_metrics(f"{original_read_time}", "Original Read Time (min)",
                                                                is_light_mode)
                                        with col2:
                                            create_safe_metrics(f"{summary_read_time}", "Summary Read Time (min)",
                                                                is_light_mode)
                                        with col3:
                                            create_safe_metrics(f"{time_saved}", "Time Saved (min)", is_light_mode)

                                    except Exception as e:
                                        st.warning(f"Advanced visualization error: {e}")

                            elif show_graphs and not PLOTLY_AVAILABLE:
                                st.info("📈 Install Plotly for advanced visualizations: pip install plotly")

                            # Download section with cross-browser safe styling
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
Visualizations: {'Enabled' if show_graphs and PLOTLY_AVAILABLE else 'Disabled'}

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
                                create_safe_download_button(
                                    "📥 Download Complete Report",
                                    download_content,
                                    filename,
                                    "text/plain",
                                    "Download summary with metadata and statistics"
                                )

                        except Exception as e:
                            st.error(f"❌ Error generating summary: {str(e)}")
                            st.info("Please try again or check if all dependencies are installed.")

        except Exception as e:
            st.error(f"❌ Error processing PDF: {str(e)}")
            st.info("Please try uploading a different PDF file.")

    else:
        # Welcome section
        st.markdown("###  Welcome to Smart Research Summarizer!")
        st.markdown("Get started by uploading a PDF research paper above.")

        # Simplified info about features - removed all the status text
        info_text = f"""
**📊 Summary Options:**

• **Short:** Quick insights (~5 sentences)

• **Medium:** Balanced overview (~8 sentences) 

• **Long:** Comprehensive summary (~12 sentences)

**📈 Available Features:**

• **Word Frequency Charts:** Interactive bar and bubble charts

• **Summary Statistics:** Compression metrics and analytics

• **Export Options:** Download reports with full analysis
        """
        st.info(info_text)

        # Installation help - only show if dependencies are missing
        missing_deps = []
        if not PDF_AVAILABLE:
            missing_deps.append("pip install PyMuPDF")
        if not NLTK_AVAILABLE:
            missing_deps.append("pip install nltk")
        if not PLOTLY_AVAILABLE:
            missing_deps.append("pip install plotly")

        if missing_deps:
            st.markdown("#### 🔧 Setup Instructions")
            for dep in missing_deps:
                st.code(dep, language="bash")

    # Simplified footer - removed cross-browser text
    st.markdown(f"""
    <div style="text-align: center; margin-top: 50px; padding: 20px; color: white; border-top: 1px solid #4a5568;">
        <p style="margin: 0; font-size: 12px; font-weight: 500;">© 2025 Smart Research Summarizer. All rights reserved.</p>
        <p style="margin: 5px 0 0 0; font-size: 10px;">AI-Powered Analysis with Interactive Visualizations</p>
        <p style="margin: 5px 0 0 0; font-size: 10px;">
            <a href="https://www.linkedin.com/in/ritika-yadav-b27344286/" target="_blank" class="linkedin-link">Connect on LinkedIn</a>
        </p>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="🧠 Smart Research Summarizer",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Initialize session state - Dark mode is now default
    if 'show_app' not in st.session_state:
        st.session_state.show_app = False
    if 'light_mode' not in st.session_state:
        st.session_state.light_mode = False  # Dark mode default

    # Load CSS with cross-browser support
    load_css()
    render_streamlit_navbar()

    # Simplified sidebar - removed cross-browser status messages
    if CSS_HANDLER_AVAILABLE:
        st.sidebar.success(" Enhanced styling active")
        st.sidebar.markdown("**Cross-browser compatibility enabled**")
    else:
        st.sidebar.info("📝 Using standard styling")

    # Route to appropriate page
    if st.session_state.show_app:
        try:
            with st.spinner(" Loading Smart Research Summarizer..."):
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