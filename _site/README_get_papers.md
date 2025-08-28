# Paper Fetcher for Semantic Scholar

This script fetches papers from Semantic Scholar for a given author and formats them into the `papers.yml` format used by your Jekyll site.

## Setup

1. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script with an author's name as an argument:

```bash
python get_papers.py "Author Name"
```

### Examples

```bash
# Fetch papers for Rachel Rudinger
python get_papers.py "Rachel Rudinger"

# Fetch papers for another author
python get_papers.py "Yejin Choi"
```

## What it does

1. **Searches for the author** on Semantic Scholar
2. **Fetches all papers** associated with that author
3. **Organizes papers by year** (newest first)
4. **Formats the data** to match your `papers.yml` structure
5. **Saves the result** to `_data/papers_copy.yml`

## Output format

The script creates a file with the same structure as your existing `papers.yml`:

```yaml
- year: 2023
  papers:
    - title: "Paper Title"
      venue: "Conference/Journal Name"
      authors: "Author1, Author2, Author3"
      pdf: "https://example.com/paper.pdf"  # if available
- year: 2022
  papers:
    # ... more papers
```

## Features

- **Automatic year detection** from publication dates
- **PDF links** when available
- **Author list formatting** 
- **Venue information** extraction
- **Error handling** for API failures
- **Unicode support** for international characters

## Notes

- The script uses Semantic Scholar's free API (no authentication required)
- It fetches up to 1000 papers per author
- Papers without publication years are excluded
- The output is saved as `papers_copy.yml` to avoid overwriting your original file
- You can review and edit the generated file before replacing your original `papers.yml`

## Troubleshooting

- **Author not found**: Check the spelling and try variations of the name
- **No papers found**: The author might not have papers indexed on Semantic Scholar
- **API errors**: Check your internet connection and try again later
