from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from PIL import Image
import io

app = FastAPI(title="MaskGenerator API")

class MaskRequest(BaseModel):
    canvas_width: int = Field(..., gt=0, description="Width of the larger background image (white)")
    canvas_height: int = Field(..., gt=0, description="Height of the larger background image (white)")
    mask_width: int = Field(..., gt=0, description="Width of the inner mask (black)")
    mask_height: int = Field(..., gt=0, description="Height of the inner mask (black)")

@app.get("/")
async def root():
    return {"message": "MaskGenerator API is running", "docs": "/docs"}

@app.post("/generate-mask")
async def generate_mask(request: MaskRequest):
    adjusted = False
    messages = []

    mask_w = request.mask_width
    mask_h = request.mask_height

    if mask_w > request.canvas_width:
        mask_w = request.canvas_width
        adjusted = True
        messages.append("mask_width cannot exceed canvas_width; clamped to canvas")

    if mask_h > request.canvas_height:
        mask_h = request.canvas_height
        adjusted = True
        messages.append("mask_height cannot exceed canvas_height; clamped to canvas")

    canvas = Image.new("RGB", (request.canvas_width, request.canvas_height), "white")
    mask = Image.new("RGB", (mask_w, mask_h), "black")

    left = (request.canvas_width - mask_w) // 2
    top = (request.canvas_height - mask_h) // 2

    canvas.paste(mask, (left, top))

    img_byte_arr = io.BytesIO()
    canvas.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    headers = {}
    if adjusted:
        headers["X-Adjusted"] = "true"
        headers["X-Message"] = "; ".join(messages)
    else:
        headers["X-Adjusted"] = "false"
    # Ensure clients save with .png extension
    headers["Content-Disposition"] = "inline; filename=mask.png"

    return StreamingResponse(img_byte_arr, media_type="image/png", headers=headers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
