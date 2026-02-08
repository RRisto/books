import os
from pathlib import Path
from datetime import datetime
from starlette.staticfiles import StaticFiles
from fasthtml.common import *
from utils import generate_books_by_year_md

COVERS_FOLDER = 'covers'
LIBRARY_FOLDER = 'Library'

app, rt = fast_app()

app.mount("/covers", StaticFiles(directory="covers"), name="covers")


@rt("/")
def get():
    return Titled("Book Manager",
                  Div(
                      H2("What would you like to do?"),
                      A("Add New Book", href="/add"),
                      Br(),
                      A("View/Edit Books", href="/books")
                  )
                  )


@rt("/add")
def get():
    form = Form(
        Div(
            Label("Title:"),
            Input(name="title", placeholder="Title")
        ),
        Div(Label("Author:"), Input(name="author", placeholder="Author")),
        Div(Label("ISBN13:"), Input(name="isbn13", placeholder="ISBN13")),
        Div(Label("Year Published:"), Input(name="year_published", type="number", placeholder="Year Published")),
        Div(Label("Date Finished:"), Input(name="date_finished", type="date", placeholder="Date Finished")),
        Div(Label("Rating (0-5):"), Input(name="rating", type="number", min="0", max="5", placeholder="Rating")),
        Div(Label("Pages:"), Input(name="pages", type="number", placeholder="Pages")),
        Div(Label("Cover Image:"), Input(type="file", name="cover", accept="image/*")),
        Div(Label("Format:"), Select(
            Option("", selected=True),
            Option("paperback"),
            Option("hardcover"),
            Option("ebook"),
            Option("audio"),
            name="format"
        )),
        Div(Label("Language:"), Input(name="language", placeholder="Language (e.g. en, et)")),
        Div(Label("Description:"),
            Textarea(name="description", placeholder="What do I want to remember about this book?", rows="3")),
        Div(Label("Key ideas/quotes:"), Textarea(name="key_ideas", placeholder="Key ideas or quotes", rows="3")),
        Div(Label("Final verdict:"), Textarea(name="final_verdict", placeholder="One-sentence summary", rows="2")),
        Div(Label("Would I reread?"),
            Div(
                Input(type="radio", name="reread", value="yes", id="reread_yes"),
                Label("Yes", for_="reread_yes"),
                Input(type="radio", name="reread", value="no", id="reread_no"),
                Label("No", for_="reread_no"),
                Input(type="radio", name="reread", value="parts", id="reread_parts"),
                Label("Parts only", for_="reread_parts")
            )
            ),
        Button("Save Book"),
        method="post",
        enctype="multipart/form-data"
    )

    return Titled("Add Book",
                  Style("""
        form div { 
            display: flex; 
            margin-bottom: 10px; 
        }
        form label { 
            width: 150px; 
            text-align: right; 
            margin-right: 10px; 
        }
    """),
                  form)


@rt("/")
def post(title: str, author: str, isbn13: str, year_published: int,
         date_finished: str, rating: int, pages: int, cover: UploadFile,
         format: str, language: str, description: str, key_ideas: str,
         final_verdict: str, reread: str):
    # Parse the date
    dt = datetime.strptime(date_finished, '%Y-%m-%d')
    year_finished = dt.year
    month_finished = dt.strftime('%Y-%m')

    # Create clean filename
    clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    file_ext = os.path.splitext(cover.filename)[1]
    cover_filename = f"{clean_title}{file_ext}"
    cover_path = Path(COVERS_FOLDER) / cover_filename

    # Check if files already exist
    md_path = Path(LIBRARY_FOLDER) / f"{clean_title}.md"
    if cover_path.exists() or md_path.exists():
        return Titled("Error",
                      P("A book with this title already exists! Please change the title or delete the existing book."),
                      Button("Go Back", onclick="history.back()"))

    # Save cover image
    cover_path.parent.mkdir(parents=True, exist_ok=True)
    cover_path.write_bytes(cover.file.read())

    # Format the reread checkboxes based on selection
    reread_yes = "[x]" if reread == "yes" else "[ ]"
    reread_no = "[x]" if reread == "no" else "[ ]"
    reread_parts = "[x]" if reread == "parts" else "[ ]"

    # Generate frontmatter
    cover_relative_path = f"{COVERS_FOLDER}/{cover_filename}"

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
format: "{format}"
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

    md_content = frontmatter + body

    md_path = Path(LIBRARY_FOLDER) / f"{clean_title}.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md_content, encoding='utf-8')
    # update stats
    generate_books_by_year_md()

    return f"Book '{title}' saved! Stats updated!"


