"""
Knowledge Base Tool - Local knowledge base search and management
"""
import sys
from pathlib import Path
import json
import asyncio
from typing import Dict, Any, List, Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class KnowledgeBaseTool:
    """Knowledge base tool for local article search and management"""
    
    def __init__(self, kb_path: str = "data/knowledge_base.json"):
        self.kb_path = Path(kb_path)
        self.kb_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize the knowledge base with default articles"""
        if not self.kb_path.exists():
            default_articles = [
                {
                    "id": "kb_001",
                    "title": "Common Login Issues",
                    "category": "technical",
                    "content": "Common login issues include incorrect password, account lockout, browser cache problems, and network connectivity issues. Solutions include password reset, clearing cache, trying different browser, and checking network connection.",
                    "keywords": ["login", "password", "account", "authentication"],
                    "created_at": "2024-01-01T00:00:00Z"
                },
                {
                    "id": "kb_002", 
                    "title": "Billing Dispute Resolution",
                    "category": "billing",
                    "content": "Billing disputes can be resolved by reviewing transaction history, checking subscription details, contacting billing department, and providing proof of payment if needed.",
                    "keywords": ["billing", "charge", "payment", "dispute"],
                    "created_at": "2024-01-01T00:00:00Z"
                },
                {
                    "id": "kb_003",
                    "title": "API Integration Guide",
                    "category": "technical",
                    "content": "API integration requires authentication setup, endpoint understanding, request/response format knowledge, error handling, and testing in sandbox environment before production.",
                    "keywords": ["api", "integration", "development", "technical"],
                    "created_at": "2024-01-01T00:00:00Z"
                },
                {
                    "id": "kb_004",
                    "title": "Account Security Best Practices",
                    "category": "account",
                    "content": "Account security best practices include using strong passwords, enabling two-factor authentication, regularly updating security settings, and monitoring account activity.",
                    "keywords": ["security", "account", "password", "2fa"],
                    "created_at": "2024-01-01T00:00:00Z"
                }
            ]
            
            with open(self.kb_path, 'w', encoding='utf-8') as f:
                json.dump(default_articles, f, indent=2, ensure_ascii=False)
    
    async def search_knowledge_base(self, query: str, category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant articles"""
        try:
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            # Simple keyword matching search
            query_lower = query.lower()
            scored_articles = []
            
            for article in articles:
                # Category filter
                if category and article.get('category') != category:
                    continue
                
                # Calculate relevance score
                score = 0
                content_lower = article.get('content', '').lower()
                title_lower = article.get('title', '').lower()
                keywords = article.get('keywords', [])
                
                # Title matching (higher weight)
                if query_lower in title_lower:
                    score += 3
                
                # Content matching
                if query_lower in content_lower:
                    score += 2
                
                # Keyword matching
                for keyword in keywords:
                    if keyword.lower() in query_lower or query_lower in keyword.lower():
                        score += 1
                
                if score > 0:
                    scored_articles.append({
                        **article,
                        "relevance_score": score
                    })
            
            # Sort by relevance score and limit results
            scored_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
            return scored_articles[:limit]
            
        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return []
    
    async def get_article_by_id(self, article_id: str) -> Optional[Dict[str, Any]]:
        """Get specific article by ID"""
        try:
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            for article in articles:
                if article.get('id') == article_id:
                    return article
            
            return None
            
        except Exception as e:
            print(f"Error getting article: {e}")
            return None
    
    async def add_article(self, title: str, content: str, category: str, keywords: List[str]) -> str:
        """Add new article to knowledge base"""
        try:
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            # Generate new ID
            new_id = f"kb_{len(articles) + 1:03d}"
            
            new_article = {
                "id": new_id,
                "title": title,
                "category": category,
                "content": content,
                "keywords": keywords,
                "created_at": "2024-01-01T00:00:00Z"
            }
            
            articles.append(new_article)
            
            with open(self.kb_path, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            
            return new_id
            
        except Exception as e:
            print(f"Error adding article: {e}")
            return ""
    
    async def get_categories(self) -> List[str]:
        """Get all available categories"""
        try:
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            categories = set()
            for article in articles:
                if 'category' in article:
                    categories.add(article['category'])
            
            return sorted(list(categories))
            
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    async def close(self):
        """Cleanup resources"""
        # No cleanup needed for file-based knowledge base
        pass
