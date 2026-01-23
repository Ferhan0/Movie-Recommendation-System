const express = require('express');
const router = express.Router();
const axios = require('axios');
const Movie = require('../models/Movie');
const Rating = require('../models/Rating');
const { protect } = require('../middleware/auth');

const TMDB_API_KEY = process.env.TMDB_API_KEY;
const TMDB_BASE_URL = 'https://api.themoviedb.org/3';

// ✅ 1. MovieLens endpoint (SPESİFİK route önce!)
router.get('/movielens', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const search = req.query.search || '';
    
    console.log('📽️ MovieLens Request - Page:', page, 'Limit:', limit);
    
    // ML Service'ten enriched movies al
    try {
      const response = await axios.get(
        `http://localhost:5000/api/movies/enriched?page=${page}&limit=${limit}&search=${search}`
      );
      
      if (response.data.success) {
        console.log('✅ MovieLens movies fetched:', response.data.data.movies.length);
        return res.json(response.data.data);
      }
    } catch (mlError) {
      console.log('⚠️ ML Service error, trying fallback:', mlError.message);
    }
    
    // Fallback: Direkt dosyadan oku
    const fs = require('fs');
    const path = require('path');
    const enrichedPath = path.join(__dirname, '../../ml-service/data/enriched_movies.json');
    
    console.log('🔄 Trying fallback - Reading from:', enrichedPath);
    
    if (fs.existsSync(enrichedPath)) {
      const enrichedMovies = JSON.parse(fs.readFileSync(enrichedPath, 'utf8'));
      
      // Filter by search if provided
      let filtered = enrichedMovies;
      if (search) {
        const searchLower = search.toLowerCase();
        filtered = enrichedMovies.filter(m => 
          m.title.toLowerCase().includes(searchLower) ||
          m.genres.toLowerCase().includes(searchLower)
        );
      }
      
      // Pagination
      const startIndex = (page - 1) * limit;
      const endIndex = startIndex + limit;
      const paginatedMovies = filtered.slice(startIndex, endIndex);
      
      console.log('✅ Fallback success:', paginatedMovies.length, 'movies');
      
      return res.json({
        movies: paginatedMovies,
        total: filtered.length,
        page: page,
        totalPages: Math.ceil(filtered.length / limit)
      });
    }
    
    console.log('❌ File not found:', enrichedPath);
    res.status(500).json({ message: 'Enriched movies file not found' });
    
  } catch (error) {
    console.error('❌ MovieLens Error:', error.message);
    res.status(500).json({ message: error.message });
  }
});

// ✅ 2. Search endpoint (SPESİFİK route)
router.get('/search', async (req, res) => {
  try {
    const query = req.query.q;
    if (!query) {
      return res.status(400).json({ message: 'Search query required' });
    }
    
    const response = await axios.get(
      `${TMDB_BASE_URL}/search/movie?api_key=${TMDB_API_KEY}&language=en-US&query=${query}`
    );
    
    const movies = response.data.results.map(movie => ({
      _id: movie.id,
      tmdbId: movie.id,
      title: movie.title,
      overview: movie.overview,
      posterPath: movie.poster_path,
      voteAverage: movie.vote_average,
      releaseDate: movie.release_date
    }));
    
    res.json(movies);
  } catch (error) {
    console.error('TMDB Search Error:', error.message);
    res.status(500).json({ message: error.message });
  }
});

