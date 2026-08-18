from pathlib import Path
from PIL import Image

SOURCE_DIRS = [
    Path("public/images"),
    Path("public/photographs"),
]

OUTPUT_ROOT = Path("compressed-images")

MAX_WIDTH = 2400
JPEG_QUALITY = 82
WEBP_QUALITY = 82


def compress_image(source, destination):
    try:
        with Image.open(source) as img:
            # Convert images with transparency appropriately
            if img.mode in ("RGBA", "LA"):
                if source.suffix.lower() in [".jpg", ".jpeg"]:
                    background = Image.new("RGB", img.size, "white")
                    background.paste(img, mask=img.getchannel("A"))
                    img = background
            elif img.mode not in ("RGB", "L"):
                img = img.convert("RGB")

            # Resize only very large images
            if img.width > MAX_WIDTH:
                new_height = round(img.height * MAX_WIDTH / img.width)
                img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)

            destination.parent.mkdir(parents=True, exist_ok=True)

            # Keep the original format
            suffix = source.suffix.lower()

            if suffix in [".jpg", ".jpeg"]:
                img.save(
                    destination,
                    "JPEG",
                    quality=JPEG_QUALITY,
                    optimize=True,
                    progressive=True,
                )

            elif suffix == ".webp":
                img.save(
                    destination,
                    "WEBP",
                    quality=WEBP_QUALITY,
                    method=6,
                )

            else:
                # Copy unsupported formats unchanged
                source.replace(destination)

    except Exception as e:
        print(f"ERROR: {source}")
        print(e)


for source_dir in SOURCE_DIRS:
    if not source_dir.exists():
        print(f"Skipping missing folder: {source_dir}")
        continue

    for source in source_dir.rglob("*"):
        if source.is_file() and source.suffix.lower() in [
            ".jpg", ".jpeg", ".webp"
        ]:
            relative = source.relative_to(source_dir)
            destination = OUTPUT_ROOT / source_dir.name / relative

            original_size = source.stat().st_size

            compress_image(source, destination)

            if destination.exists():
                new_size = destination.stat().st_size
                reduction = (1 - new_size / original_size) * 100

                print(
                    f"{source.name}: "
                    f"{original_size / 1024 / 1024:.2f} MB -> "
                    f"{new_size / 1024 / 1024:.2f} MB "
                    f"({reduction:.0f}% smaller)"
                )

print("\nDone.")
print(f"Compressed images are in: {OUTPUT_ROOT}")