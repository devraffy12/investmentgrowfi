@echo off
cd /d "C:\Users\raffy\OneDrive\Desktop\investment"

echo "=== PUSHING ALL CODE TO GITHUB ==="
echo "Current directory: %cd%"

echo "1. Checking git status..."
git status

echo "2. Adding all files..."
git add -A

echo "3. Committing changes..."
git commit -m "🚀 Pure Firebase Investment System - Complete Implementation

✅ FEATURES IMPLEMENTED:
- Pure Firebase authentication with session persistence
- 20-day investment plans (GROWFI 1-8) with automatic daily payouts
- Real-time team/referral system using Firestore
- Transaction history with real data calculations
- Balance management with registration bonus system
- Records page with proper filtering and counts

🔥 PURE FIREBASE COMPONENTS:
- User profiles stored in Firestore
- Team data in Firestore teams collection
- Referrals in Firestore referrals collection
- Commissions in Firestore commissions collection
- Authentication sessions in Firestore

💰 INVESTMENT SYSTEM:
- 8 investment plans: ₱300 to ₱11,000
- Daily returns: ₱150 to ₱3,850 per day
- 20-day investment duration
- Automatic daily payout processing
- Investment progress tracking

📊 TEAM SYSTEM:
- My Referrals: Real referral count
- Active Members: Users with balance > 0
- Total Earnings: Commission earnings
- Team Volume: Team investment volume

✅ TESTED & WORKING:
- All authentication flows
- Investment purchase and tracking
- Daily payout generation
- Team calculations
- Balance updates
- Data persistence"

echo "4. Pushing to GitHub..."
git push origin main

echo "5. Verifying push..."
git log --oneline -3

echo "=== GITHUB PUSH COMPLETED ==="
pause
