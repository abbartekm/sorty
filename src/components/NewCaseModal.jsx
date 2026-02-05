import { useState } from 'react'
import axios from 'axios'
import './NewCaseModal.css'

const API_URL = 'http://localhost:8000'

function NewCaseModal({ onClose, onSuccess }) {
  const [activeTab, setActiveTab] = useState('manual') // 'manual' or 'generate'
  
  // Manual entry state
  const [caseName, setCaseName] = useState('')
  const [caseReference, setCaseReference] = useState('')
  
  // Generate demo state
  const [description, setDescription] = useState('')
  const [numEmails, setNumEmails] = useState(10)
  const [timeSpan, setTimeSpan] = useState(90)
  
  const [loading, setLoading] = useState(false)

  const handleManualSubmit = async (e) => {
    e.preventDefault()
    
    if (!caseName.trim()) {
      alert('Please enter a case name')
      return
    }

    setLoading(true)
    
    try {
      await axios.post(`${API_URL}/api/cases`, {
        name: caseName,
        reference: caseReference || null
      })
      
      onSuccess()
    } catch (error) {
      console.error('Error creating case:', error)
      alert('Failed to create case')
    }
    
    setLoading(false)
  }

  const handleGenerateCase = async (e) => {
    e.preventDefault()
    
    if (!description.trim()) {
      alert('Please describe the dispute')
      return
    }

    setLoading(true)
    
    try {
      const response = await axios.post(`${API_URL}/api/cases/generate`, {
        description: description,
        num_emails: numEmails,
        time_span: timeSpan
      })
      
      alert(`Generated case successfully! Case ID: ${response.data.case_id}`)
      onSuccess()
    } catch (error) {
      console.error('Error generating case:', error)
      alert('Failed to generate case')
    }
    
    setLoading(false)
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content large" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Case</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        {/* Tabs */}
        <div className="modal-tabs">
          <button 
            className={`tab ${activeTab === 'manual' ? 'active' : ''}`}
            onClick={() => setActiveTab('manual')}
          >
            📝 Manual Entry
          </button>
          <button 
            className={`tab ${activeTab === 'generate' ? 'active' : ''}`}
            onClick={() => setActiveTab('generate')}
          >
            🤖 Generate Demo Case
          </button>
        </div>

        <div className="modal-body">
          {/* Manual Entry Tab */}
          {activeTab === 'manual' && (
            <form onSubmit={handleManualSubmit}>
              <div className="form-group">
                <label>Case Name *</label>
                <input
                  type="text"
                  placeholder="e.g., Company A vs Company B"
                  value={caseName}
                  onChange={(e) => setCaseName(e.target.value)}
                  required
                />
              </div>

                <div className="form-group">
                <label>Case Reference</label>
                <input
                    type="text"
                    placeholder="Leave blank to auto-generate (e.g., SCC-2025-001)"
                    value={caseReference}
                    onChange={(e) => setCaseReference(e.target.value)}
                />
                <small className="field-hint">💡 If left blank, a reference will be automatically generated</small>
                </div>

              <div className="modal-actions">
                <button 
                  type="button" 
                  className="btn-secondary"
                  onClick={onClose}
                  disabled={loading}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Creating...' : 'Create Case'}
                </button>
              </div>
            </form>
          )}

          {/* Generate Demo Case Tab */}
          {activeTab === 'generate' && (
            <form onSubmit={handleGenerateCase}>
              <div className="form-group">
                <label>Describe the dispute *</label>
                <textarea
                  placeholder="E.g., Construction contract dispute between Swedish contractor and Norwegian developer. Delay in project completion, quality issues with materials, payment disputes."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={5}
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Number of emails: {numEmails}</label>
                  <input
                    type="range"
                    min="5"
                    max="20"
                    value={numEmails}
                    onChange={(e) => setNumEmails(parseInt(e.target.value))}
                  />
                </div>

                <div className="form-group">
                  <label>Time span (days): {timeSpan}</label>
                  <input
                    type="range"
                    min="30"
                    max="365"
                    value={timeSpan}
                    onChange={(e) => setTimeSpan(parseInt(e.target.value))}
                  />
                </div>
              </div>

              <p className="info-text">
                ℹ️ This will generate a realistic arbitration case with AI-generated emails and parties. 
                This may take 30-60 seconds.
              </p>

              <div className="modal-actions">
                <button 
                  type="button" 
                  className="btn-secondary"
                  onClick={onClose}
                  disabled={loading}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Generating...' : '🎨 Generate Case'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}

export default NewCaseModal