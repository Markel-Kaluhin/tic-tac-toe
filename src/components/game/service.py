import re
from random import randint
from typing import List, Optional, Tuple

import click
from sqlalchemy.orm import scoped_session

from src.components.game.model import GameField, GameState
from src.components.management.service import ManagementService
from src.database.model.game import Game, GameResult, GameUserDecision, LeagueSeason
from src.database.model.user import User

REQUIRED_PLAYERS_NUMBER = 2


class GameSession:
    """
    The main class of the gaming session. This is where the entire gameplay is controlled, and it also contains all
     the metadata about the game.

    Attributes:
        db_session: Session of connection to the database, through this object all interactions with the database occur
        symbols (List[str]): List of game symbols for players.
        chosen_players (List[Player]): List of chosen players for the current game.
        league (LeagueSeason): Current league.
        game_field (Optional[GameField]): GameField instance representing the game board.
        winner (Optional[User]): The winner of the game.
        game_metadata (Optional[List]): List of named tuples with Game, GameResult, User, and LeagueSeason objects.

    Methods:
        __init__(self, db_session, league):
            Initializes a GameSession instance.
        __choose_players(self):
            Selects players for the game.
        __create_game_session(self):
            Creates the game session including game records and field.
        __create_game(self):
            Creates a game record in the database.
        __create_game_result(self, game_id):
            Creates game results in the database.
        __get_game_metadata(self, game_id):
            Retrieves game metadata.
        __get_symbol(self):
            Gets a random symbol for a player.
        __game_session(self, next_player, wrong_choise=False):
            Manages the main game session.
        __save_user_decision(self, user, cell_item):
            Saves a user's game decision to the database.
        __summarise(self):
            Summarises the results of the game session.
    """

    symbols: List[str] = ["x", "o"]
    chosen_players: List[User] = []
    league: LeagueSeason
    game_field: Optional[GameField] = None
    game_state: GameState = GameState()
    game_metadata: List = []

    def __init__(self, db_session: scoped_session, league: LeagueSeason) -> None:
        """
        Initializes a GameSession instance.

        Args:
            db_session (scoped_session): Session of connection to the database, through this object all interactions
             with the database occur.
            league (LeagueSeason): Current league.
        """
        self.db_session = db_session
        self.league = league

    def start_game(self) -> None:
        """
        Start the game session.
        """
        self.__choose_players()
        self.__create_game_session()
        self.__game_session(randint(0, 1))
        self.__summarise()

    def __choose_players(self) -> None:
        """
        Selects players for the game.
        """
        print(
            f"""
        Choose the players. {REQUIRED_PLAYERS_NUMBER - len(self.chosen_players)} left:
        """
        )
        user_list = self.db_session.query(User).filter(User.id.notin_([i.id for i in self.chosen_players])).all()
        for i, player in enumerate(user_list):
            print(i, player.nickname)
        player_choice = input("Enter user id: ")
        if player_choice.isdigit():
            user_id = int(player_choice)
            self.chosen_players.append(user_list[user_id])
            if len(self.chosen_players) < REQUIRED_PLAYERS_NUMBER:
                self.__choose_players()
        else:
            print(
                """
        Wrong choice. Try again, please: """
            )
            self.__choose_players()

    def __create_game_session(self) -> None:
        """
        Creates the game session including game records and field.
        """
        game = self.__create_game()
        self.__create_game_result(game.id)
        self.__get_game_metadata(game.id)
        self.game_field = GameField(self.game_metadata)

    def __create_game(self) -> Game:
        """
        Creates a game record in the database.

        Returns:
            Game: Game object.
        """
        game = Game(league_season_id=self.league.id)  # type: ignore [call-arg]
        self.db_session.add(game)
        self.db_session.flush()
        self.db_session.refresh(game)
        return game

    def __create_game_result(self, game_id: int) -> None:
        """
        Creates game results in the database.

        Args:
            game_id (int): Game object identifier.
        """
        self.db_session.add_all(
            [
                GameResult(game_id=game_id, user_id=user.id, symbol=self.__get_symbol())  # type: ignore [call-arg]
                for user in self.chosen_players
            ]
        )
        self.db_session.commit()

    def __get_game_metadata(self, game_id: int) -> None:
        """
        Retrieves game metadata.

        Args:
            game_id (int): Game object identifier.
        """
        self.game_metadata = (
            self.db_session.query(Game, GameResult, User, LeagueSeason)
            .outerjoin(GameResult, GameResult.game_id == Game.id)
            .outerjoin(User, User.id == GameResult.user_id)
            .outerjoin(LeagueSeason, LeagueSeason.id == Game.league_season_id)
            .filter(Game.id == game_id)
            .all()
        )

    def __get_symbol(self) -> str:
        """
        Gets a random symbol for a player.

        Returns:
            str: Random symbol.
        """
        if len(self.symbols) > 1:
            symbol_index = randint(0, 1)
            result = self.symbols.pop(symbol_index)
        else:
            result = self.symbols[0]
        return result

    def __game_session(self, next_player_id: int, wrong_choice: bool = False) -> GameState:
        """
        Manages the main game session.

        Args:
            next_player_id(int): ID of the user participating in the session, which will play next time.
            wrong_choice (bool): A specific parameter required to pass the state of an invalid choice in
             the last call to this method. Defaults to False.

        Returns:
            GameState: Final state of the game

        """
        user = self.chosen_players[next_player_id]
        click.clear()
        if wrong_choice is not None:
            print(
                """
        Wrong choice. Try again, please: """
            )
        print(
            f"""
        {user.nickname} turn. Please, fill the cell: """
        )
        if self.game_field is not None:
            self.game_field.show_field()
        player_choice = input("Select field with two digits and comma between: ")
        if re.search(r"[0-2],[0-2]", player_choice):
            coordinates = player_choice.split(",")
            x_coordinate = int(coordinates.pop(0))
            y_coordinate = int(coordinates.pop(0))
            try:
                self.game_state = self.game_field.set_cell_value(  # type: ignore [union-attr]
                    x_coordinate=x_coordinate,
                    y_coordinate=y_coordinate,
                    value=next(i.GameResult.symbol for i in self.game_metadata if i.User.id == user.id),
                )
                self.__save_user_decision(user, (x_coordinate, y_coordinate))
            except ValueError as error:
                print(error)
                return self.__game_session(next_player_id)
            if self.game_state.is_end is True:
                return self.game_state
            next_player_id = 0 if next_player_id == 1 else 1
            return self.__game_session(next_player_id)
        return self.__game_session(next_player_id, wrong_choice=True)

    def __save_user_decision(self, user: User, cell_item: Tuple[int, int]) -> None:
        """
        Saves a user's game decision to the database.

        Args:
            user: User object.
            cell_item: Current field coordinates.
        """
        game_user_decision = GameUserDecision(  # type: ignore [call-arg]
            game_id=next(i.Game.id for i in self.game_metadata),
            user_id=user.id,
            coordinate_x=cell_item[0],
            coordinate_y=cell_item[1],
        )
        self.db_session.add(game_user_decision)
        self.db_session.commit()

    def __summarise(self) -> None:
        """
        Summarizes the results of the game session.
        """
        for i in self.game_metadata:
            i.GameResult.is_winner = i.User == self.game_state.winner
            self.db_session.add(i.GameResult)
        self.db_session.commit()


