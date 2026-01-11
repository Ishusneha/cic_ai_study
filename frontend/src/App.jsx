import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import DocumentUpload from './components/DocumentUpload'
import Chat from './components/Chat'
import Quiz from './components/Quiz'
import Progress from './components/Progress'
import './App.css'

function Navigation() {
  const location = useLocation()
  
  const navItems = [
    { path: '/', label: '💬 Chat', icon: '💬' },
    { path: '/quiz', label: '📝 Quiz', icon: '📝' },
    { path: '/progress', label: '📈 Progress', icon: '📈' },
  ]

  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="nav-brand">
          <h1>📚 AI Study Assistant</h1>
        </div>
        <div className="nav-links">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
            >
              {item.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<><DocumentUpload /><Chat /></>} />
            <Route path="/quiz" element={<Quiz />} />
            <Route path="/progress" element={<Progress />} />
          </Routes>
        </div>
      </div>
    </Router>
  )
}

export default App

