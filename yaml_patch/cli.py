import sys

import click


@click.command(
    help="""
Apply patches to a yaml string, keeping most of the formatting and comments.

\b
Some formatting is not kept due to underlying yaml library limitations:
  - Indentation will be forced to two spaces
  - Spacing before sequence dashes will be forced to two spaces
  - Empty lines at the start of the string will be removed

You can pass any number of patches to be applied, they use the following syntax options:

\b
Patch a single value:
  <field>.<subfield>=<value>
Example:
  yaml-patch -f test.yml "spec.replicas=2"

\b
Patch a value inside a single list item:
  <field>.[<position]>.<subfield>=<value>
Example:
  yaml-patch -f test.yml "spec.template.containers.[0].image='mycontainer:latest'"

\b
Patch a value inside all list items:
  <field>.[].<subfield>=<value>
Example:
  yaml-patch -f test.yml "spec.template.containers.[].image='mycontainer:latest'"
""",
)
@click.option(
    "--file", "-f", type=click.File("r"), default=None, help="Path to yaml file being patched. Defaults to stdin."
)
@click.option(
    "--output", "-o", type=click.File("w"), default=None, help="Path to output patched file. Defaults to stdout."
)
@click.option("--in-place", "-i", is_flag=True, help="Replace source file in-place. Overrides --output.")
@click.argument("patches", nargs=-1)
def cli(file, output, in_place, patches):
    # Default i/o to stdin/stdout down here so click.testing has time to capture those streams
    if file is None:
        file = sys.stdin
    if output is None:
        output = sys.stdout

    # Check for bad arguments
    if in_place and file == sys.stdin:
        raise ValueError("Cannot use --in-place with stdin as the source")

    from yaml_patch import patch_yaml

    patched = patch_yaml(yaml_contents=file.read(), patches=patches)

    # # Split each patch into key+value separated by `=`. Use YAML to load the values coming from command line to ensure
    # # they are parsed into yaml syntax equivalents (automatically detect strings, ints, bools, etc).
    # from ruamel.yaml import YAML
    #
    # yaml = YAML()
    # dict_patches = dict()
    # for p in patches:
    #     k, v = p.split("=")
    #     dict_patches[k] = yaml.load(v)
    #
    # # Apply patches
    # from yaml_patch import patch
    #
    # patched = patch(yaml_contents=file.read(), patches=dict_patches)

    # Output results
    if in_place:
        output = open(file.name, "w")
    output.write(patched)


if __name__ == "__main__":
    cli()
