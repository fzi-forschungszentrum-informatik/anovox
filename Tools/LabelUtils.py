"""
This module have some utility functions for labeling
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Definitions import LABELS


def get_label_attributes(key_field, key_value, *attributes):
    # Find the label with the specified key field and value
    found_label = next((label for label in LABELS if getattr(label, key_field) == key_value), None)

    # If no attributes provided, return an empty tuple
    if not attributes:
        return ()

    # Validate if provided attributes are valid field names
    if not all(field in found_label._fields for field in attributes):
        raise ValueError("Invalid field name(s) provided")
    else:
        # Extract attributes from the found label
        return_tuple = tuple(getattr(found_label, attribute) for attribute in attributes)

        # If only one attribute is requested, return it directly instead of a tuple
        if len(return_tuple) == 1:
            return return_tuple[0]
        else:
            return return_tuple
