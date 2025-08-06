from pydantic import BaseModel
from typing import List

class RegionData(BaseModel):
    child_population: int
    conflict_risk: int
    food_insecurity: int  # 0: Low, 1: Medium, 2: High
    school_destruction_rate: float
    water_access: int      # 0: Good, 1: Medium, 2: Poor
    recent_aid_delivered: int
    displacement_level: int

class BatchRegionData(BaseModel):
    regions: List[RegionData] 