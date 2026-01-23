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
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchingMovies, setSearchingMovies] = useState(false);

  const fetchRecommendations = async (type) => {
  setLoading(true);
  setError(null);
  
  try {
    let url;
    let userId = null;
    
    // Collaborative ve Hybrid için ML-compatible user ID al
    if ((type === 'collaborative' || type === 'hybrid') && user) {
      console.log('🔍 Getting ML-compatible user ID...');
      
      try {
        const token = localStorage.getItem('token');
        const userIdResponse = await axios.get(
          'http://localhost:5001/api/movies/user/ml-id',
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        );
        userId = userIdResponse.data.mlUserId;
        console.log('✅ ML User ID:', userId);
      } catch (err) {
        console.error('❌ User ID mapping error:', err);
        setError('Failed to get user ID. Please try logging in again.');
        setLoading(false);
        return;
      }
    }
    
    // URL oluştur
    if (type === 'content-based') {
      if (!selectedMovieId) {
        setError('Please select a movie first');
        setLoading(false);
        return;
      }
      url = `http://localhost:5000/api/recommend/content-based/${selectedMovieId}?limit=10`;
    } else if (type === 'collaborative') {
      if (!user) {
        setError('Please login to get collaborative recommendations');
        setLoading(false);
        return;
      }
      if (!userId) {
        setError('Failed to map user ID');
        setLoading(false);
        return;
      }
      url = `http://localhost:5000/api/recommend/collaborative/${userId}?limit=10`;
    } else if (type === 'hybrid') {
      if (!user) {
        setError('Please login to get hybrid recommendations');
        setLoading(false);
        return;
      }
      if (!userId) {
        setError('Failed to map user ID');
        setLoading(false);
        return;
      }
      url = `http://localhost:5000/api/recommend/hybrid/${userId}?limit=10`;
    }
    
    console.log('📡 Fetching from:', url);
    
    const response = await axios.get(url);
    
    if (response.data.success) {
      setRecommendations(response.data.data);
      console.log('✅ Recommendations loaded:', response.data.data.recommendations?.length || 'N/A');
    } else {
      setError(response.data.error || 'Failed to get recommendations');
    }
    
    setLoading(false);
    
  } catch (err) {
    console.error('❌ Full error:', err);
    
    if (err.response) {
      // Server responded with error
      const errorMsg = err.response.data?.error || err.response.data?.message || 'Failed to fetch recommendations';
      setError(errorMsg);
      console.log('📛 Server error:', errorMsg);
    } else if (err.request) {
      // Request made but no response
      setError('Cannot connect to ML Service. Please ensure it is running on port 5000.');
    } else {
      // Something else
      setError('An error occurred: ' + err.message);
    }
    
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

    const handleMovieSearch = async (query) => {
      setSearchQuery(query);
      
      if (query.length < 2) {
        setSearchResults([]);
        return;
      }
      
      setSearchingMovies(true);
      try {
        // ML Service'ten MovieLens filmlerinde ara
        const response = await axios.get(
          `http://localhost:5000/api/movies/search?q=${query}&limit=10`
        );
        
        if (response.data.success && response.data.data.results) {
          setSearchResults(response.data.data.results);
        } else {
          setSearchResults([]);
        }
      } catch (err) {
        console.error('Search error:', err);
        setSearchResults([]);
      }
      setSearchingMovies(false);
    };

  const handleMovieSelect = (movie) => {
    setSelectedMovieId(movie.movieId);
    setSearchQuery(movie.title);
    setSearchResults([]);
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
          <label htmlFor="movieSearch">Search for a movie to find similar ones:</label>
          <div className="search-container">
            <div className="input-group">
              <input
                type="text"
                id="movieSearch"
                value={searchQuery}
                onChange={(e) => handleMovieSearch(e.target.value)}
                placeholder="Type movie name (e.g., Toy Story, Matrix...)"
                autoComplete="off"
              />
              <button 
                onClick={handleGetRecommendations} 
                className="btn-recommend"
                disabled={!selectedMovieId}
              >
                Get Recommendations
              </button>
            </div>
            
            {/* Search Results Dropdown */}
            {searchResults.length > 0 && (
              <div className="search-results">
                {searchResults.map((movie) => (
                  <div
                    key={movie.movieId}
                    className="search-result-item"
                    onClick={() => handleMovieSelect(movie)}
                  >
                    <div className="result-title">{movie.title}</div>
                    <div className="result-genres">{movie.genres}</div>
                    {movie.avgRating && (
                      <div className="result-rating">⭐ {movie.avgRating.toFixed(1)}</div>
                    )}
                  </div>
                ))}
              </div>
            )}
            
            {searchingMovies && (
              <div className="searching">Searching...</div>
            )}
          </div>
          
          {selectedMovieId && (
            <p className="selected-movie">
              ✓ Selected: <strong>{searchQuery}</strong>
            </p>
          )}
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