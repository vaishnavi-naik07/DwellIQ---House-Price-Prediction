from frontend.pages.auth import render_full_auth_page

# Maintain backward compatibility for any existing imports
render_auth_page = render_full_auth_page

__all__ = ["render_full_auth_page", "render_auth_page"]
