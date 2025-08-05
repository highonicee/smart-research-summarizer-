#!/usr/bin/env python3
"""
Setup script for Smart Research Summarizer
This script installs all required dependencies and downloads NLTK data
"""

import subprocess
import sys
import os


def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False


def download_nltk_data():
    """Download required NLTK data"""
    try:
        import nltk
        print("📥 Downloading NLTK data...")

        # Download required NLTK data
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)

        print("✅ NLTK data downloaded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to download NLTK data: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Setting up Smart Research Summarizer...")
    print("=" * 50)

    # List of required packages
    required_packages = [
        "streamlit",
        "PyMuPDF",
        "nltk",
        "plotly",
        "transformers",
        "torch",
        "collections-extended"  # For Counter if needed
    ]

    # Optional packages for enhanced functionality
    optional_packages = [
        "wordcloud",
        "matplotlib",
        "seaborn",
        "pandas",
        "numpy"
    ]

    print("📦 Installing required packages...")
    failed_packages = []

    for package in required_packages:
        if not install_package(package):
            failed_packages.append(package)

    print("\n📦 Installing optional packages...")
    for package in optional_packages:
        install_package(package)  # Don't track failures for optional packages

    print("\n📥 Setting up NLTK...")
    download_nltk_data()

    print("\n" + "=" * 50)

    if failed_packages:
        print("⚠️  Setup completed with some issues:")
        for package in failed_packages:
            print(f"   - {package} failed to install")
        print("\nYou may need to install these manually:")
        for package in failed_packages:
            print(f"   pip install {package}")
    else:
        print("✅ Setup completed successfully!")

    print("\n🎉 Ready to run Smart Research Summarizer!")
    print("Run: streamlit run your_main_file.py")


if __name__ == "__main__":
    main()