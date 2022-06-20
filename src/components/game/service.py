from src.database.model.user import User
from src.database.model.game import (
    Game, GameResult, GameUserDecision,
    LeagueSeason
)
from src.components.game.model import GameField
from src.components.management import ManagementService
from random import randint
import re
import click

from typing import List, Optional

REQUIRED_PLAYERS_NUMBER = 2


class GameSession:
    symbols: List[str]
    choosed_players: List[User]
    league: LeagueSeason
    game_field: Optional[GameField]
    winner: Optional[User]
    game_metadata: Optional[List]

    def __init__(self, db_session, league):
        """
        The main class of the gaming session. This is where the entire
         gameplay is controlled, and it also contains all the metadata
         about the game.

        :param db_session: Session of connection to the database,
         through this object all interactions with the database occur
        :param league: Current league
        """
        self.db_session = db_session
        self.symbols = ['x', 'o']
        self.choosed_players = []
        self.league = league
        self.game_field = None
        self.winner = None
        self.game_metadata = None
        self.__choose_players()
        self.__create_game_session()
        self.__game_session(randint(0, 1))
        self.__summarise()

    def __choose_players(self):
        """
        Here you select players from the list of players.
        At the previous stage in the game service, we created
         the required number of players. If we launched the game for
         the first time and created players using a mechanism that
         starts at the beginning of a new game, then we will choose
         two players from two players, which is strange but logical

        :return: None
        """
        print(f'''
        Choose the players. {REQUIRED_PLAYERS_NUMBER - len(self.choosed_players)} left: 
        ''')
        user_list = self.db_session.query(
            User
        ).filter(
            User.id.notin_([i.id for i in self.choosed_players])
        ).all()
        for i, player in enumerate(user_list):
            print(i, player.nickname)
        user_item = input('Enter user id: ')
        if user_item.isdigit():
            user_item = int(user_item)
            self.choosed_players.append(user_list[user_item])
            if len(self.choosed_players) < REQUIRED_PLAYERS_NUMBER:
                self.__choose_players()
        else:
            print('''
        Wrong choice. Try again, please: ''')
            self.__choose_players()

    def __create_game_session(self):
        """
        Here the game session is created, first the necessary
         records are created in the database, then
         the field is created

        :return: None
        """
        game = self.__create_game()
        self.__create_game_result(game.id)
        self.__get_game_metadata(game.id)
        self.game_field = GameField(self.game_metadata)

    def __create_game(self):
        """
        Creating a game record in the database

        :return: Game object
        """
        game = Game(
            league_season_id=self.league.id
        )
        self.db_session.add(game)
        self.db_session.flush()
        self.db_session.refresh(game)
        return game

    def __create_game_result(self, game_id):
        """
        Creation of game results, the results will be updated
         after the end of the game

        :param game_id: Game object identifier
        :return: None
        """
        self.db_session.add_all([GameResult(
            game_id=game_id,
            user_id=user.id,
            symbol=self.__get_symbol()
        ) for user in self.choosed_players])
        self.db_session.commit()

    def __get_game_metadata(self, game_id):
        """
        Getting game metadata for in-game logic

        :param game_id: Game object identifier
        :return: List of named tuple with Game, GameResult, User and
         LeagueSeason objects
        """
        self.game_metadata = self.db_session.query(
            Game, GameResult, User, LeagueSeason
        ).outerjoin(
            GameResult, GameResult.game_id == Game.id
        ).outerjoin(
            User, User.id == GameResult.user_id
        ).outerjoin(
            LeagueSeason, LeagueSeason.id == Game.league_season_id
        ).filter(
            Game.id == game_id
        ).all()

    def __get_symbol(self):
        """
        One character is randomly selected from the list of presented

        :return: String with only one char that will write as
         the player symbol in current game
        """
        result = None
        if len(self.symbols) > 1:
            symbol_index = randint(0, 1)
            result = self.symbols.pop(symbol_index)
        else:
            result = self.symbols[0]
        return result

    def __game_session(self, next_player, wrong_choise=False):
        """
        The main method of the game session, all steps are done through
         a sequential recursive call to this method

        :param next_player: ID of the user participating in the session,
         which will play next time
        :param wrong_choise: A specific parameter required to pass
         the state of an invalid choice in the last call to this method
        :return: None
        """
        user = self.choosed_players[next_player]
        click.clear()
        print('''
        Wrong choice. Try again, please: ''') if wrong_choise else None
        print(f'''
        {user.nickname} turn. Please, fill the cell: ''')
        self.game_field.show_field()
        cell_item = input('Select field with two digits and comma between: ')
        if re.search(r'[0-2],[0-2]', cell_item):
            cell_item = [int(i) for i in cell_item.split(',')]
            try:
                self.winner = self.game_field.set_cell_value(
                    x=cell_item[0],
                    y=cell_item[1],
                    value=next(i.GameResult.symbol for i in self.game_metadata if i.User.id == user.id)
                )
                self.__save_user_decision(user, cell_item)
            except ValueError as e:
                print(e)
                self.__game_session(next_player)
            if self.winner:
                self.game_field.show_field()
                return
            elif self.winner is False:
                self.game_field.show_field()
                return
            else:
                next_player = 0 if next_player == 1 else 1
                self.__game_session(next_player)
        else:
            self.__game_session(next_player, wrong_choise=True)

    def __save_user_decision(self, user, cell_item):
        """
        Saving the results of a custom decision to a database.
        Every decision of each user in the current game will be saved

        :param user: User object
        :param cell_item: Current field coordinates
        :return: None
        """
        game_user_decision = GameUserDecision(
            game_id=next(i.Game.id for i in self.game_metadata),
            user_id=user.id,
            coordinate_x=cell_item[0],
            coordinate_y=cell_item[1]
        )
        self.db_session.add(game_user_decision)
        self.db_session.commit()

    def __summarise(self):
        """
        Summing up the results of the current gaming session

        :return: None
        """
        for i in self.game_metadata:
            i.GameResult.is_winner = True if i.User == self.winner else False
            self.db_session.add(i.GameResult)
        self.db_session.commit()


class GameService:
    def __init__(self, db_session):
        self.db_session = db_session
        self.management_service = ManagementService(self.db_session)

    def start_game(self):
        """
        Launching flow to prepare the application for the game and
         launch the game after this preparation

        :return: None
        """
        league = self.__check_exists_league()
        self.__check_players_number()
        GameSession(self.db_session, league)

    def __check_exists_league(self):
        """
        Checking the existence of the current league. If no league is
         registered in the system, the Application offers to create
         a league right here using the functionality from the management
         service

        :return: LeagueSeason object
        """
        result = self.db_session.query(
            LeagueSeason
        ).order_by(
            LeagueSeason.id.desc()
        ).limit(1).one_or_none()

        if result:
            return result
        else:
            print('''
        You don't have any league season. You need to create one before start the game''')
            self.management_service.create_new_league_season()
            return self.__check_exists_league()

    def __check_players_number(self):
        """
        To start the game, the user needs to select players, if there are
         no players in the system or there are fewer than needed to start
         the game, the application asks to create the missing number of
         players. As soon as the players are created this item in the system
         check before the start of the game session will be passed.

        :return: List of User objects corresponding to users registered
         in the system
        """
        result = self.db_session.query(User).all()

        if len(result) >= REQUIRED_PLAYERS_NUMBER:
            return result
        else:
            print(f'''
        You don't have any players. You need to create {REQUIRED_PLAYERS_NUMBER - len(result)} at least''')
            self.management_service.player_create()
            self.__check_players_number()
