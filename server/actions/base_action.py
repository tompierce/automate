class Action():
    def __init__(self, action_data, working_dir, logger):
        self.action_data = action_data
        self.working_dir = working_dir
        self.logger      = logger
        pass

    def run(self):
        raise NotImplementedError
