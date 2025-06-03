#!/usr/bin/env python3
"""
Comprehensive Carbon Interface API Testing Framework
Tests all endpoints, calculation types, and edge cases
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pytest
from dataclasses import dataclass
from enum import Enum
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

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
class TestResult:
    """Test result data structure"""
    endpoint: str
    test_name: str
    status: TestStatus
    response_time: float
    status_code: Optional[int]
    error_message: Optional[str]
    data_sample: Optional[Dict]
    notes: Optional[str] = None

class CarbonInterfaceAPITester:
    """Comprehensive Carbon Interface API Testing Framework"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.CARBON_INTERFACE_API_KEY
        self.base_url = "https://www.carboninterface.com/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'ClimateIQ-CarbonInterface-TestFramework/1.0'
        })
        self.test_results: List[TestResult] = []
        self.start_time = time.time()
        
    def log_result(self, result: TestResult):
        """Log and store test result"""
        self.test_results.append(result)
        status_icon = result.status.value
        print(f"{status_icon} {result.test_name} ({result.response_time:.2f}s)")
        if result.error_message:
            print(f"    Error: {result.error_message}")
        if result.notes:
            print(f"    Notes: {result.notes}")
    
    def make_request(self, endpoint: str, data: Dict = None, method: str = "POST") -> Tuple[requests.Response, float]:
        """Make HTTP request with timing"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=30)
            elif method.upper() == "GET":
                response = self.session.get(url, params=data, timeout=30)
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

    # ==================== AUTHENTICATION TESTS ====================
    
    def test_authentication(self):
        """Test API authentication"""
        if not self.api_key:
            self.log_result(TestResult(
                endpoint="/estimates",
                test_name="Authentication - No API Key",
                status=TestStatus.SKIP,
                response_time=0,
                status_code=None,
                error_message="No API key provided",
                data_sample=None
            ))
            return
        
        # Test with valid API key
        test_data = {
            'type': 'electricity',
            'electricity_unit': 'kwh',
            'electricity_value': 1,
            'country': 'us'
        }
        
        response, response_time = self.make_request("/estimates", test_data)
        
        if response.status_code == 201:
            self.log_result(TestResult(
                endpoint="/estimates",
                test_name="Authentication - Valid API Key",
                status=TestStatus.PASS,
                response_time=response_time,
                status_code=response.status_code,
                error_message=None,
                data_sample={"authenticated": True}
            ))
        elif response.status_code == 401:
            self.log_result(TestResult(
                endpoint="/estimates",
                test_name="Authentication - Invalid API Key",
                status=TestStatus.FAIL,
                response_time=response_time,
                status_code=response.status_code,
                error_message="API key authentication failed",
                data_sample=None
            ))
        else:
            self.log_result(TestResult(
                endpoint="/estimates",
                test_name="Authentication - Unexpected Response",
                status=TestStatus.WARNING,
                response_time=response_time,
                status_code=response.status_code,
                error_message=f"Unexpected status code: {response.status_code}",
                data_sample=None
            ))

    # ==================== ELECTRICITY EMISSIONS TESTS ====================
    
    def test_electricity_emissions(self):
        """Test electricity carbon footprint calculations"""
        test_cases = [
            {
                "name": "Electricity - Basic US",
                "data": {
                    'type': 'electricity',
                    'electricity_unit': 'kwh',
                    'electricity_value': 100,
                    'country': 'us'
                }
            },
            {
                "name": "Electricity - Different Country",
                "data": {
                    'type': 'electricity',
                    'electricity_unit': 'kwh',
                    'electricity_value': 100,
                    'country': 'de'  # Germany
                }
            },
            {
                "name": "Electricity - Large Consumption",
                "data": {
                    'type': 'electricity',
                    'electricity_unit': 'kwh',
                    'electricity_value': 10000,
                    'country': 'us'
                }
            },
            {
                "name": "Electricity - Small Consumption",
                "data": {
                    'type': 'electricity',
                    'electricity_unit': 'kwh',
                    'electricity_value': 1,
                    'country': 'us'
                }
            },
            {
                "name": "Electricity - MWh Unit",
                "data": {
                    'type': 'electricity',
                    'electricity_unit': 'mwh',
                    'electricity_value': 1,
                    'country': 'us'
                }
            }
        ]
        
        for test_case in test_cases:
            response, response_time = self.make_request("/estimates", test_case["data"])
            
            try:
                if response.status_code == 201:
                    data = response.json()
                    
                    # Validate response structure
                    if 'data' in data and 'attributes' in data['data']:
                        attributes = data['data']['attributes']
                        required_fields = ['carbon_kg', 'carbon_lb', 'carbon_mt']
                        missing_fields = [field for field in required_fields if field not in attributes]
                        
                        if not missing_fields:
                            carbon_kg = attributes['carbon_kg']
                            self.log_result(TestResult(
                                endpoint="/estimates",
                                test_name=test_case["name"],
                                status=TestStatus.PASS,
                                response_time=response_time,
                                status_code=response.status_code,
                                error_message=None,
                                data_sample={
                                    "carbon_kg": carbon_kg,
                                    "electricity_value": test_case["data"]["electricity_value"],
                                    "country": test_case["data"]["country"]
                                }
                            ))
                        else:
                            self.log_result(TestResult(
                                endpoint="/estimates",
                                test_name=f"{test_case['name']} - Missing Fields",
                                status=TestStatus.WARNING,
                                response_time=response_time,
                                status_code=response.status_code,
                                error_message=f"Missing fields: {missing_fields}",
                                data_sample=attributes
                            ))
                    else:
                        self.log_result(TestResult(
                            endpoint="/estimates",
                            test_name=f"{test_case['name']} - Invalid Structure",
                            status=TestStatus.FAIL,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message="Invalid response structure",
                            data_sample=data
                        ))
                else:
                    self.log_result(TestResult(
                        endpoint="/estimates",
                        test_name=f"{test_case['name']} - HTTP Error",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=f"HTTP {response.status_code}: {response.text[:200]}",
                        data_sample=None
                    ))
                    
            except Exception as e:
                self.log_result(TestResult(
                    endpoint="/estimates",
                    test_name=f"{test_case['name']} - Exception",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=getattr(response, 'status_code', 0),
                    error_message=str(e),
                    data_sample=None
                ))

    # ==================== VEHICLE EMISSIONS TESTS ====================
    
    def test_vehicle_emissions(self):
        """Test vehicle carbon footprint calculations"""
        test_cases = [
            {
                "name": "Vehicle - Basic Car Trip",
                "data": {
                    'type': 'vehicle',
                    'distance_unit': 'km',
                    'distance_value': 100,
                    'vehicle_model_id': '7268a9b7-17e8-4c8d-acca-57059252afe9'  # Default car model
                }
            },
            {
                "name": "Vehicle - Miles Unit",
                "data": {
                    'type': 'vehicle',
                    'distance_unit': 'mi',
                    'distance_value': 100,
                    'vehicle_model_id': '7268a9b7-17e8-4c8d-acca-57059252afe9'
                }
            },
            {
                "name": "Vehicle - Long Distance",
                "data": {
                    'type': 'vehicle',
                    'distance_unit': 'km',
                    'distance_value': 1000,
                    'vehicle_model_id': '7268a9b7-17e8-4c8d-acca-57059252afe9'
                }
            },
            {
                "name": "Vehicle - Short Distance",
                "data": {
                    'type': 'vehicle',
                    'distance_unit': 'km',
                    'distance_value': 5,
                    'vehicle_model_id': '7268a9b7-17e8-4c8d-acca-57059252afe9'
                }
            }
        ]
        
        for test_case in test_cases:
            response, response_time = self.make_request("/estimates", test_case["data"])
            
            try:
                if response.status_code == 201:
                    data = response.json()
                    
                    if 'data' in data and 'attributes' in data['data']:
                        attributes = data['data']['attributes']
                        carbon_kg = attributes.get('carbon_kg', 0)
                        
                        self.log_result(TestResult(
                            endpoint="/estimates",
                            test_name=test_case["name"],
                            status=TestStatus.PASS,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message=None,
                            data_sample={
                                "carbon_kg": carbon_kg,
                                "distance_value": test_case["data"]["distance_value"],
                                "distance_unit": test_case["data"]["distance_unit"]
                            }
                        ))
                    else:
                        self.log_result(TestResult(
                            endpoint="/estimates",
                            test_name=f"{test_case['name']} - Invalid Structure",
                            status=TestStatus.FAIL,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message="Invalid response structure",
                            data_sample=data
                        ))
                else:
                    self.log_result(TestResult(
                        endpoint="/estimates",
                        test_name=f"{test_case['name']} - HTTP Error",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=f"HTTP {response.status_code}: {response.text[:200]}",
                        data_sample=None
                    ))
                    
            except Exception as e:
                self.log_result(TestResult(
                    endpoint="/estimates",
                    test_name=f"{test_case['name']} - Exception",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=getattr(response, 'status_code', 0),
                    error_message=str(e),
                    data_sample=None
                ))

    # ==================== FLIGHT EMISSIONS TESTS ====================
    
    def test_flight_emissions(self):
        """Test flight carbon footprint calculations"""
        test_cases = [
            {
                "name": "Flight - Domestic Short",
                "data": {
                    'type': 'flight',
                    'passengers': 1,
                    'legs': [
                        {
                            'departure_airport': 'lax',
                            'destination_airport': 'sfo'
                        }
                    ]
                }
            },
            {
                "name": "Flight - International Long",
                "data": {
                    'type': 'flight',
                    'passengers': 1,
                    'legs': [
                        {
                            'departure_airport': 'jfk',
                            'destination_airport': 'lhr'
                        }
                    ]
                }
            },
            {
                "name": "Flight - Multiple Passengers",
                "data": {
                    'type': 'flight',
                    'passengers': 4,
                    'legs': [
                        {
                            'departure_airport': 'ord',
                            'destination_airport': 'lax'
                        }
                    ]
                }
            },
            {
                "name": "Flight - Round Trip",
                "data": {
                    'type': 'flight',
                    'passengers': 1,
                    'legs': [
                        {
                            'departure_airport': 'jfk',
                            'destination_airport': 'lax'
                        },
                        {
                            'departure_airport': 'lax',
                            'destination_airport': 'jfk'
                        }
                    ]
                }
            },
            {
                "name": "Flight - Multi-City Trip",
                "data": {
                    'type': 'flight',
                    'passengers': 1,
                    'legs': [
                        {
                            'departure_airport': 'jfk',
                            'destination_airport': 'lhr'
                        },
                        {
                            'departure_airport': 'lhr',
                            'destination_airport': 'cdg'
                        },
                        {
                            'departure_airport': 'cdg',
                            'destination_airport': 'jfk'
                        }
                    ]
                }
            }
        ]
        
        for test_case in test_cases:
            response, response_time = self.make_request("/estimates", test_case["data"])
            
            try:
                if response.status_code == 201:
                    data = response.json()
                    
                    if 'data' in data and 'attributes' in data['data']:
                        attributes = data['data']['attributes']
                        carbon_kg = attributes.get('carbon_kg', 0)
                        
                        self.log_result(TestResult(
                            endpoint="/estimates",
                            test_name=test_case["name"],
                            status=TestStatus.PASS,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message=None,
                            data_sample={
                                "carbon_kg": carbon_kg,
                                "passengers": test_case["data"]["passengers"],
                                "legs_count": len(test_case["data"]["legs"])
                            }
                        ))
                    else:
                        self.log_result(TestResult(
                            endpoint="/estimates",
                            test_name=f"{test_case['name']} - Invalid Structure",
                            status=TestStatus.FAIL,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message="Invalid response structure",
                            data_sample=data
                        ))
                else:
                    self.log_result(TestResult(
                        endpoint="/estimates",
                        test_name=f"{test_case['name']} - HTTP Error",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=f"HTTP {response.status_code}: {response.text[:200]}",
                        data_sample=None
                    ))
                    
            except Exception as e:
                self.log_result(TestResult(
                    endpoint="/estimates",
                    test_name=f"{test_case['name']} - Exception",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=getattr(response, 'status_code', 0),
                    error_message=str(e),
                    data_sample=None
                ))

    # ==================== SHIPPING EMISSIONS TESTS ====================
    
    def test_shipping_emissions(self):
        """Test shipping carbon footprint calculations"""
        test_cases = [
            {
                "name": "Shipping - Basic Package",
                "data": {
                    'type': 'shipping',
                    'weight_value': 10,
                    'weight_unit': 'kg',
                    'distance_value': 100,
                    'distance_unit': 'km',
                    'transport_method': 'truck'
                }
            },
            {
                "name": "Shipping - Air Transport",
                "data": {
                    'type': 'shipping',
                    'weight_value': 5,
                    'weight_unit': 'kg',
                    'distance_value': 1000,
                    'distance_unit': 'km',
                    'transport_method': 'plane'
                }
            },
            {
                "name": "Shipping - Ship Transport",
                "data": {
                    'type': 'shipping',
                    'weight_value': 100,
                    'weight_unit': 'kg',
                    'distance_value': 5000,
                    'distance_unit': 'km',
                    'transport_method': 'ship'
                }
            },
            {
                "name": "Shipping - Train Transport",
                "data": {
                    'type': 'shipping',
                    'weight_value': 50,
                    'weight_unit': 'kg',
                    'distance_value': 500,
                    'distance_unit': 'km',
                    'transport_method': 'train'
                }
            }
        ]
        
        for test_case in test_cases:
            response, response_time = self.make_request("/estimates", test_case["data"])
            
            try:
                if response.status_code == 201:
                    data = response.json()
                    
                    if 'data' in data and 'attributes' in data['data']:
                        attributes = data['data']['attributes']
                        carbon_kg = attributes.get('carbon_kg', 0)
                        
                        self.log_result(TestResult(
                            endpoint="/estimates",
                            test_name=test_case["name"],
                            status=TestStatus.PASS,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message=None,
                            data_sample={
                                "carbon_kg": carbon_kg,
                                "weight_value": test_case["data"]["weight_value"],
                                "distance_value": test_case["data"]["distance_value"],
                                "transport_method": test_case["data"]["transport_method"]
                            }
                        ))
                    else:
                        self.log_result(TestResult(
                            endpoint="/estimates",
                            test_name=f"{test_case['name']} - Invalid Structure",
                            status=TestStatus.FAIL,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message="Invalid response structure",
                            data_sample=data
                        ))
                elif response.status_code == 422:
                    # Shipping might not be supported or require different parameters
                    self.log_result(TestResult(
                        endpoint="/estimates",
                        test_name=f"{test_case['name']} - Not Supported",
                        status=TestStatus.SKIP,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message="Shipping calculations may not be supported",
                        data_sample=None
                    ))
                else:
                    self.log_result(TestResult(
                        endpoint="/estimates",
                        test_name=f"{test_case['name']} - HTTP Error",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=f"HTTP {response.status_code}: {response.text[:200]}",
                        data_sample=None
                    ))
                    
            except Exception as e:
                self.log_result(TestResult(
                    endpoint="/estimates",
                    test_name=f"{test_case['name']} - Exception",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=getattr(response, 'status_code', 0),
                    error_message=str(e),
                    data_sample=None
                ))

    # ==================== VALIDATION TESTS ====================
    
    def test_input_validation(self):
        """Test input validation and error handling"""
        validation_tests = [
            {
                "name": "Validation - Missing Type",
                "data": {
                    'electricity_unit': 'kwh',
                    'electricity_value': 100,
                    'country': 'us'
                },
                "expected_status": 422
            },
            {
                "name": "Validation - Invalid Type",
                "data": {
                    'type': 'invalid_type',
                    'electricity_unit': 'kwh',
                    'electricity_value': 100,
                    'country': 'us'
                },
                "expected_status": 422
            },
            {
                "name": "Validation - Negative Electricity Value",
                "data": {
                    'type': 'electricity',
                    'electricity_unit': 'kwh',
                    'electricity_value': -100,
                    'country': 'us'
                },
                "expected_status": 422
            },
            {
                "name": "Validation - Invalid Country Code",
                "data": {
                    'type': 'electricity',
                    'electricity_unit': 'kwh',
                    'electricity_value': 100,
                    'country': 'invalid'
                },
                "expected_status": 422
            },
            {
                "name": "Validation - Missing Required Fields",
                "data": {
                    'type': 'electricity'
                },
                "expected_status": 422
            },
            {
                "name": "Validation - Invalid Vehicle Model ID",
                "data": {
                    'type': 'vehicle',
                    'distance_unit': 'km',
                    'distance_value': 100,
                    'vehicle_model_id': 'invalid-id'
                },
                "expected_status": 422
            },
            {
                "name": "Validation - Invalid Airport Code",
                "data": {
                    'type': 'flight',
                    'passengers': 1,
                    'legs': [
                        {
                            'departure_airport': 'invalid',
                            'destination_airport': 'also_invalid'
                        }
                    ]
                },
                "expected_status": 422
            }
        ]
        
        for test in validation_tests:
            response, response_time = self.make_request("/estimates", test["data"])
            
            if response.status_code == test["expected_status"]:
                status = TestStatus.PASS
                error_msg = None
            elif response.status_code == 201:
                status = TestStatus.WARNING
                error_msg = f"Expected {test['expected_status']} but got 201 (validation may be lenient)"
            else:
                status = TestStatus.FAIL
                error_msg = f"Expected {test['expected_status']} but got {response.status_code}"
            
            self.log_result(TestResult(
                endpoint="/estimates",
                test_name=test["name"],
                status=status,
                response_time=response_time,
                status_code=response.status_code,
                error_message=error_msg,
                data_sample=None
            ))

    # ==================== PERFORMANCE TESTS ====================
    
    def test_performance(self):
        """Test API performance and response times"""
        performance_tests = [
            {
                "name": "Performance - Simple Calculation",
                "data": {
                    'type': 'electricity',
                    'electricity_unit': 'kwh',
                    'electricity_value': 100,
                    'country': 'us'
                },
                "max_time": 3.0
            },
            {
                "name": "Performance - Complex Flight",
                "data": {
                    'type': 'flight',
                    'passengers': 1,
                    'legs': [
                        {'departure_airport': 'jfk', 'destination_airport': 'lhr'},
                        {'departure_airport': 'lhr', 'destination_airport': 'nrt'},
                        {'departure_airport': 'nrt', 'destination_airport': 'syd'},
                        {'departure_airport': 'syd', 'destination_airport': 'jfk'}
                    ]
                },
                "max_time": 5.0
            },
            {
                "name": "Performance - Large Electricity Value",
                "data": {
                    'type': 'electricity',
                    'electricity_unit': 'mwh',
                    'electricity_value': 10000,
                    'country': 'us'
                },
                "max_time": 3.0
            }
        ]
        
        for test in performance_tests:
            response, response_time = self.make_request("/estimates", test["data"])
            
            if response.status_code == 201:
                if response_time <= test["max_time"]:
                    status = TestStatus.PASS
                    error_msg = None
                else:
                    status = TestStatus.WARNING
                    error_msg = f"Response time {response_time:.2f}s exceeds threshold {test['max_time']}s"
            else:
                status = TestStatus.FAIL
                error_msg = f"HTTP {response.status_code}"
            
            self.log_result(TestResult(
                endpoint="/estimates",
                test_name=test["name"],
                status=status,
                response_time=response_time,
                status_code=response.status_code,
                error_message=error_msg,
                data_sample=None,
                notes=f"Threshold: {test['max_time']}s"
            ))

    # ==================== CONSISTENCY TESTS ====================
    
    def test_calculation_consistency(self):
        """Test calculation consistency and logical relationships"""
        # Test that doubling input doubles output
        base_data = {
            'type': 'electricity',
            'electricity_unit': 'kwh',
            'electricity_value': 100,
            'country': 'us'
        }
        
        double_data = {
            'type': 'electricity',
            'electricity_unit': 'kwh',
            'electricity_value': 200,
            'country': 'us'
        }
        
        base_response, base_time = self.make_request("/estimates", base_data)
        double_response, double_time = self.make_request("/estimates", double_data)
        
        try:
            if base_response.status_code == 201 and double_response.status_code == 201:
                base_carbon = base_response.json()['data']['attributes']['carbon_kg']
                double_carbon = double_response.json()['data']['attributes']['carbon_kg']
                
                # Check if doubling input approximately doubles output (within 5% tolerance)
                expected_double = base_carbon * 2
                tolerance = expected_double * 0.05
                
                if abs(double_carbon - expected_double) <= tolerance:
                    status = TestStatus.PASS
                    error_msg = None
                else:
                    status = TestStatus.WARNING
                    error_msg = f"Inconsistent scaling: {base_carbon} * 2 ≠ {double_carbon}"
                
                self.log_result(TestResult(
                    endpoint="/estimates",
                    test_name="Consistency - Linear Scaling",
                    status=status,
                    response_time=base_time + double_time,
                    status_code=200,
                    error_message=error_msg,
                    data_sample={
                        "base_carbon": base_carbon,
                        "double_carbon": double_carbon,
                        "expected_double": expected_double
                    }
                ))
            else:
                self.log_result(TestResult(
                    endpoint="/estimates",
                    test_name="Consistency - Linear Scaling Failed",
                    status=TestStatus.FAIL,
                    response_time=base_time + double_time,
                    status_code=None,
                    error_message="Could not perform consistency test due to API errors",
                    data_sample=None
                ))
                
        except Exception as e:
            self.log_result(TestResult(
                endpoint="/estimates",
                test_name="Consistency - Exception",
                status=TestStatus.FAIL,
                response_time=base_time + double_time,
                status_code=None,
                error_message=str(e),
                data_sample=None
            ))

    # ==================== MAIN TEST RUNNER ====================
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🧪 Carbon Interface API Comprehensive Testing Framework")
        print("=" * 80)
        print(f"🌐 Base URL: {self.base_url}")
        print(f"🔑 API Key: {'✅ Provided' if self.api_key else '❌ Missing'}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        if not self.api_key:
            print("⚠️  No API key provided. Most tests will be skipped.")
            print("   Set CARBON_INTERFACE_API_KEY environment variable to run full tests.")
            print()
        
        # Run test suites
        print("🔐 Testing Authentication...")
        self.test_authentication()
        
        if self.api_key:
            print("\n⚡ Testing Electricity Emissions...")
            self.test_electricity_emissions()
            
            print("\n🚗 Testing Vehicle Emissions...")
            self.test_vehicle_emissions()
            
            print("\n✈️ Testing Flight Emissions...")
            self.test_flight_emissions()
            
            print("\n📦 Testing Shipping Emissions...")
            self.test_shipping_emissions()
            
            print("\n✅ Testing Input Validation...")
            self.test_input_validation()
            
            print("\n⚡ Testing Performance...")
            self.test_performance()
            
            print("\n🔄 Testing Calculation Consistency...")
            self.test_calculation_consistency()
        
        # Generate summary report
        self.generate_summary_report()

    def generate_summary_report(self):
        """Generate comprehensive test summary report"""
        total_time = time.time() - self.start_time
        
        # Count results by status
        status_counts = {}
        for status in TestStatus:
            status_counts[status] = len([r for r in self.test_results if r.status == status])
        
        # Calculate statistics
        total_tests = len(self.test_results)
        pass_rate = (status_counts[TestStatus.PASS] / total_tests * 100) if total_tests > 0 else 0
        avg_response_time = sum(r.response_time for r in self.test_results) / total_tests if total_tests > 0 else 0
        
        # Group results by test type
        test_types = {}
        for result in self.test_results:
            test_type = result.test_name.split(' - ')[0]
            if test_type not in test_types:
                test_types[test_type] = []
            test_types[test_type].append(result)
        
        print("\n" + "=" * 80)
        print("📊 CARBON INTERFACE API TEST SUMMARY REPORT")
        print("=" * 80)
        print(f"⏱️  Total Execution Time: {total_time:.2f} seconds")
        print(f"🧪 Total Tests: {total_tests}")
        print(f"📈 Pass Rate: {pass_rate:.1f}%")
        print(f"⚡ Average Response Time: {avg_response_time:.2f}s")
        print()
        
        print("📋 Results by Status:")
        for status in TestStatus:
            count = status_counts[status]
            percentage = (count / total_tests * 100) if total_tests > 0 else 0
            print(f"   {status.value}: {count} ({percentage:.1f}%)")
        print()
        
        print("🧪 Results by Test Type:")
        for test_type, results in test_types.items():
            passed = len([r for r in results if r.status == TestStatus.PASS])
            total = len(results)
            success_rate = (passed / total * 100) if total > 0 else 0
            avg_time = sum(r.response_time for r in results) / total if total > 0 else 0
            print(f"   {test_type}: {passed}/{total} ({success_rate:.1f}%) - Avg: {avg_time:.2f}s")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if r.status == TestStatus.FAIL]
        if failed_tests:
            print("\n❌ Failed Tests:")
            for result in failed_tests:
                print(f"   • {result.test_name}: {result.error_message}")
        
        # Show warnings
        warning_tests = [r for r in self.test_results if r.status == TestStatus.WARNING]
        if warning_tests:
            print("\n⚠️  Warnings:")
            for result in warning_tests:
                print(f"   • {result.test_name}: {result.notes or result.error_message}")
        
        print("\n" + "=" * 80)
        print("✅ Testing Complete!")
        
        # Save detailed results to file
        self.save_detailed_report()

    def save_detailed_report(self):
        """Save detailed test results to JSON file"""
        report_data = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "has_api_key": bool(self.api_key),
                "total_time": time.time() - self.start_time,
                "total_tests": len(self.test_results)
            },
            "results": [
                {
                    "endpoint": r.endpoint,
                    "test_name": r.test_name,
                    "status": r.status.name,
                    "response_time": r.response_time,
                    "status_code": r.status_code,
                    "error_message": r.error_message,
                    "data_sample": r.data_sample,
                    "notes": r.notes
                }
                for r in self.test_results
            ]
        }
        
        filename = f"carbon_interface_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"📄 Detailed report saved to: {filepath}")
        except Exception as e:
            print(f"⚠️  Could not save detailed report: {e}")


def main():
    """Main test runner"""
    tester = CarbonInterfaceAPITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()