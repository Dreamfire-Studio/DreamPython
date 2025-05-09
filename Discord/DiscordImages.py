from discord import File
from typing import List

class DiscordImages:
    def return_image_file_array(self, image_paths: List[str]) -> List[File]:
        return [File(image_path) for image_path in image_paths]