@rt("/books")
def get(page: int = 1, search: str = "", sort: str = "title", order: str = "asc"):
    # Read all books from Library
    books = []
    for md_file in Path(LIBRARY_FOLDER).glob('*.md'):
        content = md_file.read_text(encoding='utf-8')

        # Extract title and author from frontmatter
        if content.startswith('---'):
            frontmatter_end = content.find('---', 3)
            frontmatter = content[3:frontmatter_end]

            title = author = month_finished = cover = ""
            year_published = 0
            for line in frontmatter.split('\n'):
                if line.startswith('title:'):
                    title = line.split('title:')[1].strip().strip('"')
                elif line.startswith('author:'):
                    author = line.split('author:')[1].strip().strip('"')
                elif line.startswith('month_finished:'):
                    month_finished = line.split('month_finished:')[1].strip().strip('"')
                elif line.startswith('year_published:'):
                    val = line.split('year_published:')[1].strip()
                    if val and val != 'nan':
                        year_published = int(float(val))
                elif line.startswith('cover:'):
                    cover = line.split('cover:')[1].strip().strip('"').replace("Books/covers/", "covers/")

            # Filter by search term
            if search == "" or search.lower() in title.lower() or search.lower() in author.lower():
                books.append({
                    'title': title,
                    'author': author,
                    'filename': md_file.stem,
                    'month_finished': month_finished,
                    'year_published': year_published,
                    'cover': cover
                })

    # Determine reverse flag
    reverse = (order == "desc")

    # Sort based on selection
    if sort == "month_finished":
        books.sort(key=lambda x: x['month_finished'], reverse=reverse)
    elif sort == "year_published":
        books.sort(key=lambda x: x['year_published'], reverse=reverse)
    elif sort == "author":
        books.sort(key=lambda x: x['author'], reverse=reverse)
    else:  # title
        books.sort(key=lambda x: x['title'], reverse=reverse)

    # Pagination
    per_page = 50
    total_pages = (len(books) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    books_page = books[start:end]

    # Update the book_list to show thumbnails:
    book_list = Ul(*[
        Li(
            Div(
                Img(src=f"/{b['cover']}", style="width:50px;height:75px;margin-right:10px;float:left;") if b.get(
                    'cover') and Path(b['cover']).exists() else "",
                A(f"{b['title']} by {b['author']}", href=f"/edit/{b['filename']}"),
                Br(),
                Small(f"Published: {b['year_published']}" if b['year_published'] else ""),
                Br(),
                Small(f"Finished: {b['month_finished']}" if b['month_finished'] else ""),
                style="overflow:auto;margin-bottom:15px;"
            )
        ) for b in books_page
    ])

    # Pagination controls
    prev_link = A("← Previous",
                  href=f"/books?page={page - 1}&search={search}&sort={sort}&order={order}") if page > 1 else ""
    next_link = A("Next →",
                  href=f"/books?page={page + 1}&search={search}&sort={sort}&order={order}") if page < total_pages else ""

    # Search and sort form
    search_form = Form(
        Input(name="search", placeholder="Search by title or author", value=search),
        Select(
            Option("Title", value="title", selected=(sort == "title")),
            Option("Author", value="author", selected=(sort == "author")),
            Option("Month Finished", value="month_finished", selected=(sort == "month_finished")),
            Option("Year Published", value="year_published", selected=(sort == "year_published")),
            name="sort"
        ),
        Div(
            Input(type="radio", name="order", value="asc", id="order_asc", checked=(order == "asc")),
            Label("Ascending", for_="order_asc"),
            Input(type="radio", name="order", value="desc", id="order_desc", checked=(order == "desc")),
            Label("Descending", for_="order_desc")
        ),
        Button("Apply"),
        method="get"
    )

    return Titled("All Books",
                  A("← Back to Home", href="/"),
                  search_form,
                  H2(f"Showing {len(books_page)} of {len(books)} books (Page {page} of {total_pages})"),
                  book_list,
                  Div(prev_link, " ", next_link))


@rt("/edit/{filename}")
def get(filename: str):
    # Load the markdown file
    md_path = Path(LIBRARY_FOLDER) / f"{filename}.md"

    if not md_path.exists():
        return Titled("Error", P("Book not found!"), A("← Back", href="/books"))

    content = md_path.read_text(encoding='utf-8')

    # Parse frontmatter
    frontmatter_end = content.find('---', 3)
    frontmatter = content[3:frontmatter_end]
    body = content[frontmatter_end + 3:]

    # Initialize all fields
    title = author = isbn13 = date_finished = month_finished = cover = format_val = language = ""
    year_published = rating = pages = 0

    # Extract frontmatter fields
    for line in frontmatter.split('\n'):
        if line.startswith('title:'):
            title = line.split('title:')[1].strip().strip('"')
        elif line.startswith('author:'):
            author = line.split('author:')[1].strip().strip('"')
        elif line.startswith('isbn13:'):
            isbn13 = line.split('isbn13:')[1].strip().strip('"')
        elif line.startswith('year_published:'):
            val = line.split('year_published:')[1].strip()
            if val and val != 'nan':
                year_published = int(float(val))
        elif line.startswith('date_finished:'):
            date_finished = line.split('date_finished:')[1].strip().strip('"')
            date_finished = date_finished.replace('/', '-') if date_finished else ""
        elif line.startswith('month_finished:'):
            month_finished = line.split('month_finished:')[1].strip().strip('"')
        elif line.startswith('rating:'):
            rating = int(line.split('rating:')[1].strip())
        elif line.startswith('pages:'):
            pages = int(float(line.split('pages:')[1].strip()))
        elif line.startswith('format:'):
            format_val = line.split('format:')[1].strip().strip('"')
        elif line.startswith('language:'):
            language = line.split('language:')[1].strip().strip('"')
        elif line.startswith('cover:'):
            cover = line.split('cover:')[1].strip().strip('"').replace("Books/covers/", "covers/")

    # Extract body fields
    description = key_ideas = final_verdict = reread = ""

    if "## 📝 My description" in body:
        start = body.find("## 📝 My description") + len("## 📝 My description")
        end = body.find("---", start)
        description = body[start:end].strip()

    if "## 💡 Key ideas / quotes" in body:
        start = body.find("## 💡 Key ideas / quotes") + len("## 💡 Key ideas / quotes")
        end = body.find("---", start)
        key_ideas = body[start:end].strip()

    if "## ⭐ Final verdict" in body:
        start = body.find("## ⭐ Final verdict") + len("## ⭐ Final verdict")
        final_verdict = body[start:].strip()

    if "## 🔁 Would I reread?" in body:
        section = body[body.find("## 🔁 Would I reread?"):body.find("## ⭐ Final verdict")]
        if "[x] Yes" in section:
            reread = "yes"
        elif "[x] No" in section:
            reread = "no"
        elif "[x] Parts only" in section:
            reread = "parts"

    form = Form(
        Div(Label("Title:"), Input(name="title", value=title)),
        Div(Label("Author:"), Input(name="author", value=author)),
        Div(Label("ISBN13:"), Input(name="isbn13", value=isbn13)),
        Div(Label("Year Published:"), Input(name="year_published", type="number", value=year_published)),
        Div(Label("Date Finished:"), Input(name="date_finished", type="date", value=date_finished)),
        Div(Label("Rating (0-5):"), Input(name="rating", type="number", min="0", max="5", value=rating)),
        Div(Label("Pages:"), Input(name="pages", type="number", value=pages)),
        # Cover upload - show current cover
        Div(Label("Current Cover:"), Img(src=f"/{cover}", style="width:100px;") if cover else "No cover"),
        Div(Label("New Cover (optional):"), Input(type="file", name="cover", accept="image/*")),
        Div(Label("Format:"), Select(
            Option("", selected=(format_val == "")),
            Option("paperback", selected=(format_val == "paperback")),
            Option("hardcover", selected=(format_val == "hardcover")),
            Option("ebook", selected=(format_val == "ebook")),
            Option("audio", selected=(format_val == "audio")),
            name="format"
        )),
        Div(Label("Language:"), Input(name="language", value=language)),
        Div(Label("Description:"), Textarea(name="description", rows="3", value=description)),
        Div(Label("Key ideas/quotes:"), Textarea(name="key_ideas", rows="3", value=key_ideas)),
        Div(Label("Final verdict:"), Textarea(name="final_verdict", rows="2", value=final_verdict)),
        Div(Label("Would I reread?"), Div(
            Input(type="radio", name="reread", value="yes", id="reread_yes", checked=(reread == "yes")),
            Label("Yes", for_="reread_yes"),
            Input(type="radio", name="reread", value="no", id="reread_no", checked=(reread == "no")),
            Label("No", for_="reread_no"),
            Input(type="radio", name="reread", value="parts", id="reread_parts", checked=(reread == "parts")),
            Label("Parts only", for_="reread_parts")
        )),
        Button("Update Book"),
        method="post",
        action=f"/edit/{filename}",
        enctype="multipart/form-data"
    )

    return Titled("Edit Book",
                  Style("""
        form div { display: flex; margin-bottom: 10px; }
        form label { width: 150px; text-align: right; margin-right: 10px; }
    """),
                  form)


serve()
