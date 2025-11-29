import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';

const MovieDetail = () => {
  const { id } = useParams();
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [userRating, setUserRating] = useState(null);
  const [ratingMessage, setRatingMessage] = useState('');

  useEffect(() => {
    fetchMovie();
    
  }, [id]);

  const fetchMovie = async () => {
    try {
      const res = await axios.get(`http://localhost:5000/api/movies/${id}`);
      setMovie(res.data);
    } catch (err) {
      setError('Failed to load movie');
    } finally {
      setLoading(false);
    }
  };

  const handleRating = async (value) => {
    if (!user) {
      alert('Please login to rate movies');
      navigate('/login');
      return;
    }

    try {
      await axios.post('http://localhost:5000/api/movies/rating', {
        movieId: id,
        rating: value
      });
      
      setRating(value);
      setUserRating(value);
      setRatingMessage('Rating submitted successfully!');
      setTimeout(() => setRatingMessage(''), 3000);
    } catch (err) {
      setRatingMessage('Failed to submit rating');
    }
  };

  if (loading) return <div style={styles.loading}>Loading...</div>;
  if (error) return <div style={styles.error}>{error}</div>;
  if (!movie) return <div style={styles.error}>Movie not found</div>;

  return (
    <div style={styles.container}>
      <button onClick={() => navigate('/movies')} style={styles.backButton}>
        ← Back to Movies
      </button>

      <div style={styles.content}>
        {/* Poster */}
        <div style={styles.posterContainer}>
          {movie.posterPath ? (
            <img
              src={`https://image.tmdb.org/t/p/w500${movie.posterPath}`}
              alt={movie.title}
              style={styles.poster}
            />
          ) : (
            <div style={styles.noPoster}>No poster available</div>
          )}
        </div>

        {/* Info */}
        <div style={styles.info}>
          <h1 style={styles.title}>{movie.title}</h1>
          
          <div style={styles.meta}>
            <span style={styles.rating}>⭐ {movie.voteAverage?.toFixed(1)}</span>
            <span style={styles.date}>{movie.releaseDate}</span>
          </div>

          <div style={styles.section}>
            <h3>Overview</h3>
            <p style={styles.overview}>{movie.overview || 'No overview available'}</p>
          </div>

          {/* User Rating */}
          {user && (
            <div style={styles.section}>
              <h3>Your Rating</h3>
              <div style={styles.stars}>
                {[1, 2, 3, 4, 5].map((star) => (
                  <span
                    key={star}
                    style={{
                      ...styles.star,
                      color: (hoveredRating || rating || userRating) >= star ? '#ffd700' : '#ddd'
                    }}
                    onMouseEnter={() => setHoveredRating(star)}
                    onMouseLeave={() => setHoveredRating(0)}
                    onClick={() => handleRating(star)}
                  >
                    ★
                  </span>
                ))}
              </div>
              {ratingMessage && (
                <p style={styles.ratingMessage}>{ratingMessage}</p>
              )}
            </div>
          )}

          {!user && (
            <div style={styles.loginPrompt}>
              Please <span onClick={() => navigate('/login')} style={styles.loginLink}>login</span> to rate this movie
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '2rem 1rem',
  },
  backButton: {
    backgroundColor: '#1a1a2e',
    color: '#fff',
    border: 'none',
    padding: '0.75rem 1.5rem',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '1rem',
    marginBottom: '2rem',
  },
  content: {
    display: 'flex',
    gap: '3rem',
    backgroundColor: '#fff',
    padding: '2rem',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
  },
  posterContainer: {
    flex: '0 0 300px',
  },
  poster: {
    width: '100%',
    borderRadius: '8px',
    boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
  },
  noPoster: {
    width: '300px',
    height: '450px',
    backgroundColor: '#f0f0f0',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: '8px',
    color: '#999',
  },
  info: {
    flex: 1,
  },
  title: {
    fontSize: '2.5rem',
    marginBottom: '1rem',
    color: '#1a1a2e',
  },
  meta: {
    display: 'flex',
    gap: '2rem',
    marginBottom: '2rem',
    fontSize: '1.1rem',
  },
  rating: {
    color: '#e94560',
    fontWeight: 'bold',
  },
  date: {
    color: '#666',
  },
  section: {
    marginBottom: '2rem',
  },
  overview: {
    lineHeight: '1.6',
    color: '#333',
    fontSize: '1.1rem',
  },
  stars: {
    fontSize: '2.5rem',
    cursor: 'pointer',
    userSelect: 'none',
  },
  star: {
    marginRight: '0.25rem',
    transition: 'color 0.2s',
  },
  ratingMessage: {
    marginTop: '1rem',
    color: '#28a745',
    fontWeight: 'bold',
  },
  loginPrompt: {
    padding: '1rem',
    backgroundColor: '#f8f9fa',
    borderRadius: '4px',
    color: '#666',
  },
  loginLink: {
    color: '#1a1a2e',
    fontWeight: 'bold',
    cursor: 'pointer',
    textDecoration: 'underline',
  },
  loading: {
    textAlign: 'center',
    padding: '3rem',
    fontSize: '1.2rem',
  },
  error: {
    textAlign: 'center',
    padding: '3rem',
    color: '#c33',
    fontSize: '1.2rem',
  },
};

export default MovieDetail;