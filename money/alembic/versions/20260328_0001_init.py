"""initial schema

Revision ID: 20260328_0001
Revises:
Create Date: 2026-03-28 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260328_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    timestamp = sa.text("CURRENT_TIMESTAMP")
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), server_default=timestamp),
    )
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False, unique=True),
        sa.Column("description", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime(), server_default=timestamp),
    )
    op.create_table(
        "keywords",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("phrase", sa.String(length=255), nullable=False, unique=True),
        sa.Column("slug", sa.String(length=255), nullable=False, unique=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id")),
        sa.Column("search_intent", sa.String(length=50)),
        sa.Column("priority_score", sa.Numeric(5, 2), server_default=sa.text("0")),
        sa.Column("country", sa.String(length=8)),
        sa.Column("language", sa.String(length=8)),
        sa.Column("source", sa.String(length=50)),
        sa.Column("topic_family", sa.String(length=120)),
        sa.Column("target_page_type", sa.String(length=60)),
        sa.Column("dedup_hash", sa.String(length=64)),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=timestamp),
        sa.Column("updated_at", sa.DateTime(), server_default=timestamp),
        sa.Column("last_generated_at", sa.DateTime()),
    )
    op.create_table(
        "pages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("keyword_id", sa.Integer(), sa.ForeignKey("keywords.id")),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id")),
        sa.Column("slug", sa.String(length=255), nullable=False, unique=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("meta_title", sa.String(length=255), nullable=False),
        sa.Column("meta_description", sa.String(length=255), nullable=False),
        sa.Column("h1", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text()),
        sa.Column("intro", sa.Text()),
        sa.Column("body_json", sa.JSON(), nullable=False),
        sa.Column("faq_json", sa.JSON()),
        sa.Column("schema_json", sa.JSON()),
        sa.Column("related_topics", sa.JSON()),
        sa.Column("page_type", sa.String(length=60), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("canonical_url", sa.String(length=255)),
        sa.Column("language", sa.String(length=8), server_default=sa.text("'en'")),
        sa.Column("country_target", sa.String(length=8), server_default=sa.text("'global'")),
        sa.Column("word_count", sa.Integer(), server_default=sa.text("0")),
        sa.Column("reading_time", sa.Integer(), server_default=sa.text("1")),
        sa.Column("quality_score", sa.Integer(), server_default=sa.text("80")),
        sa.Column("featured", sa.Boolean(), server_default=sa.text("0")),
        sa.Column("noindex", sa.Boolean(), server_default=sa.text("0")),
        sa.Column("ads_enabled", sa.Boolean(), server_default=sa.text("1")),
        sa.Column("author_name", sa.String(length=120)),
        sa.Column("cta_text", sa.String(length=255)),
        sa.Column("affiliate_block", sa.Text()),
        sa.Column("updated_at", sa.DateTime(), server_default=timestamp),
        sa.Column("created_at", sa.DateTime(), server_default=timestamp),
        sa.Column("publish_at", sa.DateTime()),
        sa.Column("published_at", sa.DateTime()),
    )
    op.create_table(
        "generation_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("keyword_id", sa.Integer(), sa.ForeignKey("keywords.id")),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("prompt_name", sa.String(length=60), nullable=False),
        sa.Column("model_name", sa.String(length=60)),
        sa.Column("payload", sa.JSON()),
        sa.Column("response", sa.JSON()),
        sa.Column("error_message", sa.Text()),
        sa.Column("requested_at", sa.DateTime(), server_default=timestamp),
        sa.Column("completed_at", sa.DateTime()),
    )
    op.create_table(
        "publish_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("page_id", sa.Integer(), sa.ForeignKey("pages.id")),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("scheduled_for", sa.DateTime()),
        sa.Column("started_at", sa.DateTime()),
        sa.Column("completed_at", sa.DateTime()),
        sa.Column("error_message", sa.Text()),
    )
    op.create_table(
        "settings",
        sa.Column("key", sa.String(length=100), primary_key=True),
        sa.Column("value", sa.Text()),
        sa.Column("updated_at", sa.DateTime(), server_default=timestamp),
    )
    op.create_table(
        "internal_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("from_page_id", sa.Integer(), sa.ForeignKey("pages.id")),
        sa.Column("to_page_id", sa.Integer(), sa.ForeignKey("pages.id")),
        sa.Column("anchor_text", sa.String(length=255), nullable=False),
        sa.Column("relevance_score", sa.Float(), server_default=sa.text("0.5")),
        sa.Column("created_at", sa.DateTime(), server_default=timestamp),
    )
    op.create_table(
        "log_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("level", sa.String(length=20)),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("context", sa.String(length=60)),
        sa.Column("metadata", sa.JSON()),
        sa.Column("created_at", sa.DateTime(), server_default=timestamp),
    )


def downgrade() -> None:
    op.drop_table("log_events")
    op.drop_table("internal_links")
    op.drop_table("settings")
    op.drop_table("publish_jobs")
    op.drop_table("generation_jobs")
    op.drop_table("pages")
    op.drop_table("keywords")
    op.drop_table("categories")
    op.drop_table("users")
