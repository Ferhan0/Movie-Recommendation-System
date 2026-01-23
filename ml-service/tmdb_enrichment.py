# ml-service/tmdb_enrichment.py
import requests
import pandas as pd
import json
import os
from dotenv import load_dotenv
import time

load_dotenv()
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE = 'https://api.themoviedb.org/3'

def enrich_movielens_movies():
    """MovieLens filmlerine TMDB metadata ekle"""
    print("🎬 Starting MovieLens enrichment with TMDB...")
    
    # Load MovieLens movies
    movies_df = pd.read_csv('data/ml-latest-small/movies.csv')
    print(f"📊 Loaded {len(movies_df)} MovieLens movies")
    
    enriched = []
    errors = []
    
    for idx, movie in movies_df.iterrows():
        try:
            # Extract title without year
            title = movie['title'].rsplit(' (', 1)[0].strip()
            year = None
            if '(' in movie['title'] and ')' in movie['title']:
                year_str = movie['title'].split('(')[-1].split(')')[0]
                try:
                    year = int(year_str)
                except:
                    pass
            
            # Search in TMDB
            search_params = {
                'api_key': TMDB_API_KEY,
                'query': title
            }
            if year:
                search_params['year'] = year
            
            search = requests.get(
                f"{TMDB_BASE}/search/movie",
                params=search_params
            )
            
            if search.status_code == 200 and search.json()['results']:
                tmdb_movie = search.json()['results'][0]
                enriched.append({
                    'movieId': int(movie['movieId']),
                    'title': movie['title'],
                    'genres': movie['genres'],
                    'tmdbId': tmdb_movie['id'],
                    'posterPath': tmdb_movie.get('poster_path'),
                    'backdropPath': tmdb_movie.get('backdrop_path'),
                    'overview': tmdb_movie.get('overview', ''),
                    'voteAverage': tmdb_movie.get('vote_average', 0),
                    'releaseDate': tmdb_movie.get('release_date', '')
                })
                
                if (idx + 1) % 100 == 0:
                    print(f"✅ Processed {idx + 1}/{len(movies_df)} movies")
                    time.sleep(1)  # Rate limiting
            else:
                errors.append({
                    'movieId': int(movie['movieId']),
                    'title': movie['title'],
                    'genres': movie['genres'],
                    'tmdbId': None,
                    'posterPath': None,
                    'backdropPath': None,
                    'overview': '',
                    'voteAverage': 0,
                    'releaseDate': ''
                })
        
        except Exception as e:
            print(f"❌ Error processing {movie['title']}: {e}")
            errors.append({
                'movieId': int(movie['movieId']),
                'title': movie['title'],
                'genres': movie['genres'],
                'error': str(e)
            })
        
        # Rate limiting
        time.sleep(0.25)
    
    # Save enriched movies
    output_path = 'data/enriched_movies.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 Enrichment complete!")
    print(f"✅ Successfully enriched: {len(enriched)}")
    print(f"❌ Errors: {len(errors)}")
    print(f"💾 Saved to: {output_path}")
    
    # Save errors for debugging
    if errors:
        with open('data/enrichment_errors.json', 'w') as f:
            json.dump(errors, f, indent=2)
        print(f"📝 Errors saved to: data/enrichment_errors.json")
    
    return enriched

if __name__ == '__main__':
    if not TMDB_API_KEY:
        print("❌ Error: TMDB_API_KEY not found in .env file")
        exit(1)
    
    enriched = enrich_movielens_movies()
    print(f"\n✅ Total enriched movies: {len(enriched)}")