from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session

from src.handler import BaseHandler
from src.components.model import BaseController
from src.database import make_engine, make_session, delete_session
from src.components.routing import main_menu


class Application:
    """
    This is the main application class, it is needed to compose
     different modules and initialize itself. It initializes
     the engine, with which a connection to the database is created,
     а session for connecting to the database, a basic handler that
     processes user requests to access certain screens, a basic
     controller, which is needed to obtain a register of all specific
     controllers contained in the system and by writing to the registry
     of the base controller using the subclass initialization method
    """

    db_engine: Engine
    db_session: Session
    base_handler: BaseHandler
    base_controller: BaseController

    def run(self):
        """
        This is where the application starts. Before this, the connection
         to the database and the routers are initialized

        :return:None
        """
        self.__init_database()
        self.__init_routing()
        self.base_handler.run()

    def stop(self):
        """
        This method is necessary for the correct termination of
         the application, disconnection of the connection with all
         third-party applications

        :return: None
        """
        delete_session(self.db_session)

    def __init_database(self):
        """
        The creation of the database connection engine and the database
         connection session takes place here

        :return: None
        """
        self.db_engine = make_engine({'db_url': 'sqlite:///src/database/db'})
        self.db_session = make_session(self.db_engine)

    def __init_routing(self):
        """
        Initialization of the base controller and initialization of all
         specific controllers occurs to create a list of objects endowed
         with the object of the active session of connecting to the
         database.
        Once the list of these controllers is created, the base handler
         is initialized and passed to the hierarchical menu object and list
         of controllers.

        :return: None
        """
        base_controller = BaseController()
        controllers_registry = [controller(db_session=self.db_session) for controller in base_controller.metadata]
        self.base_handler = BaseHandler(
            controllers_registry=controllers_registry,
            routes=main_menu
        )
