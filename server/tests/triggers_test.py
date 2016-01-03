from server.triggers import *
import json
from datetime import datetime


class TestCronTrigger:

    def test_next_run_returns_datetime(self):
        trigger_data_str = """{
                                "className" : "CronTrigger", 
                                "schedule" : "0 0 0 0 0"
                            }"""
        trigger = CronTrigger(json.loads(trigger_data_str))

        assert type(trigger.next_run()) == datetime


class TestFileExistsTrigger:

    def test_next_run_returns_datetime(self):
        trigger_data_str = """{
                                "className" : "FileExistsTrigger", 
                                "file" : "/tmp/this-file-does-not-exist"
                            }"""
        trigger = FileExistsTrigger(json.loads(trigger_data_str))

        assert type(trigger.next_run()) == datetime