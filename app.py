#!/usr/bin/env python3
"""
CityScout Web Application
Flask-based web interface for demographic analysis
"""

from flask import Flask, render_template, request, jsonify
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_collectors import CensusDataCollector, BLSDataCollector
from utils import CityValidator
from config import Config

app = Flask(__name__)
app.secret_key = Config.FLASK_SECRET_KEY

class CityScoutWeb:
    """Web version of CityScout application."""
    
    def __init__(self):
        self.setup_logging()
        self.census_collector = CensusDataCollector()
        self.bls_collector = BLSDataCollector()
        self.logger = logging.getLogger(__name__)
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout) if Config.DEBUG else logging.NullHandler()
            ]
        )
        
    def analyze_city(self, city: str, state: str) -> dict:
        """Perform demographic analysis for a city."""
        try:
            self.logger.info(f"Starting analysis for {city}, {state}")
            
            # Validate inputs
            if not CityValidator.validate_city_name(city):
                raise ValueError(f"Invalid city name: {city}")
            if not CityValidator.validate_state(state):
                raise ValueError(f"Invalid state: {state}")
                
            # Normalize inputs
            city = CityValidator.normalize_city_name(city)
            state = CityValidator.normalize_state(state)
            
            # Collect demographic data
            self.logger.info("Collecting demographic data...")
            demographics = self.census_collector.get_demographics_data(city, state)
            
            self.logger.info("Collecting population growth data...")
            population_growth = self.census_collector.get_population_growth(city, state)
            
            self.logger.info("Collecting employment data...")
            employment = self.bls_collector.get_unemployment_rate(state)
            employment_data = self.bls_collector.get_employment_data(state)
            
            # Combine all data
            combined_data = {
                'city': city,
                'state': state,
                **demographics,
                **population_growth,
                **employment,
                **employment_data
            }
            
            self.logger.info(f"Analysis completed for {city}, {state}")
            return {'success': True, 'data': combined_data}
            
        except Exception as e:
            self.logger.error(f"Error analyzing {city}, {state}: {e}")
            return {'success': False, 'error': str(e)}

# Initialize CityScout
cityscout = CityScoutWeb()

@app.route('/')
def index():
    """Main page with search form."""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """JSON API endpoint for city analysis."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        city = data.get('city', '').strip()
        state = data.get('state', '').strip()
        
        if not city or not state:
            return jsonify({'success': False, 'error': 'City and state are required'}), 400
        
        # Perform analysis
        result = cityscout.analyze_city(city, state)
        return jsonify(result)
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'CityScout Web'})

if __name__ == '__main__':
    print("🏙️ Starting CityScout Web Application...")
    print("📊 Access at: http://localhost:5000")
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)