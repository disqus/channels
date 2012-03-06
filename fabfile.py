from fabric.api import env, cd, run, sudo, local
from os.path import expanduser


INSTALL_PATH = '/home/ec2-user/minisite/current'

env.hosts = ['pycon.disqus.com']
env.key_filename = [expanduser('~/.ssh/minisite.pem')]
env.user = 'ec2-user'


def deploy():
    with cd(INSTALL_PATH):
        run('git pull origin master')

        run('../venv/bin/pip install -e .')

    bounce()

def flushredis():
    sudo('redis-cli flushall')

def bounce():
    sudo('supervisorctl restart all')

def realtime():
    local('./node_modules/.bin/coffee realtime/server.coffee')

def web():
    local('python manage.py runserver')
