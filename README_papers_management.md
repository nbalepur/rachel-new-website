# Papers Management System

This system manages academic publications with automatic merging from Semantic Scholar and manual control over which papers are displayed.

## Features

- **Automatic Updates**: Fetches new papers from Semantic Scholar API
- **Smart Merging**: Only adds truly new papers, preserves existing entries
- **Flexible Display Control**: Use `show` flag to control paper visibility
- **Command-line Interface**: Easy paper management from terminal

## Paper Display Control

Each paper entry now has a `show` flag:

```yaml
- title: "Example Paper Title"
  authors: "Author Name"
  venue: "Conference Name"
  year: 2023
  show: true  # Paper will be displayed on website
```

```yaml
- title: "Hidden Paper Title"
  authors: "Author Name"
  venue: "Conference Name"
  year: 2023
  show: false  # Paper will be hidden from website
```

## Usage

### Normal Merge Operation
```bash
python get_papers_merge.py
```
This will fetch new papers from Semantic Scholar and merge them with existing ones.

### Hide a Paper
```bash
# Hide by title only
python get_papers_merge.py --hide-paper "Paper Title Here"

# Hide by title and author (more precise)
python get_papers_merge.py --hide-paper "Paper Title Here" --author "Author Name"
```

### Custom Output File
```bash
python get_papers_merge.py --output "_data/my_papers.yml"
```

## How It Works

1. **New Papers**: Automatically get `show: true` by default
2. **Hidden Papers**: Papers with `show: false` are preserved in the data but hidden from the website
3. **Re-addition Prevention**: The merge script respects `show: false` and won't re-add hidden papers
4. **Website Display**: Only papers with `show: true` (or omitted) are displayed on the publications page

## Benefits

- **No Data Loss**: Hidden papers remain in the YAML file for reference
- **Easy Management**: Simple command-line interface for hiding papers
- **Automatic Protection**: Hidden papers won't be accidentally re-added during merges
- **Flexible Control**: Can easily toggle papers on/off by changing the `show` flag

## Example Workflow

1. Run merge script to get latest papers: `python get_papers_merge.py`
2. Review papers and hide unwanted ones: `python get_papers_merge.py --hide-paper "Unwanted Paper"`
3. Papers marked as `show: false` will stay hidden even after future merges
4. To show a hidden paper again, manually edit the YAML file and change `show: false` to `show: true`
