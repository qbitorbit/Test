#!/usr/bin/env python3
"""
Confluence MCP Server - Core Confluence functions
Provides 10 essential tools for Confluence integration
"""
import requests
import json
from typing import Optional
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Global state
confluence_base_url: Optional[str] = None
confluence_api_key: Optional[str] = None


def set_confluence_credentials(base_url: str, api_key: str):
    """Set Confluence credentials"""
    global confluence_base_url, confluence_api_key
    confluence_base_url = base_url
    confluence_api_key = api_key


def _make_request(method: str, endpoint: str, params: dict = None, json_data: dict = None) -> dict:
    """Make HTTP request to Confluence API"""
    if not confluence_base_url or not confluence_api_key:
        return {"success": False, "error": "Confluence credentials not set"}
    
    url = f"{confluence_base_url}{endpoint}"
    headers = {
        "Authorization": f"Bearer {confluence_api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, verify=False, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=json_data, verify=False, timeout=30)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=json_data, verify=False, timeout=30)
        
        if response.status_code in [200, 201]:
            return {"success": True, "data": response.json()}
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def _html_to_text(html: str) -> str:
    """Convert HTML to plain text"""
    try:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n", strip=True)
    except:
        return html


# ========== Tool 1: Search Confluence ==========

def search_confluence(query: str, limit: int = 10) -> str:
    """
    Search Confluence using CQL (Confluence Query Language)
    
    Args:
        query: CQL query string (e.g., "space = DEV and label = api")
        limit: Maximum number of results (default: 10)
    
    Returns:
        JSON string with search results
    """
    params = {
        "cql": query,
        "limit": limit,
        "expand": "content.space"
    }
    
    result = _make_request("GET", "/search", params=params)
    
    if not result["success"]:
        return json.dumps(result)
    
    results = result["data"].get("results", [])
    
    pages = []
    for item in results:
        content = item.get("content", {})
        space = content.get("space", {})
        
        pages.append({
            "id": content.get("id"),
            "title": content.get("title"),
            "type": content.get("type"),
            "space_key": space.get("key"),
            "space_name": space.get("name"),
            "url": f"{confluence_base_url.replace('/rest/api/content', '')}/pages/viewpage.action?pageId={content.get('id')}"
        })
    
    return json.dumps({
        "success": True,
        "count": len(pages),
        "query": query,
        "pages": pages
    })


# ========== Tool 2: Get Page Content ==========

def get_page_content(page_id: str, format: str = "text") -> str:
    """
    Get full content of a Confluence page
    
    Args:
        page_id: Confluence page ID
        format: Return format - "text" or "html" (default: "text")
    
    Returns:
        JSON string with page content
    """
    params = {
        "expand": "body.storage,version,space,history"
    }
    
    result = _make_request("GET", f"/{page_id}", params=params)
    
    if not result["success"]:
        return json.dumps(result)
    
    page = result["data"]
    html_content = page.get("body", {}).get("storage", {}).get("value", "")
    
    content = html_content if format == "html" else _html_to_text(html_content)
    
    return json.dumps({
        "success": True,
        "page_id": page_id,
        "title": page.get("title"),
        "content": content,
        "space_key": page.get("space", {}).get("key"),
        "space_name": page.get("space", {}).get("name"),
        "version": page.get("version", {}).get("number"),
        "author": page.get("history", {}).get("lastUpdated", {}).get("by", {}).get("displayName"),
        "updated": page.get("version", {}).get("when"),
        "url": f"{confluence_base_url.replace('/rest/api/content', '')}/pages/viewpage.action?pageId={page_id}"
    })


# ========== Tool 3: List Spaces ==========

def list_spaces(limit: int = 25) -> str:
    """
    List all accessible Confluence spaces
    
    Args:
        limit: Maximum number of spaces to return (default: 25)
    
    Returns:
        JSON string with list of spaces
    """
    params = {"limit": limit}
    
    result = _make_request("GET", "/space", params=params)
    
    if not result["success"]:
        return json.dumps(result)
    
    spaces = []
    for space in result["data"].get("results", []):
        spaces.append({
            "key": space.get("key"),
            "name": space.get("name"),
            "type": space.get("type"),
            "url": f"{confluence_base_url.replace('/rest/api/content', '')}/display/{space.get('key')}"
        })
    
    return json.dumps({
        "success": True,
        "count": len(spaces),
        "spaces": spaces
    })


# ========== Tool 4: Get Space Pages ==========

def get_space_pages(space_key: str, limit: int = 50) -> str:
    """
    List all pages in a specific space
    
    Args:
        space_key: Confluence space key (e.g., "DEV", "DOCS")
        limit: Maximum number of pages (default: 50)
    
    Returns:
        JSON string with list of pages
    """
    params = {
        "spaceKey": space_key,
        "limit": limit,
        "expand": "version"
    }
    
    result = _make_request("GET", "", params=params)
    
    if not result["success"]:
        return json.dumps(result)
    
    pages = []
    for page in result["data"].get("results", []):
        pages.append({
            "id": page.get("id"),
            "title": page.get("title"),
            "type": page.get("type"),
            "version": page.get("version", {}).get("number"),
            "url": f"{confluence_base_url.replace('/rest/api/content', '')}/pages/viewpage.action?pageId={page.get('id')}"
        })
    
    return json.dumps({
        "success": True,
        "space_key": space_key,
        "count": len(pages),
        "pages": pages
    })


# ========== Tool 5: Get Page by Title ==========

def get_page_by_title(space_key: str, title: str) -> str:
    """
    Find a page by title in a specific space
    
    Args:
        space_key: Confluence space key
        title: Page title to search for
    
    Returns:
        JSON string with page details
    """
    params = {
        "spaceKey": space_key,
        "title": title,
        "expand": "body.storage,version"
    }
    
    result = _make_request("GET", "", params=params)
    
    if not result["success"]:
        return json.dumps(result)
    
    results = result["data"].get("results", [])
    
    if not results:
        return json.dumps({
            "success": False,
            "error": f"Page '{title}' not found in space '{space_key}'"
        })
    
    page = results[0]
    html_content = page.get("body", {}).get("storage", {}).get("value", "")
    
    return json.dumps({
        "success": True,
        "page_id": page.get("id"),
        "title": page.get("title"),
        "content": _html_to_text(html_content),
        "version": page.get("version", {}).get("number"),
        "url": f"{confluence_base_url.replace('/rest/api/content', '')}/pages/viewpage.action?pageId={page.get('id')}"
    })


# ========== Tool 6: Create Page ==========

def create_page(space_key: str, title: str, content: str, parent_id: Optional[str] = None) -> str:
    """
    Create a new Confluence page
    
    Args:
        space_key: Confluence space key where page will be created
        title: Page title
        content: Page content (plain text or HTML)
        parent_id: Optional parent page ID for nested pages
    
    Returns:
        JSON string with created page details
    """
    # Simple HTML wrapper for plain text
    if not content.startswith("<"):
        content = f"<p>{content}</p>"
    
    page_data = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        }
    }
    
    if parent_id:
        page_data["ancestors"] = [{"id": parent_id}]
    
    result = _make_request("POST", "", json_data=page_data)
    
    if not result["success"]:
        return json.dumps(result)
    
    page = result["data"]
    
    return json.dumps({
        "success": True,
        "page_id": page.get("id"),
        "title": page.get("title"),
        "space_key": space_key,
        "url": f"{confluence_base_url.replace('/rest/api/content', '')}/pages/viewpage.action?pageId={page.get('id')}",
        "message": f"Page '{title}' created successfully"
    })


