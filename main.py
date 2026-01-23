from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI(title="Adchitect APIs")

# Include routers from sub-modules
from MaskGenerator import router as mask_router
from ImageResizer import router as resizer_router
app.include_router(mask_router)
app.include_router(resizer_router)

@app.get("/")
async def root():
    return {
        "message": "Adchitect API Hub is running",
        "docs": "/docs",
        "services": {
            "mask_generator": {
                "base_url": "/mask",
                "docs": "/mask/docs"
            },
            "image_resizer": {
                "base_url": "/resize",
                "docs": "/resize/docs"
            }
        }
    }

@app.get("/choose")
async def choose(service: str = "mask"):
    targets = {
        "mask": "/mask",
        "resize": "/resize",
    }
    target = targets.get(service)
    if not target:
        # Unknown service, send to hub root
        return RedirectResponse(url="/")
    return RedirectResponse(url=target)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
