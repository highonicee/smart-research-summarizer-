import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.data import find


# Check and download required NLTK data
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


# Initialize NLTK data
ensure_nltk_data()


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
        # Basic stopwords if NLTK doesn't work
        basic_stopwords = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an',
                           'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                           'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        tokens = [word for word in tokens if word not in basic_stopwords and len(word) > 2]

    return tokens


def create_word_frequency_chart(tokens):
    """Create a word frequency bar chart"""
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

        for idx, (word, freq) in enumerate(top_words[:20]):
            if idx >= len(positions):
                break

            row, col = positions[idx]
            x = col * 0.2
            y = 1 - row * 0.25

            # Scale font size based on frequency
            font_size = 10 + (freq / max_freq) * 20

            # Use different colors for variety
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
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


def show_graph(summary_text):
    """Main function to display all graphs"""
    if not summary_text or len(summary_text.strip()) == 0:
        st.warning("No text provided for visualization.")
        return

    try:
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


# Example usage
if __name__ == "__main__":
    st.title("Text Analysis Dashboard")

    # Sample text input
    sample_text = st.text_area(
        "Enter your text for analysis:",
        value="This is a sample text for analysis. It contains multiple sentences and words that can be analyzed for frequency and patterns.",
        height=150
    )

    if st.button("Analyze Text"):
        if sample_text:
            show_graph(sample_text)
        else:
            st.warning("Please enter some text to analyze.")