import sys
import json
import os

def extract_pdf(pdf_path):
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        total_pages = len(reader.pages)
        pages_text = []
        full_text = []
        for i, page in enumerate(reader.pages[:30]):
            text = page.extract_text() or ""
            pages_text.append({"page": i + 1, "text": text.strip()})
            if text.strip():
                full_text.append(text.strip())
        
        meta = reader.metadata or {}
        title = meta.get("/Title", "") or os.path.basename(pdf_path)
        author = meta.get("/Author", "")
        
        return {
            "success": True,
            "totalPages": total_pages,
            "title": str(title),
            "author": str(author),
            "text": "\n\n".join(full_text),
            "pages": pages_text
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "totalPages": 0,
            "text": "",
            "pages": []
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No file path provided"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = extract_pdf(file_path)
    print(json.dumps(result))
