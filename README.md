# 📄 Streamlit Document Converter

This is a **web-based file converter** powered by [Streamlit](https://streamlit.io) that lets you upload **images, PDFs, spreadsheets, Word docs, and EPUBs** and converts them to **Markdown** text for easy copy, editing, or download.

It uses:

- **Tesseract OCR** for image & scanned PDF text extraction
- **pdfplumber** for searchable PDFs
- **pandas** for CSV/XLSX handling
- **python-docx** for DOCX files
- **pypandoc** for EPUB and other format conversions

> **JPEG support is fully enabled** in our Docker build — even CMYK and sideways images should be readable thanks to auto-rotation and preprocessing.

---

## ✨ Features

- **Supported Upload Types**:
  - Images: `PNG`, `JPG`, `JPEG`
  - Documents: `PDF`, `DOCX`, `EPUB`
  - Spreadsheets: `CSV`, `XLSX`
- **Automatic OCR for Images**:
  - Auto-rotate based on EXIF
  - Detect & fix text rotation via Tesseract OSD
  - Convert CMYK to RGB to avoid processing errors
- **Preview Converted Output** in the browser
- **Download as Markdown** with one click
- Runs in a **self-contained Docker container** — no need to install Tesseract locally

---

## 🖥 Tech Stack Diagram

```mermaid
flowchart TD
    A[Web Browser Upload] --> B[Streamlit App in Docker]
    B --> C[Image Handler: Pillow + Tesseract OCR]
    B --> D[PDF Handler: pdfplumber]
    B --> E[Doc/Spreadsheet: python-docx, pandas, pypandoc]
    C --> F[Extracted Text]
    D --> F
    E --> F
    F --> G[Markdown Preview + Download]
