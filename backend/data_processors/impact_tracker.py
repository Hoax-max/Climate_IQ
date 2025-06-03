"""
Impact tracking and calculation system
"""
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import os

logger = logging.getLogger(__name__)

@dataclass
class ImpactRecord:
    """Data class for impact records"""
    action_type: str
    description: str
    quantity: float
    unit: str
    carbon_saved_kg: float
    energy_saved_kwh: float
    water_saved_liters: float
    waste_reduced_kg: float
    cost_savings: float
    timestamp: str
    location: str
    verified: bool = False

class ImpactTracker:
    """Track and calculate environmental impact of climate actions"""
    
    def __init__(self, data_dir: str = "./data/user_profiles"):
        self.data_dir = data_dir
        self.impact_factors = self._load_impact_factors()
        os.makedirs(data_dir, exist_ok=True)
    
    def _load_impact_factors(self) -> Dict[str, Dict[str, float]]:
        """Load impact calculation factors"""
        return {
            'energy_efficiency': {
                'led_bulb_replacement': {'carbon_kg_per_bulb': 40, 'energy_kwh_per_year': 50},
                'insulation_improvement': {'carbon_kg_per_sqm': 15, 'energy_kwh_per_sqm': 25},
                'smart_thermostat': {'carbon_kg_per_year': 200, 'energy_kwh_per_year': 400},
                'energy_efficient_appliance': {'carbon_kg_per_year': 150, 'energy_kwh_per_year': 300}
            },
            'transportation': {
                'bike_commute_km': {'carbon_kg_per_km': 0.21},  # vs car
                'public_transport_km': {'carbon_kg_per_km': 0.15},  # vs car
                'electric_vehicle': {'carbon_kg_per_km': 0.15},  # vs gasoline car
                'carpooling': {'carbon_kg_per_km': 0.105},  # 50% reduction
                'walking': {'carbon_kg_per_km': 0.21}  # vs car
            },
            'renewable_energy': {
                'solar_panel_kw': {'carbon_kg_per_year': 1200, 'energy_kwh_per_year': 1500},
                'wind_turbine_kw': {'carbon_kg_per_year': 1000, 'energy_kwh_per_year': 2000},
                'green_energy_plan': {'carbon_kg_per_kwh': 0.4}
            },
            'food': {
                'vegetarian_meal': {'carbon_kg_per_meal': 2.5},  # vs meat meal
                'local_food_kg': {'carbon_kg_per_kg': 0.5},  # vs imported
                'food_waste_reduction_kg': {'carbon_kg_per_kg': 2.5},
                'composting_kg': {'carbon_kg_per_kg': 0.5}
            },
            'water': {
                'low_flow_fixture': {'water_liters_per_year': 15000, 'carbon_kg_per_year': 5},
                'rainwater_harvesting': {'water_liters_per_year': 50000, 'carbon_kg_per_year': 15},
                'drought_resistant_landscaping': {'water_liters_per_year': 100000, 'carbon_kg_per_year': 30}
            },
            'waste': {
                'recycling_kg': {'carbon_kg_per_kg': 1.5},
                'reusable_bag': {'carbon_kg_per_year': 5, 'waste_kg_per_year': 10},
                'composting_kg': {'carbon_kg_per_kg': 0.5, 'waste_kg_per_kg': 1},
                'electronic_recycling_kg': {'carbon_kg_per_kg': 2}
            }
        }
    
    def track_action(self, user_id: str, action_data: Dict[str, Any]) -> ImpactRecord:
        """Track a climate action and calculate its impact"""
        try:
            # Calculate environmental impact
            impact = self._calculate_impact(action_data)
            
            # Create impact record
            record = ImpactRecord(
                action_type=action_data['action_type'],
                description=action_data['description'],
                quantity=action_data.get('quantity', 1),
                unit=action_data.get('unit', 'unit'),
                carbon_saved_kg=impact['carbon_kg'],
                energy_saved_kwh=impact['energy_kwh'],
                water_saved_liters=impact['water_liters'],
                waste_reduced_kg=impact['waste_kg'],
                cost_savings=impact['cost_savings'],
                timestamp=datetime.now().isoformat(),
                location=action_data.get('location', ''),
                verified=action_data.get('verified', False)
            )
            
            # Save record
            self._save_impact_record(user_id, record)
            
            logger.info(f"Tracked action for user {user_id}: {record.description}")
            return record
            
        except Exception as e:
            logger.error(f"Error tracking action: {e}")
            raise
    
    def _calculate_impact(self, action_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate environmental impact of an action"""
        action_type = action_data['action_type']
        action_subtype = action_data.get('subtype', '')
        quantity = action_data.get('quantity', 1)
        
        impact = {
            'carbon_kg': 0,
            'energy_kwh': 0,
            'water_liters': 0,
            'waste_kg': 0,
            'cost_savings': 0
        }
        
        # Get impact factors for the action
        if action_type in self.impact_factors:
            factors = self.impact_factors[action_type]
            
            if action_subtype in factors:
                action_factors = factors[action_subtype]
                
                # Calculate impacts based on available factors
                impact['carbon_kg'] = action_factors.get('carbon_kg_per_unit', 0) * quantity
                impact['carbon_kg'] += action_factors.get('carbon_kg_per_year', 0)
                impact['carbon_kg'] += action_factors.get('carbon_kg_per_km', 0) * quantity
                impact['carbon_kg'] += action_factors.get('carbon_kg_per_kg', 0) * quantity
                impact['carbon_kg'] += action_factors.get('carbon_kg_per_meal', 0) * quantity
                impact['carbon_kg'] += action_factors.get('carbon_kg_per_kwh', 0) * quantity
                
                impact['energy_kwh'] = action_factors.get('energy_kwh_per_year', 0)
                impact['energy_kwh'] += action_factors.get('energy_kwh_per_sqm', 0) * quantity
                
                impact['water_liters'] = action_factors.get('water_liters_per_year', 0)
                
                impact['waste_kg'] = action_factors.get('waste_kg_per_year', 0)
                impact['waste_kg'] += action_factors.get('waste_kg_per_kg', 0) * quantity
                
                # Estimate cost savings (simplified calculation)
                impact['cost_savings'] = impact['energy_kwh'] * 0.12  # $0.12 per kWh average
                impact['cost_savings'] += impact['water_liters'] * 0.001  # $0.001 per liter
        
        return impact
    
    def _save_impact_record(self, user_id: str, record: ImpactRecord):
        """Save impact record to file"""
        user_file = os.path.join(self.data_dir, f"{user_id}_impacts.json")
        
        # Load existing records
        records = []
        if os.path.exists(user_file):
            try:
                with open(user_file, 'r') as f:
                    records = json.load(f)
            except Exception as e:
                logger.error(f"Error loading existing records: {e}")
        
        # Add new record
        records.append(asdict(record))
        
        # Save updated records
        try:
            with open(user_file, 'w') as f:
                json.dump(records, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving impact record: {e}")
            raise
    
    def get_user_impact_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get impact summary for a user"""
        try:
            user_file = os.path.join(self.data_dir, f"{user_id}_impacts.json")
            
            if not os.path.exists(user_file):
                return self._empty_summary()
            
            with open(user_file, 'r') as f:
                records = json.load(f)
            
            # Filter records by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_records = [
                record for record in records
                if datetime.fromisoformat(record['timestamp']) >= cutoff_date
            ]
            
            # Calculate totals
            total_carbon = sum(record['carbon_saved_kg'] for record in recent_records)
            total_energy = sum(record['energy_saved_kwh'] for record in recent_records)
            total_water = sum(record['water_saved_liters'] for record in recent_records)
            total_waste = sum(record['waste_reduced_kg'] for record in recent_records)
            total_savings = sum(record['cost_savings'] for record in recent_records)
            
            # Calculate action breakdown
            action_breakdown = {}
            for record in recent_records:
                action_type = record['action_type']
                if action_type not in action_breakdown:
                    action_breakdown[action_type] = {
                        'count': 0,
                        'carbon_kg': 0,
                        'energy_kwh': 0,
                        'water_liters': 0,
                        'waste_kg': 0
                    }
                
                action_breakdown[action_type]['count'] += 1
                action_breakdown[action_type]['carbon_kg'] += record['carbon_saved_kg']
                action_breakdown[action_type]['energy_kwh'] += record['energy_saved_kwh']
                action_breakdown[action_type]['water_liters'] += record['water_saved_liters']
                action_breakdown[action_type]['waste_kg'] += record['waste_reduced_kg']
            
            return {
                'period_days': days,
                'total_actions': len(recent_records),
                'total_carbon_saved_kg': round(total_carbon, 2),
                'total_energy_saved_kwh': round(total_energy, 2),
                'total_water_saved_liters': round(total_water, 2),
                'total_waste_reduced_kg': round(total_waste, 2),
                'total_cost_savings': round(total_savings, 2),
                'action_breakdown': action_breakdown,
                'equivalent_metrics': self._calculate_equivalents(total_carbon),
                'recent_actions': recent_records[-5:] if recent_records else []
            }
            
        except Exception as e:
            logger.error(f"Error getting user impact summary: {e}")
            return self._empty_summary()
    
    def _empty_summary(self) -> Dict[str, Any]:
        """Return empty impact summary"""
        return {
            'period_days': 30,
            'total_actions': 0,
            'total_carbon_saved_kg': 0,
            'total_energy_saved_kwh': 0,
            'total_water_saved_liters': 0,
            'total_waste_reduced_kg': 0,
            'total_cost_savings': 0,
            'action_breakdown': {},
            'equivalent_metrics': {},
            'recent_actions': []
        }
    
    def _calculate_equivalents(self, carbon_kg: float) -> Dict[str, Any]:
        """Calculate equivalent metrics for carbon savings"""
        if carbon_kg <= 0:
            return {}
        
        return {
            'trees_planted_equivalent': round(carbon_kg / 22, 1),  # 22 kg CO2 per tree per year
            'miles_not_driven': round(carbon_kg / 0.404, 1),  # 0.404 kg CO2 per mile
            'coal_not_burned_kg': round(carbon_kg / 2.86, 1),  # 2.86 kg CO2 per kg coal
            'gasoline_not_used_liters': round(carbon_kg / 2.31, 1)  # 2.31 kg CO2 per liter gasoline
        }
    
    def get_leaderboard(self, metric: str = 'carbon_saved_kg', limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard of users by impact metric"""
        try:
            user_summaries = []
            
            # Get all user files
            for filename in os.listdir(self.data_dir):
                if filename.endswith('_impacts.json'):
                    user_id = filename.replace('_impacts.json', '')
                    summary = self.get_user_impact_summary(user_id, days=30)
                    
                    if summary['total_actions'] > 0:
                        user_summaries.append({
                            'user_id': user_id,
                            'total_actions': summary['total_actions'],
                            'carbon_saved_kg': summary['total_carbon_saved_kg'],
                            'energy_saved_kwh': summary['total_energy_saved_kwh'],
                            'water_saved_liters': summary['total_water_saved_liters'],
                            'waste_reduced_kg': summary['total_waste_reduced_kg']
                        })
            
            # Sort by specified metric
            if metric in ['carbon_saved_kg', 'energy_saved_kwh', 'water_saved_liters', 'waste_reduced_kg']:
                user_summaries.sort(key=lambda x: x[metric], reverse=True)
            else:
                user_summaries.sort(key=lambda x: x['total_actions'], reverse=True)
            
            return user_summaries[:limit]
            
        except Exception as e:
            logger.error(f"Error generating leaderboard: {e}")
            return []