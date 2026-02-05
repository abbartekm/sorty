import os
import base64
import json
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pypdf

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailReader:
    def __init__(self):
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Token file stores user's access and refresh tokens
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
    
    def get_unread_emails(self, max_results=10):
        """Get unread emails from inbox"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD'],
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            emails = []
            for message in messages:
                email_data = self.get_email_details(message['id'])
                emails.append(email_data)
            
            return emails
        
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def get_email_details(self, msg_id, include_pdf_text=True):
        """Get details of a specific email including attachments

        Args:
            msg_id: The Gmail message ID
            include_pdf_text: If True, extract and include text from PDF attachments
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()

            headers = message['payload']['headers']

            # Extract subject and sender
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')

            # Extract body
            body = self.get_email_body(message['payload'])

            # Extract attachments
            attachments = self.get_attachments(message['payload'], msg_id)

            # Extract PDF text if requested
            pdf_contents = []
            if include_pdf_text and attachments:
                pdf_contents = self.get_pdf_attachments_text(msg_id, attachments)

            return {
                'id': msg_id,
                'sender': sender,
                'subject': subject,
                'body': body,
                'date': date,
                'attachments': attachments,
                'pdf_contents': pdf_contents
            }

        except Exception as e:
            print(f"Error getting email details: {e}")
            return None
    
    def get_email_by_id(self, email_id):
        """Get a specific email by ID (simplified version for assignment)"""
        try:
            message = self.service.users().messages().get(
                userId='me', 
                id=email_id,
                format='full'
            ).execute()
            
            # Parse the email
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            
            # Get body
            body = self.get_email_body(message['payload'])
            
            return {
                'id': email_id,
                'sender': sender,
                'subject': subject,
                'body': body
            }
        except Exception as e:
            print(f"Error getting email: {e}")
            return None
    
    def get_email_body(self, payload):
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
        else:
            if 'body' in payload and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    def mark_as_read(self, msg_id):
        """Mark an email as read"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error marking email as read: {e}")
            return False

    def get_attachments(self, payload, msg_id):
        """Extract attachment metadata from email payload"""
        attachments = []

        def process_parts(parts):
            for part in parts:
                filename = part.get('filename', '')
                mime_type = part.get('mimeType', '')

                # Check if this part has nested parts (multipart)
                if 'parts' in part:
                    process_parts(part['parts'])

                # Check if this is an attachment (has filename and attachment data)
                if filename:
                    attachment_id = part['body'].get('attachmentId')
                    size = part['body'].get('size', 0)

                    attachments.append({
                        'filename': filename,
                        'mime_type': mime_type,
                        'attachment_id': attachment_id,
                        'size': size,
                        'msg_id': msg_id
                    })

        if 'parts' in payload:
            process_parts(payload['parts'])

        return attachments

    def download_attachment(self, msg_id, attachment_id):
        """Download attachment data from Gmail"""
        try:
            attachment = self.service.users().messages().attachments().get(
                userId='me',
                messageId=msg_id,
                id=attachment_id
            ).execute()

            # Decode the attachment data
            data = attachment.get('data', '')
            file_data = base64.urlsafe_b64decode(data)
            return file_data

        except Exception as e:
            print(f"Error downloading attachment: {e}")
            return None

    def extract_pdf_text(self, pdf_data):
        """Extract text content from PDF binary data"""
        try:
            pdf_file = io.BytesIO(pdf_data)
            reader = pypdf.PdfReader(pdf_file)

            text_content = []
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")

            return '\n\n'.join(text_content)

        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return None

    def get_pdf_attachments_text(self, msg_id, attachments):
        """Get text content from all PDF attachments in an email"""
        pdf_texts = []

        for attachment in attachments:
            if attachment['mime_type'] == 'application/pdf' or attachment['filename'].lower().endswith('.pdf'):
                if attachment['attachment_id']:
                    pdf_data = self.download_attachment(msg_id, attachment['attachment_id'])
                    if pdf_data:
                        text = self.extract_pdf_text(pdf_data)
                        if text:
                            pdf_texts.append({
                                'filename': attachment['filename'],
                                'text': text,
                                'size': attachment['size']
                            })

        return pdf_texts