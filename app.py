import os
import subprocess
from flask import Flask, request, send_file

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_document():
    if 'file' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['file']
    input_path = os.path.join("/tmp", file.filename)
    file.save(input_path)

    # The command that tells LibreOffice to convert to PDF
    try:
        subprocess.run([
            'libreoffice', '--headless', '--convert-to', 'pdf', 
            '--outdir', '/tmp', input_path
        ], check=True)
        
        pdf_path = input_path.rsplit('.', 1)[0] + '.pdf'
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # Cloud platforms provide a PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)