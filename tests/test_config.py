#!/usr/bin/env python3
"""
Test Configuration for Climate API Testing Framework
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class TestMode(Enum):
    """Test execution modes"""
    LIVE = "live"  # Test against real APIs
    MOCK = "mock"  # Use mock data
    HYBRID = "hybrid"  # Use mock data when APIs fail

class TestLevel(Enum):
    """Test complexity levels"""
    BASIC = "basic"  # Basic connectivity tests
    STANDARD = "standard"  # Standard functionality tests
    COMPREHENSIVE = "comprehensive"  # Full test suite including edge cases
    PERFORMANCE = "performance"  # Performance and load tests

@dataclass
class APITestConfig:
    """Configuration for individual API testing"""
    enabled: bool = True
    test_level: TestLevel = TestLevel.STANDARD
    timeout: int = 30
    retry_count: int = 3
    rate_limit_delay: float = 1.0
    mock_on_failure: bool = True
    custom_endpoints: Optional[Dict[str, str]] = None

@dataclass
class TestConfiguration:
    """Main test configuration"""
    # Test execution settings
    test_mode: TestMode = TestMode.HYBRID
    test_level: TestLevel = TestLevel.STANDARD
    parallel_execution: bool = False
    max_workers: int = 4
    
    # Output settings
    verbose: bool = True
    save_reports: bool = True
    report_format: List[str] = None
    output_directory: str = "./tests/reports"
    
    # API configurations
    climate_trace: APITestConfig = None
    carbon_interface: APITestConfig = None
    openweather: APITestConfig = None
    nasa_power: APITestConfig = None
    world_bank: APITestConfig = None
    un_sdg: APITestConfig = None
    
    # Performance test settings
    performance_thresholds: Dict[str, float] = None
    load_test_duration: int = 60
    concurrent_requests: int = 10
    
    def __post_init__(self):
        if self.report_format is None:
            self.report_format = ["json", "csv", "html"]
        
        if self.climate_trace is None:
            self.climate_trace = APITestConfig()
        
        if self.carbon_interface is None:
            self.carbon_interface = APITestConfig(
                mock_on_failure=True,
                timeout=10
            )
        
        if self.openweather is None:
            self.openweather = APITestConfig(
                enabled=bool(os.getenv("OPENWEATHER_API_KEY")),
                timeout=10
            )
        
        if self.nasa_power is None:
            self.nasa_power = APITestConfig(timeout=15)
        
        if self.world_bank is None:
            self.world_bank = APITestConfig(timeout=10)
        
        if self.un_sdg is None:
            self.un_sdg = APITestConfig(timeout=10)
        
        if self.performance_thresholds is None:
            self.performance_thresholds = {
                "climate_trace": 5.0,
                "carbon_interface": 3.0,
                "openweather": 2.0,
                "nasa_power": 8.0,
                "world_bank": 5.0,
                "un_sdg": 3.0
            }

# Test data configurations
TEST_LOCATIONS = [
    {"name": "New York", "lat": 40.7128, "lon": -74.0060, "country": "USA"},
    {"name": "London", "lat": 51.5074, "lon": -0.1278, "country": "GBR"},
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503, "country": "JPN"},
    {"name": "Sydney", "lat": -33.8688, "lon": 151.2093, "country": "AUS"},
    {"name": "São Paulo", "lat": -23.5505, "lon": -46.6333, "country": "BRA"}
]

TEST_COUNTRIES = ["USA", "CHN", "IND", "RUS", "JPN", "DEU", "GBR", "FRA", "BRA", "CAN"]

TEST_SECTORS = ["power", "transportation", "buildings", "manufacturing", "agriculture"]

TEST_YEARS = [2020, 2021, 2022]

# Carbon calculation test cases
CARBON_TEST_CASES = {
    "electricity": [
        {"electricity_value": 100, "electricity_unit": "kwh", "country": "us"},
        {"electricity_value": 1000, "electricity_unit": "kwh", "country": "de"},
        {"electricity_value": 1, "electricity_unit": "mwh", "country": "fr"}
    ],
    "vehicle": [
        {"distance_value": 100, "distance_unit": "km", "vehicle_model_id": "7268a9b7-17e8-4c8d-acca-57059252afe9"},
        {"distance_value": 50, "distance_unit": "mi", "vehicle_model_id": "7268a9b7-17e8-4c8d-acca-57059252afe9"}
    ],
    "flight": [
        {
            "passengers": 1,
            "legs": [{"departure_airport": "lax", "destination_airport": "jfk"}]
        },
        {
            "passengers": 2,
            "legs": [
                {"departure_airport": "jfk", "destination_airport": "lhr"},
                {"departure_airport": "lhr", "destination_airport": "jfk"}
            ]
        }
    ]
}

# Performance test scenarios
PERFORMANCE_SCENARIOS = [
    {
        "name": "Basic Load Test",
        "description": "Test basic API responsiveness under normal load",
        "concurrent_requests": 5,
        "duration": 30,
        "request_interval": 1.0
    },
    {
        "name": "Stress Test",
        "description": "Test API behavior under high load",
        "concurrent_requests": 20,
        "duration": 60,
        "request_interval": 0.1
    },
    {
        "name": "Endurance Test",
        "description": "Test API stability over extended period",
        "concurrent_requests": 3,
        "duration": 300,
        "request_interval": 2.0
    }
]

# Validation rules for API responses
VALIDATION_RULES = {
    "climate_trace": {
        "sectors": {
            "type": "dict",
            "required_keys": ["power", "transportation", "buildings"],
            "min_items": 5
        },
        "countries": {
            "type": "list",
            "min_items": 100,
            "item_pattern": r"^[A-Z]{3}$"
        },
        "emissions": {
            "type": "list",
            "required_fields": ["AssetCount", "Emissions", "Gas"],
            "numeric_fields": ["AssetCount", "Emissions"]
        }
    },
    "carbon_interface": {
        "estimate": {
            "type": "dict",
            "required_path": "data.attributes",
            "required_fields": ["carbon_kg", "carbon_lb", "carbon_mt"],
            "numeric_fields": ["carbon_kg", "carbon_lb", "carbon_mt"]
        }
    },
    "openweather": {
        "weather": {
            "type": "dict",
            "required_fields": ["main", "weather", "coord", "name"],
            "numeric_fields": ["main.temp", "main.humidity", "main.pressure"]
        },
        "air_quality": {
            "type": "dict",
            "required_path": "list.0",
            "required_fields": ["main.aqi", "components"],
            "numeric_fields": ["main.aqi"]
        }
    },
    "nasa_power": {
        "daily_data": {
            "type": "dict",
            "required_path": "properties.parameter",
            "min_data_points": 1
        }
    },
    "world_bank": {
        "indicator": {
            "type": "list",
            "min_items": 2,
            "data_path": "1",
            "required_fields": ["indicator", "country", "date", "value"]
        }
    },
    "un_sdg": {
        "goals": {
            "type": "list",
            "min_items": 17,
            "required_fields": ["code", "title"]
        }
    }
}

# Error handling configurations
ERROR_HANDLING = {
    "retry_on_status_codes": [429, 500, 502, 503, 504],
    "retry_delay": 2.0,
    "max_retries": 3,
    "timeout_handling": "mock",  # "fail", "mock", "skip"
    "rate_limit_handling": "wait",  # "fail", "wait", "skip"
    "connection_error_handling": "mock"  # "fail", "mock", "skip"
}

# Default test configuration
DEFAULT_CONFIG = TestConfiguration(
    test_mode=TestMode.HYBRID,
    test_level=TestLevel.STANDARD,
    verbose=True,
    save_reports=True,
    parallel_execution=False
)

def get_test_config(config_file: Optional[str] = None) -> TestConfiguration:
    """Load test configuration from file or return default"""
    if config_file and os.path.exists(config_file):
        try:
            import json
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Convert dict to TestConfiguration
            # This is a simplified version - in practice you'd want more robust deserialization
            return TestConfiguration(**config_data)
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
            print("Using default configuration")
    
    return DEFAULT_CONFIG

def save_test_config(config: TestConfiguration, config_file: str):
    """Save test configuration to file"""
    try:
        import json
        from dataclasses import asdict
        
        config_dict = asdict(config)
        
        # Convert enums to strings
        def convert_enums(obj):
            if isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums(item) for item in obj]
            elif hasattr(obj, 'value'):  # Enum
                return obj.value
            else:
                return obj
        
        config_dict = convert_enums(config_dict)
        
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        print(f"Configuration saved to {config_file}")
        
    except Exception as e:
        print(f"Error saving configuration: {e}")

def create_sample_config():
    """Create a sample configuration file"""
    config = TestConfiguration(
        test_mode=TestMode.HYBRID,
        test_level=TestLevel.COMPREHENSIVE,
        verbose=True,
        save_reports=True,
        parallel_execution=True,
        max_workers=4
    )
    
    save_test_config(config, "./tests/sample_config.json")
    print("Sample configuration created at ./tests/sample_config.json")

if __name__ == "__main__":
    create_sample_config()