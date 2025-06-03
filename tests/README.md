# Climate IQ API Testing Framework

A comprehensive testing framework for all climate-related APIs used in the Climate IQ platform, with special focus on the ClimateTRACE API v6 and Carbon Interface API.

## 🌟 Features

### Comprehensive API Coverage
- **ClimateTRACE API v6**: Complete testing of all endpoints based on OpenAPI specification
- **Carbon Interface API**: Full carbon footprint calculation testing
- **OpenWeatherMap API**: Weather and air quality data testing
- **NASA POWER API**: Renewable energy data testing
- **World Bank API**: Climate indicators testing
- **UN SDG API**: Sustainable development goals testing

### Advanced Testing Capabilities
- **Parameter Validation**: Tests for edge cases and invalid inputs
- **Performance Testing**: Response time monitoring and thresholds
- **Integration Testing**: Cross-API workflow testing
- **Mock Data Fallback**: Realistic mock data when APIs are unavailable
- **Error Handling**: Comprehensive error scenarios and recovery
- **Rate Limiting**: Respectful API usage with built-in delays

### Reporting and Analytics
- **Detailed Reports**: JSON, CSV, and HTML output formats
- **Real-time Monitoring**: Live test execution feedback
- **Statistics Tracking**: API performance and reliability metrics
- **Health Checks**: Automated API availability monitoring

## 🚀 Quick Start

### Basic Usage

```bash
# Run comprehensive tests for all APIs
python tests/comprehensive_api_tester.py

# Test specific APIs
python tests/test_climate_trace_api.py
python tests/test_carbon_interface_api.py

# Test enhanced API handler
python backend/api_handlers/enhanced_climate_apis.py
```

### Configuration

Set up your API keys in `.env` file:

```bash
# Required for full functionality
OPENWEATHER_API_KEY=your_openweather_key
CARBON_INTERFACE_API_KEY=your_carbon_interface_key

# Optional (public APIs work without keys)
NASA_API_KEY=your_nasa_key
```

## 📋 Test Suites

### 1. ClimateTRACE API v6 Tests (`test_climate_trace_api.py`)

Based on the official OpenAPI specification, tests all endpoints:

#### Definitions Endpoints
- `/v6/definitions/sectors` - Available emission sectors
- `/v6/definitions/subsectors` - Detailed subsector classifications
- `/v6/definitions/countries` - Supported country codes
- `/v6/definitions/groups` - Country groupings (G20, EU, etc.)
- `/v6/definitions/continents` - Continental classifications
- `/v6/definitions/gases` - Greenhouse gas types

#### Assets Endpoints
- `/v6/assets` - Search emissions sources
- `/v6/assets/{sourceId}` - Individual source details
- `/v6/assets/emissions` - Aggregated source emissions

#### Country Endpoints
- `/v6/country/emissions` - Country-level emissions data

#### Administrative Areas
- `/v6/admins/search` - Search administrative boundaries
- `/v6/admins/{adminId}/geojson` - GeoJSON boundary data

#### Test Categories
- **Basic Connectivity**: Endpoint availability and response format
- **Parameter Validation**: Input validation and error handling
- **Data Integrity**: Response structure and required fields
- **Performance**: Response time thresholds
- **Edge Cases**: Boundary conditions and error scenarios

### 2. Carbon Interface API Tests (`test_carbon_interface_api.py`)

Comprehensive testing of carbon footprint calculations:

#### Calculation Types
- **Electricity**: Power consumption emissions
- **Vehicle**: Transportation emissions
- **Flight**: Aviation emissions
- **Shipping**: Freight transport emissions

#### Test Categories
- **Authentication**: API key validation
- **Input Validation**: Parameter checking and error responses
- **Calculation Accuracy**: Consistency and scaling tests
- **Performance**: Response time monitoring
- **Edge Cases**: Invalid inputs and error handling

### 3. Comprehensive API Tester (`comprehensive_api_tester.py`)

