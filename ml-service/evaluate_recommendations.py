# evaluate_recommendations.py

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from performance_metrics import PerformanceEvaluator
import pickle

print("Loading data...")
ratings = pd.read_csv('data/ml-latest-small/ratings.csv')
movies = pd.read_csv('data/ml-latest-small/movies.csv')

print(f"Loaded {len(ratings):,} ratings and {len(movies):,} movies\n")

# Split data: 80% train, 20% test
from sklearn.model_selection import train_test_split

train_ratings, test_ratings = train_test_split(
    ratings, 
    test_size=0.2, 
    random_state=42
)

print(f"Train set: {len(train_ratings):,} ratings")
print(f"Test set:  {len(test_ratings):,} ratings\n")

# ============================================================
# CONTENT-BASED FILTERING PREDICTIONS
# ============================================================
print("=" * 60)
print("CONTENT-BASED FILTERING EVALUATION")
print("=" * 60)

# Create TF-IDF matrix
tfidf = TfidfVectorizer(stop_words='english')
movies['genres'] = movies['genres'].fillna('')
tfidf_matrix = tfidf.fit_transform(movies['genres'])

# Calculate cosine similarity
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Create movie_id to index mapping
movie_indices = pd.Series(movies.index, index=movies['movieId']).to_dict()

