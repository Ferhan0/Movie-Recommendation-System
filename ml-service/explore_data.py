import pandas as pd
import numpy as np

# Veriyi yükle
print("Loading data...")
movies = pd.read_csv('data/ml-latest-small/movies.csv')
ratings = pd.read_csv('data/ml-latest-small/ratings.csv')

print("\n" + "="*50)
print("MOVIES DATASET")
print("="*50)
print(f"Total movies: {len(movies)}")
print(f"\nFirst 5 movies:")
print(movies.head())

print("\n" + "="*50)
print("RATINGS DATASET")
print("="*50)
print(f"Total ratings: {len(ratings)}")
print(f"Unique users: {ratings['userId'].nunique()}")
print(f"Unique movies: {ratings['movieId'].nunique()}")
print(f"\nRating distribution:")
print(ratings['rating'].value_counts().sort_index())

print("\n" + "="*50)
print("BASIC STATISTICS")
print("="*50)
print(f"Average rating: {ratings['rating'].mean():.2f}")
print(f"Min rating: {ratings['rating'].min()}")
print(f"Max rating: {ratings['rating'].max()}")

# User-item matrix boyutu
print(f"\nUser-Item Matrix Size:")
print(f"Users: {ratings['userId'].nunique()}")
print(f"Movies: {ratings['movieId'].nunique()}")
print(f"Total possible ratings: {ratings['userId'].nunique() * ratings['movieId'].nunique():,}")
print(f"Actual ratings: {len(ratings):,}")
print(f"Sparsity: {100 * (1 - len(ratings) / (ratings['userId'].nunique() * ratings['movieId'].nunique())):.2f}%")

print("\n" + "="*50)
print("TOP 10 MOST RATED MOVIES")
print("="*50)
most_rated = ratings.groupby('movieId').size().reset_index(name='count')
most_rated = most_rated.merge(movies, on='movieId')
most_rated = most_rated.sort_values('count', ascending=False).head(10)
for idx, row in most_rated.iterrows():
    print(f"{row['title']}: {row['count']} ratings")