Unified testing framework for all APIs:

#### Features
- **Multi-API Testing**: Tests all climate APIs in one run
- **Integration Tests**: Cross-API workflow validation
- **Performance Benchmarking**: Comparative API performance
- **Health Monitoring**: Real-time API availability
- **Unified Reporting**: Consolidated test results

### 4. Enhanced API Handler (`enhanced_climate_apis.py`)

Production-ready API client with testing integration:

#### Features
- **Automatic Fallback**: Mock data when APIs fail
- **Error Recovery**: Retry logic and graceful degradation
- **Performance Monitoring**: Built-in statistics tracking
- **Health Checks**: Automated API monitoring
- **Test Mode Support**: Configurable testing modes

## 🔧 Configuration Options

### Test Modes

```python
from tests.test_config import TestMode

# Live API testing only
test_mode = TestMode.LIVE

# Mock data only (for offline testing)
test_mode = TestMode.MOCK

# Hybrid mode (fallback to mock on failure)
test_mode = TestMode.HYBRID
```

### Test Levels

```python
from tests.test_config import TestLevel

# Basic connectivity tests
test_level = TestLevel.BASIC

# Standard functionality tests
test_level = TestLevel.STANDARD

# Comprehensive testing including edge cases
test_level = TestLevel.COMPREHENSIVE

# Performance and load testing
test_level = TestLevel.PERFORMANCE
```

### Custom Configuration

Create a custom test configuration:

```python
from tests.test_config import TestConfiguration, TestMode, TestLevel

config = TestConfiguration(
    test_mode=TestMode.HYBRID,
    test_level=TestLevel.COMPREHENSIVE,
    parallel_execution=True,
    max_workers=4,
    save_reports=True,
    report_format=["json", "csv", "html"]
)
```

## 📊 Test Reports

### Report Formats

1. **JSON Reports**: Detailed machine-readable results
2. **CSV Reports**: Tabular data for analysis
3. **HTML Reports**: Human-readable dashboard (planned)

### Report Location

Reports are saved to `tests/reports/` directory:

```
tests/reports/
├── comprehensive_api_test_results_20240603_132534.json
├── climate_trace_test_results_20240603_132516.json
├── carbon_interface_test_results_20240603_132534.json
└── api_test_summary_20240603_132534.csv
```

### Sample Report Structure

```json
{
  "test_run": {
    "timestamp": "2024-06-03T13:25:32",
    "total_time": 15.42,
    "total_tests": 75,
    "framework_version": "1.0"
  },
  "api_keys_available": {
    "openweather": true,
    "carbon_interface": true,
    "nasa_power": true,
    "world_bank": true,
    "un_sdg": true,
    "climate_trace": true
  },
  "results": [
    {
      "api_name": "ClimateTRACE",
      "endpoint": "/definitions/sectors",
      "test_name": "Sectors Definition",
      "status": "PASS",
      "response_time": 0.15,
      "status_code": 200,
      "error_message": null,
      "data_sample": {...}
    }
  ]
}
```

## 🧪 Mock Data Provider

For offline testing and development, the framework includes a comprehensive mock data provider:

### Features
- **Realistic Data**: Based on real-world climate data patterns
- **Complete Coverage**: Mock responses for all API endpoints
- **Configurable**: Customizable data generation parameters
- **Performance**: Fast response times for development

### Usage

```python
from tests.mock_data_provider import MockDataProvider

mock = MockDataProvider()

# Get mock ClimateTRACE data
sectors = mock.get_climate_trace_sectors()
emissions = mock.get_climate_trace_asset_emissions(
    years=["2022"], 
    countries=["USA"], 
    gas="co2e_100yr"
)

# Get mock Carbon Interface data
estimate = mock.get_carbon_interface_estimate(
    "electricity",
    electricity_value=100,
    electricity_unit="kwh",
    country="us"
)
```

