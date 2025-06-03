"""
Simplified RAG system that works without heavy ML dependencies
"""
import json
import logging
from typing import List, Dict, Any, Tuple
import os
from config import settings

logger = logging.getLogger(__name__)

class SimpleRAGSystem:
    """Simplified RAG system for demo purposes"""
    
    def __init__(self):
        self.knowledge_base = self._load_climate_knowledge()
        self.use_fallback = True  # Always use fallback for demo
    
    def _load_climate_knowledge(self) -> List[Dict[str, Any]]:
        """Load climate knowledge base"""
        return [
            {
                "title": "Renewable Energy Transition",
                "content": "Renewable energy sources like solar, wind, and hydroelectric power are crucial for reducing greenhouse gas emissions. Solar panels can reduce household carbon footprint by 3-4 tons of CO2 per year. Wind energy is one of the fastest-growing renewable sources globally. The transition to renewable energy requires investment but provides long-term cost savings and environmental benefits. Government incentives and falling technology costs make renewable energy increasingly accessible to individuals and businesses.",
                "category": "energy",
                "keywords": ["solar", "wind", "renewable", "energy", "carbon", "emissions"]
            },
            {
                "title": "Sustainable Transportation",
                "content": "Transportation accounts for approximately 29% of greenhouse gas emissions in the United States. Electric vehicles can reduce emissions by 60-70% compared to gasoline vehicles. Public transportation, cycling, and walking are highly effective ways to reduce personal carbon footprint. Carpooling and ride-sharing can significantly reduce per-person emissions. For long-distance travel, trains are generally more environmentally friendly than planes or cars.",
                "category": "transportation",
                "keywords": ["transport", "electric", "vehicle", "bike", "walk", "public", "emissions"]
            },
            {
                "title": "Energy Efficiency at Home",
                "content": "Home energy efficiency improvements can reduce energy consumption by 20-30%. LED lighting uses 75% less energy than incandescent bulbs. Proper insulation can reduce heating and cooling costs by up to 40%. Smart thermostats can save 10-15% on heating and cooling bills. Energy-efficient appliances with ENERGY STAR ratings use 10-50% less energy than standard models. Sealing air leaks around windows and doors is a cost-effective way to improve efficiency.",
                "category": "energy_efficiency",
                "keywords": ["LED", "insulation", "thermostat", "appliances", "efficiency", "home"]
            },
            {
                "title": "Sustainable Food Choices",
                "content": "Food production accounts for about 26% of global greenhouse gas emissions. Plant-based diets can reduce food-related emissions by up to 73%. Reducing meat consumption, especially beef, has significant environmental impact. Local and seasonal food choices reduce transportation emissions. Reducing food waste is crucial - about 1/3 of food produced globally is wasted. Composting food scraps reduces methane emissions from landfills and creates valuable soil amendment.",
                "category": "food",
                "keywords": ["food", "plant", "meat", "local", "waste", "compost", "diet"]
            },
            {
                "title": "Water Conservation",
                "content": "Water conservation reduces energy consumption for water treatment and distribution. Low-flow fixtures can reduce water usage by 20-60%. Fixing leaks promptly prevents waste - a single dripping faucet can waste over 3,000 gallons per year. Rainwater harvesting can reduce municipal water demand. Drought-resistant landscaping reduces irrigation needs. Shorter showers and full loads in dishwashers and washing machines maximize efficiency.",
                "category": "water",
                "keywords": ["water", "conservation", "leak", "rainwater", "drought", "irrigation"]
            },
            {
                "title": "Waste Reduction and Recycling",
                "content": "The waste sector contributes about 5% of global greenhouse gas emissions. Reducing, reusing, and recycling materials prevents emissions from manufacturing new products. Composting organic waste reduces methane emissions from landfills. Proper recycling of electronics prevents toxic materials from entering the environment. Choosing products with minimal packaging reduces waste. Buying durable, repairable products reduces long-term waste generation.",
                "category": "waste",
                "keywords": ["waste", "recycle", "reuse", "compost", "packaging", "electronics"]
            }
        ]
    
    def search_knowledge(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Simple keyword-based search"""
        query_lower = query.lower()
        results = []
        
        for doc in self.knowledge_base:
            score = 0
            # Check title
            if any(word in doc["title"].lower() for word in query_lower.split()):
                score += 3
            
            # Check keywords
            for keyword in doc["keywords"]:
                if keyword in query_lower:
                    score += 2
            
            # Check content
            if any(word in doc["content"].lower() for word in query_lower.split()):
                score += 1
            
            if score > 0:
                results.append({
                    'content': doc["content"],
                    'metadata': {
                        'title': doc["title"],
                        'category': doc["category"],
                        'source': 'Climate Knowledge Base'
                    },
                    'similarity': min(score / 10, 1.0)  # Normalize to 0-1
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:n_results]
    
    def retrieve_and_generate(self, query: str, user_profile: Dict[str, Any] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Retrieve relevant knowledge and generate response"""
        try:
            # Search for relevant documents
            relevant_docs = self.search_knowledge(query, n_results=3)
            
            # Generate response based on query type
            response = self._generate_response(query, relevant_docs, user_profile)
            
            return response, relevant_docs
            
        except Exception as e:
            logger.error(f"Error in retrieve_and_generate: {e}")
            return f"I apologize, but I encountered an error: {str(e)}", []
    
    def _generate_response(self, query: str, docs: List[Dict[str, Any]], user_profile: Dict[str, Any] = None) -> str:
        """Generate response based on query and documents"""
        query_lower = query.lower()
        
        # Determine query type
        if any(word in query_lower for word in ["energy", "electricity", "power", "solar", "wind"]):
            return self._generate_energy_response(docs, user_profile)
        elif any(word in query_lower for word in ["transport", "car", "vehicle", "travel", "commute"]):
            return self._generate_transport_response(docs, user_profile)
        elif any(word in query_lower for word in ["food", "diet", "meat", "eat"]):
            return self._generate_food_response(docs, user_profile)
        elif any(word in query_lower for word in ["water", "conservation", "save"]):
            return self._generate_water_response(docs, user_profile)
        elif any(word in query_lower for word in ["waste", "recycle", "trash"]):
            return self._generate_waste_response(docs, user_profile)
        elif any(word in query_lower for word in ["plan", "action", "recommend"]):
            return self._generate_action_plan(user_profile)
        else:
            return self._generate_general_response(docs, user_profile)
    
    def _generate_energy_response(self, docs: List[Dict[str, Any]], user_profile: Dict[str, Any] = None) -> str:
        """Generate energy-focused response"""
        location = user_profile.get('location', 'your area') if user_profile else 'your area'
        budget = user_profile.get('budget', 'medium') if user_profile else 'medium'
        
        response = f"""🔋 **Energy Efficiency Recommendations for {location}**

**Immediate Actions (Low Cost):**
• Switch to LED bulbs - saves 75% energy vs incandescent
• Adjust thermostat 2-3°F - saves 10-15% on heating/cooling
• Unplug electronics when not in use - eliminates phantom loads
• Use cold water for washing clothes - saves 90% of energy

**Medium-term Upgrades ({budget} budget):**
• Install programmable/smart thermostat - saves 10-15% annually
• Improve insulation and seal air leaks - reduces energy use 20-30%
• Upgrade to ENERGY STAR appliances when replacing old ones

**Long-term Investments:**
• Consider solar panels - can reduce electricity bills by 70-90%
• Heat pump installation - 3x more efficient than traditional heating
• Energy-efficient windows - reduce heating/cooling loads significantly

**Estimated Impact:** These actions combined can reduce your energy consumption by 30-50% and save $500-1500 annually."""
        
        return response
    
    def _generate_transport_response(self, docs: List[Dict[str, Any]], user_profile: Dict[str, Any] = None) -> str:
        """Generate transportation-focused response"""
        lifestyle = user_profile.get('lifestyle', 'urban') if user_profile else 'urban'
        
        response = f"""🚗 **Sustainable Transportation for {lifestyle.title()} Lifestyle**

**Daily Commuting:**
• Walk or bike for trips under 2 miles - zero emissions + health benefits
• Use public transportation when available - 45% less emissions per person
• Carpool or rideshare - reduces per-person emissions by 50%
• Work from home when possible - eliminates commute emissions

**Vehicle Choices:**
• Consider electric or hybrid vehicles - 60-70% lower emissions
• If keeping gas car, maintain proper tire pressure - improves efficiency 3%
• Combine errands into single trips - reduces total miles driven

**Long-distance Travel:**
• Choose trains over planes when possible - 80% lower emissions
• If flying, consider carbon offsets - typically $10-30 per flight
• Stay longer at destinations to reduce frequency of travel

**{lifestyle.title()}-Specific Tips:**
{self._get_lifestyle_transport_tips(lifestyle)}

**Impact:** Transportation changes can reduce your carbon footprint by 20-40%."""
        
        return response
    
    def _get_lifestyle_transport_tips(self, lifestyle: str) -> str:
        """Get lifestyle-specific transport tips"""
        tips = {
            'urban': "• Take advantage of bike-share programs\n• Use ride-sharing for occasional car needs\n• Walk to nearby amenities",
            'suburban': "• Organize neighborhood carpools\n• Consider e-bike for medium distances\n• Plan efficient routes for errands",
            'rural': "• Combine trips to town efficiently\n• Consider hybrid vehicle for long commutes\n• Explore remote work options"
        }
        return tips.get(lifestyle.lower(), tips['urban'])
    
    def _generate_food_response(self, docs: List[Dict[str, Any]], user_profile: Dict[str, Any] = None) -> str:
        """Generate food-focused response"""
        household_size = user_profile.get('household_size', 2) if user_profile else 2
        
        response = f"""🍽️ **Sustainable Food Choices for {household_size}-Person Household**

**Dietary Changes:**
• Reduce meat consumption 2-3 days per week - can cut food emissions by 30%
• Choose chicken/fish over beef - 10x lower carbon footprint
• Increase plant-based meals - beans, lentils, vegetables
• Buy organic when possible for "dirty dozen" produce

**Shopping Habits:**
• Buy local and seasonal produce - reduces transportation emissions
• Shop at farmers markets - supports local agriculture
• Choose products with minimal packaging
• Buy in bulk to reduce packaging waste

**Food Waste Reduction:**
• Plan meals weekly - reduces waste by 25%
• Store food properly to extend freshness
• Use leftovers creatively - soups, stir-fries, smoothies
• Compost food scraps - reduces methane from landfills

**Estimated Impact for {household_size} people:**
• 2-3 tons CO2 reduction annually
• $800-1200 savings on grocery bills
• Improved health outcomes

**Quick Wins:** Start with "Meatless Monday" and meal planning - easiest changes with biggest impact."""
        
        return response
    
    def _generate_water_response(self, docs: List[Dict[str, Any]], user_profile: Dict[str, Any] = None) -> str:
        """Generate water conservation response"""
        response = """💧 **Water Conservation Action Plan**

**Indoor Water Saving:**
• Install low-flow showerheads and faucets - saves 20-60% water
• Fix leaks immediately - a dripping faucet wastes 3,000+ gallons/year
• Take shorter showers - each minute saved = 2.5 gallons
• Run dishwasher and washing machine only with full loads

**Outdoor Water Saving:**
• Plant drought-resistant native plants - reduces irrigation by 50%
• Install drip irrigation or soaker hoses - 90% efficiency vs sprinklers
• Collect rainwater for garden use - free water source
• Water early morning or evening - reduces evaporation

**Advanced Strategies:**
• Install dual-flush toilets - saves 4,000+ gallons annually
• Use greywater systems for irrigation
• Choose permeable paving materials
• Install smart irrigation controllers

**Impact:**
• Typical household can save 20-30% on water bills
• Reduces energy use for water heating and treatment
• Helps preserve local water resources

**Start Here:** Fix any leaks and install low-flow fixtures - biggest immediate impact."""
        
        return response
    
    def _generate_waste_response(self, docs: List[Dict[str, Any]], user_profile: Dict[str, Any] = None) -> str:
        """Generate waste reduction response"""
        response = """♻️ **Waste Reduction & Recycling Strategy**

**Reduce (Most Important):**
• Buy only what you need - prevents waste at source
• Choose products with minimal packaging
• Opt for digital receipts and bills
• Buy durable, repairable items over disposable

**Reuse:**
• Repurpose containers for storage
• Donate items instead of throwing away
• Use both sides of paper
• Turn old clothes into cleaning rags

**Recycle Properly:**
• Learn local recycling guidelines - contamination ruins batches
• Recycle electronics at special centers - contains valuable materials
• Compost organic waste - reduces methane emissions
• Recycle batteries at designated drop-offs

**Special Items:**
• Hazardous waste: Paint, chemicals at special facilities
• Textiles: Donate or use textile recycling programs
• Plastic bags: Return to grocery store collection bins

**Impact:**
• Average household can reduce waste by 50%
• Composting alone can divert 30% of household waste
• Proper recycling saves energy and raw materials

**Quick Start:** Set up a simple composting system and learn your local recycling rules."""
        
        return response
    
    def _generate_action_plan(self, user_profile: Dict[str, Any] = None) -> str:
        """Generate personalized action plan"""
        if not user_profile:
            user_profile = {}
        
        location = user_profile.get('location', 'your area')
        lifestyle = user_profile.get('lifestyle', 'general')
        interests = user_profile.get('interests', [])
        budget = user_profile.get('budget', 'medium')
        
        response = f"""🎯 **Personalized Climate Action Plan - {location}**

**Your Profile:** {lifestyle.title()} lifestyle, {budget} budget
**Focus Areas:** {', '.join(interests) if interests else 'All areas'}

**Phase 1: Quick Wins (0-3 months)**
• Switch to LED bulbs throughout home
• Start meal planning to reduce food waste
• Walk/bike for trips under 2 miles
• Fix any water leaks
• Set up basic recycling system
**Expected Impact:** 5-10% carbon reduction, $200-400 savings

**Phase 2: Efficiency Upgrades (3-12 months)**
• Install programmable thermostat
• Improve home insulation
• Reduce meat consumption 2-3 days/week
• Install low-flow water fixtures
• Start composting program
**Expected Impact:** Additional 10-15% reduction, $400-800 savings

**Phase 3: Major Investments (1-3 years)**
{self._get_budget_specific_investments(budget)}
**Expected Impact:** Additional 15-25% reduction

**Total Potential Impact:**
• 30-50% carbon footprint reduction
• $1000-2000+ annual savings
• Improved health and comfort

**Next Steps:**
1. Start with 2-3 quick wins this week
2. Research local incentives for major upgrades
3. Track your progress monthly
4. Share your success with friends and family"""
        
        return response
    
    def _get_budget_specific_investments(self, budget: str) -> str:
        """Get budget-specific investment recommendations"""
        investments = {
            'low': "• Energy-efficient appliances when replacing\n• E-bike or public transit pass\n• Drought-resistant landscaping",
            'medium': "• Solar panel installation\n• Heat pump system\n• Electric or hybrid vehicle\n• Home energy audit and improvements",
            'high': "• Whole-home solar + battery storage\n• Geothermal heating/cooling\n• Electric vehicle + home charging\n• Net-zero home renovation"
        }
        return investments.get(budget.lower(), investments['medium'])
    
    def _generate_general_response(self, docs: List[Dict[str, Any]], user_profile: Dict[str, Any] = None) -> str:
        """Generate general climate action response"""
        if docs:
            # Use the most relevant document
            doc = docs[0]
            return f"""Based on the latest climate science and best practices:

{doc['content']}

**Personalized Recommendations:**
• Start with the easiest and most cost-effective actions
• Focus on areas where you have the most control
• Track your progress to stay motivated
• Share your actions to inspire others

Would you like specific advice on any particular area like energy, transportation, food, or water conservation?"""
        else:
            return """I'm here to help you take effective climate action! I can provide personalized advice on:

🔋 **Energy Efficiency** - Reduce your home energy use
🚗 **Transportation** - Sustainable travel options  
🍽️ **Food Choices** - Lower-impact diet and shopping
💧 **Water Conservation** - Save water and money
♻️ **Waste Reduction** - Minimize and recycle better

What area would you like to focus on first?"""
    
    def initialize_with_sample_data(self):
        """Initialize with sample data (already loaded)"""
        logger.info("Simple RAG system initialized with climate knowledge base")
        return True
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        return {
            "total_documents": len(self.knowledge_base),
            "categories": list(set(doc["category"] for doc in self.knowledge_base)),
            "system_type": "Simple RAG (keyword-based)"
        }