from typing import Dict, Any, Optional
import json
from datetime import datetime

class DataFormatter:
    """Formats data for various output types (CLI, JSON, CSV)."""
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format currency values."""
        if amount >= 1_000_000:
            return f"${amount/1_000_000:.1f}M"
        elif amount >= 1_000:
            return f"${amount/1_000:.0f}K"
        else:
            return f"${amount:,.0f}"
            
    @staticmethod
    def format_percentage(value: float) -> str:
        """Format percentage values."""
        return f"{value:.1f}%"
        
    @staticmethod
    def format_number(value: float, decimals: int = 1) -> str:
        """Format general numbers."""
        if value >= 1_000_000:
            return f"{value/1_000_000:.{decimals}f}M"
        elif value >= 1_000:
            return f"{value/1_000:.{decimals}f}K"
        else:
            return f"{value:,.{decimals}f}"
            
    @staticmethod
    def format_for_cli(data: Dict[str, Any]) -> str:
        """Format data for command-line output."""
        try:
            output = []
            output.append("=" * 60)
            output.append(f"CityScout Analysis: {data.get('city', 'Unknown City')}")
            output.append("=" * 60)
            
            # Demographics
            output.append("\n📊 DEMOGRAPHICS")
            output.append("-" * 30)
            if 'total_population' in data:
                output.append(f"Population: {DataFormatter.format_number(data['total_population'], 0)}")
            if 'population_growth_5yr' in data:
                output.append(f"5-Year Growth: {DataFormatter.format_percentage(data['population_growth_5yr'])}")
            if 'median_household_income' in data:
                output.append(f"Median Income: {DataFormatter.format_currency(data['median_household_income'])}")
            if 'unemployment_rate' in data:
                output.append(f"Unemployment Rate: {DataFormatter.format_percentage(data['unemployment_rate'])}")
                    
            output.append("\n" + "=" * 60)
            output.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            output.append("=" * 60)
            
            return "\n".join(output)
            
        except Exception as e:
            return f"Error formatting CLI output: {e}"
            
    @staticmethod
    def format_for_json(data: Dict[str, Any]) -> str:
        """Format data for JSON output."""
        try:
            # Create a clean JSON structure
            json_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "tool": "CityScout",
                    "version": "1.0.0"
                },
                "city_info": {
                    "city": data.get('city', ''),
                    "state": data.get('state', ''),
                    "analysis_date": datetime.now().strftime('%Y-%m-%d')
                },
                "demographics": {
                    "total_population": data.get('total_population'),
                    "population_growth_5yr": data.get('population_growth_5yr'),
                    "median_household_income": data.get('median_household_income'),
                    "unemployment_rate": data.get('unemployment_rate')
                }
            }
            
            return json.dumps(json_data, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": f"Error formatting JSON output: {e}"}, indent=2)
            
    @staticmethod
    def format_for_csv(data: Dict[str, Any]) -> str:
        """Format data for CSV output."""
        try:
            headers = [
                "City", "State", "Population", "Population Growth 5yr (%)",
                "Median Income", "Unemployment Rate (%)", "Analysis Date"
            ]
            
            values = [
                data.get('city', ''),
                data.get('state', ''),
                data.get('total_population', ''),
                data.get('population_growth_5yr', ''),
                data.get('median_household_income', ''),
                data.get('unemployment_rate', ''),
                datetime.now().strftime('%Y-%m-%d')
            ]
            
            # Convert values to strings and handle None values
            str_values = [str(v) if v is not None else '' for v in values]
            
            csv_output = ','.join(f'"{header}"' for header in headers) + '\n'
            csv_output += ','.join(f'"{value}"' for value in str_values)
            
            return csv_output
            
        except Exception as e:
            return f"Error formatting CSV output: {e}"
