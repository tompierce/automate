from logging import log
import subprocess, os

class Action():
    def __init__(self, action_data, working_dir):
        self.action_data = action_data
        self.working_dir = working_dir
        pass

    def run(self):
        raise NotImplementedError

class ExecuteScriptAction(Action):
    def run(self):
        scriptFile = self.action_data['scriptFile']

        if not os.path.isabs(scriptFile):
            scriptFile = os.path.join(self.working_dir, scriptFile)

        process = subprocess.Popen(scriptFile, cwd=self.working_dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        out, err = process.communicate()

        if out:
            log(out, prefix=self.action_data['scriptFile'])
        if err:
            log(err, prefix=self.action_data['scriptFile'])
