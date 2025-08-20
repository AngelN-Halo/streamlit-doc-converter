import streamlit as st
import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image
import tempfile
import os
import pypandoc
from docx import Document

st.set_page_config(page_title="Document Converter", layout="centered")
st.title("📄 Upload and Convert Files")

# Brief explanation of file type choices
st.markdown("""
### Why Choose MD?
- **Markdown (MD)**: Preferred for human-readable documents with lightweight formatting. Use this if your content will be published or shared as plain text with headings, lists, etc.
- **JSON**: COMING SOON! Ideal for structured data storage, machine processing, and integration with databases or APIs. Choose this if your content is part of a pipeline for embeddings, analytics, or further programmatic handling.
""")

uploaded_file = st.file_uploader(
    "Upload a file (image/pdf/csv/xlsx/docx/epub)",
    type=["png", "jpg", "jpeg", "pdf", "csv", "xlsx", "docx", "epub"]
)

if uploaded_file is not None:
    file_ext = uploaded_file.name.split(".")[-1].lower()
    file_base = os.path.splitext(uploaded_file.name)[0]

    with tempfile.NamedTemporaryFile(delete=False, suffix="." + file_ext) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    output_text = ""

    try:
        if file_ext in ["png", "jpg", "jpeg"]:
            with st.spinner("Performing OCR on image..."):
                image = Image.open(tmp_path)
                output_text = pytesseract.image_to_string(image)

        elif file_ext == "pdf":
            texts = []
            with pdfplumber.open(tmp_path) as pdf:
                page_count = len(pdf.pages)

                # --- Auto detect if PDF is entirely scanned images ---
                all_empty = True
                for page in pdf.pages:
                    if page.extract_text() and page.extract_text().strip():
                        all_empty = False
                        break

                if all_empty:
                    st.warning(
                        "⚠️ This PDF appears to be a scanned document (image-based only). "
                        "Running OCR on all pages — this may take longer."
                    )

                # --- Process PDF with progress feedback ---
                with st.spinner("Processing PDF..."):
                    progress_bar = st.progress(0)
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        if text and text.strip():
                            texts.append(text)
                        else:
                            st.write(f"OCR on page {i+1} of {page_count}...")
                            img = page.to_image(resolution=300)
                            ocr_text = pytesseract.image_to_string(img.original)
                            texts.append(ocr_text)
                        progress_bar.progress((i + 1) / page_count)

            output_text = "\n\n".join(texts)

        elif file_ext in ["csv", "xlsx"]:
            df = pd.read_excel(tmp_path) if file_ext == "xlsx" else pd.read_csv(tmp_path)
            output_text = df.to_markdown(index=False)

        elif file_ext == "docx":
            doc = Document(tmp_path)
            output_text = "\n".join([para.text for para in doc.paragraphs])

        elif file_ext == "epub":
            with st.spinner("Converting EPUB..."):
                output_text = pypandoc.convert_file(tmp_path, 'md')

        else:
            with st.spinner(f"Converting {file_ext.upper()}..."):
                output_text = pypandoc.convert_file(tmp_path, 'md')

    except Exception as e:
        output_text = f"Error: {str(e)}"

    finally:
        os.remove(tmp_path)

    if output_text:
        st.subheader("Converted Markdown Preview")
        st.text_area("", output_text, height=300)
        output_file = f"{file_base}_converted.md"
        st.download_button(
            label="💾 Download Converted File",
            data=output_text,
            file_name=output_file,
            mime="text/markdown"
        )