## 🔍 Validation and Quality Assurance

### Response Validation

The framework includes comprehensive validation rules:

```python
VALIDATION_RULES = {
    "climate_trace": {
        "sectors": {
            "type": "dict",
            "required_keys": ["power", "transportation", "buildings"],
            "min_items": 5
        },
        "emissions": {
            "type": "list",
            "required_fields": ["AssetCount", "Emissions", "Gas"],
            "numeric_fields": ["AssetCount", "Emissions"]
        }
    }
}
```

### Error Handling

Robust error handling for common scenarios:

- **Network Timeouts**: Automatic retry with exponential backoff
- **Rate Limiting**: Respectful delays and queue management
- **Invalid Responses**: Graceful degradation to mock data
- **Authentication Errors**: Clear error messages and fallback options

## 📈 Performance Monitoring

### Metrics Tracked

- **Response Times**: Per-endpoint performance monitoring
- **Success Rates**: API reliability tracking
- **Error Rates**: Failure pattern analysis
- **Throughput**: Request volume handling

### Performance Thresholds

Default performance expectations:

```python
PERFORMANCE_THRESHOLDS = {
    "climate_trace": 5.0,      # seconds
    "carbon_interface": 3.0,   # seconds
    "openweather": 2.0,        # seconds
    "nasa_power": 8.0,         # seconds
    "world_bank": 5.0,         # seconds
    "un_sdg": 3.0              # seconds
}
```

## 🔄 Continuous Integration

### GitHub Actions Integration

Example workflow for automated testing:

```yaml
name: API Testing
on: [push, pull_request, schedule]

jobs:
  test-apis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.12
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run API tests
        env:
          OPENWEATHER_API_KEY: ${{ secrets.OPENWEATHER_API_KEY }}
          CARBON_INTERFACE_API_KEY: ${{ secrets.CARBON_INTERFACE_API_KEY }}
        run: python tests/comprehensive_api_tester.py
```

## 🛠️ Development and Extension

### Adding New API Tests

1. Create a new test file following the pattern:

```python
class NewAPITester:
    def __init__(self):
        self.test_results = []
    
    def test_endpoint(self):
        # Test implementation
        pass
    
    def run_all_tests(self):
        # Test runner
        pass
```

2. Add to comprehensive tester:

```python
# In comprehensive_api_tester.py
new_tester = NewAPITester()
new_tester.run_all_tests()

# Convert results to unified format
for result in new_tester.test_results:
    self.test_results.append(APITestResult(...))
```

### Custom Validation Rules

Add custom validation for new APIs:

```python
# In test_config.py
VALIDATION_RULES["new_api"] = {
    "endpoint": {
        "type": "dict",
        "required_fields": ["field1", "field2"],
        "numeric_fields": ["field1"]
    }
}
```

## 📚 API Documentation References

- [ClimateTRACE API v6 Documentation](https://api.climatetrace.org/v6/swagger/index.html)
- [Carbon Interface API Documentation](https://docs.carboninterface.com/)
- [OpenWeatherMap API Documentation](https://openweathermap.org/api)
- [NASA POWER API Documentation](https://power.larc.nasa.gov/docs/)
- [World Bank API Documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392)
- [UN SDG API Documentation](https://unstats.un.org/SDGAPI/swagger/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This testing framework is part of the Climate IQ project and follows the same license terms.

## 🆘 Support

For issues and questions:

1. Check the test reports for detailed error information
2. Review the API documentation for endpoint specifications
3. Use mock mode for offline development and testing
4. Check API key configuration for authentication issues

## 🔮 Future Enhancements

- **Real-time Monitoring Dashboard**: Web-based test result visualization
- **Automated Performance Regression Detection**: Historical performance comparison
- **Load Testing**: Concurrent request testing for scalability
- **API Contract Testing**: Schema validation against OpenAPI specifications
- **Alerting System**: Notifications for API failures and performance degradation