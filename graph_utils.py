import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.data import find


def ensure_nltk_data():
    """Ensure required NLTK data is available"""
    try:
        find('tokenizers/punkt')
    except LookupError:
        try:
            nltk.download('punkt', quiet=True)
        except Exception as e:
            st.warning(f"Could not download NLTK punkt tokenizer: {e}")

    try:
        find('corpora/stopwords')
    except LookupError:
        try:
            nltk.download('stopwords', quiet=True)
        except Exception as e:
            st.warning(f"Could not download NLTK stopwords: {e}")


def clean_text(text):
    """Clean and preprocess text for analysis"""
    if not text or not isinstance(text, str):
        return []

    # Remove special characters and convert to lowercase
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())

    # Tokenize
    try:
        tokens = word_tokenize(text)
    except (LookupError, OSError) as e:
        st.warning(f"NLTK tokenizer not available, using basic split: {e}")
        tokens = text.split()

    # Remove stopwords
    try:
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    except (LookupError, OSError) as e:
        st.warning(f"NLTK stopwords not available, using basic stopwords: {e}")
        # Basic stopwords if NLTK doesn't work - FIXED: proper filtering logic
        basic_stopwords = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an',
                           'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                           'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        tokens = [word for word in tokens if word not in basic_stopwords and len(word) > 2]

    return tokens


def get_word_frequency_data(text, top_n=15):
    """Extract word frequency data from text - shared utility function"""
    # Clean and tokenize text
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    # Remove common stop words
    common_stops = {'the', 'and', 'are', 'for', 'with', 'this', 'that', 'from', 'they', 'have', 'been', 'will',
                    'would', 'could', 'should'}
    words = [word for word in words if word not in common_stops]

    # Get top N most frequent words
    word_freq = Counter(words).most_common(top_n)
    return word_freq


def generate_word_frequency_chart(text):
    """Generate word frequency chart using Plotly"""
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        import numpy as np

        # Get word frequency data
        word_freq = get_word_frequency_data(text, top_n=15)

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

        # Word frequency bubble chart
        st.markdown("##### Word Frequency Bubble Chart")

        # Create positions for bubbles
        n_words = len(words)
        grid_size = int(np.ceil(np.sqrt(n_words)))
        positions_x = []
        positions_y = []

        for i in range(n_words):
            row = i // grid_size
            col = i % grid_size
            # Add some jitter to make it look more organic
            x_pos = col + np.random.uniform(-0.3, 0.3)
            y_pos = row + np.random.uniform(-0.3, 0.3)
            positions_x.append(x_pos)
            positions_y.append(y_pos)

        fig2 = go.Figure()

        # Add scatter plot with bubbles
        fig2.add_trace(go.Scatter(
            x=positions_x,
            y=positions_y,
            mode='markers',
            marker=dict(
                size=[freq * 4 + 20 for freq in frequencies],
                color=list(frequencies),
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Frequency"),
                line=dict(width=2, color='rgba(255,255,255,0.8)'),
                opacity=0.8
            ),
            text=[f"{word}<br>Count: {freq}" for word, freq in zip(words, frequencies)],
            hovertemplate="<b>%{text}</b><extra></extra>",
            showlegend=False
        ))

        # Add text annotations
        for i, (word, freq) in enumerate(zip(words, frequencies)):
            fig2.add_annotation(
                x=positions_x[i],
                y=positions_y[i],
                text=word,
                showarrow=False,
                font=dict(
                    size=min(16, 8 + freq * 2),
                    color='white'
                ),
                xanchor='center',
                yanchor='middle'
            )

        fig2.update_layout(
            title="Word Frequency Bubble Visualization",
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
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=500,
            showlegend=False
        )

        st.plotly_chart(fig2, use_container_width=True)

    except ImportError:
        st.info("📊 Install Plotly for interactive visualizations: pip install plotly")
        # Fallback to matplotlib
        create_matplotlib_word_frequency(text)
    except Exception as e:
        st.error(f"Visualization error: {e}")
        create_matplotlib_word_frequency(text)


def create_matplotlib_word_frequency(text):
    """Fallback matplotlib word frequency chart"""
    try:
        word_freq = get_word_frequency_data(text, top_n=10)

        if not word_freq:
            st.warning("No significant words found for visualization.")
            return

        words_list, frequencies = zip(*word_freq)

        # Create matplotlib chart
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(words_list, frequencies, color='skyblue', alpha=0.8)

        ax.set_title('Top 10 Most Frequent Words', fontsize=16, fontweight='bold')
        ax.set_xlabel('Frequency', fontsize=12)
        ax.set_ylabel('Words', fontsize=12)

        # Add value labels
        for bar, freq in zip(bars, frequencies):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                    str(freq), ha='left', va='center', fontweight='bold')

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    except Exception as e:
        st.error(f"Matplotlib visualization error: {e}")


