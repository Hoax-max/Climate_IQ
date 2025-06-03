#!/usr/bin/env python3
"""
Mock Data Provider for Climate APIs
Provides realistic mock data for testing when APIs are unavailable
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import uuid

class MockDataProvider:
    """Provides mock data for climate APIs"""
    
    def __init__(self):
        self.countries = [
            {"code": "USA", "name": "United States"},
            {"code": "CHN", "name": "China"},
            {"code": "IND", "name": "India"},
            {"code": "RUS", "name": "Russia"},
            {"code": "JPN", "name": "Japan"},
            {"code": "DEU", "name": "Germany"},
            {"code": "GBR", "name": "United Kingdom"},
            {"code": "FRA", "name": "France"},
            {"code": "BRA", "name": "Brazil"},
            {"code": "CAN", "name": "Canada"}
        ]
        
        self.sectors = {
            "power": 1,
            "transportation": 2,
            "buildings": 3,
            "fossil-fuel-operations": 4,
            "manufacturing": 5,
            "mineral-extraction": 6,
            "agriculture": 7,
            "waste": 8,
            "fluorinated-gases": 9,
            "forestry-and-land-use": 10
        }
        
        self.subsectors = [
            "electricity-generation",
            "steel",
            "cement",
            "aluminum",
            "pulp-and-paper",
            "chemicals",
            "domestic-shipping-ship",
            "international-shipping-ship",
            "domestic-shipping-port",
            "international-shipping-port",
            "domestic-aviation",
            "international-aviation",
            "road-transportation-urban-area",
            "road-transportation-road-segment",
            "oil-and-gas-production-and-transport-field",
            "oil-and-gas-production-and-transport",
            "oil-and-gas-refining",
            "petrochemicals",
            "coal-mining",
            "bauxite-mining",
            "iron-mining",
            "copper-mining",
            "forest-land-clearing",
            "forest-land-degradation",
            "forest-land-fires",
            "shrubgrass-fires",
            "wetland-fires",
            "removals",
            "net-forest-land",
            "net-wetland",
            "net-shrubgrass",
            "cropland-fires",
            "rice-cultivation",
            "enteric-fermentation",
            "manure-management",
            "synthetic-fertilizer-application",
            "solid-waste-disposal"
        ]
        
        self.gases = ["n2o", "co2e", "co2", "ch4", "co2e_20yr", "co2e_100yr"]
        
        self.continents = [
            "Asia",
            "South America", 
            "North America",
            "Oceania",
            "Antarctica",
            "Africa",
            "Europe"
        ]

    # ==================== CLIMATE TRACE MOCK DATA ====================
    
    def get_climate_trace_sectors(self) -> Dict[str, Any]:
        """Mock ClimateTRACE sectors response"""
        return {
            "sectors": self.sectors,
            "source": "mock_data"
        }
    
    def get_climate_trace_countries(self) -> Dict[str, Any]:
        """Mock ClimateTRACE countries response"""
        return {
            "countries": [country["code"] for country in self.countries],
            "source": "mock_data"
        }
    
    def get_climate_trace_subsectors(self) -> List[str]:
        """Mock ClimateTRACE subsectors response"""
        return self.subsectors
    
    def get_climate_trace_continents(self) -> List[str]:
        """Mock ClimateTRACE continents response"""
        return self.continents
    
    def get_climate_trace_gases(self) -> List[str]:
        """Mock ClimateTRACE gases response"""
        return self.gases
    
    def get_climate_trace_groups(self) -> Dict[str, Any]:
        """Mock ClimateTRACE groups response"""
        return {
            "G20": ["USA", "CHN", "IND", "RUS", "JPN", "DEU", "GBR", "FRA", "BRA", "CAN"],
            "EU": ["DEU", "FRA", "ITA", "ESP", "POL", "ROU", "NLD", "BEL", "GRC", "PRT"],
            "OECD": ["USA", "JPN", "DEU", "GBR", "FRA", "CAN", "AUS", "KOR", "ESP", "MEX"],
            "source": "mock_data"
        }
    
    def get_climate_trace_assets(self, country: str = None, sector: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Mock ClimateTRACE assets response"""
        assets = []
        
        for i in range(min(limit, 50)):  # Generate up to 50 mock assets
            asset_id = random.randint(1000000, 9999999)
            
            # Generate realistic coordinates based on country
            if country == "USA":
                lat = random.uniform(25.0, 49.0)
                lon = random.uniform(-125.0, -66.0)
            elif country == "CHN":
                lat = random.uniform(18.0, 54.0)
                lon = random.uniform(73.0, 135.0)
            else:
                lat = random.uniform(-60.0, 75.0)
                lon = random.uniform(-180.0, 180.0)
            
            asset = {
                "type": "Feature",
                "id": asset_id,
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "asset_id": asset_id,
                    "asset_name": f"Mock Asset {asset_id}",
                    "country": country or random.choice([c["code"] for c in self.countries]),
                    "sector": sector or random.choice(list(self.sectors.keys())),
                    "subsector": random.choice(self.subsectors),
                    "capacity": random.uniform(10, 1000),
                    "capacity_units": "MW" if sector == "power" else "units"
                },
                "emissions": [
                    {
                        "gas": gas,
                        "quantity": random.uniform(1000, 100000),
                        "factor": random.uniform(0.1, 2.0),
                        "capacity": random.uniform(10, 1000),
                        "activity": random.uniform(100, 10000),
                        "activityUnits": "MWh" if sector == "power" else "units",
                        "emissionsFactor": "mock_factor",
                        "remainder": random.uniform(0, 100)
                    }
                    for gas in self.gases
                ]
            }
            assets.append(asset)
        
        return assets
    
    def get_climate_trace_asset_emissions(self, years: List[str] = None, gas: str = "co2e_100yr", 
                                        countries: List[str] = None, sectors: List[str] = None) -> List[Dict[str, Any]]:
        """Mock ClimateTRACE asset emissions response"""
        emissions = []
        
        countries_list = countries or [c["code"] for c in self.countries[:5]]
        sectors_list = sectors or list(self.sectors.keys())[:3]
        
        for country in countries_list:
            for sector in sectors_list:
                emission_data = {
                    "AssetCount": random.randint(10, 500),
                    "Emissions": random.uniform(1000000, 50000000),  # MT CO2e
                    "Gas": gas,
                    "Country": {
                        "Code": country,
                        "Name": next((c["name"] for c in self.countries if c["code"] == country), country)
                    }
                }
                emissions.append(emission_data)
        
        return emissions
    
    def get_climate_trace_country_emissions(self, countries: List[str] = None, since: int = 2022, 
                                          to: int = 2022, sectors: List[str] = None) -> List[Dict[str, Any]]:
        """Mock ClimateTRACE country emissions response"""
        emissions = []
        
        countries_list = countries or [c["code"] for c in self.countries[:5]]
        
        for country in countries_list:
            for year in range(since, to + 1):
                country_data = {
                    "Country": {
                        "Code": country,
                        "Name": next((c["name"] for c in self.countries if c["code"] == country), country)
                    },
                    "Continent": random.choice(self.continents),
                    "Rank": random.randint(1, 200),
                    "PreviousRank": random.randint(1, 200),
                    "Emissions": [
                        {
                            "gas": gas,
                            "value": random.uniform(100000, 10000000)
                        }
                        for gas in self.gases
                    ],
                    "WorldEmissions": [
                        {
                            "gas": gas,
                            "value": random.uniform(1000000, 100000000)
                        }
                        for gas in self.gases
                    ],
                    "Year": year
                }
                emissions.append(country_data)
        
        return emissions
    
    def get_climate_trace_admin_search(self, name: str = None, level: int = None, 
                                     point: List[float] = None, bbox: List[float] = None) -> List[Dict[str, Any]]:
        """Mock ClimateTRACE admin search response"""
        admins = []
        
        # Generate mock administrative areas
        admin_names = [
            "California", "Texas", "New York", "Florida", "Illinois",
            "Ontario", "Quebec", "British Columbia", "Alberta", "Manitoba",
            "Bavaria", "North Rhine-Westphalia", "Baden-Württemberg", "Lower Saxony", "Hesse"
        ]
        
        for i, admin_name in enumerate(admin_names[:10]):
            if name and name.lower() not in admin_name.lower():
                continue
                
            admin = {
                "id": f"ADMIN_{i+1}",
                "description": f"{admin_name} Administrative Area",
                "link": f"/admins/ADMIN_{i+1}/geojson",
                "name": admin_name,
                "level": level or random.randint(0, 2),
                "country": random.choice([c["code"] for c in self.countries]),
                "area_km2": random.uniform(1000, 500000)
            }
            admins.append(admin)
        
        return admins
    
    def get_climate_trace_admin_geojson(self, admin_id: str) -> Dict[str, Any]:
        """Mock ClimateTRACE admin GeoJSON response"""
        # Generate a simple polygon around a random point
        center_lat = random.uniform(25.0, 49.0)
        center_lon = random.uniform(-125.0, -66.0)
        
        # Create a simple square polygon
        offset = 0.5
        coordinates = [[
            [center_lon - offset, center_lat - offset],
            [center_lon + offset, center_lat - offset],
            [center_lon + offset, center_lat + offset],
            [center_lon - offset, center_lat + offset],
            [center_lon - offset, center_lat - offset]
        ]]
        
        return {
            "type": "Feature",
            "id": admin_id,
            "geometry": {
                "type": "Polygon",
                "coordinates": coordinates
            },
            "properties": {
                "admin_id": admin_id,
                "name": f"Mock Admin {admin_id}",
                "level": random.randint(0, 2),
                "area_km2": random.uniform(1000, 100000),
                "population": random.randint(100000, 10000000)
            }
        }

    # ==================== CARBON INTERFACE MOCK DATA ====================
    
    def get_carbon_interface_estimate(self, estimate_type: str, **kwargs) -> Dict[str, Any]:
        """Mock Carbon Interface estimate response"""
        estimate_id = str(uuid.uuid4())
        
        # Calculate mock carbon emissions based on type
        if estimate_type == "electricity":
            kwh = kwargs.get("electricity_value", 100)
            country = kwargs.get("country", "us")
            
            # Mock emission factors (kg CO2 per kWh)
            emission_factors = {
                "us": 0.4,
                "de": 0.3,
                "fr": 0.05,
                "cn": 0.6,
                "in": 0.7
            }
            
            factor = emission_factors.get(country, 0.4)
            carbon_kg = kwh * factor
            
        elif estimate_type == "vehicle":
            distance = kwargs.get("distance_value", 100)
            unit = kwargs.get("distance_unit", "km")
            
            # Convert to km if needed
            if unit == "mi":
                distance = distance * 1.60934
            
            # Mock emission factor: 0.2 kg CO2 per km
            carbon_kg = distance * 0.2
            
        elif estimate_type == "flight":
            legs = kwargs.get("legs", [])
            passengers = kwargs.get("passengers", 1)
            
            # Mock calculation: 0.5 kg CO2 per passenger per leg
            carbon_kg = len(legs) * passengers * 500  # Assume 500 kg per leg
            
        elif estimate_type == "shipping":
            weight = kwargs.get("weight_value", 10)
            distance = kwargs.get("distance_value", 100)
            transport_method = kwargs.get("transport_method", "truck")
            
            # Mock emission factors by transport method
            factors = {
                "truck": 0.1,
                "ship": 0.02,
                "plane": 0.5,
                "train": 0.05
            }
            
            factor = factors.get(transport_method, 0.1)
            carbon_kg = weight * distance * factor
            
        else:
            carbon_kg = random.uniform(10, 1000)
        
        return {
            "data": {
                "id": estimate_id,
                "type": "estimate",
                "attributes": {
                    "country": kwargs.get("country", "us"),
                    "state": None,
                    "electricity_unit": kwargs.get("electricity_unit"),
                    "electricity_value": kwargs.get("electricity_value"),
                    "estimated_at": datetime.now().isoformat(),
                    "carbon_g": carbon_kg * 1000,
                    "carbon_lb": carbon_kg * 2.20462,
                    "carbon_kg": carbon_kg,
                    "carbon_mt": carbon_kg / 1000
                }
            }
        }

    # ==================== WEATHER API MOCK DATA ====================
    
    def get_openweather_current(self, location: str) -> Dict[str, Any]:
        """Mock OpenWeatherMap current weather response"""
        # Parse location
        if "," in location:
            city, country = location.split(",")
            city = city.strip()
            country = country.strip()
        else:
            city = location
            country = "US"
        
        # Generate realistic weather data
        base_temp = random.uniform(-10, 35)  # Celsius
        
        return {
            "coord": {
                "lon": random.uniform(-180, 180),
                "lat": random.uniform(-90, 90)
            },
            "weather": [
                {
                    "id": random.randint(200, 800),
                    "main": random.choice(["Clear", "Clouds", "Rain", "Snow", "Thunderstorm"]),
                    "description": random.choice(["clear sky", "few clouds", "light rain", "heavy snow"]),
                    "icon": "01d"
                }
            ],
            "base": "stations",
            "main": {
                "temp": base_temp,
                "feels_like": base_temp + random.uniform(-5, 5),
                "temp_min": base_temp - random.uniform(0, 10),
                "temp_max": base_temp + random.uniform(0, 10),
                "pressure": random.randint(980, 1030),
                "humidity": random.randint(30, 90)
            },
            "visibility": random.randint(1000, 10000),
            "wind": {
                "speed": random.uniform(0, 20),
                "deg": random.randint(0, 360)
            },
            "clouds": {
                "all": random.randint(0, 100)
            },
            "dt": int(datetime.now().timestamp()),
            "sys": {
                "type": 1,
                "id": random.randint(1000, 9999),
                "country": country.upper(),
                "sunrise": int((datetime.now() - timedelta(hours=2)).timestamp()),
                "sunset": int((datetime.now() + timedelta(hours=8)).timestamp())
            },
            "timezone": random.randint(-43200, 43200),
            "id": random.randint(1000000, 9999999),
            "name": city,
            "cod": 200
        }
    
    def get_openweather_air_quality(self, lat: float, lon: float) -> Dict[str, Any]:
        """Mock OpenWeatherMap air quality response"""
        return {
            "coord": {
                "lon": lon,
                "lat": lat
            },
            "list": [
                {
                    "main": {
                        "aqi": random.randint(1, 5)
                    },
                    "components": {
                        "co": random.uniform(200, 400),
                        "no": random.uniform(0, 50),
                        "no2": random.uniform(10, 100),
                        "o3": random.uniform(50, 150),
                        "so2": random.uniform(5, 50),
                        "pm2_5": random.uniform(5, 50),
                        "pm10": random.uniform(10, 100),
                        "nh3": random.uniform(0, 20)
                    },
                    "dt": int(datetime.now().timestamp())
                }
            ]
        }

    # ==================== NASA POWER MOCK DATA ====================
    
    def get_nasa_power_data(self, parameters: List[str], lat: float, lon: float, 
                           start_date: str, end_date: str) -> Dict[str, Any]:
        """Mock NASA POWER API response"""
        # Parse date range
        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        
        # Generate daily data
        parameter_data = {}
        
        current_date = start
        while current_date <= end:
            date_str = current_date.strftime("%Y%m%d")
            
            for param in parameters:
                if param not in parameter_data:
                    parameter_data[param] = {}
                
                # Generate realistic values based on parameter
                if param == "ALLSKY_SFC_SW_DWN":  # Solar irradiance
                    value = random.uniform(2.0, 8.0)  # kWh/m²/day
                elif param == "WS10M":  # Wind speed
                    value = random.uniform(1.0, 15.0)  # m/s
                elif param == "T2M":  # Temperature
                    value = random.uniform(-20.0, 40.0)  # Celsius
                else:
                    value = random.uniform(0, 100)
                
                parameter_data[param][date_str] = value
            
            current_date += timedelta(days=1)
        
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat, 0]
            },
            "properties": {
                "parameter": parameter_data
            },
            "header": {
                "title": "NASA/POWER CERES/MERRA2 Native Resolution Daily Data",
                "api_version": "v2.5.0",
                "start_date": start_date,
                "end_date": end_date
            }
        }

    # ==================== WORLD BANK MOCK DATA ====================
    
    def get_world_bank_indicator(self, country: str, indicator: str, start_year: int = 2020, 
                                end_year: int = 2023) -> List[Any]:
        """Mock World Bank API response"""
        # Metadata
        metadata = {
            "page": 1,
            "pages": 1,
            "per_page": 50,
            "total": end_year - start_year + 1,
            "sourceid": "2",
            "lastupdated": "2024-01-01"
        }
        
        # Data points
        data_points = []
        
        for year in range(start_year, end_year + 1):
            # Generate realistic values based on indicator
            if "CO2" in indicator:
                value = random.uniform(1000000, 10000000)  # CO2 emissions in kt
            elif "ELEC" in indicator:
                value = random.uniform(1000, 15000)  # Electricity consumption per capita
            elif "FRST" in indicator:
                value = random.uniform(10, 80)  # Forest area percentage
            else:
                value = random.uniform(0, 1000)
            
            data_point = {
                "indicator": {
                    "id": indicator,
                    "value": f"Mock Indicator {indicator}"
                },
                "country": {
                    "id": country,
                    "value": next((c["name"] for c in self.countries if c["code"] == country), country)
                },
                "countryiso3code": country,
                "date": str(year),
                "value": value,
                "unit": "",
                "obs_status": "",
                "decimal": 2
            }
            data_points.append(data_point)
        
        return [metadata, data_points]
    
    def get_world_bank_countries(self) -> List[Any]:
        """Mock World Bank countries response"""
        metadata = {
            "page": 1,
            "pages": 1,
            "per_page": 50,
            "total": len(self.countries)
        }
        
        countries_data = []
        for country in self.countries:
            country_data = {
                "id": country["code"],
                "iso2Code": country["code"][:2],
                "name": country["name"],
                "region": {
                    "id": random.choice(["EAS", "ECS", "LCN", "MEA", "NAC", "SAS", "SSF"]),
                    "iso2code": random.choice(["Z4", "Z7", "ZJ", "ZQ", "XU", "8S", "ZF"]),
                    "value": random.choice(["East Asia & Pacific", "Europe & Central Asia", "Latin America & Caribbean"])
                },
                "adminregion": {
                    "id": "",
                    "iso2code": "",
                    "value": ""
                },
                "incomeLevel": {
                    "id": random.choice(["HIC", "UMC", "LMC", "LIC"]),
                    "iso2code": random.choice(["XD", "XT", "XN", "XM"]),
                    "value": random.choice(["High income", "Upper middle income", "Lower middle income", "Low income"])
                },
                "lendingType": {
                    "id": random.choice(["LNX", "IBD", "IDB", "IDX"]),
                    "iso2code": random.choice(["XX", "XF", "XH", "XG"]),
                    "value": random.choice(["Not classified", "IBRD", "IDA", "Blend"])
                },
                "capitalCity": f"Capital of {country['name']}",
                "longitude": str(random.uniform(-180, 180)),
                "latitude": str(random.uniform(-90, 90))
            }
            countries_data.append(country_data)
        
        return [metadata, countries_data]

    # ==================== UN SDG MOCK DATA ====================
    
    def get_un_sdg_goals(self) -> List[Dict[str, Any]]:
        """Mock UN SDG goals response"""
        goals = [
            {"code": "1", "title": "No Poverty", "description": "End poverty in all its forms everywhere"},
            {"code": "2", "title": "Zero Hunger", "description": "End hunger, achieve food security and improved nutrition"},
            {"code": "3", "title": "Good Health and Well-being", "description": "Ensure healthy lives and promote well-being"},
            {"code": "4", "title": "Quality Education", "description": "Ensure inclusive and equitable quality education"},
            {"code": "5", "title": "Gender Equality", "description": "Achieve gender equality and empower all women and girls"},
            {"code": "6", "title": "Clean Water and Sanitation", "description": "Ensure availability and sustainable management of water"},
            {"code": "7", "title": "Affordable and Clean Energy", "description": "Ensure access to affordable, reliable, sustainable energy"},
            {"code": "8", "title": "Decent Work and Economic Growth", "description": "Promote sustained, inclusive economic growth"},
            {"code": "9", "title": "Industry, Innovation and Infrastructure", "description": "Build resilient infrastructure, promote innovation"},
            {"code": "10", "title": "Reduced Inequalities", "description": "Reduce inequality within and among countries"},
            {"code": "11", "title": "Sustainable Cities and Communities", "description": "Make cities and human settlements inclusive, safe"},
            {"code": "12", "title": "Responsible Consumption and Production", "description": "Ensure sustainable consumption and production patterns"},
            {"code": "13", "title": "Climate Action", "description": "Take urgent action to combat climate change"},
            {"code": "14", "title": "Life Below Water", "description": "Conserve and sustainably use the oceans, seas"},
            {"code": "15", "title": "Life on Land", "description": "Protect, restore and promote sustainable use of terrestrial ecosystems"},
            {"code": "16", "title": "Peace, Justice and Strong Institutions", "description": "Promote peaceful and inclusive societies"},
            {"code": "17", "title": "Partnerships for the Goals", "description": "Strengthen the means of implementation"}
        ]
        
        return goals
    
    def get_un_sdg_targets(self, goal_id: str) -> List[Dict[str, Any]]:
        """Mock UN SDG targets response"""
        # Generate mock targets for the goal
        targets = []
        
        for i in range(1, random.randint(3, 8)):
            target = {
                "goal": goal_id,
                "code": f"{goal_id}.{i}",
                "title": f"Target {goal_id}.{i}",
                "description": f"Mock target description for goal {goal_id}, target {i}",
                "uri": f"/sdg/Goal/{goal_id}/Target/{goal_id}.{i}"
            }
            targets.append(target)
        
        return targets

    # ==================== UTILITY METHODS ====================
    
    def get_random_coordinates(self, country: str = None) -> Tuple[float, float]:
        """Get random coordinates, optionally within a country"""
        if country == "USA":
            lat = random.uniform(25.0, 49.0)
            lon = random.uniform(-125.0, -66.0)
        elif country == "CHN":
            lat = random.uniform(18.0, 54.0)
            lon = random.uniform(73.0, 135.0)
        elif country == "DEU":
            lat = random.uniform(47.0, 55.0)
            lon = random.uniform(6.0, 15.0)
        else:
            lat = random.uniform(-60.0, 75.0)
            lon = random.uniform(-180.0, 180.0)
        
        return lat, lon
    
    def get_realistic_emission_value(self, country: str, sector: str, gas: str = "co2e_100yr") -> float:
        """Generate realistic emission values based on country and sector"""
        # Base emission factors (MT CO2e)
        base_emissions = {
            "USA": {"power": 1500, "transportation": 1800, "buildings": 500, "manufacturing": 400},
            "CHN": {"power": 4000, "transportation": 800, "buildings": 300, "manufacturing": 1200},
            "IND": {"power": 900, "transportation": 300, "buildings": 150, "manufacturing": 600},
            "DEU": {"power": 250, "transportation": 150, "buildings": 100, "manufacturing": 200},
            "JPN": {"power": 350, "transportation": 200, "buildings": 80, "manufacturing": 300}
        }
        
        country_data = base_emissions.get(country, base_emissions["USA"])
        base_value = country_data.get(sector, 100)
        
        # Add some randomness
        variation = random.uniform(0.8, 1.2)
        
        return base_value * variation * 1000000  # Convert to kg


