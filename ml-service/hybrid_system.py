import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math

print("="*70)
print("HYBRID RECOMMENDATION SYSTEM")
print("Collaborative Filtering + Content-Based Filtering")
print("="*70)

# 1. Veriyi yükle
print("\n1. Loading data...")
movies = pd.read_csv('data/ml-latest-small/movies.csv')
ratings = pd.read_csv('data/ml-latest-small/ratings.csv')

print(f"Total movies: {len(movies)}")
print(f"Total ratings: {len(ratings)}")

# 2. Train/Test split
print("\n2. Splitting data (80/20)...")
train_data, test_data = train_test_split(ratings, test_size=0.2, random_state=42)
print(f"Training: {len(train_data)}, Test: {len(test_data)}")

# 3. Collaborative Filtering Setup
print("\n3. Setting up Collaborative Filtering...")
user_item_matrix = train_data.pivot_table(
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
print("✓ User-user similarity matrix ready")

# 4. Content-Based Setup
print("\n4. Setting up Content-Based Filtering...")
movies['genres_clean'] = movies['genres'].str.replace('|', ' ')
movies['features'] = movies['genres_clean']

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['features'])
movie_similarity = cosine_similarity(tfidf_matrix)

movie_similarity_df = pd.DataFrame(
    movie_similarity,
    index=movies['movieId'],
    columns=movies['movieId']
)
print("✓ Movie-movie similarity matrix ready")

# 5. Collaborative Filtering Prediction
def predict_collaborative(user_id, movie_id, k=10):
    """Collaborative filtering prediction"""
    if movie_id not in user_item_matrix.columns:
        return user_item_matrix.values.mean()
    
    if user_id not in user_item_matrix.index:
        return user_item_matrix[movie_id].mean()
    
    similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:k+1]
    
    ratings_by_similar = []
    similarities = []
    
    for sim_user_id, similarity in similar_users.items():
        rating = user_item_matrix.loc[sim_user_id, movie_id]
        if rating > 0:
            ratings_by_similar.append(rating)
            similarities.append(similarity)
    
    if len(ratings_by_similar) > 0:
        weighted_sum = sum(r * s for r, s in zip(ratings_by_similar, similarities))
        similarity_sum = sum(similarities)
        return weighted_sum / similarity_sum if similarity_sum > 0 else user_item_matrix.values.mean()
    else:
        return user_item_matrix.values.mean()

# 6. Content-Based Prediction
def predict_content_based(user_id, movie_id, k=20):
    """Content-based filtering prediction"""
    user_ratings = train_data[train_data['userId'] == user_id]
    
    if len(user_ratings) == 0:
        return train_data['rating'].mean()
    
    if movie_id not in movie_similarity_df.index:
        return user_ratings['rating'].mean()
    
    similarities = []
    user_movie_ratings = []
    
    for _, row in user_ratings.iterrows():
        rated_movie_id = row['movieId']
        if rated_movie_id in movie_similarity_df.index:
            similarity = movie_similarity_df.loc[movie_id, rated_movie_id]
            similarities.append(similarity)
            user_movie_ratings.append(row['rating'])
    
    if len(similarities) == 0:
        return user_ratings['rating'].mean()
    
    similarity_rating_pairs = list(zip(similarities, user_movie_ratings))
    similarity_rating_pairs.sort(reverse=True, key=lambda x: x[0])
    top_k = similarity_rating_pairs[:k]
    
    weighted_sum = sum(sim * rating for sim, rating in top_k)
    similarity_sum = sum(sim for sim, _ in top_k)
    
    return weighted_sum / similarity_sum if similarity_sum > 0 else user_ratings['rating'].mean()

# 7. Hybrid Prediction
def predict_hybrid(user_id, movie_id, w_collab=0.5, w_content=0.5):
    """
    Hybrid prediction combining both methods
    w_collab: weight for collaborative filtering
    w_content: weight for content-based filtering
    """
    cf_score = predict_collaborative(user_id, movie_id)
    cb_score = predict_content_based(user_id, movie_id)
    
    return w_collab * cf_score + w_content * cb_score

# 8. Test different weight combinations
print("\n5. Testing different weight combinations...")
print("-" * 70)

weight_combinations = [
    (1.0, 0.0, "Collaborative Only"),
    (0.0, 1.0, "Content-Based Only"),
    (0.5, 0.5, "Equal Weights"),
    (0.7, 0.3, "Collaborative Heavy"),
    (0.3, 0.7, "Content-Based Heavy"),
]

test_sample = test_data.head(500)  # 500 örnek test
results = []

for w_cf, w_cb, name in weight_combinations:
    print(f"\nTesting: {name} (CF={w_cf}, CB={w_cb})")
    
    predictions = []
    actuals = []
    
    for idx, row in test_sample.iterrows():
        pred = predict_hybrid(row['userId'], row['movieId'], w_cf, w_cb)
        predictions.append(pred)
        actuals.append(row['rating'])
    
    rmse = math.sqrt(mean_squared_error(actuals, predictions))
    mae = mean_absolute_error(actuals, predictions)
    
    results.append({
        'name': name,
        'w_cf': w_cf,
        'w_cb': w_cb,
        'rmse': rmse,
        'mae': mae
    })
    
    print(f"  RMSE: {rmse:.4f}, MAE: {mae:.4f}")

# 9. Best configuration
print("\n" + "="*70)
print("RESULTS SUMMARY")
print("="*70)

results_df = pd.DataFrame(results)
results_df = results_df.sort_values('rmse')

print("\nRanked by RMSE (Lower is Better):")
for idx, row in results_df.iterrows():
    print(f"{row['name']:25s} - RMSE: {row['rmse']:.4f}, MAE: {row['mae']:.4f}")

best_config = results_df.iloc[0]
print(f"\n🏆 BEST CONFIGURATION:")
print(f"   {best_config['name']}")
print(f"   Weights: CF={best_config['w_cf']}, CB={best_config['w_cb']}")
print(f"   RMSE: {best_config['rmse']:.4f}")
print(f"   MAE: {best_config['mae']:.4f}")

# 10. Sample hybrid recommendations
print("\n" + "="*70)
print("SAMPLE HYBRID RECOMMENDATIONS")
print("="*70)

sample_user = train_data['userId'].sample(1).values[0]
user_movies = train_data[train_data['userId'] == sample_user]['movieId'].values

print(f"\nUser ID: {sample_user}")
print(f"Movies rated: {len(user_movies)}")

# Öneri üret
all_movies = movie_similarity_df.columns.tolist()
unwatched = [m for m in all_movies if m not in user_movies]

movie_scores = []
for movie_id in unwatched[:200]:  # İlk 200 film
    score = predict_hybrid(
        sample_user, 
        movie_id, 
        w_collab=best_config['w_cf'], 
        w_content=best_config['w_cb']
    )
    movie_scores.append((movie_id, score))

# Top 10
top_10 = sorted(movie_scores, key=lambda x: x[1], reverse=True)[:10]

print(f"\nTop 10 Recommendations (Using Best Config):")
for i, (movie_id, score) in enumerate(top_10, 1):
    movie_title = movies[movies['movieId'] == movie_id]['title'].values[0]
    movie_genres = movies[movies['movieId'] == movie_id]['genres'].values[0]
    print(f"{i}. {movie_title}")
    print(f"   Predicted Rating: {score:.2f} | Genres: {movie_genres}")

print("\n" + "="*70)
print("HYBRID SYSTEM COMPLETE!")
print("="*70)