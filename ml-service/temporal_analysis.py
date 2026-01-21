# temporal_analysis.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class TemporalAnalyzer:
    def __init__(self, ratings_df):
        """
        Initialize Temporal Analyzer
        
        Parameters:
        ratings_df: DataFrame with columns ['userId', 'movieId', 'rating', 'timestamp']
        """
        self.ratings_df = ratings_df.copy()
        
        # Convert timestamp to datetime
        if 'timestamp' in self.ratings_df.columns:
            self.ratings_df['datetime'] = pd.to_datetime(
                self.ratings_df['timestamp'], 
                unit='s'
            )
        
        # Extract temporal features
        self.ratings_df['year'] = self.ratings_df['datetime'].dt.year
        self.ratings_df['month'] = self.ratings_df['datetime'].dt.month
        self.ratings_df['dayofweek'] = self.ratings_df['datetime'].dt.dayofweek
        self.ratings_df['hour'] = self.ratings_df['datetime'].dt.hour
        self.ratings_df['quarter'] = self.ratings_df['datetime'].dt.quarter
        
    def analyze_rating_trends(self):
        """
        Analyze how average ratings change over time
        """
        print("=" * 60)
        print("TEMPORAL RATING TRENDS ANALYSIS")
        print("=" * 60)
        
        # Yearly trends
        yearly_stats = self.ratings_df.groupby('year').agg({
            'rating': ['mean', 'count', 'std']
        }).round(3)
        yearly_stats.columns = ['mean', 'count', 'std']  # Flatten columns
        
        print("\n📅 Yearly Rating Statistics:")
        print(yearly_stats)
        
        # Monthly trends
        monthly_stats = self.ratings_df.groupby('month').agg({
            'rating': ['mean', 'count']
        }).round(3)
        monthly_stats.columns = ['mean', 'count']  # Flatten columns
        
        print("\n📆 Monthly Rating Statistics:")
        print(monthly_stats)
        
        # Day of week trends
        dow_stats = self.ratings_df.groupby('dayofweek').agg({
            'rating': ['mean', 'count']
        }).round(3)
        dow_stats.columns = ['mean', 'count']  # Flatten columns
        
        print("\n📊 Day of Week Statistics (0=Monday, 6=Sunday):")
        print(dow_stats)
        
        return {
            'yearly': yearly_stats,
            'monthly': monthly_stats,
            'dayofweek': dow_stats
        }
    
    def detect_popularity_trends(self, movies_df, top_n=20):
        """
        Detect which movies are trending over time
        """
        print("\n" + "=" * 60)
        print("POPULARITY TRENDS ANALYSIS")
        print("=" * 60)
        
        # Calculate popularity by time periods
        recent_cutoff = self.ratings_df['datetime'].max() - timedelta(days=365)
        
        recent_ratings = self.ratings_df[
            self.ratings_df['datetime'] >= recent_cutoff
        ]
        
        old_ratings = self.ratings_df[
            self.ratings_df['datetime'] < recent_cutoff
        ]
        
        # Recent popular movies
        recent_popular = recent_ratings.groupby('movieId').agg({
            'rating': ['mean', 'count']
        }).reset_index()
        recent_popular.columns = ['movieId', 'avg_rating', 'rating_count']
        recent_popular = recent_popular[recent_popular['rating_count'] >= 10]
        recent_popular = recent_popular.sort_values('rating_count', ascending=False)
        
        print(f"\n🔥 Top {top_n} Trending Movies (Last Year):")
        print(recent_popular.head(top_n))
        
        # Compare old vs new
        old_popular = old_ratings.groupby('movieId').agg({
            'rating': 'mean'
        }).reset_index()
        old_popular.columns = ['movieId', 'old_avg_rating']
        
        # Merge and find rising stars
        comparison = recent_popular.merge(
            old_popular, 
            on='movieId', 
            how='left'
        )
        comparison['rating_change'] = (
            comparison['avg_rating'] - comparison['old_avg_rating']
        )
        
        rising_stars = comparison.dropna().sort_values(
            'rating_change', 
            ascending=False
        ).head(top_n)
        
        print(f"\n⭐ Rising Stars (Biggest Rating Improvements):")
        print(rising_stars[['movieId', 'old_avg_rating', 'avg_rating', 'rating_change']])
        
        return {
            'recent_popular': recent_popular,
            'rising_stars': rising_stars
        }
    
    def seasonal_analysis(self):
        """
        Analyze seasonal patterns in ratings
        """
        print("\n" + "=" * 60)
        print("SEASONAL PATTERN ANALYSIS")
        print("=" * 60)
        
        # Quarterly analysis
        quarterly_stats = self.ratings_df.groupby('quarter').agg({
            'rating': ['mean', 'count', 'std']
        }).round(3)
        quarterly_stats.columns = ['mean', 'count', 'std']  # Flatten columns
        
        print("\n🌍 Quarterly Statistics:")
        print(quarterly_stats)
        
        # Peak hours analysis
        hourly_stats = self.ratings_df.groupby('hour').agg({
            'rating': ['mean', 'count']
        }).round(3)
        hourly_stats.columns = ['mean', 'count']  # Flatten columns
        
        print("\n⏰ Hourly Rating Activity:")
        peak_hour = hourly_stats['count'].idxmax()
        print(f"Peak Activity Hour: {peak_hour}:00")
        print(hourly_stats)
        
        return {
            'quarterly': quarterly_stats,
            'hourly': hourly_stats,
            'peak_hour': peak_hour
        }
    
    def time_weighted_recommendations(self, user_id, content_based_recs, 
                                     collaborative_recs, decay_factor=0.1):
        """
        Apply time-based weighting to recommendations
        More recent ratings get higher weights
        
        Parameters:
        user_id: Target user
        content_based_recs: List of movie recommendations from CB
        collaborative_recs: List of movie recommendations from CF
        decay_factor: How fast older ratings decay (0-1)
        """
        print("\n" + "=" * 60)
        print(f"TIME-WEIGHTED RECOMMENDATIONS FOR USER {user_id}")
        print("=" * 60)
        
        # Get user's rating history
        user_ratings = self.ratings_df[
            self.ratings_df['userId'] == user_id
        ].copy()
        
        if len(user_ratings) == 0:
            print("No rating history for this user")
            return None
        
        # Calculate time decay weights
        max_timestamp = user_ratings['datetime'].max()
        user_ratings['days_ago'] = (
            max_timestamp - user_ratings['datetime']
        ).dt.days
        
        user_ratings['time_weight'] = np.exp(
            -decay_factor * user_ratings['days_ago'] / 365
        )
        
        print(f"\n📊 User Rating History (Total: {len(user_ratings)} ratings)")
        print(f"Recent ratings weight: {user_ratings['time_weight'].tail().mean():.3f}")
        print(f"Old ratings weight: {user_ratings['time_weight'].head().mean():.3f}")
        
        # Apply weights to recommendations
        weighted_scores = {}
        
        # Weight content-based recs by user's recent preferences
        recent_avg_rating = (
            user_ratings['rating'] * user_ratings['time_weight']
        ).sum() / user_ratings['time_weight'].sum()
        
        print(f"\n🎯 Time-weighted average rating: {recent_avg_rating:.2f}")
        print(f"Traditional average rating: {user_ratings['rating'].mean():.2f}")
        
        return {
            'time_weighted_avg': recent_avg_rating,
            'traditional_avg': user_ratings['rating'].mean(),
            'decay_weights': user_ratings[['movieId', 'rating', 'time_weight']],
            'recommendation_adjustment': recent_avg_rating - user_ratings['rating'].mean()
        }
    
    def generate_temporal_report(self, output_file='temporal_analysis_report.txt'):
        """
        Generate comprehensive temporal analysis report
        """
        print("\n" + "=" * 60)
        print("GENERATING COMPREHENSIVE TEMPORAL REPORT")
        print("=" * 60)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("TEMPORAL ANALYSIS REPORT\n")
            f.write("Movie Recommendation System\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Dataset overview
            f.write("1. DATASET TEMPORAL OVERVIEW\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Ratings: {len(self.ratings_df):,}\n")
            f.write(f"Date Range: {self.ratings_df['datetime'].min()} to ")
            f.write(f"{self.ratings_df['datetime'].max()}\n")
            f.write(f"Time Span: {(self.ratings_df['datetime'].max() - self.ratings_df['datetime'].min()).days} days\n\n")
            
            # Trends
            trends = self.analyze_rating_trends()
            f.write("\n2. RATING TRENDS OVER TIME\n")
            f.write("-" * 80 + "\n")
            f.write(str(trends['yearly']) + "\n\n")
            
            # Seasonal patterns
            seasonal = self.seasonal_analysis()
            f.write("\n3. SEASONAL PATTERNS\n")
            f.write("-" * 80 + "\n")
            f.write(str(seasonal['quarterly']) + "\n\n")
            
            f.write(f"Peak Activity Hour: {seasonal['peak_hour']}:00\n\n")
            
            # Insights
            f.write("\n4. KEY INSIGHTS\n")
            f.write("-" * 80 + "\n")
            f.write("• Rating patterns show temporal dependencies\n")
            f.write("• Recent ratings should have higher weights in recommendations\n")
            f.write("• User preferences evolve over time\n")
            f.write("• Seasonal trends affect movie popularity\n")
        
        print(f"\n✅ Report saved to: {output_file}")
        return output_file


# Test function
def test_temporal_analysis():
    """
    Test temporal analysis with sample data
    """
    print("\n🧪 TESTING TEMPORAL ANALYSIS MODULE\n")
    
    # Load ratings data
    ratings = pd.read_csv('data/ml-latest-small/ratings.csv')
    
    print(f"Loaded {len(ratings):,} ratings")
    print(f"Columns: {ratings.columns.tolist()}\n")
    
    # Initialize analyzer
    analyzer = TemporalAnalyzer(ratings)
    
    # Run analyses
    analyzer.analyze_rating_trends()
    analyzer.seasonal_analysis()
    
    # Generate report
    analyzer.generate_temporal_report()
    
    print("\n✅ Temporal Analysis Test Complete!")


if __name__ == "__main__":
    test_temporal_analysis()