# Global instance for easy access
mock_data = MockDataProvider()


def main():
    """Test the mock data provider"""
    print("🧪 Testing Mock Data Provider")
    print("=" * 50)
    
    # Test ClimateTRACE mock data
    print("\n🌍 ClimateTRACE Mock Data:")
    print(f"Sectors: {len(mock_data.get_climate_trace_sectors()['sectors'])}")
    print(f"Countries: {len(mock_data.get_climate_trace_countries()['countries'])}")
    print(f"Assets: {len(mock_data.get_climate_trace_assets(limit=5))}")
    
    # Test Carbon Interface mock data
    print("\n🌱 Carbon Interface Mock Data:")
    electricity_estimate = mock_data.get_carbon_interface_estimate("electricity", electricity_value=100, country="us")
    print(f"Electricity estimate: {electricity_estimate['data']['attributes']['carbon_kg']:.2f} kg CO2")
    
    # Test Weather mock data
    print("\n🌤️ Weather Mock Data:")
    weather = mock_data.get_openweather_current("New York,US")
    print(f"Weather: {weather['main']['temp']:.1f}°C, {weather['weather'][0]['description']}")
    
    # Test NASA POWER mock data
    print("\n🛰️ NASA POWER Mock Data:")
    nasa_data = mock_data.get_nasa_power_data(["ALLSKY_SFC_SW_DWN"], 40.7, -74.0, "20240101", "20240103")
    print(f"Solar data points: {len(nasa_data['properties']['parameter']['ALLSKY_SFC_SW_DWN'])}")
    
    print("\n✅ Mock Data Provider Test Complete!")


if __name__ == "__main__":
    main()