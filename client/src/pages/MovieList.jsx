import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const MovieList = () => {
  const navigate = useNavigate();
  const [movies, setMovies] = useState([]);
  const [filteredMovies, setFilteredMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchMovies();
  }, []);

  useEffect(() => {
    // Arama filtresi
    if (!Array.isArray(movies)) {
      setFilteredMovies([]);
      return;
    }
    
    if (searchTerm.trim() === '') {
      setFilteredMovies(movies);
    } else {
      const filtered = movies.filter(movie =>
        movie.title?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredMovies(filtered);
    }
  }, [searchTerm, movies]);

  const fetchMovies = async () => {
    try {
      const res = await axios.get('http://localhost:5001/api/movies?page=1');
      
      console.log('Response:', res.data); // Debug
      
      // TMDB response direkt array dönüyor
      const moviesData = Array.isArray(res.data) ? res.data : [];
      
      setMovies(moviesData);
      setFilteredMovies(moviesData);
    } catch (err) {
      console.error('Fetch error:', err);
      setError('Failed to load movies');
      setMovies([]);
      setFilteredMovies([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div style={styles.loading}>Loading movies...</div>;
  if (error) return <div style={styles.error}>{error}</div>;

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Popular Movies</h1>
      
      {/* Arama Kutusu */}
      <div style={styles.searchContainer}>
        <input
          type="text"
          placeholder="Search movies..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={styles.searchInput}
        />
        {searchTerm && (
          <button onClick={() => setSearchTerm('')} style={styles.clearButton}>
            ✕
          </button>
        )}
      </div>

      {/* Sonuç Sayısı */}
      <p style={styles.resultCount}>
        {filteredMovies.length} movie{filteredMovies.length !== 1 ? 's' : ''} found
      </p>

      {/* Film Grid */}
      <div style={styles.grid}>
        {filteredMovies.length > 0 ? (
          filteredMovies.map((movie) => (
            <div 
              key={movie._id} 
              style={styles.card}
              onClick={() => navigate(`/movies/${movie._id}`)}
            >
              {movie.posterPath && (
                <img
                  src={`https://image.tmdb.org/t/p/w300${movie.posterPath}`}
                  alt={movie.title}
                  style={styles.poster}
                />
              )}
              <div style={styles.info}>
                <h3 style={styles.movieTitle}>{movie.title}</h3>
                <p style={styles.rating}>⭐ {movie.voteAverage?.toFixed(1)}</p>
                <p style={styles.overview}>
                  {movie.overview?.substring(0, 100)}...
                </p>
              </div>
            </div>
          ))
        ) : (
          <div style={styles.noResults}>
            No movies found for "{searchTerm}"
          </div>
        )}
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
  title: {
    textAlign: 'center',
    marginBottom: '2rem',
    color: '#1a1a2e',
  },
  searchContainer: {
    position: 'relative',
    maxWidth: '500px',
    margin: '0 auto 1rem',
  },
  searchInput: {
    width: '100%',
    padding: '1rem',
    fontSize: '1rem',
    border: '2px solid #ddd',
    borderRadius: '8px',
    outline: 'none',
    transition: 'border-color 0.3s',
  },
  clearButton: {
    position: 'absolute',
    right: '10px',
    top: '50%',
    transform: 'translateY(-50%)',
    backgroundColor: 'transparent',
    border: 'none',
    fontSize: '1.5rem',
    color: '#999',
    cursor: 'pointer',
    padding: '0 0.5rem',
  },
  resultCount: {
    textAlign: 'center',
    color: '#666',
    marginBottom: '2rem',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
    gap: '2rem',
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    overflow: 'hidden',
    transition: 'transform 0.3s',
    cursor: 'pointer',
  },
  poster: {
    width: '100%',
    height: '375px',
    objectFit: 'cover',
  },
  info: {
    padding: '1rem',
  },
  movieTitle: {
    fontSize: '1.1rem',
    marginBottom: '0.5rem',
    color: '#1a1a2e',
  },
  rating: {
    color: '#e94560',
    fontWeight: 'bold',
    marginBottom: '0.5rem',
  },
  overview: {
    fontSize: '0.9rem',
    color: '#666',
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
  noResults: {
    gridColumn: '1 / -1',
    textAlign: 'center',
    padding: '3rem',
    color: '#666',
    fontSize: '1.2rem',
  },
};

export default MovieList;