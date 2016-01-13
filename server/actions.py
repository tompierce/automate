import subprocess, os, logging, shutil
import constants as const

class Action():
    def __init__(self, action_data, working_dir):
        self.action_data = action_data
        self.working_dir = working_dir
        pass

    def run(self):
        raise NotImplementedError

class DeleteWorkspaceAction(Action):
    def run(self):
        logging.debug('deleting workspace: ' + self.working_dir)
        try:
            shutil.rmtree(self.working_dir)
        except:
            pass
        os.mkdir(self.working_dir)    

class ExecuteScriptAction(Action):
    def run(self):
        scriptFile = self.action_data['scriptFile']

        if not os.path.isabs(scriptFile):
            scriptFile = os.path.join(self.working_dir, scriptFile)

        process = subprocess.Popen(scriptFile, cwd=self.working_dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        out, err = process.communicate()

        if out:
            logging.debug(self.action_data['scriptFile'] + ': ' + out)
        if err:
            logging.debug(self.action_data['scriptFile'] + ': ' + err)

        logging.debug('Completed Successfully' if process.returncode is 0 else 'Failed')

        return (const.SUCCESS if process.returncode is 0 else const.FAILED)

