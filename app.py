import os
import subprocess
from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)

# Updated HTML to allow PowerPoint files (.ppt, .pptx)
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Universal PDF Converter</title>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center; padding-top: 50px; background: #f4f4f9; }
        .card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 400px; text-align: center; }
        h2 { color: #333; }
        input { margin: 1rem 0; }
        button { background: #28a745; color: white; border: none; padding: 12px 24px; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #218838; }
        .hint { font-size: 12px; color: #666; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Office to PDF</h2>
        <p>Upload Word, PowerPoint, or Excel</p>
        <form action="/convert" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".doc,.docx,.ppt,.pptx,.odt,.rtf" required><br>
            <button type="submit">Convert Now</button>
        </form>
        <div class="hint">Supports: .docx, .pptx, .ppt, .odt</div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/convert', methods=['POST'])
def convert_document():
    if 'file' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    # Save original file
    input_path = os.path.join("/tmp", file.filename)
    file.save(input_path)

    try:
        # LibreOffice identifies the file type automatically!
        subprocess.run([
            'libreoffice', '--headless', '--convert-to', 'pdf', 
            '--outdir', '/tmp', input_path
        ], check=True)
        
        # This finds the new PDF file regardless of the original extension
        filename_without_ext = os.path.splitext(file.filename)[0]
        pdf_path = os.path.join("/tmp", filename_without_ext + '.pdf')
        
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return f"Conversion Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
