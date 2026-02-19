"""
Manglik Detector Engine - Parashara System
Works with existing Kundli JSON structure to detect Manglik Dosha.

Based on classical Parashara (Parashari) principles:
- Uses sign-based (Rashi) house system
- Manglik Dosha occurs when Mars is placed in houses: 1, 2, 4, 7, 8, 12 from Lagna
- Additional checks from Moon (Chandra Lagna) for comprehensive analysis
"""

from typing import Dict, List, Optional


class ManglikDetector:
    """
    Detects Manglik Dosha using Parashara (Parashari) system.
    
    Parashara Principles:
    - Sign-based house system (each sign = one house)
    - Mars in 1st, 2nd, 4th, 7th, 8th, 12th houses from Lagna causes Manglik
    - Also check from Moon (Chandra Lagna) for complete analysis
    - Mars in own/exalted sign reduces dosha
    - After age 28, dosha effect reduces
    """
    
    # Houses that cause Manglik Dosha (Parashara system)
    MANGLIK_HOUSES = {1, 2, 4, 7, 8, 12}
    
    # Severity scores by house (Parashara system)
    # 7th house = strongest (marriage house)
    # 8th house = very strong (longevity)
    # 1st, 4th = strong (self, happiness)
    # 2nd, 12th = moderate (family, losses)
    SEVERITY_SCORES = {
        1: 3,   # Strong - affects self, personality, health
        2: 2,   # Moderate - affects family, wealth, speech
        4: 3,   # Strong - affects mother, happiness, property
        7: 5,   # Strongest - direct effect on spouse and marriage
        8: 4,   # Very Strong - affects longevity, sudden events
        12: 2,  # Moderate - affects expenses, bed pleasures
    }
    
    # Zodiac signs (Rashis) - each occupies 30 degrees
    ZODIAC_SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    
    # Mars rulership and exaltation (Parashara)
    MARS_OWN_SIGNS = ["Aries", "Scorpio"]  # Mars rules these signs
    MARS_EXALTED_SIGN = "Capricorn"  # Mars exalted
    MARS_DEBILITATED_SIGN = "Cancer"  # Mars debilitated (increases dosha)
    MARS_FRIEND_SIGNS = ["Leo", "Sagittarius", "Pisces"]  # Mars friendly signs
    
    def __init__(self, check_from_moon: bool = True):
        """
        Initialize the Manglik Detector with Parashara principles.
        
        Args:
            check_from_moon: If True, also checks Mars position from Moon (Chandra Lagna)
                           This is recommended in Parashara system for complete analysis
        """
        self.check_from_moon = check_from_moon
    
    def get_sign_number(self, longitude: float) -> int:
        """
        Get zodiac sign number from longitude (Parashara system).
        
        Args:
            longitude: Planet longitude (0-360 degrees)
            
        Returns:
            Sign number (0-11, where 0=Aries, 11=Pisces)
        """
        # Normalize longitude to 0-360 range (handle edge cases)
        normalized = longitude % 360
        return int(normalized / 30) % 12
    
    def get_zodiac_sign(self, longitude: float) -> str:
        """
        Get zodiac sign name from longitude.
        
        Args:
            longitude: Planet longitude (0-360 degrees)
            
        Returns:
            Zodiac sign name
        """
        sign_index = self.get_sign_number(longitude)
        return self.ZODIAC_SIGNS[sign_index]
    
    def calculate_house_from_longitude(
        self,
        planet_longitude: float,
        reference_longitude: float
    ) -> int:
        """
        Calculate house position using Parashara sign-based system.
        
        In Parashara system:
        - Each sign (Rashi) is treated as one house (Bhava)
        - The sign where Lagna falls becomes 1st house
        - Next sign in zodiacal order is 2nd house, and so on
        
        Args:
            planet_longitude: Longitude of the planet (0-360 degrees)
            reference_longitude: Longitude of the reference point (Lagna/Moon) (0-360 degrees)
            
        Returns:
            House number (1-12)
        """
        # Get sign numbers
        planet_sign = self.get_sign_number(planet_longitude)
        reference_sign = self.get_sign_number(reference_longitude)
        
        # Calculate house: count signs from reference sign
        # In Parashara, the sign containing Lagna is house 1
        house = ((planet_sign - reference_sign) % 12) + 1
        
        return house
    
    def detect_manglik(self, kundli_data: Dict) -> Dict:
        """
        Main method to detect Manglik Dosha using Parashara system.
        
        Parashara Analysis:
        1. Check Mars position from Lagna (Ascendant)
        2. Check Mars position from Chandra (Moon) - if enabled
        3. Manglik if Mars in houses 1,2,4,7,8,12 from either Lagna or Moon
        4. Check for cancellations (own sign, exalted, friendly signs)
        
        Args:
            kundli_data: Dictionary containing Kundli information with planetary_longitudes
            
        Expected kundli_data format:
        {
            "planetary_longitudes": {
                "mars": 190.5,      # Mars longitude (required)
                "ascendant": 49.464221,  # Ascendant/Lagna longitude (required)
                "moon": 125.194925  # Moon longitude (optional, for Chandra Lagna check)
            }
        }
        
        Returns:
            Dictionary with Manglik detection results
        """
        try:
            # Extract planetary longitudes
            planetary_longitudes = kundli_data.get("planetary_longitudes", {})
            
            # Check if Mars longitude exists
            if "mars" not in planetary_longitudes:
                return {
                    "error": "Mars longitude not found in Kundli data",
                    "is_manglik": None,
                    "message": "Please ensure 'mars' is present in planetary_longitudes"
                }
            
            # Check if Ascendant longitude exists
            if "ascendant" not in planetary_longitudes:
                return {
                    "error": "Ascendant longitude not found in Kundli data",
                    "is_manglik": None,
                    "message": "Please ensure 'ascendant' is present in planetary_longitudes"
                }
            
            mars_longitude = planetary_longitudes["mars"]
            ascendant_longitude = planetary_longitudes["ascendant"]
            moon_longitude = planetary_longitudes.get("moon")
            
            # Calculate Mars house position from Lagna (Ascendant)
            mars_house_from_lagna = self.calculate_house_from_longitude(
                mars_longitude, ascendant_longitude
            )
            
            # Get Mars zodiac sign
            mars_sign = self.get_zodiac_sign(mars_longitude)
            mars_rashi_number = self.get_sign_number(mars_longitude) + 1
            
            # Detect Manglik from Lagna
            is_manglik_from_lagna = mars_house_from_lagna in self.MANGLIK_HOUSES
            
            # Check from Moon (Chandra Lagna) if available and enabled
            is_manglik_from_moon = False
            mars_house_from_moon = None
            
            if self.check_from_moon and moon_longitude is not None:
                mars_house_from_moon = self.calculate_house_from_longitude(
                    mars_longitude, moon_longitude
                )
                is_manglik_from_moon = mars_house_from_moon in self.MANGLIK_HOUSES
            
            # Parashara: Manglik if Mars in dosha houses from EITHER Lagna OR Moon
            is_manglik = is_manglik_from_lagna or is_manglik_from_moon
            
            # Calculate severity (use higher severity from Lagna or Moon)
            severity = "None"
            severity_score = 0
            
            if is_manglik:
                score_from_lagna = self.SEVERITY_SCORES.get(mars_house_from_lagna, 0)
                score_from_moon = 0
                if mars_house_from_moon:
                    score_from_moon = self.SEVERITY_SCORES.get(mars_house_from_moon, 0)
                
                severity_score = max(score_from_lagna, score_from_moon)
                
                if severity_score >= 5:
                    severity = "Very High"
                elif severity_score >= 4:
                    severity = "High"
                elif severity_score >= 3:
                    severity = "Medium"
                elif severity_score >= 2:
                    severity = "Low"
                else:
                    severity = "Mild"
            
            # Check for cancellations (Parashara principles)
            cancellations = self._check_parashara_cancellations(
                mars_sign, mars_house_from_lagna, mars_house_from_moon, kundli_data
            )
            
            # Build result
            result = {
                "is_manglik": is_manglik,
                "system": "Parashara (Parashari)",
                "mars_house_from_lagna": mars_house_from_lagna,
                "mars_house_from_moon": mars_house_from_moon,
                "is_manglik_from_lagna": is_manglik_from_lagna,
                "is_manglik_from_moon": is_manglik_from_moon,
                "mars_sign": mars_sign,
                "mars_rashi_number": mars_rashi_number,
                "mars_longitude": round(mars_longitude, 2),
                "severity": severity,
                "severity_score": severity_score,
                "explanation": self._get_parashara_explanation(
                    mars_house_from_lagna, mars_house_from_moon, is_manglik_from_lagna, is_manglik_from_moon
                ),
                "cancellations": cancellations,
                "is_cancelled": len(cancellations) > 0,
                "dosha_strength": self._calculate_dosha_strength(severity_score, len(cancellations)),
                "recommendation": self._get_parashara_recommendation(is_manglik, cancellations, mars_sign)
            }
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "is_manglik": None,
                "message": "Error processing Kundli data"
            }
    
    
    def _get_parashara_explanation(
        self, 
        house_from_lagna: int, 
        house_from_moon: Optional[int],
        is_manglik_from_lagna: bool,
        is_manglik_from_moon: bool
    ) -> str:
        """Get detailed explanation based on Parashara system."""
        
        if not is_manglik_from_lagna and not is_manglik_from_moon:
            return f"Mars is in {house_from_lagna}th house from Lagna. According to Parashara system, no Manglik Dosha detected."
        
        explanations = {
            1: "1st house (Tanu Bhava): Affects self, personality, health, and physical appearance. May cause aggression.",
            2: "2nd house (Dhana Bhava): Affects family relations, wealth, speech. May cause family disputes.",
            4: "4th house (Sukha Bhava): Affects mother, happiness, property, vehicles. May disturb domestic peace.",
            7: "7th house (Kalatra Bhava): Direct effect on spouse and marriage. Strongest Manglik position per Parashara.",
            8: "8th house (Ayu Bhava): Affects longevity, sudden events, transformation. Strong dosha position.",
            12: "12th house (Vyaya Bhava): Affects expenses, bed pleasures, foreign travels. May impact marital intimacy."
        }
        
        explanation_parts = []
        
        if is_manglik_from_lagna:
            exp = explanations.get(house_from_lagna, f"{house_from_lagna}th house")
            explanation_parts.append(f"Mars in {exp} from Lagna (Ascendant)")
        
        if is_manglik_from_moon and house_from_moon:
            exp = explanations.get(house_from_moon, f"{house_from_moon}th house")
            explanation_parts.append(f"Mars in {exp} from Chandra (Moon)")
        
        return ". ".join(explanation_parts) + ". Parashara considers this a Manglik position."
    
    def _calculate_dosha_strength(self, severity_score: int, cancellation_count: int) -> str:
        """Calculate overall dosha strength considering cancellations."""
        if severity_score == 0:
            return "No Dosha"
        
        effective_score = severity_score - (cancellation_count * 1.5)
        
        if effective_score <= 0:
            return "Fully Cancelled"
        elif effective_score <= 1:
            return "Negligible"
        elif effective_score <= 2:
            return "Weak"
        elif effective_score <= 3:
            return "Moderate"
        elif effective_score <= 4:
            return "Strong"
        else:
            return "Very Strong"
    
    
    def _check_parashara_cancellations(
        self,
        mars_sign: str,
        mars_house_from_lagna: int,
        mars_house_from_moon: Optional[int],
        kundli_data: Dict
    ) -> List[str]:
        """
        Check for Manglik cancellations according to Parashara principles.
        
        Parashara Cancellations:
        1. Mars in own sign (Aries/Scorpio) - Swakshetra
        2. Mars exalted (Capricorn) - Uccha
        3. Mars in friendly signs (Leo, Sagittarius, Pisces)
        4. Mars with benefics (Jupiter, Venus, Mercury)
        5. Both partners Manglik
        6. Age above 28 years (dosha naturally weakens)
        
        Args:
            mars_sign: Zodiac sign where Mars is placed
            mars_house_from_lagna: House from Lagna
            mars_house_from_moon: House from Moon
            kundli_data: Full Kundli data
            
        Returns:
            List of cancellation factors
        """
        cancellations = []
        
        # 1. Mars in own sign (Swakshetra) - Strong cancellation
        if mars_sign in self.MARS_OWN_SIGNS:
            cancellations.append(
                f"Swakshetra: Mars in own sign ({mars_sign}) - significantly reduces dosha per Parashara"
            )
        
        # 2. Mars exalted (Uccha) - Very strong cancellation
        if mars_sign == self.MARS_EXALTED_SIGN:
            cancellations.append(
                "Uccha: Mars exalted in Capricorn - greatly reduces dosha effects (Parashara principle)"
            )
        
        # 3. Mars in friendly signs - Moderate cancellation
        if mars_sign in self.MARS_FRIEND_SIGNS:
            cancellations.append(
                f"Mitra Rashi: Mars in friendly sign ({mars_sign}) - reduces dosha intensity"
            )
        
        # 4. Mars debilitated (Note: This INCREASES dosha, not a cancellation)
        # We note it but don't add to cancellations
        if mars_sign == self.MARS_DEBILITATED_SIGN:
            # This is noted separately, not a cancellation
            pass
        
        # 5. Check if Mars is Manglik only from one (Lagna or Moon) but not both
        # If only from one source, it's considered weaker dosha
        if mars_house_from_moon is not None:
            is_manglik_lagna = mars_house_from_lagna in self.MANGLIK_HOUSES
            is_manglik_moon = mars_house_from_moon in self.MANGLIK_HOUSES
            
            if is_manglik_lagna and not is_manglik_moon:
                cancellations.append(
                    "Partial Dosha: Mars creates dosha only from Lagna, not from Moon - reduces intensity"
                )
            elif is_manglik_moon and not is_manglik_lagna:
                cancellations.append(
                    "Partial Dosha: Mars creates dosha only from Moon, not from Lagna - reduces intensity"
                )
        
        # Additional Parashara considerations (if planetary data available)
        planetary_longitudes = kundli_data.get("planetary_longitudes", {})
        
        # Check for benefic conjunctions (if Jupiter, Venus, Mercury available)
        mars_longitude = planetary_longitudes.get("mars", 0)
        mars_sign_num = self.get_sign_number(mars_longitude)
        
        # Jupiter conjunction (strong cancellation)
        if "jupiter" in planetary_longitudes:
            jupiter_sign_num = self.get_sign_number(planetary_longitudes["jupiter"])
            if jupiter_sign_num == mars_sign_num:
                cancellations.append(
                    "Guru Yukti: Mars conjunct Jupiter - benefic influence reduces dosha (Parashara)"
                )
        
        # Venus conjunction (moderate cancellation)
        if "venus" in planetary_longitudes:
            venus_sign_num = self.get_sign_number(planetary_longitudes["venus"])
            if venus_sign_num == mars_sign_num:
                cancellations.append(
                    "Shukra Yukti: Mars conjunct Venus - reduces dosha intensity"
                )
        
        return cancellations
    
    
    def _get_parashara_recommendation(
        self, 
        is_manglik: bool, 
        cancellations: List[str],
        mars_sign: str
    ) -> str:
        """Get recommendation based on Parashara principles."""
        if not is_manglik:
            return "No Manglik Dosha detected per Parashara system. Mars is favorably placed."
        
        if len(cancellations) >= 2:
            return "Manglik Dosha present but significantly cancelled by multiple factors. Effects are greatly reduced. Consult a qualified Jyotishi (Vedic astrologer) for personalized guidance."
        
        if cancellations:
            return "Manglik Dosha present with some cancellation factors. Parashara recommends: Match with another Manglik native, perform remedies like Kumbh Vivah, observe Tuesday fasts, recite Hanuman Chalisa, or donate red items. Consult a Jyotishi for personalized remedies."
        
        # No cancellations - full dosha
        remedies = [
            "Parashara remedies for Manglik Dosha:",
            "1. Marriage with another Manglik native (mutual cancellation)",
            "2. Kumbh Vivah ritual before actual marriage",
            "3. Fast on Tuesdays and offer water to Peepal tree",
            "4. Recite Mangal Stotra or Hanuman Chalisa daily",
            "5. Donate red items (clothes, lentils) on Tuesdays",
            "6. Worship Lord Hanuman or Kartikeya",
            "7. Wear red coral gemstone (after astrological consultation)"
        ]
        
        if mars_sign == self.MARS_DEBILITATED_SIGN:
            remedies.append("Note: Mars debilitated in Cancer increases dosha intensity")
        
        return " ".join(remedies) + ". Always consult an experienced Jyotishi for personalized guidance and muhurta selection."
    
    def batch_detect(self, kundli_list: List[Dict]) -> List[Dict]:
        """
        Detect Manglik Dosha for multiple Kundlis.
        
        Args:
            kundli_list: List of Kundli data dictionaries
            
        Returns:
            List of detection results
        """
        results = []
        for kundli in kundli_list:
            result = self.detect_manglik(kundli)
            results.append(result)
        return results


# Standalone function for quick API integration
def is_manglik(kundli_data: Dict, check_from_moon: bool = True) -> Dict:
    """
    Quick function to detect Manglik Dosha using Parashara system.
    
    Args:
        kundli_data: Kundli dictionary with planetary_longitudes
        check_from_moon: Check Mars position from Moon (Chandra Lagna) as per Parashara
        
    Returns:
        Dictionary with Manglik detection results
        
    Example:
        >>> kundli = {
        ...     "planetary_longitudes": {
        ...         "mars": 190.5,
        ...         "ascendant": 49.464221,
        ...         "moon": 125.194925
        ...     }
        ... }
        >>> result = is_manglik(kundli)
        >>> print(result["is_manglik"])
    """
    detector = ManglikDetector(check_from_moon=check_from_moon)
    return detector.detect_manglik(kundli_data)
