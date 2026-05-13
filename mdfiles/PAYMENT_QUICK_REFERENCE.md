# ⚡ Quick Reference - Payment System

## File Structure

```
frontend/
├── src/
│   ├── services/
│   │   ├── paymentService.ts        (Payment API wrapper)
│   │   └── notificationService.ts   (Notification handler)
│   ├── screens/
│   │   ├── wallet/
│   │   │   └── TopUpScreen.tsx      (Wallet top-up UI)
│   │   └── marketplace/
│   │       └── ListingDetailScreen.tsx (Updated with wallet)
│   ├── navigation/
│   │   ├── WalletNavigator.tsx      (New wallet navigator)
│   │   ├── MainNavigator.tsx        (Updated)
│   │   └── types.ts                 (Updated)
│   └── types/
│       └── react-native-razorpay.d.ts (Razorpay types)
└── App.tsx                          (Notification setup)
```

## API Endpoints Used

```
GET  /api/v1/payment/config/razorpay-key
POST /api/v1/payment/topup/create-order
POST /api/v1/payment/energy/create-order
POST /api/v1/payment/verify
GET  /api/v1/payment/history
POST /api/v1/payment/refund
```

## Payment Service Methods

```typescript
// Get Razorpay public key
const key = await paymentService.getRazorpayKey();

// Create top-up order
const order = await paymentService.createTopupOrder(500);
// Returns: { orderId, amount, currency, key_id }

// Create energy purchase order
const order = await paymentService.createEnergyPaymentOrder(txnId, 250);

// Verify payment
const result = await paymentService.verifyPayment({
  razorpay_order_id: "order_123",
  razorpay_payment_id: "pay_123",
  razorpay_signature: "signature_123"
});
```

## Notification Service Methods

```typescript
// Request permissions (called on app startup)
await notificationService.requestPermissions();

// Show payment success
await notificationService.showPaymentSuccess(500);

// Show payment failure
await notificationService.showPaymentFailure("Card declined");

// Show purchase success
await notificationService.scheduleNotification(
  "Energy Purchased! ⚡",
  "5.5 kWh purchased for ₹275"
);

// Show listing sold (for sellers)
await notificationService.showListingSold(listingId, 1500);
```

## UI Components

### TopUpScreen
- **Location**: `/frontend/src/screens/wallet/TopUpScreen.tsx`
- **Props**: None (uses navigation params)
- **Features**:
  - Wallet balance display
  - Amount input (₹10-₹50,000)
  - Quick amount buttons
  - Razorpay checkout
  - Test mode banner

### ListingDetailScreen
- **Location**: `/frontend/src/screens/marketplace/ListingDetailScreen.tsx`
- **Props**: `{ listingId: string }`
- **Features**:
  - Wallet balance in buy modal
  - Energy amount input
  - Balance validation
  - "Top Up" navigation

## Navigation Routes

```typescript
// Wallet Tab Stack
WalletNavigator
├── WalletOverview (default)
└── TopUp         (nested screen)

// Navigation usage
navigation.navigate('TopUp' as never);
navigation.navigate('Transactions' as never);
```

## Test Card

```
Card Number:  4111 1111 1111 1111
Expiry:       Any future date (MM/YY)
CVV:          Any 3 digits (e.g., 123)
OTP:          Razorpay will auto-verify in test mode
```

## Environment

```env
# Frontend
EXPO_PUBLIC_API_BASE_URL=http://10.251.149.193:3000

# Backend (already set)
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
```

## Common Workflows

### Scenario 1: User Top-Up Wallet
```
1. User: Click "Top Up" on Wallet tab
2. App: Navigate to TopUpScreen
3. User: Enter amount ₹500
4. App: Call paymentService.createTopupOrder(500)
5. App: Show Razorpay checkout
6. User: Complete payment with test card
7. App: Call paymentService.verifyPayment()
8. App: Show "Payment Successful" notification
9. App: Call fetchBalance() to refresh
10. App: Navigate back to Wallet
```

### Scenario 2: User Buy Energy
```
1. User: Click "Buy Energy" on listing
2. App: Show buy modal with wallet balance
3. User: Enter 5 kWh, total ₹250
4. App: Validate wallet balance (e.g., ₹500 ≥ ₹250)
5. App: Call buyEnergy() API
6. App: Show "Purchase Successful" notification
7. App: Refresh wallet balance (₹500 - ₹250 = ₹250)
8. App: Show success alert and navigate back
```

### Scenario 3: Insufficient Balance
```
1. User: Click "Buy Energy" with ₹1000 cost
2. App: Check wallet balance (₹500)
3. App: Show alert: "Need ₹1000, have ₹500"
4. User: Tap "Top Up"
5. App: Navigate to TopUpScreen
6. User: Top-up with ₹1000
7. App: Wallet now has ₹1500
8. User: Go back to marketplace and purchase succeeds
```

## Error Handling

### Payment Error
```typescript
try {
  await RazorpayCheckout.open(options);
} catch (error: any) {
  if (error.code) {
    // Razorpay error
    const reason = error.description || 'Payment failed';
    await notificationService.showPaymentFailure(reason);
    Alert.alert('Payment Failed', reason);
  } else {
    // Network or other error
    Alert.alert('Error', 'Failed to process payment');
  }
}
```

### Insufficient Balance
```typescript
if (walletBalance < totalCost) {
  Alert.alert(
    'Insufficient Balance',
    `Need ₹${totalCost}, have ₹${walletBalance}`,
    [
      { text: 'Cancel' },
      { 
        text: 'Top Up', 
        onPress: () => navigation.navigate('TopUp' as never)
      }
    ]
  );
}
```

## Debugging Tips

1. **Check Razorpay setup**:
   ```typescript
   const key = await paymentService.getRazorpayKey();
   console.log('Razorpay Key:', key);
   ```

2. **Check notification permissions**:
   ```typescript
   const token = await notificationService.getExpoPushToken();
   console.log('Push Token:', token);
   ```

3. **Monitor wallet updates**:
   ```typescript
   const wallet = useWalletStore(state => state.wallet);
   console.log('Wallet Balance:', wallet.balance);
   ```

4. **Check payment history**:
   ```typescript
   const history = await paymentService.getPaymentHistory(10, 0);
   console.log('Payment History:', history);
   ```

## Performance Optimization

- ✅ Lazy load payment screens
- ✅ Cache Razorpay key for 1 hour
- ✅ Batch wallet updates
- ✅ Debounce notification requests
- ✅ Use AsyncStorage for persistence

## Security Notes

- ✅ Never store sensitive card data
- ✅ Always verify signature on backend
- ✅ Use test keys in development
- ✅ Verify wallet balance before deduction
- ✅ Log all transactions for audit

## Next Improvements

1. Add payment analytics dashboard
2. Implement card saving for future purchases
3. Add payment method management
4. Implement refund workflow
5. Add payment failure recovery
6. Implement fraud detection
7. Add recurring payments
8. Implement payment webhooks
