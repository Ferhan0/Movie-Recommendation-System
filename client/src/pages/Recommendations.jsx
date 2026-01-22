import React, { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import axios from 'axios';
import './Recommendations.css';

const Recommendations = () => {
  const { user } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('hybrid');
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedMovieId, setSelectedMovieId] = useState(1); // For content-based

  const fetchRecommendations = async (type) => {
  setLoading(true);
  setError(null);
  
  try {
    let url;
    // Use hardcoded ID if user.id is undefined
    const userId = user?.id || 1; // Fallback to 1
    
    console.log('User ID:', userId); // Debug
    
    if (type === 'content-based') {
      url = `http://localhost:5000/api/recommend/content-based/${selectedMovieId}?limit=10`;
    } else if (type === 'collaborative') {
      url = `http://localhost:5000/api/recommend/collaborative/${userId}?limit=10`;
    } else if (type === 'hybrid') {
      url = `http://localhost:5000/api/recommend/hybrid/${userId}?limit=10`;
    }
    
    console.log('Fetching from:', url); // Debug
    
    const response = await axios.get(url);
    setRecommendations(response.data.data);
    setLoading(false);
  } catch (err) {
    console.error('Full error:', err);
    setError(err.response?.data?.error || err.message || 'Failed to fetch recommendations');
    setLoading(false);
  }
};

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setRecommendations(null);
    setError(null);
  };

  const handleGetRecommendations = () => {
    fetchRecommendations(activeTab);
  };

  return (
    <div className="recommendations-page">
      <div className="recommendations-header">
        <h1>🎬 Movie Recommendations</h1>
        <p>Get personalized movie suggestions based on different algorithms</p>
      </div>

      {/* Algorithm Tabs */}
      <div className="algorithm-tabs">
        <button
          className={`tab ${activeTab === 'hybrid' ? 'active' : ''}`}
          onClick={() => handleTabChange('hybrid')}
        >
          <span className="tab-icon">⚡</span>
          <span className="tab-name">Hybrid</span>
          <span className="tab-desc">Best of Both</span>
        </button>
        <button
          className={`tab ${activeTab === 'collaborative' ? 'active' : ''}`}
          onClick={() => handleTabChange('collaborative')}
        >
          <span className="tab-icon">👥</span>
          <span className="tab-name">Collaborative</span>
          <span className="tab-desc">Similar Users</span>
        </button>
        <button
          className={`tab ${activeTab === 'content-based' ? 'active' : ''}`}
          onClick={() => handleTabChange('content-based')}
        >
          <span className="tab-icon">🎭</span>
          <span className="tab-name">Content-Based</span>
          <span className="tab-desc">Similar Movies</span>
        </button>
      </div>

      {/* Algorithm Info */}
      <div className="algorithm-info">
        {activeTab === 'hybrid' && (
          <div className="info-box hybrid-info">
            <h3>⚡ Hybrid Recommendation System</h3>
            <p>Combines Content-Based (60%) and Collaborative Filtering (40%) for the best results.</p>
            <p><strong>RMSE: 0.9276</strong> - Our most accurate algorithm!</p>
            <ul>
              <li>✅ Personalized based on your taste</li>
              <li>✅ Discovers new genres you might like</li>
              <li>✅ Best overall performance</li>
            </ul>
          </div>
        )}
        
        {activeTab === 'collaborative' && (
          <div className="info-box collaborative-info">
            <h3>👥 Collaborative Filtering</h3>
            <p>Finds users with similar taste and recommends movies they enjoyed.</p>
            <p><strong>RMSE: 1.0047</strong> - Great for discovering new content!</p>
            <ul>
              <li>✅ Learns from user behavior</li>
              <li>✅ Finds hidden gems</li>
              <li>✅ Serendipitous discoveries</li>
            </ul>
          </div>
        )}
        
        {activeTab === 'content-based' && (
          <div className="info-box content-info">
            <h3>🎭 Content-Based Filtering</h3>
            <p>Recommends movies similar to ones you've already enjoyed.</p>
            <p><strong>RMSE: 1.0381</strong> - Perfect for finding similar movies!</p>
            <ul>
              <li>✅ Genre-based matching</li>
              <li>✅ Consistent with your preferences</li>
              <li>✅ Easy to understand recommendations</li>
            </ul>
          </div>
        )}
      </div>

      {/* Input for Content-Based */}
      {activeTab === 'content-based' && (
        <div className="input-section">
          <label htmlFor="movieId">Enter Movie ID to find similar movies:</label>
          <div className="input-group">
            <input
              type="number"
              id="movieId"
              value={selectedMovieId}
              onChange={(e) => setSelectedMovieId(e.target.value)}
              placeholder="Movie ID (e.g., 1 for Toy Story)"
            />
            <button onClick={handleGetRecommendations} className="btn-recommend">
              Get Recommendations
            </button>
          </div>
          <p className="hint">💡 Popular IDs: 1 (Toy Story), 318 (Shawshank), 296 (Pulp Fiction)</p>
        </div>
      )}

      {/* Get Recommendations Button */}
      {activeTab !== 'content-based' && (
        <div className="action-section">
          <button onClick={handleGetRecommendations} className="btn-recommend">
            🎯 Get {activeTab === 'hybrid' ? 'Hybrid' : 'Collaborative'} Recommendations
          </button>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Finding the best movies for you...</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
        </div>
      )}

      {/* Recommendations List */}
      {recommendations && !loading && (
        <div className="recommendations-results">
          <div className="results-header">
            <h2>Your Recommendations</h2>
            <span className="results-count">{recommendations.recommendations?.length || recommendations.count} movies</span>
          </div>

          <div className="movies-grid">
            {recommendations.recommendations.map((movie, index) => (
              <div key={movie.movieId} className="movie-card">
                <div className="movie-rank">#{index + 1}</div>
                <div className="movie-content">
                  <h3 className="movie-title">{movie.title}</h3>
                  <div className="movie-genres">
                    {movie.genres?.split('|').map((genre, i) => (
                      <span key={i} className="genre-tag">{genre}</span>
                    ))}
                  </div>
                  <div className="movie-stats">
                    {movie.similarity_score && (
                      <span className="stat">
                        🎯 Similarity: {(movie.similarity_score * 100).toFixed(1)}%
                      </span>
                    )}
                    {movie.predicted_rating && (
                      <span className="stat">
                        ⭐ Predicted: {movie.predicted_rating.toFixed(2)}
                      </span>
                    )}
                    {movie.hybrid_score && (
                      <span className="stat">
                        ⚡ Score: {(movie.hybrid_score * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                  {movie.cb_contribution && movie.cf_contribution && (
                    <div className="score-breakdown">
                      <div className="breakdown-item">
                        <span>Content:</span>
                        <div className="progress-bar">
                          <div 
                            className="progress-fill content"
                            style={{width: `${movie.cb_contribution * 100}%`}}
                          ></div>
                        </div>
                      </div>
                      <div className="breakdown-item">
                        <span>Collaborative:</span>
                        <div className="progress-bar">
                          <div 
                            className="progress-fill collaborative"
                            style={{width: `${movie.cf_contribution * 100}%`}}
                          ></div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Recommendations;