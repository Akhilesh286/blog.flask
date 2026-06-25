"""Seed the database with demo data."""
import random
from datetime import datetime, timedelta, timezone

from app import app, bcrypt
from models import db, User, Profile, Post, PostStatus, PostLike, Comment, Bookmark, Follow


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        now = datetime.now(timezone.utc)

        # ── Users ──────────────────────────────────────────────
        users_data = [
            ("alice", "alice@example.com", "password"),
            ("bob", "bob@example.com", "password"),
            ("charlie", "charlie@example.com", "password"),
            ("diana", "diana@example.com", "password"),
            ("eve", "eve@example.com", "password"),
        ]

        users = []
        for i, (uname, email, pw) in enumerate(users_data):
            user = User(
                username=uname,
                email=email,
                password_hash=bcrypt.generate_password_hash(pw).decode(),
                is_verified=True,
                is_active=True,
            )
            db.session.add(user)
            db.session.flush()
            users.append(user)

            profile = Profile(
                user_id=user.id,
                first_name=uname.capitalize(),
                last_name="Demo",
                bio=f"Hi, I'm {uname.capitalize()}. This is my demo profile.",
                website=f"https://{uname}.example.com",
            )
            db.session.add(profile)

        # ── Posts ──────────────────────────────────────────────
        posts_data = [
            ("Getting Started with Flask", "flask-intro",
             "A beginner-friendly guide to building web apps with Flask.",
             "## Why Flask?\n\nFlask is a lightweight WSGI web application framework in Python.\n\n```python\nfrom flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef hello():\n    return 'Hello, World!'\n```\n\nIt's simple, flexible, and perfect for both small and large projects."),
            ("Understanding SQLAlchemy ORM", "sqlalchemy-orm",
             "Deep dive into SQLAlchemy's ORM patterns and best practices.",
             "## SQLAlchemy ORM\n\nSQLAlchemy is the Python SQL toolkit and ORM.\n\n### Key Concepts\n\n- **Declarative Base** – Define models as classes\n- **Session** – Manages database operations\n- **Relationships** – Define foreign keys and backrefs\n\n```python\nclass User(db.Model):\n    id = db.Column(db.Integer, primary_key=True)\n    username = db.Column(db.String(50), unique=True)\n```"),
            ("HTMX: Hypermedia-Driven UIs", "htmx-intro",
             "How HTMX simplifies dynamic web interfaces without JavaScript frameworks.",
             "## HTMX\n\nHTMX allows you to access AJAX, CSS Transitions, WebSockets and Server Sent Events directly in HTML.\n\n```html\n<button hx-post=\"/like\" hx-swap=\"outerHTML\">\n  Like\n</button>\n```\n\nNo JavaScript needed for most interactions!"),
            ("Python Type Hints Guide", "python-type-hints",
             "Leverage type hints for cleaner, more maintainable Python code.",
             "## Type Hints in Python\n\nPython 3.12+ has excellent type hint support.\n\n```python\nfrom typing import Optional\n\ndef greet(name: str, age: Optional[int] = None) -> str:\n    msg = f\"Hello, {name}\"\n    if age:\n        msg += f\" (age {age})\"\n    return msg\n```"),
            ("PostgreSQL Tips for Web Apps", "postgres-tips",
             "Performance and design tips for using PostgreSQL with Flask.",
             "## PostgreSQL Tips\n\n1. **Use connection pooling** – PgBouncer or SQLAlchemy pool\n2. **Index wisely** – Cover common query patterns\n3. **Full-text search** – Use `tsvector` for search\n4. **JSONB columns** – Great for flexible schemas\n\n```sql\nCREATE INDEX idx_posts_author ON posts(author_id);\n```"),
            ("Building a REST API with Flask", "flask-rest-api",
             "Design patterns for building clean REST APIs.",
             "## REST API Design\n\n### Endpoints\n\n| Method | Path | Action |\n|--------|------|--------|\n| GET | /api/posts | List posts |\n| POST | /api/posts | Create post |\n| GET | /api/posts/<id> | Get post |\n\n### Response Format\n\n```json\n{\n  \"id\": 1,\n  \"title\": \"My Post\",\n  \"author\": \"alice\"\n}\n```", PostStatus.archived),
            ("Docker for Python Developers", "docker-python",
             "Containerize your Flask applications with Docker.",
             "## Docker + Flask\n\n```dockerfile\nFROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD [\"gunicorn\", \"app:app\"]\n```\n\n### docker-compose.yml\n\n```yaml\nservices:\n  web:\n    build: .\n    ports:\n      - \"5000:5000\"\n  db:\n    image: postgres:16\n```"),
            ("Async Python with asyncio", "async-python",
             "An introduction to asynchronous programming in Python.",
             "## Async Python\n\n```python\nimport asyncio\n\nasync def fetch_data(url):\n    async with aiohttp.ClientSession() as session:\n        async with session.get(url) as resp:\n            return await resp.json()\n\nasync def main():\n    data = await fetch_data('https://api.example.com')\n    print(data)\n\nasyncio.run(main())\n```"),
        ]

        posts = []
        for i, (title, slug, desc, content, *status_override) in enumerate(posts_data):
            author = users[i % len(users)]
            status = status_override[0] if status_override else PostStatus.published
            created = now - timedelta(hours=i * 3, minutes=random.randint(0, 59))

            post = Post(
                title=title,
                slug=slug,
                description=desc,
                content=content,
                status=status,
                author_id=author.id,
                published_at=created if status == PostStatus.published else None,
                created_at=created,
            )
            db.session.add(post)
            db.session.flush()
            posts.append(post)

        # ── Draft posts for Alice ─────────────────────────────
        draft_posts = [
            ("Work in Progress: Part 1", "wip-part-1",
             "A draft post I'm still working on.",
             "## Draft Content\n\nThis post is not ready yet."),
            ("Ideas for Next Quarter", "ideas-q2",
             "Brainstorming ideas for Q2.",
             "- Blog redesign\n- Newsletter integration\n- API documentation"),
        ]
        for title, slug, desc, content in draft_posts:
            post = Post(
                title=title,
                slug=slug,
                description=desc,
                content=content,
                status=PostStatus.draft,
                author_id=users[0].id,
            )
            db.session.add(post)
            db.session.flush()
            posts.append(post)

        # ── Likes ─────────────────────────────────────────────
        published = [p for p in posts if p.status == PostStatus.published]
        for user in users:
            # Each user likes 2-4 random published posts (excluding their own)
            others = [p for p in published if p.author_id != user.id]
            sample = random.sample(others, min(random.randint(2, 4), len(others)))
            for post in sample:
                like = PostLike(user_id=user.id, post_id=post.id)
                db.session.add(like)

        # ── Comments ──────────────────────────────────────────
        comment_texts = [
            "Great post! Really helpful.",
            "Thanks for sharing this!",
            "I've been looking for an article like this.",
            "Could you elaborate on the second point?",
            "This cleared up a lot of confusion, thanks!",
            "Bookmarked for later reference.",
            "Nice write-up! Would love to see a follow-up.",
        ]
        reply_texts = [
            "Thanks! Glad you found it useful.",
            "Sure, I'll write a follow-up soon.",
            "Good question! I'll update the post.",
            "Happy to help!",
        ]

        for post in published[:4]:
            # 2-4 top-level comments per post
            commenters = random.sample(users, min(random.randint(2, 4), len(users)))
            for commenter in commenters:
                comment = Comment(
                    content=random.choice(comment_texts),
                    user_id=commenter.id,
                    post_id=post.id,
                )
                db.session.add(comment)
                db.session.flush()

                # 1-2 replies on some comments
                if random.random() < 0.5:
                    repliers = random.sample(
                        [u for u in users if u.id != commenter.id],
                        min(random.randint(1, 2), len(users) - 1),
                    )
                    for replier in repliers:
                        reply = Comment(
                            content=random.choice(reply_texts),
                            user_id=replier.id,
                            post_id=post.id,
                            parent_id=comment.id,
                        )
                        db.session.add(reply)

        # ── Bookmarks ─────────────────────────────────────────
        for user in users:
            unbookmarked = [p for p in published
                            if not Bookmark.query.filter_by(
                                user_id=user.id, post_id=p.id).first()]
            sample = random.sample(unbookmarked, min(2, len(unbookmarked)))
            for post in sample:
                bookmark = Bookmark(user_id=user.id, post_id=post.id)
                db.session.add(bookmark)

        # ── Follows ───────────────────────────────────────────
        for user in users:
            others = [u for u in users if u.id != user.id]
            sample = random.sample(others, random.randint(1, len(others)))
            for target in sample:
                if not Follow.query.filter_by(
                    follower_id=user.id, following_id=target.id
                ).first():
                    follow = Follow(follower_id=user.id, following_id=target.id)
                    db.session.add(follow)

        db.session.commit()
        print("✓ Database seeded successfully!")
        print(f"  {len(users)} users")
        print(f"  {len(posts)} posts ({len(published)} published, {len(posts) - len(published)} draft/archived)")
        print(f"  Likes, comments, bookmarks, and follows populated")


if __name__ == "__main__":
    seed()
