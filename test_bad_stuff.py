from conftest import module_error_teardown


@module_error_teardown
def _module_error_teardown():
    print('')
    print("A test case failed in test_bad_stuff.py!")


def test_fail_in_bad():
    assert False, "Yes, it failed."


def test_another_fail_in_bad():
    assert False, "It failed again."
