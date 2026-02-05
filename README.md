cat > README.md << 'EOF'
# Sorty - AI-Powered Arbitration Case Management 🏛️

**Intelligent case management for arbitrators with AI assistance**

![Python](https://img.shields.io/badge/Python-3.11-blue)
![React](https://img.shields.io/badge/React-18-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688)
![Claude](https://img.shields.io/badge/AI-Claude-orange)

## 🎯 What It Does

Sorty revolutionizes arbitration case management by combining smart email routing with AI-powered assistance:

- 🤖 **AI Chat Assistant** - Ask questions about your cases, get instant context-aware answers
- 📧 **Smart Email Routing** - Automatically detects case references and assigns emails to the right case
- 📊 **Automated Analysis** - Generate case summaries, email responses, and analysis frameworks with one click
- 🔍 **SCC Rules Integration** - Built-in RAG system with Stockholm Chamber of Commerce arbitration rules
- 💼 **Professional Interface** - Clean, Gmail-style inbox for case communications

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or 3.12 (NOT 3.14)
- Node.js 18+
- Anthropic API key

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/sorty.git
cd sorty

# 2. Set up Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Set up frontend
npm install

# 4. Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 5. Run the application
# Terminal 1 - Backend:
python backend.py

# Terminal 2 - Frontend:
npm run dev
```

Visit http://localhost:5173

## ✨ Key Features

### Smart Case Creation
- Auto-generates case references (e.g., SCC-2025-001)
- Create cases manually or let AI generate realistic demo cases
- Automatic party extraction from emails

### Intelligent Email Management
- Detects case references in email subjects/bodies
- Auto-assigns emails to correct cases
- Marks processed emails as read in Gmail
- AI-powered email summaries and extraction

### AI Assistant
- Context-aware responses using full case history
- Generate background summaries
- Draft email responses
- Create case analysis frameworks
- Query SCC arbitration rules with RAG system

### Professional UI
- Gmail-style sliding inbox panel
- Clean case dashboard
- Real-time chat interface
- One-click action buttons for common tasks

## 📸 Screenshots

### Case Dashboard
![Dashboard](https://via.placeholder.com/800x400?text=Add+Your+Screenshot)

### Email Sync
![Email Sync](https://via.placeholder.com/800x400?text=Add+Your+Screenshot)

### AI Chat Assistant
![Chat](https://via.placeholder.com/800x400?text=Add+Your+Screenshot)

## 🛠️ Tech Stack

**Frontend**
- React 18
- Vite
- Axios
- CSS3

**Backend**
- FastAPI
- Python 3.11
- SQLite
- Gmail API

**AI & ML**
- Anthropic Claude (Haiku & Sonnet)
- Sentence Transformers
- RAG (Retrieval-Augmented Generation)
- Vector embeddings

## 📁 Project Structure
```
sorty/
├── backend.py              # FastAPI server
├── database.py             # SQLite database layer
├── email_reader.py         # Gmail API integration
├── scc_rag_simple.py       # RAG system for SCC rules
├── case_matcher.py         # Case reference detection
├── src/
│   ├── App.jsx            # Main React application
│   ├── components/
│   │   ├── CaseSelection.jsx
│   │   ├── CaseDashboard.jsx
│   │   ├── EmailSync.jsx
│   │   └── NewCaseModal.jsx
│   └── assets/
├── data/
│   └── arbitration.db     # SQLite database (created on first run)
└── SCC_Arbitration_Rules_2023_English.pdf
```

## 🎮 Usage Guide

### Creating a Case
1. Click **"New Case"** button
2. Choose **Manual Entry** or **Generate Demo Case**
3. Fill in case details (case reference auto-generated)
4. Start managing your case!

### Syncing Emails
1. Click **"Sync Emails"** button
2. System fetches unread emails from Gmail
3. Automatically detects case references (e.g., SCC-2025-001)
4. Auto-assigns or manually select the case
5. Emails are processed and marked as read

### Using AI Assistant
1. Select a case from the dashboard
2. Type questions in the chat: 
   - "Summarize the dispute"
   - "What are the key deadlines?"
   - "Generate an email response to the latest submission"
3. Get instant AI-powered answers with full case context

### Action Buttons
- **Generate background summary** - Comprehensive case overview
- **Generate email response** - Draft reply to latest email
- **Generate case analysis** - Full analysis framework with legal issues

## 🔧 Configuration

### Environment Variables
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Gmail Integration (Optional)

For email syncing, you need Google Cloud credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download as `credentials.json` and place in project root

On first run, it will open a browser for authentication.

## 🚧 Known Limitations

- Gmail OAuth requires setup for production use
- SQLite database (single-user, local storage)
- Python 3.14 has compatibility issues (use 3.11-3.12)
- RAG system requires local vector database generation

## 🎯 Future Enhancements

- [ ] Multi-user support with authentication
- [ ] PostgreSQL/cloud database migration
- [ ] Document upload and OCR
- [ ] Calendar integration for deadline tracking
- [ ] Export cases to PDF reports
- [ ] Mobile responsive design
- [ ] Email template library

## 🤝 Contributing

This is a hackathon project built to demonstrate AI-powered legal case management. Feel free to fork and build upon it!

## 📄 License

MIT License - see LICENSE file for details

## 👨‍💻 Authors

Built with ❤️ for [Hackathon Name]

## 🙏 Acknowledgments

- Anthropic for Claude API
- Stockholm Chamber of Commerce for arbitration rules
- FastAPI and React communities

---

**⭐ If you found this project interesting, please star the repository!**

For questions or issues, please open a GitHub issue.
