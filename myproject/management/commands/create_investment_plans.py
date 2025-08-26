from django.core.management.base import BaseCommand
from myproject.models import InvestmentPlan
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create initial investment plans'

    def handle(self, *args, **options):
        plans_data = [
            {
                'name': 'Starter Plan',
                'minimum_amount': Decimal('300.00'),
                'maximum_amount': Decimal('300.00'),
                'daily_return_rate': Decimal('16.67'),  # ₱50 daily for ₱300
            },
            {
                'name': 'Basic Plan',
                'minimum_amount': Decimal('500.00'),
                'maximum_amount': Decimal('500.00'),
                'daily_return_rate': Decimal('18.00'),  # ₱90 daily for ₱500
            },
            {
                'name': 'Premium Plan',
                'minimum_amount': Decimal('1000.00'),
                'maximum_amount': Decimal('1000.00'),
                'daily_return_rate': Decimal('19.00'),  # ₱190 daily for ₱1000
            },
            {
                'name': 'Gold Plan',
                'minimum_amount': Decimal('1500.00'),
                'maximum_amount': Decimal('1500.00'),
                'daily_return_rate': Decimal('18.00'),  # ₱270 daily for ₱1500
            },
            {
                'name': 'Platinum Plan',
                'minimum_amount': Decimal('2000.00'),
                'maximum_amount': Decimal('2000.00'),
                'daily_return_rate': Decimal('20.00'),  # ₱400 daily for ₱2000
            },
            {
                'name': 'VIP Plan',
                'minimum_amount': Decimal('3000.00'),
                'maximum_amount': Decimal('3000.00'),
                'daily_return_rate': Decimal('20.00'),  # ₱600 daily for ₱3000
            },
        ]

        created_count = 0
        for plan_data in plans_data:
            plan, created = InvestmentPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            
            if created:
                created_count += 1
                daily_amount = (plan_data['minimum_amount'] * plan_data['daily_return_rate']) / 100
                total_return = daily_amount * 30
                profit = total_return - plan_data['minimum_amount']
                
                self.stdout.write(f'Created: {plan.name}')
                self.stdout.write(f'  Investment: ₱{plan_data["minimum_amount"]}')
                self.stdout.write(f'  Daily Return: ₱{daily_amount}')
                self.stdout.write(f'  Total Return: ₱{total_return}')
                self.stdout.write(f'  Pure Profit: ₱{profit}')
                self.stdout.write('---')
            else:
                self.stdout.write(f'Already exists: {plan.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} investment plans')
        )
