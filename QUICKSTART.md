# 🚀 Quick Start Guide - Climate Action Intelligence Platform

## 30-Second Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test Installation
```bash
python test_installation.py
```

### 3. Run the Application
```bash
python run_app.py
```

### 4. Open in Browser
- **Local**: http://localhost:12000
- **Network**: https://work-1-fvctichmsizgqcpl.prod-runtime.all-hands.dev

## 🎯 Demo Mode (No API Keys Required)

The platform works perfectly in demo mode! You can:
- ✅ Explore all features
- ✅ Generate action plans
- ✅ View impact tracking
- ✅ Chat with AI assistant
- ✅ See local data visualizations

## 🔑 Full Functionality (Optional)

For real-time data, add API keys to `.env`:

```env
# IBM watsonx.ai (for advanced AI)
IBM_CLOUD_API_KEY=your_key_here
WATSONX_PROJECT_ID=your_project_id

# Climate APIs (for real data)
OPENWEATHER_API_KEY=your_key_here
CARBON_INTERFACE_API_KEY=your_key_here
NASA_API_KEY=your_key_here
```

## 🎮 How to Use

1. **Set Your Profile** (sidebar):
   - Location: "New York, NY"
   - Lifestyle: Urban/Suburban/Rural
   - Interests: Energy, Transportation, etc.

2. **Generate Action Plan**:
   - Click "Generate New Action Plan"
   - Get personalized recommendations
   - See impact estimates

3. **Track Your Impact**:
   - Log your climate actions
   - View progress charts
   - Compare with community

4. **Chat with AI**:
   - Ask climate questions
   - Get personalized advice
   - Use quick action buttons

## 🏆 Key Features to Showcase

- **🤖 AI-Powered**: IBM watsonx.ai integration
- **📊 Real-Time Data**: Multiple climate APIs
- **🎯 Personalized**: Location-based recommendations
- **📈 Impact Tracking**: Quantified environmental benefits
- **🌍 Community**: Collaborative climate action

## 🆘 Troubleshooting

**Port already in use?**
```bash
pkill -f streamlit
python run_app.py
```

**Missing dependencies?**
```bash
pip install -r requirements.txt
```

**API errors?**
- Demo mode works without any APIs
- Check `.env` file for API keys
- Verify internet connection

---

**Ready to win! 🏆 Your Climate Action Intelligence Platform is running!**