# app.py (veya mevcut Flask dosyanız varsa ona ekleyelim)

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from temporal_analysis import TemporalAnalyzer
import pickle
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

# Load data
print("Loading data...")
ratings_df = pd.read_csv('data/ml-latest-small/ratings.csv')
movies_df = pd.read_csv('data/ml-latest-small/movies.csv')

# Initialize Temporal Analyzer
temporal_analyzer = TemporalAnalyzer(ratings_df)

# Load or create TF-IDF matrix
print("Creating Content-Based model...")
movies_df['genres'] = movies_df['genres'].fillna('')
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies_df['genres'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Movie ID to index mapping
movie_indices = pd.Series(movies_df.index, index=movies_df['movieId']).to_dict()
index_to_movieId = pd.Series(movies_df['movieId'].values, index=movies_df.index).to_dict()

print("✅ Content-Based model ready!")

# Create user-item matrix for collaborative filtering
print("Creating Collaborative Filtering model...")
user_item_matrix = ratings_df.pivot_table(
    index='userId',
    columns='movieId', 
    values='rating'
).fillna(0)

user_similarity = cosine_similarity(user_item_matrix)
user_similarity_df = pd.DataFrame(
    user_similarity,
    index=user_item_matrix.index,
    columns=user_item_matrix.index
)

print("✅ Collaborative Filtering model ready!")

print("✅ Flask API Ready!")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'ML Service is running',
        'total_ratings': len(ratings_df),
        'total_movies': len(movies_df)
    })

