class ContextSpecificFieldsMixin:
    """
    A mixin to facilitate the addition/replacement of fields based on the
    specific ``instance`` being serialized, and any other context available.
    """
    def to_representation(self, instance):
        fields = self.fields
        self.update_fields(
            fields, instance, getattr(self, '_context', {})
        )
        return super().to_representation(instance)

    def update_fields(self, fields, instance, context):
        pass
