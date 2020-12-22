# python_module_teardown
Example code to show how to do module-level teardown on error (only).

This was originally written to answer a question on StackOverflow:

https://stackoverflow.com/questions/31432013/pytest-skip-module-teardown

The previous answer posted on StackOverflow and link to documentation was 
helpful but not sufficient for my needs.  I needed a module teardown function 
to execute for each module independently if any test in that module (.py) 
file failed.

To start with, we need a hook to attach the test function result to 
the test node.  This is taken directly from the pytest docs:

```Python
# in conftest.py
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    var_name = "rep_" + rep.when
    setattr(item, var_name, rep)
```
After that, we need *another* hook for the test case to find the module and 
store itself there, so the module can easily find its test cases.  Perhaps 
there's a better way, but I was unable to find one.
```Python
# also in conftest.py
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
```
Once we do that, it's nice to have a decorator function to have the module on 
completion look through its test nodes, find if there are any failures, and 
then if there were call the function associated with the decorator:
```Python
# also also in conftest.py
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
```
Now we have all the necessary framework to work with.  Now, a test file with a failing test case is easy to write:
```Python
from conftest import module_error_teardown


def test_something_that_fails():
    assert False, "Yes, it failed."


def test_something_else_that_fails():
    assert False, "It failed again."


@module_error_teardown
def _this_gets_called_at_the_end_if_any_test_in_this_file_fails():
    print('')
    print("Here's where we would do module-level cleanup!")
```
