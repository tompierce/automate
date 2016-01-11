from flask import Flask, jsonify, abort

class HTTP_Server(Flask):
    def __init__(self, import_name):
        Flask.__init__(self, import_name)

    def set_job_manager(self, job_manager):
        self.job_manager = job_manager

http_server = HTTP_Server(__name__)
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
    return jsonify(job_list=http_server.job_manager.get_jobs_list())

@http_server.route('/job/<job_id>', methods=['POST'])
def start_job(job_id):
    if not http_server.job_manager.request_run(job_id):
        abort(404)
    return jsonify(status='success', job_id=job_id)