class GameService:
    """
    Service class for managing the game.

    Attributes:
        db_session: Session of connection to the database, through this object all interactions with the database occur.
        management_service: ManagementService instance for handling game management actions.

    Methods:
        __init__(self, db_session):
            Initializes a GameService instance.
        start_game(self):
            Launches the flow to prepare the application for the game and launch the game after this preparation.
        __check_exists_league(self):
            Checks the existence of the current league and creates one if it doesn't exist.
        __check_players_number(self):
            Checks the number of players and creates the required number of players if needed.

    """

    def __init__(self, db_session: scoped_session) -> None:
        """
        Initializes a GameService instance.

        Args:
            db_session(scoped_session): Session of connection to the database, through this object all interactions
             with the database occur.
        """
        self.db_session = db_session
        self.management_service = ManagementService(self.db_session)

    def start_game(self) -> None:
        """
        Launches the flow to prepare the application for the game and launch the game after this preparation.
        """
        league = self.__check_exists_league()
        self.__check_players_number()
        game_session = GameSession(self.db_session, league)
        game_session.start_game()

    def __check_exists_league(self) -> LeagueSeason:
        """
        Checks the existence of the current league and creates one if it doesn't exist.

        Returns:
            LeagueSeason: LeagueSeason object.
        """
        result: LeagueSeason = (
            self.db_session.query(LeagueSeason).order_by(LeagueSeason.id.desc()).limit(1).one_or_none()
        )

        if result:
            return result
        print(
            """
        You don't have any league season. You need to create one before start the game"""
        )
        self.management_service.create_new_league_season()
        return self.__check_exists_league()

    def __check_players_number(self) -> List[User]:
        """
        Checks the number of players and creates the required number of players if needed.

        Returns:
            List[User]: List of User objects corresponding to users registered in the system.
        """
        result: List[User] = self.db_session.query(User).all()

        if len(result) >= REQUIRED_PLAYERS_NUMBER:
            return result
        print(
            f"""
        You don't have any players. You need to create {REQUIRED_PLAYERS_NUMBER - len(result)} at least"""
        )
        self.management_service.player_create()
        return self.__check_players_number()
