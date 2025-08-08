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
    """Generate word frequency chart using Plotly with improved text visibility"""
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

        # Create interactive bar chart with improved text visibility
        fig = px.bar(
            x=list(frequencies),
            y=list(words_list),
            orientation='h',
            title="Top 15 Most Frequent Words",
            labels={'x': 'Frequency', 'y': 'Words'},
            color=list(frequencies),
            color_continuous_scale='Greens'
        )

        # Improved layout with better text contrast
        fig.update_layout(
            paper_bgcolor='rgba(15, 27, 15, 0.9)',
            plot_bgcolor='rgba(15, 27, 15, 0.9)',
            title_font_color='#22c55e',
            title_font_size=20,
            title_font_weight='bold',
            yaxis={
                'categoryorder': 'total ascending',
                'tickfont': {'color': '#f8fafc', 'size': 14},
                'title': {'text': 'Words', 'font': {'color': '#f8fafc', 'size': 16}}
            },
            xaxis={
                'tickfont': {'color': '#f8fafc', 'size': 14},
                'title': {'text': 'Frequency', 'font': {'color': '#f8fafc', 'size': 16}}
            },
            height=500,
            title_x=0.5,
            font=dict(color='#f8fafc'),
            margin=dict(l=120, r=50, t=80, b=50)
        )

        # Update traces for better visibility
        fig.update_traces(
            textfont_color='#f8fafc',
            textposition='outside',
            marker_line_color='#22c55e',
            marker_line_width=1
        )

        st.plotly_chart(fig, use_container_width=True)

        # Word frequency bubble chart with improved text visibility
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

        # Improved colors and text visibility
        bubble_colors = [f'rgba({34 + min(i * 15, 100)}, {197 - min(i * 10, 80)}, {94 + min(i * 5, 50)}, 0.9)'
                         for i in range(len(frequencies))]
        line_color = '#22c55e'
        text_color = '#ffffff'  # Changed to white for better visibility

        fig2.add_trace(go.Scatter(
            x=positions_x,
            y=positions_y,
            mode='markers+text',
            marker=dict(
                size=[freq * 6 + 25 for freq in frequencies],
                color=bubble_colors,
                line=dict(width=3, color=line_color),
                opacity=0.8
            ),
            text=list(words_list),
            textposition="middle center",
            textfont=dict(
                size=[min(20, 12 + freq * 2) for freq in frequencies],
                color=text_color,
                family="Arial Black"  # Bold font for better visibility
            ),
            hovertemplate="<b>%{text}</b><br>Frequency: %{customdata}<extra></extra>",
            customdata=frequencies,
            showlegend=False
        ))

        # Improved layout for bubble chart
        fig2.update_layout(
            paper_bgcolor='rgba(15, 27, 15, 0.9)',
            plot_bgcolor='rgba(15, 27, 15, 0.9)',
            title="Word Frequency Bubble Visualization",
            title_font_size=20,
            title_font_weight='bold',
            title_font_color='#22c55e',
            title_x=0.5,
            font=dict(color='#f8fafc'),
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
            showlegend=False,
            margin=dict(l=50, r=50, t=80, b=50)
        )

        st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"Visualization error: {e}")
        st.info("Unable to generate visualizations. Please check if all dependencies are installed.")


