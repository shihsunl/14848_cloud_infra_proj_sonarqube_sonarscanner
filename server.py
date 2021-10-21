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
if BASE_URL == None:
    BASE_URL = ''

print('BASE_URL:', BASE_URL)

folder_list = ['project']
for folder_name in folder_list:
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

@api.route(BASE_URL+'/css/style.css', methods=['GET'])
def cssfile():
    file = open("css/style.css", mode='r')
    text = file.read()
    file.close()
    return (text)

@api.route(BASE_URL+'/', methods=['GET'])
def index():
    file = open("index.html", mode='r')
    text = file.read()
    file.close()
    text = text.format(proxy_base=BASE_URL)
    return (text)

    """
    return (
        '''<!doctype html>
        <title>Select Github Project</title>
        <h1>Select Github Project</h1>
        <form method="post" enctype="multipart/form-data" action="{}/scanrun">
        <p>Git repo url</p>
        <input type="text" name="git_url">
        <p>Project Key</p>
        <input type="text" name="projectkey">
        <p>Repo project name</p>
        <input type="text" name="sources">
        <p>Login token</p>
        <input type="text" name="token">
        <p> </p>
        <input type="submit" value="Ok">
        </form>'''.format(BASE_URL)
    )
    """

@api.route(BASE_URL+'/success', methods=['GET'])
def success():
    return (
        '<!doctype html>'
        '<title>Success</title>'
        '<h1>Success</h1>'
    )

@api.route(BASE_URL+'/scanrun', methods=['POST'])
def run_scanner():
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