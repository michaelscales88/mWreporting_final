# security/forms.py
from flask_security.utils import hash_password
from wtforms import TextField


class CustomPasswordField(TextField):
    def process_data(self, value):
        self.data = ''  # even if password is already set, don't show hash here
        # or else it will be double-hashed on save
        self.orig_hash = value

    def process_formdata(self, valuelist):
        value = ''
        if valuelist:
            value = valuelist[0]
        if value:
            self.data = hash_password(value)
        else:
            self.data = self.orig_hash
