"""Schema used in Document"""
import marshmallow as ma

from .abstract import BaseSchema
from .i18n import gettext as _
from .expose_missing import ExposeMissing

__all__ = (
    'Schema',
    'RemoveMissingSchema',
)


class RemoveMissingSchema(ma.Schema):
    """
    Custom :class:`marshmallow.Schema` subclass that skips missing fields
    rather than returning None for missing fields when dumping umongo
    :class:`umongo.Document`s.
    """
    def dump(self, *args, **kwargs):
        with ExposeMissing():
            return super().dump(*args, **kwargs)


class Schema(BaseSchema):
    """Schema used in Document"""

    _marshmallow_schemas_cache = {}

    def as_marshmallow_schema(self):
        """Return a pure-marshmallow version of this schema class"""
        # Use a cache to avoid generating several times the same schema
        cache_key = (self.__class__, self.MA_BASE_SCHEMA_CLS)
        if cache_key in self._marshmallow_schemas_cache:
            return self._marshmallow_schemas_cache[cache_key]

        # Create schema if not found in cache
        nmspc = {
            name: field.as_marshmallow_field()
            for name, field in self.fields.items()
        }
        name = 'Marshmallow%s' % type(self).__name__
        m_schema = type(name, (self.MA_BASE_SCHEMA_CLS, ), nmspc)
        # Add i18n support to the schema
        # We can't use I18nErrorDict here because __getitem__ is not called
        # when error_messages is updated with _default_error_messages.
        m_schema._default_error_messages = {
            k: _(v) for k, v in m_schema._default_error_messages.items()}
        self._marshmallow_schemas_cache[cache_key] = m_schema
        return m_schema
