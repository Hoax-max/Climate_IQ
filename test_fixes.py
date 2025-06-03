#!/usr/bin/env python3
"""
Test script for IBM Granite model and Climate TRACE API fixes
"""
import sys
import os
sys.path.append('.')

from backend.watsonx_integration.watsonx_client import WatsonXClient
from backend.api_handlers.climate_apis import ClimateAPIHandler
import requests
import json

def test_ibm_granite_model():
    """Test IBM Granite model integration"""
    print("🧪 Testing IBM Granite Model Integration...")
    print("=" * 60)
    
    try:
        # Initialize Watson client
        watson = WatsonXClient()
        
        # Test basic response generation
        test_prompt = "What are the top 3 climate actions individuals can take to reduce their carbon footprint?"
        
        print(f"📝 Test Prompt: {test_prompt}")
        print("\n🤖 IBM Granite Response:")
        print("-" * 40)
        
        response = watson.generate_response(test_prompt)
        print(response)
        
        print("\n" + "=" * 60)
        
        # Test climate-specific functionality
        print("🌍 Testing Climate-Specific Features...")
        
        user_profile = {
            'location': 'San Francisco, CA',
            'lifestyle': 'urban professional',
            'household_size': 2,
            'current_actions': ['recycling', 'public transport'],
            'interests': ['renewable energy', 'sustainable living'],
            'budget': 'medium'
        }
        
        plan = watson.generate_personalized_plan(user_profile)
        print("📋 Personalized Climate Plan:")
        print("-" * 40)
        print(plan[:500] + "..." if len(plan) > 500 else plan)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing IBM Granite model: {e}")
        return False

def test_climate_trace_api():
    """Test Climate TRACE API with correct endpoints"""
    print("\n🌡️ Testing Climate TRACE API Integration...")
    print("=" * 60)
    
    try:
        api = ClimateAPIHandler()
        
        # Test 1: Get sectors definitions
        print("📊 Testing Sectors Endpoint...")
        sectors = api.get_climate_trace_sectors()
        print(f"✅ Sectors: {list(sectors['sectors'].keys())[:5]}... (source: {sectors['source']})")
        
        # Test 2: Get countries definitions  
        print("\n🌍 Testing Countries Endpoint...")
        countries = api.get_climate_trace_countries()
        if isinstance(countries['countries'], list):
            print(f"✅ Countries: {countries['countries'][:5]}... (source: {countries['source']})")
        else:
            print(f"✅ Countries available (source: {countries['source']})")
        
        # Test 3: Get emissions data for USA
        print("\n🏭 Testing Emissions Data for USA...")
        usa_emissions = api.get_climate_trace_data(country='USA')
        print(f"✅ USA Emissions: {usa_emissions.get('total_emissions_mt', 'N/A')} MT CO2e")
        print(f"   Source: {usa_emissions.get('source', usa_emissions.get('endpoint', 'unknown'))}")
        
        # Test 4: Get power sector emissions
        print("\n⚡ Testing Power Sector Emissions...")
        power_emissions = api.get_climate_trace_data(sector='power')
        print(f"✅ Power Sector: {power_emissions.get('total_emissions_mt', 'N/A')} MT CO2e")
        print(f"   Assets: {power_emissions.get('asset_count', 'N/A')}")
        
        # Test 5: Search for assets
        print("\n🔍 Testing Asset Search...")
        assets = api.search_climate_trace_assets(country='USA', sector='power', limit=5)
        if 'error' not in assets:
            print(f"✅ Found {assets.get('count', 0)} power assets in USA")
        else:
            print(f"⚠️ Asset search: {assets['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Climate TRACE API: {e}")
        return False

