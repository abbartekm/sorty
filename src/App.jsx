import { useState, useEffect } from 'react'
import axios from 'axios'
import CaseSelection from './components/CaseSelection'
import CaseDashboard from './components/CaseDashboard'
import EmailSync from './components/EmailSync'
import './App.css'

const API_URL = 'http://localhost:8000'

function App() {
  const [view, setView] = useState('case_selection') // case_selection, case_dashboard, or email_sync
  const [selectedCase, setSelectedCase] = useState(null)
  const [cases, setCases] = useState([])

  useEffect(() => {
    fetchCases()
  }, [])

  const fetchCases = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/cases`)
      setCases(response.data.cases)
    } catch (error) {
      console.error('Error fetching cases:', error)
    }
  }

  const goToEmailSync = () => {
    setView('email_sync')
  }

  const selectCase = async (caseId) => {
    try {
      const response = await axios.get(`${API_URL}/api/cases/${caseId}`)
      setSelectedCase(response.data.case)
      setView('case_dashboard')
    } catch (error) {
      console.error('Error fetching case:', error)
    }
  }

  const backToCases = () => {
    setView('case_selection')
    setSelectedCase(null)
    fetchCases()
  }

  return (
    <div className="app">
      {view === 'case_selection' && (
        <CaseSelection 
          cases={cases} 
          onSelectCase={selectCase}
          onRefresh={goToEmailSync}
        />
      )}
      
      {view === 'case_dashboard' && selectedCase && (
        <CaseDashboard 
          case={selectedCase}
          onBack={backToCases}
        />
      )}

      {view === 'email_sync' && (
        <EmailSync 
          onBack={backToCases}
          cases={cases}
          onRefreshCases={fetchCases}
        />
      )}
    </div>
  )
}

export default App