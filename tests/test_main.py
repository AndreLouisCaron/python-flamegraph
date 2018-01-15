# -*- coding: utf-8 -*-


import mock
import os.path
import pytest
import uuid

from flamegraph.flamegraph import main

__here__ = os.path.dirname(os.path.abspath(__file__))


def test_main_fail_on_invalid_command(capsys):
    argv = [
        'flamegraph',
    ]
    with mock.patch('sys.argv', argv):
        with pytest.raises(SystemExit) as exc:
            print(main())
        assert exc.value.args[0] == 2
    output, errors = capsys.readouterr()
    assert output == ''
    assert 'usage' in errors


def test_main_fail_on_missing_script_file(capsys):
    argv = [
        'flamegraph',
        str(uuid.uuid4()) + '.py',
    ]
    with mock.patch('sys.argv', argv):
        with pytest.raises(SystemExit) as exc:
            print(main())
        assert exc.value.args[0] == 2
    output, errors = capsys.readouterr()
    assert 'Script file does not exist' in errors
    assert 'usage' in errors


def test_main(capsys):
    argv = [
        'flamegraph',
        '-i', str(0.01),
        os.path.join(__here__, 'hello.py'),
    ]
    with mock.patch('sys.argv', argv):
        main()

    output, errors = capsys.readouterr()

    # Standard output contains script output.
    assert 'Hello, world!' in output

    # Standard output contains stats.
    assert 'Elapsed Time:' in output

    # Standard error contains frames.
    lines = errors.split('\n')
    lines = [line for line in lines if line]
    assert len(lines) >= 1
