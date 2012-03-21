from fabric.api import env, cd, run, sudo, local

from channels.app import app

INSTALL_PATH = app.config['INSTALL_PATH']

env.hosts = app.config['DEPLOY_HOSTS']
env.key_filename = [app.config['DEPLOY_KEY']]
env.user = app.config['DEPLOY_USER']


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
