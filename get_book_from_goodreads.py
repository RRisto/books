import httpx
from pathlib import Path
from bs4 import BeautifulSoup
import re

def create_book_from_goodreads(url):
    """Scrape Goodreads book page and create markdown file with cover"""
    
    # Fetch the page
    response = httpx.get(url, follow_redirects=True, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract book data
    title = soup.find('h1', class_='Text Text__title1').text.strip()
    author = soup.find('span', class_='ContributorLink__name').text.strip()
    
    # Get cover image
    cover_img = soup.find('img', class_='ResponsiveImage')
    cover_url = cover_img['src'] if cover_img else None
    
    # Get other metadata
    pages_elem = soup.find('p', {'data-testid': 'pagesFormat'})
    pages = 0
    if pages_elem:
        pages_match = re.search(r'(\d+)\s+pages', pages_elem.text)
        if pages_match:
            pages = int(pages_match.group(1))
    
    # Get ISBN
    isbn_elem = soup.find('div', string=re.compile('ISBN'))
    isbn = ""
    if isbn_elem:
        isbn_match = re.search(r'(\d{13})', isbn_elem.parent.text)
        if isbn_match:
            isbn = isbn_match.group(1)
    
    # Clean filename
    clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    
    # Download cover
    cover_path = ""
    if cover_url:
        cover_filename = f"{clean_title}.jpg"
        cover_filepath = Path('Books/covers') / cover_filename
        img_response = httpx.get(cover_url, follow_redirects=True, timeout=10)
        if img_response.status_code == 200:
            cover_filepath.write_bytes(img_response.content)
            cover_path = f"Books/covers/{cover_filename}"
            print(f"✓ Downloaded cover")
    
    # Create markdown
    frontmatter = f"""---
type: book
title: "{title}"
author: "{author}"

isbn13: "{isbn}"
year_published: 0

date_started: ""
date_finished: ""

year_finished: 0
month_finished: ""

rating: 0
format: ""
pages: {pages}
language: ""

tags:
  - book

cover: "{cover_path}"
---"""

    body = """
    
```dataviewjs
if (dv.current().cover) { dv.paragraph("![[" + dv.current().cover + "]]"); }
```

# `= this.title`
**Author:** `= this.author`

---

## 📝 My description
What do I want to remember about this book in a year or two?

---

## 💡 Key ideas / quotes
- 
- 

---

## 🔁 Would I reread?
- [ ] Yes
- [ ] No
- [ ] Parts only

---

## ⭐ Final verdict
One-sentence summary.
"""
    
    md_content = frontmatter + body
    
    # Save markdown
    md_filename = f"{clean_title}.md"
    md_filepath = Path('Books/Library') / md_filename
    md_filepath.write_text(md_content, encoding='utf-8')
    
    print(f"✓ Created {md_filename}")
    return md_filename

# Example usage:
# create_book_from_goodreads("https://www.goodreads.com/book/show/245986477-aju-vabadus")