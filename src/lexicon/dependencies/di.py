from dishka import Provider, Scope, make_async_container, provide, provide_all
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.lexicon.configuration.cfg import BotConfig, DatabaseConfig
from src.lexicon.database.session import DEFAULT_SESSION_FACTORY
from src.lexicon.services.entity.uow import UnitOfWork
from src.lexicon.services.logic.games.hangman import HangmanService
from src.lexicon.services.logic.games.quiz import QuizService
from src.lexicon.services.logic.stats.stats import StatsService
from src.lexicon.services.logic.user import UserService


class AsyncSessionProvider(Provider):
    @provide(scope=Scope.APP)
    def get_session(self) -> async_sessionmaker:
        return DEFAULT_SESSION_FACTORY

    @provide(scope=Scope.REQUEST)
    def get_uow(self, session_factory: async_sessionmaker) -> UnitOfWork:
        return UnitOfWork(session_factory=session_factory)


class ServicesProvider(Provider):
    scope = Scope.REQUEST
    services = provide_all(HangmanService, QuizService, StatsService, UserService)


container = make_async_container(AsyncSessionProvider(), ServicesProvider())
