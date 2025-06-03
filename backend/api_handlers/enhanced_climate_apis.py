"""
Enhanced Climate API Handler with Testing Integration
Includes fallback mechanisms, validation, and comprehensive error handling
"""

import requests
import logging
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from enum import Enum
import sys
import os

# Add parent directories to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, 'tests'))

from config import settings
from tests.mock_data_provider import MockDataProvider
from tests.test_config import TestMode, get_test_config

logger = logging.getLogger(__name__)

class APIStatus(Enum):
    """API response status"""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    MOCK_DATA = "mock_data"

@dataclass
class APIResponse:
    """Standardized API response wrapper"""
    status: APIStatus
    data: Any
    response_time: float
    error_message: Optional[str] = None
    source: str = "live_api"
    metadata: Optional[Dict] = None

class EnhancedClimateAPIHandler:
    """Enhanced handler for climate APIs with testing integration"""
    
    def __init__(self, use_mock_fallback: bool = True, test_mode: TestMode = TestMode.HYBRID):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ClimateIQ-Enhanced/1.0'
        })
        self.mock_provider = MockDataProvider()
        self.use_mock_fallback = use_mock_fallback
        self.test_mode = test_mode
        self.test_config = get_test_config()
        
        # API call statistics
        self.api_stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'mock_calls': 0,
            'average_response_time': 0.0
        }
    
    def _make_request(self, url: str, params: Dict = None, headers: Dict = None, 
                     method: str = "GET", timeout: int = 30, api_name: str = "unknown") -> APIResponse:
        """Make HTTP request with comprehensive error handling and fallback"""
        start_time = time.time()
        self.api_stats['total_calls'] += 1
        
        # Check if we should use mock data
        if self.test_mode == TestMode.MOCK:
            return self._get_mock_response(api_name, url, params)
        
        try:
            # Prepare headers
            request_headers = self.session.headers.copy()
            if headers:
                request_headers.update(headers)
            
            # Make request
            if method.upper() == "GET":
                response = self.session.get(url, params=params, headers=request_headers, timeout=timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, json=params, headers=request_headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response_time = time.time() - start_time
            
            # Handle response
            if response.status_code == 200 or response.status_code == 201:
                self.api_stats['successful_calls'] += 1
                self._update_response_time(response_time)
                
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    data = response.text
                
                return APIResponse(
                    status=APIStatus.SUCCESS,
                    data=data,
                    response_time=response_time,
                    source="live_api",
                    metadata={
                        "status_code": response.status_code,
                        "url": url,
                        "api_name": api_name
                    }
                )
            
            elif response.status_code == 429:  # Rate limited
                self.api_stats['failed_calls'] += 1
                if self.use_mock_fallback and self.test_mode == TestMode.HYBRID:
                    return self._get_mock_response(api_name, url, params, 
                                                 error_message="Rate limited, using mock data")
                
                return APIResponse(
                    status=APIStatus.RATE_LIMITED,
                    data=None,
                    response_time=response_time,
                    error_message=f"Rate limited: {response.status_code}",
                    source="live_api"
                )
            
            else:  # Other HTTP errors
                self.api_stats['failed_calls'] += 1
                if self.use_mock_fallback and self.test_mode == TestMode.HYBRID:
                    return self._get_mock_response(api_name, url, params, 
                                                 error_message=f"HTTP {response.status_code}, using mock data")
                
                return APIResponse(
                    status=APIStatus.FAILURE,
                    data=None,
                    response_time=response_time,
                    error_message=f"HTTP {response.status_code}: {response.text[:200]}",
                    source="live_api"
                )
        
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            self.api_stats['failed_calls'] += 1
            
            if self.use_mock_fallback and self.test_mode == TestMode.HYBRID:
                return self._get_mock_response(api_name, url, params, 
                                             error_message="Request timeout, using mock data")
            
            return APIResponse(
                status=APIStatus.TIMEOUT,
                data=None,
                response_time=response_time,
                error_message="Request timeout",
                source="live_api"
            )
        
        except Exception as e:
            response_time = time.time() - start_time
            self.api_stats['failed_calls'] += 1
            
            if self.use_mock_fallback and self.test_mode == TestMode.HYBRID:
                return self._get_mock_response(api_name, url, params, 
                                             error_message=f"Connection error: {str(e)}, using mock data")
            
            return APIResponse(
                status=APIStatus.FAILURE,
                data=None,
                response_time=response_time,
                error_message=str(e),
                source="live_api"
            )
    
    def _get_mock_response(self, api_name: str, url: str, params: Dict = None, 
                          error_message: str = None) -> APIResponse:
        """Generate mock response based on API and endpoint"""
        start_time = time.time()
        self.api_stats['mock_calls'] += 1
        
        try:
            # Simulate realistic response time
            mock_response_time = 0.1 + (time.time() - start_time)
            
            # Generate mock data based on API and endpoint
            if "climatetrace" in api_name.lower() or "climate" in url:
                data = self._get_climate_trace_mock_data(url, params)
            elif "carboninterface" in api_name.lower() or "carbon" in url:
                data = self._get_carbon_interface_mock_data(params)
            elif "openweathermap" in api_name.lower() or "weather" in url:
                data = self._get_openweather_mock_data(url, params)
            elif "nasa" in api_name.lower() or "power.larc.nasa.gov" in url:
                data = self._get_nasa_power_mock_data(params)
            elif "worldbank" in api_name.lower() or "worldbank.org" in url:
                data = self._get_world_bank_mock_data(url, params)
            elif "unstats.un.org" in url or "sdg" in url:
                data = self._get_un_sdg_mock_data(url)
            else:
                data = {"mock": True, "message": "Generic mock data"}
            
            return APIResponse(
                status=APIStatus.MOCK_DATA,
                data=data,
                response_time=mock_response_time,
                error_message=error_message,
                source="mock_data",
                metadata={
                    "api_name": api_name,
                    "url": url,
                    "mock_provider": "enhanced_handler"
                }
            )
        
        except Exception as e:
            return APIResponse(
                status=APIStatus.FAILURE,
                data=None,
                response_time=time.time() - start_time,
                error_message=f"Mock data generation failed: {str(e)}",
                source="mock_data"
            )
    
    def _get_climate_trace_mock_data(self, url: str, params: Dict = None) -> Any:
        """Generate ClimateTRACE mock data"""
        if "/definitions/sectors" in url:
            return self.mock_provider.get_climate_trace_sectors()["sectors"]
        elif "/definitions/countries" in url:
            return self.mock_provider.get_climate_trace_countries()["countries"]
        elif "/definitions/subsectors" in url:
            return self.mock_provider.get_climate_trace_subsectors()
        elif "/definitions/continents" in url:
            return self.mock_provider.get_climate_trace_continents()
        elif "/definitions/gases" in url:
            return self.mock_provider.get_climate_trace_gases()
        elif "/definitions/groups" in url:
            return self.mock_provider.get_climate_trace_groups()
        elif "/assets/emissions" in url:
            countries = params.get("countries", "").split(",") if params and params.get("countries") else None
            sectors = params.get("sectors", "").split(",") if params and params.get("sectors") else None
            years = params.get("years", "2022").split(",") if params and params.get("years") else ["2022"]
            gas = params.get("gas", "co2e_100yr") if params else "co2e_100yr"
            return self.mock_provider.get_climate_trace_asset_emissions(years, gas, countries, sectors)
        elif "/country/emissions" in url:
            countries = params.get("countries", "").split(",") if params and params.get("countries") else None
            since = int(params.get("since", 2022)) if params and params.get("since") else 2022
            to = int(params.get("to", 2022)) if params and params.get("to") else 2022
            return self.mock_provider.get_climate_trace_country_emissions(countries, since, to)
        elif "/assets" in url:
            country = params.get("countries") if params else None
            sector = params.get("sectors") if params else None
            limit = int(params.get("limit", 100)) if params and params.get("limit") else 100
            return self.mock_provider.get_climate_trace_assets(country, sector, limit)
        elif "/admins/search" in url:
            name = params.get("name") if params else None
            level = int(params.get("level")) if params and params.get("level") else None
            point = params.get("point") if params else None
            bbox = params.get("bbox") if params else None
            return self.mock_provider.get_climate_trace_admin_search(name, level, point, bbox)
        elif "/geojson" in url:
            admin_id = url.split("/")[-2] if "/" in url else "ADMIN_1"
            return self.mock_provider.get_climate_trace_admin_geojson(admin_id)
        else:
            return {"mock": True, "endpoint": "climate_trace_unknown"}
    
    def _get_carbon_interface_mock_data(self, params: Dict = None) -> Any:
        """Generate Carbon Interface mock data"""
        if not params:
            return {"error": "No parameters provided"}
        
        estimate_type = params.get("type", "electricity")
        return self.mock_provider.get_carbon_interface_estimate(estimate_type, **params)
    
    def _get_openweather_mock_data(self, url: str, params: Dict = None) -> Any:
        """Generate OpenWeatherMap mock data"""
        if "/weather" in url:
            location = params.get("q", "New York,US") if params else "New York,US"
            return self.mock_provider.get_openweather_current(location)
        elif "/air_pollution" in url:
            lat = float(params.get("lat", 40.7)) if params and params.get("lat") else 40.7
            lon = float(params.get("lon", -74.0)) if params and params.get("lon") else -74.0
            return self.mock_provider.get_openweather_air_quality(lat, lon)
        else:
            return {"mock": True, "endpoint": "openweather_unknown"}
    
    def _get_nasa_power_mock_data(self, params: Dict = None) -> Any:
        """Generate NASA POWER mock data"""
        if not params:
            return {"error": "No parameters provided"}
        
        parameters = params.get("parameters", "ALLSKY_SFC_SW_DWN").split(",")
        lat = float(params.get("latitude", 40.7))
        lon = float(params.get("longitude", -74.0))
        start_date = params.get("start", "20240101")
        end_date = params.get("end", "20240103")
        
        return self.mock_provider.get_nasa_power_data(parameters, lat, lon, start_date, end_date)
    
    def _get_world_bank_mock_data(self, url: str, params: Dict = None) -> Any:
        """Generate World Bank mock data"""
        if "/countries" in url and "/indicator/" not in url:
            return self.mock_provider.get_world_bank_countries()
        elif "/indicator/" in url:
            # Extract country and indicator from URL
            url_parts = url.split("/")
            country = url_parts[-3] if len(url_parts) >= 3 else "USA"
            indicator = url_parts[-1] if len(url_parts) >= 1 else "EN.ATM.CO2E.KT"
            
            # Extract date range from params
            date_range = params.get("date", "2020:2023") if params else "2020:2023"
            start_year, end_year = map(int, date_range.split(":"))
            
            return self.mock_provider.get_world_bank_indicator(country, indicator, start_year, end_year)
        else:
            return {"mock": True, "endpoint": "world_bank_unknown"}
    
    def _get_un_sdg_mock_data(self, url: str) -> Any:
        """Generate UN SDG mock data"""
        if "/Goal/List" in url:
            return self.mock_provider.get_un_sdg_goals()
        elif "/Target/List" in url:
            # Extract goal ID from URL
            goal_id = url.split("/")[-3] if "/" in url else "13"
            return self.mock_provider.get_un_sdg_targets(goal_id)
        else:
            return {"mock": True, "endpoint": "un_sdg_unknown"}
    
    def _update_response_time(self, response_time: float):
        """Update average response time statistics"""
        current_avg = self.api_stats['average_response_time']
        total_successful = self.api_stats['successful_calls']
        
        if total_successful == 1:
            self.api_stats['average_response_time'] = response_time
        else:
            # Calculate running average
            self.api_stats['average_response_time'] = (
                (current_avg * (total_successful - 1) + response_time) / total_successful
            )
    
    # ==================== CLIMATE TRACE API METHODS ====================
    
    def get_climate_trace_sectors(self) -> APIResponse:
        """Get available sectors from ClimateTRACE"""
        url = f"{settings.CLIMATETRACE_API_BASE}/definitions/sectors"
        return self._make_request(url, api_name="ClimateTRACE")
    
    def get_climate_trace_countries(self) -> APIResponse:
        """Get available countries from ClimateTRACE"""
        url = f"{settings.CLIMATETRACE_API_BASE}/definitions/countries"
        return self._make_request(url, api_name="ClimateTRACE")
    
    def get_climate_trace_emissions(self, countries: List[str] = None, sectors: List[str] = None,
                                  years: List[int] = None, gas: str = "co2e_100yr") -> APIResponse:
        """Get emissions data from ClimateTRACE"""
        url = f"{settings.CLIMATETRACE_API_BASE}/assets/emissions"
        
        params = {"gas": gas}
        if countries:
            params["countries"] = ",".join(countries)
        if sectors:
            params["sectors"] = ",".join(sectors)
        if years:
            params["years"] = ",".join(map(str, years))
        else:
            params["years"] = "2022"
        
        return self._make_request(url, params=params, api_name="ClimateTRACE")
    
    def search_climate_trace_assets(self, country: str = None, sector: str = None, 
                                  limit: int = 100, year: int = 2022) -> APIResponse:
        """Search for emissions sources in ClimateTRACE"""
        url = f"{settings.CLIMATETRACE_API_BASE}/assets"
        
        params = {"limit": min(limit, 1000), "year": year}
        if country:
            params["countries"] = country.upper()
        if sector:
            params["sectors"] = sector
        
        return self._make_request(url, params=params, api_name="ClimateTRACE")
    
    # ==================== CARBON INTERFACE API METHODS ====================
    
    def calculate_carbon_footprint(self, calculation_type: str, **kwargs) -> APIResponse:
        """Calculate carbon footprint using Carbon Interface API"""
        if not settings.CARBON_INTERFACE_API_KEY:
            return self._get_mock_response("Carbon Interface", "/estimates", 
                                         {"type": calculation_type, **kwargs},
                                         "No API key available, using mock data")
        
        url = f"{settings.CARBON_INTERFACE_API_BASE}/estimates"
        headers = {
            'Authorization': f'Bearer {settings.CARBON_INTERFACE_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {"type": calculation_type, **kwargs}
        
        return self._make_request(url, params=payload, headers=headers, 
                                method="POST", api_name="Carbon Interface")
    
    # ==================== OPENWEATHERMAP API METHODS ====================
    
    def get_weather_data(self, location: str) -> APIResponse:
        """Get current weather data"""
        if not settings.OPENWEATHER_API_KEY:
            return self._get_mock_response("OpenWeatherMap", "/weather", 
                                         {"q": location},
                                         "No API key available, using mock data")
        
        url = f"{settings.OPENWEATHER_API_BASE}/weather"
        params = {
            'q': location,
            'appid': settings.OPENWEATHER_API_KEY,
            'units': 'metric'
        }
        
        return self._make_request(url, params=params, api_name="OpenWeatherMap")
    
    def get_air_quality(self, lat: float, lon: float) -> APIResponse:
        """Get air quality data"""
        if not settings.OPENWEATHER_API_KEY:
            return self._get_mock_response("OpenWeatherMap", "/air_pollution", 
                                         {"lat": lat, "lon": lon},
                                         "No API key available, using mock data")
        
        url = f"{settings.OPENWEATHER_API_BASE}/air_pollution"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': settings.OPENWEATHER_API_KEY
        }
        
        return self._make_request(url, params=params, api_name="OpenWeatherMap")
    
    # ==================== NASA POWER API METHODS ====================
    
    def get_nasa_power_data(self, lat: float, lon: float, parameters: List[str],
                           start_date: str, end_date: str) -> APIResponse:
        """Get NASA POWER renewable energy data"""
        url = f"{settings.NASA_API_BASE}/daily/point"
        
        params = {
            'parameters': ','.join(parameters),
            'community': 'RE',
            'longitude': lon,
            'latitude': lat,
            'start': start_date,
            'end': end_date,
            'format': 'JSON'
        }
        
        if settings.NASA_API_KEY:
            params['api_key'] = settings.NASA_API_KEY
        
        return self._make_request(url, params=params, timeout=15, api_name="NASA POWER")
    
    # ==================== WORLD BANK API METHODS ====================
    
    def get_world_bank_indicator(self, country: str, indicator: str, 
                               start_year: int = 2020, end_year: int = 2023) -> APIResponse:
        """Get World Bank climate indicator data"""
        url = f"{settings.WORLD_BANK_API_BASE}/country/{country}/indicator/{indicator}"
        
        params = {
            'format': 'json',
            'date': f'{start_year}:{end_year}',
            'per_page': 100
        }
        
        return self._make_request(url, params=params, api_name="World Bank")
    
    # ==================== UN SDG API METHODS ====================
    
    def get_un_sdg_goals(self) -> APIResponse:
        """Get UN SDG goals"""
        url = f"{settings.UN_SDG_API_BASE}/sdg/Goal/List"
        return self._make_request(url, api_name="UN SDG")
    
    def get_un_sdg_targets(self, goal_id: str) -> APIResponse:
        """Get UN SDG targets for a specific goal"""
        url = f"{settings.UN_SDG_API_BASE}/sdg/Goal/{goal_id}/Target/List"
        return self._make_request(url, api_name="UN SDG")
    
    # ==================== UTILITY METHODS ====================
    
    def get_api_statistics(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        total_calls = self.api_stats['total_calls']
        if total_calls == 0:
            return self.api_stats
        
        success_rate = (self.api_stats['successful_calls'] / total_calls) * 100
        failure_rate = (self.api_stats['failed_calls'] / total_calls) * 100
        mock_rate = (self.api_stats['mock_calls'] / total_calls) * 100
        
        return {
            **self.api_stats,
            'success_rate': round(success_rate, 2),
            'failure_rate': round(failure_rate, 2),
            'mock_rate': round(mock_rate, 2)
        }
    
    def reset_statistics(self):
        """Reset API usage statistics"""
        self.api_stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'mock_calls': 0,
            'average_response_time': 0.0
        }
    
    def validate_response(self, response: APIResponse, expected_fields: List[str] = None) -> bool:
        """Validate API response structure"""
        if response.status != APIStatus.SUCCESS and response.status != APIStatus.MOCK_DATA:
            return False
        
        if not response.data:
            return False
        
        if expected_fields:
            if isinstance(response.data, dict):
                return all(field in response.data for field in expected_fields)
            elif isinstance(response.data, list) and response.data:
                return all(field in response.data[0] for field in expected_fields)
        
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all APIs"""
        health_status = {}
        
        # Test ClimateTRACE
        try:
            response = self.get_climate_trace_sectors()
            health_status['climate_trace'] = {
                'status': response.status.value,
                'response_time': response.response_time,
                'available': response.status in [APIStatus.SUCCESS, APIStatus.MOCK_DATA]
            }
        except Exception as e:
            health_status['climate_trace'] = {
                'status': 'error',
                'error': str(e),
                'available': False
            }
        
        # Test Carbon Interface (if API key available)
        if settings.CARBON_INTERFACE_API_KEY:
            try:
                response = self.calculate_carbon_footprint(
                    "electricity", 
                    electricity_value=1, 
                    electricity_unit="kwh", 
                    country="us"
                )
                health_status['carbon_interface'] = {
                    'status': response.status.value,
                    'response_time': response.response_time,
                    'available': response.status in [APIStatus.SUCCESS, APIStatus.MOCK_DATA]
                }
            except Exception as e:
                health_status['carbon_interface'] = {
                    'status': 'error',
                    'error': str(e),
                    'available': False
                }
        else:
            health_status['carbon_interface'] = {
                'status': 'no_api_key',
                'available': False
            }
        
        # Test OpenWeatherMap (if API key available)
        if settings.OPENWEATHER_API_KEY:
            try:
                response = self.get_weather_data("New York,US")
                health_status['openweather'] = {
                    'status': response.status.value,
                    'response_time': response.response_time,
                    'available': response.status in [APIStatus.SUCCESS, APIStatus.MOCK_DATA]
                }
            except Exception as e:
                health_status['openweather'] = {
                    'status': 'error',
                    'error': str(e),
                    'available': False
                }
        else:
            health_status['openweather'] = {
                'status': 'no_api_key',
                'available': False
            }
        
        # Test NASA POWER
        try:
            response = self.get_nasa_power_data(
                40.7, -74.0, 
                ["ALLSKY_SFC_SW_DWN"], 
                "20240101", "20240101"
            )
            health_status['nasa_power'] = {
                'status': response.status.value,
                'response_time': response.response_time,
                'available': response.status in [APIStatus.SUCCESS, APIStatus.MOCK_DATA]
            }
        except Exception as e:
            health_status['nasa_power'] = {
                'status': 'error',
                'error': str(e),
                'available': False
            }
        
        # Test World Bank
        try:
            response = self.get_world_bank_indicator("USA", "EN.ATM.CO2E.KT", 2022, 2022)
            health_status['world_bank'] = {
                'status': response.status.value,
                'response_time': response.response_time,
                'available': response.status in [APIStatus.SUCCESS, APIStatus.MOCK_DATA]
            }
        except Exception as e:
            health_status['world_bank'] = {
                'status': 'error',
                'error': str(e),
                'available': False
            }
        
        # Test UN SDG
        try:
            response = self.get_un_sdg_goals()
            health_status['un_sdg'] = {
                'status': response.status.value,
                'response_time': response.response_time,
                'available': response.status in [APIStatus.SUCCESS, APIStatus.MOCK_DATA]
            }
        except Exception as e:
            health_status['un_sdg'] = {
                'status': 'error',
                'error': str(e),
                'available': False
            }
        
        # Calculate overall health
        available_apis = sum(1 for api in health_status.values() if api.get('available', False))
        total_apis = len(health_status)
        overall_health = (available_apis / total_apis) * 100 if total_apis > 0 else 0
        
        return {
            'overall_health': round(overall_health, 2),
            'available_apis': available_apis,
            'total_apis': total_apis,
            'apis': health_status,
            'timestamp': datetime.now().isoformat()
        }


# Global instance for easy access
enhanced_api_handler = EnhancedClimateAPIHandler()


def main():
    """Test the enhanced API handler"""
    print("🧪 Testing Enhanced Climate API Handler")
    print("=" * 50)
    
    handler = EnhancedClimateAPIHandler(test_mode=TestMode.HYBRID)
    
    # Test ClimateTRACE
    print("\n🌍 Testing ClimateTRACE API...")
    response = handler.get_climate_trace_sectors()
    print(f"Status: {response.status.value}")
    print(f"Response time: {response.response_time:.2f}s")
    print(f"Source: {response.source}")
    
    # Test Carbon Interface
    print("\n🌱 Testing Carbon Interface API...")
    response = handler.calculate_carbon_footprint(
        "electricity",
        electricity_value=100,
        electricity_unit="kwh",
        country="us"
    )
    print(f"Status: {response.status.value}")
    print(f"Response time: {response.response_time:.2f}s")
    print(f"Source: {response.source}")
    
    # Health check
    print("\n🏥 Performing Health Check...")
    health = handler.health_check()
    print(f"Overall Health: {health['overall_health']:.1f}%")
    print(f"Available APIs: {health['available_apis']}/{health['total_apis']}")
    
    # Statistics
    print("\n📊 API Statistics:")
    stats = handler.get_api_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Enhanced API Handler Test Complete!")


if __name__ == "__main__":
    main()