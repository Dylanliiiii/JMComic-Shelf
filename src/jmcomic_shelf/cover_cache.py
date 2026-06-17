import os

from PIL import Image


class CoverCache:
    def __init__(self, cache_dir: str, max_width: int = 240, quality: int = 82):
        self.cache_dir = cache_dir
        self.max_width = max_width
        self.quality = quality

    def create_thumbnail(self, jm_id: str, source_path: str) -> str:
        os.makedirs(self.cache_dir, exist_ok=True)
        output = os.path.join(self.cache_dir, f'JM{jm_id}.jpg')
        with Image.open(source_path) as img:
            img = img.convert('RGB')
            width, height = img.size
            if width > self.max_width:
                ratio = self.max_width / width
                size = (self.max_width, max(1, round(height * ratio)))
                img = img.resize(size, Image.Resampling.LANCZOS)
            img.save(output, format='JPEG', quality=self.quality, optimize=True)
        return output

    def clear(self) -> int:
        if not os.path.isdir(self.cache_dir):
            return 0

        count = 0
        for name in os.listdir(self.cache_dir):
            if name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                os.remove(os.path.join(self.cache_dir, name))
                count += 1
        return count
