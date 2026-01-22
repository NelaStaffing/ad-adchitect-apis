from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI(title="Adchitect APIs")

# Mount sub-applications (APIs)
from MaskGenerator import app as mask_app
app.mount("/mask", mask_app)

@app.get("/")
async def root():
    return {
        "message": "Adchitect API Hub is running",
        "docs": "/docs",
        "services": {
            "mask_generator": {
                "base_url": "/mask",
                "docs": "/mask/docs"
            }
        }
    }

@app.get("/choose")
async def choose(service: str = "mask"):
    targets = {
        "mask": "/mask",
    }
    target = targets.get(service)
    if not target:
        # Unknown service, send to hub root
        return RedirectResponse(url="/")
    return RedirectResponse(url=target)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
