# 🌍 AI-NEO Asteroid Risk Analysis

An AI-powered Near-Earth Object (NEO) risk prediction system using machine learning to assess asteroid collision threats.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![React](https://img.shields.io/badge/React-18-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Features

### Core Functionality
- **ML Risk Prediction** - RandomForest classifier predicting Low/Medium/High risk levels
- **NASA API Integration** - Real-time asteroid data from NASA's NEO Web Service
- **Batch Predictions** - Process multiple asteroids simultaneously
- **Historical Comparison** - Compare to Chelyabinsk, Tunguska, and other impacts

### Advanced Features
- **Mitigation Recommendations** - Kinetic impactor, gravity tractor, and other strategies
- **Uncertainty Quantification** - Confidence intervals for predictions
- **Alert System** - Webhook notifications for high-risk detections
- **Prediction History** - SQLite database with analytics

### Frontend Dashboard
- **Mission Control UI** - Dark space theme with glassmorphism design
- **Interactive Forms** - Real-time risk assessment
- **Data Visualization** - Stats, charts, and risk gauges
- **Mobile Responsive** - Works on all devices

## 📁 Project Structure

```
Ai-Neo-asteroid-risk-analysis/
├── src/
│   ├── api/
│   │   └── main.py              # FastAPI application
│   ├── data/
│   │   ├── generate_data.py     # Synthetic data generator
│   │   └── nasa_client.py       # NASA NEO API client
│   ├── model/
│   │   └── train_model.py       # ML model training
│   ├── database/
│   │   ├── models.py            # SQLAlchemy models
│   │   └── connection.py        # Database connection
│   ├── features/
│   │   ├── uncertainty.py       # Uncertainty quantification
│   │   ├── mitigation.py        # Mitigation strategies
│   │   ├── alerts.py            # Alert system
│   │   └── historical.py        # Historical impacts
│   └── utils/
│       ├── config.py            # Configuration management
│       └── logging.py           # Structured logging
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main React component
│   │   ├── App.css              # Component styles
│   │   └── index.css            # Design system
│   └── package.json
├── tests/
│   ├── test_api.py              # API tests
│   └── test_features.py         # Feature tests
├── .github/workflows/ci.yml     # CI/CD pipeline
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose
├── requirements.txt             # Python dependencies
└── README.md
```

## 🛠️ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- NASA API Key (optional, uses DEMO_KEY by default)

### Backend Setup

```bash
# Clone repository
git clone https://github.com/Shanks2126/Ai-Neo-asteroid-risk-analysis.git
cd Ai-Neo-asteroid-risk-analysis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Generate training data
python src/data/generate_data.py

# Train model
python src/model/train_model.py

# Start API server
uvicorn src.api.main:app --reload
```

API available at: http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Dashboard available at: http://localhost:5173

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info and status |
| GET | `/health` | Health check |
| POST | `/predict` | Single prediction |
| POST | `/predict/batch` | Batch predictions |
| GET | `/predictions/history` | Prediction history |
| GET | `/stats` | Analytics statistics |

### Example Request

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "distance_km": 500000,
    "velocity_kms": 15,
    "diameter_m": 100,
    "trajectory_angle_deg": 30,
    "asteroid_name": "2024 AB1"
  }'
```

### Example Response

```json
{
  "risk_level": "Medium",
  "impact_probability": 0.4523,
  "confidence": 0.85,
  "input_summary": {
    "distance_km": 500000,
    "velocity_kms": 15,
    "diameter_m": 100,
    "trajectory_angle_deg": 30,
    "asteroid_name": "2024 AB1"
  },
  "predicted_at": "2024-01-15T10:30:00Z",
  "model_version": "2.0.0"
}
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📊 Model Details

### Input Features
| Feature | Range | Description |
|---------|-------|-------------|
| `distance_km` | 100 - 400M km | Distance from Earth |
| `velocity_kms` | 0.1 - 72 km/s | Relative velocity |
| `diameter_m` | 1 - 1M m | Asteroid diameter |
| `trajectory_angle_deg` | 0° - 90° | 0° = direct hit |

### Output
- **Risk Level**: Low, Medium, or High
- **Impact Probability**: 0.0 - 1.0
- **Confidence Score**: Model certainty

## 🛡️ Mitigation Strategies

The system recommends deflection methods based on asteroid parameters:

| Strategy | Best For | Warning Time |
|----------|----------|--------------|
| Kinetic Impactor | < 500m | 1-10 years |
| Gravity Tractor | < 200m | 10-20 years |
| Nuclear Standoff | > 500m or emergency | < 6 months |
| Monitoring | Low risk | N/A |

## 🔗 Links

- **API Docs**: http://localhost:8000/docs
- **NASA NEO API**: https://api.nasa.gov/
- **DART Mission**: https://dart.jhuapl.edu/

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 👥 Contributors

- Shanks2126 - Original Author
- shairazs - Feature Implementation

---

Made with 🚀 for planetary defense
