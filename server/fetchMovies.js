const axios = require('axios');
const mongoose = require('mongoose');
const dotenv = require('dotenv');
const Movie = require('./models/Movie');

dotenv.config();

const TMDB_API_KEY = process.env.TMDB_API_KEY;
const TMDB_BASE_URL = 'https://api.themoviedb.org/3';

const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGO_URI);
    console.log('MongoDB Connected');
  } catch (error) {
    console.error('MongoDB Error:', error.message);
    process.exit(1);
  }
};

const fetchMovies = async () => {
  try {
    console.log('Fetching movies from TMDB...');
    console.log('API Key:', TMDB_API_KEY ? 'Found' : 'Missing');
    
    for (let page = 1; page <= 10; page++) {
      const response = await axios.get(`${TMDB_BASE_URL}/movie/popular`, {
        params: {
          api_key: TMDB_API_KEY,
          language: 'en-US',
          page: page
        }
      });

      const movies = response.data.results;

      for (const movie of movies) {
        const exists = await Movie.findOne({ tmdbId: movie.id });
        if (!exists) {
          await Movie.create({
            tmdbId: movie.id,
            title: movie.title,
            overview: movie.overview,
            posterPath: movie.poster_path,
            releaseDate: movie.release_date,
            voteAverage: movie.vote_average,
            genres: movie.genre_ids
          });
          console.log(`✅ ${movie.title}`);
        }
      }
      console.log(`Page ${page}/10 done`);
    }

    console.log('\n🎉 All movies fetched!');
    const totalMovies = await Movie.countDocuments();
    console.log(`Total movies in database: ${totalMovies}`);
    process.exit(0);
  } catch (error) {
    console.error('❌ Error:', error.response?.data || error.message);
    process.exit(1);
  }
};

connectDB().then(() => fetchMovies());