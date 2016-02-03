"""Basic tests for triggers"""
import json
import logging
from datetime import datetime
from server.triggers.CronTrigger import CronTrigger
from server.triggers.FileExistsTrigger import FileExistsTrigger

# pylint: disable=missing-docstring, no-self-use

class TestCronTrigger(object):

    def test_next_run_returns_datetime(self):
        trigger_data_str = """{
                                "className" : "CronTrigger", 
                                "schedule" : "0 0 0 0 0"
                            }"""

        trigger = CronTrigger('test-job', json.loads(trigger_data_str), logging.getLogger())

        assert isinstance(trigger.next_run(), datetime)

class TestFileExistsTrigger(object):

    def test_next_run_returns_datetime(self):
        trigger_data_str = """{
                                "className" : "FileExistsTrigger", 
                                "file" : "/tmp/this-file-does-not-exist"
                            }"""
        trigger = FileExistsTrigger('test-job', json.loads(trigger_data_str), logging.getLogger())

        assert isinstance(trigger.next_run(), datetime)
