# Adchitect APIs

A collection of image processing APIs built with FastAPI.

## Getting Started

### Installation

```bash
pip install -r requirements.txt
```

### Running the Server

```bash
python main.py
```

The server will start at `http://127.0.0.1:8000`

### API Documentation

Interactive docs available at: `http://127.0.0.1:8000/docs`

---

## Endpoints

### 1. Root

**GET** `/`

Returns API hub status and available services.

#### Example Request

```bash
curl http://127.0.0.1:8000/
```

#### Example Response

```json
{
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
```

---

### 2. Mask Generator

#### GET `/mask/`

Returns Mask Generator API status.

```bash
curl http://127.0.0.1:8000/mask/
```

#### POST `/mask/generate-mask`

Generates a centered black mask on a white canvas.

**Content-Type:** `application/json`

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `canvas_width` | int | Yes | Width of the background canvas (white) |
| `canvas_height` | int | Yes | Height of the background canvas (white) |
| `mask_width` | int | Yes | Width of the inner mask (black) |
| `mask_height` | int | Yes | Height of the inner mask (black) |

#### Example Request

```bash
curl -X POST http://127.0.0.1:8000/mask/generate-mask \
  -H "Content-Type: application/json" \
  -d '{
    "canvas_width": 1920,
    "canvas_height": 1080,
    "mask_width": 800,
    "mask_height": 600
  }' \
  --output mask.png
```

#### Example Payload

```json
{
  "canvas_width": 1920,
  "canvas_height": 1080,
  "mask_width": 800,
  "mask_height": 600
}
```

#### Response

Returns a PNG image with:
- **Headers:**
  - `X-Adjusted`: "true" or "false" (indicates if mask was clamped)
  - `X-Message`: Adjustment messages (if any)
  - `Content-Disposition`: `inline; filename=mask.png`

---

### 3. Image Resizer

#### GET `/resize/`

Returns Image Resizer API status.

```bash
curl http://127.0.0.1:8000/resize/
```

#### POST `/resize/resize`

Resizes an image to fit within target dimensions while **preserving aspect ratio** (no stretching). The image is centered and padded if aspect ratios differ.

**Content-Type:** `multipart/form-data`

**Form Fields:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `file` | file | Yes | - | Image file to resize |
| `target_width` | int | Yes | - | Target width in pixels |
| `target_height` | int | Yes | - | Target height in pixels |
| `background_color` | string | No | "white" | Background/padding color (e.g., "white", "black", "#FF0000") |

#### Example Request

```bash
curl -X POST http://127.0.0.1:8000/resize/resize \
  -F "file=@input.jpg" \
  -F "target_width=1920" \
  -F "target_height=1080" \
  -F "background_color=white" \
  --output resized.png
```

#### Example with Python (requests)

```python
import requests

url = "http://127.0.0.1:8000/resize/resize"

with open("input.jpg", "rb") as f:
    files = {"file": ("input.jpg", f, "image/jpeg")}
    data = {
        "target_width": 1920,
        "target_height": 1080,
        "background_color": "white"
    }
    response = requests.post(url, files=files, data=data)

with open("resized.png", "wb") as f:
    f.write(response.content)
```

#### Response

Returns the resized image with:
- **Headers:**
  - `X-Original-Size`: Original dimensions (e.g., "3000x2000")
  - `X-New-Size`: Target canvas size (e.g., "1920x1080")
  - `X-Scaled-Image-Size`: Actual scaled image size (e.g., "1620x1080")
  - `X-Scale-Factor`: Scale factor applied (e.g., "0.5400")
  - `Content-Disposition`: `inline; filename=resized.{ext}`

---

## Response Headers Reference

### Mask Generator Headers

| Header | Description |
|--------|-------------|
| `X-Adjusted` | "true" if mask dimensions were clamped to fit canvas |
| `X-Message` | Details about adjustments made |

### Image Resizer Headers

| Header | Description |
|--------|-------------|
| `X-Original-Size` | Original image dimensions |
| `X-New-Size` | Requested target dimensions |
| `X-Scaled-Image-Size` | Actual dimensions of scaled image (before padding) |
| `X-Scale-Factor` | Scale multiplier applied to preserve aspect ratio |

---

## Notes

- **Aspect Ratio Preservation**: The resize endpoint scales images to fit within the target box without stretching. If the aspect ratio differs, the image is centered with padding.
- **Quality**: Uses Lanczos resampling for high-quality results. JPEG/WEBP outputs use 95% quality.
- **Transparency**: Images with alpha channels are preserved and output as PNG.
