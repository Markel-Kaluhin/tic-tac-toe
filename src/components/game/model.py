from typing import List, Optional
from dataclasses import dataclass, field

from src.database.model.user import User


@dataclass
class Cell:
    """
    Data model of system entity - Cell
    Contains X and Y coordinates, as well as content, which is empty
     by default, but will contain the user character as soon as the
     user specified this field in the selection during the turn
    """
    x: int = field()
    y: int = field()
    value: Optional[str] = field(default=None)


@dataclass
class GameField:
    """
    Data model of system entity - GameField
    The game field data model is a field and methods for filling
     the field with data, based on a user decision, as well as
     counting winning combinations or a combination of playing a draw
    """
    game_metadata: List = field()
    _field: List[List[Cell]] = field(init=False)

    def __post_init__(self):
        self._field = self.__create_field()

    def __get_cell(self, x, y):
        """
        Used to get the value contained in the requested cell

        :param x: X coordinate
        :param y: Y coordinate
        :return: Returns the content of the requested cell
        """
        return self._field[x][y]

    def set_cell_value(self, x, y, value) -> Optional[User]:
        """
        This method is used to register a custom decision on the game field

        :param x: X coordinate
        :param y: Y coordinate
        :param value: The user's symbol is a unique identifier for his decision
        :return: Returns the result of calculating winning positions
        """
        cell = self.__get_cell(x, y)
        result = None
        if not cell.value:
            self.__get_cell(x, y).value = value
            result = self.__calculate_win_positions()
        else:
            raise ValueError('This cell is filled, please, choose another')
        return result

    @staticmethod
    def __create_field():
        """
        The game field is created here

        :return: Game field
        """
        return [
            [Cell(x=0, y=0), Cell(x=0, y=1), Cell(x=0, y=2)],
            [Cell(x=1, y=0), Cell(x=1, y=1), Cell(x=1, y=2)],
            [Cell(x=2, y=0), Cell(x=2, y=1), Cell(x=2, y=2)]
        ]

    def show_field(self):
        """
        The method is used to rendering the current state of the game field

        :return: None
        """
        print(f'''
        +-----+-----+-----+
        | {self.__show_cell(0, 0)} | {self.__show_cell(0, 1)} | {self.__show_cell(0, 2)} |
        +-----+-----+-----+
        | {self.__show_cell(1, 0)} | {self.__show_cell(1, 1)} | {self.__show_cell(1, 2)} |
        +-----+-----+-----+
        | {self.__show_cell(2, 0)} | {self.__show_cell(2, 1)} | {self.__show_cell(2, 2)} |
        +-----+-----+-----+
        ''')

    def __show_cell(self, x, y):
        """
        Required for post-processing values

        :param x: X coordinate
        :param y: Y coordinate
        :return: A string with the value to be displayed when
         rendering the game field
        """
        cell = self.__get_cell(x, y)
        if cell.value:
            return f' {cell.value} '
        else:
            return ','.join([str(x), str(y)])

    def __calculate_win_positions(self):
        """
        Entry point into the calculation of winning positions or positions of a draw

        :return: Winner User object or False in played a draw
        """
        result = []

        for player in self.game_metadata:
            result.append(self.__calculate_win_positions_by_rows(player=player))
            result.append(self.__calculate_win_positions_by_columns(player=player))
            result.append(self.__calculate_win_positions_by_diagonals(player=player))
            if any(result):
                print(f'''
        {player.User.nickname} wins!''')
                return player.User

            if self.__calculate_draw_game():
                print(f'''
        Played a draw!''')
                return False

    def __calculate_win_positions_by_rows(self, player):
        """
        Calculation of winning positions only horizontally

        :param player: Users are used only for getting the unique symbol
         for understand that it was he who won
        :return: Boolean with result of calculation winning positions
        """
        result = []
        for row in self._field:
            result.append(all([True if player.GameResult.symbol == cell.value else False for cell in row]))
        return any(result)

    def __calculate_win_positions_by_columns(self, player):
        """
        Calculation of winning positions only vertically

        :param player: Users are used only for getting the unique symbol
         for understand that it was he who won
        :return: Boolean with result of calculation winning positions
        """
        result = []
        columns = []
        for column in range(3):
            columns.append([row[column] for row in self._field])
        for column in columns:
            result.append(all([True if player.GameResult.symbol == cell.value else False for cell in column]))
        return any(result)

    def __calculate_win_positions_by_diagonals(self, player):
        """
        Calculation of winning positions only diagonally

        :param player: Users are used only for getting the unique symbol
         for understand that it was he who won
        :return: Boolean with result of calculation winning positions
        """
        result = []
        diagonal_1 = [[self._field[0][0], self._field[1][1], self._field[2][2]]]
        diagonal_2 = [[self._field[2][0], self._field[1][1], self._field[0][2]]]
        for diagonal in diagonal_1:
            result.append(all([True if player.GameResult.symbol == cell.value else False for cell in diagonal]))
        for diagonal in diagonal_2:
            result.append(all([True if player.GameResult.symbol == cell.value else False for cell in diagonal]))
        return any(result)

    def __calculate_draw_game(self):
        """
        Calculation of draw positions

        :return: Boolean with result of calculation draw positions
        """
        result = []
        for row in self._field:
            result.append(all([True if cell.value else False for cell in row]))
        return all(result)
