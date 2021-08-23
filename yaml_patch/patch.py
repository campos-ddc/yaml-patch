from __future__ import annotations

import io
from typing import Union

from ruamel.yaml import YAML


def patch(yaml_contents: str, patches: dict[str:object]) -> str:
    """
    Applies patches to a yaml string, keeping most of the formatting and comments.

    Some formatting is not kept due to ruamel.yaml limitations:
      - Indentation will be forced to two spaces
      - Spacing before sequence dashes will be forced to two spaces
      - Empty lines at the start of the string will be removed

    :param yaml_contents:
        A yaml string

    :param patches:
        A dictionary with patches to be applied to `yaml_contents`.

        Each dictionary key points to a path that will be overridden with the dictionary value, there is a special
        syntax for overriding some or all list items.

        Examples:
            # Override a single value at yaml root
            patches = {"root": "new_value"}

            # Override a single value in a subpath
            patches = {"root.sub_item": "new_value"}

            # Override a single value at a list position
            patches = {"root.my_list.[0]": "new_value"}

            # Override all values in a list
            patches = {"root.my_list.[]": "new_value"}

        See test_patch.py for more examples.
    :return:
        The patched yaml contents
    """
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent = 2
    yaml.sequence_dash_offset = 2

    # Parse yaml using ruamel to preserve most of the original formatting/comments
    parsed = yaml.load(yaml_contents)

    for patch_path, patch_value in patches.items():
        _apply_patch(parsed, patch_path, patch_value)

    # ruamel.yaml only lets us dump to a stream, so we have to do the StringIO dance
    output = io.StringIO()
    yaml.dump(parsed, output)
    return output.getvalue()


def _apply_patch(data: Union[dict, list], path: str, patch_value: object):
    """
    Apply a single patch to a path. This will recurse deeper into the path if necessary.
    """
    # If this is the final path segment, apply the patch
    if "." not in path:
        _apply_patch_to_value(data, path, patch_value)
        return

    # If this is the not final path segment, recurse
    _apply_patch_to_subpath(data, path, patch_value)
    return


def _apply_patch_to_value(data: Union[dict, list], path: str, patch_value: object):
    """
    Apply a single patch to a final path.
    """
    # Patch all list items
    if path == "[]":
        for position in range(len(data)):
            data[position] = patch_value
        return

    # Patch single list item
    if path.startswith("[") and path.endswith("]"):
        position = int(path[1:-1])
        data[position] = patch_value
        return

    # Patch value
    data[path] = patch_value
    return


def _apply_patch_to_subpath(data: Union[dict, list], path: str, patch_value: object):
    """
    Apply a single patch to a non-final path. This will recurse deeper into the path
    """
    path, subpath = path.split(".", 1)

    # Recurse on all list items
    if path == "[]":
        for position in range(len(data)):
            _apply_patch(data[position], subpath, patch_value)
        return

    # Recurse on single list item
    if path.startswith("[") and path.endswith("]"):
        position = int(path[1:-1])
        _apply_patch(data[position], subpath, patch_value)
        return

    # Recurse on object
    return _apply_patch(data[path], subpath, patch_value)
