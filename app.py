from flask import Flask, jsonify, request
from flask_cors import CORS
import fitz  # PyMuPDF
import base64, io, difflib, os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route("/")
def home():
    return jsonify({"message": "🚀 PDF Comparison API (PyMuPDF) is running!"})


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

        # Decode Base64 → extract text
        pdf1_text = extract_text(base64.b64decode(pdf1_data))
        pdf2_text = extract_text(base64.b64decode(pdf2_data))

        if not pdf1_text.strip() and not pdf2_text.strip():
            return jsonify({
                "error": "No readable text found in either PDF. (They might be scanned images)"
            }), 400

        # Generate side-by-side HTML diff
        differ = difflib.HtmlDiff(wrapcolumn=120)
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
                body {{ font-family: 'Segoe UI', sans-serif; background:#fff; margin:10px; }}
                table.diff {{ width:100%; border-collapse: collapse; }}
                td.diff_header {{ background:#ddd; font-weight:bold; text-align:center; }}
                td.diff_next {{ background:#f7f7f7; }}
                td.diff_add {{ background:#d4edda; color:#155724; }}
                td.diff_sub {{ background:#f8d7da; color:#721c24; }}
                td.diff_chg {{ background:#fff3cd; color:#856404; }}
                td, th {{ padding:5px 8px; border:1px solid #ccc; vertical-align:top; }}
            </style>
        </head>
        <body>{diff_html}</body>
        </html>
        """

        print("📤 Sending visual_html length:", len(styled_html))
        return jsonify({
            "status": "success",
            "pdf1_name": pdf1_name,
            "pdf2_name": pdf2_name,
            "visual_html": styled_html
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def extract_text(pdf_bytes):
    """Extract text from PDF using PyMuPDF"""
    text = ""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()
    except Exception as e:
        print(f"⚠️ Text extraction failed: {e}")
        return ""
    return text.strip()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
