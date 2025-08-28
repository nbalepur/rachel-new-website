#!/usr/bin/env python3
"""
Script to fetch papers from Semantic Scholar for Rachel Rudinger and format them into papers.yml format.
Usage: python get_papers.py
"""

import requests
import yaml
import sys
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

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

def normalize_title(title: str) -> str:
    """Normalize title by removing common prefixes and suffixes."""
    # Remove common prefixes like "Title: Subtitle" and keep the main title
    if ":" in title:
        parts = title.split(":")
        if len(parts) >= 2:
            # Keep the part before the first colon
            return parts[0].strip()
    return title.strip()

def get_first_author(authors) -> str:
    """Extract the first author from the authors (can be string or list)."""
    if not authors:
        return ""
    
    if isinstance(authors, list):
        # If authors is already a list, take the first one
        if authors and len(authors) > 0:
            return authors[0].get("name", "") if isinstance(authors[0], dict) else str(authors[0])
        return ""
    elif isinstance(authors, str):
        # If authors is a string, split by comma and take the first one
        return authors.split(",")[0].strip()
    
    return ""

def is_duplicate(paper1: Dict, paper2: Dict) -> bool:
    """Check if two papers are duplicates based on title and first author."""
    title1 = normalize_title(paper1.get("title", ""))
    title2 = normalize_title(paper2.get("title", ""))
    
    # Check if titles are similar (allowing for minor differences)
    if title1.lower() == title2.lower():
        return True
    
    # Check if titles are the same after removing common prefixes
    if title1 and title2:
        # Remove common prefixes like "Title: Subtitle"
        clean_title1 = re.sub(r'^[^:]+:\s*', '', title1).strip()
        clean_title2 = re.sub(r'^[^:]+:\s*', '', title2).strip()
        if clean_title1.lower() == clean_title2.lower():
            return True
    
    # Check if first authors are the same and titles are similar
    author1 = get_first_author(paper1.get("authors", ""))
    author2 = get_first_author(paper2.get("authors", ""))
    
    if author1 and author2 and author1.lower() == author2.lower():
        # Check if titles are similar (allowing for minor differences)
        if title1.lower() in title2.lower() or title2.lower() in title1.lower():
            return True
    
    return False

def select_best_paper(duplicates: List[Dict]) -> Dict:
    """Select the best paper from duplicates, preferring conference over arXiv."""
    if not duplicates:
        return {}
    
    # First, try to find papers that are not arXiv
    non_arxiv_papers = []
    for paper in duplicates:
        venue = paper.get("venue", "").lower()
        if "arxiv" not in venue and "preprint" not in venue:
            non_arxiv_papers.append(paper)
    
    # If we have non-arXiv papers, return the first one
    if non_arxiv_papers:
        return non_arxiv_papers[0]
    
    # If all are arXiv, return the first one
    return duplicates[0]

def remove_duplicates(papers: List[Dict]) -> List[Dict]:
    """Remove duplicate papers, keeping the best version of each."""
    unique_papers = []
    processed_titles = set()
    
    for paper in papers:
        normalized_title = normalize_title(paper.get("title", ""))
        first_author = get_first_author(paper.get("authors", ""))
        key = f"{normalized_title.lower()}_{first_author.lower()}"
        
        if key not in processed_titles:
            # Check if this paper has duplicates in the remaining papers
            duplicates = [paper]
            for other_paper in papers[papers.index(paper) + 1:]:
                if is_duplicate(paper, other_paper):
                    duplicates.append(other_paper)
            
            # Select the best version
            best_paper = select_best_paper(duplicates)
            unique_papers.append(best_paper)
            processed_titles.add(key)
    
    return unique_papers

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
            
            # If we got fewer papers than the limit, we've reached the end
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

def format_papers_for_yaml(papers: List[Dict], venue_mapping: Dict[str, str], author_name_mapping: Dict[str, str]) -> Dict:
    """Format papers into the papers.yml structure."""
    # Group papers by year
    papers_by_year = {}
    papers_without_year = 0
    
    for paper in papers:
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
            papers_without_year += 1
            print(f"Warning: Paper without year: '{paper.get('title', 'Unknown')[:50]}...'")
            continue
            
        if year not in papers_by_year:
            papers_by_year[year] = []
        
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
                # Ensure proper encoding and handle special characters
                if author_name:
                    authors_list.append(author_name)
            elif isinstance(author, str):
                # Apply author name mapping if available
                if author in author_name_mapping:
                    author = author_name_mapping[author]
                authors_list.append(author)
        
        formatted_paper = {
            "title": paper.get("title", ""),
            "authors": ", ".join(authors_list) if authors_list else ""
        }
        
        # Only add venue if we have a meaningful value
        if mapped_venue:
            formatted_paper["venue"] = mapped_venue
        
        # Add PDF if available (try multiple sources)
        pdf_url = None
        if paper.get("openAccessPdf", {}).get("url"):
            pdf_url = paper["openAccessPdf"]["url"]
        elif paper.get("url"):
            # Check if the URL is a PDF
            url = paper["url"]
            if url.endswith('.pdf') or 'arxiv.org/pdf' in url:
                pdf_url = url
        
        if pdf_url:
            formatted_paper["pdf"] = pdf_url
        
        papers_by_year[year].append(formatted_paper)
    
    # Convert to the expected format
    formatted_data = []
    for year in sorted(papers_by_year.keys(), reverse=True):
        formatted_data.append({
            "year": year,
            "papers": papers_by_year[year]
        })
    
    if papers_without_year > 0:
        print(f"Note: {papers_without_year} papers were omitted due to missing publication year")
    
    return formatted_data

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
    # Use fixed author IDs for Rachel Rudinger
    author_ids = get_author_ids()
    print(f"Using author IDs: {', '.join(author_ids)}")
    
    # Load venue mapping
    print("Loading venue mapping...")
    venue_mapping = load_venue_mapping()
    
    # Load author name mapping
    print("Loading author name mapping...")
    author_name_mapping = load_author_name_mapping()
    
    # Fetch papers from all author IDs
    print("Fetching papers from all author IDs...")
    papers = get_all_author_papers(author_ids)
    
    if not papers:
        print("No papers found for these authors.")
        sys.exit(1)
    
    print(f"\nFound {len(papers)} total papers")
    
    # Remove duplicates
    print("Removing duplicates...")
    unique_papers = remove_duplicates(papers)
    print(f"After removing duplicates: {len(unique_papers)} papers")
    
    # Format papers
    print("Formatting papers...")
    formatted_papers = format_papers_for_yaml(unique_papers, venue_mapping, author_name_mapping)
    
    # Save to file
    output_file = "_data/papers_copy.yml"
    save_to_yaml(formatted_papers, output_file)
    
    # Print summary
    total_papers = sum(len(year_data["papers"]) for year_data in formatted_papers)
    print(f"\nSummary:")
    print(f"Total papers: {total_papers}")
    print(f"Years covered: {len(formatted_papers)}")
    for year_data in formatted_papers:
        print(f"  {year_data['year']}: {len(year_data['papers'])} papers")

if __name__ == "__main__":
    main()
