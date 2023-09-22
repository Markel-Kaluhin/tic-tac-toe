from typing import List, Optional, Tuple

from prettytable import PrettyTable
from sqlalchemy.orm import Session

from src.components.game.model import GameResultType
from src.database.model.game import Game, GameResult, LeagueSeason
from src.database.model.user import User


class MainMenuService:
    """
    Service class for managing the main menu functionalities.

    Attributes:
        db_session (Session): The database session.

    Methods:
        __init__(self, db_session):
            Initializes a MainMenuService instance.
        show_past_games_statistic(self) -> None:
            Display statistics for past games in the last league season.
        show_ranking_table(self, _user=None) -> None:
            Display a ranking table based on game results in the last league season.
        get_last_league_season(self) -> LeagueSeason:
            Get the last league season.
        __get_game_result_list(self, last_league_season: LeagueSeason):
            Get the results of games in the last league season.
    """

    def __init__(self, db_session: Session) -> None:
        """
        Initializes a MainMenuService instance.

        Args:
            db_session (Session): The database session.
        """
        self.db_session = db_session

    def show_past_games_statistic(self) -> None:
        """
        Display statistics for past games in the last league season.

        Returns:
            None
        """
        last_league_season = self.get_last_league_season()
        if not last_league_season:
            return
        game_result_list = self.__get_game_result_list(last_league_season)

        print(
            f"""
        Statistic for the games from league season: {last_league_season.name}"""
        )
        result = {i: {"players": [], "result": None} for i in {i.Game for i in game_result_list}}
        for game, _game_result in result.items():
            _game_result_list = [i for i in game_result_list if i.Game.id == game.id]
            _game_result["players"] = [i.User.nickname for i in _game_result_list]
            _game_result["result"] = next(
                (f"{i.User.nickname} is winner" for i in _game_result_list if i.GameResult.is_winner), "Played a draw"
            )

        table = PrettyTable()
        table.field_names = ["Players", "Result"]
        [
            table.add_row([" vs ".join(_game_result["players"]), _game_result["result"]])
            for game, _game_result in result.items()
        ]
        print(table)
        print("\n")

    def show_ranking_table(self, _user: Optional[User] = None) -> None:
        """
        Display a ranking table based on game results in the last league season.

        Args:
            _user (User, optional): User object to display ranking for a specific user.

        Returns:
            None
        """
        last_league_season = self.get_last_league_season()
        if not last_league_season:
            return
        game_result_list = self.__get_game_result_list(last_league_season)

        if _user:
            unique_user_list = {_user}
        else:
            unique_user_list = {i.User for i in game_result_list}

        result = {i: {"total_games": 0, "win": 0, "loss": 0, "pts": 0} for i in unique_user_list}
        for user, user_measures in result.items():
            for game_result in (i for i in game_result_list if i.User.id == user.id):
                user_measures["total_games"] += 1
                user_measures["win"] += 1 if game_result.GameResult.is_winner else 0
                user_measures["loss"] += 0 if game_result.GameResult.is_winner else 1
                user_measures["pts"] += 2 if game_result.GameResult.is_winner else 1

        table = PrettyTable()
        table.field_names = ["Nickname", "Total", "Win", "Loss", "Pts"]
        [table.add_row([user.nickname, *user_measures.values()]) for user, user_measures in result.items()]
        table.sortby = "Pts"
        table.reversesort = True
        print(table)
        print("\n")

    def get_last_league_season(self) -> LeagueSeason:
        """
        Get the last league season.

        Returns:
            LeagueSeason: LeagueSeason object from declarative data model.
        """
        result = self.db_session.query(LeagueSeason).order_by(LeagueSeason.id.desc()).limit(1).one_or_none()

        if result:
            return result
        else:
            print(
                """
        You don't have any league season. Create it and play some games before statistic will appear"""
            )

    def __get_game_result_list(self, last_league_season: LeagueSeason) -> List[GameResultType]:
        """
        Get the results of games in the last league season.

        Args:
            last_league_season (LeagueSeason): Needed to filter game results only for the last season.

        Returns:
            List: List of named tuples GameResult, User, Game objects from declarative data model.
        """
        return (
            self.db_session.query(GameResult, User, Game)
            .join(User, User.id == GameResult.user_id)
            .join(Game, Game.id == GameResult.game_id)
            .join(
                LeagueSeason,
                LeagueSeason.id == Game.league_season_id,
            )
            .filter(LeagueSeason.id == last_league_season.id)
        )
