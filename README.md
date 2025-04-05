# Semantic Job Matcher

**Semantic Job Matcher** is a smart Python tool that extracts your job profile from your resume and matches it with web-scraped job descriptions using semantic similarity. It leverages state-of-the-art language models to find jobs that align with your experience and skills, currently focusing on LinkedIn listings with plans to expand to other platforms.

---

## 🚀 Features

- 📄 Extracts job summary from your resume (PDF/DOCX)
- 🌐 Scrapes or uses APIs to gather job descriptions from LinkedIn
- 🤖 Computes semantic similarity using Sentence Transformers
- 📊 Ranks job listings based on relevance to your profile
- 📈 Future plan to support multiple job platforms (Indeed, Glassdoor, etc.)

---

## 🧠 Tech Stack
- Python 3.8+
- [Sentence Transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2` or better)
- `pdfplumber` / `docx2txt` for resume parsing
- `Selenium` or `BeautifulSoup` for job scraping (or an API like SerpAPI)

---

## 📦 Installation

```bash
git clone https://github.com/your-username/semantic-job-matcher.git
cd semantic-job-matcher
pip install -r requirements.txt
```

---

## 📝 Usage

```python
python main.py --resume ./resume.docx --jobs ./jobs.json
```

This will output a ranked list of job titles with their similarity scores.

---

## 🔧 Configuration Options

- `--resume` - Path to your resume file (.pdf or .docx)
- `--jobs` - Path to a JSON file of scraped job descriptions (or use live scraping module)

---

## ✅ To Do

- [x] Resume parsing
- [x] Semantic matching logic
- [ ] LinkedIn live scraping
- [ ] API-based job board integration
- [ ] Streamlit interface

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

[MIT](LICENSE)

---

## 👨‍💻 Author

Built with ❤️ by [Your Name].

