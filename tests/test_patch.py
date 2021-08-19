from textwrap import dedent

from yaml_patch import patch


def check(obtained, expected):
    assert obtained == expected, f"Obtained:\n--\n{obtained}--\n but was expecting:\n--\n{expected}--\n"


def test_empty_patch():
    yaml = dedent(
        """\
        root:
          some_key: "some_value"
          other_key: 5

          # A comment
          a_list:
            - alice
            - bob

          # Another comment
          a_list_of_objects:
            - name: alice
            - name: bob

          an_object:
            sub_key: sub_value
        """
    )
    check(patch(yaml, dict()), yaml)


def test_override_string_value():
    source_yaml = dedent(
        """\
        some_key: some_value
        """
    )
    patches = {"some_key": "new_value"}
    expected_yaml = dedent(
        """\
        some_key: new_value
        """
    )
    check(patch(source_yaml, patches), expected_yaml)


def test_override_int_value():
    source_yaml = dedent(
        """\
        some_key: 1
        """
    )
    patches = {"some_key": 2}
    expected_yaml = dedent(
        """\
        some_key: 2
        """
    )
    check(patch(source_yaml, patches), expected_yaml)


def test_override_object():
    source_yaml = dedent(
        """\
        some_dict:
          some_key: some_value
        """
    )
    patches = {"some_dict.some_key": "new_value"}
    expected_yaml = dedent(
        """\
        some_dict:
          some_key: new_value
        """
    )

    check(patch(source_yaml, patches), expected_yaml)


def test_override_list():
    source_yaml = dedent(
        """\
        some_list:
          - alice
          - bob
        """
    )
    patches = {"some_list.[0]": "charlie"}
    expected_yaml = dedent(
        """\
        some_list:
          - charlie
          - bob
        """
    )
    check(patch(source_yaml, patches), expected_yaml)


def test_override_list_all_values():
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
    check(patch(source_yaml, patches), expected_yaml)


def test_override_object_within_a_list():
    source_yaml = dedent(
        """\
        some_list:
          - some_key: some_value
        """
    )
    patches = {"some_list.[0].some_key": "new_value"}
    expected_yaml = dedent(
        """\
        some_list:
          - some_key: new_value
        """
    )
    check(patch(source_yaml, patches), expected_yaml)
