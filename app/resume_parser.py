import os
# print(os.getcwd())
import docx2txt
import pdfplumber
import re

def extract_text_from_resume(file_path):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == ".docx":
        print("Reading DOCX resume...")
        text = docx2txt.process(file_path)
    elif ext == ".pdf":
        print("Reading PDF resume...")
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    else:
        raise ValueError("Unsupported file format. Use .docx or .pdf")

    return text

def extract_resume_sections(text):
    # Define common section headers (add more if needed)
    section_headers = {
        'summary': r'(professional summary|SUMMARY|summary|profile|objective)',
        'experience': r'(experience|work experience|professional experience)',
        'education': r'(education)',
        'skills': r'(skills|technical skills)',
        'certifications': r'(certifications?)',
        'projects': r'(projects)',
        'achievements': r'(achievements)'
    }

    # Prepare regex pattern to detect section headers
    header_pattern = re.compile(rf"^({'|'.join(section_headers.values())})\s*$", re.IGNORECASE)

    lines = text.split('\n')
    sections = {}
    current_section = None
    buffer = []

    for line in lines:
        line_clean = line.strip()

        # If the line is a section header
        if header_pattern.match(line_clean.lower()):
            if current_section and buffer:
                sections[current_section] = "\n".join(buffer).strip()
                buffer = []

            # Detect which section it is
            for key, pattern in section_headers.items():
                if re.match(pattern, line_clean, re.IGNORECASE):
                    current_section = key
                    break
        elif current_section:
            buffer.append(line_clean)

    # Save the last section
    if current_section and buffer:
        sections[current_section] = "\n".join(buffer).strip()

    return sections


# Example usage:
if __name__ == "__main__":
    resume_path = "resume/Resume_Arshraj.pdf"  # or "your_resume.docx"
    resume_text = extract_text_from_resume(resume_path)
    sections = extract_resume_sections(resume_text)

    # Print extracted sections
    for section, content in sections.items():
        print(f"\n--- {section.upper()} ---\n{content[:500]}")  # limit output to 500 chars
