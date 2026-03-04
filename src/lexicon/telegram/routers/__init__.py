from .chat.quiz_routers import router as quiz_router
from .private.common.menu import router as menu_router
from .private.common.stats import router as stats_router
from .private.hangman.routers_hangman import router as hangman_router

routers = [menu_router, hangman_router, quiz_router, stats_router]
