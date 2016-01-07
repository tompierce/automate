import os, threading, signal, time, logging, json
from flask import Flask, jsonify, abort
from jobs import JobManager

PORT = 8000
SERVER_ROOT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')

def main():

    logging.getLogger().setLevel(logging.DEBUG)

    logging.debug('Starting server as ' + __name__ )
           
    http_server = Flask(__name__)
    http_server.debug = True

    @http_server.errorhandler(404)
    def not_found(error):
        response = jsonify({'code': 404,'message': 'Not found'})
        response.status_code = 404
        return response

    @http_server.route('/')
    def index():
        return "Server is running..."

    @http_server.route('/jobs')
    def list_jobs():
        return jsonify(job_list=job_manager.get_jobs_list())

    @http_server.route('/job/<job_id>', methods=['POST'])
    def start_job(job_id):
        if not job_manager.request_run(job_id):
            abort(404)
        return jsonify(status='success', job_id=job_id)

    job_manager = JobManager(os.path.join(SERVER_ROOT_DIR, 'jobs'))
    job_manager_thread = threading.Thread(target=job_manager.start)
    job_manager_thread.start()

    http_server.run(use_reloader = False)
    
    job_manager.stop()
    job_manager_thread.join()
        
if __name__ == "__main__":
    logging.warning('In main.')
    main()
