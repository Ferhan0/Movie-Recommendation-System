const express = require('express');
const router = express.Router();
const Movie = require('../models/Movie');
const Rating = require('../models/Rating');
const { protect } = require('../middleware/auth');

router.get('/', async (req, res) => {
  try {
    const movies = await Movie.find().limit(50);
    res.json(movies);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

router.get('/:id', async (req, res) => {
  try {
    const movie = await Movie.findById(req.params.id);
    if (movie) {
      res.json(movie);
    } else {
      res.status(404).json({ message: 'Movie not found' });
    }
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

router.post('/rating', protect, async (req, res) => {
  try {
    const { movieId, rating } = req.body;
    const movie = await Movie.findById(movieId);
    if (!movie) return res.status(404).json({ message: 'Movie not found' });
    
    let userRating = await Rating.findOne({ user: req.user._id, movie: movieId });
    
    if (userRating) {
      userRating.rating = rating;
      await userRating.save();
    } else {
      userRating = await Rating.create({
        user: req.user._id,
        movie: movieId,
        rating
      });
    }
    res.status(201).json(userRating);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

module.exports = router;