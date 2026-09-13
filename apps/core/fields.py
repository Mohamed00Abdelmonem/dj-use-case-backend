from rest_framework import serializers

class SafeManyRelatedField(serializers.ManyRelatedField):
    def to_internal_value(self, data):
        res = super().to_internal_value(data)
        return [x for x in res if x is not None]


class SafePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        if (data == '' or data is None) and self.allow_null:
            return None
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError:
            if self.allow_null:
                return None
            return None

    @classmethod
    def many_init(cls, *args, **kwargs):
        list_kwargs = {'child_relation': cls(*args, **kwargs)}
        for key in serializers.LIST_SERIALIZER_KWARGS:
            if key in kwargs:
                list_kwargs[key] = kwargs[key]
        return SafeManyRelatedField(**list_kwargs)
