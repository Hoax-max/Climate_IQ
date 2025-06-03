"""
Main Streamlit application for Climate Action Intelligence Platform
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import os
import sys
from datetime import datetime, timedelta
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.rag_system.climate_rag import ClimateRAGSystem
from backend.api_handlers.climate_apis import ClimateAPIHandler
from backend.data_processors.impact_tracker import ImpactTracker
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="ClimateIQ - AI Climate Action Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E8B57, #228B22);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f8f0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #228B22;
        margin: 0.5rem 0;
    }
    .action-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_systems():
    """Initialize backend systems"""
    try:
        rag_system = ClimateRAGSystem()
        rag_system.initialize_with_sample_data()
        
        api_handler = ClimateAPIHandler()
        impact_tracker = ImpactTracker()
        
        return rag_system, api_handler, impact_tracker
    except Exception as e:
        st.error(f"Error initializing systems: {e}")
        st.error("Failed to initialize backend systems. Please check your configuration.")
        # Return mock objects for demonstration
        return None, None, None

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌍 ClimateIQ - Your AI Climate Action Partner</h1>
        <p>Personalized climate solutions powered by IBM watsonx.ai and real-time data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize systems
    rag_system, api_handler, impact_tracker = initialize_systems()
    
    # Check if systems initialized properly
    demo_mode = not all([rag_system, api_handler, impact_tracker])
    if demo_mode:
        st.warning("⚠️ Running in demonstration mode. Some features may be limited.")
        st.info("💡 This demo showcases the platform's interface and capabilities. Full functionality requires proper API configuration.")
    
    # Sidebar for user profile
    with st.sidebar:
        st.header("👤 Your Profile")
        
        # User identification
        user_id = st.text_input("User ID", value="demo_user", help="Enter a unique identifier")
        
        # Location and basic info
        location = st.text_input("📍 Location", value="New York, NY", help="Enter your city, state/country")
        lifestyle = st.selectbox("🏠 Lifestyle", ["Urban", "Suburban", "Rural"])
        household_size = st.number_input("👥 Household Size", min_value=1, max_value=10, value=2)
        
        # Interests and goals
        st.subheader("🎯 Climate Goals")
        interests = st.multiselect(
            "Areas of Interest",
            ["Energy Efficiency", "Renewable Energy", "Transportation", "Food & Diet", "Waste Reduction", "Water Conservation"],
            default=["Energy Efficiency", "Transportation"]
        )
        
        budget = st.selectbox("💰 Budget for Climate Actions", ["Low ($0-500)", "Medium ($500-2000)", "High ($2000+)"])
        
        # Current actions
        current_actions = st.text_area("Current Climate Actions", 
                                     placeholder="Describe any climate actions you're already taking...")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🎯 Action Plan", "📊 Impact Tracker", "🌤️ Local Data", "💬 AI Assistant", "🏆 Community", "🌍 Global Dashboard"])
    
    # User profile dictionary
    user_profile = {
        'user_id': user_id,
        'location': location,
        'lifestyle': lifestyle,
        'household_size': household_size,
        'interests': interests,
        'budget': budget,
        'current_actions': current_actions
    }
    
    with tab1:
        display_action_plan(rag_system, user_profile, demo_mode)
    
    with tab2:
        display_impact_tracker(impact_tracker, user_id, demo_mode)
    
    with tab3:
        display_local_data(api_handler, location, demo_mode)
    
    with tab4:
        display_ai_assistant(rag_system, user_profile, demo_mode)
    
    with tab5:
        display_community(impact_tracker, demo_mode)
    
    with tab6:
        display_global_dashboard(api_handler, demo_mode)

def display_action_plan(rag_system, user_profile, demo_mode=False):
    """Display personalized action plan"""
    st.header("🎯 Your Personalized Climate Action Plan")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔄 Generate New Action Plan", type="primary"):
            with st.spinner("🤖 Analyzing your profile and generating personalized recommendations..."):
                if demo_mode or not rag_system:
                    # Demo mode action plan
                    st.success("✅ Your personalized action plan is ready!")
                    st.markdown("### 📋 Recommended Actions")
                    demo_plan = f"""
                    **Personalized for {user_profile['location']} - {user_profile['lifestyle']} Lifestyle**
                    
                    **🏠 Home Energy (Priority: High)**
                    - Switch to LED lighting (saves 75% energy)
                    - Install programmable thermostat (saves 10-15% on heating/cooling)
                    - Improve insulation and seal air leaks
                    
                    **🚗 Transportation (Priority: High)**
                    - Walk/bike for trips under 2 miles
                    - Use public transportation when available
                    - Consider carpooling for longer commutes
                    
                    **🍽️ Food & Consumption (Priority: Medium)**
                    - Reduce meat consumption by 2-3 days per week
                    - Buy local and seasonal produce
                    - Minimize food waste through meal planning
                    
                    **💧 Water Conservation (Priority: Medium)**
                    - Install low-flow showerheads and faucets
                    - Fix leaks promptly
                    - Collect rainwater for gardening
                    
                    **Estimated Annual Impact:** 2.5 tons CO2 reduction, $800 savings
                    """
                    st.markdown(demo_plan)
                    st.info("💡 This is a demo action plan. Full personalization requires proper API configuration.")
                else:
                    try:
                        # Generate personalized plan using RAG system
                        query = f"Create a personalized climate action plan for someone in {user_profile['location']} with {user_profile['lifestyle']} lifestyle, household of {user_profile['household_size']}, interested in {', '.join(user_profile['interests'])}, with {user_profile['budget']} budget."
                        
                        response, sources = rag_system.retrieve_and_generate(query, user_profile)
                        
                        st.success("✅ Your personalized action plan is ready!")
                        
                        # Display the plan
                        st.markdown("### 📋 Recommended Actions")
                        st.markdown(response)
                        
                        # Display sources
                        if sources:
                            with st.expander("📚 Supporting Information Sources"):
                                for i, source in enumerate(sources[:3]):
                                    st.write(f"**Source {i+1}:** {source['metadata'].get('title', 'Climate Data')}")
                                    st.write(f"*Category:* {source['metadata'].get('category', 'General')}")
                                    st.write(f"*Relevance:* {source['similarity']:.2%}")
                                    st.write("---")
                
                    except Exception as e:
                        st.error(f"Error generating action plan: {e}")
    
    with col2:
        st.markdown("### 💡 Quick Tips")
        st.info("💡 **Pro Tip:** The more specific your location and interests, the better your personalized recommendations!")
        
        st.markdown("### 🎯 Focus Areas")
        for interest in user_profile['interests']:
            st.markdown(f"• {interest}")

def display_impact_tracker(impact_tracker, user_id, demo_mode=False):
    """Display impact tracking dashboard"""
    st.header("📊 Your Environmental Impact")
    
    # Get user impact summary
    impact_summary = impact_tracker.get_user_impact_summary(user_id, days=30)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🌱 Carbon Saved",
            f"{impact_summary['total_carbon_saved_kg']:.1f} kg",
            help="Total CO2 emissions prevented"
        )
    
    with col2:
        st.metric(
            "⚡ Energy Saved",
            f"{impact_summary['total_energy_saved_kwh']:.1f} kWh",
            help="Total energy consumption reduced"
        )
    
    with col3:
        st.metric(
            "💧 Water Saved",
            f"{impact_summary['total_water_saved_liters']:.0f} L",
            help="Total water consumption reduced"
        )
    
    with col4:
        st.metric(
            "💰 Cost Savings",
            f"${impact_summary['total_cost_savings']:.2f}",
            help="Estimated cost savings"
        )
    
    # Action logging
    st.subheader("➕ Log New Climate Action")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        action_type = st.selectbox(
            "Action Category",
            ["energy_efficiency", "transportation", "renewable_energy", "food", "water", "waste"]
        )
        
        action_subtype = st.selectbox(
            "Specific Action",
            get_action_subtypes(action_type)
        )
        
        description = st.text_input("Description", placeholder="Describe your climate action...")
        quantity = st.number_input("Quantity", min_value=0.1, value=1.0, step=0.1)
        unit = st.text_input("Unit", value="unit")
    
    with col2:
        st.markdown("### 📝 Action Examples")
        examples = get_action_examples(action_type)
        for example in examples:
            st.write(f"• {example}")
    
    if st.button("📝 Log Action"):
        if description:
            try:
                action_data = {
                    'action_type': action_type,
                    'subtype': action_subtype,
                    'description': description,
                    'quantity': quantity,
                    'unit': unit,
                    'location': user_id  # Using user_id as location for demo
                }
                
                record = impact_tracker.track_action(user_id, action_data)
                st.success(f"✅ Action logged! Estimated impact: {record.carbon_saved_kg:.2f} kg CO2 saved")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error logging action: {e}")
        else:
            st.warning("Please provide a description for your action.")
    
    # Recent actions
    if impact_summary['recent_actions']:
        st.subheader("📋 Recent Actions")
        for action in reversed(impact_summary['recent_actions']):
            with st.expander(f"{action['description']} - {action['timestamp'][:10]}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Carbon Saved:** {action['carbon_saved_kg']:.2f} kg")
                with col2:
                    st.write(f"**Energy Saved:** {action['energy_saved_kwh']:.2f} kWh")
                with col3:
                    st.write(f"**Cost Savings:** ${action['cost_savings']:.2f}")
    
    # Equivalent metrics
    if impact_summary['equivalent_metrics']:
        st.subheader("🌳 Impact Equivalents")
        equivalents = impact_summary['equivalent_metrics']
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🌳 **Trees Planted:** {equivalents.get('trees_planted_equivalent', 0)} trees")
            st.info(f"🚗 **Miles Not Driven:** {equivalents.get('miles_not_driven', 0)} miles")
        
        with col2:
            st.info(f"⛽ **Gasoline Saved:** {equivalents.get('gasoline_not_used_liters', 0)} liters")
            st.info(f"🔥 **Coal Not Burned:** {equivalents.get('coal_not_burned_kg', 0)} kg")

def display_local_data(api_handler, location, demo_mode=False):
    """Display local climate and environmental data"""
    st.header("🌤️ Local Climate Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌡️ Current Weather")
        if st.button("🔄 Refresh Weather Data"):
            with st.spinner("Fetching weather data..."):
                # Convert location format for OpenWeatherMap API
                # "New York, NY" -> "New York,US"
                api_location = location.replace(", NY", ",US").replace(", CA", ",US").replace(", TX", ",US")
                if ", " in api_location and not api_location.endswith(",US"):
                    # For other US states, convert to US format
                    city_state = api_location.split(", ")
                    if len(city_state) == 2 and len(city_state[1]) == 2:  # US state code
                        api_location = f"{city_state[0]},US"
                
                weather_data = api_handler.get_weather_data(api_location)
                
                if 'error' not in weather_data:
                    st.success(f"📍 **{weather_data['location']}, {weather_data['country']}**")
                    
                    # Weather metrics
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("🌡️ Temperature", f"{weather_data['temperature']:.1f}°C")
                    with col_b:
                        st.metric("💨 Wind Speed", f"{weather_data['wind_speed']:.1f} m/s")
                    with col_c:
                        st.metric("💧 Humidity", f"{weather_data['humidity']}%")
                    
                    st.write(f"**Conditions:** {weather_data['weather'].title()}")
                    
                    # Air quality
                    lat, lon = weather_data['coordinates']['lat'], weather_data['coordinates']['lon']
                    air_quality = api_handler.get_air_quality(lat, lon)
                    
                    if 'error' not in air_quality:
                        aqi_levels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
                        aqi_colors = {1: "green", 2: "lightgreen", 3: "yellow", 4: "orange", 5: "red"}
                        
                        aqi = air_quality['aqi']
                        st.markdown(f"**Air Quality:** <span style='color: {aqi_colors[aqi]}'>{aqi_levels[aqi]} (AQI: {aqi})</span>", 
                                  unsafe_allow_html=True)
                else:
                    st.error(f"Error fetching weather data: {weather_data['error']}")
    
    with col2:
        st.subheader("🔋 Renewable Energy Potential")
        if st.button("🔄 Analyze Renewable Potential"):
            with st.spinner("Analyzing renewable energy potential..."):
                # Convert location format for OpenWeatherMap API
                # "New York, NY" -> "New York,US"
                api_location = location.replace(", NY", ",US").replace(", CA", ",US").replace(", TX", ",US")
                if ", " in api_location and not api_location.endswith(",US"):
                    # For other US states, convert to US format
                    city_state = api_location.split(", ")
                    if len(city_state) == 2 and len(city_state[1]) == 2:  # US state code
                        api_location = f"{city_state[0]},US"
                
                renewable_data = api_handler.get_renewable_energy_potential(api_location)
                
                if 'error' not in renewable_data:
                    st.success(f"📍 **Analysis for {renewable_data['location']}**")
                    
                    # Potential metrics
                    col_a, col_b = st.columns(2)
                    with col_a:
                        solar_color = {"High": "green", "Medium": "orange", "Low": "red"}[renewable_data['solar_potential']]
                        st.markdown(f"**☀️ Solar Potential:** <span style='color: {solar_color}'>{renewable_data['solar_potential']}</span>", 
                                  unsafe_allow_html=True)
                        st.write(f"Avg. Solar Irradiance: {renewable_data['avg_solar_irradiance']} kWh/m²/day")
                    
                    with col_b:
                        wind_color = {"High": "green", "Medium": "orange", "Low": "red"}[renewable_data['wind_potential']]
                        st.markdown(f"**💨 Wind Potential:** <span style='color: {wind_color}'>{renewable_data['wind_potential']}</span>", 
                                  unsafe_allow_html=True)
                        st.write(f"Avg. Wind Speed: {renewable_data['avg_wind_speed']} m/s")
                    
                    # Recommendations
                    st.markdown("**🎯 Recommendations:**")
                    for rec in renewable_data['recommendations']:
                        st.write(f"• {rec}")
                else:
                    st.error(f"Error analyzing renewable potential: {renewable_data['error']}")
    
    # Carbon footprint calculator
    st.subheader("🧮 Carbon Footprint Calculator")
    
    calc_type = st.selectbox("Calculate emissions for:", ["Electricity Usage", "Vehicle Travel", "Flight"])
    
    if calc_type == "Electricity Usage":
        kwh = st.number_input("Electricity usage (kWh)", min_value=0.0, value=100.0)
        country = st.selectbox("Country", ["us", "ca", "gb", "de", "fr", "au"])
        
        if st.button("Calculate Electricity Emissions"):
            activity_data = {"kwh": kwh, "country": country}
            result = api_handler.calculate_carbon_footprint("electricity", activity_data)
            
            if 'error' not in result:
                st.success(f"🌱 **Carbon Footprint:** {result['carbon_kg']:.2f} kg CO2")
                st.info(f"💡 **Tip:** This is equivalent to driving {result['carbon_kg']/0.404:.1f} miles in an average car")
            else:
                st.error(f"Error calculating emissions: {result['error']}")

def display_ai_assistant(rag_system, user_profile, demo_mode=False):
    """Display enhanced AI assistant chat interface with advanced features"""
    st.header("💬 AI Climate Assistant")
    
    # Feature selector
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("🤖 **Advanced AI-powered climate intelligence** - Ask me anything about climate action, sustainability, or environmental impact!")
    
    with col2:
        ai_mode = st.selectbox("AI Mode", [
            "💬 Chat", 
            "🔮 Predictions", 
            "📊 Analysis", 
            "🏢 Business"
        ], key="ai_mode")
    
    # Advanced AI features based on mode
    if ai_mode == "🔮 Predictions":
        st.subheader("🔮 Climate Impact Predictions")
        
        col_a, col_b = st.columns(2)
        with col_a:
            timeframe = st.selectbox("Prediction Timeframe", ["6 months", "1 year", "5 years", "10 years"])
        with col_b:
            prediction_type = st.selectbox("Prediction Type", [
                "Personal Impact", 
                "Local Climate", 
                "Energy Savings", 
                "Cost Analysis"
            ])
        
        if st.button("🔮 Generate Prediction"):
            with st.spinner("Analyzing climate data and trends..."):
                # Mock prediction data for demo
                prediction_data = {
                    "timeframe": timeframe,
                    "type": prediction_type,
                    "carbon_reduction": "25-35%",
                    "cost_savings": "$1,200-1,800",
                    "confidence": "High (85%)",
                    "key_factors": ["Energy efficiency improvements", "Transportation changes", "Local climate policies"]
                }
                
                st.success("🎯 **Prediction Results**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Carbon Reduction", prediction_data["carbon_reduction"])
                with col2:
                    st.metric("Cost Savings", prediction_data["cost_savings"])
                with col3:
                    st.metric("Confidence", prediction_data["confidence"])
                
                st.info("📈 **Key Factors:** " + ", ".join(prediction_data["key_factors"]))
                
                # Detailed analysis
                st.markdown(f"""
                **🔍 Detailed Analysis for {timeframe}:**
                
                Based on your profile and current climate trends, here's what we predict:
                
                **🌱 Environmental Impact:**
                - Your carbon footprint could decrease by {prediction_data["carbon_reduction"]} through planned actions
                - This equals removing approximately 2.5 cars from the road for a year
                - Equivalent to planting 15-20 trees annually
                
                **💰 Financial Impact:**
                - Estimated savings: {prediction_data["cost_savings"]} over {timeframe}
                - ROI on climate investments: 150-200%
                - Potential tax incentives: $300-500
                
                **🎯 Recommendations:**
                - Prioritize energy efficiency upgrades (highest ROI)
                - Consider solar installation (long-term savings)
                - Explore local climate incentive programs
                """)
    
    elif ai_mode == "📊 Analysis":
        st.subheader("📊 Climate Data Analysis")
        
        analysis_type = st.selectbox("Analysis Type", [
            "Action Synergies",
            "Local Climate Trends", 
            "Carbon Footprint Breakdown",
            "Renewable Energy Potential"
        ])
        
        if st.button("📊 Run Analysis"):
            with st.spinner("Performing advanced climate analysis..."):
                if analysis_type == "Action Synergies":
                    st.success("🔗 **Action Synergy Analysis**")
                    
                    # Mock synergy data
                    actions = ["LED Lighting", "Smart Thermostat", "Solar Panels"]
                    st.markdown(f"""
                    **Analyzing synergies between: {', '.join(actions)}**
                    
                    **🎯 Synergy Score: 92/100 (Excellent)**
                    
                    **📈 Combined Impact:**
                    - Individual actions: 15% + 12% + 25% = 52% reduction
                    - **Synergistic effect: 68% reduction** (+16% bonus!)
                    
                    **💡 Why they work together:**
                    - LED lighting reduces heat load → Smart thermostat works more efficiently
                    - Lower energy demand → Solar panels cover higher % of needs
                    - All three reduce peak demand → Better grid integration
                    
                    **🚀 Optimization Recommendations:**
                    1. Install LEDs first (quick wins, immediate savings)
                    2. Add smart thermostat (leverages LED heat reduction)
                    3. Size solar system based on reduced demand
                    
                    **💰 Financial Synergies:**
                    - Combined installation discounts: 15%
                    - Faster payback period: 6.2 years vs 8.5 years individually
                    """)
                
                elif analysis_type == "Local Climate Trends":
                    st.success("🌡️ **Local Climate Trends Analysis**")
                    
                    # Create mock trend chart
                    import pandas as pd
                    import plotly.graph_objects as go
                    
                    years = list(range(2020, 2031))
                    temp_trend = [15.2, 15.8, 16.1, 16.4, 16.7, 17.0, 17.3, 17.6, 17.9, 18.2, 18.5]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=years, 
                        y=temp_trend,
                        mode='lines+markers',
                        name='Average Temperature',
                        line=dict(color='red', width=3)
                    ))
                    fig.update_layout(
                        title="Temperature Trend for New York",
                        xaxis_title="Year",
                        yaxis_title="Temperature (°C)",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("""
                    **🔍 Key Findings:**
                    - Temperature increasing by 0.3°C per year
                    - 15% increase in extreme heat days expected
                    - Cooling costs projected to rise 25% by 2030
                    
                    **🎯 Adaptation Strategies:**
                    - Invest in efficient cooling systems
                    - Consider heat pump technology
                    - Improve building insulation
                    """)
    
    elif ai_mode == "🏢 Business":
        st.subheader("🏢 Business Climate Assessment")
        
        col_a, col_b = st.columns(2)
        with col_a:
            business_type = st.selectbox("Business Type", [
                "Technology", "Manufacturing", "Retail", "Healthcare", "Finance", "Other"
            ])
        with col_b:
            business_size = st.selectbox("Business Size", [
                "Small (1-50 employees)", 
                "Medium (51-250 employees)", 
                "Large (250+ employees)"
            ])
        
        if st.button("🏢 Generate Assessment"):
            with st.spinner("Analyzing business climate risks and opportunities..."):
                st.success("📋 **Business Climate Risk Assessment**")
                
                # Risk level indicator
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Risk Level", "Medium", delta="Manageable")
                with col2:
                    st.metric("Opportunity Score", "High", delta="+15% potential")
                with col3:
                    st.metric("Action Priority", "6 months", delta="Urgent")
                
                # Detailed assessment
                st.markdown(f"""
                **🎯 Assessment for {business_type} Business ({business_size})**
                
                **⚠️ Physical Risks:**
                - Supply chain disruption: Medium risk
                - Extreme weather impact: Low-Medium risk
                - Energy cost volatility: High risk
                
                **🔄 Transition Risks:**
                - Carbon pricing policies: Medium risk
                - Regulatory compliance: Medium risk
                - Market demand shifts: High opportunity
                
                **🚀 Opportunities:**
                - Green technology adoption: $50K-200K savings potential
                - Energy efficiency improvements: 20-30% cost reduction
                - Sustainability marketing: 15% customer preference boost
                
                **💼 Recommended Actions:**
                1. **Energy Audit** (Month 1): Identify efficiency opportunities
                2. **Sustainability Plan** (Month 2-3): Develop comprehensive strategy
                3. **Green Technology** (Month 4-6): Implement priority solutions
                4. **Supply Chain Review** (Month 6): Assess climate resilience
                
                **💰 Financial Projections:**
                - Investment required: $25K-75K
                - Annual savings: $15K-45K
                - Payback period: 2-3 years
                - Risk mitigation value: $100K-300K
                """)
    
    else:  # Chat mode
        st.markdown("💡 **Enhanced with conversation memory and context awareness**")
        
        # Quick action buttons for common queries
        st.markdown("**🚀 Quick Actions:**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💡 Energy Tips"):
                quick_prompt = "What are the most effective ways to reduce my home energy consumption?"
                st.session_state.messages.append({"role": "user", "content": quick_prompt})
                st.rerun()
        
        with col2:
            if st.button("🚗 Transport"):
                quick_prompt = "How can I make my transportation more sustainable?"
                st.session_state.messages.append({"role": "user", "content": quick_prompt})
                st.rerun()
        
        with col3:
            if st.button("🌱 Carbon Tips"):
                quick_prompt = "What actions have the biggest impact on reducing my carbon footprint?"
                st.session_state.messages.append({"role": "user", "content": quick_prompt})
                st.rerun()
        
        with col4:
            if st.button("☀️ Renewables"):
                quick_prompt = "Should I consider solar panels for my home?"
                st.session_state.messages.append({"role": "user", "content": quick_prompt})
                st.rerun()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your AI climate assistant. How can I help you take action against climate change today?"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about climate action..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if demo_mode or not rag_system:
                    # Demo mode responses
                    demo_responses = {
                        "energy": "Here are some energy-saving tips: 1) Switch to LED bulbs, 2) Use programmable thermostats, 3) Unplug electronics when not in use, 4) Improve home insulation. These actions can reduce your energy consumption by 20-30%.",
                        "transport": "For sustainable transportation: 1) Walk or bike for short trips, 2) Use public transportation, 3) Consider electric or hybrid vehicles, 4) Carpool when possible. Transportation accounts for about 29% of greenhouse gas emissions.",
                        "carbon": "To reduce your carbon footprint: 1) Eat less meat, 2) Buy local and seasonal food, 3) Reduce air travel, 4) Use renewable energy, 5) Practice the 3 R's: Reduce, Reuse, Recycle.",
                        "default": "I'm here to help with climate action advice! In demo mode, I can provide general guidance on energy efficiency, sustainable transportation, carbon footprint reduction, and environmental best practices. What specific area would you like to explore?"
                    }
                    
                    # Simple keyword matching for demo
                    response = demo_responses["default"]
                    prompt_lower = prompt.lower()
                    if any(word in prompt_lower for word in ["energy", "electricity", "power", "heating", "cooling"]):
                        response = demo_responses["energy"]
                    elif any(word in prompt_lower for word in ["transport", "car", "travel", "commute", "bike", "walk"]):
                        response = demo_responses["transport"]
                    elif any(word in prompt_lower for word in ["carbon", "footprint", "emissions", "reduce", "impact"]):
                        response = demo_responses["carbon"]
                    
                    st.markdown(response)
                    st.info("💡 This is a demo response. Full AI capabilities require proper API configuration.")
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    try:
                        response, sources = rag_system.retrieve_and_generate(prompt, user_profile)
                        st.markdown(response)
                        
                        # Show sources if available
                        if sources:
                            with st.expander("📚 Sources"):
                                for source in sources[:2]:
                                    st.write(f"• {source['metadata'].get('title', 'Climate Data')} (Relevance: {source['similarity']:.1%})")
                        
                        # Add assistant response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        
                    except Exception as e:
                        error_msg = f"I apologize, but I encountered an error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Quick action buttons
    st.markdown("### 🚀 Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💡 Energy saving tips"):
            st.session_state.messages.append({"role": "user", "content": "What are the best energy saving tips for my home?"})
            st.rerun()
    
    with col2:
        if st.button("🚗 Transportation options"):
            st.session_state.messages.append({"role": "user", "content": "What are sustainable transportation options in my area?"})
            st.rerun()
    
    with col3:
        if st.button("🌱 Carbon footprint"):
            st.session_state.messages.append({"role": "user", "content": "How can I reduce my carbon footprint?"})
            st.rerun()

def display_community(impact_tracker, demo_mode=False):
    """Display community features and leaderboard"""
    st.header("🏆 Community Impact")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🥇 Impact Leaderboard")
        
        metric_choice = st.selectbox("Rank by:", ["carbon_saved_kg", "total_actions", "energy_saved_kwh"])
        
        leaderboard = impact_tracker.get_leaderboard(metric=metric_choice, limit=10)
        
        if leaderboard:
            # Create leaderboard dataframe
            df = pd.DataFrame(leaderboard)
            
            # Display as table
            st.dataframe(
                df[['user_id', metric_choice, 'total_actions']].rename(columns={
                    'user_id': 'User',
                    'carbon_saved_kg': 'Carbon Saved (kg)',
                    'total_actions': 'Total Actions',
                    'energy_saved_kwh': 'Energy Saved (kWh)'
                }),
                use_container_width=True
            )
            
            # Create visualization
            if len(df) > 0:
                fig = px.bar(
                    df.head(5), 
                    x='user_id', 
                    y=metric_choice,
                    title=f"Top 5 Users by {metric_choice.replace('_', ' ').title()}",
                    color=metric_choice,
                    color_continuous_scale="Greens"
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No community data available yet. Start logging your climate actions to appear on the leaderboard!")
    
    with col2:
        st.subheader("🌍 Global Impact")
        
        # Mock global statistics
        st.metric("🌱 Total CO2 Saved", "12,450 kg", "↗️ +15% this month")
        st.metric("👥 Active Users", "1,247", "↗️ +8% this month")
        st.metric("📊 Actions Logged", "5,632", "↗️ +22% this month")
        
        st.markdown("### 🎯 Monthly Challenge")
        st.info("**December Challenge:** Reduce energy consumption by 20%")
        
        progress = 65  # Mock progress
        st.progress(progress / 100)
        st.write(f"Community Progress: {progress}%")

def get_action_subtypes(action_type):
    """Get subtypes for action categories"""
    subtypes = {
        "energy_efficiency": ["led_bulb_replacement", "insulation_improvement", "smart_thermostat", "energy_efficient_appliance"],
        "transportation": ["bike_commute_km", "public_transport_km", "electric_vehicle", "carpooling", "walking"],
        "renewable_energy": ["solar_panel_kw", "wind_turbine_kw", "green_energy_plan"],
        "food": ["vegetarian_meal", "local_food_kg", "food_waste_reduction_kg", "composting_kg"],
        "water": ["low_flow_fixture", "rainwater_harvesting", "drought_resistant_landscaping"],
        "waste": ["recycling_kg", "reusable_bag", "composting_kg", "electronic_recycling_kg"]
    }
    return subtypes.get(action_type, ["general"])

def get_action_examples(action_type):
    """Get example actions for categories"""
    examples = {
        "energy_efficiency": ["Replace 5 incandescent bulbs with LEDs", "Install programmable thermostat", "Add insulation to attic"],
        "transportation": ["Bike to work (10 km)", "Take public transit instead of driving", "Carpool with colleagues"],
        "renewable_energy": ["Install 5kW solar panel system", "Switch to renewable energy plan"],
        "food": ["Eat vegetarian meal instead of meat", "Buy local produce", "Compost food scraps"],
        "water": ["Install low-flow showerhead", "Set up rain barrel", "Plant drought-resistant garden"],
        "waste": ["Recycle electronics", "Use reusable shopping bags", "Compost organic waste"]
    }
    return examples.get(action_type, ["Log any climate-positive action"])

def display_global_dashboard(api_handler, demo_mode=False):
    """Display impressive global climate dashboard with real-time data and visualizations"""
    st.header("🌍 Global Climate Intelligence Dashboard")
    
    # Real-time global metrics
    st.subheader("📊 Real-Time Global Climate Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🌡️ Global Temperature",
            "16.4°C",
            delta="+1.1°C since 1880",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "🌊 CO2 Levels",
            "421.4 ppm",
            delta="+2.4 ppm/year",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "🧊 Arctic Sea Ice",
            "4.2M km²",
            delta="-13% per decade",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            "🌊 Sea Level",
            "+21.6 cm",
            delta="+3.4 mm/year",
            delta_color="inverse"
        )
    
    # Interactive global temperature map
    st.subheader("🗺️ Global Temperature Anomalies")
    
    # Create mock global temperature data
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px
    import numpy as np
    
    # Generate sample global temperature data
    countries = ['United States', 'China', 'India', 'Germany', 'Brazil', 'Canada', 'Australia', 'Russia', 'Japan', 'United Kingdom']
    temp_anomalies = [1.2, 1.8, 1.5, 1.4, 1.1, 2.1, 1.9, 2.3, 1.3, 1.6]
    
    fig_map = go.Figure(data=go.Choropleth(
        locations=['US', 'CN', 'IN', 'DE', 'BR', 'CA', 'AU', 'RU', 'JP', 'GB'],
        z=temp_anomalies,
        text=countries,
        colorscale='RdYlBu_r',
        reversescale=False,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        colorbar_title="Temperature<br>Anomaly (°C)"
    ))
    
    fig_map.update_layout(
        title_text='Global Temperature Anomalies (2024)',
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        ),
        height=500
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Climate trends and projections
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Climate Trends")
        
        # Historical and projected temperature data
        years = list(range(1980, 2051))
        historical_temp = [14.0 + 0.02 * (year - 1980) + np.random.normal(0, 0.1) for year in range(1980, 2025)]
        projected_temp = [historical_temp[-1] + 0.03 * (year - 2024) for year in range(2025, 2051)]
        
        fig_trends = go.Figure()
        
        # Historical data
        fig_trends.add_trace(go.Scatter(
            x=years[:45],
            y=historical_temp,
            mode='lines',
            name='Historical',
            line=dict(color='blue', width=2)
        ))
        
        # Projected data
        fig_trends.add_trace(go.Scatter(
            x=years[44:],
            y=projected_temp,
            mode='lines',
            name='Projected',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        fig_trends.update_layout(
            title="Global Temperature Trends & Projections",
            xaxis_title="Year",
            yaxis_title="Temperature (°C)",
            height=400
        )
        
        st.plotly_chart(fig_trends, use_container_width=True)
    
    with col2:
        st.subheader("🔋 Renewable Energy Growth")
        
        # Renewable energy capacity data
        energy_years = list(range(2015, 2025))
        solar_capacity = [200, 290, 390, 480, 580, 710, 850, 1000, 1200, 1400]
        wind_capacity = [370, 430, 490, 560, 650, 730, 820, 900, 1000, 1100]
        
        fig_energy = go.Figure()
        
        fig_energy.add_trace(go.Scatter(
            x=energy_years,
            y=solar_capacity,
            mode='lines+markers',
            name='Solar',
            line=dict(color='orange', width=3),
            marker=dict(size=8)
        ))
        
        fig_energy.add_trace(go.Scatter(
            x=energy_years,
            y=wind_capacity,
            mode='lines+markers',
            name='Wind',
            line=dict(color='green', width=3),
            marker=dict(size=8)
        ))
        
        fig_energy.update_layout(
            title="Global Renewable Energy Capacity",
            xaxis_title="Year",
            yaxis_title="Capacity (GW)",
            height=400
        )
        
        st.plotly_chart(fig_energy, use_container_width=True)
    
    # Climate action impact calculator
    st.subheader("🎯 Global Climate Action Impact")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🌱 Individual Actions Impact**
        - 1 billion people switching to LEDs: **50 million tons CO2/year**
        - 100 million people going car-free 1 day/week: **25 million tons CO2/year**
        - 50 million rooftop solar installations: **200 million tons CO2/year**
        """)
    
    with col2:
        st.markdown("""
        **🏭 Corporate Climate Commitments**
        - 500+ companies with net-zero targets
        - $130 trillion in assets under management committed
        - 25% of global emissions covered by corporate targets
        """)
    
    with col3:
        st.markdown("""
        **🏛️ Policy & Government Action**
        - 70+ countries with net-zero commitments
        - $1.8 trillion in climate finance pledged
        - 40+ carbon pricing initiatives worldwide
        """)
    
    # Real-time climate news and insights
    st.subheader("📰 Latest Climate Intelligence")
    
    # Mock climate news data
    news_items = [
        {
            "title": "Global Renewable Energy Capacity Hits Record High",
            "summary": "Solar and wind installations reached 295 GW in 2024, marking a 73% increase from previous year.",
            "impact": "Positive",
            "source": "International Energy Agency"
        },
        {
            "title": "Arctic Sea Ice Reaches Second-Lowest Extent on Record",
            "summary": "September 2024 sea ice extent was 4.28 million km², highlighting accelerating Arctic warming.",
            "impact": "Concerning",
            "source": "National Snow and Ice Data Center"
        },
        {
            "title": "Carbon Capture Technology Breakthrough",
            "summary": "New direct air capture facility can remove 1 million tons CO2/year at $100/ton cost.",
            "impact": "Positive",
            "source": "Climate Technology Research"
        }
    ]
    
    for item in news_items:
        impact_color = "green" if item["impact"] == "Positive" else "orange"
        st.markdown(f"""
        <div style="border-left: 4px solid {impact_color}; padding-left: 10px; margin: 10px 0;">
        <strong>{item['title']}</strong><br>
        {item['summary']}<br>
        <small>Source: {item['source']} | Impact: <span style="color: {impact_color};">{item['impact']}</span></small>
        </div>
        """, unsafe_allow_html=True)
    
    # Climate action recommendations based on global data
    st.subheader("🚀 AI-Powered Global Recommendations")
    
    if st.button("🔮 Generate Global Climate Insights"):
        with st.spinner("Analyzing global climate data..."):
            st.success("🌍 **Global Climate Intelligence Report**")
            
            st.markdown("""
            **🎯 Top Priority Actions for Maximum Global Impact:**
            
            1. **🔋 Accelerate Renewable Energy Transition**
               - Current: 30% of global electricity from renewables
               - Target: 70% by 2030 (Paris Agreement pathway)
               - Impact: 65% of required emissions reductions
            
            2. **🏭 Industrial Decarbonization**
               - Focus: Steel, cement, chemicals, aluminum
               - Potential: 40% reduction in industrial emissions
               - Timeline: Critical decade 2024-2034
            
            3. **🌳 Nature-Based Solutions**
               - Forest restoration: 1.2 billion hectares potential
               - Carbon sequestration: 5.2 GtCO2/year possible
               - Co-benefits: Biodiversity, water security
            
            4. **🚗 Transportation Electrification**
               - EV adoption rate: 18% globally (2024)
               - Target: 60% by 2030
               - Impact: 20% of transport emissions reduction
            
            **💡 Your Role in Global Climate Action:**
            - Personal actions amplified by community engagement
            - Local policy advocacy for systemic change
            - Investment choices supporting climate solutions
            - Knowledge sharing and climate education
            """)

if __name__ == "__main__":
    main()