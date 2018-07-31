#!/usr/bin/python3

from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify
import shutil
import string
import random
import sys
import re
import os

app = Flask(__name__)
api = Api(app)
user_file = "/etc/proftpd/ftpd.passwd" # path to ftpasswd file
ftpdata_dir = "/var/ftpdata" # data directory for the user homes
ftpuser = "ftpuser" # "admin" user. needs to be created first and needs write access to ftp data dir
ftpuser_uid = 1000 # ftp user uid
ftpuser_gid = 1000 # ftp user gid


def startup():
    u = users
    user_list = u.get(u)["users"]
    if not ftpuser in user_list:
        print("admin user not found. attempting to create it.")
        try:
            mk_user = user_create
            result = mk_user.get(mk_user, ftpuser, True)["status"]
            if result == "success":
                print("Success")
            else:
                print("Failed")
                sys.exit(1)
        except Exception as err:
            print("Could not find or create admin user")
            sys.exit(1)


class status(Resource):
    def read_status(self, service):
        output = os.popen("systemctl status "+service).read()
        status_regx= r"Active:(.*) since (.*);(.*)"
        service_status = {}
        service_status['service'] = service
        for line in output.splitlines():
            status_search = re.search(status_regx, line)
            if status_search:
                service_status['status'] = status_search.group(1).strip()
                service_status['since'] = status_search.group(2).strip()
                service_status['uptime'] = status_search.group(3).strip(" ago")
        return service_status

    def version(self):
        output = os.popen("proftpd --version").read().strip("ProFTPD Version").strip()
        return output
    
    def get_users(self):
        locked_users = 0
        active_users = 0
        with open(user_file, "r") as f:
            for line in f:
                line_spl = line.split(":")
                if line_spl[1].startswith("!"):
                    locked_users += 1
                else:
                    active_users += 1
            f.close()
        return active_users, locked_users

    def get(self):
        service = "proftpd"
        status = self.read_status(service)
        status['version'] = self.version()
        active_users, locked_users = self.get_users()
        status['active_users'] = active_users
        status['locked_users'] = locked_users
        return status


class users(Resource):
    def get(self):
        with open(user_file, "r") as f:
            userdata = f.readlines()
            f.close()
        users = []
        for user in userdata:
            users.append(user.split(":")[0])
        return {'users': users}
    def post(self):
        try:
            action = request.json["action"]
            user_name = request.json["username"]
            if user_name == ftpuser:
                response = {'status': 'failed', 'error': 'You can\'t edit the admin user'}
                return response
            user_home = ftpdata_dir+"/"+user_name
            if action == "create":
                passchars = string.ascii_letters+string.digits
                password = ''.join(random.SystemRandom().choice(passchars) for i in range(24))
                try:
                    if not os.path.exists(user_home):
                        os.makedirs(user_home)
                    os.chown(user_home, ftpuser_uid, ftpuser_gid)
                    os.system("echo \""+password+"\" | ftpasswd --passwd --file="+user_file+" --name="+user_name+" --home="+user_home+" --shell=/bin/false --uid="+str(ftpuser_uid)+" --stdin")
                    response = {'password': password, 'status': 'success'}
                except Exception as err:
                    response = {'status': 'failed', 'error': str(err)}
            elif action == "delete":
                try:
                    shutil.rmtree(user_home, ignore_errors=True)
                    os.system("ftpasswd --passwd --file="+user_file+" --name="+user_name+" --delete-user")
                    response = {'status': 'success'}
                except Exception as err:
                    response = {'status': 'failed', 'error': str(err)}
            elif action == "lock" or action == "unlock":
                try:
                    os.system("ftpasswd --passwd --file="+user_file+" --name="+user_name+" --"+action)
                    response = {'status': 'success'}
                except Exception as err:
                    response = {'status': 'failed', 'error': str(err)}
            else:
                response = {'status': 'failed', 'error': 'no such action'}
        except Exception as err:
            response = {'status': 'failed', 'error': str(err)}
        return response


class user_data(Resource):
    def get(self, user_name):
        try:
            with open(user_file, "r") as f:
                for line in f:
                    line = re.findall(r'^'+re.escape(user_name)+'\S*', line)
                    if line:
                        match = line
                f.close()
                userdata = match[0].split(":")
                if userdata[1].startswith("!"):
                    locked = True
                else:
                    locked = False
                response = {'name': userdata[0], 'uid': userdata[2], 'gid': userdata[3], 'home': userdata[5], 'shell': userdata[6], 'locked': locked}
        except:
            response = {'error': 'no such user'}
        return response


class usage(Resource):
    def get(self):
        try:
            st = os.statvfs(ftpdata_dir)
            free = st.f_bavail * st.f_frsize
            total = st.f_blocks * st.f_frsize
            used = (st.f_blocks - st.f_bfree) * st.f_frsize
            response = {'free': free, 'used': used, 'total': total, 'unit': 'bytes'}
        except Exception as err:
            response = {'status': 'failed', 'error': str(err)}
        return response
    

api.add_resource(users, '/users')
api.add_resource(user_data, '/users/<user_name>')
api.add_resource(usage, '/quota')
api.add_resource(status, '/')


if __name__ == "__main__":
    startup()
    app.run(port='5000')
