from flask_admin import Admin

from flask_admin._compat import as_unicode

# For compatibility reasons import MenuLink
from flask_admin.menu import MenuCategory  # noqa: F401


class CustomAdmin(Admin):

    def add_category(self, target_category):
        if target_category:
            cat_text = as_unicode(target_category)

            category = self._menu_categories.get(cat_text)

            # create a new menu category if one does not exist already
            if category is None:
                category = MenuCategory(target_category)
                category.class_name = self.category_icon_classes.get(cat_text)
                self._menu_categories[cat_text] = category

                self._menu.append(category)
