from typing import Dict

from app.config import get_settings

settings = get_settings()


def default_meta() -> Dict[str, str]:
    return {
        "site_name": settings.project_name,
        "title": settings.project_name,
        "description": "Fresh auto-generated explainers, templates, and quick answers updated daily.",
        "url": settings.site_url,
        "image": f"{settings.site_url}/static/og-default.png",
    }


def page_meta(page) -> Dict[str, str]:
    data = default_meta()
    data.update(
        {
            "title": page.meta_title,
            "description": page.meta_description,
            "url": f"{settings.site_url}/{page.slug}",
        }
    )
    return data
