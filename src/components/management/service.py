from typing import List, Tuple

from sqlalchemy.orm import scoped_session
from terminalplot import plot

from src.components.main_menu.service import MainMenuService
from src.components.utility.controller import Utility
from src.database.model.game import Game, GameResult, LeagueSeason
from src.database.model.user import User
from src.handler.model import Handler


class ManagementService:
    """
    Service class for managing application data and functionalities.

    Attributes:
        db_session (Any): The database session.
        main_menu_service (MainMenuService): An instance of the MainMenuService.

    Methods:
        show_player_list(self, handler, destination_component, destination_method):
            Show a list of users before deletion and requesting detailed information about a user.
        show_player_details(self, user) -> None:
            Display detailed information about a user and related data.
        __calculate_point_growing_chart(self, user):
            Calculate the growth dynamics of a user's points for a chart.
        __concat_user_detail(self, user):
            Concatenate user details based on available information.
        player_create(self) -> None:
            Create a new user by obtaining user input.
        create_new_league_season(self) -> None:
            Create a new league season.
    """

    def __init__(self, db_session: scoped_session) -> None:
        """
        Initializes a ManagementService instance.

        Args:
            db_session (Any): The database session.
        """
        self.db_session = db_session
        self.main_menu_service = MainMenuService(self.db_session)

    def show_player_list(self, handler: Handler, destination_component: str, destination_method: str) -> List[Handler]:
        """
        Show a list of users before deletion and requesting detailed information about a user.

        Args:
            handler (Handler): The handler from which this handler was called.
            destination_component (str): Name of the component to get the route.
            destination_method (str): Name of the component's method to get the route.

        Returns:
            List[Handler]: List of handlers for displaying users and the "previous" item.
        """

        user_list = self.db_session.query(User).all()
        result = []
        last_menu_item = 0
        for i, user in enumerate(user_list):
            last_menu_item = i
            _handler = Handler(
                id=i,
                name=user.nickname,
                component=destination_component,
                method=destination_method,
                kwargs={"user": user},
            )
            _handler.parent = handler
            result.append(_handler)
        previous = Handler(id=last_menu_item + 1, name="Previous", component=Utility, method="previous_menu_item")
        previous.parent = handler
        result.append(previous)

        return result

    def show_player_details(self, user: User) -> None:
        """
        Display detailed information about a user and related data.

        Args:
            user (User): User object from declarative data model.

        Returns:
            None
        """
        user_detail = self.__concat_user_detail(user)
        growing_chart = self.__calculate_point_growing_chart(user)

        print(
            f"""
        {'-' * 50}
        User detail:
        {'-' * 50}
        """
        )
        print(user_detail)
        print(
            f"""
        {'-' * 50}
        Ranking table:
        {'-' * 50}
        """
        )
        self.main_menu_service.show_ranking_table(user)
        if growing_chart:
            print(
                f"""
        {'-' * 50}
        Points growth dynamics:
        {'-' * 50}
            """
            )
            plot(*growing_chart)

    def __calculate_point_growing_chart(self, user: User) -> Tuple[range, List[int]] | None:
        """
        Calculate the growth dynamics of a user's points for a chart.

        Args:
            user (User): User object from declarative data model.

        Returns:
            Tuple: Lists of values in x, y_coordinate coordinates.
        """
        current_league = self.main_menu_service.get_last_league_season()
        game_results = (
            self.db_session.query(GameResult)
            .join(Game, Game.id == GameResult.game_id)
            .join(LeagueSeason, LeagueSeason.id == Game.league_season_id)
            .filter(LeagueSeason.id == current_league.id if current_league else None)
            .filter(GameResult.user_id == user.id)
            .order_by(GameResult.game_id.asc())
            .all()
        )
        result = None
        if game_results:
            x_coordinate = range(len(game_results))
            y_coordinate = []
            points = 0
            for i in game_results:
                points += 2 if i.is_winner else 1
                y_coordinate.append(points)
            result = x_coordinate, y_coordinate
        return result

    def __concat_user_detail(self, user: User) -> str:
        """
        Concatenate user details based on available information.

        Args:
            user (User): User object from declarative data model.

        Returns:
            str: Concatenated string with user detailed description.
        """
        label = """
                Only completed fields will be displayed in the user's detailed information
                """
        if user.first_name or user.last_name:
            user.first_name = "" if user.first_name is None else user.first_name
            user.last_name = "" if user.last_name is None else user.last_name
            label += f"""
                Detail of player {user.first_name} {user.last_name}:
                """
        if user.nickname:
            label += f"""
                Nickname: {user.nickname}"""
        if user.age:
            label += f"""
                Age: {user.age} years old"""
        if user.email:
            label += f"""
                Email: {user.email}"""
        label += "\n"
        return label

    def player_create(self) -> None:
        """
        Create a new user by obtaining user input.

        Returns:
            None
        """
        user = User()
        field_name = ""

        is_valid_form = False
        while not is_valid_form:
            try:
                print(
                    """
        Field marked with * is required"""
                )
                for field in (i for i in user.__table__.c if i.name != "id"):  # type: ignore [attr-defined] # pylint: disable=no-member
                    if getattr(user, field.name) is None:
                        label = "* " if not field.nullable else ""
                        label += field.name.capitalize().replace("_", " ")
                        label += ": "
                        setattr(user, field_name, "")
                        setattr(user, field.name, input(label))
            except AssertionError as error:
                print(error.args[0])
                field_name = error.args[1]
            else:
                self.db_session.add(user)
                self.db_session.commit()
                is_valid_form = True

        print(
            f"""
        Player {user.first_name} {user.last_name} has been created with attributes:

        Nickname: {user.nickname}
        Age: {user.age} years old
        Email: {user.email}
        """
        )

    def create_new_league_season(self) -> None:
        """
        Create a new league season.

        Returns:
            None
        """
        new_league_season_name = input("Enter new league season name: ")
        league_season = LeagueSeason(name=new_league_season_name)  # type: ignore [call-arg]
        self.db_session.add(league_season)
        self.db_session.commit()
        print(
            f"""
        New league season {new_league_season_name} was created."""
        )
