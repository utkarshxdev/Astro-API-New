from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum

# ==========================================
# 1. STRICT ENUMS (THE SAFETY LOCK)
# ==========================================

class RashiEnum(str, Enum):
    Aries = "Aries"
    Taurus = "Taurus"
    Gemini = "Gemini"
    Cancer = "Cancer"
    Leo = "Leo"
    Virgo = "Virgo"
    Libra = "Libra"
    Scorpio = "Scorpio"
    Sagittarius = "Sagittarius"
    Capricorn = "Capricorn"
    Aquarius = "Aquarius"
    Pisces = "Pisces"

class NakshatraEnum(str, Enum):
    Ashwini = "Ashwini"
    Bharani = "Bharani"
    Krittika = "Krittika"
    Rohini = "Rohini"
    Mrigashira = "Mrigashira"
    Ardra = "Ardra"
    Punarvasu = "Punarvasu"
    Pushya = "Pushya"
    Ashlesha = "Ashlesha"
    Magha = "Magha"
    Purva_Phalguni = "Purva Phalguni"
    Uttara_Phalguni = "Uttara Phalguni"
    Hasta = "Hasta"
    Chitra = "Chitra"
    Swati = "Swati"
    Vishakha = "Vishakha"
    Anuradha = "Anuradha"
    Jyeshtha = "Jyeshtha"
    Mula = "Mula"
    Purva_Ashadha = "Purva Ashadha"
    Uttara_Ashadha = "Uttara Ashadha"
    Shravana = "Shravana"
    Dhanishta = "Dhanishta"
    Shatabhisha = "Shatabhisha"
    Purva_Bhadrapada = "Purva Bhadrapada"
    Uttara_Bhadrapada = "Uttara Bhadrapada"
    Revati = "Revati"

# ==========================================
# 2. EXISTING KUNDLI MODELS (UNCHANGED)
# ==========================================

class KundliRequest(BaseModel):
    date: str = Field(..., example="13-01-2007")
    time: str = Field(..., example="06:47 PM")
    timezone: str = Field(..., example="Asia/Kolkata")
    latitude: float = Field(..., example=30.2110)
    longitude: float = Field(..., example=74.9455)

class KundliResponse(BaseModel):
    sun_sign: str
    moon_sign: str
    ascendant: str
    nakshatra: str
    nakshatra_pada: int
    ayanamsa: str
    planetary_longitudes: dict
    confidence: int

# ==========================================
# 3. STRICT COMPATIBILITY MODELS
# ==========================================

class CompatibilityProfile(BaseModel):
    """
    Profile using Strict Enums.
    Rejects invalid spelling immediately (422 Error).
    """
    moon_sign: RashiEnum
    nakshatra: NakshatraEnum

class CompatibilityRequest(BaseModel):
    bride: CompatibilityProfile
    groom: CompatibilityProfile

class CompatibilityResponse(BaseModel):
    """
    Response forcing Integer-only arithmetic.
    """
    total_gunas: int  # ✅ FIXED: Strict Integer
    max_gunas: int = 36
    verdict: str
    breakdown: Dict[str, int]  # ✅ FIXED: Integer values only
