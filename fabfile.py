from fabric.api import env, cd, run, sudo
from os.path import expanduser


INSTALL_PATH = '/home/ec2-user/minisite/current'

env.hosts = ['pycon.disqus.com']
env.key_filename = [expanduser('~/.ssh/minisite.pem')]
env.user = 'ec2-user'


def deploy():
    with cd(INSTALL_PATH):
        run('git pull origin master')

        run('../venv/bin/pip install -e .')

    #ln -s $INSTALL_DIR/local_settings.py disqus/local_settings.py

    sudo('supervisorctl restart all')
