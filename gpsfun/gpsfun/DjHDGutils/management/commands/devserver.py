"""
devserver
"""
from django.core.management.commands.runserver import BaseRunserverCommand
from django.conf import settings
import random
import os


class Command(BaseRunserverCommand):
    """ Command """

    def handle(self, addrport='', *args, **options):
        if not addrport:
            summ = sum([ord(char)
                        for char in settings.SITE_ROOT.split('/')[-2]])
            random.seed(summ)
            port = random.randrange(1024, 5000)
            server_address = '127.0.0.1'
            if os.path.exists('/etc/hosts'):
                with open('/etc/hosts') as f:
                    if f.read().find('local.dev') != -1:
                        server_address = 'local.dev'
            addrport = '%s:%s' % (server_address, port)
        super(Command, self).handle(addrport, *args, **options)
