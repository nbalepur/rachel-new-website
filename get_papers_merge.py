#!/usr/bin/env python3
"""
Script to fetch new papers from Semantic Scholar and merge them with existing papers
without updating or modifying existing entries. Only adds truly new papers.

Usage examples:
  # Normal merge operation
  python get_papers_merge.py
  
  # Hide a specific paper (mark as show: false)
  python get_papers_merge.py --hide-paper "Paper Title Here"
  
  # Hide a paper with author specification for better identification
  python get_papers_merge.py --hide-paper "Paper Title Here" --author "Author Name"
  
  # Use custom output file
  python get_papers_merge.py --output "_data/my_papers.yml"

The script now supports a "show" flag for each paper:
- show: true (or omitted) = paper will be displayed on the website
- show: false = paper will be hidden from the website but preserved in the data
- Papers marked as show: false will NOT be re-added when running the merge script
"""

import requests
import yaml
import sys
import re
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set

def get_author_ids() -> List[str]:
    """Return the fixed author IDs for Rachel Rudinger."""
    return ["2034613", "2302559920"]

def load_venue_mapping() -> Dict[str, str]:
    """Load venue mapping from venue_mapping.yml file."""
    try:
        with open("_data/venue_mapping.yml", 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("Warning: venue_mapping.yml not found, using original venue names")
        return {}
    except Exception as e:
        print(f"Warning: Error loading venue mapping: {e}")
        return {}

def load_author_name_mapping() -> Dict[str, str]:
    """Load author name mapping from author_name_mapping.yml file."""
    try:
        with open("_data/author_name_mapping.yml", 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("Warning: author_name_mapping.yml not found, using original author names")
        return {}
    except Exception as e:
        print(f"Warning: Error loading author name mapping: {e}")
        return {}

def load_existing_papers(filename: str = "_data/papers_copy.yml") -> List[Dict]:
    """Load existing papers from the YAML file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data if data else []
    except FileNotFoundError:
        print(f"Warning: {filename} not found, starting with empty paper list")
        return []
    except Exception as e:
        print(f"Warning: Error loading existing papers: {e}")
        return []

def normalize_title(title: str) -> str:
    """Normalize title by removing common prefixes and suffixes."""
    if ":" in title:
        parts = title.split(":")
        if len(parts) >= 2:
            return parts[0].strip()
    return title.strip()

def get_first_author(authors) -> str:
    """Extract the first author from the authors (can be string or list)."""
    if not authors:
        return ""
    
    if isinstance(authors, list):
        if authors and len(authors) > 0:
            return authors[0].get("name", "") if isinstance(authors[0], dict) else str(authors[0])
        return ""
    elif isinstance(authors, str):
        return authors.split(",")[0].strip()
    
    return ""

def create_paper_signature(paper: Dict) -> str:
    """Create a unique signature for a paper based on title and first author."""
    title = normalize_title(paper.get("title", ""))
    first_author = get_first_author(paper.get("authors", ""))
    return f"{title.lower()}_{first_author.lower()}"

def get_existing_paper_signatures(existing_papers: List[Dict]) -> Set[str]:
    """Get set of signatures for all existing papers."""
    signatures = set()
    for year_data in existing_papers:
        for paper in year_data.get("papers", []):
            signature = create_paper_signature(paper)
            if signature:
                signatures.add(signature)
    return signatures

def get_author_papers(author_id: str) -> List[Dict]:
    """Fetch all papers for a given author ID using pagination."""
    base_url = "https://api.semanticscholar.org/graph/v1"
    papers_url = f"{base_url}/author/{author_id}/papers"
    
    all_papers = []
    offset = 0
    limit = 100  # API limit per request
    
    while True:
        params = {
            "fields": "title,year,venue,publicationVenue,publicationDate,authors,url,openAccessPdf,publicationTypes",
            "limit": limit,
            "offset": offset
        }
        
        try:
            response = requests.get(papers_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            papers = data.get("data", [])
            if not papers:
                break
                
            # Filter out papers with 50+ authors
            filtered_papers = []
            for paper in papers:
                author_count = len(paper.get("authors", []))
                if author_count < 50:
                    filtered_papers.append(paper)
                else:
                    print(f"Filtered out paper with {author_count} authors: '{paper.get('title', 'Unknown')[:50]}...'")
                
            all_papers.extend(filtered_papers)
            print(f"Fetched {len(papers)} papers, kept {len(filtered_papers)} after filtering (offset: {offset})")
            
            if len(papers) < limit:
                break
                
            offset += limit
            
        except requests.RequestException as e:
            print(f"Error fetching papers at offset {offset}: {e}")
            break
    
    return all_papers

def get_all_author_papers(author_ids: List[str]) -> List[Dict]:
    """Fetch papers from multiple author IDs and combine them."""
    all_papers = []
    
    for author_id in author_ids:
        print(f"\nFetching papers for author ID: {author_id}")
        papers = get_author_papers(author_id)
        all_papers.extend(papers)
        print(f"Total papers so far: {len(all_papers)}")
    
    return all_papers

def format_paper_for_yaml(paper: Dict, venue_mapping: Dict[str, str], author_name_mapping: Dict[str, str]) -> Dict:
    """Format a single paper for YAML output."""
    # Extract year from publication date or year field
    year = None
    if paper.get("publicationDate"):
        try:
            year = datetime.fromisoformat(paper["publicationDate"].replace("Z", "+00:00")).year
        except:
            pass
    
    if not year and paper.get("year"):
        year = paper["year"]
    
    if not year:
        return None
        
    # Get venue and apply mapping
    venue = paper.get("venue", "") or paper.get("publicationVenue", "")
    
    # Only include venue if we have a meaningful value
    mapped_venue = None
    if venue and venue != "null":
        mapped_venue = venue_mapping.get(venue, venue)
    
    # Format paper data - handle authors carefully to preserve special characters
    authors_list = []
    raw_authors = paper.get("authors", [])
    
    for author in raw_authors:
        if isinstance(author, dict) and "name" in author:
            author_name = author["name"]
            # Apply author name mapping if available
            if author_name in author_name_mapping:
                author_name = author_name_mapping[author_name]
            if author_name:
                authors_list.append(author_name)
        elif isinstance(author, str):
            if author in author_name_mapping:
                author = author_name_mapping[author]
            authors_list.append(author)
    
    formatted_paper = {
        "title": paper.get("title", ""),
        "authors": ", ".join(authors_list) if authors_list else "",
        "show": True  # Default to showing new papers
    }
    
    # Only add venue if we have a meaningful value
    if mapped_venue:
        formatted_paper["venue"] = mapped_venue
    
    # Add PDF if available (try multiple sources)
    pdf_url = None
    if paper.get("openAccessPdf", {}).get("url"):
        pdf_url = paper["openAccessPdf"]["url"]
    elif paper.get("url"):
        url = paper["url"]
        if url.endswith('.pdf') or 'arxiv.org/pdf' in url:
            pdf_url = url
    
    if pdf_url:
        formatted_paper["pdf"] = pdf_url
    
    return {"paper": formatted_paper, "year": year}

def merge_new_papers(existing_papers: List[Dict], new_papers: List[Dict], 
                     venue_mapping: Dict[str, str], author_name_mapping: Dict[str, str]) -> Tuple[List[Dict], int]:
    """Merge new papers with existing ones, only adding truly new papers."""
    existing_signatures = get_existing_paper_signatures(existing_papers)
    
    # Track papers that have been manually hidden/deleted
    hidden_signatures = set()
    for year_data in existing_papers:
        for paper in year_data.get("papers", []):
            # If a paper exists but has show: false, consider it "deleted" and don't re-add
            if paper.get("show") is False:
                signature = create_paper_signature(paper)
                if signature:
                    hidden_signatures.add(signature)
    
    # Convert existing papers to a more manageable format
    existing_by_year = {}
    for year_data in existing_papers:
        year = year_data["year"]
        existing_by_year[year] = year_data["papers"]
    
    new_papers_added = 0
    
    # Process each new paper
    for paper in new_papers:
        formatted_data = format_paper_for_yaml(paper, venue_mapping, author_name_mapping)
        if not formatted_data:
            continue
            
        formatted_paper = formatted_data["paper"]
        year = formatted_data["year"]
        
        # Create signature for this paper
        signature = create_paper_signature(formatted_paper)
        
        # Check if this paper already exists OR was manually hidden/deleted
        if signature in existing_signatures or signature in hidden_signatures:
            continue
        
        # This is a new paper, add it
        if year not in existing_by_year:
            existing_by_year[year] = []
        
        existing_by_year[year].append(formatted_paper)
        existing_signatures.add(signature)
        new_papers_added += 1
        
        print(f"Added new paper: {formatted_paper['title'][:50]}... ({year})")
    
    # Convert back to the expected format
    merged_papers = []
    for year in sorted(existing_by_year.keys(), reverse=True):
        merged_papers.append({
            "year": year,
            "papers": existing_by_year[year]
        })
    
    return merged_papers, new_papers_added

def mark_paper_as_hidden(papers_data: List[Dict], title: str, first_author: str = None) -> bool:
    """
    Mark a paper as hidden by setting show: false.
    
    Args:
        papers_data: The papers data structure
        title: The title of the paper to hide
        first_author: Optional first author to help identify the paper
    
    Returns:
        True if paper was found and hidden, False otherwise
    """
    target_signature = create_paper_signature({"title": title, "authors": first_author or ""})
    
    for year_data in papers_data:
        for paper in year_data.get("papers", []):
            paper_signature = create_paper_signature(paper)
            if paper_signature == target_signature:
                paper["show"] = False
                print(f"Marked paper as hidden: '{paper['title']}' ({year_data['year']})")
                return True
    
    print(f"Paper not found: '{title}'")
    return False

def save_to_yaml(data: List[Dict], filename: str):
    """Save the formatted data to a YAML file with proper encoding."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, 
                     default_style='|', width=float("inf"))
        print(f"Papers saved to {filename}")
    except Exception as e:
        print(f"Error saving to YAML: {e}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Merge new papers from Semantic Scholar with existing papers')
    parser.add_argument('--hide-paper', type=str, help='Title of paper to hide (mark as show: false)')
    parser.add_argument('--author', type=str, help='First author of paper to hide (optional, helps identify the paper)')
    parser.add_argument('--output', type=str, default='_data/papers_copy.yml', 
                       help='Output YAML file (default: _data/papers_copy.yml)')
    
    args = parser.parse_args()
    
    # Load existing papers
    print("Loading existing papers...")
    existing_papers = load_existing_papers(args.output)
    existing_count = sum(len(year_data["papers"]) for year_data in existing_papers)
    print(f"Found {existing_count} existing papers")
    
    # If hiding a paper, do that and exit
    if args.hide_paper:
        if mark_paper_as_hidden(existing_papers, args.hide_paper, args.author):
            save_to_yaml(existing_papers, args.output)
            print(f"Updated {args.output} - paper marked as hidden")
        else:
            print("No changes made")
        return
    
    # Use fixed author IDs for Rachel Rudinger
    author_ids = get_author_ids()
    print(f"Using author IDs: {', '.join(author_ids)}")
    
    # Load mappings
    print("Loading venue mapping...")
    venue_mapping = load_venue_mapping()
    
    print("Loading author name mapping...")
    author_name_mapping = load_author_name_mapping()
    
    # Fetch new papers from API
    print("Fetching papers from API...")
    api_papers = get_all_author_papers(author_ids)
    
    if not api_papers:
        print("No papers found from API.")
        sys.exit(1)
    
    print(f"Fetched {len(api_papers)} papers from API")
    
    # Merge new papers with existing ones
    print("Merging new papers...")
    merged_papers, new_count = merge_new_papers(existing_papers, api_papers, venue_mapping, author_name_mapping)
    
    if new_count == 0:
        print("No new papers found. All papers are already up to date.")
        return
    
    print(f"Added {new_count} new papers")
    
    # Save merged result
    save_to_yaml(merged_papers, args.output)
    
    # Print summary
    total_papers = sum(len(year_data["papers"]) for year_data in merged_papers)
    print(f"\nSummary:")
    print(f"Existing papers: {existing_count}")
    print(f"New papers added: {new_count}")
    print(f"Total papers: {total_papers}")
    print(f"Years covered: {len(merged_papers)}")

if __name__ == "__main__":
    main()
