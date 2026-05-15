import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from loguru import logger

class PictureAnalysesService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PictureAnalysesService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        logger.info("Initializing Picture Analyses model (BLIP)...")
        try:
            # Determine device
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            # Using a smaller fast model suitable for general images
            self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(self.device)
            self._initialized = True
            logger.success(f"Picture Analyses model loaded on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load Picture Analyses model: {e}")
            self._initialized = False

    def analyze_picture(self, image_path: str) -> str:
        """Analyzes a picture and returns a descriptive caption."""
        if not self._initialized:
            logger.warning("Picture Analyses model not initialized.")
            return ""

        try:
            raw_image = Image.open(image_path).convert('RGB')
            # unconditional image captioning
            inputs = self.processor(raw_image, return_tensors="pt").to(self.device)
            out = self.model.generate(**inputs, max_new_tokens=50)
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            logger.error(f"Error analyzing picture {image_path}: {e}")
            return ""
