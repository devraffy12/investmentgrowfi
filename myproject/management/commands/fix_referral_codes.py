from django.core.management.base import BaseCommand
from myproject.models import UserProfile
import random
import string

class Command(BaseCommand):
    help = 'Fix missing referral codes for existing users'

    def handle(self, *args, **options):
        profiles_without_codes = UserProfile.objects.filter(
            referral_code__isnull=True
        ) | UserProfile.objects.filter(
            referral_code__exact=''
        )
        
        count = 0
        for profile in profiles_without_codes:
            # Generate a unique referral code
            while True:
                # Create an 8-character code with letters and numbers
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                # Ensure it's unique
                if not UserProfile.objects.filter(referral_code=code).exists():
                    profile.referral_code = code
                    profile.save()
                    count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Generated code {code} for user {profile.user.username}')
                    )
                    break
        
        self.stdout.write(
            self.style.SUCCESS(f'Fixed {count} users with missing referral codes')
        )
