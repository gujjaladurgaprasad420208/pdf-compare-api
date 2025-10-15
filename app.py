from flask import Flask, jsonify, request
from PyPDF2 import PdfReader
from flask_cors import CORS
import difflib
import os
import io
import base64

# ------------------------------------------------------
# 🚀 Initialize Flask App
# ------------------------------------------------------
app = Flask(__name__)

# Allow Salesforce and external origins (CORS)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


# ------------------------------------------------------
# 🏠 Home Route
# ------------------------------------------------------
@app.route("/")
def home():
    """Default route to verify API status."""
    return jsonify({
        "message": "🚀 PDF Comparison API is live and running on Render (Text Diff Mode)"
    })


# ------------------------------------------------------
# 🔍 Compare PDFs Endpoint
# ------------------------------------------------------
@app.route("/compare", methods=["POST"])
def compare():
    """Compares two base64-encoded PDF files and returns text differences."""
    try:
        # Get input JSON data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        pdf1_name = data.get("pdf1_name")
        pdf2_name = data.get("pdf2_name")
        pdf1_data = data.get("pdf1_data")
        pdf2_data = data.get("pdf2_data")

        # Validate input
        if not pdf1_data or not pdf2_data:
            return jsonify({
                "error": "Missing PDF content",
                "received_keys": list(data.keys())
            }), 400

        # Decode base64 to bytes
        pdf1_bytes = base64.b64decode(pdf1_data)
        pdf2_bytes = base64.b64decode(pdf2_data)

        # Extract text from both PDFs
        text1 = extract_text_from_pdf(io.BytesIO(pdf1_bytes))
        text2 = extract_text_from_pdf(io.BytesIO(pdf2_bytes))

        # Compare text line by line
        diff_result = compare_texts(text1, text2)

        # Return JSON summary
        return jsonify({
            "status": "success",
            "pdf1_name": pdf1_name,
            "pdf2_name": pdf2_name,
            "differences_found": len(diff_result) > 0,
            "differences": diff_result or ["✅ No visible text differences found"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------
# 🧩 Extract Text from PDF
# ------------------------------------------------------
def extract_text_from_pdf(file_obj):
    """
    Extracts text from all pages of a PDF file.
    :param file_obj: BytesIO PDF file object
    :return: Combined text from all pages
    """
    reader = PdfReader(file_obj)
    text = ""

    for i, page in enumerate(reader.pages):
        try:
            text += page.extract_text() or ""
        except Exception as e:
            print(f"⚠️ Error reading page {i + 1}: {e}")

    return text


# ------------------------------------------------------
# 🧠 Compare Texts Using difflib
# ------------------------------------------------------
def compare_texts(text1, text2):
    """
    Compares text content line by line using difflib.
    Returns a list of human-readable differences.
    """
    text1_lines = text1.splitlines()
    text2_lines = text2.splitlines()

    diff = difflib.unified_diff(
        text1_lines,
        text2_lines,
        fromfile="PDF1",
        tofile="PDF2",
        lineterm=""
    )

    changes = []
    for line in diff:
        if line.startswith("+ ") and not line.startswith("+++"):
            changes.append(f"🟢 Added: {line[2:]}")
        elif line.startswith("- ") and not line.startswith("---"):
            changes.append(f"🔴 Removed: {line[2:]}")

    # Limit number of changes for clean output
    if len(changes) > 30:
        changes = changes[:30] + ["...more differences not shown"]

    return changes


# ------------------------------------------------------
# ▶️ Run App
# ------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
