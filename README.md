# Photo Dump Overlay

A desktop app that composites transparent overlay images onto a batch of photos — automatically picking the right overlay based on each photo's orientation.

## Features

- Select an input folder, an overlay file, and an output folder
- Detects each photo's orientation (landscape / portrait / square)
- Applies the matching overlay (landscape or portrait version)
- Previews the composite before processing
- Batch-processes an entire folder with a progress bar and abort button
- Supports JPG, PNG, BMP, GIF, WebP, and HEIF/HEIC inputs

## Requirements

- Python 3.10 or newer
- pip

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/rxphaelbihag/Photo-Dump-Overlay-2.git
cd Photo-Dump-Overlay-2
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (cmd):**
```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

Run the app:

```bash
python main.py
```

Then:

1. **INPUT** — click **Browse Folder** and select the folder containing your photos.
2. **OVERLAY** — click **Browse File(s)** and select the overlay image(s).
   - Pick **one** file to use for both landscape and portrait.
   - Pick **two** files to use separate overlays for landscape and portrait.
3. **OUTPUT** — click **Browse Folder** to choose where the processed images are saved, and optionally edit the output name prefix.
4. A preview of the first photo with the overlay appears on the right.
5. Click **Overlay All** to process every photo. Use **Abort** to stop early.

Processed images are saved to the output folder using the prefix you set (default: `overlaid_`).

## Project Structure

```
Photo-Dump-Overlay-2/
├── main.py               # Tkinter GUI application
├── overlay_utils.py      # Overlay compositing logic
├── requirements.txt      # Python dependencies
└── .gitignore
```

## How the Overlay Works

- The photo's EXIF orientation is applied first (fixes rotated phone photos).
- If the photo is landscape (width ≥ height), the landscape overlay is used.
- If the photo is portrait (height > width), the portrait overlay is used.
- The overlay is scaled to fully cover the photo using a cover fit (aspect ratio preserved, excess cropped).
- The overlay is pasted centered using its alpha channel as the mask.

## Troubleshooting

**`UnidentifiedImageError` on HEIC files**
Make sure `pillow-heif` is installed and `register_heif_opener()` runs at import (it's already in `overlay_utils.py`). Reinstall with:
```bash
pip install --upgrade pillow-heif
```

**Preview not appearing**
A preview only shows once **both** an input folder and an overlay are selected.

**Nothing happens after clicking Overlay All**
Ensure all three fields are set: input folder, overlay file, and output folder. A warning dialog will tell you which is missing.

## License

No license specified. Contact the repository owner for usage terms.