def create_word_frequency_chart(tokens):
    """Create a word frequency bar chart using matplotlib"""
    if not tokens:
        return None

    # Get top 10 most common words
    word_freq = Counter(tokens).most_common(10)

    if not word_freq:
        return None

    words, frequencies = zip(*word_freq)

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(words, frequencies, color='skyblue', alpha=0.8)

    # Customize the plot
    ax.set_title('Top 10 Most Frequent Words in Summary', fontsize=16, fontweight='bold')
    ax.set_xlabel('Words', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.tick_params(axis='x', rotation=45)

    # Add value labels on bars
    for bar, freq in zip(bars, frequencies):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                str(freq), ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    return fig


def create_simple_wordcloud_visualization(tokens):
    """Create a simple word cloud-like visualization using matplotlib"""
    if not tokens:
        return None

    try:
        # Get word frequencies
        word_freq = Counter(tokens)
        top_words = word_freq.most_common(20)

        if not top_words:
            return None

        # Create a simple text-based visualization
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')

        # Position words in a grid-like pattern with size based on frequency
        max_freq = top_words[0][1]

        rows, cols = 4, 5
        positions = [(i, j) for i in range(rows) for j in range(cols)]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']

        for idx, (word, freq) in enumerate(top_words[:20]):
            if idx >= len(positions):
                break

            row, col = positions[idx]
            x = col * 0.2
            y = 1 - row * 0.25

            # Scale font size based on frequency
            font_size = 10 + (freq / max_freq) * 20
            color = colors[idx % len(colors)]

            ax.text(x, y, word, fontsize=font_size, color=color,
                    ha='center', va='center', weight='bold', alpha=0.8)

        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.1, 1.1)
        ax.set_title('Word Frequency Visualization', fontsize=16, fontweight='bold', pad=20)

        plt.tight_layout()
        return fig

    except Exception as e:
        st.error(f"Could not generate word visualization: {e}")
        return None


def create_summary_stats(text):
    """Create summary statistics visualization"""
    if not text:
        return None

    # Calculate basic statistics
    words = text.split()
    sentences = text.split('.')

    # Remove empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]

    # Calculate average words per sentence
    avg_words_per_sentence = len(words) / len(sentences) if sentences else 0

    # Create statistics
    stats = {
        'Total Words': len(words),
        'Total Sentences': len(sentences),
        'Avg Words/Sentence': round(avg_words_per_sentence, 1),
        'Total Characters': len(text)
    }

    # Create bar chart for statistics
    fig, ax = plt.subplots(figsize=(10, 6))

    categories = list(stats.keys())
    values = list(stats.values())

    bars = ax.bar(categories, values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'], alpha=0.8)

    ax.set_title('Summary Statistics', fontsize=16, fontweight='bold')
    ax.set_ylabel('Count', fontsize=12)
    ax.tick_params(axis='x', rotation=45)

    # Add value labels on bars
    max_value = max(values) if values else 1
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max_value * 0.01,
                str(value), ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    return fig


def create_advanced_plotly_analytics(text, summary_text, word_count, summary_word_count):
    """Create advanced analytics using Plotly"""
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
        compression_ratio = round((1 - summary_word_count / word_count) * 100) if word_count > 0 else 0

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

        # Analyze both texts for comparison (using the parameters)
        if text and summary_text:
            original_words = get_word_frequency_data(text, top_n=10)
            summary_words = get_word_frequency_data(summary_text, top_n=10)

            if original_words and summary_words:
                st.markdown("##### Word Frequency Comparison")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Original Text Top Words**")
                    orig_df = pd.DataFrame(original_words, columns=['Word', 'Frequency'])
                    st.dataframe(orig_df, use_container_width=True)

                with col2:
                    st.markdown("**Summary Top Words**")
                    summ_df = pd.DataFrame(summary_words, columns=['Word', 'Frequency'])
                    st.dataframe(summ_df, use_container_width=True)

    except ImportError:
        st.info("📈 Install Plotly for advanced visualizations: pip install plotly")
    except Exception as e:
        st.warning(f"Advanced visualization error: {e}")


def show_graph(summary_text):
    """Main function to display all graphs"""
    if not summary_text or len(summary_text.strip()) == 0:
        st.warning("No text provided for visualization.")
        return

    try:
        # Initialize NLTK data
        ensure_nltk_data()

        # Clean the text for analysis
        tokens = clean_text(summary_text)

        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["📊 Word Frequency", "☁️ Word Visualization", "📈 Summary Stats"])

        with tab1:
            st.subheader("Most Frequent Words")
            if tokens:
                fig1 = create_word_frequency_chart(tokens)
                if fig1:
                    st.pyplot(fig1)
                    plt.close(fig1)  # Close to free memory
                else:
                    st.info("No meaningful words found for frequency analysis.")
            else:
                st.info("No words available for analysis after cleaning.")

        with tab2:
            st.subheader("Word Visualization")
            if tokens and len(summary_text.strip()) > 10:
                fig2 = create_simple_wordcloud_visualization(tokens)
                if fig2:
                    st.pyplot(fig2)
                    plt.close(fig2)  # Close to free memory
                else:
                    st.info("Could not generate word visualization.")
            else:
                st.info("Text too short for word visualization.")

        with tab3:
            st.subheader("Summary Statistics")
            fig3 = create_summary_stats(summary_text)
            if fig3:
                st.pyplot(fig3)
                plt.close(fig3)  # Close to free memory

            # Additional text statistics table
            words = summary_text.split()
            sentences = [s.strip() for s in summary_text.split('.') if s.strip()]

            stats_df = pd.DataFrame({
                'Metric': ['Word Count', 'Sentence Count', 'Character Count', 'Average Word Length'],
                'Value': [
                    len(words),
                    len(sentences),
                    len(summary_text),
                    round(sum(len(word) for word in words) / len(words), 2) if words else 0
                ]
            })

            st.table(stats_df)

    except Exception as e:
        st.error(f"Error creating visualizations: {str(e)}")
        st.info("Visualization features are experiencing technical difficulties.")


# Export all functions for easy import
__all__ = [
    'ensure_nltk_data',
    'clean_text',
    'get_word_frequency_data',
    'generate_word_frequency_chart',
    'create_matplotlib_word_frequency',
    'create_word_frequency_chart',
    'create_simple_wordcloud_visualization',
    'create_summary_stats',
    'create_advanced_plotly_analytics',
    'show_graph'
]