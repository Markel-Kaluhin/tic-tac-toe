from typing import Callable, List, Optional

import click

from src.handler.model import Handler


class BaseHandler:
    """
    Class responsible for creating and initializing the Application Menu.

    Attributes:
        current_handler (Handler): The current handler associated with the application menu.
        routes (Handler): Hierarchical structure of handlers corresponding to the structure of the application menu.

    Methods:
        __init__(self, controllers_registry, routes):
            Initializes a BaseHandler instance.
        run(self, handler_list=None) -> None:
            Initializes the application menu and handles transitions between screens.
        __get_handler_index(self) -> int:
            Gets the ordinal number of the menu item selected by the user.
        __get_executor(self) -> Callable:
            Gets the handler method based on the current handler's component and method.
        __show_menu_labels_or_define_handler(self, handler_list: List[Handler]) -> None:
            Displays menu labels or defines the handler based on the provided list of handlers.
        __choose_menu_rendering_method(self) -> None:
            Chooses the method for processing the request to display the next screen.

    """

    current_handler: Handler
    routes: Handler

    def __init__(self, controllers_registry, routes):
        """
        Initializes a BaseHandler instance.

        Args:
            controllers_registry (Any): Business Objects controller application entities.
            routes (Handler): Hierarchical structure of handlers corresponding to the structure of the application menu.
        """
        self.controllers_registry = controllers_registry
        self.routes = routes
        self.current_handler = self.routes

    def run(self, handler_list: List[Handler] = None) -> None:
        """
        Initializes the application menu and handles transitions between screens.

        Args:
            handler_list (List[Handler]): List of handlers to display on the next screen.
        """
        self.__show_menu_labels_or_define_handler(handler_list)
        menu_item = self.__get_handler_index()
        try:
            click.clear()
            self.current_handler = handler_list[menu_item]
            self.__choose_menu_rendering_method()
        except (IndexError, TypeError):
            print(
                """
        Wrong choice, try again: """
            )
            # print('Debug: ', e)
            if self.current_handler.children:
                self.run(self.current_handler.children)
            else:
                self.run(self.current_handler.parent.children)

    @staticmethod
    def __get_handler_index() -> int:
        """
        Method for getting user decision

        :return: The ordinal number of the menu item selected by
         the user serialized to an integer
        """
        result: Optional[int] = None
        raw_menu_item: str = input()
        if raw_menu_item.isdigit():
            result = int(raw_menu_item)
        return result

    def __get_executor(self) -> Callable:
        """
        This method is required to get a handler. In the first step, we get
         the controller from the registry, initialized controller objects,
         then we get a method of this object and return it to be called

        :return: Method object
        """
        result = next(
            (
                controller
                for controller in self.controllers_registry
                if controller.__class__.__name__ == self.current_handler.component.__name__
            ),
            None,
        )
        if result:
            result = getattr(result, self.current_handler.method)
            if result:
                return result
            raise AttributeError(
                f"Method {self.current_handler.method}  in Component {self.current_handler.component} does not exist"
            )
        raise AttributeError(f"Component {self.current_handler.component} does not exist")

    def __show_menu_labels_or_define_handler(self, handler_list: List[Handler]) -> None:
        """
        Every time we receive a new list of handlers, we need to
         display a list of its child handlers, if they are not there,
         we need to take the parent handler and display its child
         handlers, where the current handler will enter.
        This method needs for all of that

        :param handler_list: List of child handlers of the current handler
        """
        if handler_list and isinstance(handler_list, list):
            for handler in handler_list:
                print(
                    f"""
        {handler.id} | {handler.name}"""
                )
        elif self.current_handler.children:
            self.run(self.current_handler.children)
        else:
            self.run(self.routes.children)

    def __choose_menu_rendering_method(self) -> None:
        """
        The choice of method for processing the request to display
         the next screen is based on various parameters.
        Whether the handler has child handlers or not, whether we received
         dynamic handlers in response to the previous handler.
        The basis of all this is the choice of the request method for the next
         handler.
        """
        response = self.__get_executor()(self.current_handler.parent, **self.current_handler.kwargs)
        if response.dynamic_menu_items:
            self.run(response.dynamic_menu_items)
        elif response.parent:
            self.run(response.parent.children)
        elif self.current_handler.children:
            self.run(self.current_handler.children)
        else:
            self.run(self.current_handler.parent.children)
