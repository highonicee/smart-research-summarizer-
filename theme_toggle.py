import streamlit as st


def init_theme_toggle():
    """Initialize theme toggle in session state with dark mode as default"""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True  # Changed to True for dark mode default


def create_theme_toggle():
    """Create animated theme toggle in top-right corner using st.toggle"""
    init_theme_toggle()

    # Layout: top-right toggle with better positioning
    col1, col2 = st.columns([10, 1])
    with col2:
        dark_mode_selected = st.toggle(
            "🌙" if not st.session_state.dark_mode else "☀️",
            value=st.session_state.dark_mode,
            help="Toggle Dark/Light Mode"
        )
        st.session_state.dark_mode = dark_mode_selected

    # Enhanced base CSS for smooth transitions
    st.markdown("""
        <style>
            .stApp {
                transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            * {
                transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease !important;
            }

            /* Custom scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
            }
            ::-webkit-scrollbar-track {
                background: transparent;
            }
            ::-webkit-scrollbar-thumb {
                background: rgba(156, 163, 175, 0.5);
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: rgba(156, 163, 175, 0.8);
            }
        </style>
    """, unsafe_allow_html=True)


def apply_theme_styles():
    """Apply comprehensive theme styles based on current mode"""
    dark_mode = st.session_state.get('dark_mode', True)  # Changed default to True

    if dark_mode:
        theme_css = """
        <style>
        /* ENHANCED DARK MODE STYLES */

        /* Main App Background with animated gradient */
        html, body, .stApp, [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 25%, #1e2329 50%, #2d3748 100%) !important;
            color: #e2e8f0 !important;
            animation: gradientShift 10s ease infinite;
        }

        @keyframes gradientShift {
            0%, 100% { background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 25%, #1e2329 50%, #2d3748 100%); }
            50% { background: linear-gradient(135deg, #1a1f2e 0%, #0f1419 25%, #2d3748 50%, #1e2329 100%); }
        }

        /* Enhanced Main Container with glassmorphism */
        .main .block-container {
            background: linear-gradient(135deg, 
                rgba(30, 35, 41, 0.95) 0%, 
                rgba(45, 55, 72, 0.9) 50%,
                rgba(26, 32, 44, 0.95) 100%) !important;
            backdrop-filter: blur(25px) saturate(180%) !important;
            border-radius: 30px !important;
            box-shadow: 
                0 25px 80px rgba(0, 0, 0, 0.5),
                0 0 0 1px rgba(255, 255, 255, 0.05),
                inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            color: #e2e8f0 !important;
            position: relative;
        }

        /* Subtle glow effect */
        .main .block-container::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #4299e1, #9f7aea, #ed64a6, #4299e1);
            border-radius: 32px;
            z-index: -1;
            opacity: 0.1;
            background-size: 300% 300%;
            animation: gradientAnimation 6s ease infinite;
        }

        @keyframes gradientAnimation {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        /* Enhanced Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(20px) !important;
        }

        /* ALL TEXT ELEMENTS - COMPREHENSIVE with better hierarchy */
        h1, h2, h3, h4, h5, h6 {
            color: #f7fafc !important;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
        }

        p, span, div, li, ul, ol, strong, em, small, label {
            color: #e2e8f0 !important;
        }

        /* Streamlit specific text elements */
        .stMarkdown, .stMarkdown *, 
        .stText, .stText *,
        .stCaption, .stCaption *,
        .stCode, .stCode *,
        .stAlert, .stAlert *,
        .stInfo, .stInfo *,
        .stSuccess, .stSuccess *,
        .stWarning, .stWarning *,
        .stError, .stError *,
        .stException, .stException * {
            color: #e2e8f0 !important;
        }

        /* CRITICAL FIX: Custom summary boxes with inline styles - DARK MODE */
        .stMarkdown div[style*="background: linear-gradient(135deg, #ffffff"] p,
        .stMarkdown div[style*="background: linear-gradient(135deg, #ffffff"] * {
            color: #2d3748 !important;
        }

        .stMarkdown div[style*="background: linear-gradient(135deg, #2d3748"] p,
        .stMarkdown div[style*="background: linear-gradient(135deg, #2d3748"] * {
            color: #e2e8f0 !important;
        }

        /* Enhanced Input Fields with focus effects */
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stTimeInput"] input {
            background-color: rgba(45, 55, 72, 0.8) !important;
            color: #e2e8f0 !important;
            border: 2px solid rgba(74, 85, 104, 0.6) !important;
            border-radius: 12px !important;
            backdrop-filter: blur(10px) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        [data-testid="stTextInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus,
        [data-testid="stNumberInput"] input:focus {
            border-color: #4299e1 !important;
            box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2) !important;
            transform: translateY(-1px) !important;
        }

        [data-testid="stTextInput"] input::placeholder,
        [data-testid="stTextArea"] textarea::placeholder {
            color: #a0aec0 !important;
        }

        /* ENHANCED File Uploader - Complete Dark Mode Fix */
        [data-testid="stFileUploader"] {
            background-color: rgba(26, 32, 44, 0.9) !important;
            border: 2px dashed rgba(66, 153, 225, 0.6) !important;
            border-radius: 20px !important;
            backdrop-filter: blur(15px) !important;
            transition: all 0.3s ease !important;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: rgba(66, 153, 225, 0.8) !important;
            background-color: rgba(26, 32, 44, 0.95) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3) !important;
        }

        /* File uploader text elements - Force white text */
        [data-testid="stFileUploader"] label,
        [data-testid="stFileUploader"] div,
        [data-testid="stFileUploader"] span,
        [data-testid="stFileUploader"] p,
        [data-testid="stFileUploader"] small,
        [data-testid="stFileUploader"] * {
            color: #ffffff !important;
            background: transparent !important;
        }

        /* File uploader drag text specifically */
        [data-testid="stFileUploader"] div[data-testid] div,
        [data-testid="stFileUploader"] div[data-testid] span {
            color: #ffffff !important;
        }

        /* Browse files button */
        [data-testid="stFileUploader"] button {
            background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.5rem 1.5rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }

        [data-testid="stFileUploader"] button:hover {
            background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%) !important;
            transform: scale(1.05) !important;
        }

        /* Enhanced Buttons with better animations */
        .stButton > button {
            background: linear-gradient(135deg, #4299e1 0%, #3182ce 50%, #2c5282 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 15px !important;
            padding: 0.875rem 2.5rem !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            letter-spacing: 0.025em !important;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 
                0 4px 20px rgba(66, 153, 225, 0.4),
                0 0 0 0 rgba(66, 153, 225, 0.5) !important;
            position: relative;
            overflow: hidden;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #3182ce 0%, #2c5282 50%, #2a4365 100%) !important;
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 
                0 12px 35px rgba(66, 153, 225, 0.5),
                0 0 0 3px rgba(66, 153, 225, 0.3) !important;
        }

        /* Enhanced Download Button - BLACK text in dark mode */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 50%, #2f855a 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 15px !important;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
            font-weight: 700 !important;
        }

        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #38a169 0%, #2f855a 50%, #276749 100%) !important;
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 0 12px 35px rgba(72, 187, 120, 0.4) !important;
            color: #ffffff !important;
        }

        /* Force white text on file uploader - Ultimate fix */
        [data-testid="stFileUploader"],
        [data-testid="stFileUploader"] *,
        [data-testid="stFileUploader"] div,
        [data-testid="stFileUploader"] span,
        [data-testid="stFileUploader"] p,
        [data-testid="stFileUploader"] small,
        [data-testid="stFileUploader"] label {
            color: #ffffff !important;
        }

        /* Override any inherited styles */
        [data-testid="stFileUploader"] [data-testid] {
            color: #ffffff !important;
        }

        </style>
        """
    else:
        theme_css = """
        <style>
        /* ENHANCED LIGHT MODE STYLES */

        /* Main App Background with subtle animation */
        html, body, .stApp, [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 25%, #e2e8f0 50%, #f1f5f9 100%) !important;
            color: #1a202c !important;
            animation: lightGradientShift 12s ease infinite;
        }

        @keyframes lightGradientShift {
            0%, 100% { background: linear-gradient(135deg, #ffffff 0%, #f8fafc 25%, #e2e8f0 50%, #f1f5f9 100%); }
            50% { background: linear-gradient(135deg, #f8fafc 0%, #ffffff 25%, #f1f5f9 50%, #e2e8f0 100%); }
        }

        /* Enhanced Main Container */
        .main .block-container {
            background: rgba(255, 255, 255, 0.98) !important;
            backdrop-filter: blur(20px) saturate(180%) !important;
            border-radius: 30px !important;
            box-shadow: 
                0 20px 60px rgba(0, 0, 0, 0.08),
                0 0 0 1px rgba(0, 0, 0, 0.02),
                inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(0, 0, 0, 0.03) !important;
            color: #1a202c !important;
            position: relative;
        }

        /* Text hierarchy */
        h1, h2, h3, h4, h5, h6 {
            color: #1a202c !important;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
        }

        p, span, div, li, ul, ol, strong, em, small, label {
            color: #1a202c !important;
        }

        /* Streamlit specific text elements */
        .stMarkdown, .stMarkdown *, 
        .stText, .stText *,
        .stCaption, .stCaption *,
        .stCode, .stCode *,
        .stAlert, .stAlert *,
        .stInfo, .stInfo *,
        .stSuccess, .stSuccess *,
        .stWarning, .stWarning *,
        .stError, .stError *,
        .stException, .stException * {
            color: #1a202c !important;
        }

        /* CRITICAL FIX: Custom summary boxes with inline styles - LIGHT MODE */
        .stMarkdown div[style*="background: linear-gradient(135deg, #ffffff"] p,
        .stMarkdown div[style*="background: linear-gradient(135deg, #ffffff"] * {
            color: #2d3748 !important;
        }

        .stMarkdown div[style*="background: linear-gradient(135deg, #2d3748"] p,
        .stMarkdown div[style*="background: linear-gradient(135deg, #2d3748"] * {
            color: #e2e8f0 !important;
        }

        /* Enhanced Input Fields */
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stTimeInput"] input {
            background-color: rgba(255, 255, 255, 0.9) !important;
            color: #1a202c !important;
            border: 2px solid rgba(226, 232, 240, 0.8) !important;
            border-radius: 12px !important;
            backdrop-filter: blur(10px) !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        [data-testid="stTextInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus,
        [data-testid="stNumberInput"] input:focus {
            border-color: #4facfe !important;
            box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.1) !important;
            transform: translateY(-1px) !important;
        }

        [data-testid="stTextInput"] input::placeholder,
        [data-testid="stTextArea"] textarea::placeholder {
            color: #718096 !important;
        }

        /* FIXED FILE UPLOADER FOR LIGHT MODE - ENHANCED */
        [data-testid="stFileUploader"] {
            background-color: rgba(255, 255, 255, 0.95) !important;
            border: 2px dashed rgba(79, 172, 254, 0.6) !important;
            border-radius: 20px !important;
            backdrop-filter: blur(15px) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04) !important;
            transition: all 0.3s ease !important;
            min-height: 100px !important;
            padding: 20px !important;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: rgba(79, 172, 254, 0.8) !important;
            background-color: rgba(248, 250, 252, 0.98) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08) !important;
        }

        /* CRITICAL FIX: File uploader text visibility in light mode */
        [data-testid="stFileUploader"] label,
        [data-testid="stFileUploader"] div,
        [data-testid="stFileUploader"] span,
        [data-testid="stFileUploader"] p,
        [data-testid="stFileUploader"] small,
        [data-testid="stFileUploader"] * {
            color: #1a202c !important;
            background: transparent !important;
            font-weight: 500 !important;
        }

        /* Specific targeting for drag text */
        [data-testid="stFileUploader"] div[data-testid] div,
        [data-testid="stFileUploader"] div[data-testid] span,
        [data-testid="stFileUploader"] div[data-testid] p {
            color: #2d3748 !important;
            font-weight: 600 !important;
        }

        /* File uploader drop zone text */
        [data-testid="stFileUploader"] > div > div {
            color: #2d3748 !important;
        }

        /* File name display */
        [data-testid="stFileUploader"] div[data-testid="fileUploaderText"] {
            color: #2d3748 !important;
        }

        /* Browse files button for light mode */
        [data-testid="stFileUploader"] button {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 2rem !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3) !important;
        }

        [data-testid="stFileUploader"] button:hover {
            background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
            transform: scale(1.05) translateY(-1px) !important;
            box-shadow: 0 6px 20px rgba(79, 172, 254, 0.4) !important;
        }

        /* Enhanced Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 50%, #a8edea 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 15px !important;
            padding: 0.875rem 2.5rem !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            letter-spacing: 0.025em !important;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 
                0 4px 20px rgba(79, 172, 254, 0.3),
                0 0 0 0 rgba(79, 172, 254, 0.4) !important;
            position: relative;
            overflow: hidden;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #a8edea 100%) !important;
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 
                0 12px 35px rgba(79, 172, 254, 0.4),
                0 0 0 3px rgba(79, 172, 254, 0.2) !important;
        }

        /* Enhanced Download Button - WHITE text in light mode */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 50%, #68d391 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 15px !important;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #38a169 0%, #2f855a 50%, #48bb78 100%) !important;
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 0 12px 35px rgba(72, 187, 120, 0.4) !important;
        }

        </style>
        """

    st.markdown(theme_css, unsafe_allow_html=True)


