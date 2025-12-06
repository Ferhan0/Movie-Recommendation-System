import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math

print("="*60)
print("CONTENT-BASED FILTERING")
print("="*60)

# 1. Veriyi yükle
print("\n1. Loading data...")
movies = pd.read_csv('data/ml-latest-small/movies.csv')
ratings = pd.read_csv('data/ml-latest-small/ratings.csv')

print(f"Total movies: {len(movies)}")
print(f"Total ratings: {len(ratings)}")

# 2. Film özelliklerini hazırla
print("\n2. Preparing movie features...")

# Genres'i temizle ve birleştir
movies['genres_clean'] = movies['genres'].str.replace('|', ' ')

# Her film için feature string oluştur (türler)
movies['features'] = movies['genres_clean']

print("Sample movie features:")
print(movies[['title', 'features']].head(3))

# 3. TF-IDF ile vektörlere çevir
print("\n3. Creating TF-IDF vectors...")
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['features'])

print(f"TF-IDF Matrix shape: {tfidf_matrix.shape}")
print(f"(Movies x Features): ({tfidf_matrix.shape[0]} x {tfidf_matrix.shape[1]})")

# 4. Film-Film benzerlik hesapla
print("\n4. Computing movie-movie similarity (cosine)...")
movie_similarity = cosine_similarity(tfidf_matrix)

# DataFrame'e çevir (kolay erişim için)
movie_similarity_df = pd.DataFrame(
    movie_similarity,
    index=movies['movieId'],
    columns=movies['movieId']
)

print("Similarity matrix created!")

# 5. Öneri fonksiyonu
def get_similar_movies(movie_id, n=10):
    """
    Bir filme benzer filmleri bul
    movie_id: Film ID
    n: Kaç film döndürülecek
    """
    if movie_id not in movie_similarity_df.index:
        return []
    
    # En benzer filmleri bul (ilk film kendisi olacak, onu atla)
    similar_scores = movie_similarity_df[movie_id].sort_values(ascending=False)[1:n+1]
    
    similar_movies = []
    for similar_movie_id, similarity in similar_scores.items():
        movie_info = movies[movies['movieId'] == similar_movie_id].iloc[0]
        similar_movies.append({
            'movieId': similar_movie_id,
            'title': movie_info['title'],
            'genres': movie_info['genres'],
            'similarity': similarity
        })
    
    return similar_movies

def predict_rating_content_based(user_id, movie_id, k=10):
    """
    Content-based filtering ile rating tahmini
    user_id: Kullanıcı ID
    movie_id: Film ID
    k: Kullanıcının izlediği en benzer K film
    """
    
    # Kullanıcının daha önce puanladığı filmler
    user_ratings = ratings[ratings['userId'] == user_id]
    
    if len(user_ratings) == 0:
        return ratings['rating'].mean()  # Global ortalama
    
    if movie_id not in movie_similarity_df.index:
        return user_ratings['rating'].mean()  # Kullanıcının ortalama puanı
    
    # Kullanıcının izlediği filmlerle hedef filmin benzerliği
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
    
    # En benzer K filmi al
    similarity_rating_pairs = list(zip(similarities, user_movie_ratings))
    similarity_rating_pairs.sort(reverse=True, key=lambda x: x[0])
    top_k = similarity_rating_pairs[:k]
    
    # Ağırlıklı ortalama
    weighted_sum = sum(sim * rating for sim, rating in top_k)
    similarity_sum = sum(sim for sim, _ in top_k)
    
    if similarity_sum > 0:
        return weighted_sum / similarity_sum
    else:
        return user_ratings['rating'].mean()

# 6. Test set oluştur
print("\n5. Splitting data and making predictions...")
train_data, test_data = train_test_split(ratings, test_size=0.2, random_state=42)

print(f"Training set: {len(train_data)} ratings")
print(f"Test set: {len(test_data)} ratings")

# Sadece train data ile çalış (predict_rating_content_based için)
ratings = train_data

# Test set üzerinde tahmin
predictions = []
actuals = []

test_sample = test_data.head(1000)  # İlk 1000 örnek

for idx, row in test_sample.iterrows():
    user_id = row['userId']
    movie_id = row['movieId']
    actual_rating = row['rating']
    
    predicted_rating = predict_rating_content_based(user_id, movie_id, k=20)
    
    predictions.append(predicted_rating)
    actuals.append(actual_rating)
    
    if len(predictions) % 100 == 0:
        print(f"  Processed {len(predictions)}/{len(test_sample)} predictions...")

# 7. Performans metrikleri
print("\n" + "="*60)
print("PERFORMANCE METRICS")
print("="*60)

rmse = math.sqrt(mean_squared_error(actuals, predictions))
mae = mean_absolute_error(actuals, predictions)

print(f"RMSE (Root Mean Square Error): {rmse:.4f}")
print(f"MAE (Mean Absolute Error): {mae:.4f}")
print(f"\nInterpretation:")
print(f"  Average prediction error: ±{mae:.2f} stars")

# 8. Film benzerlik örnekleri
print("\n" + "="*60)
print("MOVIE SIMILARITY EXAMPLES")
print("="*60)

# Toy Story'ye benzer filmler
toy_story_id = movies[movies['title'].str.contains('Toy Story', case=False)].iloc[0]['movieId']
toy_story_title = movies[movies['movieId'] == toy_story_id].iloc[0]['title']

print(f"\nMovies similar to '{toy_story_title}':")
similar_to_toy_story = get_similar_movies(toy_story_id, n=5)

for i, movie in enumerate(similar_to_toy_story, 1):
    print(f"{i}. {movie['title']} (Similarity: {movie['similarity']:.3f})")
    print(f"   Genres: {movie['genres']}")

# Matrix'e benzer filmler
matrix_movies = movies[movies['title'].str.contains('Matrix', case=False)]
if len(matrix_movies) > 0:
    matrix_id = matrix_movies.iloc[0]['movieId']
    matrix_title = matrix_movies.iloc[0]['title']
    
    print(f"\nMovies similar to '{matrix_title}':")
    similar_to_matrix = get_similar_movies(matrix_id, n=5)
    
    for i, movie in enumerate(similar_to_matrix, 1):
        print(f"{i}. {movie['title']} (Similarity: {movie['similarity']:.3f})")
        print(f"   Genres: {movie['genres']}")

print("\n" + "="*60)
print("CONTENT-BASED FILTERING COMPLETE!")
print("="*60)