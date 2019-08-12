from django.conf import settings

if settings.DATABASE_ENGINE == 'pool':
    settings.DATABASE_ENGINE = settings.POOL_DATABASE_ENGINE
from django.core.management.base import BaseCommand, CommandError
import os, time, sys


class Command(BaseCommand):
    option_list = BaseCommand.option_list + ()
    help = 'Starts sql pool server.'
    args = ''

    def handle(self, *args, **options):
        from pool.datapool import runsql
        print self.help
        runsql(settings.POOL_CONNECTION)
