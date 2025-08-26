# GCash and PayMaya API Integration Setup Guide

## Overview
This guide will help you set up automatic payment processing for deposits and withdrawals using GCash and PayMaya APIs.

## 🔑 Getting API Credentials

### GCash for Business API
1. **Register for GCash for Business**
   - Visit: https://www.gcash.com/business
   - Apply for a business account
   - Complete KYB (Know Your Business) verification

2. **API Access**
   - Contact GCash Business Support to request API access
   - Submit required business documents
   - Get approved for payment processing

3. **Credentials You'll Receive**
   - API Key
   - Secret Key
   - Merchant ID
   - Sandbox credentials for testing

### PayMaya for Business API
1. **Register for PayMaya Business**
   - Visit: https://paymaya.com/business
   - Apply for merchant account
   - Complete business verification

2. **Developer Access**
   - Visit PayMaya Developer Portal
   - Create an application
   - Request API access

3. **Credentials You'll Receive**
   - Public Key (for checkouts)
   - Secret Key (for disbursements)
   - Webhook keys

## 🛠️ Environment Setup

### 1. Add API Credentials to Environment Variables

Create a `.env` file in your project root:

```bash
# GCash API Configuration
GCASH_API_KEY=your_actual_gcash_api_key
GCASH_SECRET_KEY=your_actual_gcash_secret_key
GCASH_MERCHANT_ID=your_actual_merchant_id
GCASH_SANDBOX=True  # Set to False for production
GCASH_API_URL=https://sandbox-api.gcash.com/v1  # Sandbox URL

# PayMaya API Configuration
PAYMAYA_PUBLIC_KEY=your_actual_paymaya_public_key
PAYMAYA_SECRET_KEY=your_actual_paymaya_secret_key
PAYMAYA_SANDBOX=True  # Set to False for production
PAYMAYA_API_URL=https://pg-sandbox.paymaya.com  # Sandbox URL

# Site Configuration
SITE_URL=https://yourdomain.com  # Your website URL for callbacks
```

### 2. Install Required Packages

```bash
pip install requests python-decouple
```

### 3. Database Migration

Run the migration to update your Transaction model:

```bash
python manage.py makemigrations myproject
python manage.py migrate
```

## 🚀 Implementation Steps

### 1. Basic Deposit Flow
```python
# In your view or JavaScript
from myproject.payment_integrations import create_deposit_payment

# Create a deposit request
result = create_deposit_payment(
    payment_method='gcash',  # or 'paymaya'
    amount=500,  # PHP amount
    user_phone='09171234567',
    reference_id='DEP_123_ABC123'
)

if result['success']:
    # Redirect user to payment URL
    payment_url = result['payment_url']
    # Or show QR code
    qr_code = result['qr_code']
```

### 2. Basic Withdrawal Flow
```python
from myproject.payment_integrations import process_withdrawal_payment

# Process a withdrawal
result = process_withdrawal_payment(
    payment_method='gcash',  # or 'paymaya'
    amount=1000,  # PHP amount
    account_number='09171234567',
    account_name='Juan Dela Cruz',
    reference_id='WTH_123_XYZ789'
)

if result['success']:
    # Withdrawal initiated
    transaction_id = result['transaction_id']
```

### 3. Frontend Integration
Use the provided JavaScript in `payment_integration_example.html` to integrate with your frontend.

## 📋 API Endpoints

### Your New Endpoints:
- `POST /payment/deposit/create/` - Create automatic deposit
- `POST /payment/withdrawal/process/` - Process automatic withdrawal
- `GET /payment/status/{transaction_id}/` - Check payment status
- `POST /webhooks/gcash/` - GCash webhook handler
- `POST /webhooks/paymaya/` - PayMaya webhook handler

### Example Usage:

#### Create Deposit
```javascript
fetch('/payment/deposit/create/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        amount: 500,
        payment_method: 'gcash'
    })
})
```

#### Process Withdrawal
```javascript
fetch('/payment/withdrawal/process/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        amount: 1000,
        bank_account_id: 1
    })
})
```

## 🔐 Security Features

1. **HMAC Signature Verification** - All API requests are signed
2. **Webhook Validation** - Incoming webhooks are verified
3. **Reference ID Tracking** - Unique identifiers for all transactions
4. **Status Monitoring** - Real-time transaction status updates

## 🧪 Testing

### Sandbox Mode
- All APIs are configured for sandbox testing by default
- Use test credentials provided by GCash and PayMaya
- Test transactions won't affect real money

### Test Flow:
1. Create a deposit request
2. Use sandbox payment credentials
3. Complete payment in sandbox environment
4. Verify webhook callbacks
5. Check transaction status updates

## 📊 Monitoring & Logs

The system logs all payment activities:
- API requests and responses
- Webhook events
- Transaction status changes
- Error conditions

Check Django logs for debugging:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Payment processed successfully")
```

## 🔄 Webhook Configuration

### GCash Webhooks
Set up webhook URL in GCash dashboard:
```
https://yourdomain.com/webhooks/gcash/
```

### PayMaya Webhooks
Configure in PayMaya developer portal:
```
https://yourdomain.com/webhooks/paymaya/
```

## ⚠️ Important Notes

1. **Production Setup**:
   - Get production API credentials
   - Set `GCASH_SANDBOX=False` and `PAYMAYA_SANDBOX=False`
   - Update API URLs to production endpoints
   - Implement proper SSL certificates

2. **Error Handling**:
   - Always check API response status
   - Implement retry logic for failed requests
   - Monitor webhook delivery

3. **Security**:
   - Never expose API keys in frontend code
   - Use environment variables for credentials
   - Validate all webhook requests

4. **Compliance**:
   - Follow BSP (Bangko Sentral ng Pilipinas) regulations
   - Implement proper KYC/AML procedures
   - Maintain transaction records

## 📞 Support

- **GCash Business Support**: business@gcash.com
- **PayMaya Business Support**: business@paymaya.com
- **Technical Issues**: Check API documentation and error logs

## 📖 Additional Resources

- [GCash API Documentation](https://developer.gcash.com)
- [PayMaya API Documentation](https://developers.paymaya.com)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Webhook Best Practices](https://webhooks.fyi/)

---

This implementation provides a solid foundation for automatic payment processing. Remember to thoroughly test in sandbox mode before going live!
