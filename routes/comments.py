from flask import Blueprint,render_template, request, abort
from models import Comment, db, Post
from flask_login import login_required, current_user


comments_bp = Blueprint("comments", __name__)

@comments_bp.get("/posts/<int:post_id>/comments")
def load_post_comments(post_id):
    comments = (
        Comment.query
        .filter_by(post_id=post_id, parent_id=None)
        .order_by(Comment.created_at.desc())
        .limit(20)
        .all()
    )

    return render_template(
        "comments/comment-list.html",
        comments=comments,
        post_id=post_id
    )


# -------------------------------------------------------------------
@comments_bp.post("/posts/<int:post_id>/comment")
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get("content", "").strip()
    parent_id = request.form.get("parentId")

    if not content:
        abort(400, "Comment cannot be empty")

    if parent_id:
        parent_id = int(parent_id)
    else:
        parent_id = None

    comment = Comment(
        content=content,
        user_id=current_user.id,
        post_id=post_id,
        parent_id=parent_id
    )

    db.session.add(comment)
    db.session.commit()
    return render_template(
        "comments/comment-item.html",
        comment=comment,
        depth=0
    )


# -------------------------------------------------------------------

@comments_bp.get("/comments/<int:comment_id>/reply-form")
@login_required
def load_reply_form(comment_id):
    depth = request.args.get("depth", 1, type=int)
    return render_template("reply-form.html", comment_id=comment_id, depth=depth)

# -------------------------------------------------------------------

@comments_bp.post("/comments/<int:comment_id>/reply")
@login_required
def reply_comment(comment_id):
    parent = Comment.query.get_or_404(comment_id)
    content = request.form.get("content", "").strip()
    if not content:
        abort(400)

    reply = Comment(
        content=content,
        user_id=current_user.id,
        post_id=parent.post_id,
        parent_id=parent.id
    )

    db.session.add(reply)
    db.session.commit()

    reply_depth = request.form.get("depth", 1, type=int)
    return render_template("comments/reply-item.html", reply=reply, depth=reply_depth)


# -------------------------------------------------------------------

@comments_bp.get("/comments/<int:comment_id>/replies")
def load_replies(comment_id):
    offset = request.args.get("offset", 0, type=int)

    replies = (
        Comment.query
        .filter_by(parent_id=comment_id)
        .order_by(Comment.created_at.asc())
        .offset(offset)
        .limit(10)
        .all()
    )

    depth = request.args.get("depth", 1, type=int)

    return render_template(
        "comments/reply-list.html",
        replies=replies,
        comment_id=comment_id,
        next_offset=offset + len(replies),
        depth=depth
    )

@comments_bp.get("/comments/<int:comment_id>/reply-preview")
@login_required
def reply_preview(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return comment.content

# -------------------------------------------------------------------

@comments_bp.post("/comments/<int:comment_id>/delete")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    # only owner of comment can delete
    if comment.user_id != current_user.id:
        abort(403)

    db.session.delete(comment)
    db.session.commit()

    # HTMX: remove the element from DOM
    return ""

