from decimal import Decimal, InvalidOperation


def validate_decimal(name: str, value: int | float | Decimal | str, digits: int):
    """
    Validates that the decimal is acceptable, and returns it with the correct number of digits.
    """
    if isinstance(value, str):
        try:
            value = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError(f"{name} must be a valid numeric value, not '{value}'") from exc
    if not isinstance(value, (int, float, Decimal)):
        raise TypeError(f"'{name}' must be a numeric type, not {type(value)}")
    return Decimal(f"{value:.{digits}f}")


def validate_list(name, value, item_type, length):
    """
    Validates that the list is of the correct type, length and content type.
    """
    if not isinstance(value, list):
        raise TypeError(f"'{name}' must be a list, not {type(value)}")
    if len(value) < length:
        raise ValueError(f"'Length of list '{name}' must be {length} or greater, not {len(value)}")
    for index, item in enumerate(value):
        if not isinstance(item, item_type):
            raise TypeError(
                f"Not all items of property {name} were of type {item_type}: "
                f"item at index {index} was of type {type(item)}"
            )
    return value
