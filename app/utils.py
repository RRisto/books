from pathlib import Path


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