"""This module defines a function, get_label_attributes, that retrieves specified attributes from a label in the
Definitions module based on a given key field and value, ensuring attribute validity."""
import Definitions


# ======================================================================================================================
# region -- LABEL ------------------------------------------------------------------------------------------------------
# ======================================================================================================================
def get_label_attributes(key_field, key_value, *attributes):
    """
    This method is used to retrieve attribute values from a label object based on a specified key field and key
    value. It searches for the label with the specified key field and key value * in a list of labels and returns the
    attribute values as a tuple or a single value if only one attribute is specified.
    """
    # Find the label with the specified key_field and key_value
    found_label = next(
        (label for label in Definitions.LABELS if getattr(label, key_field) == key_value),
        None,
    )

    # If no attributes are specified, return an empty tuple
    if not attributes:
        return ()

    # Check if all specified attributes are valid fields in the found_label
    if not all(field in found_label._fields for field in attributes):
        raise ValueError("Invalid field name(s) provided")
    else:
        # Retrieve the values of the specified attributes from the found_label
        return_tuple = tuple(getattr(found_label, attribute) for attribute in attributes)

        # If only one attribute is specified, return the single value instead of a tuple
        if len(return_tuple) == 1:
            return return_tuple[0]
        else:
            return return_tuple

# endregion
# ======================================================================================================================
