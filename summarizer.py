import os
import ssl
import certifi
from transformers import pipeline
import re
import streamlit as st
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix SSL certificate issues
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()


def create_ssl_context():
    """Create a secure SSL context with proper certificate verification"""
    try:
        context = ssl.create_default_context(cafile=certifi.where())
        return context
    except (ssl.SSLError, OSError) as e:
        logger.warning("SSL context creation failed: %s", e)
        st.warning(f"SSL context creation failed: {e}")
        # Only use unverified context as last resort and warn user
        try:
            # Using getattr to avoid protected member access warning
            unverified_context = getattr(ssl, '_create_unverified_context', None)
            if unverified_context:
                context = unverified_context()
                st.warning("⚠️ Using unverified SSL context. This is not recommended for production.")
                return context
            else:
                logger.error("Unable to create any SSL context")
                return None
        except Exception as fallback_error:
            logger.error("Unable to create any SSL context: %s", fallback_error)
            return None


class SummarizerManager:
    """Manages the summarization pipeline with fallback models"""

    def __init__(self):
        self.summarizer = None
        self.model_hierarchy = [
            ("facebook/bart-large-cnn", "BART-large-CNN"),
            ("facebook/bart-base", "BART-base"),
            ("sshleifer/distilbart-cnn-12-6", "DistilBART"),
            ("t5-small", "T5-small")
        ]
        self._initialize_summarizer()

    def _initialize_summarizer(self) -> None:
        """Initialize the summarization pipeline with fallback options"""
        for model_name, display_name in self.model_hierarchy:
            try:
                logger.info("Loading %s model...", display_name)
                self.summarizer = pipeline("summarization", model=model_name)
                st.success(f"✅ Loaded {display_name} model successfully")
                return
            except Exception as e:
                logger.warning("Failed to load %s: %s", display_name, e)
                continue

        logger.error("All models failed to load")
        st.error("❌ All summarization models failed to load")
        self.summarizer = None


