from fastapi import FastAPI, APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from PIL import Image
import io

router = APIRouter(prefix="/resize", tags=["Image Resizer"])

app = FastAPI(title="ImageResizer API")


@router.get("/")
async def resizer_root():
    return {"message": "ImageResizer API is running", "docs": "/docs"}


@router.post("/resize")
async def resize_image(
    file: UploadFile = File(..., description="Image file to resize"),
    target_width: int = Form(..., gt=0, description="Target width in pixels"),
    target_height: int = Form(..., gt=0, description="Target height in pixels"),
    background_color: str = Form("white", description="Background color for padding (e.g., 'white', 'black', '#FF0000')")
):
    """
    Resize an image to fit within target dimensions while preserving aspect ratio.
    
    The image will be scaled to fit inside the target box without stretching.
    If the aspect ratios differ, the image is centered and padded with the background color.
    Quality is preserved using high-quality resampling (Lanczos).
    """
    image_data = await file.read()
    img = Image.open(io.BytesIO(image_data))
    
    original_format = img.format or "PNG"
    
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        has_alpha = True
    else:
        has_alpha = False
    
    orig_width, orig_height = img.size
    
    width_ratio = target_width / orig_width
    height_ratio = target_height / orig_height
    scale = min(width_ratio, height_ratio)
    
    new_width = int(orig_width * scale)
    new_height = int(orig_height * scale)
    
    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    
    if has_alpha:
        canvas = Image.new("RGBA", (target_width, target_height), background_color)
    else:
        canvas = Image.new("RGB", (target_width, target_height), background_color)
    
    left = (target_width - new_width) // 2
    top = (target_height - new_height) // 2
    
    if has_alpha:
        canvas.paste(resized_img, (left, top), resized_img)
    else:
        if resized_img.mode != canvas.mode:
            resized_img = resized_img.convert(canvas.mode)
        canvas.paste(resized_img, (left, top))
    
    img_byte_arr = io.BytesIO()
    
    output_format = "PNG" if has_alpha else (original_format if original_format in ["JPEG", "PNG", "WEBP"] else "PNG")
    
    save_kwargs = {"format": output_format}
    if output_format == "JPEG":
        save_kwargs["quality"] = 95
    elif output_format == "WEBP":
        save_kwargs["quality"] = 95
    elif output_format == "PNG":
        save_kwargs["optimize"] = True
    
    canvas.save(img_byte_arr, **save_kwargs)
    img_byte_arr.seek(0)
    
    media_types = {
        "PNG": "image/png",
        "JPEG": "image/jpeg",
        "WEBP": "image/webp"
    }
    media_type = media_types.get(output_format, "image/png")
    
    ext = output_format.lower()
    headers = {
        "Content-Disposition": f"inline; filename=resized.{ext}",
        "X-Original-Size": f"{orig_width}x{orig_height}",
        "X-New-Size": f"{target_width}x{target_height}",
        "X-Scaled-Image-Size": f"{new_width}x{new_height}",
        "X-Scale-Factor": f"{scale:.4f}"
    }
    
    return StreamingResponse(img_byte_arr, media_type=media_type, headers=headers)


app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
