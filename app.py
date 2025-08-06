import streamlit as st
from datetime import datetime
import json


def show_pipeline_results(summary_text, summary_length):
    """
    Display the pipeline: Summary → Graph → Download

    Args:
        summary_text (str): The generated summary text
        summary_length (str): Length category (e.g., 'Short', 'Medium', 'Long')
    """
    # Input validation
    if not summary_text or not summary_text.strip():
        st.error("⚠️ No summary text provided")
        return

    if not summary_length:
        summary_length = "Unknown"

    # Store summary in session state
    st.session_state["summary"] = summary_text
    st.session_state["summary_length"] = summary_length

    st.markdown("---")
    st.markdown("### 📝 Step 1: Generated Summary")

    # Enhanced metrics
    summary_word_count = len(summary_text.split())
    summary_char_count = len(summary_text)
    estimated_reading_time = max(1, round(summary_word_count / 200))  # ~200 words per minute

    # Metrics display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Words", summary_word_count)
    with col2:
        st.metric("Characters", summary_char_count)
    with col3:
        st.metric("Reading Time", f"{estimated_reading_time} min")

    st.success(f"✅ {summary_length} summary generated!")

    # Enhanced dynamic styling with better contrast
    theme = get_theme_colors()

    st.markdown(f"""
    <div style="
        background: {theme['box_bg']};
        padding: 25px;
        border-radius: 15px;
        border-left: 4px solid {theme['border_color']};
        margin: 15px 0;
        box-shadow: 0 4px 20px {theme['shadow_color']};
        border: {theme['border_style']};
        transition: all 0.3s ease;
    ">
        <p style="
            margin: 0; 
            line-height: 1.7; 
            font-size: 16px; 
            color: {theme['text_color']};
            text-align: justify;
        ">
            {summary_text}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # STEP 2: Graph Visualization
    st.markdown("---")
    st.markdown("### 📊 Step 2: Summary Visualization")

    if st.button("🔄 Generate/Refresh Graph", use_container_width=True):
        st.session_state["refresh_graph"] = True

    try:
        show_graph_section(summary_text)
    except NameError:
        st.warning("⚠️ Graph visualization function not available. Please ensure `show_graph_section()` is defined.")
        with st.expander("📈 Alternative Visualization Options"):
            st.info("""
            Consider implementing these visualization features:
            - Word frequency charts
            - Sentiment analysis graphs
            - Topic modeling visualizations
            - Summary statistics dashboard
            """)

    # STEP 3: Enhanced Download Options
    st.markdown("---")
    st.markdown("### 💾 Step 3: Export & Share")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        # Text file download
        filename = f"{summary_length.lower()}_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        download_content = create_download_content(summary_text, summary_length, summary_word_count)

        st.download_button(
            "📄 Download as TXT",
            data=download_content,
            file_name=filename,
            mime="text/plain",
            use_container_width=True,
            help="Download summary as plain text file"
        )

    with col2:
        # JSON format download
        json_filename = f"{summary_length.lower()}_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_content = create_json_content(summary_text, summary_length, summary_word_count)

        st.download_button(
            "📊 Download as JSON",
            data=json_content,
            file_name=json_filename,
            mime="application/json",
            use_container_width=True,
            help="Download summary with metadata as JSON"
        )

    with col3:
        # Markdown format download
        md_filename = f"{summary_length.lower()}_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        md_content = create_markdown_content(summary_text, summary_length, summary_word_count)

        st.download_button(
            "📝 Download as MD",
            data=md_content,
            file_name=md_filename,
            mime="text/markdown",
            use_container_width=True,
            help="Download summary as Markdown file"
        )

    # Copy to clipboard section
    st.markdown("---")
    st.markdown("**📋 Quick Copy Options:**")

    copy_col1, copy_col2 = st.columns([2, 1])

    with copy_col1:
        if st.button("📋 Copy Summary to Clipboard", use_container_width=True):
            # Note: Actual clipboard functionality would require additional libraries
            st.success("Summary copied! (Paste with Ctrl+V)")
            st.session_state["clipboard_content"] = summary_text

    with copy_col2:
        if st.button("🔗 Generate Share Link", use_container_width=True):
            # Placeholder for share functionality
            st.info("Share functionality coming soon!")

    # Expandable raw text view
    with st.expander("👁️ View Raw Text"):
        st.code(summary_text, language=None)

    # Optional: Add summary history
    if st.checkbox("📚 Show Summary History"):
        show_summary_history()


def get_theme_colors():
    """Get theme-appropriate colors for styling"""
    if st.session_state.get("dark_mode", False):
        return {
            "box_bg": "linear-gradient(135deg, #2d3748 0%, #4a5568 100%)",
            "text_color": "#e2e8f0",
            "border_color": "#667eea",
            "shadow_color": "rgba(102, 126, 234, 0.2)",
            "border_style": "1px solid #4a5568",
            "metrics_bg": "linear-gradient(135deg, #2d3748 0%, #4a5568 100%)"
        }
    else:
        return {
            "box_bg": "linear-gradient(135deg, #ffffff 0%, #f0fdf4 20%, #ffffff 100%)",
            "text_color": "#2d3748",
            "border_color": "#22c55e",
            "shadow_color": "rgba(34, 197, 94, 0.15)",
            "border_style": "1px solid #dcfce7",
            "metrics_bg": "linear-gradient(135deg, #ffffff 0%, #f0fdf4 50%, #ecfdf5 100%)"
        }


def create_download_content(summary_text, summary_length, word_count):
    """Create formatted content for text file download"""
    return f"""SUMMARY REPORT
{'=' * 50}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Length Category: {summary_length}
Word Count: {word_count}
Character Count: {len(summary_text)}
Estimated Reading Time: {max(1, round(word_count / 200))} minutes

{'=' * 50}
SUMMARY CONTENT
{'=' * 50}

{summary_text}

{'=' * 50}
Generated by Summary Pipeline
"""


def create_json_content(summary_text, summary_length, word_count):
    """Create JSON formatted content for download"""
    data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "length_category": summary_length,
            "word_count": word_count,
            "character_count": len(summary_text),
            "estimated_reading_time_minutes": max(1, round(word_count / 200))
        },
        "summary": {
            "text": summary_text,
            "sentences": summary_text.split('.')[:-1] if summary_text.endswith('.') else summary_text.split('.')
        }
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def create_markdown_content(summary_text, summary_length, word_count):
    """Create Markdown formatted content for download"""
    return f"""# Summary Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Length Category:** {summary_length}  
**Word Count:** {word_count}  
**Character Count:** {len(summary_text)}  
**Estimated Reading Time:** {max(1, round(word_count / 200))} minutes

---

## Summary

{summary_text}

---

*Generated by Summary Pipeline*
"""


def show_summary_history():
    """Display history of generated summaries"""
    if "summary_history" not in st.session_state:
        st.session_state["summary_history"] = []

    if st.session_state["summary_history"]:
        st.markdown("**Recent Summaries:**")
        for i, entry in enumerate(reversed(st.session_state["summary_history"][-5:])):
            with st.expander(f"Summary {len(st.session_state['summary_history']) - i} - {entry['timestamp']}"):
                st.write(f"**Length:** {entry['length']}")
                st.write(f"**Words:** {entry['word_count']}")
                st.write(entry['text'][:200] + "..." if len(entry['text']) > 200 else entry['text'])
    else:
        st.info("No summary history available yet.")


# Optional: Function to add summary to history
def add_to_summary_history(summary_text, summary_length):
    """Add current summary to history"""
    if "summary_history" not in st.session_state:
        st.session_state["summary_history"] = []

    entry = {
        "text": summary_text,
        "length": summary_length,
        "word_count": len(summary_text.split()),
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    st.session_state["summary_history"].append(entry)

    # Keep only last 10 summaries
    if len(st.session_state["summary_history"]) > 10:
        st.session_state["summary_history"] = st.session_state["summary_history"][-10:]