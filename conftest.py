# Sample conftest.py file to allow a session fixture to detect test error.
# See https://stackoverflow.com/questions/31432013/pytest-skip-module-teardown
from functools import wraps
import pytest


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    var_name = "rep_" + rep.when
    setattr(item, var_name, rep)


@pytest.fixture(scope="function", autouse=True)
def _testcase_exit(request):
    yield
    parent = request.node.parent
    while not isinstance(parent, pytest.Module):
        parent = parent.parent
    try:
        parent.test_nodes.append(request.node)
    except AttributeError:
        parent.test_nodes = [request.node]


def module_error_teardown(f):
    @wraps(f)
    @pytest.fixture(scope="module", autouse=True)
    def wrapped(request, *args, **kwargs):
        yield
        try:
            test_nodes = request.node.test_nodes
        except AttributeError:
            test_nodes = []

        something_failed = False
        for x in test_nodes:
            try:
                something_failed |= x.rep_setup.failed
                something_failed |= x.rep_call.failed
                something_failed |= x.rep_teardown.failed
            except AttributeError:
                pass
        if something_failed:
            f(*args, **kwargs)
    return wrapped
