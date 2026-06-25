# Flask Blog

A feature-rich blogging platform built with Flask, SQLAlchemy, PostgreSQL, and HTMX.

## Features

### User System
- **Sign up / Sign in** — Email + password authentication with bcrypt hashing
- **Profile management** — Edit name, bio, website, gender, upload profile picture
- **Soft delete** — Users can be deactivated without losing data

### Posts
- **Full CRUD** — Create, read, update, delete posts
- **Markdown editor** — CodeMirror-based editor with live preview
- **Status workflow** — Draft → Published → Archived
- **Slug generation** — Auto-generated unique URL slugs per post title
- **Pagination** — 10 posts per page with infinite scroll via HTMX

### Social Interactions
- **Likes** — Toggle like/unlike with HTMX partial refresh
- **Bookmarks** — Save posts to read later
- **Follows** — Follow/unfollow other users; self-follow prevented at DB level
- **Comments** — Nested replies loaded lazily via HTMX
- **Search** — Real-time search for posts (by title) and people (by username)

### Dashboard
- Drafts, published posts, archived posts
- Liked posts, bookmarks
- Followers / following lists
- Comment history
- Security, email, phone, and 2FA pages (UI stubs)

## Architecture

### Tech Stack

| Layer | Technology |
|---|---|
| Framework | Flask 3.x |
| ORM | Flask-SQLAlchemy (SQLAlchemy 2.x) |
| Database | PostgreSQL via psycopg2-binary |
| Auth | Flask-Login + Flask-Bcrypt |
| Frontend | Bootstrap 5 + Bootstrap Icons |
| Dynamic UI | HTMX 2.x |
| Markdown | CodeMirror 5 (editor) + python-markdown (renderer) |
| Migrations | Flask-Migrate (Alembic) |
| Time formatting | humanize |

### Project Layout

```
blog.flask/
├── app.py                 # Application factory, routes, helpers
├── models.py              # SQLAlchemy models & enums
├── routes/
│   └── comments.py        # Comments blueprint (nested replies)
├── templates/             # Jinja2 templates
│   ├── base.html          # Base layout (Bootstrap + HTMX)
│   ├── home.html          # Main feed
│   ├── editor.html        # Post editor (CodeMirror)
│   ├── dashboard/         # Dashboard sub-pages
│   ├── comments/          # Comment/reply partials
│   ├── components/        # Reusable components (sidebar, profile pic)
│   ├── modals/            # HTMX modals (delete confirmation)
│   ├── action-buttons/    # Per-post action button partials
│   └── macro/             # Jinja2 macros (follow button)
├── static/
│   ├── css/               # Per-component stylesheets
│   └── js/                # Per-page JavaScript
├── media/uploads/         # User-uploaded profile pictures
├── migrations/            # Alembic migration scripts
├── action/                # Prototype/scratch apps (not part of main app)
└── docs/                  # Documentation
```

### Database Models

```
User (id, username, email, password_hash, phone, is_active, is_verified, is_deleted)
  ├── Profile (first_name, last_name, gender, bio, pic, website)
  ├── Post (title, slug, description, content, status, published_at)
  │   ├── PostLike (user_id, post_id)
  │   ├── Comment (content, parent_id for replies)
  │   └── Bookmark (user_id, post_id)
  └── Follow (follower_id, following_id)
```

- `PostStatus` enum: `draft`, `published`, `archived`
- All tables use `TimestampMixin` (`created_at`, `updated_at`)
- Unique constraints prevent duplicate likes, bookmarks, and follows
- Check constraint prevents self-follows

### Request Flow

1. User visits a page → Flask route handler queries DB
2. Route returns rendered Jinja2 template (or HTMX partial)
3. HTMX handles dynamic interactions (like, bookmark, follow, comment, search) without full page reload
4. HTMX partials return HTML snippets swapped into the DOM

### Key Patterns

- **HTMX partials** — `like-section.html`, `bookmark-section.html`, `follow-section.html` are re-rendered and swapped in place on toggle actions
- **Lazy-loaded comments** — Top-level comments load on page visit; replies load on click via `load_replies`
- **Search** — `/search-posts` and `/search-people` return partial HTML for HTMX-driven search
- **Authentication guard** — `@login_required` on most routes; `@unauthenticated_only` on sign-in/sign-up
- **Soft delete** — `User.is_deleted` flag; deleted users cannot sign in

## Installation

### Prerequisites

- Python 3.12+
- PostgreSQL
- `uv` package manager (recommended) or `pip`

### Setup

1. **Clone the repository**

   ```bash
   git clone <repo-url> blog.flask
   cd blog.flask
   ```

2. **Create and activate a virtual environment**

   ```bash
   uv venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   uv sync
   ```

   Or with pip:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database**

   Update the `SQLALCHEMY_DATABASE_URI` in `app.py:43`:

   ```python
   "postgresql+psycopg2://username:password@localhost:5432/blogdb"
   ```

   Create the database:

   ```bash
   createdb blogdb
   ```

5. **Run migrations**

   ```bash
   flask db upgrade
   ```

6. **(Optional) Seed demo data**

   ```bash
   python seed.py
   ```

   This creates 5 users (password: `password`), 10 posts, plus likes, comments, bookmarks, and follows.

7. **Start the development server**

   ```bash
   python app.py
   ```

   The app will be available at `http://127.0.0.1:5000`.

## Development

### Adding a migration

```bash
flask db migrate -m "description of change"
flask db upgrade
```

### Code style

- Flask routes use explicit HTTP method decorators (`@app.get`, `@app.post`) where possible
- HTMX endpoints return rendered partial templates, not JSON
- Templates extend `base.html` and override `{% block head %}`, `{% block body %}`, `{% block scripts %}`
