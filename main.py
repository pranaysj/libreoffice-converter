import os
import subprocess
import uuid
import shutil
import base64
from io import BytesIO
from fastapi import FastAPI, UploadFile, File, HTTPException
from pdf2image import convert_from_path

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "online", "engine": "LibreOffice/Poppler"}

@app.post("/convert")
async def convert_pptx(file: UploadFile = File(...)):
    # 1. Validation
    allowed_extensions = {".pptx", ".ppt", ".docx", ".doc", ".odt"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file extension")

    job_id = str(uuid.uuid4())
    tmp_dir = f"/tmp/{job_id}"
    os.makedirs(tmp_dir, exist_ok=True)
    
    # Use a generic name to avoid shell injection via filenames
    input_path = os.path.join(tmp_dir, f"input{ext}")
    pdf_path = os.path.join(tmp_dir, "input.pdf")

    try:
        # Save uploaded file
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)

        # 2. Convert Office -> PDF
        # We use 'soffice' (LibreOffice) 
        subprocess.run([
            "soffice", "--headless", "--convert-to", "pdf", 
            "--outdir", tmp_dir, input_path
        ], check=True, timeout=60)
        
        # 3. PDF -> Images
        # thread_count=2 helps process pages in parallel
        images = convert_from_path(pdf_path, thread_count=2)
        base64_slides = []
        
        for img in images:
            buffered = BytesIO()
            # JPEG quality 70 is the "sweet spot" for Unity mobile/web performance
            img.save(buffered, format="JPEG", quality=70)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            base64_slides.append(img_str)

        return {
            "job_id": job_id, 
            "slides": base64_slides, 
            "total_pages": len(base64_slides)
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Conversion took too long")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 4. Cleanup: Always delete the folder to save Render disk space
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
