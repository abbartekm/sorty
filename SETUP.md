# Sorty - React Frontend Setup

## **Installation Instructions**

### **1. Install Dependencies**

```bash
cd /Users/artaekhtiari/Desktop/GAR-LCIA

# Install FastAPI
pip install fastapi uvicorn

# Install React dependencies
npm install
```

### **2. Start Backend (Terminal 1)**

```bash
python backend.py
```

Backend runs on: `http://localhost:8000`

### **3. Start Frontend (Terminal 2)**

```bash
npm run dev
```

Frontend runs on: `http://localhost:3000`

### **4. Open Browser**

Navigate to: `http://localhost:3000`

---

## **File Structure**

```
/Users/artaekhtiari/Desktop/GAR-LCIA/
├── backend.py              # FastAPI backend
├── database.py             # Your existing DB
├── email_reader.py         # Your existing Gmail reader
├── scc_rag.py             # Your existing RAG system
├── package.json            # React dependencies
├── vite.config.js          # Vite config
├── index.html              # HTML entry point
└── src/
    ├── main.jsx            # React entry point
    ├── App.jsx             # Main app component
    ├── App.css
    ├── index.css           # Global styles
    └── components/
        ├── CaseDashboard.jsx    # EXACT Figma layout
        ├── CaseDashboard.css
        ├── CaseSelection.jsx
        └── CaseSelection.css
```

---

## **What's Working**

✅ **EXACT Figma design**
✅ Sorty branding
✅ Case summary card (white, shadow)
✅ Orange Attachments/Emails buttons
✅ Gray action pills
✅ Blue circular send button
✅ Chat interface
✅ Cases button (top right circle)
✅ All Python backend integrated

---

## **Next Steps After Demo**

- Add case creation modal
- Add email sync UI
- Add attachments viewer
- Polish animations
- Deploy to production

---

**Made with ❤️ for GAR-LCIA Hackathon**
