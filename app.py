from flask import Flask, jsonify, request
from PyPDF2 import PdfReader
from flask_cors import CORS
import os, io, base64, difflib

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route("/")
def home():
    return jsonify({
        "message": "🚀 PDF Comparison API is live and running (Text + Visual Highlight Mode)"
    })


@app.route("/compare", methods=["POST"])
def compare():
    """
    Compare two base64-encoded PDFs and return a visually formatted
    HTML snippet showing text side-by-side with color highlights.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        pdf1_name = data.get("pdf1_name")
        pdf2_name = data.get("pdf2_name")
        pdf1_data = data.get("pdf1_data")
        pdf2_data = data.get("pdf2_data")

        if not pdf1_data or not pdf2_data:
            return jsonify({
                "error": "Missing PDF content",
                "received_keys": list(data.keys())
            }), 400

        # Decode PDFs
        pdf1_bytes = base64.b64decode(pdf1_data)
        pdf2_bytes = base64.b64decode(pdf2_data)

        # Extract text
        text1 = extract_text_from_pdf(io.BytesIO(pdf1_bytes))
        text2 = extract_text_from_pdf(io.BytesIO(pdf2_bytes))

        # Generate HTML diff (side by side)
        html_result = generate_side_by_side_html(text1, text2, pdf1_name, pdf2_name)

        return jsonify({
            "status": "success",
            "pdf1_name": pdf1_name,
            "pdf2_name": pdf2_name,
            "visual_html": html_result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------------------------------
# Extract Text
# -----------------------------------------------------
def extract_text_from_pdf(file_obj):
    """Extracts all text from a PDF."""
    reader = PdfReader(file_obj)
    text = ""
    for i, page in enumerate(reader.pages):
        try:
            text += page.extract_text() or ""
        except Exception as e:
            print(f"⚠️ Error reading page {i+1}: {e}")
    return text


# -----------------------------------------------------
# Generate Side-by-Side HTML View
# -----------------------------------------------------
def generate_side_by_side_html(text1, text2, pdf1_name, pdf2_name):
    """Generates colored side-by-side HTML for two text blocks."""
    text1_lines = text1.splitlines()
    text2_lines = text2.splitlines()

    diff = difflib.ndiff(text1_lines, text2_lines)

    left_html, right_html = [], []
    for line in diff:
        code = line[:2]
        content = line[2:].replace(" ", "&nbsp;")

        if code == "  ":  # matching line
            left_html.append(f"<div class='match'>{content}</div>")
            right_html.append(f"<div class='match'>{content}</div>")
        elif code == "- ":  # removed from pdf1
            left_html.append(f"<div class='removed'>{content}</div>")
            right_html.append("<div class='empty'>&nbsp;</div>")
        elif code == "+ ":  # added in pdf2
            left_html.append("<div class='empty'>&nbsp;</div>")
            right_html.append(f"<div class='added'>{content}</div>")

    # Build final HTML layout
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: monospace;
                display: flex;
                justify-content: center;
                background: #f9f9f9;
                color: #333;
                margin: 20px;
            }}
            .container {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                width: 95%;
            }}
            .column {{
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                background: white;
                overflow-y: auto;
                max-height: 80vh;
            }}
            .header {{
                font-weight: bold;
                background: #eee;
                padding: 8px;
                text-align: center;
                border-bottom: 1px solid #ccc;
            }}
            .match {{ background-color: #e9fbe9; color: #1b5e20; }}
            .added {{ background-color: #e8f5e9; color: #2e7d32; }}
            .removed {{ background-color: #ffebee; color: #c62828; }}
            .empty {{ background-color: #fafafa; color: #aaa; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="column">
                <div class="header">{pdf1_name or "PDF 1"}</div>
                {''.join(left_html)}
            </div>
            <div class="column">
                <div class="header">{pdf2_name or "PDF 2"}</div>
                {''.join(right_html)}
            </div>
        </div>
    </body>
    </html>
    """
    return html


# -----------------------------------------------------
# Run App
# -----------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
