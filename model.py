from enum import Enum

from pydantic import BaseModel, field_validator


class NewsCategory(str, Enum):
    WAR_CONFLICT = "war_conflict"
    ADVERTISEMENT = "advertisement"
    POLITICS = "politics"
    ECONOMY = "economy"
    SOCIAL = "social"
    SPORTS = "sports"
    CULTURE_ART = "culture_art"
    SCIENCE_TECH = "science_tech"
    UNKNOWN = "unknown"  # fallback


class NewsPost(BaseModel):
    sid: str
    text: str
    category: NewsCategory | None

    @field_validator("category", mode="before")
    @classmethod
    def fallback_category(cls, v):
        if v is None or isinstance(v, NewsCategory):
            return v
        try:
            return NewsCategory(v)
        except ValueError:
            return None
