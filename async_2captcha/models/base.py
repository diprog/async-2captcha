from pydantic import BaseModel, ConfigDict

def to_camel(s: str) -> str:
    """
    Convert a snake_case string to camelCase.
    Example: "some_field_name" -> "someFieldName"
    """
    parts = s.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class CamelCaseModel(BaseModel):
    """
    Base model for 2captcha API objects using Pydantic v2.

    Fields should be defined in snake_case within the model,
    but can be populated with camelCase keys when creating instances.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )
