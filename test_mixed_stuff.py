from conftest import module_error_teardown


@module_error_teardown
def _module_error_teardown():
    print('')
    print("A test case failed in test_mixed_stuff.py!")


def test_success_in_mixed():
    pass


def test_fail_in_mixed():
    assert False, "Yes, it failed."


def test_another_success_in_mixed():
    pass


def test_another_fail_in_mixed():
    assert False, "It failed again."


def test_one_more_success_in_mixed():
    pass
