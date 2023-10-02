from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session

from src.components.model import BaseController
from src.components.routing import main_menu
from src.database import delete_session, make_engine, make_session
from src.handler.base import BaseHandler


class Application:
    """
    The main application class that composes different modules and initializes itself.

    Attributes:
        db_engine (Engine): The SQLAlchemy engine for database connection.
        db_session (Session): The SQLAlchemy session for database operations.
        base_handler (BaseHandler): The base handler to process user requests for accessing screens.
        base_controller (BaseController): The base controller for obtaining a register of all specific controllers
         in the system.

    Methods:
        run(self):
            Starts the application by initializing the database connection and routing.
        stop(self):
            Stops the application and disconnects from external applications.
        __init_database(self):
            Initializes the database connection engine and the database connection session.
        __init_routing(self):
            Initializes the base controller and specific controllers to create a list of objects with an active
             database session.
    """

    db_engine: Engine
    db_session: Session
    base_handler: BaseHandler
    base_controller: BaseController

    def run(self) -> None:
        """
        Starts the application. Initializes the database connection and the routing.

        Returns:
            None
        """
        self.__init_database()
        self.__init_routing()
        self.base_handler.run()

    def stop(self) -> None:
        """
        Stops the application, disconnecting from external applications.

        Returns:
            None
        """
        delete_session(self.db_session)

    def __init_database(self) -> None:
        """
        Initializes the database connection engine and the database connection session.

        Returns:
            None
        """
        self.db_engine = make_engine({"db_url": "sqlite:///src/database/db"})
        self.db_session = make_session(self.db_engine)

    def __init_routing(self) -> None:
        """
        Initializes the base controller and specific controllers to create a list of objects with an active database
         session.
        Once the list of these controllers is created, the base handler is initialized and passed to the hierarchical
         menu object and list of controllers.

        Returns:
            None
        """
        base_controller = BaseController()
        controllers_registry = [controller(db_session=self.db_session) for controller in base_controller.metadata]
        self.base_handler = BaseHandler(controllers_registry=controllers_registry, routes=main_menu)
