import pdfplumber
from docx import Document


def extract_text_from_file(file):
    name = file.name.lower()

    if name.endswith(".pdf"):
        return extract_pdf(file)
    elif name.endswith(".docx"):
        return extract_docx(file)
    else:
        raise ValueError("Unsupported file type")


def extract_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()


def extract_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs]).strip()
