import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import axios from 'axios';
import './TemporalDashboard.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82ca9d'];

const TemporalDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [trends, setTrends] = useState(null);
  const [seasonal, setSeasonal] = useState(null);
  const [popular, setPopular] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTemporalData();
  }, []);

  const fetchTemporalData = async () => {
    try {
      setLoading(true);
      
      // Fetch all temporal data
      const [trendsRes, seasonalRes, popularRes] = await Promise.all([
        axios.get('http://localhost:5000/api/temporal/trends'),
        axios.get('http://localhost:5000/api/temporal/seasonal'),
        axios.get('http://localhost:5000/api/temporal/popular?limit=10')
      ]);

      setTrends(trendsRes.data.data);
      setSeasonal(seasonalRes.data.data);
      setPopular(popularRes.data.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching temporal data:', err);
      setError('Failed to load temporal analysis data');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="temporal-dashboard">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading Temporal Analysis...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="temporal-dashboard">
        <div className="error-message">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={fetchTemporalData}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="temporal-dashboard">
      <div className="dashboard-header">
        <h1>📊 Temporal Analysis Dashboard</h1>
        <p>Analyzing rating trends and patterns over time</p>
      </div>

      {/* Yearly Trends */}
      <div className="dashboard-section">
        <h2>📅 Yearly Rating Trends (1996-2018)</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={trends?.yearly}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis domain={[3, 4]} />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="mean" 
                stroke="#8884d8" 
                strokeWidth={2}
                name="Average Rating"
              />
              <Line 
                type="monotone" 
                dataKey="count" 
                stroke="#82ca9d" 
                strokeWidth={2}
                name="Rating Count"
                yAxisId="right"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="insights">
          <div className="insight-card">
            <h4>Highest Year</h4>
            <p className="insight-value">
              {trends?.yearly.reduce((max, y) => y.mean > max.mean ? y : max).year}
            </p>
            <p className="insight-label">
              Rating: {trends?.yearly.reduce((max, y) => y.mean > max.mean ? y : max).mean.toFixed(3)}
            </p>
          </div>
          <div className="insight-card">
            <h4>Most Active Year</h4>
            <p className="insight-value">
              {trends?.yearly.reduce((max, y) => y.count > max.count ? y : max).year}
            </p>
            <p className="insight-label">
              {trends?.yearly.reduce((max, y) => y.count > max.count ? y : max).count.toLocaleString()} ratings
            </p>
          </div>
        </div>
      </div>

      {/* Monthly Patterns */}
      <div className="dashboard-section">
        <h2>📆 Monthly Rating Patterns</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={trends?.monthly}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="month" 
                tickFormatter={(month) => {
                  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                  return months[month - 1];
                }}
              />
              <YAxis />
              <Tooltip 
                labelFormatter={(month) => {
                  const months = ['January', 'February', 'March', 'April', 'May', 'June',
                                  'July', 'August', 'September', 'October', 'November', 'December'];
                  return months[month - 1];
                }}
              />
              <Legend />
              <Bar dataKey="mean" fill="#8884d8" name="Average Rating" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Seasonal Patterns */}
        <div className="dashboard-section">
        <h2>🌍 Quarterly Patterns (Seasonal Analysis)</h2>
        <div className="stats-grid">
            {seasonal?.quarterly.map((q) => {
            const quarters = {
                1: { name: 'Q1: Winter', months: 'Jan-Mar', emoji: '❄️' },
                2: { name: 'Q2: Spring', months: 'Apr-Jun', emoji: '🌸' },
                3: { name: 'Q3: Summer', months: 'Jul-Sep', emoji: '☀️' },
                4: { name: 'Q4: Fall', months: 'Oct-Dec', emoji: '🍂' }
            };
            return (
                <div key={q.quarter} className="stat-card">
                <h3>{quarters[q.quarter].emoji} {quarters[q.quarter].name}</h3>
                <p className="quarter-months">{quarters[q.quarter].months}</p>
                <div className="stat-value">{q.mean.toFixed(3)}</div>
                <div className="stat-label">Average Rating</div>
                <div className="stat-count">{q.count.toLocaleString()} ratings</div>
                </div>
            );
            })}
        </div>
        </div>

      {/* Hourly Activity */}
      <div className="dashboard-section">
        <h2>⏰ Hourly Activity Pattern</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={seasonal?.hourly}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" label={{ value: 'Hour of Day', position: 'insideBottom', offset: -5 }} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#82ca9d" name="Activity Count" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="peak-info">
          <p>🔥 Peak Activity Hour: <strong>{seasonal?.peak_hour}:00</strong></p>
        </div>
      </div>

      {/* Day of Week */}
      <div className="dashboard-section">
        <h2>📊 Day of Week Analysis</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={trends?.dayofweek}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="dayofweek"
                tickFormatter={(day) => {
                  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                  return days[day];
                }}
              />
              <YAxis />
              <Tooltip 
                labelFormatter={(day) => {
                  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                               'Friday', 'Saturday', 'Sunday'];
                  return days[day];
                }}
              />
              <Legend />
              <Bar dataKey="count" fill="#FFBB28" name="Rating Count" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

            {/* Trending Movies */}
        <div className="dashboard-section">
        <h2>🔥 Trending Movies (Last Year)</h2>
        <div className="trending-grid">
            {popular?.recent_popular.slice(0, 6).map((movie, index) => (
            <div key={movie.movieId} className="trending-card">
                <div className="trending-rank">#{index + 1}</div>
                <div className="trending-info">
                <h4 className="movie-title">{movie.title}</h4>
                <p className="movie-genres">{movie.genres}</p>
                <div className="trending-stats">
                    <span className="rating">⭐ {movie.avg_rating.toFixed(2)}</span>
                    <span className="count">📊 {movie.rating_count} ratings</span>
                </div>
                </div>
            </div>
            ))}
        </div>
        </div>

            {/* Rising Stars */}
        <div className="dashboard-section">
        <h2>⭐ Rising Stars (Biggest Improvements)</h2>
        <div className="rising-stars-list">
            {popular?.rising_stars.slice(0, 5).map((movie, index) => (
            <div key={movie.movieId} className="rising-star-item">
                <div className="rank">#{index + 1}</div>
                <div className="movie-info">
                <h4 className="movie-title">{movie.title}</h4>
                <p className="movie-genres">{movie.genres}</p>
                <div className="rating-change">
                    <span className="old-rating">{movie.old_avg_rating.toFixed(2)}</span>
                    <span className="arrow">→</span>
                    <span className="new-rating">{movie.avg_rating.toFixed(2)}</span>
                    <span className="improvement">+{movie.rating_change.toFixed(3)}</span>
                </div>
                </div>
            </div>
            ))}
        </div>
        </div>

      {/* Summary */}
      <div className="dashboard-section summary-section">
        <h2>📋 Key Insights</h2>
        <div className="insights-grid">
          <div className="insight-box">
            <h4>📊 Total Dataset</h4>
            <p>100,836 ratings analyzed</p>
            <p>1996-2018 time span</p>
          </div>
          <div className="insight-box">
            <h4>📈 Best Period</h4>
            <p>Q4 has highest ratings (3.563)</p>
            <p>Holiday season effect</p>
          </div>
          <div className="insight-box">
            <h4>⏰ Peak Time</h4>
            <p>20:00 (8 PM) most active</p>
            <p>Evening viewing patterns</p>
          </div>
          <div className="insight-box">
            <h4>🎯 Trends</h4>
            <p>User preferences evolve</p>
            <p>Temporal weighting matters</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemporalDashboard;