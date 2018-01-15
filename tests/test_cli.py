# -*- coding: utf-8 -*-


import subprocess
import sys

import flamegraph.__main__


def noop(*args):
    pass


noop(flamegraph.__main__)  # for 100% coverage


def test_run_as_module():
    output = subprocess.check_output([
        sys.executable,
        '-m', 'flamegraph', '--help'
    ])
    output = output.decode('utf-8')
    assert 'usage' in output


def test_run_as_program():
    output = subprocess.check_output([
        'flamegraph', '--help'
    ])
    output = output.decode('utf-8')
    assert 'usage' in output
