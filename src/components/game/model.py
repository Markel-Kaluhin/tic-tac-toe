from dataclasses import dataclass, field
from typing import List, Optional

from src.database.model.game import Game, GameResult, LeagueSeason
from src.database.model.user import User


class GameResultType:
    GameResult: GameResult
    User: User
    Game: Game


class PlayerType(GameResultType):
    LeagueSeason: LeagueSeason


class GameState:
    is_end: bool = False
    winner: Optional[User] = None


@dataclass
class Cell:
    """
    Data model of the system entity - Cell.

    Attributes:
        x_coordinate (int): X coordinate.
        y_coordinate (int): Y coordinate.
        value (Optional[str]): Content of the cell (default: None).
    """

    x_coordinate: int = field()
    y_coordinate: int = field()
    value: Optional[str] = field(default=None)


@dataclass
class GameField:
    """
    Data model of the system entity - GameField.

    Attributes:
        game_metadata (List): List of game metadata.
        _field (List[List[Cell]]): 2D list representing the game field (initialized later).

    Methods:
        __post_init__(self):
            Initializes the GameField instance.
        __get_cell(self, x, y):
            Gets the value contained in the specified cell.
        set_cell_value(self, x, y, value) -> Optional[User]:
            Registers a custom decision on the game field.
        __create_field():
            Creates the game field.
        show_field(self):
            Renders the current state of the game field.
        __show_cell(self, x, y):
            Post-processes values for rendering.
        __calculate_win_positions(self):
            Entry point into the calculation of winning positions or positions of a draw.
        __calculate_win_positions_by_rows(self, player):
            Calculates winning positions horizontally.
        __calculate_win_positions_by_columns(self, player):
            Calculates winning positions vertically.
        __calculate_win_positions_by_diagonals(self, player):
            Calculates winning positions diagonally.
        __calculate_draw_game(self):
            Calculates draw positions.
    """

    game_metadata: List = field(default_factory=list)
    _field: List[List[Cell]] = field(init=False)

    def __post_init__(self) -> None:
        """
        Initializes a GameField instance.
        """
        self._field = self.__create_field()

    def __get_cell(self, x_coordinate: int, y_coordinate: int) -> Cell:
        """
        Gets the value contained in the requested cell.

        Args:
            x_coordinate (int): X coordinate.
            y_coordinate (int): Y coordinate.

        Returns:
            Cell: Returns the content of the requested cell.
        """
        return self._field[x_coordinate][y_coordinate]

    def set_cell_value(self, x_coordinate: int, y_coordinate: int, value: str) -> GameState:
        """
        Registers a custom decision on the game field.

        Args:
            x_coordinate (int): X coordinate.
            y_coordinate (int): Y coordinate.
            value (str): The user's symbol.

        Returns:
            Optional[User]: Winner User object or None if played a draw.
        """
        cell = self.__get_cell(x_coordinate, y_coordinate)
        if not cell.value:
            self.__get_cell(x_coordinate, y_coordinate).value = value
            result = self.__calculate_win_positions()
        else:
            raise ValueError("This cell is filled, please, choose another")
        return result

    @staticmethod
    def __create_field() -> List[List[Cell]]:
        """
        Creates the game field.

        Returns:
            List[List[Cell]]: Game field.
        """

        return [
            [
                Cell(x_coordinate=0, y_coordinate=0),
                Cell(x_coordinate=0, y_coordinate=1),
                Cell(x_coordinate=0, y_coordinate=2),
            ],
            [
                Cell(x_coordinate=1, y_coordinate=0),
                Cell(x_coordinate=1, y_coordinate=1),
                Cell(x_coordinate=1, y_coordinate=2),
            ],
            [
                Cell(x_coordinate=2, y_coordinate=0),
                Cell(x_coordinate=2, y_coordinate=1),
                Cell(x_coordinate=2, y_coordinate=2),
            ],
        ]

    def show_field(self) -> None:
        """
        Renders the current state of the game field.
        """
        print(
            f"""
        +-----+-----+-----+
        | {self.__show_cell(0, 0)} | {self.__show_cell(0, 1)} | {self.__show_cell(0, 2)} |
        +-----+-----+-----+
        | {self.__show_cell(1, 0)} | {self.__show_cell(1, 1)} | {self.__show_cell(1, 2)} |
        +-----+-----+-----+
        | {self.__show_cell(2, 0)} | {self.__show_cell(2, 1)} | {self.__show_cell(2, 2)} |
        +-----+-----+-----+
        """
        )

    def __show_cell(self, x_coordinate: int, y_coordinate: int) -> str:
        """
        Post-processes values for rendering.

        Args:
            x_coordinate (int): X coordinate.
            y_coordinate (int): Y coordinate.

        Returns:
            str: A string with the value to be displayed when rendering the game field.
        """
        cell = self.__get_cell(x_coordinate, y_coordinate)
        if cell.value:
            return f" {cell.value} "
        return ",".join([str(x_coordinate), str(y_coordinate)])

    def __calculate_win_positions(self) -> GameState:
        """
        Entry point into the calculation of winning positions or positions of a draw.

        Returns:
            Union[User, bool]: Winner User object or False if played a draw.
        """
        result = GameState()
        game_state_result = []

        for player in self.game_metadata:
            game_state_result.append(self.__calculate_win_positions_by_rows(player=player))
            game_state_result.append(self.__calculate_win_positions_by_columns(player=player))
            game_state_result.append(self.__calculate_win_positions_by_diagonals(player=player))
            if any(game_state_result):
                print(
                    f"""
        {player.User.nickname} wins!"""
                )
                result.is_end = True
                result.winner = player.User
                break

            if self.__calculate_draw_game():
                print(
                    """
        Played a draw!"""
                )
                result.is_end = True
                result.winner = None
                break
        return result

    def __calculate_win_positions_by_rows(self, player: PlayerType) -> bool:
        """
        Calculates winning positions only horizontally.

        Args:
            player: User representing a player.

        Returns:
            bool: Boolean with the result of the calculation of winning positions.
        """
        result = []
        for row in self._field:
            result.append(all(player.GameResult.symbol == cell.value for cell in row))
        return any(result)

    def __calculate_win_positions_by_columns(self, player: PlayerType) -> bool:
        """
        Calculates winning positions only vertically.

        Args:
            player: User representing a player.

        Returns:
            bool: Boolean with the result of the calculation of winning positions.
        """
        result = []
        columns = []
        for column_number in range(3):
            columns.append([row[column_number] for row in self._field])
        for column in columns:
            result.append(all(player.GameResult.symbol == cell.value for cell in column))
        return any(result)

    def __calculate_win_positions_by_diagonals(self, player: PlayerType) -> bool:
        """
        Calculates winning positions only diagonally.

        Args:
            player: User representing a player.

        Returns:
            bool: Boolean with the result of the calculation of winning positions.
        """
        result = []
        diagonal_1 = [[self._field[0][0], self._field[1][1], self._field[2][2]]]
        diagonal_2 = [[self._field[2][0], self._field[1][1], self._field[0][2]]]
        for diagonal in diagonal_1:
            result.append(all(player.GameResult.symbol == cell.value for cell in diagonal))
        for diagonal in diagonal_2:
            result.append(all(player.GameResult.symbol == cell.value for cell in diagonal))
        return any(result)

    def __calculate_draw_game(self) -> bool:
        """
        Calculates draw positions.

        Returns:
            bool: Boolean with the result of the calculation of draw positions.
        """
        result = []
        for row in self._field:
            result.append(all(cell.value is not None for cell in row))
        return all(result)
