from routers.auth import router as auth_router
from routers.blog import router as blog_router
from routers.contacts import router as contacts_router
from routers.events import router as events_router
from routers.dashboard import router as dashboard_router

__all__ = ["auth_router", "blog_router", "contacts_router", "events_router", "dashboard_router"]
