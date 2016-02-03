""""base class for actions"""

class Action(object):
    """"base class for actions"""
    def __init__(self, action_data, working_dir, logger):
        self.action_data = action_data
        self.working_dir = working_dir
        self.logger      = logger

    def run(self):
        """actions must implement this method, it is called when an action must run"""
        raise NotImplementedError
