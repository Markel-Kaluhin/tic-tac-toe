from typing import List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class HandlerResponse:
    """
    Data model of system entity - HandlerResponse.
    Required attribute for any handler. The return from the handler
     must be processed by an object of this class
    dynamic_menu_items - are needed to create dynamic handlers, which will be
     shown as a list on the next screen.
    parent - is the current handler from which the response is generated.
    But you can set any parent.
    kwargs - needed to pass specific data from the current one to
     the called handler. For example, to pass user IDs from a list of users
     to a handler, and then a controller and service of user details screen.
    """
    kwargs: Any = field(init=False)

    parent: Optional['Handler'] = field(default=None)
    dynamic_menu_items: List['Handler'] = field(default_factory=list)


@dataclass
class Handler:
    """
    Data model of system entity - Handler.
    Has a link to a parent and a list of its own children.
    Yes, I know that circular references are bad, but this whole structure
     is static, created during initialization and does not change anymore.
    Things like dynamic handlers are removed after they are used and cleared
     from memory.
    It also contains the id and its own name for the association in the
     router with an item from the menu list, as well as the name
     of the component and the name of the method, to take the method object
     from the registry, initialized components, it also has a list of named
     arguments to pass specific data when calling the next handler
    """
    name: str = field(repr=True)
    parent: 'Handler' = field(init=False, repr=True)
    component: str = field()
    method: str = field()
    kwargs: Any = field(default_factory=dict)

    id: int = field(default=0)
    children: List['Handler'] = field(default_factory=list)

    def add_children(self, item: 'Handler'):
        item.id = len(self.children)
        item.parent = self
        self.children.append(item)
