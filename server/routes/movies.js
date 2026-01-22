const express = require('express');
const router = express.Router();
const axios = require('axios');
const Movie = require('../models/Movie');
const Rating = require('../models/Rating');
const { protect } = require('../middleware/auth');

const TMDB_API_KEY = process.env.TMDB_API_KEY;
const TMDB_BASE_URL = 'https://api.themoviedb.org/3';

// Get popular movies from TMDB (fetch multiple pages to get ~200 movies)
router.get('/', async (req, res) => {
  try {
    const requestedPage = req.query.page || 1;
    const pagesToFetch = 10; // Fetch 10 pages to get ~200 movies (20 per page)
    const allMovies = [];
    const seenIds = new Set(); // Track unique movie IDs to avoid duplicates
    
    // Fetch multiple pages from TMDB
    for (let page = 1; page <= pagesToFetch; page++) {
      try {
        const response = await axios.get(
          `${TMDB_BASE_URL}/movie/popular?api_key=${TMDB_API_KEY}&language=en-US&page=${page}`
        );
        
        // Format TMDB response to match our frontend and filter duplicates
        const movies = response.data.results
          .filter(movie => !seenIds.has(movie.id)) // Filter duplicates
          .map(movie => {
            seenIds.add(movie.id); // Mark as seen
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
        // Continue with other pages even if one fails
      }
    }
    
    // Limit to 200 unique movies as before
    const limitedMovies = allMovies.slice(0, 200);
    
    res.json(limitedMovies);
  } catch (error) {
    console.error('TMDB Error:', error.message);
    res.status(500).json({ message: error.message });
  }
});

// Search movies from TMDB
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

// Get movie by ID from TMDB
router.get('/:id', async (req, res) => {
  try {
    const response = await axios.get(
      `${TMDB_BASE_URL}/movie/${req.params.id}?api_key=${TMDB_API_KEY}&language=en-US`
    );
    
    const movie = {
      _id: response.data.id,
      tmdbId: response.data.id,
      title: response.data.title,
      overview: response.data.overview,
      posterPath: response.data.poster_path,
      backdropPath: response.data.backdrop_path,
      voteAverage: response.data.vote_average,
      voteCount: response.data.vote_count,
      releaseDate: response.data.release_date,
      runtime: response.data.runtime,
      genres: response.data.genres,
      productionCompanies: response.data.production_companies
    };
    
    res.json(movie);
  } catch (error) {
    console.error('TMDB Movie Error:', error.message);
    res.status(404).json({ message: 'Movie not found' });
  }
});

// Rating endpoints (keep as is for MongoDB ratings)
router.post('/rating', protect, async (req, res) => {
  try {
    const { movieId, rating } = req.body;
    
    // movieId is TMDB ID, we need to find or create the Movie in MongoDB
    let movie = await Movie.findOne({ tmdbId: movieId });
    
    // If movie doesn't exist in MongoDB, fetch from TMDB and create it
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
    
    // Now use the MongoDB movie _id for rating
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

module.exports = router;