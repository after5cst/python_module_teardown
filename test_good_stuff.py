from conftest import module_error_teardown


@module_error_teardown
def _module_error_teardown():
    print('')
    print("A test case failed in test_good_stuff.py!")


def test_success_in_good():
    pass


def test_another_success_in_good():
    pass
