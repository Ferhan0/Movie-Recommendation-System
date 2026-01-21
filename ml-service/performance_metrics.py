# performance_metrics.py

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
from math import sqrt
import warnings
warnings.filterwarnings('ignore')

class PerformanceEvaluator:
    def __init__(self, predictions, actuals, k=10):
        """
        Initialize Performance Evaluator
        
        Parameters:
        predictions: DataFrame with columns ['userId', 'movieId', 'predicted_rating']
        actuals: DataFrame with columns ['userId', 'movieId', 'rating']
        k: Top-K for Precision@K and Recall@K
        """
        self.predictions = predictions
        self.actuals = actuals
        self.k = k
        
        # Merge predictions with actuals
        self.merged = pd.merge(
            predictions, 
            actuals, 
            on=['userId', 'movieId'], 
            how='inner'
        )
        
    def calculate_rmse(self):
        """Root Mean Squared Error"""
        if len(self.merged) == 0:
            return None
        
        rmse = sqrt(mean_squared_error(
            self.merged['rating'], 
            self.merged['predicted_rating']
        ))
        return rmse
    
    def calculate_mae(self):
        """Mean Absolute Error"""
        if len(self.merged) == 0:
            return None
        
        mae = mean_absolute_error(
            self.merged['rating'], 
            self.merged['predicted_rating']
        )
        return mae
    
    def calculate_precision_at_k(self, threshold=3.5):
        """
        Precision@K: What proportion of recommended items are relevant?
        
        Parameters:
        threshold: Rating threshold to consider as "relevant"
        """
        precision_scores = []
        
        for user in self.merged['userId'].unique():
            user_data = self.merged[self.merged['userId'] == user]
            
            # Sort by predicted rating (descending)
            user_data = user_data.sort_values('predicted_rating', ascending=False)
            
            # Top K predictions
            top_k = user_data.head(self.k)
            
            # How many are actually relevant (rating >= threshold)?
            relevant = len(top_k[top_k['rating'] >= threshold])
            
            precision = relevant / self.k if self.k > 0 else 0
            precision_scores.append(precision)
        
        return np.mean(precision_scores) if precision_scores else 0
    
    def calculate_recall_at_k(self, threshold=3.5):
        """
        Recall@K: What proportion of relevant items are recommended?
        
        Parameters:
        threshold: Rating threshold to consider as "relevant"
        """
        recall_scores = []
        
        for user in self.merged['userId'].unique():
            user_data = self.merged[self.merged['userId'] == user]
            
            # Total relevant items for this user
            total_relevant = len(user_data[user_data['rating'] >= threshold])
            
            if total_relevant == 0:
                continue
            
            # Sort by predicted rating (descending)
            user_data = user_data.sort_values('predicted_rating', ascending=False)
            
            # Top K predictions
            top_k = user_data.head(self.k)
            
            # How many relevant items are in top K?
            relevant_in_top_k = len(top_k[top_k['rating'] >= threshold])
            
            recall = relevant_in_top_k / total_relevant
            recall_scores.append(recall)
        
        return np.mean(recall_scores) if recall_scores else 0
    
    def calculate_f1_score(self, threshold=3.5):
        """
        F1 Score: Harmonic mean of Precision and Recall
        """
        precision = self.calculate_precision_at_k(threshold)
        recall = self.calculate_recall_at_k(threshold)
        
        if precision + recall == 0:
            return 0
        
        f1 = 2 * (precision * recall) / (precision + recall)
        return f1
    
    def calculate_coverage(self, total_movies):
        """
        Coverage: What percentage of movies are recommended?
        
        Parameters:
        total_movies: Total number of movies in catalog
        """
        unique_recommended = self.predictions['movieId'].nunique()
        coverage = (unique_recommended / total_movies) * 100
        return coverage
    
    def calculate_diversity(self):
        """
        Diversity: How diverse are the recommendations?
        Measured as average pairwise distance between recommended items
        """
        # Group by user
        diversity_scores = []
        
        for user in self.predictions['userId'].unique():
            user_recs = self.predictions[
                self.predictions['userId'] == user
            ]['movieId'].values
            
            if len(user_recs) < 2:
                continue
            
            # Calculate pairwise uniqueness
            unique_ratio = len(set(user_recs)) / len(user_recs)
            diversity_scores.append(unique_ratio)
        
        return np.mean(diversity_scores) if diversity_scores else 0
    
    def calculate_novelty(self, popularity_dict):
        """
        Novelty: How novel (non-popular) are the recommendations?
        
        Parameters:
        popularity_dict: Dictionary of {movieId: popularity_score}
        """
        novelty_scores = []
        
        for _, row in self.predictions.iterrows():
            movie_id = row['movieId']
            if movie_id in popularity_dict:
                # Lower popularity = higher novelty
                novelty = 1 - popularity_dict[movie_id]
                novelty_scores.append(novelty)
        
        return np.mean(novelty_scores) if novelty_scores else 0
    
    def calculate_all_metrics(self, total_movies=None, popularity_dict=None):
        """
        Calculate all performance metrics
        """
        print("=" * 60)
        print("PERFORMANCE METRICS EVALUATION")
        print("=" * 60)
        
        metrics = {}
        
        # Accuracy Metrics
        print("\n📊 ACCURACY METRICS:")
        metrics['RMSE'] = self.calculate_rmse()
        metrics['MAE'] = self.calculate_mae()
        print(f"  RMSE: {metrics['RMSE']:.4f}")
        print(f"  MAE:  {metrics['MAE']:.4f}")
        
        # Ranking Metrics
        print(f"\n🎯 RANKING METRICS (K={self.k}):")
        metrics[f'Precision@{self.k}'] = self.calculate_precision_at_k()
        metrics[f'Recall@{self.k}'] = self.calculate_recall_at_k()
        metrics['F1-Score'] = self.calculate_f1_score()
        print(f"  Precision@{self.k}: {metrics[f'Precision@{self.k}']:.4f}")
        print(f"  Recall@{self.k}:    {metrics[f'Recall@{self.k}']:.4f}")
        print(f"  F1-Score:     {metrics['F1-Score']:.4f}")
        
        # Beyond-Accuracy Metrics
        print("\n🌟 BEYOND-ACCURACY METRICS:")
        
        if total_movies:
            metrics['Coverage'] = self.calculate_coverage(total_movies)
            print(f"  Coverage:  {metrics['Coverage']:.2f}%")
        
        metrics['Diversity'] = self.calculate_diversity()
        print(f"  Diversity: {metrics['Diversity']:.4f}")
        
        if popularity_dict:
            metrics['Novelty'] = self.calculate_novelty(popularity_dict)
            print(f"  Novelty:   {metrics['Novelty']:.4f}")
        
        print("\n" + "=" * 60)
        
        return metrics
    
    def generate_metrics_report(self, metrics, output_file='performance_metrics_report.txt'):
        """
        Generate comprehensive metrics report
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("PERFORMANCE METRICS REPORT\n")
            f.write("Movie Recommendation System\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("1. ACCURACY METRICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"RMSE (Root Mean Squared Error): {metrics.get('RMSE', 'N/A')}\n")
            f.write(f"MAE (Mean Absolute Error):      {metrics.get('MAE', 'N/A')}\n\n")
            
            f.write("2. RANKING METRICS\n")
            f.write("-" * 80 + "\n")
            k = self.k
            f.write(f"Precision@{k}: {metrics.get(f'Precision@{k}', 'N/A')}\n")
            f.write(f"Recall@{k}:    {metrics.get(f'Recall@{k}', 'N/A')}\n")
            f.write(f"F1-Score:      {metrics.get('F1-Score', 'N/A')}\n\n")
            
            f.write("3. BEYOND-ACCURACY METRICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Coverage:  {metrics.get('Coverage', 'N/A')}\n")
            f.write(f"Diversity: {metrics.get('Diversity', 'N/A')}\n")
            f.write(f"Novelty:   {metrics.get('Novelty', 'N/A')}\n\n")
            
            f.write("4. INTERPRETATION\n")
            f.write("-" * 80 + "\n")
            f.write("• Lower RMSE/MAE = Better prediction accuracy\n")
            f.write("• Higher Precision/Recall/F1 = Better ranking quality\n")
            f.write("• Higher Coverage = More movies recommended\n")
            f.write("• Higher Diversity = Less repetitive recommendations\n")
            f.write("• Higher Novelty = More long-tail recommendations\n")
        
        print(f"\n✅ Report saved to: {output_file}")
        return output_file


def test_performance_metrics():
    """
    Test performance metrics with sample data
    """
    print("\n🧪 TESTING PERFORMANCE METRICS MODULE\n")
    
    # Create sample predictions and actuals
    np.random.seed(42)
    
    n_samples = 1000
    predictions = pd.DataFrame({
        'userId': np.random.randint(1, 100, n_samples),
        'movieId': np.random.randint(1, 500, n_samples),
        'predicted_rating': np.random.uniform(1, 5, n_samples)
    })
    
    actuals = pd.DataFrame({
        'userId': predictions['userId'],
        'movieId': predictions['movieId'],
        'rating': predictions['predicted_rating'] + np.random.normal(0, 0.5, n_samples)
    })
    actuals['rating'] = actuals['rating'].clip(1, 5)
    
    # Initialize evaluator
    evaluator = PerformanceEvaluator(predictions, actuals, k=10)
    
    # Calculate metrics
    metrics = evaluator.calculate_all_metrics(
        total_movies=500,
        popularity_dict=None
    )
    
    # Generate report
    evaluator.generate_metrics_report(metrics)
    
    print("\n✅ Performance Metrics Test Complete!")


if __name__ == "__main__":
    test_performance_metrics()