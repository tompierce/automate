class Action():
    def __init__(self, action_data, working_dir):
        self.action_data = action_data
        self.working_dir = working_dir
        pass

    def run(self):
        raise NotImplementedError
