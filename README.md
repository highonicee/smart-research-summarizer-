#  Smart Research Summarizer

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Framework](https://img.shields.io/badge/Framework-Flask-green)
![NLP](https://img.shields.io/badge/NLP-Transformers-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Last Commit](https://img.shields.io/github/last-commit/highonicee/smart-research-summarizer)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-brightgreen)](https://smart-researcher.streamlit.app/)

Smart Research Summarizer is an AI-powered tool that helps researchers, students, and professionals quickly generate concise summaries of lengthy research papers. The goal is to save time, improve productivity, and make complex academic content more accessible.

---

## ✨ Features
-  Upload research papers (PDF or text format)
-  Extracts text automatically
-  Generates concise summaries using NLP models
-  Highlights key findings and insights
-  Simple and user-friendly interface

---

##  Screenshots

![Homepage](assets/main.png)  
*Application Homepage*

![Homepage Alternate](assets/main1.png)  
*Alternate view of the homepage*

![Summary Output](assets/summary.png)  
*Generated summary example*

![Visualization 1](assets/visual.png)  
*Visualization of results*

![Visualization 2](assets/visual1.png)  
*Another view of the visualization*




---

##  Tech Stack
- **Language:** Python  
- **Libraries:** Hugging Face Transformers, PyPDF2, NLTK  
- **Backend:** Flask / FastAPI  
- **Frontend:** Streamlit or React (depending on your implementation)  
- **Other Tools:** Markdown rendering, PDF parsing  

---

##  Installation and Usage

Clone the repository:

```bash
git clone https://github.com/your-username/smart-research-summarizer.git
cd smart-research-summarizer
```

Install dependencies:

pip install -r requirements.txt


Run the application:

python app.py


Open your browser and navigate to:

http://localhost:5000


## 🧠 How It Works

- User uploads a research paper (PDF or text file).

- The system extracts raw text from the document.

- The NLP model (Transformers) processes the text.

- A concise, structured summary is generated and displayed.

## Alternatively, you can try the deployed app here: https://smart-researcher.streamlit.app/
> ⚠️ Note: The app might "sleep" so if one wants to see the app they'll have to click on the blue button which will "wake the app up" may take a few seconds to load if it hasn't been used recently ("wake up" delay). Please be patient while it starts.
