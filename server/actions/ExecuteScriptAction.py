"""Action for executing arbitrary scripts"""
import os
import subprocess
from server.actions.base_action import Action
import server.constants as const


class ExecuteScriptAction(Action):
    """Executes a script using Popen, logs the output and reports SUCCESS/FAILURE"""
    def run(self):
        script_file = self.action_data['scriptFile']

        if not os.path.isabs(script_file):
            script_file = os.path.join(self.working_dir, script_file)

        process = subprocess.Popen(script_file,
                                   cwd=self.working_dir,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        out, err = process.communicate()

        if out:
            self.logger.info(script_file + ': ' + out)
        if err:
            self.logger.info(script_file + ': ' + err)

        self.logger.debug('Completed Successfully' if process.returncode is 0 else 'Failed')

        return const.SUCCESS if process.returncode is 0 else const.FAILURE