// ✅ 3. Mapping endpoint (SPESİFİK route)
router.get('/mapping/:movieLensId', async (req, res) => {
  try {
    const fs = require('fs');
    const path = require('path');
    const enrichedPath = path.join(__dirname, '../../ml-service/data/enriched_movies.json');
    
    if (fs.existsSync(enrichedPath)) {
      const enrichedMovies = JSON.parse(fs.readFileSync(enrichedPath, 'utf8'));
      const movie = enrichedMovies.find(
        m => m.movieId === parseInt(req.params.movieLensId)
      );
      
      if (movie) {
        return res.json(movie);
      }
    }
    
    res.status(404).json({ message: 'Movie not found' });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// ✅ 4. Get popular movies from TMDB
router.get('/', async (req, res) => {
  try {
    const requestedPage = req.query.page || 1;
    const pagesToFetch = 10;
    const allMovies = [];
    const seenIds = new Set();
    
    for (let page = 1; page <= pagesToFetch; page++) {
      try {
        const response = await axios.get(
          `${TMDB_BASE_URL}/movie/popular?api_key=${TMDB_API_KEY}&language=en-US&page=${page}`
        );
        
        const movies = response.data.results
          .filter(movie => !seenIds.has(movie.id))
          .map(movie => {
            seenIds.add(movie.id);
            return {
              _id: movie.id,
              tmdbId: movie.id,
              title: movie.title,
              overview: movie.overview,
              posterPath: movie.poster_path,
              voteAverage: movie.vote_average,
              releaseDate: movie.release_date,
              genres: movie.genre_ids
            };
          });
        
        allMovies.push(...movies);
      } catch (pageError) {
        console.error(`Error fetching page ${page}:`, pageError.message);
      }
    }
    
    const limitedMovies = allMovies.slice(0, 200);
    res.json(limitedMovies);
  } catch (error) {
    console.error('TMDB Error:', error.message);
    res.status(500).json({ message: error.message });
  }
});

// ✅ 5. Get single movie details - MovieLens ID (GENEL route en sona!)
router.get('/:id', async (req, res) => {
  try {
    const movieId = parseInt(req.params.id);
    
    if (isNaN(movieId)) {
      console.log('❌ Invalid movie ID:', req.params.id);
      return res.status(400).json({ message: 'Invalid movie ID' });
    }
    
    console.log('📽️ Movie Detail Request: MovieLens ID', movieId);
    
    const fs = require('fs');
    const path = require('path');
    const enrichedPath = path.join(__dirname, '../../ml-service/data/enriched_movies.json');
    
    if (fs.existsSync(enrichedPath)) {
      const enrichedMovies = JSON.parse(fs.readFileSync(enrichedPath, 'utf8'));
      const movie = enrichedMovies.find(m => m.movieId === movieId);
      
      if (movie) {
        console.log('✅ Found in enriched_movies.json:', movie.title);
        
        if (movie.tmdbId) {
          try {
            const tmdbDetails = await axios.get(
              `https://api.themoviedb.org/3/movie/${movie.tmdbId}`,
              { params: { api_key: TMDB_API_KEY } }
            );
            
            console.log('✅ TMDB details fetched for TMDB ID:', movie.tmdbId);
            
            const fullMovie = {
              ...movie,
              runtime: tmdbDetails.data.runtime,
              budget: tmdbDetails.data.budget,
              revenue: tmdbDetails.data.revenue,
              tagline: tmdbDetails.data.tagline,
              homepage: tmdbDetails.data.homepage,
              productionCompanies: tmdbDetails.data.production_companies,
            };
            
            return res.json(fullMovie);
          } catch (tmdbError) {
            console.log('⚠️ TMDB details fetch failed, using enriched data only');
            return res.json(movie);
          }
        }
        
        return res.json(movie);
      }
    }
    
    console.log('❌ Movie not found');
    res.status(404).json({ message: 'Movie not found' });
    
  } catch (error) {
    console.error('❌ Movie Detail Error:', error.message);
    res.status(500).json({ message: error.message });
  }
});

// ✅ 6. Rating endpoints
router.post('/rating', protect, async (req, res) => {
  try {
    const { movieId, rating } = req.body;
    
    let movie = await Movie.findOne({ tmdbId: movieId });
    
    if (!movie) {
      try {
        const tmdbResponse = await axios.get(
          `${TMDB_BASE_URL}/movie/${movieId}?api_key=${TMDB_API_KEY}&language=en-US`
        );
        
        movie = await Movie.create({
          tmdbId: tmdbResponse.data.id,
          title: tmdbResponse.data.title,
          overview: tmdbResponse.data.overview,
          posterPath: tmdbResponse.data.poster_path,
          releaseDate: tmdbResponse.data.release_date,
          voteAverage: tmdbResponse.data.vote_average,
          genres: tmdbResponse.data.genres?.map(g => g.name) || []
        });
      } catch (tmdbError) {
        return res.status(404).json({ message: 'Movie not found' });
      }
    }
    
    let userRating = await Rating.findOne({ 
      user: req.user._id, 
      movie: movie._id 
    });
    
    if (userRating) {
      userRating.rating = rating;
      await userRating.save();
    } else {
      userRating = await Rating.create({
        user: req.user._id,
        movie: movie._id,
        rating
      });
    }
    res.status(201).json(userRating);
  } catch (error) {
    console.error('Rating error:', error);
    res.status(500).json({ message: error.message });
  }
});

router.get('/ratings/user/:userId', async (req, res) => {
  try {
    const ratings = await Rating.find({ user: req.params.userId })
      .populate('movie');
    res.json(ratings);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// Get ML Service compatible user ID
router.get('/user/ml-id', protect, async (req, res) => {
  try {
    // MongoDB user'ının _id'sinden sayısal bir ID üret
    const objectId = req.user._id.toString();
    
    // ObjectId'nin son 8 karakterini hex'ten integer'a çevir
    const mlUserId = parseInt(objectId.slice(-8), 16) % 610 + 1; // 1-610 arası
    
    console.log(`📊 User ${objectId} mapped to ML User ID: ${mlUserId}`);
    
    res.json({
      mongoUserId: objectId,
      mlUserId: mlUserId
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

module.exports = router;
