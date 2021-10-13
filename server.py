from flask import Flask, json, session, request, redirect, url_for, send_from_directory
from datetime import datetime
import time
import random
import os
import subprocess
import shutil

DEFAULT_HOST = '0.0.0.0'

def current_milli_time():
    return round(time.time() * 1000)

api = Flask(__name__)
api.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
BASE_URL = os.getenv('BASE_URL')

folder_list = ['project']
for folder_name in folder_list:
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

@api.route(BASE_URL+'/', methods=['GET'])
def index():
    return (
        '<!doctype html>'
        '<title>Select Github Project</title>'
        '<h1>Select Github Project</h1>'
        '<form method="post" enctype="multipart/form-data" action="/sonarscanner">'
        '<p>Git repo url</p>'
        '<input type="text" name="git_url">'
        '<p>Project Key</p>'
        '<input type="text" name="projectkey">'
        '<p>Repo project name</p>'
        '<input type="text" name="sources">'
        '<p>Login token</p>'
        '<input type="text" name="token">'
        '<p> </p>'
        '<input type="submit" value="Ok">'
        '</form>'
    )
    # 4622775b31dc637e130077883dc2979aa7c61d11
    # 14848_Cloud_Infra_HW3
    # test
    # https://github.com/shihsunl/14848_Cloud_Infra_HW3.git

@api.route(BASE_URL+'/success', methods=['GET'])
def success():
    return (
        '<!doctype html>'
        '<title>Success</title>'
        '<h1>Success</h1>'
    )

@api.route(BASE_URL+'/sonarscanner', methods=['POST'])
def post_table_content():
    git_url    = request.form['git_url']
    projectkey = request.form['projectkey']
    sources    = request.form['sources']
    token      = request.form['token']

    print(git_url, projectkey, sources, token)

    cmd = 'cd project/ && git clone {} && sonar-scanner -Dsonar.projectKey={} -Dsonar.sources=/temp/project/{} -Dsonar.host.url=http://127.0.0.1:9000/sonarqube -Dsonar.login={}'.format(git_url, projectkey, sources, token)
    print(cmd)

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()

    print("Command output: ", output.decode())
    print("Command exit status/return code: ", p_status)

    path = '/temp/project/{}'.format(sources)
    shutil.rmtree(path)

    return output.decode()

if __name__ == '__main__':
    api.run(host=DEFAULT_HOST) 