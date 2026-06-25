# blog.flask

A feature-rich blogging platform built with **Flask**, **SQLAlchemy**, **PostgreSQL**, and **HTMX**. Dynamic interactions (likes, bookmarks, comments, search, follows) are handled entirely via HTMX — no JavaScript frameworks, no REST API required.

---

## Features

- **User authentication** — sign-up, sign-in, logout with bcrypt hashing and Flask-Login sessions
- **Blog posts** — full CRUD with draft / published / archived status workflow
- **Markdown rendering** — post content rendered with fenced code blocks, tables, and TOC
- **Social interactions** — toggle-based likes, bookmarks, follows, and threaded comments
- **Nested comments** — lazy-loaded replies via HTMX
- **Profile management** — upload profile picture, edit bio, name, website
- **Search** — search posts by title and users by username
- **Dashboard** — manage drafts, archives, likes, bookmarks, followers/following, comments, security, and account settings
- **Unique URL slugs** — auto-generated, collision-safe slugs per post title
- **Soft delete** — users can be deactivated without losing data
- **Seed data** — `seed.py` populates the database with demo users, posts, likes, comments, bookmarks, and follows

---

## System Requirements

- **Python** 3.12+
- **PostgreSQL** 14+
- **uv** (recommended) or pip

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [Flask](https://flask.palletsprojects.com/) 3.x |
| ORM | [SQLAlchemy](https://www.sqlalchemy.org/) 2.x via Flask-SQLAlchemy |
| Database | [PostgreSQL](https://www.postgresql.org/) via psycopg2-binary |
| Migrations | [Alembic](https://alembic.sqlalchemy.org/) via Flask-Migrate |
| Auth | [Flask-Login](https://flask-login.readthedocs.io/) + [Flask-Bcrypt](https://flask-bcrypt.readthedocs.io/) |
| Dynamic UI | [HTMX](https://htmx.org/) 2.x — no custom JavaScript |
| Markdown | [python-markdown](https://python-markdown.github.io/) |
| Templating | [Jinja2](https://jinja.palletsprojects.com/) |
| Icons | [Bootstrap Icons](https://icons.getbootstrap.com/) |
| Time formatting | [humanize](https://python-humanize.readthedocs.io/) |
| Package manager | [uv](https://docs.astral.sh/uv/) |

---

## Quick Start

### 1. Clone

```bash
git clone <repo-url> blog.flask
cd blog.flask
```

### 2. Create and activate a virtual environment

```bash
uv venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
uv sync
```

Or with pip:

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Copy the example env file and edit as needed:

```bash
cp .env.example .env
```

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Flask secret key for session signing | `generate a random string` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://user:pass@localhost:5432/blogdb` |

### 5. Create the database

```bash
createdb blogdb
```

### 6. Run migrations

```bash
flask db upgrade
```

### 7. (Optional) Seed demo data

```bash
python seed.py
```

Creates 5 users (password: `password`), 10 posts, plus likes, comments, bookmarks, and follows.

### 8. Run the dev server

```bash
python app.py
```

Visit **http://127.0.0.1:5000**

---

## Project Structure

```
blog.flask/
├── app.py                 # App factory, routes, helpers, decorators
├── models.py              # SQLAlchemy models & enums
├── seed.py                # Demo data seeder
├── pyproject.toml         # Project metadata & dependencies
├── .env.example           # Environment variable template
├── routes/
│   └── comments.py        # Comments blueprint (nested replies)
├── templates/             # Jinja2 templates
│   ├── base.html          # Base layout (Bootstrap + HTMX)
│   ├── home.html          # Main feed
│   ├── editor.html        # Post editor
│   ├── dashboard/         # Dashboard sub-pages
│   ├── comments/          # Comment/reply partials
│   ├── components/        # Reusable components
│   ├── modals/            # HTMX modals (delete confirmation)
│   └── macro/             # Jinja2 macros (follow button)
├── static/
│   ├── css/               # Stylesheets
│   └── js/                # Per-page JavaScript
├── media/uploads/         # User-uploaded profile pictures
├── migrations/            # Alembic migration scripts
├── action/                # Prototype/scratch apps
└── docs/                  # Documentation
```

---

## Database Models

```
User (id, username, email, password_hash, phone, is_active, is_verified, is_deleted)
  ├── Profile (first_name, last_name, gender, bio, pic, website)
  ├── Post (title, slug, description, content, status, published_at)
  │   ├── PostLike (user_id, post_id)       — unique constraint
  │   ├── Comment (content, parent_id)       — nested replies via self-referential FK
  │   └── Bookmark (user_id, post_id)        — unique constraint
  └── Follow (follower_id, following_id)     — unique constraint, no self-follow
```

- `PostStatus` enum: `draft`, `published`, `archived`
- `TimestampMixin` on all tables (`created_at`, `updated_at`)

---

## Development Workflow

### Add a migration

```bash
flask db migrate -m "description of change"
flask db upgrade
```

### Run the app

```bash
flask run
```

Or:

```bash
python app.py
```

---

## License

MIT