def get_theme_aware_summary_style():
    """Return appropriate styling for summary boxes based on current theme"""
    dark_mode = st.session_state.get('dark_mode', True)  # Changed default to True

    if dark_mode:
        return {
            'background': 'linear-gradient(135deg, #2d3748 0%, #4a5568 100%)',
            'color': '#e2e8f0',
            'border_color': '#667eea',
            'shadow': 'rgba(102, 126, 234, 0.2)',
            'border': '1px solid #4a5568'
        }
    else:
        return {
            'background': 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
            'color': '#2d3748',
            'border_color': '#4facfe',
            'shadow': 'rgba(79, 172, 254, 0.1)',
            'border': '1px solid #e2e8f0'
        }


def force_cache_clear():
    """Force browser cache clear for theme styles"""
    import time
    cache_buster = int(time.time())

    st.markdown(f"""
        <style id="cache-buster-{cache_buster}">
        /* Force cache refresh */
        [data-testid="stFileUploader"] {{
            position: relative !important;
        }}
        </style>
    """, unsafe_allow_html=True)


def get_current_theme():
    """Get current theme mode"""
    return "dark" if st.session_state.get('dark_mode', True) else "light"  # Changed default to True


def create_theme_status_indicator():
    """Create a subtle theme status indicator"""
    theme = get_current_theme()
    status_color = "#4299e1" if theme == "dark" else "#4facfe"

    st.markdown(f"""
        <div style="
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: {status_color};
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            z-index: 999;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
        ">
            {theme.title()} Mode
        </div>
    """, unsafe_allow_html=True)


# Quick setup function for easy integration
def setup_theme_toggle():
    """One-line setup for theme toggle with cache clearing and dark mode default"""
    create_theme_toggle()
    apply_theme_styles()
    force_cache_clear()


# Utility functions for easy integration
def apply_custom_theme_css(custom_css_dark="", custom_css_light=""):
    """Allow users to add custom CSS for each theme"""
    dark_mode = st.session_state.get('dark_mode', True)  # Changed default to True

    if dark_mode and custom_css_dark:
        st.markdown(f"<style>{custom_css_dark}</style>", unsafe_allow_html=True)
    elif not dark_mode and custom_css_light:
        st.markdown(f"<style>{custom_css_light}</style>", unsafe_allow_html=True)


def theme_aware_color(dark_color, light_color):
    """Return appropriate color based on current theme"""
    return dark_color if st.session_state.get('dark_mode', True) else light_color  # Changed default to True


# Alternative initialization function for forced dark mode default
def force_dark_mode_default():
    """Force dark mode as default regardless of previous session state"""
    st.session_state.dark_mode = True
    setup_theme_toggle()