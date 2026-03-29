from app.config import get_settings

settings = get_settings()


ROBOTS_TEMPLATE = """User-agent: *
Disallow: /admin
Disallow: /auth
Allow: /

Sitemap: {site_url}/sitemap.xml
"""


def robots_txt() -> str:
    return ROBOTS_TEMPLATE.format(site_url=settings.site_url)
