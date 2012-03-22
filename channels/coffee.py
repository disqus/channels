"""
flaskext.coffee
~~~~~~~~~~~~~

A CoffeeScript extension for Flask

:copyright: (c) 2011 by Col Wilson.
:license: MIT
"""
import os
import subprocess


def compile(static_dir):

    coffee_paths = []
    for path, subdirs, filenames in os.walk(static_dir):
        coffee_paths.extend([
            os.path.join(path, f)
            for f in filenames if os.path.splitext(f)[1] == '.coffee'
        ])

    for coffee_path in coffee_paths:
        js_path = os.path.splitext(coffee_path)[0] + '.coffee'
        if not os.path.isfile(js_path):
            js_mtime = -1
        else:
            js_mtime = os.path.getmtime(js_path)
        coffee_mtime = os.path.getmtime(coffee_path)
        if coffee_mtime >= js_mtime:
            subprocess.call(['node_modules/.bin/coffee', '-c', coffee_path], shell=False)


def coffee(app):
    @app.before_request
    def _render_coffee():
        try:
            static_dir = app.root_path + app.static_url_path
        except AttributeError:
            static_dir = app.root_path + app.static_path  # < version 0.7
        compile(static_dir)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        static_dir = sys.argv[1]
    else:
        import os.path
        static_dir = os.path.join(os.path.dirname(sys.argv[0]), 'static', 'js')

    compile(static_dir)
