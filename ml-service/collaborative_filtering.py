import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math

print("="*60)
print("COLLABORATIVE FILTERING - USER-BASED")
print("="*60)

# 1. Veriyi yükle
print("\n1. Loading data...")
ratings = pd.read_csv('data/ml-latest-small/ratings.csv')
movies = pd.read_csv('data/ml-latest-small/movies.csv')

print(f"Total ratings: {len(ratings)}")
print(f"Total users: {ratings['userId'].nunique()}")
print(f"Total movies: {ratings['movieId'].nunique()}")

# 2. Train/Test split
print("\n2. Splitting data (80/20)...")
train_data, test_data = train_test_split(ratings, test_size=0.2, random_state=42)
print(f"Training set: {len(train_data)} ratings")
print(f"Test set: {len(test_data)} ratings")

# 3. User-Item matrix oluştur
print("\n3. Creating user-item matrix...")
user_item_matrix = train_data.pivot_table(
    index='userId',
    columns='movieId',
    values='rating'
).fillna(0)

print(f"Matrix shape: {user_item_matrix.shape}")
print(f"(Users x Movies): ({user_item_matrix.shape[0]} x {user_item_matrix.shape[1]})")

# 4. User-User benzerlik hesapla
print("\n4. Computing user-user similarity (cosine)...")
user_similarity = cosine_similarity(user_item_matrix)
user_similarity_df = pd.DataFrame(
    user_similarity,
    index=user_item_matrix.index,
    columns=user_item_matrix.index
)
print("Similarity matrix created!")

# 5. Öneri fonksiyonu
def predict_rating(user_id, movie_id, k=5):
    """
    Collaborative Filtering ile rating tahmini
    user_id: Kullanıcı ID
    movie_id: Film ID
    k: En benzer K kullanıcı
    """
    
    # Film matrixte var mı kontrol
    if movie_id not in user_item_matrix.columns:
        return user_item_matrix.values.mean()  # Global ortalama
    
    # User var mı kontrol
    if user_id not in user_item_matrix.index:
        return user_item_matrix[movie_id].mean()  # Film ortalaması
    
    # Benzer kullanıcıları bul
    similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:k+1]
    
    # Bu kullanıcıların bu filme verdiği puanlar
    ratings_by_similar_users = []
    similarities = []
    
    for similar_user_id, similarity in similar_users.items():
        rating = user_item_matrix.loc[similar_user_id, movie_id]
        if rating > 0:  # 0 = puan verilmemiş
            ratings_by_similar_users.append(rating)
            similarities.append(similarity)
    
    # Ağırlıklı ortalama
    if len(ratings_by_similar_users) > 0:
        weighted_sum = sum(r * s for r, s in zip(ratings_by_similar_users, similarities))
        similarity_sum = sum(similarities)
        return weighted_sum / similarity_sum if similarity_sum > 0 else user_item_matrix.values.mean()
    else:
        return user_item_matrix.values.mean()

# 6. Test set üzerinde tahmin yap
print("\n5. Making predictions on test set...")
predictions = []
actuals = []

# İlk 1000 test örneği (hızlı test için)
test_sample = test_data.head(1000)

for idx, row in test_sample.iterrows():
    user_id = row['userId']
    movie_id = row['movieId']
    actual_rating = row['rating']
    
    predicted_rating = predict_rating(user_id, movie_id, k=10)
    
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
print(f"  On a scale of 0.5-5.0 stars")

# 8. Örnek öneriler
print("\n" + "="*60)
print("SAMPLE RECOMMENDATIONS")
print("="*60)

# Rastgele bir kullanıcı seç
sample_user = ratings['userId'].sample(1).values[0]
print(f"\nUser ID: {sample_user}")

# Kullanıcının izlediği filmler
user_movies = ratings[ratings['userId'] == sample_user]['movieId'].values

print(f"Movies watched: {len(user_movies)}")

# Kullanıcının izlemediği filmler
all_movies = user_item_matrix.columns.tolist()
unwatched_movies = [m for m in all_movies if m not in user_movies]

# Her film için tahmin yap
movie_predictions = []
for movie_id in unwatched_movies[:100]:  # İlk 100 film
    pred = predict_rating(sample_user, movie_id, k=10)
    movie_predictions.append((movie_id, pred))

# En yüksek puanlı 10 film
top_10 = sorted(movie_predictions, key=lambda x: x[1], reverse=True)[:10]

print(f"\nTop 10 Recommended Movies:")
for i, (movie_id, predicted_rating) in enumerate(top_10, 1):
    movie_title = movies[movies['movieId'] == movie_id]['title'].values[0]
    print(f"{i}. {movie_title} - Predicted Rating: {predicted_rating:.2f}")

print("\n" + "="*60)
print("COLLABORATIVE FILTERING COMPLETE!")
print("="*60)