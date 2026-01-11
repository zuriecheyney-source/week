"""
Web Search Tool - External web search capabilities
"""
import sys
from pathlib import Path
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
import os

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class WebSearchTool:
    """Web search tool for external information retrieval"""
    
    def __init__(self):
        self.session = None
        self.search_provider = os.getenv("SEARCH_PROVIDER", "mock")  # mock, duckduckgo, serpapi
        self.api_key = os.getenv("SERPAPI_KEY")
    
    async def _get_session(self):
        """Get HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web for information"""
        if self.search_provider == "mock":
            return await self._mock_search(query, num_results)
        elif self.search_provider == "duckduckgo":
            return await self._duckduckgo_search(query, num_results)
        elif self.search_provider == "serpapi" and self.api_key:
            return await self._serpapi_search(query, num_results)
        else:
            return await self._mock_search(query, num_results)
    
    async def _mock_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Mock search for testing purposes"""
        await asyncio.sleep(0.5)  # Simulate network delay
        
        mock_results = [
            {
                "title": f"Mock Result 1: {query}",
                "url": "https://example.com/result1",
                "snippet": f"This is a mock search result for the query: {query}. It contains relevant information about the topic.",
                "source": "Mock Search"
            },
            {
                "title": f"Mock Result 2: {query}",
                "url": "https://example.com/result2", 
                "snippet": f"Another mock search result that provides additional context about {query}.",
                "source": "Mock Search"
            },
            {
                "title": f"Mock Result 3: {query}",
                "url": "https://example.com/result3",
                "snippet": f"Third mock result with more information related to {query} and potential solutions.",
                "source": "Mock Search"
            }
        ]
        
        return mock_results[:num_results]
    
    async def _duckduckgo_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo"""
        try:
            session = await self._get_session()
            
            # DuckDuckGo instant answers API
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    results = []
                    
                    # Add abstract if available
                    if data.get("Abstract"):
                        results.append({
                            "title": data.get("AbstractText", "Abstract"),
                            "url": data.get("AbstractURL", ""),
                            "snippet": data.get("Abstract", ""),
                            "source": "DuckDuckGo"
                        })
                    
                    # Add related topics
                    for topic in data.get("RelatedTopics", [])[:num_results-len(results)]:
                        if topic.get("Text") and topic.get("FirstURL"):
                            results.append({
                                "title": topic.get("Text", ""),
                                "url": topic.get("FirstURL", ""),
                                "snippet": topic.get("Text", ""),
                                "source": "DuckDuckGo"
                            })
                    
                    return results[:num_results]
                else:
                    print(f"DuckDuckGo search failed: {response.status}")
                    return await self._mock_search(query, num_results)
                    
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return await self._mock_search(query, num_results)
    
    async def _serpapi_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using SerpApi"""
        try:
            session = await self._get_session()
            
            url = "https://serpapi.com/search.json"
            params = {
                "api_key": self.api_key,
                "engine": "google",
                "q": query,
                "num": num_results
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    results = []
                    
                    # Extract organic results
                    for result in data.get("organic_results", [])[:num_results]:
                        results.append({
                            "title": result.get("title", ""),
                            "url": result.get("link", ""),
                            "snippet": result.get("snippet", ""),
                            "source": "Google"
                        })
                    
                    return results
                else:
                    print(f"SerpApi search failed: {response.status}")
                    return await self._mock_search(query, num_results)
                    
        except Exception as e:
            print(f"SerpApi search error: {e}")
            return await self._mock_search(query, num_results)
    
    async def get_url_content(self, url: str) -> Optional[str]:
        """Get content from a specific URL"""
        try:
            session = await self._get_session()
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Basic text extraction (in real implementation, use proper HTML parsing)
                    if len(content) > 10000:
                        content = content[:10000] + "..."
                    
                    return content
                else:
                    print(f"Failed to fetch URL: {response.status}")
                    return None
                    
        except Exception as e:
            print(f"Error fetching URL content: {e}")
            return None
    
    async def search_and_extract(self, query: str, max_content_length: int = 2000) -> Dict[str, Any]:
        """Search and extract content from top result"""
        results = await self.search_web(query, num_results=1)
        
        if results:
            top_result = results[0]
            content = await self.get_url_content(top_result.get("url", ""))
            
            if content:
                # Limit content length
                if len(content) > max_content_length:
                    content = content[:max_content_length] + "..."
                
                return {
                    "result": top_result,
                    "content": content
                }
        
        return {
            "result": None,
            "content": None
        }
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
