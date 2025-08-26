from django.core.management.base import BaseCommand
from myproject.models import InvestmentPlan
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create/refresh GrowFi 1-7 investment plans (fixed values)'

    PLANS = [
        ('GROWFI 1', '300', 30, '56', '1680'),
        ('GROWFI 2', '700', 30, '88', '2640'),
        ('GROWFI 3', '2200', 60, '150', '4500'),
        ('GROWFI 4', '3500', 60, '190', '11400'),
        ('GROWFI 5', '5000', 90, '250', '22500'),
        ('GROWFI 6', '7000', 120, '250', '42000'),
        ('GROWFI 7', '9000', 140, '450', '63000'),
    ]

    def handle(self, *args, **options):
        created = 0
        for name, price, duration, daily, total in self.PLANS:
            # store a percentage approximation for reference (not used in logic)
            try:
                percent = (Decimal(daily) / Decimal(price)) * 100
            except Exception:
                percent = Decimal('0')
            obj, was_created = InvestmentPlan.objects.update_or_create(
                name=name,
                defaults={
                    'minimum_amount': Decimal(price),
                    'maximum_amount': Decimal(price),
                    'daily_return_rate': percent,
                    'duration_days': duration,
                    'is_active': True,
                }
            )
            created += 1 if was_created else 0
            self.stdout.write(self.style.SUCCESS(f'{"Created" if was_created else "Updated"}: {name}'))
            self.stdout.write(f'  Price: ₱{price}  Daily: ₱{daily}  Duration: {duration}d  Total/Net: ₱{total}')
        self.stdout.write(self.style.SUCCESS(f'Plans processed: {len(self.PLANS)} (created {created})'))
