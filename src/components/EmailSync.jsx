import { useState, useEffect } from 'react'
import axios from 'axios'
import NewCaseModal from './NewCaseModal'
import './EmailSync.css'

const API_URL = 'http://localhost:8000'

function EmailSync({ onBack, cases, onRefreshCases }) {
  const [emails, setEmails] = useState([])
  const [loading, setLoading] = useState(false)
  const [processing, setProcessing] = useState({})
  const [showNewCaseModal, setShowNewCaseModal] = useState(false)
  const [emailForNewCase, setEmailForNewCase] = useState(null)

  const fetchEmails = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_URL}/api/emails/unread`)
      setEmails(response.data.emails || [])
    } catch (error) {
      console.error('Error fetching emails:', error)
      alert('Failed to fetch emails')
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchEmails()
  }, [])

  const assignEmailToCase = async (email, caseId) => {
    setProcessing({ ...processing, [email.id]: true })
    
    try {
      await axios.post(`${API_URL}/api/emails/assign`, {
        email_id: email.id,
        case_id: caseId
      })
      
      // Remove email from list
      setEmails(emails.filter(e => e.id !== email.id))
      alert('Email assigned successfully!')
      onRefreshCases()
    } catch (error) {
      console.error('Error assigning email:', error)
      alert('Failed to assign email')
    }
    
    setProcessing({ ...processing, [email.id]: false })
  }

  const handleCreateCaseForEmail = (email) => {
    setEmailForNewCase(email)
    setShowNewCaseModal(true)
  }

  const handleNewCaseSuccess = async () => {
    setShowNewCaseModal(false)
    await onRefreshCases()
    
    // If we were creating a case for a specific email, assign it
    if (emailForNewCase) {
      // Get the newly created case (last one in the list)
      const response = await axios.get(`${API_URL}/api/cases`)
      const newCase = response.data.cases[response.data.cases.length - 1]
      
      if (newCase) {
        await assignEmailToCase(emailForNewCase, newCase.id)
      }
      
      setEmailForNewCase(null)
    }
  }

  // Extract case references from subject/body
  const extractCaseReference = (text) => {
    const match = text.match(/\b[A-Z]{2,4}-\d{4}-\d{3,4}\b/i)
    return match ? match[0] : null
  }

  const findMatchingCase = (email) => {
    const ref = extractCaseReference(email.subject + ' ' + email.body)
    if (ref) {
      return cases.find(c => c.case_reference?.toLowerCase() === ref.toLowerCase())
    }
    return null
  }

  return (
    <div className="email-sync">
      <div className="sync-header">
        <button className="back-btn" onClick={onBack}>← Back to Cases</button>
        <h1>📧 Sync Emails from Gmail</h1>
        <button className="refresh-btn" onClick={fetchEmails} disabled={loading}>
          🔄 Refresh
        </button>
      </div>

      {loading ? (
        <div className="loading">Loading emails...</div>
      ) : emails.length === 0 ? (
        <div className="no-emails">
          <p>✅ No unread emails found!</p>
          <button onClick={onBack}>Back to Cases</button>
        </div>
      ) : (
        <div className="emails-container">
          <h2>Review and Assign Emails ({emails.length})</h2>
          
          {emails.map(email => {
            const matchedCase = findMatchingCase(email)
            const caseRef = extractCaseReference(email.subject + ' ' + email.body)
            
            return (
              <div key={email.id} className="email-card">
                <div className="email-header">
                  <h3>{email.subject}</h3>
                  <span className="email-sender">From: {email.sender}</span>
                </div>

                {caseRef && (
                  <div className={`case-detection ${matchedCase ? 'matched' : 'not-matched'}`}>
                    🔍 Detected case reference: <strong>{caseRef}</strong>
                    {matchedCase && (
                      <span className="match-info">
                        ✅ Matched to: {matchedCase.case_name}
                      </span>
                    )}
                  </div>
                )}

                <div className="email-body-preview">
                  {email.body.substring(0, 200)}...
                </div>

                <div className="email-actions">
                  {matchedCase ? (
                    <button 
                      className="btn-primary"
                      onClick={() => assignEmailToCase(email, matchedCase.id)}
                      disabled={processing[email.id]}
                    >
                      {processing[email.id] ? 'Assigning...' : `✅ Auto-assign to ${matchedCase.case_name}`}
                    </button>
                  ) : (
                    <>
                      <select 
                        className="case-select"
                        onChange={(e) => {
                          if (e.target.value) {
                            assignEmailToCase(email, parseInt(e.target.value))
                          }
                        }}
                        disabled={processing[email.id]}
                      >
                        <option value="">Select a case...</option>
                        {cases.map(c => (
                          <option key={c.id} value={c.id}>
                            {c.case_name} ({c.case_reference || 'No ref'})
                          </option>
                        ))}
                      </select>
                      
                      <button 
                        className="btn-secondary"
                        onClick={() => handleCreateCaseForEmail(email)}
                      >
                        + Create New Case
                      </button>
                    </>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {showNewCaseModal && (
        <NewCaseModal 
          onClose={() => {
            setShowNewCaseModal(false)
            setEmailForNewCase(null)
          }}
          onSuccess={handleNewCaseSuccess}
        />
      )}
    </div>
  )
}

export default EmailSync