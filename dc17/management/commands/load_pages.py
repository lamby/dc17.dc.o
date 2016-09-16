import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from wafer.pages.models import Page
import yaml


class Command(BaseCommand):
    help = 'Load pages from yaml files into the DB'

    def handle(self, *args, **options):
        for dirpath, dirnames, filenames in os.walk(settings.PAGE_DIR):
            parent = self.get_parent(dirpath)
            for fn in filenames:
                if not fn.endswith('.yaml'):
                    continue
                slug = fn[:-5]
                with open(os.path.join(dirpath, fn)) as f:
                    contents = yaml.load(f)
                self.load_page(parent, slug, contents)

    def get_parent(self, directory):
        """
        Given a directory name, return the Page representing it in the menu
        heirarchy.
        """
        assert settings.PAGE_DIR.startswith('/')
        assert settings.PAGE_DIR.endswith('/')

        parents = directory[len(settings.PAGE_DIR):]

        page = None
        if parents:
            for slug in parents.split('/'):
                page = Page.objects.get(parent=page, slug=slug)
        return page

    def load_page(self, parent, slug, contents):
        page, created = Page.objects.get_or_create(parent=parent, slug=slug)
        page.name = contents['name']
        page.content = contents['content']
        page.include_in_menu = contents.get('include_in_menu', False)
        page.exclude_from_static = contents.get('exclude_from_static', False)
        page.people.clear()
        page.people.add(*(
            get_user_model().objects.get(username=person)
            for person in contents.get('people', ())
        ))
        page.save()
        self.stdout.write('Loaded page %s\n' % '/'.join(page.get_path()))
