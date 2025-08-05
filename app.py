import streamlit as st
from datetime import datetime


def show_pipeline_results(summary_text, summary_length):
    """Display the pipeline: Summary → Graph → Download"""
    # Store summary in session state
    st.session_state["summary"] = summary_text
    st.session_state["summary_length"] = summary_length

    st.markdown("---")
    st.markdown("### 📝 Step 1: Generated Summary")

    summary_word_count = len(summary_text.split())
    st.success(f"✅ {summary_length} summary generated! ({summary_word_count} words)")

    # Dynamic styling based on theme
    if st.session_state.get("dark_mode", False):
        box_bg = "linear-gradient(135deg, #2d3748 0%, #4a5568 100%)"
        text_color = "#e2e8f0"
        border_color = "#667eea"
        shadow_color = "rgba(102, 126, 234, 0.2)"
        border_style = "1px solid #4a5568"
    else:
        box_bg = "linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)"
        text_color = "#2d3748"
        border_color = "#4facfe"
        shadow_color = "rgba(79, 172, 254, 0.1)"
        border_style = "1px solid #e2e8f0"

    st.markdown(f"""
    <div style="
        background: {box_bg};
        padding: 25px;
        border-radius: 15px;
        border-left: 4px solid {border_color};
        margin: 15px 0;
        box-shadow: 0 4px 20px {shadow_color};
        border: {border_style};
    ">
        <p style="margin: 0; line-height: 1.7; font-size: 16px; color: {text_color};">
            {summary_text}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # STEP 2: Graph Visualization
    st.markdown("---")
    st.markdown("### 📊 Step 2: Summary Visualization")
    # Call to show_graph_section function (defined elsewhere in your code)
    try:
        show_graph_section(summary_text)
    except NameError:
        st.warning("Graph visualization function not available")

    # STEP 3: Download Options
    st.markdown("---")
    st.markdown("### 💾 Step 3: Download Summary")

    col1, col2 = st.columns([1, 1])

    with col1:
        # Summary download
        filename = f"{summary_length.lower()}_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        download_content = f"""Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Length: {summary_length}
Word Count: {summary_word_count}

{'-' * 50}
SUMMARY
{'-' * 50}

{summary_text}
"""
        st.download_button(
            "📥 Download Summary",
            data=download_content,
            file_name=filename,
            mime="text/plain",
            use_container_width=True
        )

    with col2:
        # Copy to clipboard option
        st.markdown("**Copy Summary:**")
        st.code(summary_text, language=None)