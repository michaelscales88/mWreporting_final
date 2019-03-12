from flask_nav.elements import NavigationItem


class ExtendedNavbar(NavigationItem):
    def __init__(self, title, root_class='navbar navbar-default', items=(), right_items=()):
        self.title = title
        self.root_class = root_class
        self.items = items
        self.right_items = right_items
