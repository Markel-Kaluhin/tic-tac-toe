from src.handler import HandlerResponse
from src.components.model import BaseController

from src.components.utility.service import UtilityService


class Utility(BaseController):

    def __init__(self, db_session):
        self.db_session = db_session
        self.service = UtilityService()

    @staticmethod
    def previous_menu_item(handler, **kwargs):
        """
        Returns the previous menu item

        :return HandlerResponse object where stored the data to run the next
            handlers or generated dynamic handlers
        """
        result = HandlerResponse()
        result.parent = handler.parent
        return result