def get_content_based_predictions(test_df, n_similar=20):
    """Generate content-based predictions"""
    predictions = []
    
    for idx, row in test_df.iterrows():
        user_id = row['userId']
        movie_id = row['movieId']
        
        # Get user's rating history
        user_ratings = train_ratings[train_ratings['userId'] == user_id]
        
        if len(user_ratings) == 0:
            continue
        
        # Get similar movies to the test movie
        if movie_id not in movie_indices:
            continue
        
        movie_idx = movie_indices[movie_id]
        sim_scores = list(enumerate(cosine_sim[movie_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:n_similar+1]
        
        # Get movies user has rated that are similar
        similar_movie_ids = [movies.iloc[i[0]]['movieId'] for i in sim_scores]
        user_similar_ratings = user_ratings[
            user_ratings['movieId'].isin(similar_movie_ids)
        ]
        
        if len(user_similar_ratings) > 0:
            predicted_rating = user_similar_ratings['rating'].mean()
        else:
            predicted_rating = user_ratings['rating'].mean()
        
        predictions.append({
            'userId': user_id,
            'movieId': movie_id,
            'predicted_rating': predicted_rating
        })
        
        if len(predictions) % 1000 == 0:
            print(f"Processed {len(predictions)} predictions...")
    
    return pd.DataFrame(predictions)

print("\nGenerating Content-Based predictions...")
cb_predictions = get_content_based_predictions(test_ratings)

print(f"Generated {len(cb_predictions):,} predictions")

# Evaluate Content-Based
cb_evaluator = PerformanceEvaluator(cb_predictions, test_ratings, k=10)
cb_metrics = cb_evaluator.calculate_all_metrics(
    total_movies=len(movies),
    popularity_dict=None
)

# Save report
cb_evaluator.generate_metrics_report(
    cb_metrics, 
    'content_based_metrics.txt'
)

# ============================================================
# COLLABORATIVE FILTERING PREDICTIONS
# ============================================================
print("\n" + "=" * 60)
print("COLLABORATIVE FILTERING EVALUATION")
print("=" * 60)

# Create user-item matrix
user_item_matrix = train_ratings.pivot_table(
    index='userId',
    columns='movieId',
    values='rating'
).fillna(0)

# Calculate user similarity
user_similarity = cosine_similarity(user_item_matrix)
user_similarity_df = pd.DataFrame(
    user_similarity,
    index=user_item_matrix.index,
    columns=user_item_matrix.index
)

def get_collaborative_predictions(test_df, n_neighbors=20):
    """Generate collaborative filtering predictions"""
    predictions = []
    
    for idx, row in test_df.iterrows():
        user_id = row['userId']
        movie_id = row['movieId']
        
        if user_id not in user_similarity_df.index:
            continue
        
        # Get similar users
        similar_users = user_similarity_df[user_id].sort_values(
            ascending=False
        )[1:n_neighbors+1]
        
        # Get ratings from similar users for this movie
        similar_user_ratings = train_ratings[
            (train_ratings['userId'].isin(similar_users.index)) &
            (train_ratings['movieId'] == movie_id)
        ]
        
        if len(similar_user_ratings) > 0:
            # Weighted average based on similarity
            weights = similar_user_ratings['userId'].map(similar_users)
            predicted_rating = np.average(
                similar_user_ratings['rating'],
                weights=weights
            )
        else:
            # Fallback to user's average
            user_ratings = train_ratings[train_ratings['userId'] == user_id]
            predicted_rating = user_ratings['rating'].mean() if len(user_ratings) > 0 else 3.0
        
        predictions.append({
            'userId': user_id,
            'movieId': movie_id,
            'predicted_rating': predicted_rating
        })
        
        if len(predictions) % 1000 == 0:
            print(f"Processed {len(predictions)} predictions...")
    
    return pd.DataFrame(predictions)

print("\nGenerating Collaborative Filtering predictions...")
cf_predictions = get_collaborative_predictions(test_ratings)

print(f"Generated {len(cf_predictions):,} predictions")

# Evaluate Collaborative Filtering
cf_evaluator = PerformanceEvaluator(cf_predictions, test_ratings, k=10)
cf_metrics = cf_evaluator.calculate_all_metrics(
    total_movies=len(movies),
    popularity_dict=None
)

# Save report
cf_evaluator.generate_metrics_report(
    cf_metrics,
    'collaborative_metrics.txt'
)

# ============================================================
# HYBRID SYSTEM PREDICTIONS
# ============================================================
print("\n" + "=" * 60)
print("HYBRID SYSTEM EVALUATION")
print("=" * 60)

# Merge predictions (weighted combination)
cb_weight = 0.6
cf_weight = 0.4

hybrid_predictions = pd.merge(
    cb_predictions,
    cf_predictions,
    on=['userId', 'movieId'],
    how='inner',
    suffixes=('_cb', '_cf')
)

hybrid_predictions['predicted_rating'] = (
    cb_weight * hybrid_predictions['predicted_rating_cb'] +
    cf_weight * hybrid_predictions['predicted_rating_cf']
)

hybrid_predictions = hybrid_predictions[['userId', 'movieId', 'predicted_rating']]

print(f"Generated {len(hybrid_predictions):,} hybrid predictions")

# Evaluate Hybrid
hybrid_evaluator = PerformanceEvaluator(hybrid_predictions, test_ratings, k=10)
hybrid_metrics = hybrid_evaluator.calculate_all_metrics(
    total_movies=len(movies),
    popularity_dict=None
)

# Save report
hybrid_evaluator.generate_metrics_report(
    hybrid_metrics,
    'hybrid_metrics.txt'
)

# ============================================================
# COMPARISON TABLE
# ============================================================
print("\n" + "=" * 60)
print("PERFORMANCE COMPARISON")
print("=" * 60)

comparison = pd.DataFrame({
    'Metric': ['RMSE', 'MAE', 'Precision@10', 'Recall@10', 'F1-Score', 'Coverage', 'Diversity'],
    'Content-Based': [
        cb_metrics['RMSE'],
        cb_metrics['MAE'],
        cb_metrics['Precision@10'],
        cb_metrics['Recall@10'],
        cb_metrics['F1-Score'],
        cb_metrics['Coverage'],
        cb_metrics['Diversity']
    ],
    'Collaborative': [
        cf_metrics['RMSE'],
        cf_metrics['MAE'],
        cf_metrics['Precision@10'],
        cf_metrics['Recall@10'],
        cf_metrics['F1-Score'],
        cf_metrics['Coverage'],
        cf_metrics['Diversity']
    ],
    'Hybrid': [
        hybrid_metrics['RMSE'],
        hybrid_metrics['MAE'],
        hybrid_metrics['Precision@10'],
        hybrid_metrics['Recall@10'],
        hybrid_metrics['F1-Score'],
        hybrid_metrics['Coverage'],
        hybrid_metrics['Diversity']
    ]
})

print("\n")
print(comparison.to_string(index=False))

# Save comparison
comparison.to_csv('metrics_comparison.csv', index=False)
print("\n✅ Comparison saved to: metrics_comparison.csv")

print("\n" + "=" * 60)
print("✅ EVALUATION COMPLETE!")
print("=" * 60)