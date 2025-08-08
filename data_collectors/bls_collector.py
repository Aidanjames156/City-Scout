import requests
import pandas as pd
from typing import Dict, Optional, Any
import logging
from config import Config

class BLSDataCollector:
    """Collects employment and labor statistics from Bureau of Labor Statistics API."""
    
    def __init__(self):
        self.api_key = Config.BLS_API_KEY
        self.base_url = Config.BLS_BASE_URL
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # Check if API key is available
        if not self.api_key or self.api_key == 'your_bls_api_key_here':
            self.logger.warning("BLS API key not configured - employment data will be unavailable")
            self.api_available = False
        else:
            self.api_available = True
        
    def get_unemployment_rate(self, state: str) -> Dict[str, Any]:
        """Get unemployment rate for a state (BLS doesn't provide city-level data for all cities)."""
        if not self.api_available:
            self.logger.info("BLS API not available - returning default employment data")
            return {
                'unemployment_rate': None,
                'unemployment_rate_note': 'BLS API key not configured'
            }
            
        try:
            # Use state-level unemployment rate as proxy
            # Format: LAUST + state FIPS + 0000000000 + 03 (unemployment rate)
            state_fips = self._get_state_fips(state)
            series_id = f"LAUS{state_fips}0000000000003"
            
            payload = {
                'seriesid': [series_id],
                'startyear': '2022',
                'endyear': '2023'
            }
            
            if self.api_key:
                payload['registrationkey'] = self.api_key
                
            response = self.session.post(
                self.base_url, 
                json=payload, 
                timeout=Config.DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'REQUEST_SUCCEEDED' and data['Results']['series']:
                series = data['Results']['series'][0]
                if series['data']:
                    latest_rate = float(series['data'][0]['value'])
                    return {
                        'unemployment_rate': latest_rate,
                        'year': series['data'][0]['year'],
                        'period': series['data'][0]['period']
                    }
                    
        except Exception as e:
            self.logger.error(f"Error getting unemployment rate for {state}: {e}")
            
        return {}
        
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
        
    def get_employment_data(self, state: str) -> Dict[str, Any]:
        """Get employment statistics for a state."""
        if not self.api_available:
            self.logger.info("BLS API not available - returning default employment data")
            return {
                'employment_level': None,
                'labor_force': None,
                'employment_note': 'BLS API key not configured'
            }
            
        try:
            # Get employment level and labor force data
            state_fips = self._get_state_fips(state)
            
            # Employment level series
            employment_series = f"LAUS{state_fips}0000000000005"
            # Labor force series
            labor_force_series = f"LAUS{state_fips}0000000000006"
            
            payload = {
                'seriesid': [employment_series, labor_force_series],
                'startyear': '2020',
                'endyear': '2023'
            }
            
            if self.api_key:
                payload['registrationkey'] = self.api_key
                
            response = self.session.post(
                self.base_url, 
                json=payload, 
                timeout=Config.DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'REQUEST_SUCCEEDED' and data['Results']['series']:
                employment_data = {}
                
                for series in data['Results']['series']:
                    if series['data']:
                        latest_value = int(series['data'][0]['value']) * 1000  # BLS data in thousands
                        
                        if employment_series in series['seriesID']:
                            employment_data['employment_level'] = latest_value
                        elif labor_force_series in series['seriesID']:
                            employment_data['labor_force'] = latest_value
                            
                # Calculate employment rate
                if 'employment_level' in employment_data and 'labor_force' in employment_data:
                    employment_rate = (employment_data['employment_level'] / 
                                     employment_data['labor_force'] * 100)
                    employment_data['employment_rate'] = round(employment_rate, 1)
                    
                return employment_data
                
        except Exception as e:
            self.logger.error(f"Error getting employment data for {state}: {e}")
            
        return {}
