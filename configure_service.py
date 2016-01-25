"""prepare a docker container service to run."""

import os
import re


class ConfigureService(object):
    """
    provide the tools to configure the service.

    to be run inside the container.
    """

    version = '0.1'

    def __init__(self, env_dict, templates_path):
        """init."""
        self.env = env_dict
        self.templates_path = templates_path
        # default mode of writing files
        self.set_write_mode()

    def create_config_files(self):
        """loop through templates and call create config files for them."""
        for template_file in self._find_templates():
            file_name = re.sub(r'\.tpl$', '', template_file)
            with open(template_file) as t:
                content = t.read()
            # self._content_to_file(template_file)
            new_file_content = self._build_config_file(content)
            self._content_to_file(file_name, new_file_content)

    def create_special_file(self, file_name, content_var):
        """create file_name containing the value of self.env[content_var]."""
        if content_var not in self.env:
            print 'Cannot find variable named', content_var
            print 'Skipping creation of file', file_name
            return
        content = self._env_to_str(self.env[content_var])
        self._content_to_file(file_name, content)

    def set_write_mode(self, overwrite=False, private=False, uid=0, gid=0):
        """set parameters for the future file writes."""
        # default mode of writing files
        self.overwrite = overwrite
        self.private = private
        self.uid = uid
        self.gid = gid

    @staticmethod
    def _env_to_str(string):
        """convert the content of a env var to a string."""
        if '"' in string:
            string = string.replace('"', '')
        string = string.split(":::")
        # ensure new line at the end
        string.append('\n')
        return '\n'.join(string)

    def _content_to_file(self, file_name, content):
        """write the content provided to specified file."""
        if self.private:
            mode = 0o400
        else:
            mode = 0o644

        if os.path.isfile(file_name) and not self.overwrite:
            print 'File', file_name, 'aleady exists. Skipping.'
            return
        with open(file_name, 'w') as f:
            print 'writing', file_name, '...'
            f.write(content)
        os.chown(file_name, self.uid, self.gid)
        os.chmod(file_name, mode)

    def _find_templates(self):
        """find all teplates files in the specified path."""
        templates = []
        for root, dirs, files in os.walk(self.templates_path):
            for file_name in files:
                if file_name.endswith('.tpl'):
                    templates.append(os.path.join(root, file_name))
        return templates

    def _build_config_file(self, content):
        """replace in content the env vars with their values."""
        template_variables = re.findall(r'\$\{([0-9a-zA-Z_]+)\}', content)
        for tvar in template_variables:
            if tvar not in self.env:
                # env dict incomplete
                print 'Could not find env var:', tvar
                continue
            content = content.replace('${' + tvar + '}', self.env[tvar])
        content = content.replace('%', '$')
        return content

if __name__ == '__main__':
    # example for HDX nginx.
    container_env = os.environ
    templates_root_path = '/etc/nginx'
    cs = ConfigureService(container_env, templates_root_path)
    cs.create_config_files()
    cs.create_special_file('/etc/nginx/ssl.crt', 'HDX_SSL_CRT')
    # cs.create_special_file('/etc/nginx/XXX-datapass', 'HDX_NGINX_PASS')
    cs.set_write_mode(private=True)
    cs.create_special_file('/etc/nginx/ssl.key', 'HDX_SSL_KEY')