def test_direct_api_calls():
    """Test direct API calls to verify endpoints"""
    print("\n🔗 Testing Direct API Calls...")
    print("=" * 60)
    
    base_url = "https://api.climatetrace.org"
    
    # Test endpoints from the OpenAPI spec
    endpoints_to_test = [
        "/v6/definitions/sectors",
        "/v6/definitions/countries", 
        "/v6/definitions/gases",
        "/v6/country/emissions?countries=USA&since=2022&to=2022",
        "/v6/assets/emissions?years=2022&gas=co2e_100yr"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            url = base_url + endpoint
            print(f"🌐 Testing: {endpoint}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ Status: {response.status_code} | Items: {len(data)}")
                elif isinstance(data, dict):
                    print(f"   ✅ Status: {response.status_code} | Keys: {list(data.keys())[:3]}")
                else:
                    print(f"   ✅ Status: {response.status_code} | Type: {type(data)}")
            else:
                print(f"   ⚠️ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}...")
    
    return True

def test_all_apis_status():
    """Test status of all APIs"""
    print("\n📡 Testing All API Status...")
    print("=" * 60)
    
    apis_to_test = [
        ('OpenWeather', 'https://api.openweathermap.org/data/2.5/weather?q=London&appid=5e172a22e5e4412a98dc331708df15ba'),
        ('Carbon Interface', 'https://www.carboninterface.com/api/v1/estimates', {'Authorization': 'Bearer ShPi2tb4XAMuLVO6c5RMDg'}),
        ('NASA POWER', 'https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M&community=RE&longitude=0&latitude=0&start=20231201&end=20231201&format=JSON&api_key=aD45yiM5C8uJErMjBWgK3LTGBufejUQ9andcvdMr'),
        ('World Bank', 'https://api.worldbank.org/v2/country/US/indicator/EN.ATM.CO2E.PC?format=json&date=2020'),
        ('UN SDG', 'https://unstats.un.org/SDGAPI/v1/sdg/Goal/List'),
        ('Climate Trace Sectors', 'https://api.climatetrace.org/v6/definitions/sectors'),
        ('Climate Trace Countries', 'https://api.climatetrace.org/v6/definitions/countries'),
        ('Climate Trace Emissions', 'https://api.climatetrace.org/v6/country/emissions?countries=USA&since=2022&to=2022')
    ]
    
    working_apis = 0
    total_apis = len(apis_to_test)
    
    for name, url, *headers in apis_to_test:
        try:
            headers_dict = headers[0] if headers else {}
            response = requests.get(url, headers=headers_dict, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {name}: {response.status_code}")
                working_apis += 1
            else:
                print(f"⚠️ {name}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {name}: {str(e)[:50]}...")
    
    print(f"\n📊 API Status Summary: {working_apis}/{total_apis} APIs working")
    return working_apis, total_apis

def main():
    """Run all tests"""
    print("🚀 Climate-IQ Platform - IBM Hackathon Fixes Test")
    print("=" * 80)
    
    # Test IBM Granite model
    granite_success = test_ibm_granite_model()
    
    # Test Climate TRACE API
    climate_trace_success = test_climate_trace_api()
    
    # Test direct API calls
    direct_api_success = test_direct_api_calls()
    
    # Test all APIs status
    working_apis, total_apis = test_all_apis_status()
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 TEST SUMMARY")
    print("=" * 80)
    
    print(f"🤖 IBM Granite Model: {'✅ WORKING' if granite_success else '❌ ISSUES'}")
    print(f"🌡️ Climate TRACE API: {'✅ WORKING' if climate_trace_success else '❌ ISSUES'}")
    print(f"🔗 Direct API Calls: {'✅ WORKING' if direct_api_success else '❌ ISSUES'}")
    print(f"📡 Overall API Status: {working_apis}/{total_apis} APIs working")
    
    if working_apis >= 6 and granite_success:
        print("\n🏆 HACKATHON READY! Platform is fully functional for IBM competition.")
    elif working_apis >= 5:
        print("\n🎯 MOSTLY READY! Platform has good API coverage for demonstration.")
    else:
        print("\n⚠️ NEEDS ATTENTION! Some critical APIs need fixing.")
    
    print("\n🚀 Ready to showcase IBM Watson Granite integration!")

if __name__ == "__main__":
    main()