import subprocess, os, logging, shutil
from base_action import Action
import constants as const


class ExecuteScriptAction(Action):
    def run(self):
        scriptFile = self.action_data['scriptFile']

        if not os.path.isabs(scriptFile):
            scriptFile = os.path.join(self.working_dir, scriptFile)

        process = subprocess.Popen(scriptFile, cwd=self.working_dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        out, err = process.communicate()

        if out:
            self.logger.debug(self.action_data['scriptFile'] + ': ' + out)
        if err:
            self.logger.debug(self.action_data['scriptFile'] + ': ' + err)

        self.logger.debug('Completed Successfully' if process.returncode is 0 else 'Failed')

        return (const.SUCCESS if process.returncode is 0 else const.FAILED)
