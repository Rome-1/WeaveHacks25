import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any
import json

def scrape_url_metadata(url: str) -> Dict[str, Any]:
    """
    Scrape metadata from a URL.
    
    Returns:
        Dict with status, url, title, metadescription, and optional error_message
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ""
        
        return {
            'status': 'success',
            'url': url,
            'title': title_text,
            'metadescription': description
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'url': url,
            'error_message': str(e)
        }
