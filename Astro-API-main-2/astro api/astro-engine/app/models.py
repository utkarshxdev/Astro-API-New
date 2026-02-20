from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
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


# ==========================================
# 4. ✨ NEW: MANGLIK DETECTION MODELS
# ==========================================

class ManglikRequest(BaseModel):
    """
    Request model for Manglik detection.
    Can use planetary longitudes from kundli generation.
    """
    planetary_longitudes: dict = Field(
        ...,
        description="Planetary longitudes in degrees (0-360)",
        example={
            "mars": 220.5,
            "ascendant": 49.464221,
            "moon": 125.194925
        }
    )
    check_from_moon: bool = Field(
        default=True,
        description="Check Mars position from Moon (Parashara system)"
    )


class ManglikResponse(BaseModel):
    """
    Response model for Manglik detection (Parashara system).
    """
    is_manglik: bool = Field(..., description="Whether the person has Manglik Dosha")
    system: str = Field(default="Parashara (Parashari)", description="Astrological system used")
    
    # Mars position details
    mars_house_from_lagna: int = Field(..., description="Mars house from Lagna (1-12)")
    mars_house_from_moon: Optional[int] = Field(None, description="Mars house from Moon (1-12)")
    is_manglik_from_lagna: bool = Field(..., description="Manglik from Lagna")
    is_manglik_from_moon: bool = Field(..., description="Manglik from Moon")
    
    mars_sign: str = Field(..., description="Zodiac sign where Mars is placed")
    mars_rashi_number: int = Field(..., description="Rashi number (1-12)")
    mars_longitude: float = Field(..., description="Mars longitude in degrees")
    
    # Severity assessment
    severity: str = Field(..., description="Dosha severity level")
    severity_score: int = Field(..., description="Numerical severity score (0-5)")
    dosha_strength: str = Field(..., description="Overall dosha strength after cancellations")
    
    # Analysis
    explanation: str = Field(..., description="Detailed explanation")
    cancellations: List[str] = Field(default_factory=list, description="Cancellation factors")
    is_cancelled: bool = Field(..., description="Whether dosha has cancellations")
    recommendation: str = Field(..., description="Recommendations")


class ManglikCompatibilityRequest(BaseModel):
    """
    Request for Manglik compatibility between two people.
    """
    person1_longitudes: dict = Field(..., description="First person's planetary longitudes")
    person2_longitudes: dict = Field(..., description="Second person's planetary longitudes")
    check_from_moon: bool = Field(default=True, description="Check from Moon")


class ManglikCompatibilityResponse(BaseModel):
    """
    Response for Manglik compatibility check.
    """
    compatible: bool = Field(..., description="Whether compatible regarding Manglik")
    compatibility_type: str = Field(..., description="Type of compatibility")
    reason: str = Field(..., description="Explanation")
    
    person1_analysis: ManglikResponse = Field(..., description="Person 1 analysis")
    person2_analysis: ManglikResponse = Field(..., description="Person 2 analysis")
    
    recommendation: str = Field(..., description="Recommendation for couple")
