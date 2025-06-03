#!/usr/bin/env python3
"""
Comprehensive Climate API Testing Framework
Integrates all climate APIs with unified testing, reporting, and validation
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import pytest
from dataclasses import dataclass, asdict
from enum import Enum
import sys
import os
import asyncio
import concurrent.futures
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from tests.test_climate_trace_api import ClimateTraceAPITester
from tests.test_carbon_interface_api import CarbonInterfaceAPITester

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """Test result status"""
    PASS = "✅ PASS"
    FAIL = "❌ FAIL"
    SKIP = "⏭️ SKIP"
    WARNING = "⚠️ WARNING"

@dataclass
class APITestResult:
    """Comprehensive API test result"""
    api_name: str
    endpoint: str
    test_name: str
    status: TestStatus
    response_time: float
    status_code: Optional[int]
    error_message: Optional[str]
    data_sample: Optional[Dict]
    notes: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class ComprehensiveAPITester:
    """Unified testing framework for all climate APIs"""
    
    def __init__(self):
        self.test_results: List[APITestResult] = []
        self.start_time = time.time()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ClimateIQ-ComprehensiveTestFramework/1.0'
        })
        
    def log_result(self, result: APITestResult):
        """Log and store test result"""
        self.test_results.append(result)
        status_icon = result.status.value
        print(f"{status_icon} [{result.api_name}] {result.test_name} ({result.response_time:.2f}s)")
        if result.error_message:
            print(f"    Error: {result.error_message}")
        if result.notes:
            print(f"    Notes: {result.notes}")

    def make_request(self, url: str, params: Dict = None, headers: Dict = None, method: str = "GET", timeout: int = 30) -> Tuple[requests.Response, float]:
        """Make HTTP request with timing and error handling"""
        start_time = time.time()
        
        try:
            if headers:
                session_headers = self.session.headers.copy()
                session_headers.update(headers)
            else:
                session_headers = self.session.headers
            
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=session_headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=params, headers=session_headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = time.time() - start_time
            return response, response_time
            
        except Exception as e:
            response_time = time.time() - start_time
            # Create a mock response object for error cases
            class MockResponse:
                def __init__(self, error):
                    self.status_code = 0
                    self.text = str(error)
                    self.error = error
                def json(self):
                    return {"error": str(self.error)}
                def raise_for_status(self):
                    raise self.error
            
            return MockResponse(e), response_time

    # ==================== NASA POWER API TESTS ====================
    
    def test_nasa_power_api(self):
        """Test NASA POWER API for renewable energy data"""
        print("\n🛰️ Testing NASA POWER API...")
        
        base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        
        test_cases = [
            {
                "name": "Solar and Wind Data - New York",
                "params": {
                    'parameters': 'ALLSKY_SFC_SW_DWN,WS10M,T2M',
                    'community': 'RE',
                    'longitude': -74.0,
                    'latitude': 40.7,
                    'start': '20240101',
                    'end': '20240107',
                    'format': 'JSON'
                }
            },
            {
                "name": "Solar Data - Los Angeles",
                "params": {
                    'parameters': 'ALLSKY_SFC_SW_DWN',
                    'community': 'RE',
                    'longitude': -118.2,
                    'latitude': 34.0,
                    'start': '20240101',
                    'end': '20240103',
                    'format': 'JSON'
                }
            },
            {
                "name": "Wind Data - Chicago",
                "params": {
                    'parameters': 'WS10M',
                    'community': 'RE',
                    'longitude': -87.6,
                    'latitude': 41.9,
                    'start': '20240101',
                    'end': '20240103',
                    'format': 'JSON'
                }
            }
        ]
        
        for test_case in test_cases:
            response, response_time = self.make_request(base_url, test_case["params"])
            
            try:
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate NASA POWER response structure
                    if 'properties' in data and 'parameter' in data['properties']:
                        parameters = data['properties']['parameter']
                        
                        self.log_result(APITestResult(
                            api_name="NASA POWER",
                            endpoint="/api/temporal/daily/point",
                            test_name=test_case["name"],
                            status=TestStatus.PASS,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message=None,
                            data_sample={
                                "parameters": list(parameters.keys()),
                                "data_points": len(list(parameters.values())[0]) if parameters else 0
                            }
                        ))
                    else:
                        self.log_result(APITestResult(
                            api_name="NASA POWER",
                            endpoint="/api/temporal/daily/point",
                            test_name=f"{test_case['name']} - Invalid Structure",
                            status=TestStatus.FAIL,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message="Invalid response structure",
                            data_sample=data
                        ))
                else:
                    self.log_result(APITestResult(
                        api_name="NASA POWER",
                        endpoint="/api/temporal/daily/point",
                        test_name=f"{test_case['name']} - HTTP Error",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=f"HTTP {response.status_code}",
                        data_sample=None
                    ))
                    
            except Exception as e:
                self.log_result(APITestResult(
                    api_name="NASA POWER",
                    endpoint="/api/temporal/daily/point",
                    test_name=f"{test_case['name']} - Exception",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=getattr(response, 'status_code', 0),
                    error_message=str(e),
                    data_sample=None
                ))

    # ==================== OPENWEATHERMAP API TESTS ====================
    
    def test_openweather_api(self):
        """Test OpenWeatherMap API for weather and air quality data"""
        print("\n🌤️ Testing OpenWeatherMap API...")
        
        if not settings.OPENWEATHER_API_KEY:
            self.log_result(APITestResult(
                api_name="OpenWeatherMap",
                endpoint="/weather",
                test_name="API Key Check",
                status=TestStatus.SKIP,
                response_time=0,
                status_code=None,
                error_message="No API key provided",
                data_sample=None
            ))
            return
        
        base_url = "https://api.openweathermap.org/data/2.5"
        
        test_cases = [
            {
                "name": "Current Weather - New York",
                "endpoint": "/weather",
                "params": {
                    'q': 'New York,US',
                    'appid': settings.OPENWEATHER_API_KEY,
                    'units': 'metric'
                }
            },
            {
                "name": "Current Weather - London",
                "endpoint": "/weather",
                "params": {
                    'q': 'London,UK',
                    'appid': settings.OPENWEATHER_API_KEY,
                    'units': 'metric'
                }
            },
            {
                "name": "Air Quality - New York",
                "endpoint": "/air_pollution",
                "params": {
                    'lat': 40.7,
                    'lon': -74.0,
                    'appid': settings.OPENWEATHER_API_KEY
                }
            }
        ]
        
        for test_case in test_cases:
            url = f"{base_url}{test_case['endpoint']}"
            response, response_time = self.make_request(url, test_case["params"])
            
            try:
                if response.status_code == 200:
                    data = response.json()
                    
                    if test_case['endpoint'] == '/weather':
                        # Validate weather response
                        required_fields = ['name', 'main', 'weather', 'coord']
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if not missing_fields:
                            self.log_result(APITestResult(
                                api_name="OpenWeatherMap",
                                endpoint=test_case['endpoint'],
                                test_name=test_case["name"],
                                status=TestStatus.PASS,
                                response_time=response_time,
                                status_code=response.status_code,
                                error_message=None,
                                data_sample={
                                    "location": data['name'],
                                    "temperature": data['main']['temp'],
                                    "weather": data['weather'][0]['description']
                                }
                            ))
                        else:
                            self.log_result(APITestResult(
                                api_name="OpenWeatherMap",
                                endpoint=test_case['endpoint'],
                                test_name=f"{test_case['name']} - Missing Fields",
                                status=TestStatus.WARNING,
                                response_time=response_time,
                                status_code=response.status_code,
                                error_message=f"Missing fields: {missing_fields}",
                                data_sample=data
                            ))
                    
                    elif test_case['endpoint'] == '/air_pollution':
                        # Validate air quality response
                        if 'list' in data and data['list']:
                            aqi_data = data['list'][0]
                            self.log_result(APITestResult(
                                api_name="OpenWeatherMap",
                                endpoint=test_case['endpoint'],
                                test_name=test_case["name"],
                                status=TestStatus.PASS,
                                response_time=response_time,
                                status_code=response.status_code,
                                error_message=None,
                                data_sample={
                                    "aqi": aqi_data['main']['aqi'],
                                    "components": list(aqi_data['components'].keys())
                                }
                            ))
                        else:
                            self.log_result(APITestResult(
                                api_name="OpenWeatherMap",
                                endpoint=test_case['endpoint'],
                                test_name=f"{test_case['name']} - No Data",
                                status=TestStatus.FAIL,
                                response_time=response_time,
                                status_code=response.status_code,
                                error_message="No air quality data in response",
                                data_sample=data
                            ))
                else:
                    self.log_result(APITestResult(
                        api_name="OpenWeatherMap",
                        endpoint=test_case['endpoint'],
                        test_name=f"{test_case['name']} - HTTP Error",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=f"HTTP {response.status_code}",
                        data_sample=None
                    ))
                    
            except Exception as e:
                self.log_result(APITestResult(
                    api_name="OpenWeatherMap",
                    endpoint=test_case['endpoint'],
                    test_name=f"{test_case['name']} - Exception",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=getattr(response, 'status_code', 0),
                    error_message=str(e),
                    data_sample=None
                ))

    # ==================== WORLD BANK API TESTS ====================
    
    def test_world_bank_api(self):
        """Test World Bank API for climate indicators"""
        print("\n🏛️ Testing World Bank API...")
        
        base_url = "https://api.worldbank.org/v2"
        
        test_cases = [
            {
                "name": "CO2 Emissions - USA",
                "endpoint": "/country/USA/indicator/EN.ATM.CO2E.KT",
                "params": {
                    'format': 'json',
                    'date': '2020:2023',
                    'per_page': 5
                }
            },
            {
                "name": "Electric Power Consumption - Germany",
                "endpoint": "/country/DEU/indicator/EG.USE.ELEC.KH.PC",
                "params": {
                    'format': 'json',
                    'date': '2020:2023',
                    'per_page': 5
                }
            },
            {
                "name": "Forest Area - Brazil",
                "endpoint": "/country/BRA/indicator/AG.LND.FRST.ZS",
                "params": {
                    'format': 'json',
                    'date': '2020:2023',
                    'per_page': 5
                }
            },
            {
                "name": "Countries List",
                "endpoint": "/countries",
                "params": {
                    'format': 'json',
                    'per_page': 10
                }
            }
        ]
        
        for test_case in test_cases:
            url = f"{base_url}{test_case['endpoint']}"
            response, response_time = self.make_request(url, test_case["params"])
            
            try:
                if response.status_code == 200:
                    data = response.json()
                    
                    # World Bank API returns array with metadata and data
                    if isinstance(data, list) and len(data) >= 1:
                        if len(data) > 1 and data[1]:
                            # Has actual data
                            data_points = data[1]
                            self.log_result(APITestResult(
                                api_name="World Bank",
                                endpoint=test_case['endpoint'],
                                test_name=test_case["name"],
                                status=TestStatus.PASS,
                                response_time=response_time,
                                status_code=response.status_code,
                                error_message=None,
                                data_sample={
                                    "data_points": len(data_points),
                                    "sample": data_points[0] if data_points else None
                                }
                            ))
                        else:
                            # Only metadata, no data
                            self.log_result(APITestResult(
                                api_name="World Bank",
                                endpoint=test_case['endpoint'],
                                test_name=f"{test_case['name']} - No Data",
                                status=TestStatus.WARNING,
                                response_time=response_time,
                                status_code=response.status_code,
                                error_message="No data available for requested parameters",
                                data_sample={"metadata": data[0] if data else None}
                            ))
                    else:
                        self.log_result(APITestResult(
                            api_name="World Bank",
                            endpoint=test_case['endpoint'],
                            test_name=f"{test_case['name']} - Invalid Format",
                            status=TestStatus.FAIL,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message="Unexpected response format",
                            data_sample=data
                        ))
                else:
                    self.log_result(APITestResult(
                        api_name="World Bank",
                        endpoint=test_case['endpoint'],
                        test_name=f"{test_case['name']} - HTTP Error",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=f"HTTP {response.status_code}",
                        data_sample=None
                    ))
                    
            except Exception as e:
                self.log_result(APITestResult(
                    api_name="World Bank",
                    endpoint=test_case['endpoint'],
                    test_name=f"{test_case['name']} - Exception",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=getattr(response, 'status_code', 0),
                    error_message=str(e),
                    data_sample=None
                ))

    # ==================== UN SDG API TESTS ====================
    
    def test_un_sdg_api(self):
        """Test UN SDG API for sustainable development goals"""
        print("\n🇺🇳 Testing UN SDG API...")
        
        base_url = "https://unstats.un.org/SDGAPI/v1"
        
        test_cases = [
            {
                "name": "SDG Goals List",
                "endpoint": "/sdg/Goal/List",
                "params": None
            },
            {
                "name": "Climate Action Targets (Goal 13)",
                "endpoint": "/sdg/Goal/13/Target/List",
                "params": None
            },
            {
                "name": "Clean Energy Targets (Goal 7)",
                "endpoint": "/sdg/Goal/7/Target/List",
                "params": None
            }
        ]
        
        for test_case in test_cases:
            url = f"{base_url}{test_case['endpoint']}"
            response, response_time = self.make_request(url, test_case["params"])
            
            try:
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list):
                        self.log_result(APITestResult(
                            api_name="UN SDG",
                            endpoint=test_case['endpoint'],
                            test_name=test_case["name"],
                            status=TestStatus.PASS,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message=None,
                            data_sample={
                                "count": len(data),
                                "sample": data[0] if data else None
                            }
                        ))
                    else:
                        self.log_result(APITestResult(
                            api_name="UN SDG",
                            endpoint=test_case['endpoint'],
                            test_name=f"{test_case['name']} - Invalid Format",
                            status=TestStatus.FAIL,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message="Expected array format",
                            data_sample=data
                        ))
                else:
                    self.log_result(APITestResult(
                        api_name="UN SDG",
                        endpoint=test_case['endpoint'],
                        test_name=f"{test_case['name']} - HTTP Error",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=f"HTTP {response.status_code}",
                        data_sample=None
                    ))
                    
            except Exception as e:
                self.log_result(APITestResult(
                    api_name="UN SDG",
                    endpoint=test_case['endpoint'],
                    test_name=f"{test_case['name']} - Exception",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=getattr(response, 'status_code', 0),
                    error_message=str(e),
                    data_sample=None
                ))

    # ==================== INTEGRATION TESTS ====================
    
    def test_api_integration(self):
        """Test integration between different APIs"""
        print("\n🔗 Testing API Integration...")
        
        # Test 1: Get weather data and calculate carbon footprint for electricity usage
        try:
            # Get weather data for New York
            if settings.OPENWEATHER_API_KEY:
                weather_url = "https://api.openweathermap.org/data/2.5/weather"
                weather_params = {
                    'q': 'New York,US',
                    'appid': settings.OPENWEATHER_API_KEY,
                    'units': 'metric'
                }
                
                weather_response, weather_time = self.make_request(weather_url, weather_params)
                
                if weather_response.status_code == 200:
                    weather_data = weather_response.json()
                    temperature = weather_data['main']['temp']
                    
                    # Calculate electricity usage based on temperature (simplified model)
                    # Higher temperatures = more AC usage
                    base_usage = 100  # kWh
                    temp_factor = max(1.0, (temperature - 20) * 0.1) if temperature > 20 else 1.0
                    electricity_usage = base_usage * temp_factor
                    
                    # Calculate carbon footprint if Carbon Interface API is available
                    if settings.CARBON_INTERFACE_API_KEY:
                        carbon_url = "https://www.carboninterface.com/api/v1/estimates"
                        carbon_headers = {
                            'Authorization': f'Bearer {settings.CARBON_INTERFACE_API_KEY}',
                            'Content-Type': 'application/json'
                        }
                        carbon_data = {
                            'type': 'electricity',
                            'electricity_unit': 'kwh',
                            'electricity_value': electricity_usage,
                            'country': 'us'
                        }
                        
                        carbon_response, carbon_time = self.make_request(
                            carbon_url, carbon_data, carbon_headers, "POST"
                        )
                        
                        if carbon_response.status_code == 201:
                            carbon_result = carbon_response.json()
                            carbon_kg = carbon_result['data']['attributes']['carbon_kg']
                            
                            self.log_result(APITestResult(
                                api_name="Integration",
                                endpoint="Weather + Carbon",
                                test_name="Weather-Based Carbon Calculation",
                                status=TestStatus.PASS,
                                response_time=weather_time + carbon_time,
                                status_code=200,
                                error_message=None,
                                data_sample={
                                    "temperature": temperature,
                                    "electricity_usage": electricity_usage,
                                    "carbon_kg": carbon_kg,
                                    "location": weather_data['name']
                                }
                            ))
                        else:
                            self.log_result(APITestResult(
                                api_name="Integration",
                                endpoint="Weather + Carbon",
                                test_name="Weather-Based Carbon Calculation - Carbon API Failed",
                                status=TestStatus.FAIL,
                                response_time=weather_time + carbon_time,
                                status_code=carbon_response.status_code,
                                error_message="Carbon Interface API failed",
                                data_sample=None
                            ))
                    else:
                        self.log_result(APITestResult(
                            api_name="Integration",
                            endpoint="Weather + Carbon",
                            test_name="Weather-Based Carbon Calculation - No Carbon API Key",
                            status=TestStatus.SKIP,
                            response_time=weather_time,
                            status_code=None,
                            error_message="No Carbon Interface API key",
                            data_sample={"temperature": temperature, "electricity_usage": electricity_usage}
                        ))
                else:
                    self.log_result(APITestResult(
                        api_name="Integration",
                        endpoint="Weather + Carbon",
                        test_name="Weather-Based Carbon Calculation - Weather API Failed",
                        status=TestStatus.FAIL,
                        response_time=weather_time,
                        status_code=weather_response.status_code,
                        error_message="Weather API failed",
                        data_sample=None
                    ))
            else:
                self.log_result(APITestResult(
                    api_name="Integration",
                    endpoint="Weather + Carbon",
                    test_name="Weather-Based Carbon Calculation - No Weather API Key",
                    status=TestStatus.SKIP,
                    response_time=0,
                    status_code=None,
                    error_message="No OpenWeatherMap API key",
                    data_sample=None
                ))
                
        except Exception as e:
            self.log_result(APITestResult(
                api_name="Integration",
                endpoint="Weather + Carbon",
                test_name="Weather-Based Carbon Calculation - Exception",
                status=TestStatus.FAIL,
                response_time=0,
                status_code=None,
                error_message=str(e),
                data_sample=None
            ))

    # ==================== PERFORMANCE TESTS ====================
    
    def test_api_performance(self):
        """Test API performance and response times"""
        print("\n⚡ Testing API Performance...")
        
        performance_tests = [
            {
                "name": "NASA POWER - Performance",
                "url": "https://power.larc.nasa.gov/api/temporal/daily/point",
                "params": {
                    'parameters': 'ALLSKY_SFC_SW_DWN',
                    'community': 'RE',
                    'longitude': -74.0,
                    'latitude': 40.7,
                    'start': '20240101',
                    'end': '20240101',
                    'format': 'JSON'
                },
                "max_time": 5.0,
                "api_name": "NASA POWER"
            },
            {
                "name": "World Bank - Performance",
                "url": "https://api.worldbank.org/v2/countries",
                "params": {
                    'format': 'json',
                    'per_page': 50
                },
                "max_time": 3.0,
                "api_name": "World Bank"
            },
            {
                "name": "UN SDG - Performance",
                "url": "https://unstats.un.org/SDGAPI/v1/sdg/Goal/List",
                "params": None,
                "max_time": 3.0,
                "api_name": "UN SDG"
            }
        ]
        
        if settings.OPENWEATHER_API_KEY:
            performance_tests.append({
                "name": "OpenWeatherMap - Performance",
                "url": "https://api.openweathermap.org/data/2.5/weather",
                "params": {
                    'q': 'New York,US',
                    'appid': settings.OPENWEATHER_API_KEY
                },
                "max_time": 2.0,
                "api_name": "OpenWeatherMap"
            })
        
        for test in performance_tests:
            response, response_time = self.make_request(test["url"], test["params"])
            
            if response.status_code == 200:
                if response_time <= test["max_time"]:
                    status = TestStatus.PASS
                    error_msg = None
                else:
                    status = TestStatus.WARNING
                    error_msg = f"Response time {response_time:.2f}s exceeds threshold {test['max_time']}s"
            else:
                status = TestStatus.FAIL
                error_msg = f"HTTP {response.status_code}"
            
            self.log_result(APITestResult(
                api_name=test["api_name"],
                endpoint=test["url"].split('/')[-1],
                test_name=test["name"],
                status=status,
                response_time=response_time,
                status_code=response.status_code,
                error_message=error_msg,
                data_sample=None,
                notes=f"Threshold: {test['max_time']}s"
            ))

    # ==================== MAIN TEST RUNNER ====================
    
    def run_all_tests(self):
        """Run comprehensive test suite for all APIs"""
        print("🧪 Comprehensive Climate API Testing Framework")
        print("=" * 80)
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔑 API Keys Available:")
        print(f"   • OpenWeatherMap: {'✅' if settings.OPENWEATHER_API_KEY else '❌'}")
        print(f"   • Carbon Interface: {'✅' if settings.CARBON_INTERFACE_API_KEY else '❌'}")
        print(f"   • NASA POWER: Public API")
        print(f"   • World Bank: Public API")
        print(f"   • UN SDG: Public API")
        print(f"   • ClimateTRACE: Public API")
        print()
        
        # Run individual API tests
        self.test_nasa_power_api()
        self.test_openweather_api()
        self.test_world_bank_api()
        self.test_un_sdg_api()
        
        # Run specialized API testers
        print("\n🌍 Running ClimateTRACE API Tests...")
        climate_trace_tester = ClimateTraceAPITester()
        climate_trace_tester.run_all_tests()
        
        # Convert ClimateTRACE results to our format
        for result in climate_trace_tester.test_results:
            self.test_results.append(APITestResult(
                api_name="ClimateTRACE",
                endpoint=result.endpoint,
                test_name=result.test_name,
                status=result.status,
                response_time=result.response_time,
                status_code=result.status_code,
                error_message=result.error_message,
                data_sample=result.data_sample,
                notes=result.notes
            ))
        
        print("\n🌱 Running Carbon Interface API Tests...")
        carbon_tester = CarbonInterfaceAPITester()
        carbon_tester.run_all_tests()
        
        # Convert Carbon Interface results to our format
        for result in carbon_tester.test_results:
            self.test_results.append(APITestResult(
                api_name="Carbon Interface",
                endpoint=result.endpoint,
                test_name=result.test_name,
                status=result.status,
                response_time=result.response_time,
                status_code=result.status_code,
                error_message=result.error_message,
                data_sample=result.data_sample,
                notes=result.notes
            ))
        
        # Run integration and performance tests
        self.test_api_integration()
        self.test_api_performance()
        
        # Generate comprehensive report
        self.generate_comprehensive_report()

    def generate_comprehensive_report(self):
        """Generate comprehensive test report across all APIs"""
        total_time = time.time() - self.start_time
        
        # Count results by status and API
        status_counts = {}
        api_counts = {}
        
        for status in TestStatus:
            status_counts[status] = len([r for r in self.test_results if (
                r.status == status or 
                (hasattr(r.status, 'name') and r.status.name == status.name)
            )])
        
        for result in self.test_results:
            if result.api_name not in api_counts:
                api_counts[result.api_name] = {status: 0 for status in TestStatus}
            # Handle different TestStatus enums from different modules
            status_key = result.status
            if hasattr(result.status, 'name'):
                # Find matching status by name
                for ts in TestStatus:
                    if ts.name == result.status.name:
                        status_key = ts
                        break
            api_counts[result.api_name][status_key] += 1
        
        # Calculate statistics
        total_tests = len(self.test_results)
        pass_rate = (status_counts[TestStatus.PASS] / total_tests * 100) if total_tests > 0 else 0
        avg_response_time = sum(r.response_time for r in self.test_results) / total_tests if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE CLIMATE API TEST REPORT")
        print("=" * 80)
        print(f"⏱️  Total Execution Time: {total_time:.2f} seconds")
        print(f"🧪 Total Tests: {total_tests}")
        print(f"📈 Overall Pass Rate: {pass_rate:.1f}%")
        print(f"⚡ Average Response Time: {avg_response_time:.2f}s")
        print()
        
        print("📋 Overall Results by Status:")
        for status in TestStatus:
            count = status_counts[status]
            percentage = (count / total_tests * 100) if total_tests > 0 else 0
            print(f"   {status.value}: {count} ({percentage:.1f}%)")
        print()
        
        print("🌐 Results by API:")
        for api_name, counts in api_counts.items():
            total_api_tests = sum(counts.values())
            passed = counts[TestStatus.PASS]
            success_rate = (passed / total_api_tests * 100) if total_api_tests > 0 else 0
            
            api_results = [r for r in self.test_results if r.api_name == api_name]
            avg_time = sum(r.response_time for r in api_results) / len(api_results) if api_results else 0
            
            print(f"   {api_name}: {passed}/{total_api_tests} ({success_rate:.1f}%) - Avg: {avg_time:.2f}s")
            
            # Show status breakdown for each API
            for status in TestStatus:
                if counts[status] > 0:
                    print(f"      {status.value}: {counts[status]}")
        
        # Show critical failures
        critical_failures = [r for r in self.test_results if r.status == TestStatus.FAIL and 'Exception' not in r.test_name]
        if critical_failures:
            print("\n❌ Critical Failures:")
            for result in critical_failures:
                print(f"   • [{result.api_name}] {result.test_name}: {result.error_message}")
        
        # Show API availability summary
        print("\n🔗 API Availability Summary:")
        api_availability = {}
        for api_name in api_counts.keys():
            api_results = [r for r in self.test_results if r.api_name == api_name]
            working_tests = [r for r in api_results if r.status == TestStatus.PASS]
            availability = (len(working_tests) / len(api_results) * 100) if api_results else 0
            api_availability[api_name] = availability
            
            status_icon = "✅" if availability >= 80 else "⚠️" if availability >= 50 else "❌"
            print(f"   {status_icon} {api_name}: {availability:.1f}% available")
        
        print("\n" + "=" * 80)
        print("✅ Comprehensive Testing Complete!")
        
        # Save detailed results
        self.save_comprehensive_report()
        
        return {
            "total_tests": total_tests,
            "pass_rate": pass_rate,
            "api_availability": api_availability,
            "execution_time": total_time
        }

    def save_comprehensive_report(self):
        """Save comprehensive test results to JSON file"""
        report_data = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "total_time": time.time() - self.start_time,
                "total_tests": len(self.test_results),
                "framework_version": "1.0"
            },
            "api_keys_available": {
                "openweather": bool(settings.OPENWEATHER_API_KEY),
                "carbon_interface": bool(settings.CARBON_INTERFACE_API_KEY),
                "nasa_power": True,  # Public API
                "world_bank": True,  # Public API
                "un_sdg": True,  # Public API
                "climate_trace": True  # Public API
            },
            "results": [asdict(result) for result in self.test_results]
        }
        
        # Create reports directory if it doesn't exist
        reports_dir = Path(__file__).parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        filename = f"comprehensive_api_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = reports_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"📄 Comprehensive report saved to: {filepath}")
            
            # Also save a summary CSV
            self.save_summary_csv(reports_dir)
            
        except Exception as e:
            print(f"⚠️  Could not save comprehensive report: {e}")

    def save_summary_csv(self, reports_dir: Path):
        """Save a summary CSV for easy analysis"""
        try:
            import csv
            
            filename = f"api_test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = reports_dir / filename
            
            with open(filepath, 'w', newline='') as csvfile:
                fieldnames = ['api_name', 'test_name', 'status', 'response_time', 'status_code', 'error_message']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for result in self.test_results:
                    writer.writerow({
                        'api_name': result.api_name,
                        'test_name': result.test_name,
                        'status': result.status.name,
                        'response_time': result.response_time,
                        'status_code': result.status_code,
                        'error_message': result.error_message
                    })
            
            print(f"📊 Summary CSV saved to: {filepath}")
            
        except Exception as e:
            print(f"⚠️  Could not save summary CSV: {e}")


def main():
    """Main test runner"""
    tester = ComprehensiveAPITester()
    results = tester.run_all_tests()
    
    # Print final summary
    print(f"\n🎯 Final Summary:")
    print(f"   • Total Tests: {results['total_tests']}")
    print(f"   • Pass Rate: {results['pass_rate']:.1f}%")
    print(f"   • Execution Time: {results['execution_time']:.2f}s")
    print(f"   • Reports saved to: tests/reports/")


if __name__ == "__main__":
    main()