from flask import Flask, jsonify, request
from flask_cors import CORS
import fitz  # PyMuPDF
import base64, io, os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


@app.route("/")
def home():
    return jsonify({"message": "🚀 Visual PDF Comparison API (Side-by-Side) Running!"})


@app.route("/compare", methods=["POST"])
def compare():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        pdf1_name = data.get("pdf1_name", "File1.pdf")
        pdf2_name = data.get("pdf2_name", "File2.pdf")
        pdf1_data = data.get("pdf1_data")
        pdf2_data = data.get("pdf2_data")

        if not pdf1_data or not pdf2_data:
            return jsonify({"error": "Missing PDF content"}), 400

        # Decode + extract text
        pdf1_text = extract_text(base64.b64decode(pdf1_data))
        pdf2_text = extract_text(base64.b64decode(pdf2_data))

        # Prepare for line-by-line comparison
        lines1 = [l.strip() for l in pdf1_text.splitlines() if l.strip()]
        lines2 = [l.strip() for l in pdf2_text.splitlines() if l.strip()]
        max_len = max(len(lines1), len(lines2))

        # Equalize lengths
        while len(lines1) < max_len:
            lines1.append("")
        while len(lines2) < max_len:
            lines2.append("")

        # Build HTML rows with color highlights
        rows = ""
        for i in range(max_len):
            l1 = lines1[i]
            l2 = lines2[i]
            if l1 == l2:
                rows += f"<tr><td class='match'>{l1}</td><td class='match'>{l2}</td></tr>"
            else:
                rows += f"<tr><td class='diff'>{l1}</td><td class='diff'>{l2}</td></tr>"

        visual_html = f"""
        <html>
        <head>
            <meta charset='utf-8'>
            <style>
                body {{
                    font-family: 'Segoe UI', sans-serif;
                    background-color: #fff;
                    margin: 20px;
                }}
                h2 {{
                    text-align: center;
                    color: #333;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    table-layout: fixed;
                }}
                th, td {{
                    border: 1px solid #ccc;
                    padding: 8px;
                    vertical-align: top;
                    word-wrap: break-word;
                }}
                th {{
                    background-color: #f3f3f3;
                    font-weight: bold;
                }}
                td.match {{
                    background-color: #d4edda;
                    color: #155724;
                }}
                td.diff {{
                    background-color: #f8d7da;
                    color: #721c24;
                }}
                .wrapper {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }}
                .table-container {{
                    width: 95%;
                    overflow: auto;
                }}
            </style>
        </head>
        <body>
            <div class="wrapper">
                <h2>📄 Visual Text Comparison</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{pdf1_name}</th>
                                <th>{pdf2_name}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </body>
        </html>
        """

        return jsonify({
            "status": "success",
            "pdf1_name": pdf1_name,
            "pdf2_name": pdf2_name,
            "visual_html": visual_html
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def extract_text(pdf_bytes):
    """Extract full text using PyMuPDF (handles fonts, layers, embedded text)."""
    text = ""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()
    except Exception as e:
        print(f"⚠️ Error extracting text: {e}")
        text = ""
    if not text.strip():
        text = "(⚠️ No selectable text found — likely image-based PDF.)"
    return text


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
