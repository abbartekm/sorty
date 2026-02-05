import { useState } from 'react'
import './CaseSelection.css'
import NewCaseModal from './NewCaseModal' 

function CaseSelection({ cases, onSelectCase, onRefresh }) {
  const [showNewCaseModal, setShowNewCaseModal] = useState(false)
  const [syncing, setSyncing] = useState(false)

  const handleSyncEmails = async () => {
    setSyncing(true)
    try {
      await onRefresh() // This should trigger the sync
      alert('Emails synced successfully!')
    } catch (error) {
      console.error('Error syncing emails:', error)
      alert('Failed to sync emails')
    }
    setSyncing(false)
  }

  return (
    <div className="case-selection">
      <div className="selection-container">
        <h1 className="sorty-brand">Sorty</h1>
        <p className="selection-subtitle">Select a case to manage</p>

        <div className="selection-actions">
          <button 
            className="action-btn primary"
            onClick={() => setShowNewCaseModal(true)}
          >
            New Case
          </button>
          <button 
            className="action-btn" 
            onClick={handleSyncEmails}
            disabled={syncing}
          >
            {syncing ? 'Syncing...' : 'Sync Emails'}
          </button>
        </div>

        {cases.length > 0 ? (
          <div className="cases-grid">
            {cases.map(caseItem => (
              <div 
                key={caseItem.id}
                className="case-card"
                onClick={() => onSelectCase(caseItem.id)}
              >
                <h3 className="case-card-title">{caseItem.case_name}</h3>
                <p className="case-card-ref">{caseItem.case_reference || 'No reference'}</p>
                <p className="case-card-meta">{caseItem.email_count || 0} emails</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-cases">No cases yet. Create your first case or sync emails.</p>
        )}
      </div>

      {/* New Case Modal */}
      {showNewCaseModal && (
        <NewCaseModal 
          onClose={() => setShowNewCaseModal(false)}
          onSuccess={() => {
            setShowNewCaseModal(false)
            onRefresh()
          }}
        />
      )}
    </div>
  )
}

export default CaseSelection