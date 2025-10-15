from flask import Flask, jsonify, request
from flask_cors import CORS
from PyPDF2 import PdfReader
import base64, io, difflib, os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route("/")
def home():
    return jsonify({"message": "🚀 PDF Comparison API is running with text extraction!"})

@app.route("/compare", methods=["POST"])
def compare():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        pdf1_name = data.get("pdf1_name", "file1.pdf")
        pdf2_name = data.get("pdf2_name", "file2.pdf")
        pdf1_data = data.get("pdf1_data")
        pdf2_data = data.get("pdf2_data")

        if not pdf1_data or not pdf2_data:
            return jsonify({"error": "Missing PDF content"}), 400

        # Decode Base64 → bytes → extract text
        pdf1_text = extract_text_from_pdf(base64.b64decode(pdf1_data))
        pdf2_text = extract_text_from_pdf(base64.b64decode(pdf2_data))

        if not pdf1_text.strip() and not pdf2_text.strip():
            return jsonify({
                "error": "No text could be extracted from either PDF (possibly scanned images).",
                "pdf1_length": len(pdf1_text),
                "pdf2_length": len(pdf2_text)
            }), 400

        # Generate HTML diff
        differ = difflib.HtmlDiff(wrapcolumn=100)
        diff_html = differ.make_file(
            pdf1_text.splitlines(),
            pdf2_text.splitlines(),
            fromdesc=pdf1_name,
            todesc=pdf2_name,
            context=True,
            numlines=2
        )

        styled_html = f"""
        <html>
        <head>
            <meta charset='utf-8'>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background:#fafafa; }}
                table.diff {{ width:100%; border-collapse: collapse; }}
                td.diff_header {{ background:#d0d0d0; font-weight:bold; text-align:center; }}
                td.diff_next {{ background:#f2f2f2; }}
                td.diff_add {{ background:#d4edda; color:#155724; }}
                td.diff_sub {{ background:#f8d7da; color:#721c24; }}
                td.diff_chg {{ background:#fff3cd; color:#856404; }}
                td, th {{ padding:6px 8px; border:1px solid #ccc; vertical-align:top; }}
            </style>
        </head>
        <body>{diff_html}</body>
        </html>
        """

        return jsonify({
            "status": "success",
            "pdf1_name": pdf1_name,
            "pdf2_name": pdf2_name,
            "visual_html": styled_html
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def extract_text_from_pdf(pdf_bytes):
    """Try multiple fallback strategies for reliable text extraction."""
    text = ""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as e:
                print(f"⚠️ Error extracting page {i+1}: {e}")
    except Exception as e:
        print(f"⚠️ PDF read error: {e}")
        text = ""

    # Fallback if PyPDF2 failed
    if not text.strip():
        text = "(⚠️ No selectable text found in this PDF. It may be image-based.)"
    return text


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
