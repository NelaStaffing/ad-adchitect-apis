from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from PIL import Image, ImageOps
import io

app = FastAPI(title="Adchitect APIs")

class MaskRequest(BaseModel):
    canvas_width: int = Field(..., gt=0, description="Width of the larger background image (white)")
    canvas_height: int = Field(..., gt=0, description="Height of the larger background image (white)")
    mask_width: int = Field(..., gt=0, description="Width of the inner mask (black)")
    mask_height: int = Field(..., gt=0, description="Height of the inner mask (black)")

@app.get("/")
async def root():
    return {"message": "Adchitect API is running", "docs": "/docs"}

@app.post("/generate-mask")
async def generate_mask(request: MaskRequest):
    if request.mask_width > request.canvas_width or request.mask_height > request.canvas_height:
        raise HTTPException(
            status_code=400, 
            detail="Mask dimensions cannot be larger than canvas dimensions."
        )

    # Create white canvas
    canvas = Image.new("RGB", (request.canvas_width, request.canvas_height), "white")
    
    # Create black mask
    mask = Image.new("RGB", (request.mask_width, request.mask_height), "black")
    
    # Calculate centering position
    left = (request.canvas_width - request.mask_width) // 2
    top = (request.canvas_height - request.mask_height) // 2
    
    # Paste black mask onto white canvas
    canvas.paste(mask, (left, top))
    
    # Save to byte stream
    img_byte_arr = io.BytesIO()
    canvas.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return StreamingResponse(img_byte_arr, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