class TextProcessor:
    """Handles text cleaning and preprocessing"""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and preprocess text for better summarization"""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:-]', '', text)
        # Remove very short lines (likely artifacts)
        lines = text.split('.')
        lines = [line.strip() for line in lines if len(line.strip()) > 10]
        return '. '.join(lines).strip()

    @staticmethod
    def chunk_text(text: str, max_chunk_length: int = 1000) -> List[str]:
        """Split text into chunks for processing"""
        sentences = text.split('. ')
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence.split())
            if current_length + sentence_length > max_chunk_length and current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        if current_chunk:
            chunks.append('. '.join(current_chunk) + '.')

        return chunks


class ExtractiveSummarizer:
    """Fallback extractive summarization when transformers fail"""

    @staticmethod
    def summarize(text: str, target_length: int = 150) -> str:
        """Simple extractive summarization as fallback"""
        sentences = [s.strip() + '.' for s in text.split('. ') if len(s.strip()) > 20]

        if not sentences:
            return "Unable to generate summary from the provided text."

        # Calculate how many sentences to include
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        target_sentences = max(1, min(len(sentences), target_length // int(avg_sentence_length)))

        # Take first, middle, and last sentences for variety
        if len(sentences) <= target_sentences:
            return ' '.join(sentences)

        selected = [sentences[0]]  # First sentence

        # Middle sentences
        if target_sentences > 2:
            middle_start = len(sentences) // 3
            middle_end = min(len(sentences), middle_start + target_sentences - 2)
            selected.extend(sentences[middle_start:middle_end])

        # Last sentence if we have room
        if len(selected) < target_sentences and len(sentences) > 1:
            selected.append(sentences[-1])

        return ' '.join(selected)


class SmartSummarizer:
    """Main summarization class that combines all approaches"""

    def __init__(self):
        self.manager = SummarizerManager()
        self.processor = TextProcessor()
        self.extractive = ExtractiveSummarizer()

    def generate_summary(self, text: str, min_len: int = 50, max_len: int = 150) -> str:
        """Generate summary with specific length constraints"""
        try:
            cleaned_text = self.processor.clean_text(text)

            # Check if text is too short
            if len(cleaned_text.split()) < 50:
                return "Text is too short to generate a meaningful summary."

            # If summarizer failed to load, use extractive method
            if self.manager.summarizer is None:
                return self.extractive.summarize(cleaned_text, max_len)

            # For very long texts, chunk and summarize
            if len(cleaned_text.split()) > 1000:
                return self._handle_long_text(cleaned_text, min_len, max_len)
            else:
                return self._handle_short_text(cleaned_text, min_len, max_len)

        except Exception as e:
            logger.error("Error in generate_summary: %s", e)
            try:
                cleaned_text = self.processor.clean_text(text)
                return self.extractive.summarize(cleaned_text, max_len)
            except Exception as final_error:
                logger.error("Final fallback failed: %s", final_error)
                return f"Error generating summary: {str(final_error)}. Please try with a different text."

    def _summarize_with_pipeline(self, text: str, min_len: int, max_len: int) -> str:
        """Helper method to avoid code duplication in summarization"""
        try:
            summary = self.manager.summarizer(
                text,
                min_length=min_len,
                max_length=max_len,
                do_sample=False,
                truncation=True
            )
            return summary[0]['summary_text']
        except (ValueError, RuntimeError, KeyError) as e:
            logger.warning("Pipeline summarization failed: %s", e)
            return self.extractive.summarize(text, max_len)
        except Exception as e:
            logger.error("Unexpected error in pipeline summarization: %s", e)
            return self.extractive.summarize(text, max_len)

    def _handle_long_text(self, text: str, min_len: int, max_len: int) -> str:
        """Handle long text by chunking"""
        chunks = self.processor.chunk_text(text)
        chunk_summaries = []

        for chunk in chunks:
            if len(chunk.split()) > 50:
                chunk_min_len = max(20, min_len // len(chunks))
                chunk_max_len = min(130, max_len // len(chunks))

                try:
                    chunk_summary = self._summarize_with_pipeline(chunk, chunk_min_len, chunk_max_len)
                    chunk_summaries.append(chunk_summary)
                except Exception as e:
                    logger.warning("Chunk summarization failed: %s", e)
                    chunk_summaries.append(self.extractive.summarize(chunk, max_len // len(chunks)))

        combined_summary = ' '.join(chunk_summaries)

        if len(combined_summary.split()) > max_len:
            return self._summarize_with_pipeline(combined_summary, min_len, max_len)

        return combined_summary

    def _handle_short_text(self, text: str, min_len: int, max_len: int) -> str:
        """Handle shorter texts with direct summarization"""
        return self._summarize_with_pipeline(text, min_len, max_len)


class SummaryStats:
    """Handle summary statistics and display"""

    @staticmethod
    def get_stats(summary: str) -> Dict[str, int]:
        """Get statistics about the generated summary"""
        return {
            'words': len(summary.split()),
            'characters': len(summary),
            'sentences': len([s for s in summary.split('.') if s.strip()])
        }

    @staticmethod
    def display_stats(summary: str) -> None:
        """Display summary statistics in Streamlit"""
        stats = SummaryStats.get_stats(summary)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Words", stats['words'])
        with col2:
            st.metric("Characters", stats['characters'])
        with col3:
            st.metric("Sentences", stats['sentences'])


class SummarizerInterface:
    """Main interface class for the Streamlit app"""

    def __init__(self):
        self.summarizer = SmartSummarizer()

    def create_interface(self) -> None:
        """Create the complete summarization interface"""
        st.title("🧠 Smart Research Summarizer")
        st.markdown("Generate intelligent summaries from your research documents")

        # Input section
        user_text = self._create_input_section()

        # Summary configuration
        min_length, max_length = self._create_settings_section()

        # Generate summary
        if st.button("🚀 Generate Summary", type="primary", disabled=not user_text.strip()):
            self._handle_summary_generation(user_text, min_length, max_length)

    @staticmethod
    def _create_input_section() -> str:
        """Create the input section of the interface"""
        st.subheader("📝 Input Text")

        input_method = st.radio(
            "Choose input method:",
            ["📄 Paste Text", "📎 Upload File"],
            horizontal=True
        )

        if input_method == "📄 Paste Text":
            return st.text_area(
                "Enter your text here:",
                height=200,
                placeholder="Paste your article, research paper, or any long text here..."
            )

        else:  # Upload File
            uploaded_file = st.file_uploader(
                "Choose a text file",
                type=['txt', 'md'],
                help="Upload a .txt or .md file"
            )
            if uploaded_file is not None:
                user_text = str(uploaded_file.read(), "utf-8")
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                with st.expander("📖 Preview uploaded content"):
                    preview_text = user_text[:1000] + "..." if len(user_text) > 1000 else user_text
                    st.text_area("File content:", preview_text, height=150)
                return user_text
            return ""

    @staticmethod
    def _create_settings_section() -> Tuple[int, int]:
        """Create the settings section"""
        st.subheader("⚙️ Summary Settings")
        col1, col2 = st.columns(2)

        with col1:
            min_length = st.slider("Minimum length (words)", 30, 100, 50)
        with col2:
            max_length = st.slider("Maximum length (words)", 100, 300, 150)

        return min_length, max_length

    def _handle_summary_generation(self, user_text: str, min_length: int, max_length: int) -> None:
        """Handle the summary generation process"""
        if not user_text.strip():
            st.warning("⚠️ Please enter some text to summarize.")
            return

        with st.spinner("Generating summary..."):
            summary = self.summarizer.generate_summary(user_text, min_length, max_length)

        if summary:
            self._display_results(summary)
        else:
            st.error("❌ Failed to generate summary. Please try again with different text.")

    @staticmethod
    def _display_results(summary: str) -> None:
        """Display the summary results"""
        st.subheader("📄 Summary")
        st.write(summary)

        # Display statistics
        SummaryStats.display_stats(summary)

        # Download button
        st.download_button(
            label="📥 Download Summary",
            data=summary,
            file_name="summary.txt",
            mime="text/plain"
        )


# Main function to be called from other modules
def generate_summary(text: str, min_len: int = 50, max_len: int = 150) -> str:
    """Main entry point for summary generation from external modules"""
    try:
        summarizer = SmartSummarizer()
        return summarizer.generate_summary(text, min_len, max_len)
    except Exception as e:
        logger.error("Error in generate_summary function: %s", e)
        return f"Error generating summary: {str(e)}"


def main():
    """Main execution function"""
    try:
        interface = SummarizerInterface()
        interface.create_interface()
    except ImportError as e:
        st.error(f"❌ Import error: {str(e)}")
        st.info("Please ensure all required packages are installed. Check requirements.txt")
    except Exception as e:
        logger.error("Application error: %s", str(e))
        st.error(f"❌ Application error: {str(e)}")
        st.info("Please refresh the page and try again.")


if __name__ == "__main__":
    main()