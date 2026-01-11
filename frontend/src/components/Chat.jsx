import { useState, useRef, useEffect } from 'react'
import { sendChatMessage } from '../services/api'
import './Chat.css'

function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await sendChatMessage(input, conversationId)
      setConversationId(response.conversation_id)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.answer,
        sources: response.sources || []
      }])
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: error.response?.data?.detail || 'Sorry, I encountered an error. Please try again.',
        error: true
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-card">
        <h2>💬 Chat with AI Assistant</h2>
        <p className="chat-description">
          Ask questions about your uploaded study materials
        </p>

        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="empty-state">
              <p>👋 Start a conversation by asking a question about your study materials!</p>
            </div>
          )}
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-content">
                {msg.role === 'user' ? (
                  <div className="user-message">{msg.content}</div>
                ) : (
                  <div className={`assistant-message ${msg.error ? 'error-message' : ''}`}>
                    <div className="message-text">{msg.content}</div>
                    {msg.sources && msg.sources.length > 0 && !msg.error && (
                      <details className="sources">
                        <summary>Sources ({msg.sources.length})</summary>
                        <div className="sources-list">
                          {msg.sources.map((source, i) => (
                            <div key={i} className="source-item">
                              <p>{typeof source === 'string' ? (source.length > 300 ? source.substring(0, 300) + '...' : source) : (source.content?.substring(0, 300) || source)}</p>
                            </div>
                          ))}
                        </div>
                      </details>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="message assistant">
              <div className="message-content">
                <div className="loading">Thinking...</div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSend} className="chat-input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your study materials..."
            className="chat-input"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="send-button"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  )
}

export default Chat

