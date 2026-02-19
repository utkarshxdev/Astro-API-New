from typing import Tuple, Literal, TypeVar, List

# Type aliases
ZodiacSign = Literal[
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NakshatraName = Literal[
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

SIGNS: List[ZodiacSign] = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS: List[NakshatraName] = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

def normalize_degrees(degrees: float) -> float:
    """Normalize degrees to 0-360 range."""
    degrees = degrees % 360
    return degrees + 360 if degrees < 0 else degrees

def zodiac_sign(longitude: float) -> ZodiacSign:
    """
    Calculate the zodiac sign for a given celestial longitude.
    
    Args:
        longitude: Ecliptic longitude in degrees (0-360)
        
    Returns:
        The zodiac sign as a string
        
    Example:
        >>> zodiac_sign(23.5)
        'Aries'
    """
    if not isinstance(longitude, (int, float)):
        raise TypeError(f"Longitude must be a number, got {type(longitude).__name__}")
        
    norm_long = normalize_degrees(longitude)
    sign_index = int(norm_long // 30) % 12
    return SIGNS[sign_index]

def nakshatra_and_pada(moon_longitude: float) -> Tuple[NakshatraName, int]:
    """
    Calculate the nakshatra and pada for a given moon longitude.
    
    Args:
        moon_longitude: Moon's ecliptic longitude in degrees (0-360)
        
    Returns:
        A tuple of (nakshatra_name, pada_number)
        
    Example:
        >>> nakshatra_and_pada(123.45)
        ('Purva Phalguni', 3)
    """
    if not isinstance(moon_longitude, (int, float)):
        raise TypeError(f"Moon longitude must be a number, got {type(moon_longitude).__name__}")
        
    norm_long = normalize_degrees(moon_longitude)
    segment = 13 + 1/3  # 13°20' per nakshatra
    
    # Calculate nakshatra index (0-26)
    nak_index = int(norm_long // segment) % len(NAKSHATRAS)
    
    # Calculate pada (1-4)
    pada = int((norm_long % segment) // (segment / 4)) + 1
    
    # Ensure pada is between 1-4
    pada = max(1, min(4, pada))
    
    return NAKSHATRAS[nak_index], pada  # Ensure pada is between 1-4
