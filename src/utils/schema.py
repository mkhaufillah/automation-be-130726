"""
This module provides a utility class for validating JSON data against a given schema using the `jsonschema` library. It defines a `SchemaValidator` class with a static method `validate_schema` that takes in the data and schema as parameters and performs the validation. If the validation fails, it raises a `ValidationError` with a descriptive message.
"""

from jsonschema import validate
from jsonschema.exceptions import ValidationError


def validate_schema(data, schema) -> str:
    if schema == None or schema == {}:
        return ""  # No schema provided, skip validation
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return f"Response does not match schema: {e}"
    return ""
