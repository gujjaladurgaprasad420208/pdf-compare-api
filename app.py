from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import fitz  # PyMuPDF
import io
import base64
from pdf2image import convert_from_bytes
from PIL import Image, ImageChops
import os

app = Flask(__name__)
CORS(app) 

@app.route('/')
def home():
    return "✅ Visual PDF Diff API Running"

@app.route('/compare', methods=['POST'])
def compare_pdfs():
    try:
        file1 = request.files.get('file1')
        file2 = request.files.get('file2')

        if not file1 or not file2:
            return jsonify({"error": "Missing PDF files"}), 400

        pdf1 = file1.read()
        pdf2 = file2.read()

        # Convert both PDFs to images (page by page)
        pages1 = convert_from_bytes(pdf1)
        pages2 = convert_from_bytes(pdf2)

        diff_pages = []
        for i in range(min(len(pages1), len(pages2))):
            img1 = pages1[i].convert('RGB')
            img2 = pages2[i].convert('RGB')

            diff = ImageChops.difference(img1, img2)
            # Highlight changes
            overlay = img1.copy()
            for x in range(img1.width):
                for y in range(img1.height):
                    r, g, b = diff.getpixel((x, y))
                    if r + g + b > 50:  # significant pixel difference
                        overlay.putpixel((x, y), (255, 0, 0))  # red

            diff_pages.append(overlay)

        # Merge all difference pages into a new PDF
        output_pdf = io.BytesIO()
        diff_pages[0].save(output_pdf, save_all=True, append_images=diff_pages[1:], format="PDF")
        output_pdf.seek(0)

        base64_pdf = base64.b64encode(output_pdf.read()).decode('utf-8')

        return jsonify({
            "status": "ok",
            "message": "Visual diff generated successfully",
            "diff_pdf": base64_pdf
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

