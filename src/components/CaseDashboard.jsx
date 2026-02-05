import { useState } from 'react'
import axios from 'axios'
import './CaseDashboard.css'

const API_URL = 'http://localhost:8000'

function CaseDashboard({ case: caseData, onBack }) {
  const [chatMessages, setChatMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [generatedContent, setGeneratedContent] = useState(null)
  const [showEmailInbox, setShowEmailInbox] = useState(false)

  const sendMessage = async () => {
    if (!chatInput.trim()) return
    
    setLoading(true)
    const userMessage = chatInput
    setChatInput('')
    
    // Add user message
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }])
    
    try {
      const response = await axios.post(`${API_URL}/api/chat`, {
        case_id: caseData.id,
        message: userMessage
      })
      
      // Add AI response
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data.response 
      }])
    } catch (error) {
      console.error('Error sending message:', error)
    }
    
    setLoading(false)
  }

  const handleAction = async (actionText) => {
    // Send the button text as a chat message
    setChatInput('')
    setChatMessages(prev => [...prev, { role: 'user', content: actionText }])
    setLoading(true)
    
    try {
      const response = await axios.post(`${API_URL}/api/chat`, {
        case_id: caseData.id,
        message: actionText
      })
      
      // Add AI response
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data.response 
      }])
    } catch (error) {
      console.error('Error sending message:', error)
    }
    
    setLoading(false)
  }

  // Get latest email summary for case summary
  const latestSummary = caseData.emails && caseData.emails[0]?.extracted_info 
    ? JSON.parse(caseData.emails[0].extracted_info).summary 
    : "A text summary of the case. Background (what has lead to the dispute).\n\nWhat stage are we in, what has the parties given us?"

  return (
    <div className="dashboard">
      {/* Cases button - top right */}
      <button className="cases-btn" onClick={onBack}>
        Cases
      </button>

      <div className={`dashboard-container ${showEmailInbox ? 'inbox-open' : ''}`}>
        {/* Sorty branding */}
        <h1 className="sorty-brand">Sorty</h1>

        {/* Case header */}
        <div className="case-header">
          <div className="case-info">
            <span className="case-label">Case {caseData.case_reference || 'XXYY'}</span>
            <span className="case-parties">{caseData.case_name}</span>
          </div>
          <div className="case-info">
            <span className="case-label">Location:</span>
            <span className="case-detail">Your Role: Arbitrator</span>
          </div>
        </div>

        {/* Main content - two columns */}
        <div className="dashboard-grid">
          {/* LEFT: Summary card */}
          <div className="summary-section">
            <div className="summary-card">
              <h3 className="summary-title">Case Summary</h3>
              <p className="summary-text">{latestSummary}</p>

              {/* Orange buttons */}
              <div className="orange-buttons">
                <button className="orange-btn">Attachments</button>
                <button 
                  className="orange-btn"
                  onClick={() => setShowEmailInbox(true)}
                >
                  Emails
                </button>
              </div>
            </div>
          </div>

          {/* RIGHT: Action pills */}
          <div className="actions-section">
            <button 
              className="action-pill"
              onClick={() => handleAction('Generate an background summary')}
              disabled={loading}
            >
              Generate an background summary
            </button>
            <button 
              className="action-pill"
              onClick={() => handleAction('Generate an email response to latest email')}
              disabled={loading}
            >
              Generate an email response to latest email
            </button>
            <button 
              className="action-pill"
              onClick={() => handleAction('Generate an Case Analysis Framework')}
              disabled={loading}
            >
              Generate an Case Analysis Framework
            </button>
          </div>
        </div>

        {/* Chat messages */}
        {chatMessages.length > 0 && (
          <div className="chat-messages">
            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-bubble">
                  {msg.content}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Chat input - fixed at bottom */}
        <div className="chat-input-wrapper">
          <div className="chat-input-container">
            <input 
              type="text"
              placeholder="What can i help you with today?"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              disabled={loading}
            />
            <button 
              className="send-btn"
              onClick={sendMessage}
              disabled={loading || !chatInput.trim()}
            >
              →
            </button>
          </div>
        </div>
      </div>

      {/* Email Inbox Sidebar */}
      {showEmailInbox && (
        <div className="email-inbox-sidebar">
          <div className="inbox-header">
            <h2>📧 Email Inbox</h2>
            <button 
              className="close-inbox-btn"
              onClick={() => setShowEmailInbox(false)}
            >
              ×
            </button>
          </div>

          <div className="inbox-content">
            {caseData.emails && caseData.emails.length > 0 ? (
              <div className="email-list">
                {caseData.emails.map((email) => {
                  let extractedInfo = null
                  try {
                    extractedInfo = email.extracted_info ? JSON.parse(email.extracted_info) : null
                  } catch (e) {
                    console.error('Error parsing email info:', e)
                  }

                  return (
                    <div key={email.id} className="email-item">
                      <div className="email-item-header">
                        <span className="email-sender">{email.sender}</span>
                        <span className="email-date">
                          {new Date(email.received_at).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="email-subject">{email.subject}</div>
                      <div className="email-preview">
                        {extractedInfo?.summary || email.body.substring(0, 100) + '...'}
                      </div>
                      <details className="email-full">
                        <summary>Read full email</summary>
                        <div className="email-body">
                          <p><strong>From:</strong> {email.sender}</p>
                          <p><strong>Date:</strong> {email.received_at}</p>
                          <p><strong>Subject:</strong> {email.subject}</p>
                          <hr />
                          <div className="email-body-text">{email.body}</div>
                        </div>
                      </details>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="no-emails">
                <p>No emails yet for this case.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default CaseDashboard