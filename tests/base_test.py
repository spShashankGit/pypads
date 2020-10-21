import atexit
import logging
import os
import unittest
from os.path import expanduser

from pypads.app import base
from pypads.app.pypads import logger

# Disable all setup functions
base.DEFAULT_SETUP_FNS = {}

# Default test config
config = {
    "recursion_identity": False,
    "recursion_depth": -1,
    "mongo_db" : False}

if "loguru" in str(logger):
    import pytest


    @pytest.fixture
    def caplog(_caplog):
        class PropogateHandler(logging.Handler):
            def emit(self, record):
                logging.getLogger(record.name).handle(record)

        from loguru import logger
        from pypads.pads_loguru import logger_manager
        handler_id = logger_manager.add(PropogateHandler(), format="{message}")
        yield _caplog
        logger_manager.remove(handler_id)

TEST_FOLDER = os.path.join(expanduser("~"), ".pypads-test_" + str(os.getpid()))


# TODO Is sometimes not run?
@atexit.register
def cleanup():
    import shutil
    if os.path.isdir(TEST_FOLDER):
        shutil.rmtree(TEST_FOLDER)

def mac_os_disabled(f):
    """
    Function to disable a tests when mac os is used
    :param f:
    :return:
    """
    from sys import platform
    if platform == "darwin":
        def disabled(self):
            print(f.__name__ + ' has been disabled on mac osx')

        return disabled
    else:
        return f


class BaseTest(unittest.TestCase):

    def setUp(self) -> None:
        if not os.path.isdir(TEST_FOLDER):
            os.mkdir(TEST_FOLDER)

    def tearDown(self):
        # TODO isn't run on unexpected errors
        from pypads.app.pypads import current_pads, set_current_pads
        if current_pads:
            current_pads.deactivate_tracking(run_atexits=True, reload_modules=False)
            # noinspection PyTypeChecker
            set_current_pads(None)
        cleanup()

