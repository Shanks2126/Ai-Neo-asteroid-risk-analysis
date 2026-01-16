import { useState, useEffect } from 'react'
import './App.css'
import EarthViewer from './components/EarthViewer'
import './components/EarthViewer.css'

// API Configuration
const API_URL = '/api'

function App() {
    const [prediction, setPrediction] = useState(null)
    const [loading, setLoading] = useState(false)
    const [stats, setStats] = useState(null)
    const [history, setHistory] = useState([])

    // Form state
    const [formData, setFormData] = useState({
        distance_km: 500000,
        velocity_kms: 15,
        diameter_m: 100,
        trajectory_angle_deg: 30,
        asteroid_name: ''
    })

    // Fetch stats on mount
    useEffect(() => {
        fetchStats()
        fetchHistory()
    }, [])

    const fetchStats = async () => {
        try {
            const res = await fetch(`${API_URL}/stats`)
            const data = await res.json()
            setStats(data)
        } catch (err) {
            console.error('Failed to fetch stats:', err)
        }
    }

    const fetchHistory = async () => {
        try {
            const res = await fetch(`${API_URL}/predictions/history?limit=10`)
            const data = await res.json()
            setHistory(data.predictions || [])
        } catch (err) {
            console.error('Failed to fetch history:', err)
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)

        try {
            const res = await fetch(`${API_URL}/predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            })
            const data = await res.json()
            setPrediction(data)
            fetchStats()
            fetchHistory()
        } catch (err) {
            console.error('Prediction failed:', err)
        } finally {
            setLoading(false)
        }
    }

    const handleDelete = async (id) => {
        if (!id) return
        try {
            await fetch(`${API_URL}/predictions/${id}`, { method: 'DELETE' })
            fetchStats()
            fetchHistory()
        } catch (err) {
            console.error('Delete failed:', err)
        }
    }

    const handleInputChange = (e) => {
        const { name, value } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: name === 'asteroid_name' ? value : parseFloat(value)
        }))
    }

    const getRiskColor = (level) => {
        switch (level) {
            case 'Low': return 'var(--color-risk-low)'
            case 'Medium': return 'var(--color-risk-medium)'
            case 'High': return 'var(--color-risk-high)'
            default: return 'var(--color-text-secondary)'
        }
    }

    return (
        <div className="app">
            {/* Header */}
            <header className="header container">
                <div className="logo">
                    <div className="logo-icon">🌍</div>
                    <span>NEO Risk</span>
                </div>
                <nav className="nav">
                    <a href="#dashboard">Dashboard</a>
                    <a href="#predict">Predict</a>
                    <a href="#history">History</a>
                </nav>
            </header>

            <main className="container">
                {/* Hero Section */}
                <section className="hero">
                    <h1>Asteroid Threat Assessment</h1>
                    <p className="hero-subtitle">
                        AI-powered Near-Earth Object risk prediction system
                    </p>
                </section>

                {/* Stats Grid */}
                <section id="dashboard" className="section">
                    <h2 className="section-title">Mission Control</h2>
                    <div className="grid grid-cols-4">
                        <div className="card stat-card">
                            <div className="stat-value">{stats?.total_predictions || 0}</div>
                            <div className="stat-label">Total Predictions</div>
                        </div>
                        <div className="card stat-card">
                            <div className="stat-value" style={{ color: 'var(--color-risk-low)' }}>
                                {stats?.by_risk_level?.Low || 0}
                            </div>
                            <div className="stat-label">Low Risk</div>
                        </div>
                        <div className="card stat-card">
                            <div className="stat-value" style={{ color: 'var(--color-risk-medium)' }}>
                                {stats?.by_risk_level?.Medium || 0}
                            </div>
                            <div className="stat-label">Medium Risk</div>
                        </div>
                        <div className="card stat-card">
                            <div className="stat-value" style={{ color: 'var(--color-risk-high)' }}>
                                {stats?.by_risk_level?.High || 0}
                            </div>
                            <div className="stat-label">High Risk</div>
                        </div>
                    </div>
                </section>

                {/* 3D Earth Visualization */}
                <section className="section">
                    <h2 className="section-title">🌍 Near-Earth Object Tracker</h2>
                    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                        <EarthViewer
                            asteroids={history}
                            onAsteroidClick={(ast) => console.log('Clicked:', ast)}
                        />
                    </div>
                </section>

                {/* Prediction Form */}
                <section id="predict" className="section">
                    <div className="grid grid-cols-2">
                        <div className="card">
                            <h3 className="card-title">Risk Assessment</h3>
                            <form onSubmit={handleSubmit} className="form">
                                <div className="form-group">
                                    <label className="input-label">Asteroid Name (Optional)</label>
                                    <input
                                        type="text"
                                        name="asteroid_name"
                                        value={formData.asteroid_name}
                                        onChange={handleInputChange}
                                        placeholder="e.g., 2024 AB1"
                                        className="input"
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="input-label">Distance from Earth (km)</label>
                                    <input
                                        type="number"
                                        name="distance_km"
                                        value={formData.distance_km}
                                        onChange={handleInputChange}
                                        min="100"
                                        max="400000000"
                                        required
                                        className="input"
                                    />
                                    <span className="input-hint">Range: 100 - 400,000,000 km</span>
                                </div>

                                <div className="form-group">
                                    <label className="input-label">Velocity (km/s)</label>
                                    <input
                                        type="number"
                                        name="velocity_kms"
                                        value={formData.velocity_kms}
                                        onChange={handleInputChange}
                                        min="0.1"
                                        max="72"
                                        step="0.1"
                                        required
                                        className="input"
                                    />
                                    <span className="input-hint">Typical: 5 - 40 km/s</span>
                                </div>

                                <div className="form-group">
                                    <label className="input-label">Diameter (meters)</label>
                                    <input
                                        type="number"
                                        name="diameter_m"
                                        value={formData.diameter_m}
                                        onChange={handleInputChange}
                                        min="1"
                                        max="1000000"
                                        required
                                        className="input"
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="input-label">Trajectory Angle (°)</label>
                                    <input
                                        type="range"
                                        name="trajectory_angle_deg"
                                        value={formData.trajectory_angle_deg}
                                        onChange={handleInputChange}
                                        min="0"
                                        max="90"
                                        className="input-range"
                                    />
                                    <div className="range-labels">
                                        <span>0° (Direct Hit)</span>
                                        <span>{formData.trajectory_angle_deg}°</span>
                                        <span>90° (Tangent)</span>
                                    </div>
                                </div>

                                <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                                    {loading ? '🔄 Analyzing...' : '🔍 Analyze Risk'}
                                </button>
                            </form>
                        </div>

                        {/* Prediction Result */}
                        <div className="card card-glass result-card">
                            <h3 className="card-title">Prediction Result</h3>
                            {prediction ? (
                                <div className="result animate-fadeIn">
                                    <div className="risk-display">
                                        <div
                                            className="risk-level"
                                            style={{ color: getRiskColor(prediction.risk_level) }}
                                        >
                                            {prediction.risk_level === 'High' && '⚠️ '}
                                            {prediction.risk_level}
                                        </div>
                                        <div className={`risk-badge risk-badge-${prediction.risk_level.toLowerCase()}`}>
                                            {prediction.risk_level} Risk
                                        </div>
                                    </div>

                                    <div className="result-stats">
                                        <div className="result-stat">
                                            <span className="result-stat-label">Miss Chance</span>
                                            <span className="result-stat-value">
                                                {((1 - prediction.impact_probability) * 100).toFixed(2)}%
                                            </span>
                                        </div>
                                        <div className="result-stat">
                                            <span className="result-stat-label">Model Confidence</span>
                                            <span className="result-stat-value">
                                                {(prediction.confidence * 100).toFixed(1)}%
                                            </span>
                                        </div>
                                        <div className="result-stat">
                                            <span className="result-stat-label">Model Version</span>
                                            <span className="result-stat-value">{prediction.model_version}</span>
                                        </div>
                                    </div>

                                    {prediction.risk_level === 'High' && (
                                        <div className="alert alert-danger">
                                            ⚠️ High risk detected! This asteroid requires immediate attention.
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="result-placeholder">
                                    <div className="placeholder-icon">🛸</div>
                                    <p>Enter asteroid parameters and click Analyze to get risk prediction</p>
                                </div>
                            )}
                        </div>
                    </div>
                </section>

                {/* History */}
                <section id="history" className="section">
                    <h2 className="section-title">Recent Predictions</h2>
                    <div className="table-container card">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Asteroid</th>
                                    <th>Distance (km)</th>
                                    <th>Diameter (m)</th>
                                    <th>Risk</th>
                                    <th>Probability</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {history.length > 0 ? history.map((pred, idx) => (
                                    <tr key={pred.id || idx} className="animate-fadeIn" style={{ animationDelay: `${idx * 50}ms` }}>
                                        <td>{new Date(pred.timestamp).toLocaleTimeString()}</td>
                                        <td>{pred.asteroid_name || '—'}</td>
                                        <td>{pred.distance_km?.toLocaleString()}</td>
                                        <td>{pred.diameter_m?.toLocaleString()}</td>
                                        <td>
                                            <span className={`risk-badge risk-badge-${pred.risk_level.toLowerCase()}`}>
                                                {pred.risk_level}
                                            </span>
                                        </td>
                                        <td>{(pred.impact_probability * 100).toFixed(2)}%</td>
                                        <td>
                                            <button
                                                className="btn-delete"
                                                onClick={() => handleDelete(pred.id)}
                                                title="Delete"
                                            >
                                                🗑️
                                            </button>
                                        </td>
                                    </tr>
                                )) : (
                                    <tr>
                                        <td colSpan="7" className="table-empty">No predictions yet</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </section>
            </main>

            {/* Footer */}
            <footer className="footer">
                <div className="container">
                    <p>NEO Risk Prediction System v2.0 | Powered by Machine Learning</p>
                </div>
            </footer>
        </div>
    )
}

export default App
