"""
Picture analysis service.

Keeps image analysis lightweight enough for hosted deployments while still
returning useful metadata and OCR text when available.
"""
from pathlib import Path
from typing import Dict

from loguru import logger
from PIL import Image, ImageStat, UnidentifiedImageError


class PictureAnalysesService:
    """Analyze uploaded plant/herb images without requiring a GPU model."""

    def analyze_picture(self, file_path: str) -> str:
        result = self.analyze(file_path)
        return result["caption"]

    def analyze(self, file_path: str) -> Dict[str, str]:
        image_path = Path(file_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {file_path}")

        try:
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                width, height = img.size
                stat = ImageStat.Stat(img.resize((1, 1)))
                avg_r, avg_g, avg_b = [int(v) for v in stat.mean]
        except UnidentifiedImageError as exc:
            raise ValueError("Uploaded file is not a valid image") from exc

        visual_hint = self._visual_hint(avg_r, avg_g, avg_b)
        ocr_text = self._extract_text(image_path)

        caption = (
            f"Uploaded image ({width}x{height}) with {visual_hint}. "
            "Use the visual preview and any extracted text to identify the plant or herb."
        )
        if ocr_text:
            caption += f" Extracted text: {ocr_text[:300]}"

        details = (
            "Image received successfully. This deployment-safe analyzer does not make "
            "a medical identification claim from pixels alone. Verify the plant identity "
            "with a qualified botanist or practitioner before using it medicinally."
        )
        if ocr_text:
            details += f"\n\nText found in image:\n{ocr_text}"

        return {"caption": caption, "details": details}

    def _visual_hint(self, red: int, green: int, blue: int) -> str:
        if green > red + 15 and green > blue + 15:
            return "predominantly green tones"
        if red > green + 15 and red > blue + 15:
            return "warm reddish/brown tones"
        if blue > red + 15 and blue > green + 15:
            return "cool bluish tones"
        return "mixed neutral tones"

    def _extract_text(self, image_path: Path) -> str:
        try:
            import pytesseract

            with Image.open(image_path) as img:
                return pytesseract.image_to_string(img).strip()
        except Exception as exc:
            logger.debug(f"OCR skipped for {image_path.name}: {exc}")
            return ""
