import os, subprocess

def coffee(app):
    @app.before_request
    def _render_coffee():
        try:
            static_dir = app.root_path + app.static_url_path
        except AttributeError, e:    
            static_dir = app.root_path + app.static_path # < version 0.7
        
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