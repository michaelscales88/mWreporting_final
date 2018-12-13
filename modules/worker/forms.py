# security/forms.py
from flask_admin.form import fields


class CustomSelectField(fields.Select2Field):
    def pre_validate(self, form):
        # Prevent "not a valid choice" error
        pass

    def process_formdata(self, valuelist):
        value = ''
        if valuelist:
            value = valuelist[0]
        if value:
            self.data = value