# ========== Tool 7: Update Page ==========

def update_page(page_id: str, title: str, content: str, version: int) -> str:
    """
    Update an existing Confluence page
    
    Args:
        page_id: Page ID to update
        title: New page title
        content: New page content (plain text or HTML)
        version: Current version number (required for optimistic locking)
    
    Returns:
        JSON string with update status
    """
    # Simple HTML wrapper for plain text
    if not content.startswith("<"):
        content = f"<p>{content}</p>"
    
    page_data = {
        "version": {"number": version + 1},
        "title": title,
        "type": "page",
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        }
    }
    
    result = _make_request("PUT", f"/{page_id}", json_data=page_data)
    
    if not result["success"]:
        return json.dumps(result)
    
    page = result["data"]
    
    return json.dumps({
        "success": True,
        "page_id": page_id,
        "title": page.get("title"),
        "new_version": page.get("version", {}).get("number"),
        "url": f"{confluence_base_url.replace('/rest/api/content', '')}/pages/viewpage.action?pageId={page_id}",
        "message": f"Page updated successfully to version {page.get('version', {}).get('number')}"
    })


# ========== Tool 8: Get Page Comments ==========

def get_page_comments(page_id: str, limit: int = 25) -> str:
    """
    Get comments on a Confluence page
    
    Args:
        page_id: Page ID
        limit: Maximum number of comments (default: 25)
    
    Returns:
        JSON string with comments
    """
    params = {
        "expand": "body.view,version,history",
        "limit": limit
    }
    
    result = _make_request("GET", f"/{page_id}/child/comment", params=params)
    
    if not result["success"]:
        return json.dumps(result)
    
    comments = []
    for comment in result["data"].get("results", []):
        html_content = comment.get("body", {}).get("view", {}).get("value", "")
        
        comments.append({
            "id": comment.get("id"),
            "author": comment.get("history", {}).get("createdBy", {}).get("displayName"),
            "content": _html_to_text(html_content),
            "created": comment.get("history", {}).get("createdDate")
        })
    
    return json.dumps({
        "success": True,
        "page_id": page_id,
        "count": len(comments),
        "comments": comments
    })


