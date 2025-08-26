#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

# Now test the API
from myproject.la2568_api import la2568_api
from decimal import Decimal
import json

print('Testing LA2568 API...')
result = la2568_api.create_direct_deposit_order(
    amount=Decimal('500.00'),
    user_id=1,
    payment_method='gcash',
    auto_redirect=True
)

print('API Response:')
print(json.dumps(result, indent=2, default=str))
