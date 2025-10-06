from pydantic import BaseModel
from typing import List, Tuple

class Result(BaseModel):
    meta_keys: List[str] = []
    image_size: Tuple[int, int, int] = (0, 0, 0)
    Max: int = 0
    Min: int = 0
    distances: List[float] = []
    pixels_presence: List[int] = []