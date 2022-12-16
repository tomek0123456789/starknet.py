import warnings
from typing import Generator

from starkware.crypto.signature.signature import FIELD_PRIME

from starknet_py.cairo.felt import encode_shortstring, is_in_felt_range

from starknet_py.cairo.serialization._context import (
    SerializationContext,
    DeserializationContext,
    Context,
)
from starknet_py.cairo.serialization.data_serializers.cairo_data_serializer import (
    CairoDataSerializer,
)


class FeltSerializer(CairoDataSerializer[int, int]):
    """
    Serializer for field element. At the time of writing it is the only existing numeric type.
    """

    def deserialize_with_context(self, context: DeserializationContext) -> int:
        [val] = context.reader.read(1)
        self._ensure_felt(context, val)
        return val

    def serialize_with_context(
        self, context: SerializationContext, value: int
    ) -> Generator[int, None, None]:
        if isinstance(value, str):
            warnings.warn(
                "Serializing shortstrings in FeltSerializer is deprecated. "
                "Use starknet_py.cairo.felt.encode_shortstring instead.",
                category=DeprecationWarning,
            )
            value = encode_shortstring(value)
            yield value
            return

        context.ensure_valid_type(value, isinstance(value, int), "int")
        self._ensure_felt(context, value)
        yield value

    @staticmethod
    def _ensure_felt(context: Context, value: int):
        context.ensure_valid_value(
            value, is_in_felt_range(value), f"must be in [0, {FIELD_PRIME}) range"
        )
