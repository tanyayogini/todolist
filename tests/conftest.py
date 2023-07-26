from pytest_factoryboy import register

from tests.factories import UserFactory, BoardFactory, GoalFactory, GoalCategoryFactory

pytest_plugins = "tests.fixtures"
register(UserFactory)
register(BoardFactory)
register(GoalCategoryFactory)
register(GoalFactory)


