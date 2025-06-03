#!/usr/bin/env python3
"""
Comprehensive ClimateTRACE API v6 Testing Framework
Tests all endpoints, parameters, and edge cases based on OpenAPI specification
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
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

class ClimateTraceAPITester:
    """Comprehensive ClimateTRACE API v6 Testing Framework"""
    
    def __init__(self, base_url: str = "https://api.climatetrace.org/v6"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ClimateIQ-TestFramework/1.0',
            'Accept': 'application/json'
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
    
    def make_request(self, endpoint: str, params: Dict = None, method: str = "GET") -> Tuple[requests.Response, float]:
        """Make HTTP request with timing"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=params, timeout=30)
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

    # ==================== DEFINITIONS ENDPOINTS ====================
    
    def test_definitions_sectors(self):
        """Test /v6/definitions/sectors endpoint"""
        response, response_time = self.make_request("/definitions/sectors")
        
        try:
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if isinstance(data, dict):
                    expected_sectors = [
                        "power", "transportation", "buildings", "fossil-fuel-operations",
                        "manufacturing", "mineral-extraction", "agriculture", "waste",
                        "fluorinated-gases", "forestry-and-land-use"
                    ]
                    
                    found_sectors = list(data.keys())
                    missing_sectors = [s for s in expected_sectors if s not in found_sectors]
                    
                    if missing_sectors:
                        self.log_result(TestResult(
                            endpoint="/definitions/sectors",
                            test_name="Sectors Definition - Structure",
                            status=TestStatus.WARNING,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message=None,
                            data_sample={"found_sectors": found_sectors[:5]},
                            notes=f"Missing expected sectors: {missing_sectors}"
                        ))
                    else:
                        self.log_result(TestResult(
                            endpoint="/definitions/sectors",
                            test_name="Sectors Definition - Complete",
                            status=TestStatus.PASS,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message=None,
                            data_sample={"sectors_count": len(data), "sample": dict(list(data.items())[:3])}
                        ))
                else:
                    self.log_result(TestResult(
                        endpoint="/definitions/sectors",
                        test_name="Sectors Definition - Format",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message="Expected dict format",
                        data_sample={"actual_type": type(data).__name__}
                    ))
            else:
                self.log_result(TestResult(
                    endpoint="/definitions/sectors",
                    test_name="Sectors Definition - HTTP",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=response.status_code,
                    error_message=f"HTTP {response.status_code}: {response.text[:200]}",
                    data_sample=None
                ))
                
        except Exception as e:
            self.log_result(TestResult(
                endpoint="/definitions/sectors",
                test_name="Sectors Definition - Exception",
                status=TestStatus.FAIL,
                response_time=response_time,
                status_code=getattr(response, 'status_code', 0),
                error_message=str(e),
                data_sample=None
            ))

    def test_definitions_subsectors(self):
        """Test /v6/definitions/subsectors endpoint"""
        response, response_time = self.make_request("/definitions/subsectors")
        
        try:
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    expected_subsectors = [
                        "electricity-generation", "steel", "cement", "aluminum",
                        "domestic-shipping-ship", "international-shipping-ship",
                        "domestic-aviation", "international-aviation",
                        "road-transportation-urban-area", "oil-and-gas-production-and-transport"
                    ]
                    
                    found_count = len(data)
                    sample_subsectors = data[:5] if data else []
                    
                    self.log_result(TestResult(
                        endpoint="/definitions/subsectors",
                        test_name="Subsectors Definition",
                        status=TestStatus.PASS,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=None,
                        data_sample={"count": found_count, "sample": sample_subsectors}
                    ))
                else:
                    self.log_result(TestResult(
                        endpoint="/definitions/subsectors",
                        test_name="Subsectors Definition - Format",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message="Expected array format",
                        data_sample={"actual_type": type(data).__name__}
                    ))
            else:
                self.log_result(TestResult(
                    endpoint="/definitions/subsectors",
                    test_name="Subsectors Definition - HTTP",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=response.status_code,
                    error_message=f"HTTP {response.status_code}",
                    data_sample=None
                ))
                
        except Exception as e:
            self.log_result(TestResult(
                endpoint="/definitions/subsectors",
                test_name="Subsectors Definition - Exception",
                status=TestStatus.FAIL,
                response_time=response_time,
                status_code=getattr(response, 'status_code', 0),
                error_message=str(e),
                data_sample=None
            ))

    def test_definitions_countries(self):
        """Test /v6/definitions/countries endpoint"""
        response, response_time = self.make_request("/definitions/countries")
        
        try:
            if response.status_code == 200:
                data = response.json()
                
                # The API returns an object with Name and Code properties
                if isinstance(data, (dict, list)):
                    self.log_result(TestResult(
                        endpoint="/definitions/countries",
                        test_name="Countries Definition",
                        status=TestStatus.PASS,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=None,
                        data_sample={"type": type(data).__name__, "sample": str(data)[:200]}
                    ))
                else:
                    self.log_result(TestResult(
                        endpoint="/definitions/countries",
                        test_name="Countries Definition - Format",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message="Unexpected format",
                        data_sample={"actual_type": type(data).__name__}
                    ))
            else:
                self.log_result(TestResult(
                    endpoint="/definitions/countries",
                    test_name="Countries Definition - HTTP",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=response.status_code,
                    error_message=f"HTTP {response.status_code}",
                    data_sample=None
                ))
                
        except Exception as e:
            self.log_result(TestResult(
                endpoint="/definitions/countries",
                test_name="Countries Definition - Exception",
                status=TestStatus.FAIL,
                response_time=response_time,
                status_code=getattr(response, 'status_code', 0),
                error_message=str(e),
                data_sample=None
            ))

    def test_definitions_groups(self):
        """Test /v6/definitions/groups endpoint"""
        response, response_time = self.make_request("/definitions/groups")
        
        try:
            if response.status_code == 200:
                data = response.json()
                
                self.log_result(TestResult(
                    endpoint="/definitions/groups",
                    test_name="Groups Definition",
                    status=TestStatus.PASS,
                    response_time=response_time,
                    status_code=response.status_code,
                    error_message=None,
                    data_sample={"type": type(data).__name__, "sample": str(data)[:200]}
                ))
            else:
                self.log_result(TestResult(
                    endpoint="/definitions/groups",
                    test_name="Groups Definition - HTTP",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=response.status_code,
                    error_message=f"HTTP {response.status_code}",
                    data_sample=None
                ))
                
        except Exception as e:
            self.log_result(TestResult(
                endpoint="/definitions/groups",
                test_name="Groups Definition - Exception",
                status=TestStatus.FAIL,
                response_time=response_time,
                status_code=getattr(response, 'status_code', 0),
                error_message=str(e),
                data_sample=None
            ))

    def test_definitions_continents(self):
        """Test /v6/definitions/continents endpoint"""
        response, response_time = self.make_request("/definitions/continents")
        
        try:
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    expected_continents = ["Asia", "South America", "North America", "Oceania", "Antarctica", "Africa", "Europe"]
                    
                    self.log_result(TestResult(
                        endpoint="/definitions/continents",
                        test_name="Continents Definition",
                        status=TestStatus.PASS,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=None,
                        data_sample={"count": len(data), "continents": data}
                    ))
                else:
                    self.log_result(TestResult(
                        endpoint="/definitions/continents",
                        test_name="Continents Definition - Format",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message="Expected array format",
                        data_sample={"actual_type": type(data).__name__}
                    ))
            else:
                self.log_result(TestResult(
                    endpoint="/definitions/continents",
                    test_name="Continents Definition - HTTP",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=response.status_code,
                    error_message=f"HTTP {response.status_code}",
                    data_sample=None
                ))
                
        except Exception as e:
            self.log_result(TestResult(
                endpoint="/definitions/continents",
                test_name="Continents Definition - Exception",
                status=TestStatus.FAIL,
                response_time=response_time,
                status_code=getattr(response, 'status_code', 0),
                error_message=str(e),
                data_sample=None
            ))

    def test_definitions_gases(self):
        """Test /v6/definitions/gases endpoint"""
        response, response_time = self.make_request("/definitions/gases")
        
        try:
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    expected_gases = ["n2o", "co2e", "co2", "ch4", "co2e_20yr", "co2e_100yr"]
                    
                    self.log_result(TestResult(
                        endpoint="/definitions/gases",
                        test_name="Gases Definition",
                        status=TestStatus.PASS,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=None,
                        data_sample={"count": len(data), "gases": data}
                    ))
                else:
                    self.log_result(TestResult(
                        endpoint="/definitions/gases",
                        test_name="Gases Definition - Format",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message="Expected array format",
                        data_sample={"actual_type": type(data).__name__}
                    ))
            else:
                self.log_result(TestResult(
                    endpoint="/definitions/gases",
                    test_name="Gases Definition - HTTP",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=response.status_code,
                    error_message=f"HTTP {response.status_code}",
                    data_sample=None
                ))
                
        except Exception as e:
            self.log_result(TestResult(
                endpoint="/definitions/gases",
                test_name="Gases Definition - Exception",
                status=TestStatus.FAIL,
                response_time=response_time,
                status_code=getattr(response, 'status_code', 0),
                error_message=str(e),
                data_sample=None
            ))

    # ==================== ASSETS ENDPOINTS ====================
    
    def test_assets_search(self):
        """Test /v6/assets endpoint with various parameters"""
        test_cases = [
            {
                "name": "Basic Assets Search",
                "params": {"limit": 10, "year": 2022}
            },
            {
                "name": "Assets by Country",
                "params": {"countries": "USA", "limit": 5, "year": 2022}
            },
            {
                "name": "Assets by Sector",
                "params": {"sectors": "power", "limit": 5, "year": 2022}
            },
            {
                "name": "Assets by Multiple Countries",
                "params": {"countries": "USA,CHN,IND", "limit": 10, "year": 2022}
            },
            {
                "name": "Assets with Continent Filter",
                "params": {"continents": "North America", "limit": 5, "year": 2022}
            }
        ]
        
        for test_case in test_cases:
            response, response_time = self.make_request("/assets", test_case["params"])
            
            try:
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list):
                        self.log_result(TestResult(
                            endpoint="/assets",
                            test_name=test_case["name"],
                            status=TestStatus.PASS,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message=None,
                            data_sample={"count": len(data), "sample": data[0] if data else None}
                        ))
                    else:
                        self.log_result(TestResult(
                            endpoint="/assets",
                            test_name=f"{test_case['name']} - Format",
                            status=TestStatus.FAIL,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message="Expected array format",
                            data_sample={"actual_type": type(data).__name__}
                        ))
                else:
                    self.log_result(TestResult(
                        endpoint="/assets",
                        test_name=f"{test_case['name']} - HTTP",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=f"HTTP {response.status_code}",
                        data_sample=None
                    ))
                    
            except Exception as e:
                self.log_result(TestResult(
                    endpoint="/assets",
                    test_name=f"{test_case['name']} - Exception",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=getattr(response, 'status_code', 0),
                    error_message=str(e),
                    data_sample=None
                ))

    def test_assets_by_id(self):
        """Test /v6/assets/{sourceId} endpoint"""
        # First get some asset IDs from the search
        response, _ = self.make_request("/assets", {"limit": 5, "year": 2022})
        
        if response.status_code == 200:
            try:
                assets = response.json()
                if assets and isinstance(assets, list):
                    # Try to get an asset ID from the first result
                    first_asset = assets[0]
                    if isinstance(first_asset, dict) and 'id' in first_asset:
                        asset_id = first_asset['id']
                        
                        # Test getting specific asset
                        response, response_time = self.make_request(f"/assets/{asset_id}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            self.log_result(TestResult(
                                endpoint=f"/assets/{asset_id}",
                                test_name="Asset by ID",
                                status=TestStatus.PASS,
                                response_time=response_time,
                                status_code=response.status_code,
                                error_message=None,
                                data_sample={"asset_id": asset_id, "type": type(data).__name__}
                            ))
                        else:
                            self.log_result(TestResult(
                                endpoint=f"/assets/{asset_id}",
                                test_name="Asset by ID - HTTP",
                                status=TestStatus.FAIL,
                                response_time=response_time,
                                status_code=response.status_code,
                                error_message=f"HTTP {response.status_code}",
                                data_sample=None
                            ))
                    else:
                        # Test with a sample ID
                        sample_id = 12345
                        response, response_time = self.make_request(f"/assets/{sample_id}")
                        
                        self.log_result(TestResult(
                            endpoint=f"/assets/{sample_id}",
                            test_name="Asset by Sample ID",
                            status=TestStatus.WARNING,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message=None,
                            data_sample=None,
                            notes="Used sample ID as no valid ID found in assets search"
                        ))
                else:
                    self.log_result(TestResult(
                        endpoint="/assets/{id}",
                        test_name="Asset by ID - No Assets",
                        status=TestStatus.SKIP,
                        response_time=0,
                        status_code=None,
                        error_message="No assets found to test with",
                        data_sample=None
                    ))
            except Exception as e:
                self.log_result(TestResult(
                    endpoint="/assets/{id}",
                    test_name="Asset by ID - Exception",
                    status=TestStatus.FAIL,
                    response_time=0,
                    status_code=getattr(response, 'status_code', 0),
                    error_message=str(e),
                    data_sample=None
                ))
        else:
            self.log_result(TestResult(
                endpoint="/assets/{id}",
                test_name="Asset by ID - Prerequisites Failed",
                status=TestStatus.SKIP,
                response_time=0,
                status_code=None,
                error_message="Could not get assets list for ID testing",
                data_sample=None
            ))

    def test_assets_emissions(self):
        """Test /v6/assets/emissions endpoint"""
        test_cases = [
            {
                "name": "Basic Asset Emissions",
                "params": {"years": "2022", "gas": "co2e_100yr"}
            },
            {
                "name": "Asset Emissions by Country",
                "params": {"countries": "USA", "years": "2022", "gas": "co2e_100yr"}
            },
            {
                "name": "Asset Emissions by Sector",
                "params": {"sectors": "power", "years": "2022", "gas": "co2e_100yr"}
            },
            {
                "name": "Asset Emissions Multiple Years",
                "params": {"years": "2021,2022", "gas": "co2e_100yr"}
            },
            {
                "name": "Asset Emissions by Continent",
                "params": {"continents": "North America", "years": "2022", "gas": "co2e_100yr"}
            }
        ]
        
        for test_case in test_cases:
            response, response_time = self.make_request("/assets/emissions", test_case["params"])
            
            try:
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list):
                        # Validate structure of emissions data
                        valid_structure = True
                        if data:
                            first_item = data[0]
                            required_fields = ["AssetCount", "Emissions", "Gas"]
                            missing_fields = [field for field in required_fields if field not in first_item]
                            if missing_fields:
                                valid_structure = False
                        
                        status = TestStatus.PASS if valid_structure else TestStatus.WARNING
                        self.log_result(TestResult(
                            endpoint="/assets/emissions",
                            test_name=test_case["name"],
                            status=status,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message=None,
                            data_sample={"count": len(data), "sample": data[0] if data else None},
                            notes="Missing required fields" if not valid_structure else None
                        ))
                    else:
                        self.log_result(TestResult(
                            endpoint="/assets/emissions",
                            test_name=f"{test_case['name']} - Format",
                            status=TestStatus.FAIL,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message="Expected array format",
                            data_sample={"actual_type": type(data).__name__}
                        ))
                else:
                    self.log_result(TestResult(
                        endpoint="/assets/emissions",
                        test_name=f"{test_case['name']} - HTTP",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=f"HTTP {response.status_code}",
                        data_sample=None
                    ))
                    
            except Exception as e:
                self.log_result(TestResult(
                    endpoint="/assets/emissions",
                    test_name=f"{test_case['name']} - Exception",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=getattr(response, 'status_code', 0),
                    error_message=str(e),
                    data_sample=None
                ))

    # ==================== COUNTRY ENDPOINTS ====================
    
    def test_country_emissions(self):
        """Test /v6/country/emissions endpoint"""
        test_cases = [
            {
                "name": "Country Emissions - Basic",
                "params": {"countries": "USA", "since": 2022, "to": 2022}
            },
            {
                "name": "Country Emissions - Multiple Countries",
                "params": {"countries": "USA,CHN,IND", "since": 2021, "to": 2022}
            },
            {
                "name": "Country Emissions - By Sector",
                "params": {"countries": "USA", "sector": ["power"], "since": 2022, "to": 2022}
            },
            {
                "name": "Country Emissions - By Continent",
                "params": {"continents": "North America", "since": 2022, "to": 2022}
            },
            {
                "name": "Country Emissions - Time Range",
                "params": {"countries": "USA", "since": 2020, "to": 2022}
            }
        ]
        
        for test_case in test_cases:
            response, response_time = self.make_request("/country/emissions", test_case["params"])
            
            try:
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list):
                        # Validate structure
                        valid_structure = True
                        if data:
                            first_item = data[0]
                            expected_fields = ["Country", "Emissions"]
                            missing_fields = [field for field in expected_fields if field not in first_item]
                            if missing_fields:
                                valid_structure = False
                        
                        status = TestStatus.PASS if valid_structure else TestStatus.WARNING
                        self.log_result(TestResult(
                            endpoint="/country/emissions",
                            test_name=test_case["name"],
                            status=status,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message=None,
                            data_sample={"count": len(data), "sample": data[0] if data else None},
                            notes="Missing expected fields" if not valid_structure else None
                        ))
                    else:
                        self.log_result(TestResult(
                            endpoint="/country/emissions",
                            test_name=f"{test_case['name']} - Format",
                            status=TestStatus.FAIL,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message="Expected array format",
                            data_sample={"actual_type": type(data).__name__}
                        ))
                else:
                    self.log_result(TestResult(
                        endpoint="/country/emissions",
                        test_name=f"{test_case['name']} - HTTP",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=f"HTTP {response.status_code}",
                        data_sample=None
                    ))
                    
            except Exception as e:
                self.log_result(TestResult(
                    endpoint="/country/emissions",
                    test_name=f"{test_case['name']} - Exception",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=getattr(response, 'status_code', 0),
                    error_message=str(e),
                    data_sample=None
                ))

    # ==================== ADMINISTRATIVE AREAS ENDPOINTS ====================
    
    def test_admins_search(self):
        """Test /v6/admins/search endpoint"""
        test_cases = [
            {
                "name": "Admin Search - By Name",
                "params": {"name": "California", "limit": 5}
            },
            {
                "name": "Admin Search - By Level",
                "params": {"level": 1, "limit": 10}
            },
            {
                "name": "Admin Search - By Point",
                "params": {"point": [-74.0, 40.7], "limit": 5}  # New York coordinates
            },
            {
                "name": "Admin Search - By Bbox",
                "params": {"bbox": [-75.0, 40.0, -73.0, 41.0], "limit": 5}  # NYC area
            }
        ]
        
        for test_case in test_cases:
            response, response_time = self.make_request("/admins/search", test_case["params"])
            
            try:
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list):
                        self.log_result(TestResult(
                            endpoint="/admins/search",
                            test_name=test_case["name"],
                            status=TestStatus.PASS,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message=None,
                            data_sample={"count": len(data), "sample": data[0] if data else None}
                        ))
                    else:
                        self.log_result(TestResult(
                            endpoint="/admins/search",
                            test_name=f"{test_case['name']} - Format",
                            status=TestStatus.FAIL,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message="Expected array format",
                            data_sample={"actual_type": type(data).__name__}
                        ))
                else:
                    self.log_result(TestResult(
                        endpoint="/admins/search",
                        test_name=f"{test_case['name']} - HTTP",
                        status=TestStatus.FAIL,
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=f"HTTP {response.status_code}",
                        data_sample=None
                    ))
                    
            except Exception as e:
                self.log_result(TestResult(
                    endpoint="/admins/search",
                    test_name=f"{test_case['name']} - Exception",
                    status=TestStatus.FAIL,
                    response_time=response_time,
                    status_code=getattr(response, 'status_code', 0),
                    error_message=str(e),
                    data_sample=None
                ))

    def test_admin_geojson(self):
        """Test /v6/admins/{adminId}/geojson endpoint"""
        # First try to get an admin ID from search
        response, _ = self.make_request("/admins/search", {"name": "California", "limit": 1})
        
        if response.status_code == 200:
            try:
                admins = response.json()
                if admins and isinstance(admins, list) and len(admins) > 0:
                    admin_id = admins[0].get('id')
                    if admin_id:
                        # Test getting GeoJSON for this admin
                        response, response_time = self.make_request(f"/admins/{admin_id}/geojson")
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Validate GeoJSON structure
                            is_valid_geojson = (
                                isinstance(data, dict) and
                                data.get('type') == 'Feature' and
                                'geometry' in data and
                                'properties' in data
                            )
                            
                            status = TestStatus.PASS if is_valid_geojson else TestStatus.WARNING
                            self.log_result(TestResult(
                                endpoint=f"/admins/{admin_id}/geojson",
                                test_name="Admin GeoJSON",
                                status=status,
                                response_time=response_time,
                                status_code=response.status_code,
                                error_message=None,
                                data_sample={"admin_id": admin_id, "type": data.get('type'), "has_geometry": 'geometry' in data},
                                notes="Invalid GeoJSON structure" if not is_valid_geojson else None
                            ))
                        else:
                            self.log_result(TestResult(
                                endpoint=f"/admins/{admin_id}/geojson",
                                test_name="Admin GeoJSON - HTTP",
                                status=TestStatus.FAIL,
                                response_time=response_time,
                                status_code=response.status_code,
                                error_message=f"HTTP {response.status_code}",
                                data_sample=None
                            ))
                    else:
                        # Test with sample admin ID
                        sample_admin_id = "USA.1_1"
                        response, response_time = self.make_request(f"/admins/{sample_admin_id}/geojson")
                        
                        self.log_result(TestResult(
                            endpoint=f"/admins/{sample_admin_id}/geojson",
                            test_name="Admin GeoJSON - Sample ID",
                            status=TestStatus.WARNING,
                            response_time=response_time,
                            status_code=response.status_code,
                            error_message=None,
                            data_sample=None,
                            notes="Used sample admin ID as no valid ID found"
                        ))
                else:
                    self.log_result(TestResult(
                        endpoint="/admins/{id}/geojson",
                        test_name="Admin GeoJSON - No Admins",
                        status=TestStatus.SKIP,
                        response_time=0,
                        status_code=None,
                        error_message="No admin areas found to test with",
                        data_sample=None
                    ))
            except Exception as e:
                self.log_result(TestResult(
                    endpoint="/admins/{id}/geojson",
                    test_name="Admin GeoJSON - Exception",
                    status=TestStatus.FAIL,
                    response_time=0,
                    status_code=getattr(response, 'status_code', 0),
                    error_message=str(e),
                    data_sample=None
                ))
        else:
            self.log_result(TestResult(
                endpoint="/admins/{id}/geojson",
                test_name="Admin GeoJSON - Prerequisites Failed",
                status=TestStatus.SKIP,
                response_time=0,
                status_code=None,
                error_message="Could not get admin list for GeoJSON testing",
                data_sample=None
            ))

    # ==================== PARAMETER VALIDATION TESTS ====================
    
    def test_parameter_validation(self):
        """Test parameter validation and edge cases"""
        validation_tests = [
            {
                "name": "Invalid Year - Too Early",
                "endpoint": "/assets",
                "params": {"year": 1999, "limit": 5},
                "expected_status": 400
            },
            {
                "name": "Invalid Year - Too Late",
                "endpoint": "/assets",
                "params": {"year": 2051, "limit": 5},
                "expected_status": 400
            },
            {
                "name": "Invalid Limit - Too High",
                "endpoint": "/assets",
                "params": {"limit": 2000, "year": 2022},
                "expected_status": 400
            },
            {
                "name": "Invalid Country Code",
                "endpoint": "/country/emissions",
                "params": {"countries": "INVALID", "since": 2022, "to": 2022},
                "expected_status": 400
            },
            {
                "name": "Invalid Gas Type",
                "endpoint": "/assets/emissions",
                "params": {"gas": "invalid_gas", "years": "2022"},
                "expected_status": 400
            },
            {
                "name": "Invalid Date Range",
                "endpoint": "/country/emissions",
                "params": {"countries": "USA", "since": 2023, "to": 2022},
                "expected_status": 400
            }
        ]
        
        for test in validation_tests:
            response, response_time = self.make_request(test["endpoint"], test["params"])
            
            if response.status_code == test["expected_status"]:
                status = TestStatus.PASS
                error_msg = None
            elif response.status_code == 200:
                status = TestStatus.WARNING
                error_msg = f"Expected {test['expected_status']} but got 200 (validation may be lenient)"
            else:
                status = TestStatus.FAIL
                error_msg = f"Expected {test['expected_status']} but got {response.status_code}"
            
            self.log_result(TestResult(
                endpoint=test["endpoint"],
                test_name=f"Validation: {test['name']}",
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
                "name": "Large Dataset Request",
                "endpoint": "/assets",
                "params": {"limit": 1000, "year": 2022},
                "max_time": 10.0
            },
            {
                "name": "Multiple Countries Request",
                "endpoint": "/country/emissions",
                "params": {"countries": "USA,CHN,IND,RUS,JPN,DEU,GBR,FRA,ITA,BRA", "since": 2022, "to": 2022},
                "max_time": 5.0
            },
            {
                "name": "Complex Asset Emissions Query",
                "endpoint": "/assets/emissions",
                "params": {"years": "2020,2021,2022", "gas": "co2e_100yr", "sectors": "power,transportation"},
                "max_time": 8.0
            }
        ]
        
        for test in performance_tests:
            response, response_time = self.make_request(test["endpoint"], test["params"])
            
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
            
            self.log_result(TestResult(
                endpoint=test["endpoint"],
                test_name=f"Performance: {test['name']}",
                status=status,
                response_time=response_time,
                status_code=response.status_code,
                error_message=error_msg,
                data_sample=None,
                notes=f"Threshold: {test['max_time']}s"
            ))

    # ==================== MAIN TEST RUNNER ====================
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🧪 ClimateTRACE API v6 Comprehensive Testing Framework")
        print("=" * 80)
        print(f"🌐 Base URL: {self.base_url}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run test suites
        print("📋 Testing Definitions Endpoints...")
        self.test_definitions_sectors()
        self.test_definitions_subsectors()
        self.test_definitions_countries()
        self.test_definitions_groups()
        self.test_definitions_continents()
        self.test_definitions_gases()
        
        print("\n🏭 Testing Assets Endpoints...")
        self.test_assets_search()
        self.test_assets_by_id()
        self.test_assets_emissions()
        
        print("\n🌍 Testing Country Endpoints...")
        self.test_country_emissions()
        
        print("\n🗺️ Testing Administrative Areas Endpoints...")
        self.test_admins_search()
        self.test_admin_geojson()
        
        print("\n✅ Testing Parameter Validation...")
        self.test_parameter_validation()
        
        print("\n⚡ Testing Performance...")
        self.test_performance()
        
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
        
        # Group results by endpoint
        endpoint_results = {}
        for result in self.test_results:
            endpoint = result.endpoint.split('?')[0]  # Remove query params
            if endpoint not in endpoint_results:
                endpoint_results[endpoint] = []
            endpoint_results[endpoint].append(result)
        
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY REPORT")
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
        
        print("🌐 Results by Endpoint:")
        for endpoint, results in endpoint_results.items():
            passed = len([r for r in results if r.status == TestStatus.PASS])
            total = len(results)
            success_rate = (passed / total * 100) if total > 0 else 0
            avg_time = sum(r.response_time for r in results) / total if total > 0 else 0
            print(f"   {endpoint}: {passed}/{total} ({success_rate:.1f}%) - Avg: {avg_time:.2f}s")
        
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
        
        filename = f"climate_trace_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"📄 Detailed report saved to: {filepath}")
        except Exception as e:
            print(f"⚠️  Could not save detailed report: {e}")


def main():
    """Main test runner"""
    tester = ClimateTraceAPITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()