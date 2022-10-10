import io
import textwrap
import traceback

import mock
from click.testing import CliRunner, Result


def test_no_patches():
    """
    Test that we call yaml_patch correctly
    """

    runner = CliRunner()

    with mock.patch("yaml_patch.patch_yaml", return_value="mock_output") as mock_patch:
        from yaml_patch.cli import cli

        result = runner.invoke(cli, input="key: value")

    __assert_result_success(result)
    assert result.stdout == "mock_output"
    mock_patch.assert_called_once_with(yaml_contents="key: value", patches=tuple())


def test_patches():
    """
    Test that patch arguments from CLI are forwarded correctly
    """
    runner = CliRunner()

    cli_patches = (
        "key='new value'",
        "key.subkey='new subvalue'",
        "key.list.[0]='value in list'",
        "key.subint=5",
        "key.subbool=true",
    )

    with mock.patch("yaml_patch.patch_yaml", return_value="mock_output") as mock_patch:
        from yaml_patch.cli import cli

        result = runner.invoke(cli, cli_patches, input="key: value")

    __assert_result_success(result)
    assert result.stdout == "mock_output"
    mock_patch.assert_called_once_with(yaml_contents="key: value", patches=cli_patches)


def test_patch_file_input(tmp_path):
    """
    Test that we can patch a file other than stdin and still output to stdout
    """
    tmp_yaml = tmp_path / "test.yml"
    tmp_yaml.write_text("key: 'value in file'")

    runner = CliRunner()

    with mock.patch("yaml_patch.patch_yaml", return_value="mock_output") as mock_patch:
        from yaml_patch.cli import cli

        result = runner.invoke(cli, [f"--file={tmp_yaml}"])

    __assert_result_success(result)
    assert result.stdout == "mock_output"
    mock_patch.assert_called_once_with(yaml_contents="key: 'value in file'", patches=tuple())


def test_patch_file_output(tmp_path):
    """
    Test that we can patch stdin and output to a file
    """
    tmp_yaml = tmp_path / "test.yml"
    # tmp_yaml.write_text("key: 'value in file'")

    runner = CliRunner()

    with mock.patch("yaml_patch.patch_yaml", return_value="mock_output") as mock_patch:
        from yaml_patch.cli import cli

        result = runner.invoke(cli, [f"--output={tmp_yaml}"], input="key: value")

    __assert_result_success(result)
    assert result.stdout == ""  # stdout is empty because we output to a file
    assert tmp_yaml.read_text() == "mock_output"
    mock_patch.assert_called_once_with(yaml_contents="key: value", patches=tuple())


def test_patch_file_input_and_output(tmp_path):
    """
    Test that we can patch from file into another file
    """
    input_yaml = tmp_path / "input.yml"
    input_yaml.write_text("key: 'value in file'")
    output_yaml = tmp_path / "output.yml"

    runner = CliRunner()

    with mock.patch("yaml_patch.patch_yaml", return_value="mock_output") as mock_patch:
        from yaml_patch.cli import cli

        result = runner.invoke(cli, [f"--file={input_yaml}", f"--output={output_yaml}"], input="key: value")

    __assert_result_success(result)
    assert result.stdout == ""  # stdout is empty because we output to a file
    assert output_yaml.read_text() == "mock_output"
    mock_patch.assert_called_once_with(yaml_contents="key: 'value in file'", patches=tuple())


def test_patch_file_same_input_and_output(tmp_path):
    """
    Test that we can patch from file into the same file
    """
    tmp_yaml = tmp_path / "input.yml"
    tmp_yaml.write_text("key: 'value in file'")

    runner = CliRunner()

    with mock.patch("yaml_patch.patch_yaml", return_value="mock_output") as mock_patch:
        from yaml_patch.cli import cli

        result = runner.invoke(cli, [f"--file={tmp_yaml}", f"--output={tmp_yaml}"], input="key: value")

    __assert_result_success(result)
    assert result.stdout == ""  # stdout is empty because we output to a file
    assert tmp_yaml.read_text() == "mock_output"
    mock_patch.assert_called_once_with(yaml_contents="key: 'value in file'", patches=tuple())


def test_inplace(tmp_path):
    """
    Test that we can patch from file into the same file using --in-place
    """
    tmp_yaml = tmp_path / "input.yml"
    tmp_yaml.write_text("key: 'value in file'")

    runner = CliRunner()

    with mock.patch("yaml_patch.patch_yaml", return_value="mock_output") as mock_patch:
        from yaml_patch.cli import cli

        result = runner.invoke(cli, [f"--file={tmp_yaml}", "--in-place"], input="key: value")

    __assert_result_success(result)
    assert result.stdout == ""  # stdout is empty because we output to a file
    assert tmp_yaml.read_text() == "mock_output"
    mock_patch.assert_called_once_with(yaml_contents="key: 'value in file'", patches=tuple())


def test_cant_use_inplace_with_stdin(tmp_path):
    """
    Test that we get an error if trying to use --in-place with stdin as input
    """
    tmp_yaml = tmp_path / "input.yml"
    tmp_yaml.write_text("key: 'value in file'")

    runner = CliRunner()

    with mock.patch("yaml_patch.patch_yaml", return_value="mock_output") as mock_patch:
        from yaml_patch.cli import cli

        result = runner.invoke(cli, ["--in-place"], input="key: value")

    assert result.exit_code == 1, __result_str(result)
    assert str(result.exception) == str(ValueError("Cannot use --in-place with stdin as the source")), __result_str(
        result
    )
    mock_patch.assert_not_called()


def __assert_result_success(result):
    assert result.exception is None and result.exit_code == 0, __result_str(result)


def __result_str(result: Result):
    as_str = f"\nexit_code: {result.exit_code}\n"

    if result.exception is not None:
        buf = io.StringIO()
        traceback.print_tb(result.exc_info[2], file=buf)

        as_str += f"exception: {result.exception}\n"
        as_str += f"traceback:\n{textwrap.indent( buf.getvalue(), prefix='    ')}\n"

    as_str += f"stdout:\n{textwrap.indent(result.stdout, prefix='    ')}\n"

    return as_str
