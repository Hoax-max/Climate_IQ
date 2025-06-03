#!/usr/bin/env python3
"""
Climate Data Extraction Script for RAG System
Extracts real data from World Bank, UN SDG, Climate TRACE, and NASA APIs
"""
import requests
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd

class ClimateDataExtractor:
    """Extract climate data from various APIs for RAG system"""
    
    def __init__(self):
        self.data_dir = "data/climate_knowledge"
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.extracted_data = []
        
    def extract_world_bank_data(self):
        """Extract climate indicators from World Bank"""
        print("🏛️ Extracting World Bank climate data...")
        
        indicators = {
            "EN.ATM.CO2E.KT": "CO2 emissions (kt)",
            "EG.USE.ELEC.KH.PC": "Electric power consumption (kWh per capita)",
            "AG.LND.FRST.ZS": "Forest area (% of land area)",
            "EN.ATM.METH.KT.CE": "Methane emissions (kt of CO2 equivalent)",
            "EN.ATM.NOXE.KT.CE": "Nitrous oxide emissions (kt of CO2 equivalent)",
            "EG.ELC.RNEW.ZS": "Renewable electricity output (% of total)",
            "SP.POP.TOTL": "Population, total"
        }
        
        countries = ["USA", "CHN", "IND", "DEU", "JPN", "GBR", "FRA", "BRA", "CAN", "AUS"]
        
        for indicator_code, indicator_name in indicators.items():
            for country in countries:
                try:
                    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator_code}"
                    params = {
                        'format': 'json',
                        'date': '2015:2023',
                        'per_page': 100
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if len(data) > 1 and data[1]:
                            latest_data = [item for item in data[1] if item['value'] is not None]
                            if latest_data:
                                latest = latest_data[0]
                                
                                document = {
                                    "title": f"{indicator_name} - {latest['country']['value']}",
                                    "content": f"In {latest['date']}, {latest['country']['value']} had {indicator_name.lower()} of {latest['value']:,.2f}. This indicator measures {self._get_indicator_description(indicator_code)}. The data comes from the World Bank's official climate and development indicators database.",
                                    "source": "World Bank Open Data",
                                    "category": "climate_indicators",
                                    "country": country,
                                    "year": latest['date'],
                                    "indicator": indicator_code,
                                    "value": latest['value']
                                }
                                
                                self.extracted_data.append(document)
                                print(f"  ✅ {country} - {indicator_name}")
                    
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    print(f"  ❌ Error extracting {country} {indicator_code}: {e}")
    
    def extract_climate_trace_data(self):
        """Extract emissions data from Climate TRACE"""
        print("🌍 Extracting Climate TRACE emissions data...")
        
        countries = ["USA", "CHN", "IND", "RUS", "JPN", "DEU", "IRN", "SAU", "KOR", "CAN"]
        sectors = ["power", "transportation", "buildings", "manufacturing", "agriculture"]
        
        for country in countries:
            try:
                # Get country total emissions
                url = "https://api.climatetrace.org/v6/country/emissions"
                params = {
                    'countries': country,
                    'since': 2022,
                    'to': 2022
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    if data and len(data) > 0:
                        country_data = data[0]
                        emissions = country_data['emissions']
                        
                        document = {
                            "title": f"Total Greenhouse Gas Emissions - {country}",
                            "content": f"In 2022, {country} emitted {emissions['co2e_100yr']/1e9:.2f} billion tons of CO2 equivalent greenhouse gases. This includes {emissions['co2']/1e9:.2f} billion tons of CO2, {emissions['ch4']/1e6:.1f} million tons of methane, and {emissions['n2o']/1e3:.1f} thousand tons of nitrous oxide. {country} ranks #{country_data['rank']} globally in total emissions. The country's emissions represent {(emissions['co2e_100yr']/country_data['worldEmissions']['co2e_100yr']*100):.1f}% of global greenhouse gas emissions.",
                            "source": "Climate TRACE",
                            "category": "emissions_data",
                            "country": country,
                            "year": 2022,
                            "total_emissions_gt": emissions['co2e_100yr']/1e9,
                            "global_rank": country_data['rank']
                        }
                        
                        self.extracted_data.append(document)
                        print(f"  ✅ {country} total emissions")
                
                time.sleep(0.2)  # Rate limiting
                
            except Exception as e:
                print(f"  ❌ Error extracting {country}: {e}")
    
    def extract_un_sdg_data(self):
        """Extract UN SDG climate-related data"""
        print("🇺🇳 Extracting UN SDG climate data...")
        
        try:
            # Get SDG 13 (Climate Action) targets
            response = requests.get("https://unstats.un.org/SDGAPI/v1/sdg/Goal/13/Target/List", timeout=10)
            if response.status_code == 200:
                targets = response.json()
                
                for target in targets:
                    document = {
                        "title": f"SDG 13 Target: {target['title']}",
                        "content": f"UN Sustainable Development Goal 13 (Climate Action) includes the target: {target['title']}. {target.get('description', 'This target focuses on urgent action to combat climate change and its impacts.')} This is part of the global framework for sustainable development and climate action adopted by all UN Member States.",
                        "source": "UN SDG Database",
                        "category": "sdg_targets",
                        "sdg_goal": 13,
                        "target_code": target['code']
                    }
                    
                    self.extracted_data.append(document)
                    print(f"  ✅ SDG 13 Target: {target['code']}")
            
            # Get SDG 7 (Clean Energy) targets
            response = requests.get("https://unstats.un.org/SDGAPI/v1/sdg/Goal/7/Target/List", timeout=10)
            if response.status_code == 200:
                targets = response.json()
                
                for target in targets:
                    document = {
                        "title": f"SDG 7 Target: {target['title']}",
                        "content": f"UN Sustainable Development Goal 7 (Affordable and Clean Energy) includes the target: {target['title']}. {target.get('description', 'This target focuses on ensuring access to affordable, reliable, sustainable and modern energy for all.')} Achieving this target is crucial for climate action and sustainable development.",
                        "source": "UN SDG Database",
                        "category": "sdg_targets",
                        "sdg_goal": 7,
                        "target_code": target['code']
                    }
                    
                    self.extracted_data.append(document)
                    print(f"  ✅ SDG 7 Target: {target['code']}")
                    
        except Exception as e:
            print(f"  ❌ Error extracting UN SDG data: {e}")
    
    def extract_nasa_climate_data(self):
        """Extract climate data from NASA"""
        print("🛰️ Extracting NASA climate data...")
        
        # Major cities for renewable energy potential
        cities = [
            {"name": "New York", "lat": 40.7, "lon": -74.0},
            {"name": "Los Angeles", "lat": 34.1, "lon": -118.2},
            {"name": "London", "lat": 51.5, "lon": -0.1},
            {"name": "Tokyo", "lat": 35.7, "lon": 139.7},
            {"name": "Sydney", "lat": -33.9, "lon": 151.2}
        ]
        
        for city in cities:
            try:
                # Get recent 30 days of data
                end_date = datetime.now().strftime('%Y%m%d')
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
                
                url = "https://power.larc.nasa.gov/api/temporal/daily/point"
                params = {
                    'parameters': 'ALLSKY_SFC_SW_DWN,WS10M,T2M',
                    'community': 'RE',
                    'longitude': city['lon'],
                    'latitude': city['lat'],
                    'start': start_date,
                    'end': end_date,
                    'format': 'JSON'
                }
                
                response = requests.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    
                    solar_data = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
                    wind_data = data['properties']['parameter']['WS10M']
                    temp_data = data['properties']['parameter']['T2M']
                    
                    # Calculate averages
                    avg_solar = sum(solar_data.values()) / len(solar_data)
                    avg_wind = sum(wind_data.values()) / len(wind_data)
                    avg_temp = sum(temp_data.values()) / len(temp_data)
                    
                    # Determine potential
                    solar_potential = "High" if avg_solar > 5 else "Medium" if avg_solar > 3 else "Low"
                    wind_potential = "High" if avg_wind > 6 else "Medium" if avg_wind > 3 else "Low"
                    
                    document = {
                        "title": f"Renewable Energy Potential - {city['name']}",
                        "content": f"Based on NASA satellite data, {city['name']} has {solar_potential.lower()} solar energy potential with an average solar irradiance of {avg_solar:.2f} kWh/m²/day and {wind_potential.lower()} wind energy potential with average wind speeds of {avg_wind:.2f} m/s. The average temperature is {avg_temp:.1f}°C. {'Solar panels would be highly effective' if solar_potential == 'High' else 'Solar panels would be moderately effective' if solar_potential == 'Medium' else 'Solar panels would have limited effectiveness'} in this location. {'Wind turbines would be highly viable' if wind_potential == 'High' else 'Small wind systems might be viable' if wind_potential == 'Medium' else 'Wind energy would be challenging'} for renewable energy generation.",
                        "source": "NASA POWER",
                        "category": "renewable_potential",
                        "city": city['name'],
                        "solar_potential": solar_potential,
                        "wind_potential": wind_potential,
                        "avg_solar_irradiance": avg_solar,
                        "avg_wind_speed": avg_wind
                    }
                    
                    self.extracted_data.append(document)
                    print(f"  ✅ {city['name']} renewable potential")
                
                time.sleep(0.5)  # Rate limiting for NASA API
                
            except Exception as e:
                print(f"  ❌ Error extracting {city['name']}: {e}")
    
    def extract_climate_science_facts(self):
        """Add climate science facts and best practices"""
        print("🔬 Adding climate science facts...")
        
        climate_facts = [
            {
                "title": "Global Temperature Rise",
                "content": "Global average temperatures have risen by approximately 1.1°C (2°F) since the late 19th century. The last decade (2014-2023) includes the 10 warmest years on record. This warming is primarily driven by increased carbon dioxide and other greenhouse gas emissions from human activities. The Intergovernmental Panel on Climate Change (IPCC) projects that global temperatures could rise by 1.5°C as early as 2030-2035 if current trends continue.",
                "source": "IPCC Climate Reports",
                "category": "climate_science"
            },
            {
                "title": "Carbon Dioxide Levels",
                "content": "Atmospheric CO2 concentrations have reached 421 parts per million (ppm) in 2024, the highest level in over 3 million years. Pre-industrial CO2 levels were around 280 ppm. The current rate of increase is about 2.4 ppm per year. To limit warming to 1.5°C, global emissions need to be cut by 45% by 2030 and reach net-zero by 2050.",
                "source": "NOAA Global Monitoring Laboratory",
                "category": "climate_science"
            },
            {
                "title": "Renewable Energy Growth",
                "content": "Renewable energy capacity has grown exponentially, with solar and wind now the cheapest sources of electricity in most regions. In 2023, renewables accounted for 30% of global electricity generation. Solar photovoltaic costs have fallen by 85% since 2010, while wind costs have fallen by 70%. The International Energy Agency projects that renewables could provide 90% of the emissions reductions needed in the power sector.",
                "source": "International Energy Agency",
                "category": "renewable_energy"
            },
            {
                "title": "Transportation Emissions",
                "content": "Transportation accounts for 16% of global greenhouse gas emissions and 24% in developed countries. Road transport represents 75% of transport emissions. Electric vehicle sales are growing rapidly, reaching 14% of global car sales in 2023. A typical electric vehicle produces 60-70% fewer emissions than a gasoline car over its lifetime, even accounting for battery production and electricity generation.",
                "source": "International Transport Forum",
                "category": "transportation"
            },
            {
                "title": "Building Energy Efficiency",
                "content": "Buildings account for 40% of global energy consumption and 36% of CO2 emissions. Simple efficiency measures like LED lighting, insulation, and smart thermostats can reduce building energy use by 20-30%. Heat pumps are 3-4 times more efficient than traditional heating systems. Green building standards like LEED and BREEAM can reduce energy consumption by 25-30% compared to conventional buildings.",
                "source": "Global Alliance for Buildings and Construction",
                "category": "energy_efficiency"
            }
        ]
        
        for fact in climate_facts:
            self.extracted_data.append(fact)
            print(f"  ✅ {fact['title']}")
    
    def _get_indicator_description(self, indicator_code: str) -> str:
        """Get description for World Bank indicators"""
        descriptions = {
            "EN.ATM.CO2E.KT": "the total amount of carbon dioxide emissions from fossil fuel combustion and cement production",
            "EG.USE.ELEC.KH.PC": "the average electricity consumption per person, indicating energy access and usage patterns",
            "AG.LND.FRST.ZS": "the percentage of land covered by forests, important for carbon sequestration",
            "EN.ATM.METH.KT.CE": "methane emissions from agriculture, waste, and energy sectors",
            "EN.ATM.NOXE.KT.CE": "nitrous oxide emissions primarily from agriculture and fossil fuel combustion",
            "EG.ELC.RNEW.ZS": "the share of electricity generated from renewable sources like solar, wind, and hydro",
            "SP.POP.TOTL": "the total population, relevant for per-capita emissions calculations"
        }
        return descriptions.get(indicator_code, "climate and development indicators")
    
    def save_extracted_data(self):
        """Save extracted data to JSON file"""
        output_file = os.path.join(self.data_dir, "extracted_climate_data.json")
        
        with open(output_file, 'w') as f:
            json.dump(self.extracted_data, f, indent=2)
        
        print(f"\n💾 Saved {len(self.extracted_data)} documents to {output_file}")
        
        # Create summary
        categories = {}
        for doc in self.extracted_data:
            category = doc['category']
            categories[category] = categories.get(category, 0) + 1
        
        print("\n📊 Data Summary:")
        for category, count in categories.items():
            print(f"  {category}: {count} documents")
    
    def run_extraction(self):
        """Run complete data extraction"""
        print("🌍 Climate Guardian - Data Extraction for RAG System")
        print("=" * 60)
        
        start_time = time.time()
        
        # Extract from all sources
        self.extract_world_bank_data()
        self.extract_climate_trace_data()
        self.extract_un_sdg_data()
        self.extract_nasa_climate_data()
        self.extract_climate_science_facts()
        
        # Save results
        self.save_extracted_data()
        
        end_time = time.time()
        print(f"\n⏱️ Extraction completed in {end_time - start_time:.1f} seconds")
        print(f"🎉 Ready for RAG system integration!")

def main():
    """Main function"""
    extractor = ClimateDataExtractor()
    extractor.run_extraction()

if __name__ == "__main__":
    main()