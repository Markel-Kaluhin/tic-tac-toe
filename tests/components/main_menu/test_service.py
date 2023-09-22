import unittest
from unittest.mock import MagicMock, patch

from prettytable import PrettyTable

from src.components.main_menu.service import MainMenuService


class TestMainMenuService(unittest.TestCase):
    def setUp(self):
        self.db_session = MagicMock()
        self.menu_service = MainMenuService(self.db_session)

    def test_show_past_games_statistic(self):
        last_league_season = MagicMock()
        last_league_season.name = "Test League Season"
        self.menu_service.get_last_league_season = MagicMock(return_value=last_league_season)
        with patch("src.components.main_menu.service.print") as mock_print:
            self.menu_service.show_past_games_statistic()
        table = PrettyTable()
        table.field_names = ["Players", "Result"]
        self.assertEqual(
            list(map(lambda x: str(x.args[0]), mock_print.call_args_list)),
            [f"\n        Statistic for the games from league season: {last_league_season.name}", str(table), "\n"],
        )

    def test_show_ranking_table(self):
        last_league_season = MagicMock()
        self.menu_service.get_last_league_season = MagicMock(return_value=last_league_season)
        game_result_list = [MagicMock(), MagicMock()]
        self.menu_service._MainMenuService__get_game_result_list = MagicMock(return_value=game_result_list)
        with patch("src.components.main_menu.service.print") as mock_print:
            self.menu_service.show_ranking_table()
        mock_print.assert_called()

    def test_get_last_league_season_existing(self):
        existing_league_season = MagicMock()
        existing_league_season.name = "Test League Season"
        mock_query = MagicMock(return_value=existing_league_season)
        self.menu_service.db_session.query.return_value.order_by.return_value.limit.return_value.one_or_none = (
            mock_query
        )
        result = self.menu_service.get_last_league_season()
        self.assertEqual(result, existing_league_season)
        mock_query.assert_called_once()

    def test_get_last_league_season_not_existing(self):
        mock_query = MagicMock(return_value=None)
        self.menu_service.db_session.query.return_value.order_by.return_value.limit.return_value.one_or_none = (
            mock_query
        )
        with patch("src.components.main_menu.service.print") as mock_print:
            result = self.menu_service.get_last_league_season()
        mock_print.assert_called_once_with(
            "\n        You don't have any league season. Create it and play some games before statistic will appear"
        )
        self.assertIsNone(result)
        mock_query.assert_called_once()
