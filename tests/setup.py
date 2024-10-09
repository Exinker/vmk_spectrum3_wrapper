import sys

import pytest


@pytest.fixture(autouse=True)
def setup(monkeypatch: pytest.MonkeyPatch):
    print('++ def setup(monkeypatch: pytest.MonkeyPatch):')
    monkeypatch.setattr(sys, 'path', list(['./tests/fakes/', *sys.path]))
