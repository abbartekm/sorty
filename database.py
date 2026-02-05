import sqlite3
import json
from datetime import datetime

class ArbitrationDB:
    def __init__(self, db_path="data/arbitration.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_name TEXT NOT NULL,
                case_reference TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER,
                sender TEXT NOT NULL,
                subject TEXT,
                body TEXT,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                extracted_info TEXT,
                FOREIGN KEY (case_id) REFERENCES cases (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER,
                filename TEXT,
                doc_type TEXT,
                summary TEXT,
                FOREIGN KEY (email_id) REFERENCES emails (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_case(self, case_name, case_reference=None):
        import datetime
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Auto-generate reference if not provided
        if not case_reference:
            # Get current year (full 4 digits)
            year = datetime.datetime.now().year
            
            # Get next case number for this year
            cursor.execute(
                "SELECT COUNT(*) FROM cases WHERE case_reference LIKE ?", 
                (f"SCC-{year}-%",)
            )
            count = cursor.fetchone()[0]
            next_num = count + 1
            
            # Generate reference: SCC-2025-001, SCC-2025-002, etc.
            case_reference = f"SCC-{year}-{next_num:03d}"
        
        cursor.execute(
            "INSERT INTO cases (case_name, case_reference) VALUES (?, ?)", 
            (case_name, case_reference)
        )
        case_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return case_id
    
    def find_case_by_reference(self, reference_pattern):
        """Find case by reference pattern (flexible matching)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Try exact match first
        cursor.execute("SELECT * FROM cases WHERE case_reference = ?", (reference_pattern,))
        case = cursor.fetchone()
        
        if not case:
            # Try partial match
            cursor.execute("SELECT * FROM cases WHERE case_reference LIKE ?", (f"%{reference_pattern}%",))
            case = cursor.fetchone()
        
        conn.close()
        return dict(case) if case else None

    def add_email(self, case_id, sender, subject, body, extracted_info=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO emails (case_id, sender, subject, body, extracted_info) VALUES (?, ?, ?, ?, ?)",
            (case_id, sender, subject, body, json.dumps(extracted_info) if extracted_info else None)
        )
        email_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return email_id
    
    def get_case_emails(self, case_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emails WHERE case_id = ? ORDER BY received_at DESC", (case_id,))
        emails = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return emails
    
    def get_all_cases(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cases ORDER BY created_at DESC")
        cases = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return cases
    
    def get_case_by_id(self, case_id):
        """Get a single case by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cases WHERE id = ?", (case_id,))
        case = cursor.fetchone()
        conn.close()
        return dict(case) if case else None

    def get_case_parties(self, case_id):
        """Get unique parties from all emails in a case"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT sender 
            FROM emails 
            WHERE case_id = ?
        """, (case_id,))
        parties = [row[0] for row in cursor.fetchall()]
        conn.close()
        return parties