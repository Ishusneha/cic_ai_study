import { useState, useEffect } from 'react'
import { getProgress } from '../services/api'
import './Progress.css'

function Progress() {
  const [progress, setProgress] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProgress()
  }, [])

  const loadProgress = async () => {
    try {
      setLoading(true)
      const data = await getProgress()
      setProgress(data)
    } catch (error) {
      console.error('Failed to load progress:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="progress-container">
        <div className="progress-card">
          <p>Loading progress...</p>
        </div>
      </div>
    )
  }

  if (!progress) {
    return (
      <div className="progress-container">
        <div className="progress-card">
          <p>Failed to load progress data</p>
        </div>
      </div>
    )
  }

  return (
    <div className="progress-container">
      <div className="progress-header">
        <h2>📈 Learning Progress</h2>
        <p>Track your learning progress and identify weak areas</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-value">{progress.total_quizzes || 0}</div>
          <div className="stat-label">Total Quizzes</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">❓</div>
          <div className="stat-value">{progress.total_questions_attempted || 0}</div>
          <div className="stat-label">Questions Attempted</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⭐</div>
          <div className="stat-value">{progress.average_score?.toFixed(1) || 0}%</div>
          <div className="stat-label">Average Score</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-value">{progress.weak_areas?.length || 0}</div>
          <div className="stat-label">Weak Areas</div>
        </div>
      </div>

      <div className="weak-areas-section">
        <h3>🎯 Weak Areas</h3>
        {progress.weak_areas && progress.weak_areas.length > 0 ? (
          <div className="weak-areas-list">
            {progress.weak_areas.map((area, idx) => (
              <div key={idx} className="weak-area-card">
                <div className="weak-area-header">
                  <h4>{area.topic}</h4>
                  <span className="accuracy-badge">{area.accuracy.toFixed(1)}%</span>
                </div>
                <div className="progress-bar-container">
                  <div
                    className="progress-bar"
                    style={{ width: `${area.accuracy}%` }}
                  />
                </div>
                <div className="weak-area-stats">
                  <span>Total: {area.total_questions}</span>
                  <span>Correct: {area.correct_answers}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-weak-areas">
            <p>🎉 No weak areas identified. Keep up the great work!</p>
          </div>
        )}
      </div>

      <div className="recent-activity-section">
        <h3>📊 Recent Activity</h3>
        {progress.recent_activity && progress.recent_activity.length > 0 ? (
          <div className="activity-list">
            {progress.recent_activity.slice().reverse().slice(0, 10).map((activity, idx) => (
              <div key={idx} className="activity-item">
                <div className="activity-info">
                  <span className="activity-id">Quiz: {activity.quiz_id?.substring(0, 8)}...</span>
                  <span className="activity-score">Score: {activity.score?.toFixed(1) || 0}%</span>
                  <span className="activity-questions">Questions: {activity.total_questions || 0}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-activity">
            <p>No recent activity. Start taking quizzes to track your progress!</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Progress

