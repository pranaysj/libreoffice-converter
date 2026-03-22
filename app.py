import os
import subprocess
from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)

# This is the "Look" of your tester page
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>PDF Converter</title>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center; padding-top: 50px; background: #f4f4f9; }
        .card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h2 { color: #333; }
        input { margin-bottom: 1rem; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Doc to PDF Converter</h2>
        <form action="/convert" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".doc,.docx,.odt,.rtf" required><br>
            <button type="submit">Convert to PDF</button>
        </form>
        <p><small>Powered by LibreOffice + Python</small></p>
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

    input_path = os.path.join("/tmp", file.filename)
    file.save(input_path)

    try:
        subprocess.run([
            'libreoffice', '--headless', '--convert-to', 'pdf', 
            '--outdir', '/tmp', input_path
        ], check=True)
        
        pdf_path = input_path.rsplit('.', 1)[0] + '.pdf'
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
