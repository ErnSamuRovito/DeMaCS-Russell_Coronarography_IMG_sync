from pydantic import BaseModel, Field
from typing import List, Tuple

class Result(BaseModel):
    meta_keys: List[str] = Field(default_factory=list)
    image_size: Tuple[int, int, int] = (0, 0, 0)
    Max: int = 0
    Min: int = 0
    distances: List[float] = Field(default_factory=list)
    pixels_presence: List[int] = Field(default_factory=list)
