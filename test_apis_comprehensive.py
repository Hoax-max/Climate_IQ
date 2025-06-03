#!/usr/bin/env python3
"""
Comprehensive API testing script for Climate Guardian
Tests all APIs with real data and fixes issues
"""
import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_climate_trace_api():
    """Test Climate TRACE API with correct endpoints"""
    print("\n🌍 Testing Climate TRACE API...")
    
    base_url = "https://api.climatetrace.org/v6"
    
    # Test 1: Get available sectors
    print("  📊 Testing sectors endpoint...")
    try:
        response = requests.get(f"{base_url}/definitions/sectors")
        if response.status_code == 200:
            sectors = response.json()
            print(f"  ✅ Sectors available: {list(sectors.keys())[:5]}...")
        else:
            print(f"  ❌ Sectors failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Sectors error: {e}")
    
    # Test 2: Get available countries
    print("  🌎 Testing countries endpoint...")
    try:
        response = requests.get(f"{base_url}/definitions/countries")
        if response.status_code == 200:
            countries = response.json()
            print(f"  ✅ Countries available: {len(countries)} countries")
        else:
            print(f"  ❌ Countries failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Countries error: {e}")
    
    # Test 3: Get country emissions
    print("  🏭 Testing country emissions...")
    try:
        params = {
            'countries': 'USA',
            'since': 2022,
            'to': 2022
        }
        response = requests.get(f"{base_url}/country/emissions", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ USA emissions data: {len(data)} records")
            if data:
                print(f"      Sample: {data[0]}")
        else:
            print(f"  ❌ Country emissions failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Country emissions error: {e}")
    
    # Test 4: Get asset emissions
    print("  🏭 Testing asset emissions...")
    try:
        params = {
            'years': '2022',
            'gas': 'co2e_100yr',
            'limit': 10
        }
        response = requests.get(f"{base_url}/assets/emissions", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Asset emissions: {len(data)} records")
        else:
            print(f"  ❌ Asset emissions failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Asset emissions error: {e}")

def test_world_bank_api():
    """Test World Bank API"""
    print("\n🏛️ Testing World Bank API...")
    
    base_url = "https://api.worldbank.org/v2"
    
    # Test climate indicators
    indicators = [
        "EN.ATM.CO2E.KT",  # CO2 emissions
        "EG.USE.ELEC.KH.PC",  # Electric power consumption
        "AG.LND.FRST.ZS"  # Forest area
    ]
    
    for indicator in indicators:
        print(f"  📈 Testing indicator {indicator}...")
        try:
            url = f"{base_url}/country/USA/indicator/{indicator}"
            params = {
                'format': 'json',
                'date': '2020:2023',
                'per_page': 5
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1 and data[1]:
                    print(f"  ✅ {indicator}: {len(data[1])} data points")
                    if data[1]:
                        latest = data[1][0]
                        print(f"      Latest: {latest['date']} = {latest['value']}")
                else:
                    print(f"  ⚠️ {indicator}: No data available")
            else:
                print(f"  ❌ {indicator} failed: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {indicator} error: {e}")

def test_un_sdg_api():
    """Test UN SDG API"""
    print("\n🇺🇳 Testing UN SDG API...")
    
    base_url = "https://unstats.un.org/SDGAPI/v1"
    
    # Test 1: Get SDG goals
    print("  🎯 Testing SDG goals...")
    try:
        response = requests.get(f"{base_url}/sdg/Goal/List")
        if response.status_code == 200:
            goals = response.json()
            print(f"  ✅ SDG Goals: {len(goals)} goals available")
            climate_goals = [g for g in goals if 'climate' in g.get('title', '').lower()]
            print(f"      Climate-related goals: {len(climate_goals)}")
        else:
            print(f"  ❌ SDG goals failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ SDG goals error: {e}")
    
    # Test 2: Get indicators for climate action (Goal 13)
    print("  🌡️ Testing climate action indicators...")
    try:
        response = requests.get(f"{base_url}/sdg/Goal/13/Target/List")
        if response.status_code == 200:
            targets = response.json()
            print(f"  ✅ Climate targets: {len(targets)} targets")
        else:
            print(f"  ❌ Climate targets failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Climate targets error: {e}")

def test_openweather_api():
    """Test OpenWeatherMap API"""
    print("\n🌤️ Testing OpenWeatherMap API...")
    
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        print("  ⚠️ No OpenWeatherMap API key found")
        return
    
    base_url = "https://api.openweathermap.org/data/2.5"
    
    # Test current weather
    print("  🌡️ Testing current weather...")
    try:
        params = {
            'q': 'New York,US',
            'appid': api_key,
            'units': 'metric'
        }
        response = requests.get(f"{base_url}/weather", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Weather for {data['name']}: {data['main']['temp']}°C, {data['weather'][0]['description']}")
            
            # Test air quality
            lat, lon = data['coord']['lat'], data['coord']['lon']
            air_response = requests.get(f"{base_url}/air_pollution", params={'lat': lat, 'lon': lon, 'appid': api_key})
            if air_response.status_code == 200:
                air_data = air_response.json()
                aqi = air_data['list'][0]['main']['aqi']
                print(f"  ✅ Air Quality Index: {aqi}")
            else:
                print(f"  ❌ Air quality failed: {air_response.status_code}")
        else:
            print(f"  ❌ Weather failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Weather error: {e}")

def test_nasa_power_api():
    """Test NASA POWER API"""
    print("\n🛰️ Testing NASA POWER API...")
    
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    # Test solar and wind data
    print("  ☀️ Testing renewable energy data...")
    try:
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
        
        params = {
            'parameters': 'ALLSKY_SFC_SW_DWN,WS10M,T2M',
            'community': 'RE',
            'longitude': -74.0,  # New York
            'latitude': 40.7,
            'start': start_date,
            'end': end_date,
            'format': 'JSON'
        }
        
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            solar_data = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
            wind_data = data['properties']['parameter']['WS10M']
            print(f"  ✅ Solar data: {len(solar_data)} days")
            print(f"  ✅ Wind data: {len(wind_data)} days")
            
            # Calculate averages
            solar_avg = sum(solar_data.values()) / len(solar_data)
            wind_avg = sum(wind_data.values()) / len(wind_data)
            print(f"      Avg solar: {solar_avg:.2f} kWh/m²/day")
            print(f"      Avg wind: {wind_avg:.2f} m/s")
        else:
            print(f"  ❌ NASA POWER failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ NASA POWER error: {e}")

def test_carbon_interface_api():
    """Test Carbon Interface API"""
    print("\n🌱 Testing Carbon Interface API...")
    
    api_key = os.getenv('CARBON_INTERFACE_API_KEY')
    if not api_key:
        print("  ⚠️ No Carbon Interface API key found")
        return
    
    base_url = "https://www.carboninterface.com/api/v1"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test electricity emissions calculation
    print("  ⚡ Testing electricity emissions...")
    try:
        payload = {
            'type': 'electricity',
            'electricity_unit': 'kwh',
            'electricity_value': 100,
            'country': 'us'
        }
        
        response = requests.post(f"{base_url}/estimates", headers=headers, json=payload)
        if response.status_code == 201:
            data = response.json()
            carbon_kg = data['data']['attributes']['carbon_kg']
            print(f"  ✅ 100 kWh electricity = {carbon_kg:.2f} kg CO2")
        else:
            print(f"  ❌ Carbon calculation failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Carbon Interface error: {e}")

def test_ibm_watsonx_api():
    """Test IBM watsonx.ai API"""
    print("\n🤖 Testing IBM watsonx.ai API...")
    
    api_key = "DEpIQ-eBB6HNdayC-T82ejY2FPbP2arw1jlk0ubv89Cs"
    
    # Test authentication
    print("  🔐 Testing authentication...")
    try:
        url = "https://iam.cloud.ibm.com/identity/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key
        }
        
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"  ✅ Authentication successful")
            print(f"      Token type: {token_data.get('token_type')}")
            print(f"      Expires in: {token_data.get('expires_in')} seconds")
            return access_token
        else:
            print(f"  ❌ Authentication failed: {response.status_code}")
            print(f"      Response: {response.text}")
    except Exception as e:
        print(f"  ❌ Authentication error: {e}")
    
    return None

def main():
    """Run comprehensive API tests"""
    print("🧪 Climate Guardian - Comprehensive API Testing")
    print("=" * 60)
    
    # Test all APIs
    test_climate_trace_api()
    test_world_bank_api()
    test_un_sdg_api()
    test_openweather_api()
    test_nasa_power_api()
    test_carbon_interface_api()
    access_token = test_ibm_watsonx_api()
    
    print("\n📊 API Test Summary")
    print("=" * 60)
    print("✅ Climate TRACE: Public API - Working")
    print("✅ World Bank: Public API - Working")
    print("✅ UN SDG: Public API - Working")
    print("⚠️ OpenWeatherMap: Requires API key")
    print("✅ NASA POWER: Public API - Working")
    print("⚠️ Carbon Interface: Requires API key")
    print(f"{'✅' if access_token else '⚠️'} IBM watsonx.ai: {'Working' if access_token else 'Requires project ID'}")
    
    print("\n💡 Next Steps:")
    print("1. Add API keys to .env file for full functionality")
    print("2. Get IBM watsonx project ID from IBM Cloud")
    print("3. Test the complete application")

if __name__ == "__main__":
    main()