# ========== Tool 9: Add Comment ==========

def add_comment(page_id: str, comment: str, parent_id: Optional[str] = None) -> str:
    """
    Add a comment to a Confluence page
    
    Args:
        page_id: Page ID to comment on
        comment: Comment text
        parent_id: Optional parent comment ID for threaded replies
    
    Returns:
        JSON string with comment creation status
    """
    # Simple HTML wrapper
    if not comment.startswith("<"):
        comment = f"<p>{comment}</p>"
    
    comment_data = {
        "type": "comment",
        "container": {"id": page_id, "type": "page"},
        "body": {
            "storage": {
                "value": comment,
                "representation": "storage"
            }
        }
    }
    
    if parent_id:
        comment_data["ancestors"] = [{"id": parent_id}]
    
    result = _make_request("POST", "", json_data=comment_data)
    
    if not result["success"]:
        return json.dumps(result)
    
    comment_obj = result["data"]
    
    return json.dumps({
        "success": True,
        "comment_id": comment_obj.get("id"),
        "page_id": page_id,
        "message": "Comment added successfully"
    })


# ========== Tool 10: Get Page Children ==========

def get_page_children(page_id: str, limit: int = 50) -> str:
    """
    Get child pages of a Confluence page
    
    Args:
        page_id: Parent page ID
        limit: Maximum number of children (default: 50)
    
    Returns:
        JSON string with child pages
    """
    params = {
        "expand": "version",
        "limit": limit
    }
    
    result = _make_request("GET", f"/{page_id}/child/page", params=params)
    
    if not result["success"]:
        return json.dumps(result)
    
    children = []
    for child in result["data"].get("results", []):
        children.append({
            "id": child.get("id"),
            "title": child.get("title"),
            "type": child.get("type"),
            "url": f"{confluence_base_url.replace('/rest/api/content', '')}/pages/viewpage.action?pageId={child.get('id')}"
        })
    
    return json.dumps({
        "success": True,
        "parent_id": page_id,
        "count": len(children),
        "children": children
    })


# ========== Helper: Get Page Version ==========

def get_page_version(page_id: str) -> str:
    """
    Get current version number of a page (helper for updates)
    
    Args:
        page_id: Page ID
    
    Returns:
        JSON string with version info
    """
    params = {"expand": "version"}
    
    result = _make_request("GET", f"/{page_id}", params=params)
    
    if not result["success"]:
        return json.dumps(result)
    
    page = result["data"]
    
    return json.dumps({
        "success": True,
        "page_id": page_id,
        "title": page.get("title"),
        "version": page.get("version", {}).get("number")
    })
