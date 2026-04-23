Built with jekyll minima.
Info here: https://github.com/jekyll/minima

You can start the website locally with `scripts/start.sh`

To automatically update papers:
- `python get_papers_merge.py`: merges new papers into the current `_data/papers.yml`
- `python get_papers.py`: refreshes all papers

The data gets saved as `_data/papers_copy.yaml` so you can review the changes