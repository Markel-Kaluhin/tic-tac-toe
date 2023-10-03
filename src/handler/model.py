from dataclasses import dataclass, field
from typing import Any, List, Optional, Type

from src.components.model import BaseController


@dataclass
class HandlerResponse:
    """
    Data model of a system entity - HandlerResponse.

    Attributes:
        kwargs (Any): Additional data to be passed along with the response.
        parent (Optional[Handler]): The parent handler associated with this response.
        dynamic_menu_items (List[Handler]): List of dynamic menu items for creating dynamic handlers.

    Notes:
        HandlerResponse is a required attribute for any handler. The return from the handler
        must be processed by an object of this class.
    """

    kwargs: Any = field(init=False)

    parent: Optional["Handler"] = field(default=None)
    dynamic_menu_items: List["Handler"] = field(default_factory=list)


@dataclass
class Handler:
    """
    Data model of a system entity - Handler.

    Attributes:
        name (str): Name of the handler.
        parent (Handler): The parent handler associated with this handler.
        component (TController): Type of component associated with this handler.
        method (str): Name of the method associated with this handler.
        kwargs (Any): Additional named arguments to pass specific data when calling the next handler.
        id (int): Identifier for the handler.
        children (List[Handler]): List of child handlers associated with this handler.

    Notes:
        Handler is a required part of the system structure and has a link to a parent and a list of its own children.
        This structure is static, created during initialization and does not change.
        It also contains the id and its own name for the association in the router with an item from the menu list,
        as well as the name of the component and the name of the method to retrieve the method object from the registry
        initialized components.
    """

    name: str = field(repr=True)
    parent: "Handler" = field(init=False, repr=True)
    component: Type[BaseController] = field()
    method: str = field()
    kwargs: Any = field(default_factory=dict)

    id: int = field(default=0)  # pylint: disable=invalid-name
    children: List["Handler"] = field(default_factory=list)

    def add_children(self, item: "Handler") -> None:
        """
        Add a child handler to this handler.

        Args:
            item (Handler): The handler to be added as a child.
        """
        item.id = len(self.children)
        item.parent = self
        self.children.append(item)
