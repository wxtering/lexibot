from .group.quiz import router as quiz_router
from .private.hangman import router as hangman_router
from .private.menu import router as menu_router
from .private.stats import router as stats_router

routers = [menu_router, hangman_router, quiz_router, stats_router]
