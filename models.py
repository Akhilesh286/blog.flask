from datetime import datetime
from enum import Enum

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum as PgEnum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

# -------------------------------------------------------------------
# DB instance (THIS is what app.py imports)
# -------------------------------------------------------------------

db = SQLAlchemy()


# -------------------------------------------------------------------
# Mixins
# -------------------------------------------------------------------

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=datetime.utcnow
    )


class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# -------------------------------------------------------------------
# Enums
# -------------------------------------------------------------------

class PostStatus(Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


# -------------------------------------------------------------------
# Users
# -------------------------------------------------------------------

class User(db.Model, UserMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relations
    profile = relationship(
        "Profile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    posts = relationship(
        "Post", back_populates="author", cascade="all, delete-orphan"
    )
    likes = relationship("PostLike", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    following = relationship(
        "Follow",
        foreign_keys="[Follow.follower_id]",
        back_populates="follower",
        cascade="all, delete-orphan"
    )
    followers = relationship(
        "Follow",
        foreign_keys="[Follow.following_id]",
        back_populates="following",
        cascade="all, delete-orphan"
    )


    __table_args__ = (
        Index("ix_users_username", "username"),
        Index("ix_users_email", "email"),
    )


# -------------------------------------------------------------------
# Profile
# -------------------------------------------------------------------

class Profile(db.Model, TimestampMixin):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(100))
    gender: Mapped[str | None] = mapped_column(String(20))
    bio: Mapped[str | None] = mapped_column(Text)
    pic: Mapped[str | None] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(255))

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    user = relationship("User", back_populates="profile")


# -------------------------------------------------------------------
# Posts
# -------------------------------------------------------------------

class Post(db.Model, TimestampMixin):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)

    status: Mapped[PostStatus] = mapped_column(
        PgEnum(PostStatus, name="post_status"),
        default=PostStatus.draft,
        nullable=False,
    )

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Relations
    author = relationship("User", back_populates="posts")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan", lazy="dynamic")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan", lazy="dynamic")
    bookmarks = relationship("Bookmark", back_populates="post", cascade="all, delete-orphan", lazy="dynamic")

    __table_args__ = (
        Index("ix_posts_author", "author_id"),
        Index("ix_posts_status", "status"),
    )

# -------------------------------------------------------------------
# Post Likes
# -------------------------------------------------------------------

class PostLike(db.Model, TimestampMixin):
    __tablename__ = "post_likes"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )

    # Relations
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")

    __table_args__ = (
        db.UniqueConstraint("user_id", "post_id"),  # Prevent duplicate likes
        Index("ix_likes_user", "user_id"),
        Index("ix_likes_post", "post_id"),
    )


# -------------------------------------------------------------------
# Comment
# -------------------------------------------------------------------
class Comment(db.Model, TimestampMixin):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )

    # Relations
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

    replies = relationship(
        "Comment",
        cascade="all, delete-orphan",
        backref=backref("parent", remote_side=[id])
    )

    __table_args__ = (
        Index("ix_comments_post", "post_id"),
        Index("ix_comments_user", "user_id"),
    )



# -------------------------------------------------------------------
# Bookmark
# -------------------------------------------------------------------
class Bookmark(db.Model, TimestampMixin):
    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )

    # Relations
    user = relationship("User", back_populates="bookmarks")
    post = relationship("Post", back_populates="bookmarks")

    __table_args__ = (
        db.UniqueConstraint("user_id", "post_id"),  
        Index("ix_bookmarks_user", "user_id"),
        Index("ix_bookmarks_post", "post_id"),
    )


# -------------------------------------------------------------------
# Followers
# -------------------------------------------------------------------
class Follow(db.Model, TimestampMixin):
    __tablename__ = "follows"

    id: Mapped[int] = mapped_column(primary_key=True)

    follower_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    following_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Relations
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = relationship("User", foreign_keys=[following_id], back_populates="followers")

    __table_args__ = (
        db.UniqueConstraint("follower_id", "following_id"),
        CheckConstraint("follower_id != following_id"),  # prevent self-follow
        Index("ix_follow_follower", "follower_id"),
        Index("ix_follow_following", "following_id"),
    )
