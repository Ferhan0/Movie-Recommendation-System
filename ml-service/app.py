# app.py (veya mevcut Flask dosyanız varsa ona ekleyelim)

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from temporal_analysis import TemporalAnalyzer
import pickle
import os

app = Flask(__name__)
CORS(app)

# Load data
print("Loading data...")
ratings_df = pd.read_csv('data/ml-latest-small/ratings.csv')
movies_df = pd.read_csv('data/ml-latest-small/movies.csv')

# Initialize Temporal Analyzer
temporal_analyzer = TemporalAnalyzer(ratings_df)

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
        
        recent_popular = trends['recent_popular'].head(top_n).to_dict('records')
        rising_stars = trends['rising_stars'].head(top_n).to_dict('records')
        
        return jsonify({
            'success': True,
            'data': {
                'recent_popular': recent_popular,
                'rising_stars': rising_stars
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

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Flask ML Service")
    print("="*60)
    print(f"📊 Loaded {len(ratings_df):,} ratings")
    print(f"🎬 Loaded {len(movies_df):,} movies")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)