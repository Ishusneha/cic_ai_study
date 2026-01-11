import { useState, useEffect } from 'react'
import { generateQuiz, submitQuiz, getQuizHistory } from '../services/api'
import './Quiz.css'

function Quiz() {
  const [numQuestions, setNumQuestions] = useState(5)
  const [questionType, setQuestionType] = useState('mcq')
  const [topic, setTopic] = useState('')
  const [generating, setGenerating] = useState(false)
  const [currentQuiz, setCurrentQuiz] = useState(null)
  const [answers, setAnswers] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  const [quizHistory, setQuizHistory] = useState([])

  useEffect(() => {
    loadQuizHistory()
  }, [])

  const loadQuizHistory = async () => {
    try {
      const data = await getQuizHistory()
      setQuizHistory(data.quizzes || [])
    } catch (error) {
      console.error('Failed to load quiz history:', error)
    }
  }

  const handleGenerate = async () => {
    setGenerating(true)
    setResult(null)
    setCurrentQuiz(null)
    setAnswers({})

    try {
      const quiz = await generateQuiz(numQuestions, questionType, topic || null)
      setCurrentQuiz(quiz)
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to generate quiz. Please try again.')
    } finally {
      setGenerating(false)
    }
  }

  const handleAnswerChange = (questionIndex, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionIndex]: answer
    }))
  }

  const handleSubmit = async () => {
    if (!currentQuiz) return

    const allAnswered = currentQuiz.questions.every((_, idx) => answers[idx] !== undefined && answers[idx] !== '')
    if (!allAnswered) {
      alert('Please answer all questions before submitting.')
      return
    }

    setSubmitting(true)

    try {
      const result = await submitQuiz(currentQuiz.quiz_id, answers)
      setResult(result)
      setCurrentQuiz(null)
      setAnswers({})
      loadQuizHistory()
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to submit quiz. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="quiz-container">
      <div className="quiz-header">
        <h2>📝 Quiz Generator</h2>
        <p>Generate practice questions from your study materials</p>
      </div>

      <div className="quiz-layout">
        <div className="quiz-main">
          {!currentQuiz && !result && (
            <div className="quiz-generator-card">
              <h3>Generate New Quiz</h3>
              <div className="form-group">
                <label>Number of Questions</label>
                <input
                  type="range"
                  min="3"
                  max="20"
                  value={numQuestions}
                  onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                />
                <span className="range-value">{numQuestions}</span>
              </div>

              <div className="form-group">
                <label>Question Type</label>
                <select
                  value={questionType}
                  onChange={(e) => setQuestionType(e.target.value)}
                >
                  <option value="mcq">Multiple Choice</option>
                  <option value="short_answer">Short Answer</option>
                  <option value="mixed">Mixed</option>
                </select>
              </div>

              <div className="form-group">
                <label>Topic (optional)</label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g., Photosynthesis, Chapter 3"
                />
              </div>

              <button
                onClick={handleGenerate}
                disabled={generating}
                className="generate-button"
              >
                {generating ? 'Generating...' : 'Generate Quiz'}
              </button>
            </div>
          )}

          {currentQuiz && (
            <div className="quiz-card">
              <h3>Current Quiz</h3>
              {currentQuiz.questions.map((question, idx) => (
                <div key={idx} className="question-card">
                  <h4>Question {idx + 1}</h4>
                  <p className="question-text">{question.question}</p>

                  {question.question_type === 'mcq' ? (
                    <div className="options">
                      {question.options.map((option, optIdx) => (
                        <label key={optIdx} className="option-label">
                          <input
                            type="radio"
                            name={`question-${idx}`}
                            value={option}
                            checked={answers[idx] === option}
                            onChange={() => handleAnswerChange(idx, option)}
                          />
                          <span>{option}</span>
                        </label>
                      ))}
                    </div>
                  ) : (
                    <textarea
                      value={answers[idx] || ''}
                      onChange={(e) => handleAnswerChange(idx, e.target.value)}
                      placeholder="Type your answer here..."
                      className="answer-textarea"
                      rows="4"
                    />
                  )}
                </div>
              ))}

              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="submit-button"
              >
                {submitting ? 'Submitting...' : 'Submit Quiz'}
              </button>
            </div>
          )}

          {result && (
            <div className="result-card">
              <h3>Quiz Results</h3>
              <div className="score-display">
                <h2>Score: {result.score.toFixed(1)}%</h2>
                <p>{result.correct_answers} out of {result.total_questions} correct</p>
              </div>

              <div className="results-list">
                {Object.entries(result.results || {}).map(([idx, res]) => (
                  <div key={idx} className={`result-item ${res.correct ? 'correct' : 'incorrect'}`}>
                    <h4>Question {parseInt(idx) + 1}</h4>
                    <p><strong>Question:</strong> {res.question}</p>
                    <p><strong>Your Answer:</strong> {res.user_answer}</p>
                    <p><strong>Correct Answer:</strong> {res.correct_answer}</p>
                    <span className="result-badge">
                      {res.correct ? '✅ Correct' : '❌ Incorrect'}
                    </span>
                  </div>
                ))}
              </div>

              <button
                onClick={() => {
                  setResult(null)
                  setCurrentQuiz(null)
                }}
                className="new-quiz-button"
              >
                Generate New Quiz
              </button>
            </div>
          )}
        </div>

        <div className="quiz-sidebar">
          <h3>Quiz History</h3>
          {quizHistory.length === 0 ? (
            <p className="no-history">No quiz history yet</p>
          ) : (
            <div className="history-list">
              {quizHistory.slice(-5).reverse().map((quiz) => (
                <div key={quiz.quiz_id} className="history-item">
                  <p className="history-id">Quiz: {quiz.quiz_id.substring(0, 8)}...</p>
                  {quiz.score !== undefined && (
                    <p className="history-score">Score: {quiz.score.toFixed(1)}%</p>
                  )}
                  <p className="history-questions">Questions: {quiz.total_questions || 0}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Quiz

