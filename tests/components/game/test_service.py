import unittest
from unittest.mock import MagicMock, call, patch

from src.components.game.model import GameField
from src.components.game.service import GameService, GameSession
from src.database.model.game import GameUserDecision

REQUIRED_PLAYERS_NUMBER = 2


class TestGameSession(unittest.TestCase):
    def setUp(self):
        self.db_session = MagicMock()
        self.league = MagicMock()
        self.game_session = GameSession(self.db_session, self.league)

    @patch("src.components.game.service.input", side_effect=["0", "0"])
    def test_choose_players(self, mock_input):
        expected_chosen_players_count = 2
        user1 = MagicMock()
        user1.id = 1
        user1.nickname = "User1"
        user2 = MagicMock()
        user2.id = 2
        user2.nickname = "User2"
        self.db_session.query.return_value.filter.return_value.all.return_value = [user1, user2]
        self.game_session._GameSession__choose_players()
        self.assertEqual(len(self.game_session.chosen_players), expected_chosen_players_count)

    def test_create_game_session(self):
        game_id = 123
        expected_game_field = GameField()
        self.game_session._GameSession__create_game = MagicMock(return_value=MagicMock(id=game_id))
        self.game_session._GameSession__create_game_result = MagicMock()
        self.game_session._GameSession__get_game_metadata = MagicMock(return_value=[])
        self.game_session._GameSession__game_metadata = MagicMock()
        self.game_session._GameSession__create_game_session()
        self.game_session._GameSession__create_game.assert_called_once()
        self.game_session._GameSession__create_game_result.assert_called_once_with(game_id)
        self.game_session._GameSession__get_game_metadata.assert_called_once_with(game_id)
        self.assertEqual(self.game_session.game_field, expected_game_field)

    def test_create_game(self):
        league_id = 123
        expected_game = MagicMock()

        with patch("src.components.game.service.Game", return_value=expected_game) as mock_game:
            mock_game.return_value.league_season_id = league_id
            result = self.game_session._GameSession__create_game()
            mock_game.assert_called_once()
            self.db_session.add.assert_called_once_with(expected_game)
            self.db_session.flush.assert_called_once()
            self.db_session.refresh.assert_called_once_with(expected_game)
            self.assertEqual(result, expected_game)

    @patch("src.components.game.service.randint", return_value=0)
    def test_create_game_result(self, _):
        game_id = 123
        user_ids = [12, 23]
        expected_game_results = self.game_session.chosen_players = [MagicMock(id=user_id) for user_id in user_ids]

        with patch("src.components.game.service.GameResult", side_effect=expected_game_results) as mock_game_result:
            symbols = self.game_session.symbols[:]
            self.game_session._GameSession__create_game_result(game_id)
            self.game_session.symbols = symbols
            calls = [
                call(game_id=game_id, user_id=user_id, symbol=self.game_session._GameSession__get_symbol())
                for user_id in user_ids
            ]
            mock_game_result.assert_has_calls(calls)
            self.db_session.add_all.assert_called_once_with(expected_game_results)
            self.db_session.commit.assert_called_once()

    @patch("src.components.game.service.input", side_effect=["0,0"])  # Simulate user input
    @patch("src.components.game.service.GameField.set_cell_value", return_value=MagicMock(is_end=True))
    def test_game_session(self, mock_set_cell_value, _):
        next_player = 0
        wrong_choice = False
        user_ids = [12, 23]
        self.game_session.game_metadata = [
            MagicMock(
                User=MagicMock(
                    id=user_id,
                ),
                GameResult=MagicMock(
                    symbol="x",
                ),
            )
            for i, user_id in enumerate(user_ids)
        ]
        self.game_session.game_field = GameField(game_metadata=self.game_session.game_metadata)
        self.game_session.chosen_players = [MagicMock(id=user_id) for user_id in user_ids]
        result = self.game_session._GameSession__game_session(next_player, wrong_choice)
        mock_set_cell_value.assert_called_once_with(x=0, y=0, value="x")
        result.assert_not_called()

    def test_save_user_decision(self):
        user = MagicMock()
        user.id = 123
        game_id = 456
        cell_item = [1, 1]
        self.game_session = GameSession(self.db_session, self.league)
        self.game_session.game_metadata = [
            MagicMock(
                User=user,
                Game=MagicMock(
                    id=game_id,
                ),
            )
        ]
        self.game_session._GameSession__save_user_decision(user, cell_item)
        expected_game_user_decision = GameUserDecision(
            game_id=game_id, user_id=user.id, coordinate_x=cell_item[0], coordinate_y=cell_item[1]
        )
        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()
        game_user_decision = self.db_session.add.mock_calls[0].args[0]
        self.assertIsInstance(game_user_decision, expected_game_user_decision.__class__)
        game_user_decision_attributes = game_user_decision.__dict__
        game_user_decision_attributes.pop("_sa_instance_state")
        for key, value in game_user_decision_attributes.items():
            self.assertEqual(getattr(expected_game_user_decision, key), value)

    def test_summarise(self):
        user1 = MagicMock()
        user2 = MagicMock()
        game_metadata = [
            MagicMock(User=user1, GameResult=MagicMock(is_winner=False)),
            MagicMock(User=user2, GameResult=MagicMock(is_winner=True)),
        ]

        self.game_session.game_metadata = game_metadata
        self.game_session.game_state.winner = user2
        self.game_session._GameSession__summarise()
        expected_calls = [call(MagicMock(name="mock.GameResult", is_winner=is_winner)) for is_winner in [False, True]]
        self.assertEqual(
            list(map(lambda x: x.args[0].is_winner, self.db_session.add.call_args_list)),
            list(map(lambda x: x.args[0].is_winner, expected_calls)),
        )
        self.db_session.commit.assert_called_once()


