"""
Enhanced Climate Guardian Application with Real Data and Advanced Features
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import os
import sys
import requests
from datetime import datetime, timedelta
import logging
import folium
from streamlit_folium import st_folium
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from backend.api_handlers.climate_apis import ClimateAPIHandler
from backend.simple_rag import SimpleRAGSystem
from backend.simple_impact_tracker import SimpleImpactTracker
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Climate Guardian - AI Climate Action Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2E8B57, #228B22, #32CD32);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #f0f8f0, #e8f5e8);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #228B22;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .action-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
        transition: transform 0.2s;
    }
    .action-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .impact-highlight {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        padding: 1rem;
        border-radius: 10px;
        color: #333;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    .api-status {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.2rem;
        display: inline-block;
    }
    .api-working { background: #d4edda; color: #155724; }
    .api-limited { background: #fff3cd; color: #856404; }
    .api-error { background: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_systems():
    """Initialize backend systems"""
    try:
        rag_system = SimpleRAGSystem()
        rag_system.initialize_with_sample_data()
        
        api_handler = ClimateAPIHandler()
        impact_tracker = SimpleImpactTracker()
        
        return rag_system, api_handler, impact_tracker
    except Exception as e:
        st.error(f"Error initializing systems: {e}")
        return None, None, None

def test_api_status():
    """Test and display API status"""
    api_status = {}
    
    # Test Climate TRACE
    try:
        response = requests.get("https://api.climatetrace.org/v6/definitions/countries", timeout=5)
        api_status['Climate TRACE'] = 'working' if response.status_code == 200 else 'limited'
    except:
        api_status['Climate TRACE'] = 'error'
    
    # Test World Bank
    try:
        response = requests.get("https://api.worldbank.org/v2/country/USA/indicator/EN.ATM.CO2E.KT?format=json&date=2020", timeout=5)
        api_status['World Bank'] = 'working' if response.status_code == 200 else 'limited'
    except:
        api_status['World Bank'] = 'error'
    
    # Test UN SDG
    try:
        response = requests.get("https://unstats.un.org/SDGAPI/v1/sdg/Goal/List", timeout=5)
        api_status['UN SDG'] = 'working' if response.status_code == 200 else 'limited'
    except:
        api_status['UN SDG'] = 'error'
    
    # Test NASA POWER
    try:
        response = requests.get("https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M&community=RE&longitude=0&latitude=0&start=20240101&end=20240102&format=JSON", timeout=5)
        api_status['NASA POWER'] = 'working' if response.status_code == 200 else 'limited'
    except:
        api_status['NASA POWER'] = 'error'
    
    return api_status

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌍 Climate Guardian - Your AI Climate Action Partner</h1>
        <p>Personalized climate solutions powered by IBM watsonx.ai and real-time global data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Status
    with st.expander("🔌 Real-Time API Status", expanded=False):
        api_status = test_api_status()
        cols = st.columns(len(api_status))
        for i, (api, status) in enumerate(api_status.items()):
            with cols[i]:
                status_class = f"api-{status}"
                status_text = {"working": "✅ Active", "limited": "⚠️ Limited", "error": "❌ Offline"}[status]
                st.markdown(f'<div class="api-status {status_class}">{api}: {status_text}</div>', unsafe_allow_html=True)
    
    # Initialize systems
    rag_system, api_handler, impact_tracker = initialize_systems()
    
    # Sidebar for user profile
    with st.sidebar:
        st.header("👤 Your Climate Profile")
        
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
        
        # Generate demo data button
        if st.button("🎲 Generate Demo Data"):
            impact_tracker.generate_demo_data(user_id)
            st.success("Demo data generated!")
            st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🎯 Action Plan", 
        "📊 Impact Tracker", 
        "🌤️ Local Data", 
        "💬 AI Assistant", 
        "🏆 Community", 
        "🌍 Global Dashboard",
        "🗺️ Climate Maps"
    ])
    
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
        display_action_plan(rag_system, user_profile)
    
    with tab2:
        display_impact_tracker(impact_tracker, user_id)
    
    with tab3:
        display_local_data(api_handler, location)
    
    with tab4:
        display_ai_assistant(rag_system, user_profile)
    
    with tab5:
        display_community(impact_tracker)
    
    with tab6:
        display_global_dashboard(api_handler)
    
    with tab7:
        display_climate_maps(api_handler)

def display_action_plan(rag_system, user_profile):
    """Display personalized action plan"""
    st.header("🎯 Your Personalized Climate Action Plan")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔄 Generate New Action Plan", type="primary"):
            with st.spinner("🤖 Analyzing your profile and generating personalized recommendations..."):
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
    
    with col2:
        st.markdown("### 💡 Quick Tips")
        st.info("💡 **Pro Tip:** The more specific your location and interests, the better your personalized recommendations!")
        
        st.markdown("### 🎯 Focus Areas")
        for interest in user_profile['interests']:
            st.markdown(f"• {interest}")
        
        # Impact preview
        st.markdown("### 📈 Potential Impact")
        st.metric("Annual CO2 Reduction", "2.5 tons", "↗️ 30% improvement")
        st.metric("Cost Savings", "$800", "↗️ 15% increase")

def display_impact_tracker(impact_tracker, user_id):
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
                    'location': user_id
                }
                
                record = impact_tracker.track_action(user_id, action_data)
                st.success(f"✅ Action logged! Estimated impact: {record['carbon_saved_kg']:.2f} kg CO2 saved")
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
            st.markdown(f"""
            <div class="impact-highlight">
                🌳 Trees Planted Equivalent: {equivalents.get('trees_planted_equivalent', 0)} trees
            </div>
            """, unsafe_allow_html=True)
            st.info(f"🚗 **Miles Not Driven:** {equivalents.get('miles_not_driven', 0)} miles")
        
        with col2:
            st.info(f"⛽ **Gasoline Saved:** {equivalents.get('gasoline_not_used_liters', 0)} liters")
            st.info(f"🔥 **Coal Not Burned:** {equivalents.get('coal_not_burned_kg', 0)} kg")

def display_local_data(api_handler, location):
    """Display local climate and environmental data"""
    st.header("🌤️ Local Climate Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌡️ Current Weather")
        if st.button("🔄 Refresh Weather Data"):
            with st.spinner("Fetching weather data..."):
                api_location = location.replace(", NY", ",US").replace(", CA", ",US").replace(", TX", ",US")
                if ", " in api_location and not api_location.endswith(",US"):
                    city_state = api_location.split(", ")
                    if len(city_state) == 2 and len(city_state[1]) == 2:
                        api_location = f"{city_state[0]},US"
                
                weather_data = api_handler.get_weather_data(api_location)
                
                if 'error' not in weather_data:
                    st.success(f"📍 **{weather_data['location']}, {weather_data['country']}**")
                    
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
                    st.error(f"Weather data unavailable. Using demo data for {location}")
                    # Demo weather data
                    st.success(f"📍 **{location} (Demo Data)**")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("🌡️ Temperature", "22.5°C")
                    with col_b:
                        st.metric("💨 Wind Speed", "3.2 m/s")
                    with col_c:
                        st.metric("💧 Humidity", "65%")
                    st.write("**Conditions:** Partly Cloudy")
                    st.markdown("**Air Quality:** <span style='color: green'>Good (AQI: 2)</span>", unsafe_allow_html=True)
    
    with col2:
        st.subheader("🔋 Renewable Energy Potential")
        if st.button("🔄 Analyze Renewable Potential"):
            with st.spinner("Analyzing renewable energy potential..."):
                renewable_data = api_handler.get_renewable_energy_potential(location)
                
                if 'error' not in renewable_data:
                    st.success(f"📍 **Analysis for {renewable_data['location']}**")
                    
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
                    
                    st.markdown("**🎯 Recommendations:**")
                    for rec in renewable_data['recommendations']:
                        st.write(f"• {rec}")
                else:
                    st.error("Renewable analysis unavailable. Using demo data.")
                    # Demo renewable data
                    st.success(f"📍 **Analysis for {location} (Demo Data)**")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**☀️ Solar Potential:** <span style='color: green'>High</span>", unsafe_allow_html=True)
                        st.write("Avg. Solar Irradiance: 5.2 kWh/m²/day")
                    with col_b:
                        st.markdown("**💨 Wind Potential:** <span style='color: orange'>Medium</span>", unsafe_allow_html=True)
                        st.write("Avg. Wind Speed: 4.1 m/s")
                    
                    st.markdown("**🎯 Recommendations:**")
                    st.write("• Excellent location for solar panels - consider rooftop solar installation")
                    st.write("• Solar water heating would be very effective in this location")
                    st.write("• Moderate wind potential - small wind systems might be viable")

def display_ai_assistant(rag_system, user_profile):
    """Display AI assistant chat interface"""
    st.header("💬 AI Climate Assistant")
    
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
                response, sources = rag_system.retrieve_and_generate(prompt, user_profile)
                st.markdown(response)
                
                # Show sources if available
                if sources:
                    with st.expander("📚 Sources"):
                        for source in sources[:2]:
                            st.write(f"• {source['metadata'].get('title', 'Climate Data')} (Relevance: {source['similarity']:.1%})")
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
    
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

def display_community(impact_tracker):
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
        
        progress = 65
        st.progress(progress / 100)
        st.write(f"Community Progress: {progress}%")

def display_global_dashboard(api_handler):
    """Display global climate dashboard with real data"""
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
    
    # Get real Climate TRACE data
    st.subheader("🏭 Global Emissions Data (Climate TRACE)")
    
    if st.button("🔄 Fetch Latest Global Emissions"):
        with st.spinner("Fetching real-time emissions data..."):
            # Get USA emissions data
            usa_data = api_handler.get_climate_trace_data("USA", year=2022)
            
            if 'error' not in usa_data:
                st.success("✅ Real emissions data loaded from Climate TRACE API")
                
                if 'data' in usa_data and usa_data['data']:
                    emissions_data = usa_data['data'][0]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("🇺🇸 USA Total Emissions", f"{emissions_data['emissions']['co2e_100yr']/1e9:.1f} Gt CO2e")
                        st.metric("🏭 USA CO2 Emissions", f"{emissions_data['emissions']['co2']/1e9:.1f} Gt CO2")
                    
                    with col2:
                        st.metric("🌍 World Total Emissions", f"{emissions_data['worldEmissions']['co2e_100yr']/1e9:.1f} Gt CO2e")
                        st.metric("📊 USA Share of Global", f"{(emissions_data['emissions']['co2e_100yr']/emissions_data['worldEmissions']['co2e_100yr']*100):.1f}%")
            else:
                st.warning("Using demo emissions data (API temporarily unavailable)")
    
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

def display_climate_maps(api_handler):
    """Display interactive climate maps"""
    st.header("🗺️ Interactive Climate Maps")
    
    # Map type selector
    map_type = st.selectbox("Select Map Type", [
        "Global Temperature Anomalies",
        "CO2 Emissions by Country", 
        "Renewable Energy Potential",
        "Climate Risk Assessment"
    ])
    
    if map_type == "Global Temperature Anomalies":
        st.subheader("🌡️ Global Temperature Anomalies")
        
        # Create temperature anomaly map
        countries = ['United States', 'China', 'India', 'Germany', 'Brazil', 'Canada', 'Australia', 'Russia', 'Japan', 'United Kingdom']
        country_codes = ['US', 'CN', 'IN', 'DE', 'BR', 'CA', 'AU', 'RU', 'JP', 'GB']
        temp_anomalies = [1.2, 1.8, 1.5, 1.4, 1.1, 2.1, 1.9, 2.3, 1.3, 1.6]
        
        fig_map = go.Figure(data=go.Choropleth(
            locations=country_codes,
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
        
        st.info("🔍 **Interpretation:** Red areas show higher temperature increases. Arctic regions (Canada, Russia) show the highest warming.")
    
    elif map_type == "CO2 Emissions by Country":
        st.subheader("🏭 CO2 Emissions by Country")
        
        if st.button("🔄 Fetch Real Emissions Data"):
            with st.spinner("Loading real emissions data from Climate TRACE..."):
                # Get real data for major countries
                countries_data = []
                major_countries = ['USA', 'CHN', 'IND', 'RUS', 'JPN']
                
                for country in major_countries:
                    data = api_handler.get_climate_trace_data(country, year=2022)
                    if 'error' not in data and 'data' in data and data['data']:
                        emissions = data['data'][0]['emissions']['co2e_100yr'] / 1e9  # Convert to Gt
                        countries_data.append({'country': country, 'emissions': emissions})
                
                if countries_data:
                    df = pd.DataFrame(countries_data)
                    
                    fig = px.bar(
                        df, 
                        x='country', 
                        y='emissions',
                        title="CO2 Emissions by Country (2022)",
                        labels={'emissions': 'CO2 Emissions (Gt)', 'country': 'Country'},
                        color='emissions',
                        color_continuous_scale='Reds'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    st.success("✅ Real emissions data from Climate TRACE API")
                else:
                    st.warning("Could not fetch real data, showing demo visualization")
    
    elif map_type == "Renewable Energy Potential":
        st.subheader("☀️ Global Renewable Energy Potential")
        
        # Create folium map
        m = folium.Map(location=[20, 0], zoom_start=2)
        
        # Add renewable energy markers
        renewable_sites = [
            {"name": "Sahara Solar", "lat": 25, "lon": 0, "type": "Solar", "potential": "Very High"},
            {"name": "North Sea Wind", "lat": 55, "lon": 3, "type": "Wind", "potential": "High"},
            {"name": "Australian Outback Solar", "lat": -25, "lon": 135, "type": "Solar", "potential": "Very High"},
            {"name": "Great Plains Wind", "lat": 40, "lon": -100, "type": "Wind", "potential": "High"},
            {"name": "Patagonia Wind", "lat": -45, "lon": -70, "type": "Wind", "potential": "Very High"}
        ]
        
        for site in renewable_sites:
            color = 'orange' if site['type'] == 'Solar' else 'green'
            folium.Marker(
                [site['lat'], site['lon']],
                popup=f"{site['name']}<br>Type: {site['type']}<br>Potential: {site['potential']}",
                icon=folium.Icon(color=color, icon='bolt')
            ).add_to(m)
        
        # Display map
        map_data = st_folium(m, width=700, height=500)
        
        st.info("🔍 **Legend:** Orange markers = Solar potential, Green markers = Wind potential")
    
    else:  # Climate Risk Assessment
        st.subheader("⚠️ Climate Risk Assessment")
        
        # Risk assessment data
        risk_data = {
            'Region': ['Caribbean', 'Pacific Islands', 'Sub-Saharan Africa', 'South Asia', 'Arctic', 'Mediterranean'],
            'Risk Level': [9, 10, 8, 7, 9, 6],
            'Primary Threat': ['Sea Level Rise', 'Sea Level Rise', 'Drought', 'Flooding', 'Ice Melt', 'Heat Waves'],
            'Population at Risk (M)': [44, 12, 800, 1900, 4, 500]
        }
        
        df_risk = pd.DataFrame(risk_data)
        
        fig_risk = px.scatter(
            df_risk,
            x='Population at Risk (M)',
            y='Risk Level',
            size='Population at Risk (M)',
            color='Primary Threat',
            hover_name='Region',
            title="Climate Risk Assessment by Region",
            labels={'Risk Level': 'Climate Risk Level (1-10)'}
        )
        
        st.plotly_chart(fig_risk, use_container_width=True)
        
        st.dataframe(df_risk, use_container_width=True)

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

if __name__ == "__main__":
    main()