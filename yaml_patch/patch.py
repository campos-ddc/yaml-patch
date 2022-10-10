from __future__ import annotations

import io
from typing import Union, Sequence, NamedTuple

from ruamel.yaml import YAML


def patch_yaml(yaml_contents: str, patches: Sequence[str]) -> str:
    """
    Applies patches to a yaml string, keeping most of the formatting and comments.

    Some formatting is not kept due to ruamel.yaml limitations:
      - Indentation will be forced to two spaces
      - Spacing before sequence dashes will be forced to two spaces
      - Empty lines at the start of the string will be removed

    :param yaml_contents:
        A yaml string

    :param patches:
        A list of patches to be applied to `yaml_contents`.

        Each item points is an expression of `{path}{action}{value}` where {path} refers to a path in `yaml_contents`,
        {action} is one of `=` (override) or `+=` (append) and {value} is the value being applied (in raw format).

        Examples:
            # Override a single value at yaml root
            patches = ["root='new_value'"]

            # Override a single value in a subpath
            patches = ["root.sub_item='new_value'"]

            # Override a single value at a list position
            patches = ["root.my_list.[0]='new_value'"]

            # Override all values in a list
            patches = ["root.my_list.[]='new_value'"]

            # Increment a single value at yaml root
            patches = ["root+='new_value'"]

            # Append an item to a list
            patches = ["root.my_list+=['new_value']"]

        See test_patch.py for more examples.
    :return:
        The patched yaml contents
    """
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent = 2
    yaml.sequence_dash_offset = 2

    # Parse yaml using ruamel.yaml to preserve most of the original formatting/comments
    parsed = yaml.load(yaml_contents)

    # Split each patch into key+value separated by an action Use YAML to load the values coming from command line to
    # ensure they are parsed into yaml syntax equivalents (automatically detect strings, ints, bools, etc).
    yamlparser = YAML()
    for p in patches:
        if "+=" in p:
            path, value = p.split("+=")
            action = _patch._action_append
        else:
            path, value = p.split("=")
            action = _patch._action_set

        _apply_patch(parsed, path, action, yamlparser.load(value))

    # ruamel.yaml only lets us dump to a stream, so we have to do the StringIO dance
    output = io.StringIO()
    yaml.dump(parsed, output)
    return output.getvalue()


def patch(yaml_contents: str, patches: dict[str:object]) -> str:
    """
    Deprecated.

    Calls patch.yaml using `=` as the action to apply on all patches.
    """
    return patch_yaml(yaml_contents, [path + "=" + repr(value) for path, value in patches.items()])


class _patch(NamedTuple):
    path: str
    action: callable
    value: object

    @staticmethod
    def _action_set(data, path, value):
        data[path] = value

    @staticmethod
    def _action_append(data, path, value):
        data[path] = data[path] + value  # Use `+` instead of `+=` because they are not the same in ruamel.yaml types


def _apply_patch(data: Union[dict, list], path: str, action: callable, patch_value: object):
    """
    Apply a single patch to a path. This will recurse deeper into the path if necessary.
    """
    # If this is the final path segment, apply the patch
    if "." not in path:
        _apply_patch_to_value(data, path, action, patch_value)
        return

    # If this is the not final path segment, recurse
    _apply_patch_to_subpath(data, path, action, patch_value)
    return


def _apply_patch_to_value(data: Union[dict, list], path: str, action: callable, patch_value: object):
    """
    Apply a single patch to a final path.
    """
    # Patch all list items
    if path == "[]":
        for position in range(len(data)):
            action(data, position, patch_value)
            # data[position] = patch_value
        return

    # Patch single list item
    if path.startswith("[") and path.endswith("]"):
        position = int(path[1:-1])
        action(data, position, patch_value)
        # data[position] = patch_value
        return

    # Patch value
    action(data, path, patch_value)
    return


def _apply_patch_to_subpath(data: Union[dict, list], path: str, action: callable, patch_value: object):
    """
    Apply a single patch to a non-final path. This will recurse deeper into the path
    """
    path, subpath = path.split(".", 1)

    # Recurse on all list items
    if path == "[]":
        for position in range(len(data)):
            _apply_patch(data[position], subpath, action, patch_value)
        return

    # Recurse on single list item
    if path.startswith("[") and path.endswith("]"):
        position = int(path[1:-1])
        _apply_patch(data[position], subpath, action, patch_value)
        return

    # Recurse on object
    return _apply_patch(data[path], subpath, action, patch_value)
