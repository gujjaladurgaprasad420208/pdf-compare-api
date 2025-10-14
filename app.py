from flask import Flask, request, jsonify
import io
import base64
from PyPDF2 import PdfReader
import difflib
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Flask PDF Comparison API is Running"

@app.route('/compare', methods=['POST'])
def compare_pdfs():
    try:
        # Check request content
        if "multipart/form-data" in request.content_type:
            # Get raw request body
            raw_data = request.get_data(as_text=True)
            print("📦 Raw incoming data (truncated):", raw_data[:200])

            # Extract base64 strings (split by our boundary)
            # This is a minimal parser since Salesforce sends as base64
            import re
            base64_blocks = re.findall(r'Content-Type: application/pdf\r\n\r\n([A-Za-z0-9+/=\r\n]+)', raw_data)
            if len(base64_blocks) < 2:
                return jsonify({"error": "Could not extract both PDF parts"}), 400

            pdf1_bytes = base64.b64decode(base64_blocks[0])
            pdf2_bytes = base64.b64decode(base64_blocks[1])

            text1 = extract_text_from_pdf(io.BytesIO(pdf1_bytes))
            text2 = extract_text_from_pdf(io.BytesIO(pdf2_bytes))
            diffs = compare_texts(text1, text2)
            return jsonify({"status": "ok", "comparison": diffs}), 200

        return jsonify({"error": "Unsupported content type"}), 400

    except Exception as e:
        print("🔥 Error:", e)
        return jsonify({"error": str(e)}), 500


def extract_text_from_pdf(file_stream):
    text = ""
    reader = PdfReader(file_stream)
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text += page_text + "\n"
    return text.strip()


def compare_texts(text1, text2):
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    diff = difflib.ndiff(lines1, lines2)
    result = []
    for line in diff:
        if line.startswith('  '):
            result.append({"text1": line[2:], "text2": line[2:], "status": "match"})
        elif line.startswith('- '):
            result.append({"text1": line[2:], "text2": "", "status": "diff"})
        elif line.startswith('+ '):
            result.append({"text1": "", "text2": line[2:], "status": "diff"})
    return result


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
