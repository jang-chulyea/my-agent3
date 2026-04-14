def extract_text_from_pdf(path):
    import fitz

    if hasattr(path, "read"):
        doc = fitz.open(stream=path.read(), filetype="pdf")
    else:
        doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text
