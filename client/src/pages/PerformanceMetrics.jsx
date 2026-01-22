import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import './PerformanceMetrics.css';

const PerformanceMetrics = () => {
  const [metrics] = useState({
    contentBased: {
      rmse: 1.0381,
      mae: 0.7829,
      precision: 0.5784,
      recall: 0.6399,
      f1Score: 0.6076,
      coverage: 52.78,
      diversity: 1.0000
    },
    collaborative: {
      rmse: 1.0047,
      mae: 0.7687,
      precision: 0.6202,
      recall: 0.6631,
      f1Score: 0.6409,
      coverage: 52.78,
      diversity: 1.0000
    },
    hybrid: {
      rmse: 0.9276,
      mae: 0.7117,
      precision: 0.6169,
      recall: 0.6611,
      f1Score: 0.6382,
      coverage: 52.78,
      diversity: 1.0000
    }
  });

  const comparisonData = [
    {
      metric: 'RMSE',
      'Content-Based': 1.0381,
      'Collaborative': 1.0047,
      'Hybrid': 0.9276,
      target: 1.0
    },
    {
      metric: 'MAE',
      'Content-Based': 0.7829,
      'Collaborative': 0.7687,
      'Hybrid': 0.7117
    },
    {
      metric: 'Precision@10',
      'Content-Based': 0.5784,
      'Collaborative': 0.6202,
      'Hybrid': 0.6169
    },
    {
      metric: 'Recall@10',
      'Content-Based': 0.6399,
      'Collaborative': 0.6631,
      'Hybrid': 0.6611
    },
    {
      metric: 'F1-Score',
      'Content-Based': 0.6076,
      'Collaborative': 0.6409,
      'Hybrid': 0.6382
    }
  ];

  const radarData = [
    {
      metric: 'Accuracy',
      'Content-Based': 0.65,
      'Collaborative': 0.72,
      'Hybrid': 0.85,
      fullMark: 1
    },
    {
      metric: 'Ranking',
      'Content-Based': 0.61,
      'Collaborative': 0.64,
      'Hybrid': 0.64,
      fullMark: 1
    },
    {
      metric: 'Coverage',
      'Content-Based': 0.53,
      'Collaborative': 0.53,
      'Hybrid': 0.53,
      fullMark: 1
    },
    {
      metric: 'Diversity',
      'Content-Based': 1.0,
      'Collaborative': 1.0,
      'Hybrid': 1.0,
      fullMark: 1
    }
  ];

  const getBestAlgorithm = (metric) => {
    const values = {
      cb: metrics.contentBased[metric],
      cf: metrics.collaborative[metric],
      hybrid: metrics.hybrid[metric]
    };
    
    // For RMSE and MAE, lower is better
    if (metric === 'rmse' || metric === 'mae') {
      const min = Math.min(values.cb, values.cf, values.hybrid);
      if (min === values.hybrid) return 'hybrid';
      if (min === values.cf) return 'collaborative';
      return 'content-based';
    }
    
    // For others, higher is better
    const max = Math.max(values.cb, values.cf, values.hybrid);
    if (max === values.hybrid) return 'hybrid';
    if (max === values.cf) return 'collaborative';
    return 'content-based';
  };

  return (
    <div className="performance-metrics-page">
      <div className="metrics-header">
        <h1>📊 Performance Metrics Analysis</h1>
        <p>Comprehensive evaluation of recommendation algorithms</p>
      </div>

      {/* Key Findings */}
      <div className="key-findings">
        <div className="finding-card best">
          <div className="finding-icon">🏆</div>
          <div className="finding-content">
            <h3>Best Overall</h3>
            <p className="finding-value">Hybrid System</p>
            <p className="finding-desc">RMSE: 0.9276 (10.6% better than Content-Based)</p>
          </div>
        </div>
        <div className="finding-card">
          <div className="finding-icon">🎯</div>
          <div className="finding-content">
            <h3>Best Ranking</h3>
            <p className="finding-value">Collaborative</p>
            <p className="finding-desc">F1-Score: 0.6409</p>
          </div>
        </div>
        <div className="finding-card">
          <div className="finding-icon">✅</div>
          <div className="finding-content">
            <h3>Target Achieved</h3>
            <p className="finding-value">{'RMSE < 1.0'}</p>
            <p className="finding-desc">Hybrid system meets production criteria</p>
          </div>
        </div>
      </div>

      {/* Comparison Chart */}
      <div className="metrics-section">
        <h2>Algorithm Comparison</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={comparisonData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="metric" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="Content-Based" fill="#e74c3c" />
              <Bar dataKey="Collaborative" fill="#3498db" />
              <Bar dataKey="Hybrid" fill="#2ecc71" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Radar Chart */}
      <div className="metrics-section">
        <h2>Multi-Dimensional Performance</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" />
              <PolarRadiusAxis angle={90} domain={[0, 1]} />
              <Radar name="Content-Based" dataKey="Content-Based" stroke="#e74c3c" fill="#e74c3c" fillOpacity={0.3} />
              <Radar name="Collaborative" dataKey="Collaborative" stroke="#3498db" fill="#3498db" fillOpacity={0.3} />
              <Radar name="Hybrid" dataKey="Hybrid" stroke="#2ecc71" fill="#2ecc71" fillOpacity={0.5} />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Metrics Tables */}
      <div className="metrics-section">
        <h2>Detailed Metrics Breakdown</h2>
        
        <div className="metrics-grid">
          {/* Content-Based */}
          <div className="metric-card">
            <h3>🎭 Content-Based Filtering</h3>
            <div className="metric-table">
              <div className="metric-row">
                <span className="metric-name">RMSE</span>
                <span className={`metric-value ${getBestAlgorithm('rmse') === 'content-based' ? 'best' : ''}`}>
                  {metrics.contentBased.rmse.toFixed(4)}
                </span>
              </div>
              <div className="metric-row">
                <span className="metric-name">MAE</span>
                <span className={`metric-value ${getBestAlgorithm('mae') === 'content-based' ? 'best' : ''}`}>
                  {metrics.contentBased.mae.toFixed(4)}
                </span>
              </div>
              <div className="metric-row">
                <span className="metric-name">Precision@10</span>
                <span className={`metric-value ${getBestAlgorithm('precision') === 'content-based' ? 'best' : ''}`}>
                  {metrics.contentBased.precision.toFixed(4)}
                </span>
              </div>
              <div className="metric-row">
                <span className="metric-name">Recall@10</span>
                <span className={`metric-value ${getBestAlgorithm('recall') === 'content-based' ? 'best' : ''}`}>
                  {metrics.contentBased.recall.toFixed(4)}
                </span>
              </div>
              <div className="metric-row">
                <span className="metric-name">F1-Score</span>
                <span className={`metric-value ${getBestAlgorithm('f1Score') === 'content-based' ? 'best' : ''}`}>
                  {metrics.contentBased.f1Score.toFixed(4)}
                </span>
              </div>
              <div className="metric-row">
                <span className="metric-name">Coverage</span>
                <span className="metric-value">{metrics.contentBased.coverage.toFixed(2)}%</span>
              </div>
              <div className="metric-row">
                <span className="metric-name">Diversity</span>
                <span className="metric-value">{metrics.contentBased.diversity.toFixed(4)}</span>
              </div>
            </div>
          </div>

          {/* Collaborative */}
          <div className="metric-card">
            <h3>👥 Collaborative Filtering</h3>
            <div className="metric-table">
              <div className="metric-row">
                <span className="metric-name">RMSE</span>
                <span className={`metric-value ${getBestAlgorithm('rmse') === 'collaborative' ? 'best' : ''}`}>
                  {metrics.collaborative.rmse.toFixed(4)}
                </span>
              </div>
              <div className="metric-row">
                <span className="metric-name">MAE</span>
                <span className={`metric-value ${getBestAlgorithm('mae') === 'collaborative' ? 'best' : ''}`}>
                  {metrics.collaborative.mae.toFixed(4)}
                </span>
              </div>
              <div className="metric-row">
                <span className="metric-name">Precision@10</span>
                <span className={`metric-value ${getBestAlgorithm('precision') === 'collaborative' ? 'best' : ''}`}>
                  {metrics.collaborative.precision.toFixed(4)}
                </span>
              </div>
              <div className="metric-row">
                <span className="metric-name">Recall@10</span>
                <span className={`metric-value ${getBestAlgorithm('recall') === 'collaborative' ? 'best' : ''}`}>
                  {metrics.collaborative.recall.toFixed(4)}
                </span>
              </div>
              <div className="metric-row">
                <span className="metric-name">F1-Score</span>
                <span className={`metric-value ${getBestAlgorithm('f1Score') === 'collaborative' ? 'best' : ''}`}>
                  {metrics.collaborative.f1Score.toFixed(4)}
                </span>
              </div>
              <div className="metric-row">
                <span className="metric-name">Coverage</span>
                <span className="metric-value">{metrics.collaborative.coverage.toFixed(2)}%</span>
              </div>
              <div className="metric-row">
                <span className="metric-name">Diversity</span>
                <span className="metric-value">{metrics.collaborative.diversity.toFixed(4)}</span>
              </div>
            </div>
          </div>

          {/* Hybrid */}
          <div className="metric-card highlight">
            <h3>⚡ Hybrid System</h3>
            <div className="metric-table">
              <div className="metric-row">
                <span className="metric-name">RMSE</span>
                <span className={`metric-value ${getBestAlgorithm('rmse') === 'hybrid' ? 'best' : ''}`}>
                  {metrics.hybrid.rmse.toFixed(4)}
                </span>
              </div>
              <div className="metric-row">
                <span className="metric-name">MAE</span>
                <span className={`metric-value ${getBestAlgorithm('mae') === 'hybrid' ? 'best' : ''}`}>
                  {metrics.hybrid.mae.toFixed(4)}
                </span>
              </div>
              <div className="metric-row">
                <span className="metric-name">Precision@10</span>
                <span className={`metric-value ${getBestAlgorithm('precision') === 'hybrid' ? 'best' : ''}`}>
                  {metrics.hybrid.precision.toFixed(4)}
                </span>
              </div>
              <div className="metric-row">
                <span className="metric-name">Recall@10</span>
                <span className={`metric-value ${getBestAlgorithm('recall') === 'hybrid' ? 'best' : ''}`}>
                  {metrics.hybrid.recall.toFixed(4)}
                </span>
              </div>
              <div className="metric-row">
                <span className="metric-name">F1-Score</span>
                <span className={`metric-value ${getBestAlgorithm('f1Score') === 'hybrid' ? 'best' : ''}`}>
                  {metrics.hybrid.f1Score.toFixed(4)}
                </span>
              </div>
              <div className="metric-row">
                <span className="metric-name">Coverage</span>
                <span className="metric-value">{metrics.hybrid.coverage.toFixed(2)}%</span>
              </div>
              <div className="metric-row">
                <span className="metric-name">Diversity</span>
                <span className="metric-value">{metrics.hybrid.diversity.toFixed(4)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Interpretation */}
      <div className="metrics-section interpretation">
        <h2>📖 Metrics Interpretation Guide</h2>
        <div className="interpretation-grid">
          <div className="interpretation-card">
            <h4>RMSE (Root Mean Squared Error)</h4>
            <p><strong>Lower is better</strong></p>
            <p>Measures prediction accuracy. Our hybrid system achieves 0.9276, meeting the RMSE &lt; 1.0 production target.</p>
          </div>
          <div className="interpretation-card">
            <h4>Precision@10</h4>
            <p><strong>Higher is better</strong></p>
            <p>Of top 10 recommendations, how many are relevant? Collaborative achieves 62%, meaning 6+ movies are good matches.</p>
          </div>
          <div className="interpretation-card">
            <h4>Recall@10</h4>
            <p><strong>Higher is better</strong></p>
            <p>Of all relevant movies, how many appear in top 10? Our systems achieve ~66%, capturing most user preferences.</p>
          </div>
          <div className="interpretation-card">
            <h4>F1-Score</h4>
            <p><strong>Higher is better</strong></p>
            <p>Harmonic mean of Precision and Recall. Collaborative's 0.64 shows balanced performance.</p>
          </div>
          <div className="interpretation-card">
            <h4>Coverage</h4>
            <p><strong>Higher is better</strong></p>
            <p>52.78% of movies are recommended, showing good catalog utilization without over-concentration.</p>
          </div>
          <div className="interpretation-card">
            <h4>Diversity</h4>
            <p><strong>Higher is better</strong></p>
            <p>Perfect 1.0 score means recommendations are maximally diverse, avoiding filter bubbles.</p>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="metrics-section summary">
        <h2>🎯 Summary & Conclusions</h2>
        <div className="summary-content">
          <div className="conclusion-box">
            <h3>Best Accuracy</h3>
            <p>✅ <strong>Hybrid System</strong> with RMSE of 0.9276</p>
            <p>10.6% improvement over Content-Based</p>
            <p>7.7% improvement over Collaborative</p>
          </div>
          <div className="conclusion-box">
            <h3>Best Ranking</h3>
            <p>✅ <strong>Collaborative Filtering</strong> with F1-Score of 0.6409</p>
            <p>Superior precision and recall</p>
            <p>Best for discovering relevant content</p>
          </div>
          <div className="conclusion-box">
            <h3>Production Ready</h3>
            <p>✅ <strong>Hybrid System</strong> meets all criteria</p>
            <p>RMSE &lt; 1.0 ✓</p>
            <p>Balanced performance across metrics ✓</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceMetrics;