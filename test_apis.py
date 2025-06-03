#!/usr/bin/env python3
"""
Test script to verify API connectivity and functionality
"""
import requests
import json
from config import settings

def test_carbon_interface_api():
    """Test Carbon Interface API"""
    print("🧪 Testing Carbon Interface API...")
    try:
        url = f"{settings.CARBON_INTERFACE_API_BASE}/estimates"
        headers = {
            'Authorization': f'Bearer {settings.CARBON_INTERFACE_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Test with a simple electricity calculation
        payload = {
            'type': 'electricity',
            'electricity_unit': 'kwh',
            'electricity_value': 100,
            'country': 'us'
        }
        
        response = requests.post(url, headers=headers, json=payload)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Working - Carbon footprint: {data['data']['attributes']['carbon_kg']} kg CO2")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_nasa_power_api():
    """Test NASA POWER API"""
    print("🧪 Testing NASA POWER API...")
    try:
        url = f"{settings.NASA_API_BASE}/daily/point"
        params = {
            'parameters': 'ALLSKY_SFC_SW_DWN,T2M',
            'community': 'RE',
            'longitude': -74.0,
            'latitude': 40.7,
            'start': '20240101',
            'end': '20240102',
            'format': 'JSON',
            'api_key': settings.NASA_API_KEY
        }
        
        response = requests.get(url, params=params)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Working - Retrieved solar data for coordinates")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_openweather_api():
    """Test OpenWeatherMap API"""
    print("🧪 Testing OpenWeatherMap API...")
    try:
        url = f"{settings.OPENWEATHER_API_BASE}/weather"
        
        # Try different city formats
        city_formats = [
            'New York,US',
            'New York',
            'London,UK',
            'London'
        ]
        
        for city in city_formats:
            params = {
                'q': city,
                'appid': settings.OPENWEATHER_API_KEY,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            print(f"   Trying '{city}' - Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Working - Weather for {data['name']}: {data['main']['temp']}°C")
                return True
            elif response.status_code != 404:
                print(f"   ⚠️  Non-404 error: {response.text}")
        
        print(f"   ❌ All city formats failed")
        return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_climate_trace_api():
    """Test Climate TRACE API"""
    print("🧪 Testing Climate TRACE API...")
    try:
        # Try different endpoints
        endpoints = [
            f"{settings.CLIMATETRACE_API_BASE}/emissions",
            f"{settings.CLIMATETRACE_API_BASE}/data/emissions",
            f"{settings.CLIMATETRACE_API_BASE}/v5/emissions",
            "https://api.climatetrace.org/v5/emissions",
            "https://api.climatetrace.org/emissions"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=10)
                print(f"   Endpoint: {endpoint}")
                print(f"   Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ Working endpoint found!")
                    return True
                elif response.status_code == 404:
                    print(f"   ❌ 404 Not Found")
                else:
                    print(f"   ⚠️  Status: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Exception for {endpoint}: {e}")
        
        print("   ❌ No working endpoints found")
        return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_un_sdg_api():
    """Test UN SDG API"""
    print("🧪 Testing UN SDG API...")
    try:
        url = f"{settings.UN_SDG_API_BASE}/sdg/Goal/List"
        
        response = requests.get(url)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Working - Retrieved {len(data)} SDG goals")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_world_bank_api():
    """Test World Bank API"""
    print("🧪 Testing World Bank API...")
    try:
        # Try different indicators and date ranges
        test_queries = [
            {
                'url': f"{settings.WORLD_BANK_API_BASE}/country/US/indicator/EN.ATM.CO2E.PC",
                'params': {'format': 'json', 'date': '2018:2022', 'per_page': 5},
                'desc': 'CO2 emissions per capita'
            },
            {
                'url': f"{settings.WORLD_BANK_API_BASE}/country/US/indicator/EG.USE.ELEC.KH.PC",
                'params': {'format': 'json', 'date': '2018:2022', 'per_page': 5},
                'desc': 'Electric power consumption'
            },
            {
                'url': f"{settings.WORLD_BANK_API_BASE}/countries",
                'params': {'format': 'json', 'per_page': 5},
                'desc': 'Countries list'
            }
        ]
        
        for query in test_queries:
            response = requests.get(query['url'], params=query['params'])
            print(f"   Testing {query['desc']} - Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1 and data[1]:
                    print(f"   ✅ Working - Retrieved {query['desc']}")
                    return True
                elif len(data) == 1:
                    print(f"   ✅ Working - Retrieved {query['desc']} (metadata only)")
                    return True
                else:
                    print(f"   ⚠️  No data in response")
            else:
                print(f"   ❌ Error: {response.text[:100]}")
        
        print("   ❌ All queries failed")
        return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_ibm_watson_credentials():
    """Test IBM Watson credentials"""
    print("🧪 Testing IBM Watson credentials...")
    try:
        from backend.watsonx_integration.watsonx_client import WatsonXClient
        
        client = WatsonXClient()
        if not client.use_fallback:
            print("   ✅ Watson credentials valid and model initialized")
            return True
        else:
            print("   ⚠️  Watson in fallback mode - credentials may be invalid")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    """Run all API tests"""
    print("🌍 Climate Action Intelligence Platform - API Connectivity Test")
    print("=" * 70)
    
    tests = [
        ("Carbon Interface", test_carbon_interface_api),
        ("NASA POWER", test_nasa_power_api),
        ("OpenWeatherMap", test_openweather_api),
        ("Climate TRACE", test_climate_trace_api),
        ("UN SDG", test_un_sdg_api),
        ("World Bank", test_world_bank_api),
        ("IBM Watson", test_ibm_watson_credentials)
    ]
    
    working_apis = []
    
    for name, test_func in tests:
        print()
        if test_func():
            working_apis.append(name)
    
    print("\n" + "=" * 70)
    print(f"📊 API Test Results: {len(working_apis)}/{len(tests)} APIs working")
    print("\n✅ Working APIs:")
    for api in working_apis:
        print(f"   • {api}")
    
    if len(working_apis) < len(tests):
        print("\n❌ Non-working APIs:")
        for name, _ in tests:
            if name not in working_apis:
                print(f"   • {name}")
    
    print(f"\n🚀 Platform ready with {len(working_apis)} functional APIs!")

if __name__ == "__main__":
    main()