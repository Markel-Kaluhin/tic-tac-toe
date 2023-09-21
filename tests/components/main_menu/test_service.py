import unittest
from unittest.mock import MagicMock, patch

from src.components.main_menu.service import MainMenuService


class TestMainMenuService(unittest.TestCase):
    def setUp(self):
        self.db_session = MagicMock()
        self.main_menu_service = MainMenuService(self.db_session)

    def test_show_past_games_statistic(self):
        self.main_menu_service.get_last_league_season = MagicMock(return_value=None)
        print_mock = MagicMock()
        with patch("builtins.print", print_mock):
            self.main_menu_service.show_past_games_statistic()
        print_mock.assert_called()

    def test_show_ranking_table(self):
        self.main_menu_service.get_last_league_season = MagicMock(return_value=None)
        print_mock = MagicMock()
        with patch("builtins.print", print_mock):
            self.main_menu_service.show_ranking_table()
        print_mock.assert_called()

    def test_get_last_league_season(self):
        self.db_session.query.return_value.order_by.return_value.limit.return_value.one_or_none.return_value = None
        result = self.main_menu_service.get_last_league_season()
        self.assertIsNone(result)

    def test__get_game_result_list(self):
        # TODO: Implement this test based on your specific use case
        pass
