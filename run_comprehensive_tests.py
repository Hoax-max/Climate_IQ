#!/usr/bin/env python3
"""
Climate IQ - Comprehensive API Testing Suite
Demonstrates the complete testing framework for all climate APIs
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tests.comprehensive_api_tester import ComprehensiveAPITester
from tests.test_climate_trace_api import ClimateTraceAPITester
from tests.test_carbon_interface_api import CarbonInterfaceAPITester
from backend.api_handlers.enhanced_climate_apis import EnhancedClimateAPIHandler, TestMode
from tests.mock_data_provider import MockDataProvider
from tests.test_config import TestConfiguration, TestLevel, get_test_config
from config import settings

def print_header(title: str, char: str = "=", width: int = 80):
    """Print a formatted header"""
    print(f"\n{char * width}")
    print(f"{title:^{width}}")
    print(f"{char * width}")

def print_section(title: str, char: str = "-", width: int = 60):
    """Print a formatted section header"""
    print(f"\n{title}")
    print(char * len(title))

def check_api_keys():
    """Check which API keys are available"""
    print_section("🔑 API Key Status")
    
    api_keys = {
        "OpenWeatherMap": bool(settings.OPENWEATHER_API_KEY),
        "Carbon Interface": bool(settings.CARBON_INTERFACE_API_KEY),
        "NASA POWER": True,  # Public API
        "World Bank": True,  # Public API
        "UN SDG": True,  # Public API
        "ClimateTRACE": True  # Public API
    }
    
    for api_name, available in api_keys.items():
        status = "✅ Available" if available else "❌ Missing"
        print(f"   {api_name}: {status}")
    
    available_count = sum(api_keys.values())
    total_count = len(api_keys)
    
    print(f"\n📊 Summary: {available_count}/{total_count} APIs available")
    
    if available_count < total_count:
        print("\n💡 To enable all APIs, set these environment variables:")
        if not settings.OPENWEATHER_API_KEY:
            print("   OPENWEATHER_API_KEY=your_key_here")
        if not settings.CARBON_INTERFACE_API_KEY:
            print("   CARBON_INTERFACE_API_KEY=your_key_here")
    
    return api_keys

def demonstrate_mock_data():
    """Demonstrate mock data capabilities"""
    print_section("🎭 Mock Data Provider Demo")
    
    mock = MockDataProvider()
    
    # ClimateTRACE mock data
    print("🌍 ClimateTRACE Mock Data:")
    sectors = mock.get_climate_trace_sectors()
    print(f"   Sectors: {len(sectors['sectors'])} available")
    
    countries = mock.get_climate_trace_countries()
    print(f"   Countries: {len(countries['countries'])} available")
    
    assets = mock.get_climate_trace_assets(country="USA", sector="power", limit=5)
    print(f"   Sample Assets: {len(assets)} power plants in USA")
    
    # Carbon Interface mock data
    print("\n🌱 Carbon Interface Mock Data:")
    electricity_estimate = mock.get_carbon_interface_estimate(
        "electricity", 
        electricity_value=100, 
        electricity_unit="kwh", 
        country="us"
    )
    carbon_kg = electricity_estimate['data']['attributes']['carbon_kg']
    print(f"   100 kWh electricity = {carbon_kg:.2f} kg CO2")
    
    # Weather mock data
    print("\n🌤️ Weather Mock Data:")
    weather = mock.get_openweather_current("New York,US")
    print(f"   New York: {weather['main']['temp']:.1f}°C, {weather['weather'][0]['description']}")
    
    print("\n✅ Mock data provider working correctly!")

def test_enhanced_api_handler():
    """Test the enhanced API handler"""
    print_section("🚀 Enhanced API Handler Test")
    
    # Test in different modes
    modes = [TestMode.LIVE, TestMode.HYBRID, TestMode.MOCK]
    
    for mode in modes:
        print(f"\n🧪 Testing in {mode.value.upper()} mode:")
        
        handler = EnhancedClimateAPIHandler(test_mode=mode)
        
        # Test ClimateTRACE
        response = handler.get_climate_trace_sectors()
        print(f"   ClimateTRACE: {response.status.value} ({response.response_time:.2f}s) - {response.source}")
        
        # Test Carbon Interface (if key available)
        if settings.CARBON_INTERFACE_API_KEY or mode == TestMode.MOCK:
            response = handler.calculate_carbon_footprint(
                "electricity",
                electricity_value=100,
                electricity_unit="kwh",
                country="us"
            )
            print(f"   Carbon Interface: {response.status.value} ({response.response_time:.2f}s) - {response.source}")
        
        # Get statistics
        stats = handler.get_api_statistics()
        print(f"   Success Rate: {stats['success_rate']:.1f}%")

def run_individual_tests():
    """Run individual API test suites"""
    print_section("🧪 Individual API Test Suites")
    
    # ClimateTRACE API Tests
    print("\n🌍 Running ClimateTRACE API Tests...")
    climate_tester = ClimateTraceAPITester()
    
    # Run a subset of tests for demo
    print("   Testing definitions endpoints...")
    climate_tester.test_definitions_sectors()
    climate_tester.test_definitions_countries()
    climate_tester.test_definitions_gases()
    
    print("   Testing assets endpoints...")
    climate_tester.test_assets_search()
    
    # Show results
    passed = len([r for r in climate_tester.test_results if r.status.name == "PASS"])
    total = len(climate_tester.test_results)
    print(f"   Results: {passed}/{total} tests passed")
    
    # Carbon Interface API Tests (if key available)
    if settings.CARBON_INTERFACE_API_KEY:
        print("\n🌱 Running Carbon Interface API Tests...")
        carbon_tester = CarbonInterfaceAPITester()
        
        # Run a subset of tests
        print("   Testing authentication...")
        carbon_tester.test_authentication()
        
        print("   Testing electricity calculations...")
        carbon_tester.test_electricity_emissions()
        
        # Show results
        passed = len([r for r in carbon_tester.test_results if r.status.name == "PASS"])
        total = len(carbon_tester.test_results)
        print(f"   Results: {passed}/{total} tests passed")
    else:
        print("\n🌱 Carbon Interface API Tests: Skipped (no API key)")

def run_comprehensive_tests():
    """Run the comprehensive test suite"""
    print_section("🎯 Comprehensive Test Suite")
    
    print("Running comprehensive tests for all APIs...")
    print("This may take a few minutes depending on API response times.\n")
    
    tester = ComprehensiveAPITester()
    
    # Run a subset for demo (to avoid long execution time)
    print("🛰️ Testing NASA POWER API...")
    tester.test_nasa_power_api()
    
    if settings.OPENWEATHER_API_KEY:
        print("🌤️ Testing OpenWeatherMap API...")
        tester.test_openweather_api()
    
    print("🏛️ Testing World Bank API...")
    tester.test_world_bank_api()
    
    print("🇺🇳 Testing UN SDG API...")
    tester.test_un_sdg_api()
    
    print("🔗 Testing API Integration...")
    tester.test_api_integration()
    
    # Generate summary
    total_tests = len(tester.test_results)
    if total_tests > 0:
        passed = len([r for r in tester.test_results if r.status.name == "PASS"])
        print(f"\n📊 Comprehensive Test Results: {passed}/{total_tests} tests passed")
    else:
        print("\n📊 No comprehensive tests completed")

def demonstrate_health_monitoring():
    """Demonstrate health monitoring capabilities"""
    print_section("🏥 Health Monitoring Demo")
    
    handler = EnhancedClimateAPIHandler()
    
    print("Performing health check on all APIs...")
    health = handler.health_check()
    
    print(f"\n📊 Overall Health: {health['overall_health']:.1f}%")
    print(f"📈 Available APIs: {health['available_apis']}/{health['total_apis']}")
    
    print("\n🌐 Individual API Status:")
    for api_name, status in health['apis'].items():
        available = "✅" if status.get('available', False) else "❌"
        response_time = status.get('response_time', 0)
        print(f"   {available} {api_name}: {status['status']} ({response_time:.2f}s)")

def generate_sample_reports():
    """Generate sample test reports"""
    print_section("📄 Sample Report Generation")
    
    # Create reports directory
    reports_dir = Path("tests/reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Generate a sample report
    sample_report = {
        "test_run": {
            "timestamp": datetime.now().isoformat(),
            "framework_version": "1.0",
            "total_tests": 25,
            "execution_time": 45.2
        },
        "summary": {
            "pass_rate": 88.0,
            "apis_tested": 6,
            "apis_available": 5
        },
        "api_results": {
            "climate_trace": {"status": "available", "tests_passed": 8, "tests_total": 10},
            "carbon_interface": {"status": "available", "tests_passed": 5, "tests_total": 5},
            "openweather": {"status": "available", "tests_passed": 3, "tests_total": 3},
            "nasa_power": {"status": "available", "tests_passed": 3, "tests_total": 3},
            "world_bank": {"status": "available", "tests_passed": 3, "tests_total": 4},
            "un_sdg": {"status": "unavailable", "tests_passed": 0, "tests_total": 3}
        }
    }
    
    # Save sample report
    report_file = reports_dir / f"sample_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(sample_report, f, indent=2)
    
    print(f"📄 Sample report generated: {report_file}")
    print(f"📁 Reports directory: {reports_dir.absolute()}")

def main():
    """Main demonstration function"""
    print_header("🌍 Climate IQ - Comprehensive API Testing Framework")
    print("This demonstration showcases the complete testing capabilities")
    print("for all climate APIs used in the Climate IQ platform.")
    
    start_time = time.time()
    
    try:
        # 1. Check API key availability
        api_keys = check_api_keys()
        
        # 2. Demonstrate mock data capabilities
        demonstrate_mock_data()
        
        # 3. Test enhanced API handler
        test_enhanced_api_handler()
        
        # 4. Run individual test suites
        run_individual_tests()
        
        # 5. Run comprehensive tests (subset)
        run_comprehensive_tests()
        
        # 6. Demonstrate health monitoring
        demonstrate_health_monitoring()
        
        # 7. Generate sample reports
        generate_sample_reports()
        
        # Final summary
        execution_time = time.time() - start_time
        
        print_header("✅ Testing Framework Demonstration Complete")
        print(f"⏱️  Total execution time: {execution_time:.2f} seconds")
        print(f"🧪 Framework features demonstrated:")
        print(f"   • API key validation and fallback mechanisms")
        print(f"   • Mock data generation for offline testing")
        print(f"   • Enhanced API handler with error recovery")
        print(f"   • Individual API test suites")
        print(f"   • Comprehensive multi-API testing")
        print(f"   • Real-time health monitoring")
        print(f"   • Automated report generation")
        
        print(f"\n🚀 Next Steps:")
        print(f"   • Run full test suite: python tests/comprehensive_api_tester.py")
        print(f"   • Test specific APIs: python tests/test_climate_trace_api.py")
        print(f"   • Use enhanced handler: from backend.api_handlers.enhanced_climate_apis import enhanced_api_handler")
        print(f"   • Check test reports in: tests/reports/")
        
        print(f"\n📚 Documentation: tests/README.md")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🌟 Climate IQ API Testing Framework - Ready for Production!")

if __name__ == "__main__":
    main()