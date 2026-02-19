from typing import Dict, Any, Tuple
import swisseph as swe
import pytz
from datetime import datetime
from pydantic import ValidationError

from .models import KundliRequest
from .utils import zodiac_sign, nakshatra_and_pada

# Initialize Swiss Ephemeris
try:
    swe.set_ephe_path(None)  # Use built-in ephemeris
    swe.set_sid_mode(swe.SIDM_LAHIRI)  # Use Lahiri Ayanamsa
    swe.set_topo(0, 0, 0)  # Reset any previous topocentric settings
except Exception as e:
    raise RuntimeError(f"Failed to initialize Swiss Ephemeris: {str(e)}")

def validate_coordinates(latitude: float, longitude: float) -> None:
    """Validate latitude and longitude values."""
    if not (-90 <= latitude <= 90):
        raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
    if not (-180 <= longitude <= 180):
        raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")

def parse_datetime(date_str: str, time_str: str, timezone_str: str) -> Tuple[float, datetime]:
    """Parse and validate datetime input."""
    try:
        # Parse the input datetime
        dt = datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %I:%M %p")
        
        # Get timezone
        try:
            local_tz = pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f"Unknown timezone: {timezone_str}")
        
        # Localize and convert to UTC
        local_dt = local_tz.localize(dt, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        
        # Calculate Julian Day
        jd = swe.julday(
            utc_dt.year,
            utc_dt.month,
            utc_dt.day,
            utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
        )
        
        return jd, utc_dt
    except ValueError as e:
        raise ValueError(f"Invalid date/time format: {str(e)}. Expected format: 'DD-MM-YYYY HH:MM AM/PM'")

def calculate_planetary_positions(jd: float, latitude: float, longitude: float) -> Dict[str, Any]:
    """Calculate planetary positions and house cusps."""
    try:
        # Tropical houses (Placidus)
        houses, ascmc = swe.houses(jd, latitude, longitude, b'P')
        asc_tropical = ascmc[0]

        # Lahiri ayanamsa for this Julian day (we already set SIDM_LAHIRI above)
        ayan = swe.get_ayanamsa_ut(jd)

        # Convert ascendant to sidereal longitude
        asc_sidereal = (asc_tropical - ayan) % 360.0

        # Calculate planetary positions (sidereal)
        iflag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

        sun = swe.calc_ut(jd, swe.SUN, iflag)
        sun_long = sun[0][0]

        moon = swe.calc_ut(jd, swe.MOON, iflag)
        moon_long = moon[0][0]

        return {
            "sun_long": sun_long,
            "moon_long": moon_long,
            "asc_long": asc_sidereal,
        }
    except Exception as e:
        raise RuntimeError(f"Astronomical calculation failed: {str(e)}")

def calculate_confidence(moon_long: float, asc_long: float) -> int:
    """Calculate confidence score based on planetary positions."""
    confidence = 100
    
    # Reduce confidence if near nakshatra boundary
    nakshatra_boundary = 13 + 1/3
    moon_pos = moon_long % nakshatra_boundary
    if moon_pos < 0.5 or moon_pos > (nakshatra_boundary - 0.5):
        confidence -= 5
    
    # Reduce confidence if near sign boundary
    asc_pos = asc_long % 30
    if asc_pos < 0.5 or asc_pos > 29.5:
        confidence -= 5
    
    return max(confidence, 0)  # Ensure confidence doesn't go below 0

def generate_kundli(data: KundliRequest) -> Dict[str, Any]:
    """
    Generate a kundli (astrological chart) based on birth details.
    
    Args:
        data: KundliRequest object containing birth details
        
    Returns:
        Dict containing kundli data
        
    Raises:
        ValueError: If input validation fails
        RuntimeError: If there's an error in astronomical calculations
    """
    # Validate coordinates
    validate_coordinates(data.latitude, data.longitude)
    
    # Parse and validate datetime
    jd, utc_dt = parse_datetime(data.date, data.time, data.timezone)
    
    # Calculate planetary positions
    positions = calculate_planetary_positions(jd, data.latitude, data.longitude)
    
    # Calculate derived data
    sun_sign = zodiac_sign(positions["sun_long"])
    moon_sign = zodiac_sign(positions["moon_long"])
    asc_sign = zodiac_sign(positions["asc_long"])
    nakshatra, pada = nakshatra_and_pada(positions["moon_long"])
    
    # Calculate confidence score
    confidence = calculate_confidence(positions["moon_long"], positions["asc_long"])
    
    return {
        "sun_sign": sun_sign,
        "moon_sign": moon_sign,
        "ascendant": asc_sign,
        "nakshatra": nakshatra,
        "nakshatra_pada": pada,
        "ayanamsa": "Lahiri",
        "planetary_longitudes": {
            "sun": round(positions["sun_long"], 6),
            "moon": round(positions["moon_long"], 6),
            "ascendant": round(positions["asc_long"], 6)
        },
        "metadata": {
            "calculation_time": utc_dt.isoformat(),
            "timezone": data.timezone,
            "coordinates": {
                "latitude": data.latitude,
                "longitude": data.longitude
            }
        },
        "confidence": confidence
    }
