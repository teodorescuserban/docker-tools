"""generate templates and key files for a service inside a container."""
import imp
import os

HELPER_PATH = 'docohelper.py'


def main():
    """show a use-case."""
    doco = imp.load_source('docohelper', HELPER_PATH)

    # inside the container
    s = doco.DockerHelper.fromcontainer(templates_root_path='/etc/nginx')

    s.create_special_file('/etc/nginx/ssl.crt', 'NGINX_SSL_CRT', private=False)
    s.create_special_file('/etc/nginx/ssl.key', 'NGINX_SSL_KEY', private=True)

    # constructs basic auth pass file
    PASSWORD_FILE = ''.join(['/etc', '/nginx/',
                             os.getenv('DEPLOY_TYPE'), '-datapass'])

    s.create_special_file(PASSWORD_FILE, 'NGINX_PASS_FILE', private=True)

    s.create_config_files()


if __name__ == '__main__':
    main()
