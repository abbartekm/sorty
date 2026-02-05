import json
import re
import pickle
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import vertexai
from vertexai.generative_models import GenerativeModel
import pypdf
import os

class SCCRagSystem:
    def __init__(self, pdf_path="./SCC_Arbitration_Rules_2023_English.pdf"):
        # Initialize Vertex AI
        project_id = os.getenv("GCP_PROJECT_ID")
        location = os.getenv("GCP_LOCATION", "us-central1")
        
        vertexai.init(project=project_id, location=location)
        
        # Use Gemini Flash for simple queries (cheap & fast)
        self.flash_model = GenerativeModel("gemini-2.5-flash")
        
        # Initialize components
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.pdf_path = pdf_path
        self.db_path = "./scc_vector_db.pkl"
        
        # Article categories for smart routing
        self.categories = {
            "time_periods": [4, 7, 9, 10, 28, 29, 40, 43, 47, 48],
            "costs": [7, 49, 50, 51],
            "tribunal": [16, 17, 18, 19, 20, 21, 24],
            "proceedings": [22, 23, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
            "awards": [41, 42, 43, 44, 45, 46, 47, 48],
            "commencement": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        }
        
        # Load or create database
        if os.path.exists(self.db_path):
            print("Loading existing vector database...")
            with open(self.db_path, 'rb') as f:
                self.articles_db = pickle.load(f)
        else:
            print("Processing SCC Rules PDF...")
            self.articles_db = self.process_pdf()
            with open(self.db_path, 'wb') as f:
                pickle.dump(self.articles_db, f)
    
    def extract_articles_from_pdf(self) -> List[Dict]:
        """Extract articles from SCC PDF"""
        reader = pypdf.PdfReader(self.pdf_path)
        full_text = ""
        
        # Extract all text
        for page in reader.pages:
            full_text += page.extract_text()
        
        articles = []
        
        # Pattern to match articles
        article_pattern = r'Article (\d+)\s+([^\n]+)\n(.*?)(?=Article \d+|Appendix|$)'
        matches = re.finditer(article_pattern, full_text, re.DOTALL)
        
        for match in matches:
            article_num = int(match.group(1))
            title = match.group(2).strip()
            content = match.group(3).strip()
            
            articles.append({
                "article_number": article_num,
                "title": title,
                "content": content,
                "full_text": f"Article {article_num} {title}\n\n{content}"
            })
        
        return articles
    
    def process_pdf(self) -> Dict:
        """Process PDF and create vector database"""
        articles = self.extract_articles_from_pdf()
        
        print(f"Extracted {len(articles)} articles")
        
        articles_db = {
            "articles": [],
            "embeddings": []
        }
        
        for article in articles:
            # Determine category
            categories = [cat for cat, nums in self.categories.items() 
                         if article['article_number'] in nums]
            
            # Create embedding
            embedding = self.embedding_model.encode(article['full_text'])
            
            articles_db["articles"].append({
                "article_number": article['article_number'],
                "title": article['title'],
                "content": article['content'],
                "full_text": article['full_text'],
                "categories": categories if categories else ["general"]
            })
            
            articles_db["embeddings"].append(embedding)
        
        # Convert embeddings to numpy array
        articles_db["embeddings"] = np.array(articles_db["embeddings"])
        
        print(f"✅ SCC Rules processed and stored ({len(articles)} articles)")
        return articles_db
    
    def query_vertex(self, prompt: str) -> str:
        """Use Vertex AI Gemini for queries"""
        try:
            response = self.flash_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Vertex AI error: {e}")
            return ""
    
    def classify_query(self, query: str) -> Dict:
        """Use Vertex AI to classify the user's query"""
        prompt = f"""Analyze this arbitration question and extract:
1. Main topic (deadline, cost, tribunal, procedure, award, general)
2. Keywords
3. Complexity (simple/medium/complex)

Question: {query}

Respond ONLY with valid JSON in this exact format:
{{"topic": "deadline", "keywords": ["challenge", "arbitrator"], "complexity": "simple"}}"""
        
        response = self.query_vertex(prompt)
        
        try:
            # Clean response
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"Parse error: {e}")
            pass
        
        return {
            "topic": "general",
            "keywords": query.split(),
            "complexity": "medium"
        }
    
    def cosine_similarity(self, a, b):
        """Calculate cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def retrieve_relevant_articles(self, query: str, n_results: int = 5) -> List[Dict]:
        """Retrieve relevant articles using semantic search"""
        # Create query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Calculate similarities
        similarities = []
        for i, embedding in enumerate(self.articles_db["embeddings"]):
            sim = self.cosine_similarity(query_embedding, embedding)
            similarities.append((i, sim))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top N articles
        top_articles = []
        for i, sim in similarities[:n_results]:
            article = self.articles_db["articles"][i].copy()
            article["similarity"] = float(sim)
            top_articles.append(article)
        
        return top_articles
    
    def answer_simple_query(self, query: str, articles: List[Dict]) -> str:
        """Use Vertex AI for simple queries"""
        articles_text = "\n\n".join([
            f"Article {a['article_number']}: {a['title']}\n{a['content'][:500]}..."
            for a in articles[:3]
        ])
        
        prompt = f"""Based on these SCC Arbitration Rules, answer briefly:

{articles_text}

Question: {query}

Answer concisely:"""
        
        return self.query_vertex(prompt)
    
    def answer_complex_query(self, query: str, articles: List[Dict], claude_client) -> str:
        """Use Claude API for complex queries"""
        articles_text = "\n\n".join([
            f"Article {a['article_number']}: {a['title']}\n{a['content']}"
            for a in articles
        ])
        
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""You are an expert in SCC Arbitration Rules. Answer this question using the provided articles:

Relevant SCC Articles:
{articles_text}

Question: {query}

Provide a detailed, accurate answer based on the rules:"""
            }]
        )
        
        return response.content[0].text
    
    def smart_query(self, query: str, claude_client, force_claude: bool = False) -> Dict:
        """Main query function with hybrid approach"""
        # Step 1: Classify query with Vertex AI
        classification = self.classify_query(query)
        
        print(f"Query classified as: {classification}")
        
        # Step 2: Retrieve relevant articles
        articles = self.retrieve_relevant_articles(query, n_results=5)
        
        # Step 3: Decide which model to use
        complexity = classification.get('complexity', 'medium')
        
        if force_claude or complexity == 'complex':
            print("Using Claude API for complex query...")
            answer = self.answer_complex_query(query, articles, claude_client)
            model_used = "Claude API"
        else:
            print("Using Vertex AI Gemini Flash for simple query...")
            answer = self.answer_simple_query(query, articles)
            model_used = "Vertex AI Gemini"
        
        return {
            "answer": answer,
            "articles_used": [
                {"number": a['article_number'], "title": a['title'], "similarity": a['similarity']}
                for a in articles
            ],
            "model_used": model_used,
            "classification": classification
        }