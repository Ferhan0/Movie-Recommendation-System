# 🎬 Hybrid Movie Recommendation System

A sophisticated web-based movie recommendation platform powered by machine learning algorithms, featuring temporal analysis and comprehensive performance metrics.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-black.svg)](https://flask.palletsprojects.com/)

## 📋 Table of Contents
- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Performance Metrics](#-performance-metrics)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Technologies](#-technologies)
- [Project Structure](#-project-structure)
- [Author](#-author)

## ✨ Features

### 🎯 Recommendation Algorithms
- **Hybrid System** (RMSE: 0.9276) - Best overall accuracy
  - Combines Content-Based (60%) and Collaborative Filtering (40%)
  - Achieves 10.6% improvement over individual algorithms
- **Collaborative Filtering** (RMSE: 1.0047) - User-based recommendations
  - Finds similar users and recommends their favorites
  - Best ranking metrics (F1-Score: 0.6409)
- **Content-Based Filtering** (RMSE: 1.0381) - Genre similarity
  - TF-IDF vectorization with cosine similarity
  - Perfect for finding similar movies

### 📊 Temporal Analysis
- **Time Series Analysis** of rating trends (1996-2018)
- **Seasonal Patterns** detection (quarterly, monthly, hourly)
- **Popularity Trends** and rising stars identification
- **Time-Weighted Recommendations** with exponential decay

### 📈 Performance Metrics Dashboard
- Comprehensive evaluation across 7 metrics
- Visual comparisons with interactive charts
- Radar charts for multi-dimensional analysis
- Detailed interpretation guides

### 🎨 User Features
- User authentication with JWT
- Movie browsing and advanced search
- Personal rating system
- Watchlist management
- Responsive modern UI

## 🏗️ System Architecture
```
┌─────────────────────────────────────────────────────┐
│                   React Frontend                     │
│              (http://localhost:3000)                 │
└──────────────┬──────────────────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
┌──────────────┐  ┌──────────────────────────────┐
│  Node.js API │  │   Flask ML Service          │
│   (Port 5001)│  │   (http://localhost:5000)   │
└──────┬───────┘  └──────────┬───────────────────┘
       │                     │
       ▼                     ▼
┌──────────────┐  ┌──────────────────────────────┐
│   MongoDB    │  │  ML Models & Algorithms      │
│    Atlas     │  │  - Content-Based Filtering  │
└──────────────┘  │  - Collaborative Filtering  │
                  │  - Hybrid System            │
                  │  - Temporal Analysis        │
                  └─────────────────────────────┘
```

## 📊 Performance Metrics

### Accuracy Metrics
| Algorithm       | RMSE   | MAE    | Status |
|----------------|--------|--------|--------|
| Content-Based  | 1.0381 | 0.7829 | ✓      |
| Collaborative  | 1.0047 | 0.7687 | ✓      |
| **Hybrid**     | **0.9276** | **0.7117** | **✓ BEST** |

### Ranking Metrics (K=10)
| Algorithm       | Precision | Recall | F1-Score |
|----------------|-----------|--------|----------|
| Content-Based  | 0.5784    | 0.6399 | 0.6076   |
| **Collaborative** | **0.6202** | **0.6631** | **0.6409** |
| Hybrid         | 0.6169    | 0.6611 | 0.6382   |

### Beyond-Accuracy Metrics
- **Coverage:** 52.78% (All algorithms)
- **Diversity:** 1.0000 (Perfect score)

### Key Findings
- ✅ Hybrid system achieves **RMSE < 1.0** (production target met)
- ✅ 10.6% improvement over Content-Based filtering
- ✅ 7.7% improvement over Collaborative filtering
- ✅ Balanced performance across all metric categories

## 🚀 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (or local MongoDB)
- npm or yarn

### 1️⃣ Clone Repository
```bash
git clone https://github.com/Ferhan0/Movie-Recommendation-System.git
cd Movie-Recommendation-System
```

### 2️⃣ Backend Setup (Node.js)
```bash
cd server
npm install

# Create .env file
echo "MONGO_URI=your_mongodb_connection_string" > .env
echo "JWT_SECRET=your_secret_key" >> .env
echo "PORT=5001" >> .env

# Start server
npm start
```

### 3️⃣ ML Service Setup (Flask)
```bash
cd ml-service
pip install -r requirements.txt

# Start Flask API
python3 app.py
```

### 4️⃣ Frontend Setup (React)
```bash
cd client
npm install

# Start development server
npm start
```

### 5️⃣ Access Application
- Frontend: http://localhost:3000
- Flask API: http://localhost:5000
- Node.js API: http://localhost:5001

## 📖 Usage

### Getting Recommendations

1. **Register/Login** to the platform
2. **Rate some movies** to build your profile
3. Navigate to **Recommendations** page
4. Choose algorithm:
   - **Hybrid**: Best overall results
   - **Collaborative**: Discover new content
   - **Content-Based**: Similar to your favorites

### Exploring Analytics

1. Visit **📊 Analysis** page for temporal insights
2. View **📈 Metrics** page for algorithm performance
3. Explore rating trends, seasonal patterns, and more

## 🔌 API Documentation

### Flask ML Service Endpoints

#### Recommendations
```bash
GET /api/recommend/content-based/<movie_id>?limit=10
GET /api/recommend/collaborative/<user_id>?limit=10
GET /api/recommend/hybrid/<user_id>?limit=10
```

#### Temporal Analysis
```bash
GET /api/temporal/trends
GET /api/temporal/seasonal
GET /api/temporal/popular?limit=20
GET /api/temporal/user-weights/<user_id>
GET /api/temporal/report
```

#### Movies
```bash
GET /api/movies?page=1&limit=20&search=query
GET /api/movies/<movie_id>
GET /api/movies/search?q=query&limit=20
```

### Node.js Backend Endpoints

#### Authentication
```bash
POST /api/auth/register
POST /api/auth/login
```

#### Movies & Ratings
```bash
GET /api/movies
GET /api/movies/:id
POST /api/ratings
GET /api/ratings/user/:userId
```

## 🛠️ Technologies

### Frontend
- **React 18** - UI framework
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **React Router** - Navigation

### Backend
- **Node.js + Express** - REST API
- **MongoDB + Mongoose** - Database
- **JWT** - Authentication
- **bcrypt** - Password hashing

### ML Service
- **Flask 3.0** - Web framework
- **Scikit-learn** - Machine learning
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **TF-IDF Vectorizer** - Text processing
- **Cosine Similarity** - Recommendation engine

### Data
- **MovieLens 100K Dataset** - Rating data
- **TMDB API** - Movie metadata

## 📊 Dataset Information

### MovieLens 100K Dataset
- **100,836 ratings** from 610 users
- **9,742 movies** across multiple genres
- **Time span:** 1996-2018
- **Rating scale:** 0.5 to 5.0 stars

### Temporal Insights
- **Peak activity hour:** 20:00 (8 PM)
- **Most active year:** 2000 (10,061 ratings)
- **Highest rated year:** 2013 (avg: 3.877)
- **Best quarter:** Q4 (holiday season effect)

## 🎓 Academic Context

This project was developed as a graduation thesis at Mersin University, Computer Engineering Department.

### Project Timeline
- **Start Date:** October 9, 2025
- **Midterm Report:** December 20, 2025
- **Final Delivery:** January 14, 2026

### Supervisor
Dr. Furkan Gözükara - Mersin University

### Research Contributions
1. Comprehensive temporal analysis of user behavior
2. Hybrid recommendation system optimization
3. Multi-dimensional performance evaluation
4. Time-weighted recommendation algorithm

## 👨‍💻 Author

**Ferhan Akdağ**
- University: Mersin University
- Department: Computer Engineering

## 📄 License

This project is developed for academic purposes as part of a graduation thesis.

## 🙏 Acknowledgments

- MovieLens for the rating dataset
- TMDB for movie metadata
- Dr. Furkan Gözükara for supervision and guidance
- Mersin University Computer Engineering Department

---

**Note:** This system is designed for educational and research purposes. The recommendation algorithms demonstrate various ML techniques and their comparative performance in real-world scenarios.