@app.route('/api/temporal/trends', methods=['GET'])
def get_temporal_trends():
    """Get temporal rating trends"""
    try:
        trends = temporal_analyzer.analyze_rating_trends()
        
        # Convert multi-index DataFrames to simple format
        yearly_data = trends['yearly'].reset_index().to_dict('records')
        monthly_data = trends['monthly'].reset_index().to_dict('records')
        dayofweek_data = trends['dayofweek'].reset_index().to_dict('records')
        
        return jsonify({
            'success': True,
            'data': {
                'yearly': yearly_data,
                'monthly': monthly_data,
                'dayofweek': dayofweek_data
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/temporal/seasonal', methods=['GET'])
def get_seasonal_patterns():
    """Get seasonal patterns"""
    try:
        seasonal = temporal_analyzer.seasonal_analysis()
        
        # Convert multi-index DataFrames to simple format
        quarterly_data = seasonal['quarterly'].reset_index().to_dict('records')
        hourly_data = seasonal['hourly'].reset_index().to_dict('records')
        
        return jsonify({
            'success': True,
            'data': {
                'quarterly': quarterly_data,
                'hourly': hourly_data,
                'peak_hour': int(seasonal['peak_hour'])
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/temporal/popular', methods=['GET'])
def get_trending_movies():
    """Get trending movies"""
    try:
        top_n = request.args.get('limit', default=20, type=int)
        trends = temporal_analyzer.detect_popularity_trends(movies_df, top_n=top_n)
        
        recent_popular = trends['recent_popular'].head(top_n)
        rising_stars = trends['rising_stars'].head(top_n)
        
        # Add movie titles to recent_popular
        recent_popular_with_titles = []
        for _, row in recent_popular.iterrows():
            movie = movies_df[movies_df['movieId'] == row['movieId']]
            if len(movie) > 0:
                recent_popular_with_titles.append({
                    'movieId': int(row['movieId']),
                    'title': movie.iloc[0]['title'],
                    'genres': movie.iloc[0]['genres'],
                    'avg_rating': float(row['avg_rating']),
                    'rating_count': int(row['rating_count'])
                })
        
        # Add movie titles to rising_stars
        rising_stars_with_titles = []
        for _, row in rising_stars.iterrows():
            movie = movies_df[movies_df['movieId'] == row['movieId']]
            if len(movie) > 0:
                rising_stars_with_titles.append({
                    'movieId': int(row['movieId']),
                    'title': movie.iloc[0]['title'],
                    'genres': movie.iloc[0]['genres'],
                    'avg_rating': float(row['avg_rating']),
                    'old_avg_rating': float(row['old_avg_rating']),
                    'rating_change': float(row['rating_change']),
                    'rating_count': int(row['rating_count'])
                })
        
        return jsonify({
            'success': True,
            'data': {
                'recent_popular': recent_popular_with_titles,
                'rising_stars': rising_stars_with_titles
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/temporal/user-weights/<int:user_id>', methods=['GET'])
def get_user_temporal_weights(user_id):
    """Get time-weighted recommendations for a user"""
    try:
        # Mock recommendations for testing
        content_recs = []
        collab_recs = []
        
        weights = temporal_analyzer.time_weighted_recommendations(
            user_id, 
            content_recs, 
            collab_recs
        )
        
        if weights is None:
            return jsonify({
                'success': False,
                'error': 'No rating history for this user'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': user_id,
                'time_weighted_avg': float(weights['time_weighted_avg']),
                'traditional_avg': float(weights['traditional_avg']),
                'adjustment': float(weights['recommendation_adjustment'])
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/temporal/report', methods=['GET'])

def generate_temporal_report():
    """Generate comprehensive temporal analysis report"""
    try:
        report_file = temporal_analyzer.generate_temporal_report()
        
        with open(report_file, 'r', encoding='utf-8') as f:
            report_content = f.read()
        
        return jsonify({
            'success': True,
            'data': {
                'report': report_content,
                'file': report_file
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommend/content-based/<int:movie_id>', methods=['GET'])
def content_based_recommendations(movie_id):
    """
    Get content-based recommendations for a movie
    """
    try:
        n_recommendations = request.args.get('limit', default=10, type=int)
        
        if movie_id not in movie_indices:
            return jsonify({
                'success': False,
                'error': 'Movie not found'
            }), 404
        
        # Get movie index
        idx = movie_indices[movie_id]
        
        # Get similarity scores
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:n_recommendations+1]
        
        # Get movie IDs
        movie_ids = [index_to_movieId[i[0]] for i in sim_scores]
        
        # Get movie details
        recommended_movies = movies_df[movies_df['movieId'].isin(movie_ids)]
        recommendations = []
        
        for _, movie in recommended_movies.iterrows():
            recommendations.append({
                'movieId': int(movie['movieId']),
                'title': movie['title'],
                'genres': movie['genres'],
                'similarity_score': float(sim_scores[len(recommendations)][1])
            })
        
        return jsonify({
            'success': True,
            'data': {
                'source_movie_id': movie_id,
                'recommendations': recommendations,
                'method': 'content-based',
                'count': len(recommendations)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommend/collaborative/<int:user_id>', methods=['GET'])
def collaborative_recommendations(user_id):
    """
    Get collaborative filtering recommendations for a user
    """
    try:
        n_recommendations = request.args.get('limit', default=10, type=int)
        
        if user_id not in user_similarity_df.index:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get similar users
        similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:21]
        
        # Get movies rated by similar users
        similar_user_ratings = ratings_df[
            ratings_df['userId'].isin(similar_users.index)
        ]
        
        # Get movies user hasn't rated
        user_rated_movies = ratings_df[ratings_df['userId'] == user_id]['movieId'].values
        
        # Calculate weighted scores
        movie_scores = {}
        for _, row in similar_user_ratings.iterrows():
            if row['movieId'] not in user_rated_movies:
                similarity = similar_users.get(row['userId'], 0)
                if row['movieId'] not in movie_scores:
                    movie_scores[row['movieId']] = {
                        'total_score': 0,
                        'total_weight': 0
                    }
                movie_scores[row['movieId']]['total_score'] += row['rating'] * similarity
                movie_scores[row['movieId']]['total_weight'] += similarity
        
        # Calculate average weighted scores
        for movie_id in movie_scores:
            if movie_scores[movie_id]['total_weight'] > 0:
                movie_scores[movie_id]['avg_score'] = (
                    movie_scores[movie_id]['total_score'] / 
                    movie_scores[movie_id]['total_weight']
                )
            else:
                movie_scores[movie_id]['avg_score'] = 0
        
        # Sort by score
        sorted_movies = sorted(
            movie_scores.items(),
            key=lambda x: x[1]['avg_score'],
            reverse=True
        )[:n_recommendations]
        
        # Get movie details
        recommendations = []
        for movie_id, scores in sorted_movies:
            movie = movies_df[movies_df['movieId'] == movie_id].iloc[0]
            recommendations.append({
                'movieId': int(movie_id),
                'title': movie['title'],
                'genres': movie['genres'],
                'predicted_rating': float(scores['avg_score'])
            })
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': user_id,
                'recommendations': recommendations,
                'method': 'collaborative-filtering',
                'count': len(recommendations)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommend/hybrid/<int:user_id>', methods=['GET'])
def hybrid_recommendations(user_id):
    """
    Get hybrid recommendations
    """
    try:
        n_recommendations = request.args.get('limit', default=10, type=int)
        cb_weight = request.args.get('cb_weight', default=0.6, type=float)
        cf_weight = 1 - cb_weight
        
        user_ratings = ratings_df[ratings_df['userId'] == user_id].sort_values(
            'timestamp', 
            ascending=False
        ).head(5)
        
        if len(user_ratings) == 0:
            return jsonify({
                'success': False,
                'error': 'User has no rating history'
            }), 404
        
        cb_recommendations = {}
        for _, rating in user_ratings.iterrows():
            movie_id = rating['movieId']
            if movie_id in movie_indices:
                idx = movie_indices[movie_id]
                sim_scores = list(enumerate(cosine_sim[idx]))
                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                
                for i, score in sim_scores[1:n_recommendations*2]:
                    rec_movie_id = index_to_movieId[i]
                    if rec_movie_id not in cb_recommendations:
                        cb_recommendations[rec_movie_id] = 0
                    cb_recommendations[rec_movie_id] += score * rating['rating']
        
        if cb_recommendations:
            max_cb = max(cb_recommendations.values())
            for movie_id in cb_recommendations:
                cb_recommendations[movie_id] /= max_cb
        
        cf_recommendations = {}
        if user_id in user_similarity_df.index:
            similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:21]
            similar_user_ratings = ratings_df[
                ratings_df['userId'].isin(similar_users.index)
            ]
            
            user_rated_movies = ratings_df[ratings_df['userId'] == user_id]['movieId'].values
            
            for _, row in similar_user_ratings.iterrows():
                if row['movieId'] not in user_rated_movies:
                    similarity = similar_users.get(row['userId'], 0)
                    if row['movieId'] not in cf_recommendations:
                        cf_recommendations[row['movieId']] = {
                            'score': 0,
                            'weight': 0
                        }
                    cf_recommendations[row['movieId']]['score'] += row['rating'] * similarity
                    cf_recommendations[row['movieId']]['weight'] += similarity
            
            max_cf = 0
            for movie_id in cf_recommendations:
                if cf_recommendations[movie_id]['weight'] > 0:
                    cf_recommendations[movie_id] = (
                        cf_recommendations[movie_id]['score'] / 
                        cf_recommendations[movie_id]['weight']
                    )
                    if cf_recommendations[movie_id] > max_cf:
                        max_cf = cf_recommendations[movie_id]
                else:
                    cf_recommendations[movie_id] = 0
            
            if max_cf > 0:
                for movie_id in cf_recommendations:
                    cf_recommendations[movie_id] /= max_cf
        
        hybrid_scores = {}
        all_movies = set(list(cb_recommendations.keys()) + list(cf_recommendations.keys()))
        
        for movie_id in all_movies:
            cb_score = cb_recommendations.get(movie_id, 0)
            cf_score = cf_recommendations.get(movie_id, 0)
            hybrid_scores[movie_id] = cb_weight * cb_score + cf_weight * cf_score
        
        sorted_movies = sorted(
            hybrid_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n_recommendations]
        
        recommendations = []
        for movie_id, score in sorted_movies:
            movie = movies_df[movies_df['movieId'] == movie_id].iloc[0]
            recommendations.append({
                'movieId': int(movie_id),
                'title': movie['title'],
                'genres': movie['genres'],
                'hybrid_score': float(score)
            })
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': user_id,
                'recommendations': recommendations,
                'method': 'hybrid',
                'count': len(recommendations)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/movies/search', methods=['GET'])
def search_movies():
    """
    Search movies by title or genre
    """
    try:
        query = request.args.get('q', default='', type=str)
        limit = request.args.get('limit', default=20, type=int)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter required'
            }), 400
        
        results = movies_df[
            movies_df['title'].str.contains(query, case=False, na=False) |
            movies_df['genres'].str.contains(query, case=False, na=False)
        ].head(limit)
        
        movies = []
        for _, movie in results.iterrows():
            movie_ratings = ratings_df[ratings_df['movieId'] == movie['movieId']]
            avg_rating = movie_ratings['rating'].mean() if len(movie_ratings) > 0 else 0
            
            movies.append({
                'movieId': int(movie['movieId']),
                'title': movie['title'],
                'genres': movie['genres'],
                'avgRating': float(avg_rating) if avg_rating > 0 else None,
                'ratingCount': len(movie_ratings)
            })
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'results': movies,
                'count': len(movies)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/movies', methods=['GET'])
def get_all_movies():
    """
    Get all movies with pagination
    """
    try:
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=20, type=int)
        search = request.args.get('search', default='', type=str)
        
        # Filter by search if provided
        if search:
            filtered_movies = movies_df[
                movies_df['title'].str.contains(search, case=False, na=False) |
                movies_df['genres'].str.contains(search, case=False, na=False)
            ]
        else:
            filtered_movies = movies_df
        
        # Pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_movies = filtered_movies.iloc[start_idx:end_idx]
        
        # Prepare response
        movies = []
        for _, movie in paginated_movies.iterrows():
            # Get average rating
            movie_ratings = ratings_df[ratings_df['movieId'] == movie['movieId']]
            avg_rating = movie_ratings['rating'].mean() if len(movie_ratings) > 0 else 0
            
            movies.append({
                'movieId': int(movie['movieId']),
                'title': movie['title'],
                'genres': movie['genres'].split('|') if movie['genres'] else [],
                'averageRating': float(avg_rating) if avg_rating > 0 else None,
                'ratingCount': len(movie_ratings)
            })
        
        return jsonify({
            'success': True,
            'data': {
                'movies': movies,
                'page': page,
                'limit': limit,
                'total': len(filtered_movies),
                'totalPages': (len(filtered_movies) + limit - 1) // limit
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie_by_id(movie_id):
    """
    Get movie details by ID
    """
    try:
        movie = movies_df[movies_df['movieId'] == movie_id]
        
        if len(movie) == 0:
            return jsonify({
                'success': False,
                'error': 'Movie not found'
            }), 404
        
        movie = movie.iloc[0]
        
        # Get ratings
        movie_ratings = ratings_df[ratings_df['movieId'] == movie_id]
        avg_rating = movie_ratings['rating'].mean() if len(movie_ratings) > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'movieId': int(movie['movieId']),
                'title': movie['title'],
                'genres': movie['genres'].split('|') if movie['genres'] else [],
                'averageRating': float(avg_rating) if avg_rating > 0 else None,
                'ratingCount': len(movie_ratings)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Flask ML Service")
    print("="*60)
    print(f"📊 Loaded {len(ratings_df):,} ratings")
    print(f"🎬 Loaded {len(movies_df):,} movies")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)