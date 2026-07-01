import requests
from bs4 import BeautifulSoup
import re
import sys


def decode_secret_message(doc_url: str) -> None:
    """
    Fetches a published Google Doc containing a table of (x, character, y) rows,
    builds a 2D character grid, and prints it. Characters form a secret message
    when displayed in a fixed-width font.
    """
    # Support both /pub and /edit (or other) URLs
    if "/pub" in doc_url:
        fetch_url = doc_url
    else:
        doc_id_match = re.search(r"/d/([a-zA-Z0-9_-]+)", doc_url)
        if not doc_id_match:
            raise ValueError("Could not extract document ID from URL")
        fetch_url = f"https://docs.google.com/document/d/{doc_id_match.group(1)}/pub"

    response = requests.get(fetch_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    if not table:
        raise ValueError("No table found in document")

    rows = table.find_all("tr")
    # Skip header row
    entries = []
    for row in rows[1:]:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        x_text = cells[0].get_text(strip=True)
        char = cells[1].get_text(strip=True)
        y_text = cells[2].get_text(strip=True)
        if not x_text or not y_text or not char:
            continue
        entries.append((int(x_text), char, int(y_text)))

    if not entries:
        raise ValueError("No data entries found in table")

    max_x = max(e[0] for e in entries)
    max_y = max(e[2] for e in entries)

    # grid[y][x], default space
    grid = [[" "] * (max_x + 1) for _ in range(max_y + 1)]
    for x, char, y in entries:
        grid[y][x] = char

    for row in reversed(grid):
        print("".join(row))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python decode_grid.py <google_doc_url>")
        sys.exit(1)
    decode_secret_message(sys.argv[1])
