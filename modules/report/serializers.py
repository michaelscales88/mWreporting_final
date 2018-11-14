# report/serializers.py
from modules.extensions import serializer

from .models import CallTableModel, EventTableModel, SlaReportModel, ClientModel


class ClientModelSchema(serializer.ModelSchema):
    class Meta:
        model = ClientModel


class SlaReportModelSchema(serializer.ModelSchema):
    class Meta:
        model = SlaReportModel


class EventTableModelSchema(serializer.ModelSchema):
    class Meta:
        model = EventTableModel


class CallTableModelSchema(serializer.ModelSchema):
    class Meta:
        model = CallTableModel
