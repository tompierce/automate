"""base classes for triggers"""

class Trigger(object):
    """"base class for triggers"""
    def __init__(self, job_id, trigger_data, logger):
        self.job_id       = job_id
        self.trigger_data = trigger_data
        self.logger       = logger

    def next_run(self):
        """must return a datetime to indicate when it should be run
            see server/constants.py for useful datetime constants
            e.g. DATETIME_NEVER
        """
        raise NotImplementedError
