"""
Simplified impact tracker that works without database dependencies
"""
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

logger = logging.getLogger(__name__)

class SimpleImpactTracker:
    """Simplified impact tracker using file storage"""
    
    def __init__(self):
        self.data_dir = "data/user_profiles"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Impact calculation factors
        self.impact_factors = {
            'energy_efficiency': {
                'led_bulb_replacement': {'carbon_per_unit': 0.5, 'energy_per_unit': 10, 'cost_savings_per_unit': 5},
                'insulation_improvement': {'carbon_per_unit': 50, 'energy_per_unit': 500, 'cost_savings_per_unit': 200},
                'smart_thermostat': {'carbon_per_unit': 30, 'energy_per_unit': 300, 'cost_savings_per_unit': 150},
                'energy_efficient_appliance': {'carbon_per_unit': 20, 'energy_per_unit': 200, 'cost_savings_per_unit': 100}
            },
            'transportation': {
                'bike_commute_km': {'carbon_per_unit': 0.2, 'energy_per_unit': 0, 'cost_savings_per_unit': 0.5},
                'public_transport_km': {'carbon_per_unit': 0.1, 'energy_per_unit': 0, 'cost_savings_per_unit': 0.3},
                'electric_vehicle': {'carbon_per_unit': 1000, 'energy_per_unit': 0, 'cost_savings_per_unit': 500},
                'carpooling': {'carbon_per_unit': 0.15, 'energy_per_unit': 0, 'cost_savings_per_unit': 0.4},
                'walking': {'carbon_per_unit': 0.25, 'energy_per_unit': 0, 'cost_savings_per_unit': 0.6}
            },
            'renewable_energy': {
                'solar_panel_kw': {'carbon_per_unit': 1200, 'energy_per_unit': 1500, 'cost_savings_per_unit': 600},
                'wind_turbine_kw': {'carbon_per_unit': 1000, 'energy_per_unit': 1200, 'cost_savings_per_unit': 500},
                'green_energy_plan': {'carbon_per_unit': 500, 'energy_per_unit': 800, 'cost_savings_per_unit': 200}
            },
            'food': {
                'vegetarian_meal': {'carbon_per_unit': 2.5, 'energy_per_unit': 0, 'cost_savings_per_unit': 3},
                'local_food_kg': {'carbon_per_unit': 0.5, 'energy_per_unit': 0, 'cost_savings_per_unit': 0},
                'food_waste_reduction_kg': {'carbon_per_unit': 3.3, 'energy_per_unit': 0, 'cost_savings_per_unit': 4},
                'composting_kg': {'carbon_per_unit': 0.8, 'energy_per_unit': 0, 'cost_savings_per_unit': 0}
            },
            'water': {
                'low_flow_fixture': {'carbon_per_unit': 15, 'energy_per_unit': 50, 'cost_savings_per_unit': 75},
                'rainwater_harvesting': {'carbon_per_unit': 25, 'energy_per_unit': 30, 'cost_savings_per_unit': 100},
                'drought_resistant_landscaping': {'carbon_per_unit': 40, 'energy_per_unit': 60, 'cost_savings_per_unit': 150}
            },
            'waste': {
                'recycling_kg': {'carbon_per_unit': 0.5, 'energy_per_unit': 2, 'cost_savings_per_unit': 0},
                'reusable_bag': {'carbon_per_unit': 0.1, 'energy_per_unit': 0, 'cost_savings_per_unit': 0.05},
                'composting_kg': {'carbon_per_unit': 0.8, 'energy_per_unit': 0, 'cost_savings_per_unit': 0},
                'electronic_recycling_kg': {'carbon_per_unit': 2, 'energy_per_unit': 5, 'cost_savings_per_unit': 0}
            }
        }
    
    def get_user_file_path(self, user_id: str) -> str:
        """Get file path for user data"""
        return os.path.join(self.data_dir, f"{user_id}_actions.json")
    
    def load_user_actions(self, user_id: str) -> List[Dict[str, Any]]:
        """Load user actions from file"""
        file_path = self.get_user_file_path(user_id)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading user actions: {e}")
        return []
    
    def save_user_actions(self, user_id: str, actions: List[Dict[str, Any]]):
        """Save user actions to file"""
        file_path = self.get_user_file_path(user_id)
        try:
            with open(file_path, 'w') as f:
                json.dump(actions, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving user actions: {e}")
    
    def track_action(self, user_id: str, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track a new climate action"""
        try:
            # Calculate impact
            impact = self.calculate_impact(action_data)
            
            # Create action record
            action_record = {
                'id': f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'action_type': action_data['action_type'],
                'subtype': action_data['subtype'],
                'description': action_data['description'],
                'quantity': action_data['quantity'],
                'unit': action_data['unit'],
                'carbon_saved_kg': impact['carbon_saved_kg'],
                'energy_saved_kwh': impact['energy_saved_kwh'],
                'cost_savings': impact['cost_savings'],
                'water_saved_liters': impact.get('water_saved_liters', 0)
            }
            
            # Load existing actions and add new one
            actions = self.load_user_actions(user_id)
            actions.append(action_record)
            
            # Save updated actions
            self.save_user_actions(user_id, actions)
            
            return action_record
            
        except Exception as e:
            logger.error(f"Error tracking action: {e}")
            raise
    
    def calculate_impact(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate environmental impact of an action"""
        action_type = action_data['action_type']
        subtype = action_data['subtype']
        quantity = action_data['quantity']
        
        # Get impact factors
        if action_type in self.impact_factors and subtype in self.impact_factors[action_type]:
            factors = self.impact_factors[action_type][subtype]
        else:
            # Default factors for unknown actions
            factors = {'carbon_per_unit': 1, 'energy_per_unit': 2, 'cost_savings_per_unit': 1}
        
        # Calculate impacts
        carbon_saved_kg = factors['carbon_per_unit'] * quantity
        energy_saved_kwh = factors['energy_per_unit'] * quantity
        cost_savings = factors['cost_savings_per_unit'] * quantity
        
        # Estimate water savings (simplified)
        water_saved_liters = 0
        if action_type == 'water':
            water_saved_liters = quantity * 100  # Rough estimate
        elif subtype in ['low_flow_fixture', 'drought_resistant_landscaping']:
            water_saved_liters = quantity * 50
        
        return {
            'carbon_saved_kg': round(carbon_saved_kg, 2),
            'energy_saved_kwh': round(energy_saved_kwh, 2),
            'cost_savings': round(cost_savings, 2),
            'water_saved_liters': round(water_saved_liters, 2)
        }
    
    def get_user_impact_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user impact summary for specified period"""
        actions = self.load_user_actions(user_id)
        
        # Filter actions by date
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_actions = [
            action for action in actions
            if datetime.fromisoformat(action['timestamp']) >= cutoff_date
        ]
        
        # Calculate totals
        total_carbon_saved_kg = sum(action['carbon_saved_kg'] for action in recent_actions)
        total_energy_saved_kwh = sum(action['energy_saved_kwh'] for action in recent_actions)
        total_water_saved_liters = sum(action['water_saved_liters'] for action in recent_actions)
        total_cost_savings = sum(action['cost_savings'] for action in recent_actions)
        
        # Calculate equivalent metrics
        equivalent_metrics = self.calculate_equivalent_metrics(total_carbon_saved_kg)
        
        return {
            'user_id': user_id,
            'period_days': days,
            'total_actions': len(recent_actions),
            'total_carbon_saved_kg': round(total_carbon_saved_kg, 2),
            'total_energy_saved_kwh': round(total_energy_saved_kwh, 2),
            'total_water_saved_liters': round(total_water_saved_liters, 2),
            'total_cost_savings': round(total_cost_savings, 2),
            'recent_actions': recent_actions[-5:],  # Last 5 actions
            'equivalent_metrics': equivalent_metrics
        }
    
    def calculate_equivalent_metrics(self, carbon_saved_kg: float) -> Dict[str, Any]:
        """Calculate equivalent metrics for carbon savings"""
        # Conversion factors
        kg_co2_per_tree_per_year = 22  # Average tree absorption
        kg_co2_per_liter_gasoline = 2.31
        kg_co2_per_kg_coal = 2.86
        km_per_liter_average_car = 12
        
        trees_planted_equivalent = carbon_saved_kg / kg_co2_per_tree_per_year
        gasoline_not_used_liters = carbon_saved_kg / kg_co2_per_liter_gasoline
        coal_not_burned_kg = carbon_saved_kg / kg_co2_per_kg_coal
        miles_not_driven = (gasoline_not_used_liters * km_per_liter_average_car) * 0.621371  # Convert km to miles
        
        return {
            'trees_planted_equivalent': round(trees_planted_equivalent, 1),
            'gasoline_not_used_liters': round(gasoline_not_used_liters, 1),
            'coal_not_burned_kg': round(coal_not_burned_kg, 1),
            'miles_not_driven': round(miles_not_driven, 1)
        }
    
    def get_leaderboard(self, metric: str = 'carbon_saved_kg', limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard of users by specified metric"""
        leaderboard = []
        
        # Get all user files
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.endswith('_actions.json'):
                    user_id = filename.replace('_actions.json', '')
                    summary = self.get_user_impact_summary(user_id, days=365)  # Annual summary
                    
                    leaderboard.append({
                        'user_id': user_id,
                        'carbon_saved_kg': summary['total_carbon_saved_kg'],
                        'energy_saved_kwh': summary['total_energy_saved_kwh'],
                        'total_actions': summary['total_actions'],
                        'cost_savings': summary['total_cost_savings']
                    })
        
        # Add some demo users if leaderboard is empty
        if not leaderboard:
            demo_users = [
                {'user_id': 'eco_warrior', 'carbon_saved_kg': 1250.5, 'energy_saved_kwh': 2100, 'total_actions': 45, 'cost_savings': 850},
                {'user_id': 'green_champion', 'carbon_saved_kg': 980.2, 'energy_saved_kwh': 1800, 'total_actions': 38, 'cost_savings': 720},
                {'user_id': 'climate_hero', 'carbon_saved_kg': 875.8, 'energy_saved_kwh': 1650, 'total_actions': 42, 'cost_savings': 680},
                {'user_id': 'sustainability_star', 'carbon_saved_kg': 750.3, 'energy_saved_kwh': 1400, 'total_actions': 35, 'cost_savings': 590},
                {'user_id': 'earth_guardian', 'carbon_saved_kg': 650.7, 'energy_saved_kwh': 1200, 'total_actions': 28, 'cost_savings': 520}
            ]
            leaderboard.extend(demo_users)
        
        # Sort by specified metric
        leaderboard.sort(key=lambda x: x.get(metric, 0), reverse=True)
        
        return leaderboard[:limit]
    
    def generate_demo_data(self, user_id: str):
        """Generate demo data for a user"""
        demo_actions = [
            {
                'action_type': 'energy_efficiency',
                'subtype': 'led_bulb_replacement',
                'description': 'Replaced 10 incandescent bulbs with LEDs',
                'quantity': 10,
                'unit': 'bulbs'
            },
            {
                'action_type': 'transportation',
                'subtype': 'bike_commute_km',
                'description': 'Biked to work instead of driving',
                'quantity': 25,
                'unit': 'km'
            },
            {
                'action_type': 'food',
                'subtype': 'vegetarian_meal',
                'description': 'Had vegetarian meals this week',
                'quantity': 5,
                'unit': 'meals'
            },
            {
                'action_type': 'water',
                'subtype': 'low_flow_fixture',
                'description': 'Installed low-flow showerhead',
                'quantity': 1,
                'unit': 'fixture'
            },
            {
                'action_type': 'waste',
                'subtype': 'recycling_kg',
                'description': 'Recycled paper and plastic',
                'quantity': 15,
                'unit': 'kg'
            }
        ]
        
        # Add demo actions with random timestamps over the last 30 days
        for i, action_data in enumerate(demo_actions):
            # Random timestamp in the last 30 days
            days_ago = random.randint(1, 30)
            timestamp = datetime.now() - timedelta(days=days_ago)
            
            impact = self.calculate_impact(action_data)
            
            action_record = {
                'id': f"{user_id}_demo_{i}",
                'user_id': user_id,
                'timestamp': timestamp.isoformat(),
                'action_type': action_data['action_type'],
                'subtype': action_data['subtype'],
                'description': action_data['description'],
                'quantity': action_data['quantity'],
                'unit': action_data['unit'],
                'carbon_saved_kg': impact['carbon_saved_kg'],
                'energy_saved_kwh': impact['energy_saved_kwh'],
                'cost_savings': impact['cost_savings'],
                'water_saved_liters': impact.get('water_saved_liters', 0)
            }
            
            # Save action
            actions = self.load_user_actions(user_id)
            actions.append(action_record)
            self.save_user_actions(user_id, actions)