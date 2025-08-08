import requests
import pandas as pd
from typing import Dict, Optional, Any
import logging
from config import Config

class CensusDataCollector:
    """Collects demographic and economic data from U.S. Census Bureau API."""
    
    def __init__(self):
        self.api_key = Config.CENSUS_API_KEY
        self.base_url = Config.CENSUS_BASE_URL
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
    def get_city_fips_code(self, city: str, state: str) -> Optional[str]:
        """Get FIPS code for a city and state combination."""
        try:
            # Use places API to find city FIPS code
            url = f"{self.base_url}/2021/acs/acs5"
            params = {
                'get': 'NAME',
                'for': 'place:*',
                'in': f'state:{self._get_state_fips(state)}',
                'key': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=Config.DEFAULT_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            for row in data[1:]:  # Skip header row
                if city.lower() in row[0].lower():
                    return row[-1]  # Return place FIPS code
                    
        except Exception as e:
            self.logger.error(f"Error getting FIPS code for {city}, {state}: {e}")
            
        return None
        
    def _get_state_fips(self, state: str) -> str:
        """Convert state abbreviation to FIPS code."""
        state_fips = {
            'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06',
            'CO': '08', 'CT': '09', 'DE': '10', 'FL': '12', 'GA': '13',
            'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18', 'IA': '19',
            'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23', 'MD': '24',
            'MA': '25', 'MI': '26', 'MN': '27', 'MS': '28', 'MO': '29',
            'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33', 'NJ': '34',
            'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39',
            'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45',
            'SD': '46', 'TN': '47', 'TX': '48', 'UT': '49', 'VT': '50',
            'VA': '51', 'WA': '53', 'WV': '54', 'WI': '55', 'WY': '56'
        }
        return state_fips.get(state.upper(), '00')
        
    def get_demographics_data(self, city: str, state: str) -> Dict[str, Any]:
        """Collect demographic data for a city."""
        try:
            place_fips = self.get_city_fips_code(city, state)
            state_fips = self._get_state_fips(state)
            
            if not place_fips:
                self.logger.warning(f"Could not find FIPS code for {city}, {state}")
                return {}
                
            # Try most recent data sources in order of preference
            # 1-year estimates are more recent but only available for larger places
            data_sources = [
                ('2022/acs/acs1', '1-year estimates (most recent)'),
                ('2022/acs/acs5', '5-year estimates 2022'),
                ('2021/acs/acs1', '1-year estimates 2021'),
                ('2021/acs/acs5', '5-year estimates 2021')
            ]
            
            response = None
            for dataset, description in data_sources:
                try:
                    url = f"{self.base_url}/{dataset}"
                    params = {
                        'get': 'B01003_001E,B19013_001E',
                        'for': f'place:{place_fips}',
                        'in': f'state:{state_fips}',
                        'key': self.api_key
                    }
                    
                    response = self.session.get(url, params=params, timeout=Config.DEFAULT_TIMEOUT)
                    if response.status_code == 200:
                        self.logger.info(f"Using {description} for {city}, {state}")
                        break
                except Exception as e:
                    self.logger.debug(f"Failed to get {description}: {e}")
                    continue
            
            if not response or response.status_code != 200:
                self.logger.error(f"Failed to get Census data for {city}, {state}")
                return {}
                
            response.raise_for_status()
            
            data = response.json()
            if len(data) < 2:
                return {}
                
            row = data[1]  # First data row after header
            
            total_population = int(row[0]) if row[0] != '-999999999' else 0
            median_income = int(row[1]) if row[1] != '-999999999' else 0
            
            return {
                'total_population': total_population,
                'median_household_income': median_income
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting demographics for {city}, {state}: {e}")
            return {}
            
    def get_population_growth(self, city: str, state: str) -> Dict[str, float]:
        """Get population growth rates for a city."""
        try:
            # This would typically require multiple years of data
            # For demo purposes, using estimated growth rates
            # In production, you'd fetch multiple years and calculate actual growth
            
            return {
                'population_growth_1yr': 2.1,  # Placeholder - would calculate from real data
                'population_growth_5yr': 8.5   # Placeholder - would calculate from real data
            }
            
        except Exception as e:
            self.logger.error(f"Error getting population growth for {city}, {state}: {e}")
            return {}
