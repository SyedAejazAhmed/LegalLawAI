import os
import json
import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF and returns a list of lines."""
    try:
        doc = fitz.open(pdf_path)
        extracted_lines = []
        for page in doc:
            lines = page.get_text("text").split("\n")
            extracted_lines.extend([line.strip() for line in lines if line.strip()])
        return extracted_lines
    except Exception as e:
        print(f"❌ Error extracting text from {pdf_path}: {e}")
        return None

def parse_legal_text(lines):
    """Parses legal text into structured JSON format, ensuring chapters and sections retain full content."""
    legal_structure = {}
    current_law = None
    current_chapter = None
    chapter_content = []

    chapter_pattern = re.compile(r"CHAPTER\s+[IVXLCDM]+", re.IGNORECASE)  # Match "CHAPTER I, II, III..."
    
    for line in lines:
        # Identify Laws (Assuming Law names have specific keywords)
        if "BHARATIYA" in line or "INDIAN PENAL CODE" in line:  
            current_law = line
            if current_law not in legal_structure:
                legal_structure[current_law] = {}
            continue
        
        # Identify Chapters
        chapter_match = chapter_pattern.match(line)
        if chapter_match:
            if current_chapter and chapter_content:
                # ✅ Append instead of overwriting if chapter already exists
                if current_chapter in legal_structure[current_law]:
                    legal_structure[current_law][current_chapter] += " " + " ".join(chapter_content)
                else:
                    legal_structure[current_law][current_chapter] = " ".join(chapter_content)

            # ✅ Start a new chapter
            current_chapter = line
            chapter_content = []  # Reset for new chapter
            continue  # Skip to next line

        # Append text to the current chapter (Avoiding overwriting)
        if current_law and current_chapter:
            chapter_content.append(line)

    # ✅ Store last chapter's content properly
    if current_chapter and chapter_content:
        if current_chapter in legal_structure[current_law]:
            legal_structure[current_law][current_chapter] += " " + " ".join(chapter_content)
        else:
            legal_structure[current_law][current_chapter] = " ".join(chapter_content)

    return legal_structure

def process_all_pdfs(pdf_folder, output_json_path):
    """Extracts and processes all PDFs in the folder into a structured JSON file."""
    all_laws_data = {}

    for file_name in os.listdir(pdf_folder):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, file_name)
            print(f"📖 Processing: {file_name}...")

            extracted_lines = extract_text_from_pdf(pdf_path)
            if not extracted_lines:
                print(f"⚠️ Skipping {file_name} due to extraction error.")
                continue

            structured_data = parse_legal_text(extracted_lines)
            all_laws_data.update(structured_data)

    # Save structured data as JSON
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(all_laws_data, f, indent=4, ensure_ascii=False)

    print(f"✅ Processed legal text saved at: {output_json_path}")

# Define folder containing PDFs and output JSON file path
pdf_folder = "LegalLawAI"
output_json_path = "pdf_to_text/Laws_structured.json"

# ✅ Run extraction and structuring
process_all_pdfs(pdf_folder, output_json_path)