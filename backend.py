from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from database import ArbitrationDB
from email_reader import GmailReader
from scc_rag_simple import SCCRagSystem
import json

load_dotenv()

app = FastAPI()

# CORS - allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
db = ArbitrationDB()
rag = SCCRagSystem(pdf_path="./SCC_Arbitration_Rules_2023_English.pdf")

try:
    gmail_reader = GmailReader()
except:
    gmail_reader = None

# Pydantic models
class CaseCreate(BaseModel):
    name: str
    reference: Optional[str] = None

class ChatMessage(BaseModel):
    case_id: int
    message: str

class EmailAssign(BaseModel):
    email_id: str
    case_id: int

# ========== CASES ==========

@app.get("/api/cases")
def get_cases():
    """Get all cases"""
    cases = db.get_all_cases()
    # Add email count to each case
    for case in cases:
        case['email_count'] = len(db.get_case_emails(case['id']))
    return {"cases": cases}

@app.get("/api/cases/{case_id}")
def get_case(case_id: int):
    """Get single case details"""
    case = db.get_case_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Add related data
    case['emails'] = db.get_case_emails(case_id)
    case['parties'] = db.get_case_parties(case_id)
    
    return {"case": case}

@app.post("/api/cases")
def create_case(case: CaseCreate):
    """Create new case"""
    case_id = db.create_case(case.name, case.reference)
    return {"case_id": case_id, "message": "Case created successfully"}

@app.delete("/api/cases/{case_id}")
def delete_case(case_id: int):
    """Delete a case"""
    # TODO: Implement delete in database.py
    return {"message": "Case deleted"}

# ========== EMAILS ==========

@app.get("/api/emails/unread")
def get_unread_emails():
    """Fetch unread emails from Gmail"""
    if not gmail_reader:
        raise HTTPException(status_code=500, detail="Gmail not connected")
    
    try:
        emails = gmail_reader.get_unread_emails(max_results=20)
        return {"emails": emails}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/emails/assign")
def assign_email(data: EmailAssign):
    """Assign email to case and process it"""
    if not gmail_reader:
        raise HTTPException(status_code=500, detail="Gmail not connected")
    
    try:
        # Get the email from Gmail
        email = gmail_reader.get_email_by_id(data.email_id)
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Extract info with Claude
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""Analyze this arbitration email and extract key information.

From: {email['sender']}
Subject: {email['subject']}
Body: {email['body']}

Extract the following and return ONLY a valid JSON object:
{{
    "parties_mentioned": ["list", "of", "parties"],
    "document_types": ["list", "of", "documents"],
    "key_dates": ["list", "of", "dates"],
    "action_items": ["list", "of", "actions"],
    "summary": "brief summary in 2-3 sentences"
}}"""
            }]
        )
        
        response_text = response.content[0].text.strip()
        
        # Parse JSON response
        try:
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            extracted_info = json.loads(response_text)
        except:
            extracted_info = {"summary": "Email processed"}
        
        # Save to database
        email_id = db.add_email(
            data.case_id,
            email['sender'],
            email['subject'],
            email['body'],
            extracted_info
        )
        
        # Mark as read in Gmail
        gmail_reader.mark_as_read(data.email_id)
        
        return {
            "message": "Email assigned successfully",
            "email_id": email_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cases/{case_id}/emails")
def get_case_emails(case_id: int):
    """Get all emails for a case"""
    emails = db.get_case_emails(case_id)
    return {"emails": emails}

# ========== CHAT / AI ==========

@app.post("/api/chat")
def chat(data: ChatMessage):
    """Chat with AI about a case"""
    case = db.get_case_by_id(data.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get case context
    emails = db.get_case_emails(data.case_id)
    context = f"Case: {case['case_name']} ({case.get('case_reference')})\n\n"
    context += "Recent emails:\n"
    for e in emails[:5]:
        context += f"- From {e['sender']}: {e['subject']}\n"
    
    # Check if procedural question
    is_procedural = any(word in data.message.lower() for word in 
                       ['deadline', 'rule', 'article', 'procedure', 'cost'])
    
    if is_procedural:
        # Use RAG system
        result = rag.smart_query(data.message, client, force_claude=False)
        return {
            "response": result['answer'],
            "model": result['model_used'],
            "articles": result['articles_used']
        }
    else:
        # Direct Claude call
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": f"{context}\n\nQuestion: {data.message}\n\nAnswer concisely:"
            }]
        )
        
        return {
            "response": response.content[0].text,
            "model": "Claude",
            "articles": []
        }

@app.post("/api/generate/background-summary")
def generate_background_summary(data: ChatMessage):
    """Generate background summary for case"""
    case = db.get_case_by_id(data.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    emails = db.get_case_emails(data.case_id)
    context = f"Case: {case['case_name']}\n\n"
    for e in emails[:10]:
        context += f"Email from {e['sender']}: {e['subject']}\n{e['body'][:300]}\n\n"
    
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"{context}\n\nGenerate a comprehensive background summary of this arbitration case, including:\n1. Parties involved\n2. Nature of dispute\n3. Key events and timeline\n4. Current status\n\nProvide a professional, detailed summary:"
        }]
    )
    
    return {"response": response.content[0].text}

@app.post("/api/generate/email-response")
def generate_email_response(data: ChatMessage):
    """Generate email response to latest email"""
    case = db.get_case_by_id(data.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    emails = db.get_case_emails(data.case_id)
    if not emails:
        raise HTTPException(status_code=404, detail="No emails found")
    
    latest_email = emails[0]
    
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": f"""Draft a professional email response to this arbitration email:

From: {latest_email['sender']}
Subject: {latest_email['subject']}
Body: {latest_email['body']}

Write a clear, professional response addressing the main points:"""
        }]
    )
    
    return {"response": response.content[0].text}

@app.post("/api/generate/case-analysis")
def generate_case_analysis(data: ChatMessage):
    """Generate case analysis framework"""
    case = db.get_case_by_id(data.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    emails = db.get_case_emails(data.case_id)
    context = f"Case: {case['case_name']}\n\n"
    for e in emails:
        if e.get('extracted_info'):
            try:
                info = json.loads(e['extracted_info'])
                context += f"Email summary: {info.get('summary', '')}\n"
            except:
                pass
    
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=2500,
        messages=[{
            "role": "user",
            "content": f"""{context}

Create a comprehensive Case Analysis Framework including:

1. **Key Legal Issues**: Identify the main disputes
2. **Arguments by Each Party**: Summarize positions
3. **Applicable Law/Rules**: Relevant SCC articles and legal principles
4. **Evidence Assessment**: What evidence has been presented
5. **Procedural Timeline**: Key dates and deadlines
6. **Recommendations**: Suggested next steps

Provide a structured, professional analysis:"""
        }]
    )
    
    return {"response": response.content[0].text}

# ========== CASE GENERATION ==========

class CaseGenerate(BaseModel):
    description: str
    num_emails: int = 10
    time_span: int = 60

@app.post("/api/cases/generate")
def generate_demo_case(data: CaseGenerate):
    """Generate a demo case with AI"""
    # TODO: Implement full case generation from app.py
    # For now, just create empty case
    case_id = db.create_case("Demo Case", "DEMO-001")
    return {
        "case_id": case_id,
        "message": "Demo case generated (simplified version)"
    }

# ========== HEALTH CHECK ==========

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "gmail_connected": gmail_reader is not None
    }

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Serve built frontend (after all API routes)
if os.path.exists("dist"):
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")
    
    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        # If it's an API call, let FastAPI handle it normally
        if full_path.startswith("api/"):
            return
        
        # Serve index.html for all other routes
        return FileResponse("dist/index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
