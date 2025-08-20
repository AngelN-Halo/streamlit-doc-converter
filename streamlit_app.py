import streamlit as st
import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image, UnidentifiedImageError, features
import tempfile
import os
import pypandoc
from docx import Document

# Debug info: show image format support
print("=== Pillow Debug Info ===")
try:
    import PIL
    print("Pillow version:", PIL.__version__)
    print("JPEG support:", features.check("jpg"))
    print("Available decoders:", features.get_supported_decoders())
    print("Available encoders:", features.get_supported_encoders())
except Exception as e:
    print("Pillow debug failed:", e)
print("=========================")

st.set_page_config(page_title="Document Converter", layout="centered")
st.title("📄 Upload and Convert Files")

st.markdown("""
### Why Choose MD?
- **Markdown (MD)**: Preferred for human-readable documents with lightweight formatting.
- **JSON**: COMING SOON! Ideal for structured data storage, machine processing, and integration with databases or APIs.
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
            try:
                image = Image.open(tmp_path).convert("RGB")

                # Step 1: Auto-rotate using EXIF metadata (common from phone cameras)
                try:
                    from PIL import ImageOps
                    image = ImageOps.exif_transpose(image)
                except Exception:
                    pass  # Not all images have EXIF orientation info

                # Step 2: Detect text rotation from Tesseract (OSD)
                try:
                    osd = pytesseract.image_to_osd(image)
                    import re
                    rotation = int(re.search(r"Rotate: (\d+)", osd).group(1))
                    if rotation != 0:
                        image = image.rotate(-rotation, expand=True)
                except Exception as e:
                    print("OSD detection failed:", e)

                # (Optional) Step 3: Improve contrast for better OCR
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.5)

                # Step 4: OCR with English language
                output_text = pytesseract.image_to_string(image, lang="eng")

            except UnidentifiedImageError:
                output_text = "Error: Unsupported or corrupted image file."
            except Exception as e:
                output_text = f"Error processing image: {str(e)}"
            except UnidentifiedImageError:
                output_text = "Error: Unsupported or corrupted image file."
            except Exception as e:
                output_text = f"Error processing image: {str(e)}"

        elif file_ext == "pdf":
            with pdfplumber.open(tmp_path) as pdf:
                output_text = "\n\n".join([page.extract_text() or "" for page in pdf.pages])

        elif file_ext in ["csv", "xlsx"]:
            df = pd.read_excel(tmp_path) if file_ext == "xlsx" else pd.read_csv(tmp_path)
            output_text = df.to_markdown(index=False)

        elif file_ext == "docx":
            doc = Document(tmp_path)
            output_text = "\n".join([para.text for para in doc.paragraphs])

        elif file_ext == "epub":
            output_text = pypandoc.convert_file(tmp_path, 'md')

        else:
            output_text = pypandoc.convert_file(tmp_path, 'md')

    except Exception as e:
        output_text = f"Error: {str(e)}"
    finally:
        os.remove(tmp_path)

    if output_text:
        st.subheader("Converted Markdown Preview")
        st.text_area("Converted Text", output_text, height=300)
        output_file = f"{file_base}_converted.md"
        st.download_button(
            label="💾 Download Converted File",
            data=output_text,
            file_name=output_file,
            mime="text/markdown"
        )
