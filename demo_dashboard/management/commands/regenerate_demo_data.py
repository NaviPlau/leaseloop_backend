from django.core.management.base import BaseCommand, CommandError









class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("--test", action="store_true")


    def handle(self, *args, **options):
        if options["test"]:
            self.stdout.write("This is a test")
        self.stdout.write("Regenerating demo data...")