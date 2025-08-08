import re
from typing import Optional, Tuple

class CityValidator:
    """Validates and normalizes city and state inputs."""
    
    # US state abbreviations
    US_STATES = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
        'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
        'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
        'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
        'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
    }
    
    @classmethod
    def validate_city_name(cls, city: str) -> bool:
        """Validate city name format."""
        if not city or not isinstance(city, str):
            return False
            
        # Remove extra whitespace
        city = city.strip()
        
        # Check length
        if len(city) < 2 or len(city) > 50:
            return False
            
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", city):
            return False
            
        return True
        
    @classmethod
    def validate_state(cls, state: str) -> bool:
        """Validate state abbreviation or name."""
        if not state or not isinstance(state, str):
            return False
            
        state = state.strip().upper()
        
        # Check if it's a valid state abbreviation
        if state in cls.US_STATES:
            return True
            
        # Check if it's a valid state name
        state_names = [name.upper() for name in cls.US_STATES.values()]
        if state in state_names:
            return True
            
        return False
        
    @classmethod
    def normalize_city_name(cls, city: str) -> str:
        """Normalize city name to standard format."""
        if not cls.validate_city_name(city):
            raise ValueError(f"Invalid city name: {city}")
            
        # Remove extra whitespace and capitalize properly
        city = city.strip()
        
        # Handle special cases for city names
        # Split by spaces and capitalize each word
        words = city.split()
        normalized_words = []
        
        for word in words:
            # Handle hyphenated words
            if '-' in word:
                hyphen_parts = word.split('-')
                normalized_hyphen = '-'.join([part.capitalize() for part in hyphen_parts])
                normalized_words.append(normalized_hyphen)
            # Handle apostrophes
            elif "'" in word:
                apos_parts = word.split("'")
                normalized_apos = "'".join([apos_parts[0].capitalize()] + 
                                         [part.lower() if len(part) > 1 else part.lower() 
                                          for part in apos_parts[1:]])
                normalized_words.append(normalized_apos)
            else:
                normalized_words.append(word.capitalize())
                
        return ' '.join(normalized_words)
        
    @classmethod
    def normalize_state(cls, state: str) -> str:
        """Normalize state to standard abbreviation format."""
        if not cls.validate_state(state):
            raise ValueError(f"Invalid state: {state}")
            
        state = state.strip().upper()
        
        # If it's already an abbreviation, return it
        if state in cls.US_STATES:
            return state
            
        # Find the abbreviation for the state name
        for abbrev, name in cls.US_STATES.items():
            if name.upper() == state:
                return abbrev
                
        raise ValueError(f"Could not normalize state: {state}")
        
    @classmethod
    def parse_location(cls, location: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse a location string to extract city and state.
        Handles formats like:
        - "Tampa, FL"
        - "Tampa, Florida"
        - "New York City, NY"
        - "St. Louis, Missouri"
        """
        if not location or not isinstance(location, str):
            return None, None
            
        # Split by comma
        parts = [part.strip() for part in location.split(',')]
        
        if len(parts) == 2:
            city_part, state_part = parts
            
            try:
                normalized_city = cls.normalize_city_name(city_part)
                normalized_state = cls.normalize_state(state_part)
                return normalized_city, normalized_state
            except ValueError:
                return None, None
        elif len(parts) == 1:
            # Only city provided
            try:
                normalized_city = cls.normalize_city_name(parts[0])
                return normalized_city, None
            except ValueError:
                return None, None
        else:
            return None, None
            
    @classmethod
    def suggest_corrections(cls, city: str, state: str) -> dict:
        """Suggest corrections for invalid city/state inputs."""
        suggestions = {'city': [], 'state': []}
        
        # State suggestions
        if state and not cls.validate_state(state):
            state_upper = state.upper()
            
            # Look for partial matches in state names
            for abbrev, name in cls.US_STATES.items():
                if (state_upper in name.upper() or 
                    name.upper().startswith(state_upper) or
                    abbrev.startswith(state_upper)):
                    suggestions['state'].append(f"{name} ({abbrev})")
                    
        # City suggestions (basic implementation)
        if city and not cls.validate_city_name(city):
            # Remove invalid characters and suggest
            cleaned_city = re.sub(r'[^a-zA-Z\s\-\']', '', city)
            if cleaned_city and cleaned_city != city:
                suggestions['city'].append(cleaned_city)
                
        return suggestions
        
    @classmethod
    def is_major_city(cls, city: str, state: str) -> bool:
        """Check if the city is a major U.S. city (for data availability)."""
        # Major cities that typically have good data availability
        major_cities = {
            'NY': ['New York', 'Buffalo', 'Rochester', 'Syracuse', 'Albany'],
            'CA': ['Los Angeles', 'San Francisco', 'San Diego', 'San Jose', 'Sacramento', 
                   'Fresno', 'Oakland', 'Long Beach', 'Anaheim'],
            'TX': ['Houston', 'Dallas', 'Austin', 'San Antonio', 'Fort Worth', 'El Paso'],
            'FL': ['Miami', 'Tampa', 'Orlando', 'Jacksonville', 'St. Petersburg'],
            'IL': ['Chicago', 'Aurora', 'Rockford', 'Joliet', 'Naperville'],
            'PA': ['Philadelphia', 'Pittsburgh', 'Allentown', 'Erie'],
            'OH': ['Columbus', 'Cleveland', 'Cincinnati', 'Toledo', 'Akron'],
            'GA': ['Atlanta', 'Augusta', 'Columbus', 'Savannah'],
            'NC': ['Charlotte', 'Raleigh', 'Greensboro', 'Durham', 'Winston-Salem'],
            'MI': ['Detroit', 'Grand Rapids', 'Warren', 'Sterling Heights', 'Lansing'],
            'WA': ['Seattle', 'Spokane', 'Tacoma', 'Vancouver', 'Bellevue'],
            'AZ': ['Phoenix', 'Tucson', 'Mesa', 'Chandler', 'Scottsdale'],
            'MA': ['Boston', 'Worcester', 'Springfield', 'Lowell', 'Cambridge'],
            'TN': ['Nashville', 'Memphis', 'Knoxville', 'Chattanooga'],
            'IN': ['Indianapolis', 'Fort Wayne', 'Evansville', 'South Bend'],
            'MO': ['Kansas City', 'St. Louis', 'Springfield', 'Independence'],
            'MD': ['Baltimore', 'Frederick', 'Rockville', 'Gaithersburg'],
            'WI': ['Milwaukee', 'Madison', 'Green Bay', 'Kenosha'],
            'MN': ['Minneapolis', 'St. Paul', 'Plymouth', 'Woodbury'],
            'CO': ['Denver', 'Colorado Springs', 'Aurora', 'Fort Collins', 'Lakewood'],
            'AL': ['Birmingham', 'Montgomery', 'Mobile', 'Huntsville'],
            'SC': ['Charleston', 'Columbia', 'North Charleston', 'Mount Pleasant'],
            'LA': ['New Orleans', 'Baton Rouge', 'Shreveport', 'Lafayette'],
            'KY': ['Louisville', 'Lexington', 'Bowling Green', 'Owensboro'],
            'OR': ['Portland', 'Eugene', 'Salem', 'Gresham'],
            'OK': ['Oklahoma City', 'Tulsa', 'Norman', 'Broken Arrow'],
            'CT': ['Bridgeport', 'New Haven', 'Hartford', 'Stamford'],
            'IA': ['Des Moines', 'Cedar Rapids', 'Davenport', 'Sioux City'],
            'MS': ['Jackson', 'Gulfport', 'Southaven', 'Hattiesburg'],
            'AR': ['Little Rock', 'Fort Smith', 'Fayetteville', 'Springdale'],
            'KS': ['Wichita', 'Overland Park', 'Kansas City', 'Topeka'],
            'UT': ['Salt Lake City', 'West Valley City', 'Provo', 'West Jordan'],
            'NV': ['Las Vegas', 'Henderson', 'Reno', 'North Las Vegas'],
            'NM': ['Albuquerque', 'Las Cruces', 'Rio Rancho', 'Santa Fe'],
            'WV': ['Charleston', 'Huntington', 'Morgantown', 'Parkersburg'],
            'NE': ['Omaha', 'Lincoln', 'Bellevue', 'Grand Island'],
            'ID': ['Boise', 'Meridian', 'Nampa', 'Idaho Falls'],
            'HI': ['Honolulu', 'East Honolulu', 'Pearl City', 'Hilo'],
            'NH': ['Manchester', 'Nashua', 'Concord', 'Derry'],
            'ME': ['Portland', 'Lewiston', 'Bangor', 'South Portland'],
            'RI': ['Providence', 'Cranston', 'Warwick', 'Pawtucket'],
            'MT': ['Billings', 'Missoula', 'Great Falls', 'Bozeman'],
            'DE': ['Wilmington', 'Dover', 'Newark', 'Middletown'],
            'SD': ['Sioux Falls', 'Rapid City', 'Aberdeen', 'Brookings'],
            'ND': ['Fargo', 'Bismarck', 'Grand Forks', 'Minot'],
            'AK': ['Anchorage', 'Fairbanks', 'Juneau', 'Sitka'],
            'DC': ['Washington'],
            'VT': ['Burlington', 'Essex', 'South Burlington', 'Colchester'],
            'WY': ['Cheyenne', 'Casper', 'Laramie', 'Gillette']
        }
        
        state_cities = major_cities.get(state.upper(), [])
        return any(city.lower() in city_name.lower() or city_name.lower() in city.lower() 
                  for city_name in state_cities)