class TestGameService(unittest.TestCase):
    def setUp(self):
        self.db_session = MagicMock()
        self.game_service = GameService(self.db_session)

    def test_check_exists_league_existing(self):
        existing_league = MagicMock()
        existing_league.id = 123
        mock_query = MagicMock(return_value=existing_league)
        self.db_session.query.return_value.order_by.return_value.limit.return_value.one_or_none = mock_query

        result = self.game_service._GameService__check_exists_league()

        self.assertEqual(result, existing_league)

    @patch("src.components.management.service.input", side_effect=["Test League"])
    def test_check_exists_league_not_existing(self, _):
        mock_query = MagicMock(side_effect=[None, MagicMock()])
        self.db_session.query.return_value.order_by.return_value.limit.return_value.one_or_none = mock_query

        with patch("src.components.game.service.print") as mock_game_print:
            with patch("src.components.management.service.print") as mock_management_print:
                result = self.game_service._GameService__check_exists_league()

        mock_management_print.assert_called_once_with("\n        New league season Test League was created.")
        mock_game_print.assert_called_once_with(
            "\n        You don't have any league season. You need to create one before start the game"
        )
        mock_management_print.assert_called()
        self.db_session.query.assert_called()

    def test_check_players_number_enough(self):
        enough_players = [MagicMock() for _ in range(REQUIRED_PLAYERS_NUMBER)]
        self.db_session.query.return_value.all.return_value = enough_players
        result = self.game_service._GameService__check_players_number()
        self.assertEqual(result, enough_players)

    @patch(
        "src.components.management.service.input",
        side_effect=["Firstname", "Lastname", "test@test.com", "NicknameTest", "30"],
    )
    def test_check_players_number_not_enough(self, _):
        not_enough_players = [MagicMock()]
        enough_players = [MagicMock(), MagicMock()]
        mock_query = MagicMock(side_effect=[not_enough_players, enough_players])
        self.db_session.query.return_value.all = mock_query

        with patch("src.components.game.service.print") as mock_print:
            self.game_service._GameService__check_players_number()

        mock_print.assert_called_once_with(
            f"\n        You don't have any players. You need to create {REQUIRED_PLAYERS_NUMBER - len(not_enough_players)} at least"
        )
        self.db_session.query.assert_called()
