import os
import os.path
import logging


class Gdrive(object):
    VIEW_FILE_URL = 'https://drive.google.com/file/d/%s/view'
    _logger = logging.getLogger('gdrive')

    def __init__(self, service_account):
        self.service_account = service_account

    def gdrive_command(self, *args):
        cmd = ' '.join(['gdrive', '-c', os.path.dirname(self.service_account),
            '--service-account', os.path.basename(self.service_account)] + list(args))
        self._logger.debug('popen: %s', cmd)
        ret = os.popen(cmd).read().strip()
        self._logger.debug('stdout: %s', ret)
        return ret

    def upload_file(self, file_path, delete=False, share=False, parent_directory=None, name=None, description=None):
        args = ['upload', '--no-progress']
        if delete:
            args.append('--delete')
        if share:
            args.append('--share')
        if parent_directory is not None:
            args.append('--parent')
            args.append(parent_directory)
        if name is not None:
            args.append('--name')
            args.append(name)
        if description is not None:
            args.append('--description')
            args.append(description)
        args.append(file_path)
        return self.gdrive_command(*args).splitlines()[1].split()[1]
