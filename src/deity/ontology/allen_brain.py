#!/usr/bin/env python3
"""allen_brain.py in src/deity/ontology."""

from typing import Any
from typing import Dict
from typing import List

import pandas as pd


def flatten_ontology_tree(
    node: Dict[str, Any],
    parent_id: int = None,
    flattened_list: List[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Recursively flattens a nested dictionary (ontology tree) into a list of dictionaries,
    suitable for conversion into a Pandas DataFrame.

    Args:
        node (Dict[str, Any]): The current node in the ontology tree.
        parent_id (int, optional): The ID of the parent node, if any. Defaults to None.
        flattened_list (List[Dict[str, Any]], optional): Accumulator for flattened nodes.
            Defaults to None.

    Returns:
        List[Dict[str, Any]]: A list of flattened node dictionaries.
    """
    if flattened_list is None:
        flattened_list = []

    # Extract the current node's properties, adding the parent ID
    node_data = {key: value for key, value in node.items() if key != "children"}
    node_data["parent_id"] = parent_id  # Track parent ID

    # Add the current node to the flattened list
    flattened_list.append(node_data)

    # Recursively process children
    children = node.get("children", [])
    if isinstance(children, list):  # When children is a list
        for child in children:
            flatten_ontology_tree(child, node_data["id"], flattened_list)
    elif isinstance(children, dict):  # When children is a dict (single child)
        flatten_ontology_tree(children, node_data["id"], flattened_list)

    return flattened_list


def ontology_to_dataframe(nested_dict: Dict[str, Any]) -> pd.DataFrame:
    """
    Converts a nested ontology dictionary into a Pandas DataFrame.

    Args:
        nested_dict (Dict[str, Any]): The nested dictionary representing the ontology tree.

    Returns:
        pd.DataFrame: A DataFrame where each row is a node in the ontology tree.
    """
    flattened_nodes = []

    # Process each top-level key
    for root_key, root_node in nested_dict.items():
        flattened_nodes.extend(flatten_ontology_tree(root_node))

    # Create and return a DataFrame from the flattened list
    return pd.DataFrame(flattened_nodes)