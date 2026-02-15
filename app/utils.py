from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotx

plt.style.use(matplotx.styles.dufte)


def generate_book_markdown(title, author, isbn13, year_published, date_finished,
                           year_finished, month_finished, rating, format_val,
                           pages, language, cover_relative_path, description,
                           key_ideas, reread, final_verdict):
    reread_yes = "[x]" if reread == "yes" else "[ ]"
    reread_no = "[x]" if reread == "no" else "[ ]"
    reread_parts = "[x]" if reread == "parts" else "[ ]"

    frontmatter = f"""---
type: book
title: "{title}"
author: "{author}"

isbn13: "{isbn13}"
year_published: {year_published}

date_started: ""
date_finished: "{date_finished}"

year_finished: {year_finished}
month_finished: "{month_finished}"

rating: {rating}
format: "{format_val}"
pages: {pages}
language: "{language}"

tags:
  - book

cover: "{cover_relative_path}"
---
"""

    body = f"""

```dataviewjs
if (dv.current().cover) {{ dv.paragraph("![[" + dv.current().cover + "]]"); }}
```

# `= this.title`
**Author:** `= this.author`

---

## 📝 My description
{description}

---

## 💡 Key ideas / quotes
{key_ideas}

---

## 🔁 Would I reread?
- {reread_yes} Yes
- {reread_no} No
- {reread_parts} Parts only

---

## ⭐ Final verdict
{final_verdict}
"""

    return frontmatter + body


def generate_books_by_year_md():
    books_by_year = {}

    # Read all markdown files
    for md_file in Path('Library').glob('*.md'):
        content = md_file.read_text(encoding='utf-8')

        # Extract frontmatter (same as before)
        if content.startswith('---'):
            frontmatter_end = content.find('---', 3)
            frontmatter = content[3:frontmatter_end]
            body = content[frontmatter_end + 3:]

            # Parse fields (same as before)
            year_finished = year_published = None
            title = author = cover = month_finished = ""
            rating = pages = 0

            for line in frontmatter.split('\n'):
                if line.startswith('title:'):
                    title = line.split('title:')[1].strip().strip('"')
                elif line.startswith('author:'):
                    author = line.split('author:')[1].strip().strip('"')
                elif line.startswith('year_finished:'):
                    year_finished = int(line.split('year_finished:')[1].strip())
                elif line.startswith('month_finished:'):
                    month_finished = line.split('month_finished:')[1].strip().strip('"')
                elif line.startswith('year_published:'):
                    val = line.split('year_published:')[1].strip()
                    if val and val != 'nan':
                        year_published = int(float(val))
                elif line.startswith('rating:'):
                    rating = int(line.split('rating:')[1].strip())
                elif line.startswith('pages:'):
                    pages = int(float(line.split('pages:')[1].strip()))
                elif line.startswith('cover:'):
                    cover = line.split('cover:')[1].strip().strip('"')

            # Extract description
            description = ""
            if "## 📝 My description" in body:
                desc_start = body.find("## 📝 My description") + len("## 📝 My description")
                desc_end = body.find("---", desc_start)
                description = body[desc_start:desc_end].strip()

            # Group by year
            if year_finished and year_finished > 0:
                if year_finished not in books_by_year:
                    books_by_year[year_finished] = []
                books_by_year[year_finished].append({
                    'title': title,
                    'author': author,
                    'rating': rating,
                    'pages': pages,
                    'cover': cover,
                    'description': description,
                    'month_finished': month_finished,
                    'year_published': year_published
                })

    # Generate separate file for each year
    views_dir = Path('Views')
    views_dir.mkdir(exist_ok=True)

    for year in books_by_year.keys():
        books = books_by_year[year]
        books_sorted = sorted(books, key=lambda x: x['month_finished'] if x['month_finished'] else "")

        md_content = f"# Books Read in {year}\n\n"
        md_content += f"**Total: {len(books_sorted)} books**\n\n"

        for book in books_sorted:
            md_content += f"### {book['title']}\n"
            md_content += f"**Author:** {book['author']}  \n"
            if book['year_published']:
                md_content += f"**Published:** {book['year_published']}  \n"
            if book['month_finished']:
                md_content += f"**Finished:** {book['month_finished']}  \n"
            md_content += f"**Rating:** {'⭐' * book['rating']}  \n"
            md_content += f"**Pages:** {book['pages']}  \n\n"

            if book['cover'] and Path(book['cover']).exists():
                md_content += f"![[{book['cover']}|150]]  \n\n"

            if book['description']:
                md_content += f"{book['description']}\n\n"

            md_content += "---\n\n"

        # Save year file
        output_file = views_dir / f"Books_{year}.md"
        output_file.write_text(md_content, encoding='utf-8')
        print(f"✓ Created {output_file}")


def generate_statistics():
    # Collect stats
    books_per_month = defaultdict(int)
    pages_per_month = defaultdict(int)

    for md_file in Path('Library').glob('*.md'):
        content = md_file.read_text(encoding='utf-8')

        if content.startswith('---'):
            frontmatter_end = content.find('---', 3)
            frontmatter = content[3:frontmatter_end]

            month_finished = ""
            pages = 0

            for line in frontmatter.split('\n'):
                if line.startswith('month_finished:'):
                    month_finished = line.split('month_finished:')[1].strip().strip('"')
                elif line.startswith('pages:'):
                    try:
                        pages = int(float(line.split('pages:')[1].strip()))
                    except:
                        pages = 0

            if month_finished:
                books_per_month[month_finished] += 1
                pages_per_month[month_finished] += pages

    # Sort by month
    months = sorted(books_per_month.keys())
    book_counts = [books_per_month[m] for m in months]
    page_counts = [pages_per_month[m] for m in months]

    # Create Views folder
    views_dir = Path('Views')
    views_dir.mkdir(exist_ok=True)

    # Dual axis chart: Books and Pages per month
    fig, ax1 = plt.subplots(figsize=(12, 5))

    # Books on left axis
    ax1.plot(months, book_counts, marker='o', color='blue', label='Books')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Books', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    # Pages on right axis
    ax2 = ax1.twinx()
    ax2.plot(months, page_counts, marker='s', color='green', label='Pages')
    ax2.set_ylabel('Pages', color='green')
    ax2.tick_params(axis='y', labelcolor='green')

    plt.title('Books and Pages Read Per Month')
    ax1.set_xticks(range(0, len(months), 3))
    ax1.set_xticklabels([months[i] for i in range(0, len(months), 3)], rotation=90)
    plt.tight_layout()
    # Add vertical lines where year changes
    for i in range(1, len(months)):
        if months[i][:4] != months[i - 1][:4]:  # compare year part (YYYY)
            ax1.axvline(x=i, color='gray', linestyle='--', alpha=0.5)
    plt.savefig(views_dir / 'books_pages_per_month.png')
    plt.close()



    # Create statistics.md
    md_content = """# Reading Statistics

## Books and Pages Per Month
![[Views/books_pages_per_month.png]]

"""

    (views_dir / 'statistics.md').write_text(md_content, encoding='utf-8')
    print("✓ Statistics updated!")