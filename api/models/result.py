from pydantic import BaseModel, Field
from typing import List, Optional, Tuple


class Result(BaseModel):
    meta_keys: List[str] = Field(default_factory=list)
    image_size: Tuple[int, ...] = ()
    Max: float = 0.0
    Min: float = 0.0
    distances: List[float] = Field(default_factory=list)
    pixels_presence: List[int] = Field(default_factory=list)
    error: Optional[str] = None