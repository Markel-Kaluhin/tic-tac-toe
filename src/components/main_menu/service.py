from prettytable import PrettyTable

from src.database.model.user import User
from src.database.model.game import Game, GameResult, LeagueSeason


class MainMenuService:
    def __init__(self, db_session):
        self.db_session = db_session

    def show_past_games_statistic(self) -> None:
        """
        The table that is generated here is generated from the data obtained
         from the list of games that are included in the last season.
        First, we take the last league, then - the results of all games in the
         last league, after which, by comprehension the dictionary, we write
         the object of the game into the key and, in the meaning, the list
         of users and the result - an explanation of how the game ended.
        After that, we fill in the data in the values of the dictionary and
        transfer it to PrettyTable for rendering

        :return: None
        """
        last_league_season = self.get_last_league_season()
        if not last_league_season:
            return
        game_result_list = self.__get_game_result_list(last_league_season)

        print(f'''
        Statistic for the games from league season: {last_league_season.name}''')
        result = {
            i: {
                'players': [],
                'result': None
            } for i in {i.Game for i in game_result_list}
        }
        for game, _game_result in result.items():
            _game_result_list = [i for i in game_result_list if i.Game.id == game.id]
            _game_result['players'] = [i.User.nickname for i in _game_result_list]
            _game_result['result'] = next(
                (f'{i.User.nickname} is winner' for i in _game_result_list if i.GameResult.is_winner),
                'Played a draw'
            )

        table = PrettyTable()
        table.field_names = ['Players', 'Result']
        [table.add_row([
            ' vs '.join(_game_result['players']),
            _game_result['result']
        ]) for game, _game_result in result.items()]
        print(table)
        print('\n')

    def show_ranking_table(self, _user=None) -> None:
        """
        The table that is generated here is generated from the data obtained
         from the list of games that are included in the last season.
        First, we take the last league, then - the results of all games
         in the last league, after which, by comprehension the dictionary,
         we write the User object into the key, and the value contains
         counters: total games played, victories, defeats, points.
        Then we fill in these values and pass them to for rendering.
        Data ordered by points with reverse

        :return: None
        """
        last_league_season = self.get_last_league_season()
        if not last_league_season:
            return
        game_result_list = self.__get_game_result_list(last_league_season)

        if _user:
            unique_user_list = {_user}
        else:
            unique_user_list = {i.User for i in game_result_list}

        result = {
            i: {
                'total_games': 0,
                'win': 0,
                'loss': 0,
                'pts': 0
            } for i in unique_user_list
        }
        for user, user_measures in result.items():
            for game_result in (i for i in game_result_list if i.User.id == user.id):
                user_measures['total_games'] += 1
                user_measures['win'] += 1 if game_result.GameResult.is_winner else 0
                user_measures['loss'] += 0 if game_result.GameResult.is_winner else 1
                user_measures['pts'] += 2 if game_result.GameResult.is_winner else 1

        table = PrettyTable()
        table.field_names = ['Nickname', 'Total', 'Win', 'Loss', 'Pts']
        [table.add_row([
            user.nickname,
            *user_measures.values()
        ]) for user, user_measures in result.items()]
        table.sortby = 'Pts'
        table.reversesort = True
        print(table)
        print('\n')

    def get_last_league_season(self) -> LeagueSeason:
        """
        Receives the last object if it exists or a message that
         it needs to be created if no league exists

        :return: LeagueSeason object from decorative data model
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
        You don't have any league season. Create it and play some games before statistic will appear''')

    def __get_game_result_list(self, last_league_season: LeagueSeason):
        """
        Getting the results of games in the current season

        :param last_league_season: Needed to filter game results only for
         the last season
        :return: List of named tuples GameResult, User, Game objects from
         declarative data model
        """
        return self.db_session.query(
            GameResult, User, Game
        ).join(
            User, User.id == GameResult.user_id
        ).join(
            Game, Game.id == GameResult.game_id
        ).join(
            LeagueSeason, LeagueSeason.id == Game.league_season_id,
        ).filter(
            LeagueSeason.id == last_league_season.id
        )