def load_css():
    """Load custom CSS for light mode with enhanced nebula effect"""
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

        /* Enhanced nebula background with green theme */
        .stApp {
            background: linear-gradient(135deg, #0a0f0c 0%, #1a2e1a 25%, #0f1b0f 50%, #1a2e1a 75%, #0a0f0c 100%) !important;
            background-size: 400% 400% !important;
            animation: cosmic-drift 25s ease infinite;
            min-height: 100vh !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            position: relative;
            overflow-x: hidden;
            color: #e2e8f0 !important;
        }

        /* Force override system colors */
        .stApp, .stApp * {
            color-scheme: dark !important;
        }

        @keyframes cosmic-drift {
            0% { background-position: 0% 50%; }
            25% { background-position: 100% 25%; }
            50% { background-position: 50% 100%; }
            75% { background-position: 25% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Multi-layered nebula effects */
        .stApp::before {
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background-image: 
                /* Core nebula */
                radial-gradient(ellipse 1200px 800px at 20% 30%, 
                    rgba(34, 197, 94, 0.4) 0%, 
                    rgba(16, 185, 129, 0.3) 20%, 
                    rgba(34, 197, 94, 0.2) 40%, 
                    rgba(22, 163, 74, 0.15) 60%, 
                    rgba(5, 150, 105, 0.1) 80%, 
                    transparent 100%),
                /* Secondary nebula */
                radial-gradient(ellipse 1000px 1200px at 80% 70%, 
                    rgba(22, 163, 74, 0.35) 0%, 
                    rgba(34, 197, 94, 0.25) 25%, 
                    rgba(16, 185, 129, 0.2) 50%, 
                    rgba(5, 150, 105, 0.12) 75%, 
                    transparent 90%),
                /* Accent nebula */
                radial-gradient(ellipse 800px 600px at 50% 20%, 
                    rgba(16, 185, 129, 0.3) 0%, 
                    rgba(34, 197, 94, 0.2) 30%, 
                    rgba(22, 163, 74, 0.15) 60%, 
                    transparent 85%),
                /* Distant nebula */
                radial-gradient(ellipse 1500px 900px at 70% 90%, 
                    rgba(5, 150, 105, 0.2) 0%, 
                    rgba(34, 197, 94, 0.15) 35%, 
                    rgba(16, 185, 129, 0.1) 70%, 
                    transparent 95%);
            animation: nebula-flow 35s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
            filter: blur(1px);
        }

        @keyframes nebula-flow {
            0%, 100% { 
                transform: translateX(0) translateY(0) rotate(0deg) scale(1);
                opacity: 0.8;
            }
            25% { 
                transform: translateX(-30px) translateY(-40px) rotate(-2deg) scale(1.05);
                opacity: 0.9;
            }
            50% { 
                transform: translateX(25px) translateY(-20px) rotate(1deg) scale(0.95);
                opacity: 0.85;
            }
            75% { 
                transform: translateX(-15px) translateY(30px) rotate(-1deg) scale(1.02);
                opacity: 0.88;
            }
        }

        /* Additional nebula layer for depth */
        .stApp::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image:
                /* Scattered stars/particles */
                radial-gradient(circle at 15% 25%, rgba(34, 197, 94, 0.8) 0px, transparent 2px),
                radial-gradient(circle at 85% 15%, rgba(16, 185, 129, 0.6) 0px, transparent 1px),
                radial-gradient(circle at 35% 75%, rgba(22, 163, 74, 0.7) 0px, transparent 1.5px),
                radial-gradient(circle at 75% 85%, rgba(5, 150, 105, 0.5) 0px, transparent 1px),
                radial-gradient(circle at 55% 35%, rgba(34, 197, 94, 0.4) 0px, transparent 1px),
                radial-gradient(circle at 25% 65%, rgba(16, 185, 129, 0.6) 0px, transparent 1px),
                /* Subtle dust clouds */
                radial-gradient(ellipse 400px 200px at 60% 40%, rgba(34, 197, 94, 0.08) 0%, transparent 70%),
                radial-gradient(ellipse 300px 400px at 30% 80%, rgba(22, 163, 74, 0.06) 0%, transparent 80%);
            animation: stellar-twinkle 20s linear infinite;
            pointer-events: none;
            z-index: 1;
        }

        @keyframes stellar-twinkle {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
        }

        /* TOP NAVBAR STYLES with nebula integration */
        .top-navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, 
                rgba(10, 15, 12, 0.95) 0%, 
                rgba(26, 46, 26, 0.9) 50%, 
                rgba(15, 27, 15, 0.85) 100%) !important;
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(34, 197, 94, 0.3);
            box-shadow: 0 4px 25px rgba(34, 197, 94, 0.2);
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
            font-size: 1.8rem !important;
            font-weight: 900 !important;
            background: linear-gradient(135deg, #22c55e, #16a34a, #059669) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
            display: flex;
            align-items: center;
            gap: 0.7rem;
            text-shadow: 0 0 20px rgba(34, 197, 94, 0.3);
            color: #22c55e !important;
        }

        .nav-brand-icon {
            font-size: 2rem !important;
            animation: logo-nebula-glow 3s ease-in-out infinite;
            filter: drop-shadow(0 0 10px rgba(34, 197, 94, 0.6));
            color: #22c55e !important;
        }

        @keyframes logo-nebula-glow {
            0%, 100% { 
                transform: scale(1);
                filter: drop-shadow(0 0 10px rgba(34, 197, 94, 0.6));
            }
            50% { 
                transform: scale(1.1);
                filter: drop-shadow(0 0 20px rgba(34, 197, 94, 0.8));
            }
        }

        /* Add top margin to main content */
        .stApp > div:first-child {
            margin-top: 80px;
        }

        /* Hero section with nebula enhancement */
        .hero-section {
            text-align: center;
            padding: 4rem 0;
            position: relative;
            z-index: 2;
            margin-top: 2rem;
        }

        .hero-badge {
            display: inline-block;
            padding: 0.75rem 2rem !important;
            background: rgba(34, 197, 94, 0.15) !important;
            color: #22c55e !important;
            border-radius: 50px !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            margin-bottom: 2rem;
            border: 1px solid rgba(34, 197, 94, 0.4) !important;
            animation: nebula-pulse-glow 4s ease-in-out infinite;
            backdrop-filter: blur(10px);
        }

        @keyframes nebula-pulse-glow {
            0%, 100% { 
                box-shadow: 0 0 25px rgba(34, 197, 94, 0.4);
                transform: scale(1);
                border-color: rgba(34, 197, 94, 0.4);
            }
            50% { 
                box-shadow: 0 0 40px rgba(34, 197, 94, 0.7);
                transform: scale(1.05);
                border-color: rgba(34, 197, 94, 0.6);
            }
        }

        .main-title {
            font-size: clamp(3rem, 8vw, 5.5rem) !important;
            font-weight: 900 !important;
            color: #f8fafc !important;
            line-height: 1.1 !important;
            margin-bottom: 2rem !important;
            letter-spacing: -0.02em !important;
            text-shadow: 0 0 30px rgba(34, 197, 94, 0.3) !important;
        }

        .subtitle {
            font-size: clamp(1.2rem, 3vw, 1.8rem) !important;
            color: #e2e8f0 !important;
            font-weight: 500 !important;
            margin-bottom: 1.5rem !important;
            line-height: 1.4 !important;
            text-shadow: 0 0 15px rgba(34, 197, 94, 0.2) !important;
        }

        .description {
            font-size: clamp(1rem, 2.5vw, 1.3rem) !important;
            color: #cbd5e1 !important;
            margin-bottom: 3rem !important;
            line-height: 1.6 !important;
            max-width: 800px !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }

        /* UNIVERSAL FILE UPLOADER STYLING - WORKS ACROSS ALL BROWSERS AND THEMES */

        /* Target all possible file uploader elements */
        .stFileUploader,
        .stFileUploader > div,
        .stFileUploader > div > div,
        .stFileUploader section,
        .stFileUploader section > div,
        div[data-testid="stFileUploader"],
        div[data-testid="stFileUploader"] > div,
        div[data-testid="stFileUploader"] section,
        div[data-testid="stFileUploaderDropzone"],
        div[data-testid="stFileUploaderDropzoneInstructions"],
        [data-testid*="fileUploader"],
        [data-testid*="FileUploader"] {
            background: rgba(15, 27, 15, 0.95) !important;
            background-color: rgba(15, 27, 15, 0.95) !important;
            border: 2px dashed #22c55e !important;
            border-color: #22c55e !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            text-align: center !important;
            transition: all 0.3s ease !important;
            backdrop-filter: blur(10px) !important;
            color: #e2e8f0 !important;
            box-shadow: 0 4px 20px rgba(34, 197, 94, 0.2) !important;
            position: relative !important;
            overflow: hidden !important;
        }

        /* Force text color for all file uploader text elements */
        .stFileUploader label,
        .stFileUploader p,
        .stFileUploader span,
        .stFileUploader div,
        .stFileUploader small,
        div[data-testid="stFileUploader"] label,
        div[data-testid="stFileUploader"] p,
        div[data-testid="stFileUploader"] span,
        div[data-testid="stFileUploader"] div,
        div[data-testid="stFileUploader"] small,
        div[data-testid="stFileUploaderDropzoneInstructions"] *,
        [data-testid*="fileUploader"] *,
        [data-testid*="FileUploader"] * {
            color: #e2e8f0 !important;
            font-weight: 500 !important;
            font-size: 1.1rem !important;
            text-shadow: 0 0 10px rgba(34, 197, 94, 0.3) !important;
        }

        /* Specific targeting for drag and drop text */
        .stFileUploader [class*="drag"],
        .stFileUploader [class*="drop"],
        div[data-testid="stFileUploader"] [class*="drag"],
        div[data-testid="stFileUploader"] [class*="drop"],
        div[data-testid="stFileUploaderDropzoneInstructions"],
        div[data-testid="stFileUploaderDropzoneInstructions"] > *,
        [data-testid*="fileUploader"] [class*="drag"],
        [data-testid*="fileUploader"] [class*="drop"] {
            color: #e2e8f0 !important;
            background: transparent !important;
            font-weight: 600 !important;
            font-size: 1.2rem !important;
            text-shadow: 0 0 15px rgba(34, 197, 94, 0.4) !important;
        }

        /* File uploader button styling */
        .stFileUploader button,
        .stFileUploader input[type="file"],
        div[data-testid="stFileUploader"] button,
        div[data-testid="stFileUploader"] input[type="file"],
        [data-testid*="fileUploader"] button,
        [data-testid*="FileUploader"] button {
            background: linear-gradient(135deg, #059669, #16a34a) !important;
            background-color: #059669 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3) !important;
        }

        .stFileUploader button:hover,
        div[data-testid="stFileUploader"] button:hover,
        [data-testid*="fileUploader"] button:hover {
            background: linear-gradient(135deg, #047857, #15803d) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(34, 197, 94, 0.4) !important;
        }

        /* File uploader hover effects */
        .stFileUploader:hover,
        div[data-testid="stFileUploader"]:hover,
        [data-testid*="fileUploader"]:hover {
            background: rgba(15, 27, 15, 0.98) !important;
            border-color: #16a34a !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(34, 197, 94, 0.4) !important;
        }

        /* Override any system/browser default styling */
        .stFileUploader *,
        div[data-testid="stFileUploader"] *,
        [data-testid*="fileUploader"] *,
        [data-testid*="FileUploader"] * {
            color: #e2e8f0 !important;
            background-color: transparent !important;
        }

        /* Force override for webkit browsers */
        @media screen and (-webkit-min-device-pixel-ratio:0) {
            .stFileUploader,
            div[data-testid="stFileUploader"],
            [data-testid*="fileUploader"] {
                background: rgba(15, 27, 15, 0.95) !important;
                border: 2px dashed #22c55e !important;
                color: #e2e8f0 !important;
            }
        }

        /* Firefox specific overrides */
        @-moz-document url-prefix() {
            .stFileUploader,
            div[data-testid="stFileUploader"],
            [data-testid*="fileUploader"] {
                background: rgba(15, 27, 15, 0.95) !important;
                border: 2px dashed #22c55e !important;
                color: #e2e8f0 !important;
            }
        }

        /* Edge specific overrides */
        @supports (-ms-ime-align: auto) {
            .stFileUploader,
            div[data-testid="stFileUploader"],
            [data-testid*="fileUploader"] {
                background: rgba(15, 27, 15, 0.95) !important;
                border: 2px dashed #22c55e !important;
                color: #e2e8f0 !important;
            }
        }

        /* Force dark color scheme for file uploader area */
        .stFileUploader,
        div[data-testid="stFileUploader"],
        [data-testid*="fileUploader"] {
            color-scheme: dark !important;
            -webkit-color-scheme: dark !important;
        }

        /* Text colors for dark nebula theme - FORCED OVERRIDES */
        h1, h1 *, 
        h2, h2 *, 
        h3, h3 *, 
        h4, h4 *, 
        h5, h5 *, 
        h6, h6 * {
            color: #f8fafc !important;
            text-shadow: 0 0 10px rgba(34, 197, 94, 0.2) !important;
        }

        p, p *,
        div, 
        span, span *,
        li, li *,
        label, label *,
        small, small * {
            color: #e2e8f0 !important;
        }

        .stMarkdown, 
        .stMarkdown *,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] * {
            color: #e2e8f0 !important;
        }

        /* Enhanced button styling with nebula glow */
        .stButton > button {
            background: linear-gradient(135deg, #059669 0%, #16a34a 50%, #22c55e 100%) !important;
            border: none !important;
            color: white !important;
            padding: 1.25rem 3rem !important;
            border-radius: 16px !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            transition: all 0.4s ease !important;
            box-shadow: 0 10px 40px rgba(34, 197, 94, 0.4) !important;
            min-width: 250px !important;
            height: 60px !important;
            position: relative !important;
            overflow: hidden !important;
        }

        .stButton > button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }

        .stButton > button:hover::before {
            left: 100%;
        }

        .stButton > button:hover {
            transform: translateY(-3px) scale(1.05) !important;
            box-shadow: 0 15px 60px rgba(34, 197, 94, 0.6) !important;
        }

        /* Cards and feature styling with nebula integration */
        .feature-card {
            background: rgba(15, 27, 15, 0.8) !important;
            backdrop-filter: blur(15px);
            border-radius: 20px !important;
            padding: 2rem !important;
            border: 1px solid rgba(34, 197, 94, 0.3) !important;
            transition: all 0.4s ease;
            text-align: center;
            height: 100%;
            position: relative;
            z-index: 2;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3) !important;
        }

        .feature-card:hover {
            background: rgba(15, 27, 15, 0.9) !important;
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(34, 197, 94, 0.3) !important;
            border-color: rgba(34, 197, 94, 0.5) !important;
        }

        .feature-icon {
            font-size: 3rem !important;
            margin-bottom: 1rem !important;
            display: block !important;
            filter: drop-shadow(0 0 10px rgba(34, 197, 94, 0.4));
            color: #22c55e !important;
        }

        .feature-title {
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            color: #22c55e !important;
            margin-bottom: 1rem !important;
            text-shadow: 0 0 10px rgba(34, 197, 94, 0.3) !important;
        }

        .feature-text {
            color: #cbd5e1 !important;
            line-height: 1.6 !important;
        }

        /* LinkedIn link styling */
        .linkedin-link {
            color: #22c55e !important;
            text-decoration: none !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }

        .linkedin-link:hover {
            color: #16a34a !important;
            text-decoration: underline !important;
            text-shadow: 0 0 5px rgba(34, 197, 94, 0.5) !important;
        }

        /* Text area styling for nebula theme */
        .stTextArea textarea {
            background-color: rgba(15, 27, 15, 0.8) !important;
            border: 2px solid rgba(34, 197, 94, 0.3) !important;
            border-radius: 8px !important;
            color: #e2e8f0 !important;
            backdrop-filter: blur(10px) !important;
        }

        .stTextArea textarea:focus {
            border-color: #22c55e !important;
            box-shadow: 0 0 15px rgba(34, 197, 94, 0.3) !important;
        }

        /* Metrics styling with nebula glow */
        .metric-container {
            background: rgba(15, 27, 15, 0.8) !important;
            border: 1px solid rgba(34, 197, 94, 0.3) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            text-align: center !important;
            transition: all 0.3s ease !important;
            backdrop-filter: blur(10px) !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        }

        .metric-container:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(34, 197, 94, 0.3) !important;
            border-color: rgba(34, 197, 94, 0.5) !important;
        }

        /* Summary box styling with nebula theme */
        .summary-box {
            background: rgba(15, 27, 15, 0.9) !important;
            border: 2px solid rgba(34, 197, 94, 0.4) !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            margin: 1rem 0 !important;
            box-shadow: 0 8px 25px rgba(34, 197, 94, 0.2) !important;
            backdrop-filter: blur(15px) !important;
        }

        /* Selectbox and radio button styling */
        .stSelectbox > div > div {
            background-color: rgba(15, 27, 15, 0.8) !important;
            border-color: rgba(34, 197, 94, 0.3) !important;
            color: #e2e8f0 !important;
        }

        .stRadio > div {
            background-color: rgba(15, 27, 15, 0.3) !important;
            border-radius: 8px !important;
            padding: 0.5rem !important;
        }

        .stRadio label {
            color: #e2e8f0 !important;
        }

        /* Checkbox styling */
        .stCheckbox > label {
            color: #e2e8f0 !important;
        }

        /* Info/warning/error boxes with nebula theme */
        .stAlert {
            background-color: rgba(15, 27, 15, 0.8) !important;
            border: 1px solid rgba(34, 197, 94, 0.3) !important;
            backdrop-filter: blur(10px) !important;
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: rgba(15, 27, 15, 0.8) !important;
            border: 1px solid rgba(34, 197, 94, 0.3) !important;
            color: #e2e8f0 !important;
        }

        .streamlit-expanderContent {
            background-color: rgba(15, 27, 15, 0.9) !important;
            border: 1px solid rgba(34, 197, 94, 0.2) !important;
        }

        /* Sidebar styling */
        .css-1d391kg {
            background-color: rgba(10, 15, 12, 0.95) !important;
            border-right: 1px solid rgba(34, 197, 94, 0.3) !important;
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            background-color: rgba(15, 27, 15, 0.8) !important;
            border-radius: 8px !important;
        }

        .stTabs [data-baseweb="tab"] {
            color: #e2e8f0 !important;
            background-color: transparent !important;
        }

        .stTabs [aria-selected="true"] {
            background-color: rgba(34, 197, 94, 0.2) !important;
            color: #22c55e !important;
        }

        /* Progress bar styling */
        .stProgress .st-bo {
            background-color: rgba(34, 197, 94, 0.3) !important;
        }

        /* Spinner styling */
        .stSpinner > div {
            border-top-color: #22c55e !important;
        }

        /* Success/error message styling */
        .stSuccess {
            background-color: rgba(34, 197, 94, 0.1) !important;
            border: 1px solid rgba(34, 197, 94, 0.3) !important;
            color: #22c55e !important;
        }

        .stError {
            background-color: rgba(239, 68, 68, 0.1) !important;
            border: 1px solid rgba(239, 68, 68, 0.3) !important;
            color: #ef4444 !important;
        }

        .stWarning {
            background-color: rgba(245, 158, 11, 0.1) !important;
            border: 1px solid rgba(245, 158, 11, 0.3) !important;
            color: #f59e0b !important;
        }

        .stInfo {
            background-color: rgba(34, 197, 94, 0.1) !important;
            border: 1px solid rgba(34, 197, 94, 0.3) !important;
            color: #22c55e !important;
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
            .nav-brand {
                font-size: 1.6rem !important;
            }
            .stButton > button {
                min-width: 200px !important;
                padding: 1rem 2rem !important;
            }

            /* Mobile nebula adjustments */
            .stApp::before {
                background-size: 150% 150%;
            }

            /* Mobile file uploader */
            .stFileUploader,
            div[data-testid="stFileUploader"],
            [data-testid*="fileUploader"] {
                padding: 1.5rem !important;
                font-size: 0.9rem !important;
            }
        }

        /* Floating particles animation */
        @keyframes float-particles {
            0%, 100% {
                transform: translateY(0px) translateX(0px);
                opacity: 0.7;
            }
            50% {
                transform: translateY(-20px) translateX(10px);
                opacity: 1;
            }
        }

        /* Additional nebula enhancement for landing page */
        .hero-section::before {
            content: '';
            position: absolute;
            top: -20%;
            left: -20%;
            width: 140%;
            height: 140%;
            background: radial-gradient(ellipse 600px 400px at 50% 50%, 
                rgba(34, 197, 94, 0.1) 0%, 
                rgba(22, 163, 74, 0.05) 50%, 
                transparent 80%);
            animation: hero-nebula-pulse 8s ease-in-out infinite;
            z-index: 1;
            pointer-events: none;
        }

        @keyframes hero-nebula-pulse {
            0%, 100% {
                opacity: 0.3;
                transform: scale(1);
            }
            50% {
                opacity: 0.6;
                transform: scale(1.1);
            }
        }

        /* Enhanced glow effects for interactive elements */
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 20px;
            padding: 1px;
            background: linear-gradient(45deg, 
                rgba(34, 197, 94, 0.3), 
                rgba(22, 163, 74, 0.2), 
                rgba(16, 185, 129, 0.3));
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: exclude;
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: -1;
        }

        .feature-card:hover::before {
            opacity: 1;
        }

        /* Additional file uploader enhancements for better cross-browser compatibility */
        .stFileUploader::before,
        div[data-testid="stFileUploader"]::before,
        [data-testid*="fileUploader"]::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(15, 27, 15, 0.95) !important;
            border-radius: 16px !important;
            z-index: -1;
        }

        /* Force text visibility in file uploader regardless of browser theme */
        .stFileUploader *::selection,
        div[data-testid="stFileUploader"] *::selection,
        [data-testid*="fileUploader"] *::selection {
            background: rgba(34, 197, 94, 0.3) !important;
            color: #f8fafc !important;
        }

        /* Webkit specific file input styling */
        .stFileUploader input[type="file"]::-webkit-file-upload-button,
        div[data-testid="stFileUploader"] input[type="file"]::-webkit-file-upload-button,
        [data-testid*="fileUploader"] input[type="file"]::-webkit-file-upload-button {
            background: linear-gradient(135deg, #059669, #16a34a) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            cursor: pointer !important;
        }

        /* Override any potential theme conflicts */
        html[data-theme="light"] .stFileUploader,
        html[data-theme="light"] div[data-testid="stFileUploader"],
        html[data-theme="dark"] .stFileUploader,
        html[data-theme="dark"] div[data-testid="stFileUploader"],
        [data-color-mode="light"] .stFileUploader,
        [data-color-mode="light"] div[data-testid="stFileUploader"],
        [data-color-mode="dark"] .stFileUploader,
        [data-color-mode="dark"] div[data-testid="stFileUploader"] {
            background: rgba(15, 27, 15, 0.95) !important;
            border: 2px dashed #22c55e !important;
            color: #e2e8f0 !important;
        }

        html[data-theme="light"] .stFileUploader *,
        html[data-theme="light"] div[data-testid="stFileUploader"] *,
        html[data-theme="dark"] .stFileUploader *,
        html[data-theme="dark"] div[data-testid="stFileUploader"] *,
        [data-color-mode="light"] .stFileUploader *,
        [data-color-mode="light"] div[data-testid="stFileUploader"] *,
        [data-color-mode="dark"] .stFileUploader *,
        [data-color-mode="dark"] div[data-testid="stFileUploader"] * {
            color: #e2e8f0 !important;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_streamlit_navbar():
    """Render navbar with enhanced nebula styling"""
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
    """Render the landing page with enhanced nebula effects"""

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

    # Hero Section with enhanced nebula effects
    st.markdown("""
    <div class="hero-section">
        <div class="hero-badge">AI-Powered Research Analysis with Interactive Visualizations</div>
        <h1 class="main-title">Smart Research Summarizer</h1>
        <p class="subtitle">Transform PDFs into intelligent summaries with stunning interactive charts</p>
        <div style="text-align: center; max-width: 800px; margin: 0 auto;">
            <p class="description">Upload any PDF research paper and get comprehensive summaries with beautiful interactive visualizations including word frequency charts, summary statistics, and data analytics powered by advanced AI models.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA Button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Start Analyzing", key="main_cta", use_container_width=True):
            st.session_state.show_app = True
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
            <p class="feature-text">Beautiful word frequency charts and summary analytics with hover effects, zoom, and export capabilities powered by advanced data visualization.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3 class="feature-title">AI-Powered Analysis</h3>
            <p class="feature-text">Advanced AI models extract key insights and findings from complex academic papers with precision using state-of-the-art NLP techniques.</p>
        </div>
        """, unsafe_allow_html=True)

    with feature_cols[1]:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <h3 class="feature-title">Smart Summarization</h3>
            <p class="feature-text">Choose from short, medium, or long summaries tailored to your needs with advanced text processing and intelligent content extraction.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💾</div>
            <h3 class="feature-title">Export & Download</h3>
            <p class="feature-text">Download complete analysis reports with metadata, statistics, and visualizations included for easy sharing and reference.</p>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #cbd5e1;">
        <p><strong>© 2025 Ritika Yadav Smart Research Summarizer. All rights reserved.</strong></p>
        <p style="margin: 1rem 0; font-size: 0.9rem;">Empowering research through AI and interactive visualization</p>
        <p style="margin: 0.5rem 0; font-size: 0.9rem;">
            <a href="https://www.linkedin.com/in/ritika-yadav-b27344286/" target="_blank" class="linkedin-link">Connect on LinkedIn</a>
        </p>
    </div>
    """, unsafe_allow_html=True)


def create_metrics(value, label):
    """Create styled metrics for nebula theme"""
    st.markdown(f"""
    <div class="metric-container">
        <div style="font-size: 2rem; font-weight: bold; color: #22c55e; margin-bottom: 0.5rem; text-shadow: 0 0 10px rgba(34, 197, 94, 0.3);">{value}</div>
        <div style="font-size: 0.9rem; color: #cbd5e1;">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def create_summary_box(summary_text):
    """Create styled summary box for nebula theme"""
    st.markdown(f"""
    <div class="summary-box">
        <div style="color: #e2e8f0; line-height: 1.6; font-size: 1.1rem;">
            {summary_text}
        </div>
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

    # Back button
    if st.button("← Back to Landing Page", key="back_to_landing"):
        st.session_state.show_app = False
        st.rerun()

    # App Title
    st.title(" Smart Research Summarizer")

    # Simple status
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
                st.text_area("", value=preview_text, height=200, disabled=True)

            # Document stats
            word_count = len(full_text.split())
            char_count = len(full_text)
            estimated_read_time = max(1, round(word_count / 250))

            col1, col2, col3 = st.columns(3)
            with col1:
                create_metrics(f"{word_count:,}", "Word Count")
            with col2:
                create_metrics(f"{char_count:,}", "Characters")
            with col3:
                create_metrics(f"{estimated_read_time}", "Est. Read Time (min)")

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
                                create_metrics(f"{summary_word_count}", "Summary Words")
                            with col2:
                                create_metrics(f"{compression_ratio}%", "Compression")
                            with col3:
                                create_metrics(f"{summary_length}", "Summary Type")

                            # Display summary
                            st.markdown("#### 📝 Generated Summary")
                            create_summary_box(summary)

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
                                        # Summary comparison chart with improved text visibility
                                        fig_comparison = px.bar(
                                            x=['Original Document', 'Generated Summary'],
                                            y=[word_count, summary_word_count],
                                            title="Word Count Comparison",
                                            color=['Original Document', 'Generated Summary'],
                                            color_discrete_sequence=['#22c55e', '#16a34a']
                                        )

                                        # Improved dark nebula theme configuration
                                        fig_comparison.update_layout(
                                            paper_bgcolor='rgba(15, 27, 15, 0.9)',
                                            plot_bgcolor='rgba(15, 27, 15, 0.9)',
                                            title_font_color='#22c55e',
                                            title_font_size=20,
                                            title_x=0.5,
                                            font=dict(color='#f8fafc', size=14),
                                            xaxis=dict(
                                                tickfont=dict(color='#f8fafc', size=14),
                                                title=dict(text='Document Type', font=dict(color='#f8fafc', size=16))
                                            ),
                                            yaxis=dict(
                                                tickfont=dict(color='#f8fafc', size=14),
                                                title=dict(text='Word Count', font=dict(color='#f8fafc', size=16))
                                            ),
                                            showlegend=False,
                                            margin=dict(l=50, r=50, t=80, b=50)
                                        )

                                        # Update traces for better visibility
                                        fig_comparison.update_traces(
                                            textfont_color='#f8fafc',
                                            marker_line_color='#22c55e',
                                            marker_line_width=2
                                        )

                                        st.plotly_chart(fig_comparison, use_container_width=True)

                                        # Compression gauge with improved visibility
                                        fig_gauge = go.Figure(go.Indicator(
                                            mode="gauge+number+delta",
                                            value=compression_ratio,
                                            domain={'x': [0, 1], 'y': [0, 1]},
                                            title={'text': "Compression Efficiency %",
                                                   'font': {'color': '#f8fafc', 'size': 18}},
                                            delta={'reference': 50, 'font': {'color': '#f8fafc', 'size': 16}},
                                            number={'font': {'color': '#f8fafc', 'size': 32}},
                                            gauge={
                                                'axis': {'range': [None, 100], 'tickcolor': '#f8fafc',
                                                         'tickfont': {'color': '#f8fafc', 'size': 12}},
                                                'bar': {'color': "#22c55e"},
                                                'steps': [
                                                    {'range': [0, 25], 'color': "rgba(239, 68, 68, 0.3)"},
                                                    {'range': [25, 50], 'color': "rgba(245, 158, 11, 0.3)"},
                                                    {'range': [50, 75], 'color': "rgba(34, 197, 94, 0.3)"},
                                                    {'range': [75, 100], 'color': "rgba(34, 197, 94, 0.5)"}
                                                ],
                                                'threshold': {
                                                    'line': {'color': "#22c55e", 'width': 4},
                                                    'thickness': 0.75,
                                                    'value': 80
                                                }
                                            }
                                        ))

                                        # Improved dark nebula theme for gauge
                                        fig_gauge.update_layout(
                                            paper_bgcolor='rgba(15, 27, 15, 0.9)',
                                            plot_bgcolor='rgba(15, 27, 15, 0.9)',
                                            font=dict(color='#f8fafc'),
                                            height=400,
                                            margin=dict(l=50, r=50, t=50, b=50)
                                        )

                                        st.plotly_chart(fig_gauge, use_container_width=True)

                                        # Reading time comparison
                                        original_read_time = max(1, round(word_count / 250))
                                        summary_read_time = max(1, round(summary_word_count / 250))
                                        time_saved = max(0, original_read_time - summary_read_time)

                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            create_metrics(f"{original_read_time}", "Original Read Time (min)")
                                        with col2:
                                            create_metrics(f"{summary_read_time}", "Summary Read Time (min)")
                                        with col3:
                                            create_metrics(f"{time_saved}", "Time Saved (min)")

                                    except Exception as e:
                                        st.warning(f"Advanced visualization error: {e}")

                            elif show_graphs and not PLOTLY_AVAILABLE:
                                st.info("📈 Install Plotly for advanced visualizations: pip install plotly")

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
                                st.download_button(
                                    "📥 Download Complete Report",
                                    download_content,
                                    filename,
                                    "text/plain",
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
        st.markdown("### Welcome to Smart Research Summarizer!")
        st.markdown("Get started by uploading a PDF research paper above.")

        # Info about features
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

    # Footer
    st.markdown(f"""
    <div style="text-align: center; margin-top: 50px; padding: 20px; color: #cbd5e1; border-top: 1px solid rgba(34, 197, 94, 0.3);">
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

    # Initialize session state
    if 'show_app' not in st.session_state:
        st.session_state.show_app = False

    # Load CSS
    load_css()
    render_streamlit_navbar()

    # Enhanced sidebar for nebula theme
    st.sidebar.success("✨ Nebula mode active")
    st.sidebar.markdown("**Beautiful green nebula interface**")
    st.sidebar.markdown("---")
    st.sidebar.markdown("🌌 **Features:**")
    st.sidebar.markdown("• Multi-layered nebula effects")
    st.sidebar.markdown("• Animated stellar particles")
    st.sidebar.markdown("• Dynamic cosmic backgrounds")
    st.sidebar.markdown("• Responsive glow effects")

    # Route to appropriate page
    if st.session_state.show_app:
        try:
            with st.spinner("🌌 Loading Smart Research Summarizer..."):
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