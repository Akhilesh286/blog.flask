# blog.flask — Features & Summary

## Summary

**blog.flask** is a full-featured blog platform built with Flask, SQLAlchemy, PostgreSQL, and HTMX. It's a server-rendered web app that uses **HTMX** for dynamic interactions (likes, bookmarks, comments, infinite scroll) without writing a single line of JavaScript — no SPA framework, no REST API for the client.

## Features

- **User auth** — sign-up, sign-in, logout (bcrypt hashing, Flask-Login sessions)
- **Blog posts** — create, update, archive, delete with draft/published/archived statuses
- **Markdown rendering** — post content rendered via `python-markdown` with fenced code blocks, tables, TOC
- **Likes & bookmarks** — toggle-based, rendered as HTMX partials
- **Comments with nested replies** — threaded discussions with lazy-loaded replies via HTMX
- **Follow system** — follow/unfollow other users
- **Profile management** — profile picture upload, bio, website, name
- **Search** — search posts by title and users by username
- **Dashboard** — manage drafts, archived posts, likes, bookmarks, followers/following, comments, security, email/phone verification pages
- **Post status management** — publish, archive, and delete posts from anywhere
- **Slug generation** — auto-generated unique URL slugs
- **Seed data** — `seed.py` populates the DB with demo users, posts, likes, comments, bookmarks, follows

## Technology Stack

| Layer | Technology |
|---|---|
| Framework | Flask 3.x |
| ORM | SQLAlchemy (with Flask-SQLAlchemy) |
| DB | PostgreSQL (via psycopg2-binary) |
| Migrations | Alembic (Flask-Migrate) |
| Auth | Flask-Login + Flask-Bcrypt |
| Templating | Jinja2 |
| Dynamic UI | **HTMX** (no JS frameworks) |
| Markdown | python-markdown |
| Human dates | humanize |
| Python | 3.12+ |

## Why It's Important

1. **HTMX-first architecture** — The entire interactive UI (likes, bookmarks, comments, follows, search, pagination) works via HTMX attributes in HTML. There's zero custom JavaScript. This demonstrates the "hypermedia-driven" pattern for building modern UIs without a JS framework.

2. **Server-rendered reactivity** — Every interaction returns HTML fragments, not JSON. The server is the single source of truth for UI state, which simplifies the mental model and eliminates client-server state sync bugs.

3. **Educational value** — It's a clean, modern Flask codebase that showcases best practices: blueprints, mixins (timestamp, soft-delete), enum-based statuses, pagination, file uploads, decorators for auth, and SQLAlchemy relationships with proper cascade deletes.

4. **Production-ready patterns** — Environment-based config, dedicated seed script, Alembic migrations, and a well-organized route/template structure make this a good reference architecture for a Flask + HTMX project.
