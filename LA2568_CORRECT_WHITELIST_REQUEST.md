# LA2568 WHITELIST REQUEST - CORRECT OUTBOUND IPs

## 🚨 URGENT: Correct IP Addresses for Whitelisting

**Date**: August 21, 2025  
**Issue**: API calls being blocked - whitelist error

---

## 📝 WHITELIST REQUEST

Dear LA2568 Support,

I am receiving the following whitelist error when making API calls:
```
"Not added to the api whitelist:QXBpQ29udHJvbGxlci5waHA=:682"
```

**Please whitelist the following OUTBOUND IP addresses for API calls:**

### 🌐 Production - Render.com Outbound IPs
```
44.229.227.142
54.188.71.94  
52.13.128.108
```

### 🔧 Development IP
```
180.190.127.16
```

### 📋 Account Details
- **Merchant ID**: `RodolfHitler`
- **Secret Key**: `86cb40fe1666b41eb0ad21577d66baef`
- **Production Domain**: `https://investmentgrowfi.onrender.com`
- **Callback URL**: `https://investmentgrowfi.onrender.com/payment/callback/`
- **Success URL**: `https://investmentgrowfi.onrender.com/payment/success/`

### 💳 Payment Channels Configured
- **GCash QR**: `payment_type=1, bank_code=gcash`
- **GCash H5**: `payment_type=7, bank_code=mya` 
- **PayMaya**: `payment_type=3, bank_code=PMP`

---

## 🔍 TECHNICAL DETAILS

### What needs whitelisting:
- ✅ **OUTBOUND IPs** (for API calls FROM my server TO LA2568)
- ✅ **Development IP** (for testing)

### What's happening:
1. My Django app calls LA2568 API from Render.com servers
2. Render.com uses specific outbound IP addresses for external API calls  
3. These IPs need to be whitelisted on LA2568 side
4. Currently getting blocked with whitelist error

### API Call Flow:
```
User deposits → Django app → LA2568 API (via Render outbound IPs) → Payment gateway
```

---

## 📞 NEXT STEPS

1. **Whitelist the outbound IPs above**
2. **Confirm when whitelisting is complete**
3. **I will test and confirm functionality**

**Contact**: Please reply when whitelisting is complete so I can test the integration.

Thank you for your assistance!

---

## 🔧 TECHNICAL VERIFICATION

After whitelisting, I expect:
- ✅ API calls return `{"status":"1", "payment_url":"...", "order_id":"..."}`
- ✅ No more whitelist error messages
- ✅ Successful payment processing

**Current Error**: `Not added to the api whitelist:QXBpQ29udHJvbGxlci5waHA=:682`  
**Expected**: Successful API responses with payment URLs
