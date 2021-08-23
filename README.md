# yaml-patch

Apply patches to a yaml string, keeping most of the formatting and comments.

Some formatting is not kept due to underlying yaml library limitations:
  - Indentation will be forced to two spaces
  - Spacing before sequence dashes will be forced to two spaces
  - Empty lines at the start of the string will be removed

## As a command line tool

You can pass any number of patches to be applied, they use the following syntax options:

### Patch a single value:
`<field>.<subfield>=<value>`

Example:
```bash
yaml-patch -f test.yml  'spec.replicas=2'
```

### Patch a value inside a single list item:
`<field>.[<position]>.<subfield>=<value>`

Example:
```bash
yaml-patch -f test.yml  'spec.template.containers.[0].image="mycontainer:latest"'
```

### Patch a value inside all list items:
`<field>.[].<subfield>=<value>`

Example:
```bash
yaml-patch -f test.yml 'spec.template.containers.[].image="mycontainer:latest"'
```

## As a Python library

To use `yaml-patch` as a library just import the function and pass patches as dictionary entries.

Example:

```python
from yaml_patch import patch
from textwrap import dedent

def override_list_all_values():
    source_yaml = dedent(
        """\
        some_list:
          - alice
          - bob
        """
    )
    patches = {"some_list.[]": "charlie"}
    expected_yaml = dedent(
        """\
        some_list:
          - charlie
          - charlie
        """
    )
    assert patch(source_yaml, patches) == expected_yaml
```