# Payment System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOLAR SHARING APP                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐      ┌──────────────────┐              │
│  │   Marketplace    │      │     Wallet       │              │
│  │   (Buy Energy)   │      │   (Top-Up/Pay)   │              │
│  └────────┬─────────┘      └────────┬─────────┘              │
│           │                         │                        │
│           └─────────────┬───────────┘                        │
│                         ▼                                     │
│                  ┌──────────────────┐                        │
│                  │  Wallet Store    │                        │
│                  │   (Zustand)      │                        │
│                  └────────┬─────────┘                        │
│                           │                                  │
│           ┌───────────────┼───────────────┐                 │
│           ▼               ▼               ▼                 │
│  ┌─────────────────┐ ┌──────────────┐ ┌─────────────┐      │
│  │ Payment         │ │ Notification │ │ Auth Store  │      │
│  │ Service         │ │ Service      │ │ (preserved) │      │
│  └────────┬────────┘ └──────┬───────┘ └─────────────┘      │
│           │                 │                              │
│           │                 └──────► Notifications         │
│           │                         (Expo)                │
│           │                                              │
│           └──────► HTTP Client                          │
│                   (axios)                               │
│                        ▼                                │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────┐
        │         BACKEND SERVER            │
        ├───────────────────────────────────┤
        │                                   │
        │  ✅ Payment Routes                │
        │     ├─ /payment/config            │
        │     ├─ /payment/topup             │
        │     ├─ /payment/verify            │
        │     └─ /payment/energy            │
        │                                   │
        │  ✅ Marketplace Routes            │
        │     └─ /marketplace/buy-energy    │
        │                                   │
        │  ✅ Wallet Routes                 │
        │     ├─ /wallet/balance            │
        │     └─ /wallet/transactions       │
        │                                   │
        └───────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────┐
        │      RAZORPAY API                 │
        ├───────────────────────────────────┤
        │ Create Order → Verify Payment     │
        │ Test Mode (No Real Charges)       │
        └───────────────────────────────────┘
```

## Data Flow: Top-Up Wallet

```
┌──────────┐
│   User   │
│ Opens    │
│ Wallet   │
└────┬─────┘
     │
     ▼
┌─────────────────────┐
│ WalletScreen        │
│ - Show Balance      │
│ - Top Up Button     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Navigation          │
│ navigate('TopUp')   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ TopUpScreen         │
│ - Amount Input      │
│ - Quick Buttons     │
│ - Test Card Banner  │
└──────────┬──────────┘
           │
    ┌──────┴───────┬──────────┐
    │ User Enters  │ Quick    │
    │ Amount       │ Button   │
    └──────────────┴──────┬───┘
                         │
                         ▼
           ┌─────────────────────────────┐
           │ paymentService              │
           │ .createTopupOrder(amount)   │
           └──────────┬──────────────────┘
                      │
           HTTP POST  │ /payment/topup/create-order
                      ▼
           ┌─────────────────────────────┐
           │ BACKEND                     │
           │ Create Razorpay Order       │
           └──────────┬──────────────────┘
                      │
                      ▼
           ┌─────────────────────────────┐
           │ Return OrderID              │
           │ Amount, Currency            │
           │ Public Key                  │
           └──────────┬──────────────────┘
                      │
                      ▼
           ┌─────────────────────────────┐
           │ RazorpayCheckout.open()     │
           │ Shows Native Checkout UI    │
           └──────────┬──────────────────┘
                      │
           ┌──────────┴──────────┐
           ▼                     ▼
    ┌────────────┐        ┌────────────┐
    │ User       │        │ Success!   │
    │ Completes  │        │ Payment ID │
    │ Payment    │        │ Signature  │
    └──────┬─────┘        └──────┬─────┘
           │                     │
           └──────────┬──────────┘
                      │
                      ▼
           ┌─────────────────────────────┐
           │ paymentService              │
           │ .verifyPayment(data)        │
           └──────────┬──────────────────┘
                      │
           HTTP POST  │ /payment/verify
                      ▼
           ┌─────────────────────────────┐
           │ BACKEND                     │
           │ Verify Signature            │
           │ Update Wallet Balance       │
           │ Create Transaction Record   │
           └──────────┬──────────────────┘
                      │
                      ▼
           ┌─────────────────────────────┐
           │ Return { success: true }    │
           └──────────┬──────────────────┘
                      │
                      ▼
           ┌─────────────────────────────┐
           │ notificationService         │
           │ .showPaymentSuccess(amount) │
           │ "Payment Successful ⚡"     │
           └──────────┬──────────────────┘
                      │
                      ▼
           ┌─────────────────────────────┐
           │ walletStore.fetchBalance()  │
           │ Update Local Balance        │
           └──────────┬──────────────────┘
                      │
                      ▼
           ┌─────────────────────────────┐
           │ Navigation                  │
           │ .goBack()                   │
           │ Return to Wallet Tab        │
           └─────────────────────────────┘
```

## Data Flow: Buy Energy

```
┌──────────┐
│   User   │
│ Views    │
│ Listing  │
└────┬─────┘
     │
     ▼
┌──────────────────────┐
│ ListingDetailScreen  │
│ - Show Details       │
│ - Buy Button         │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ handleBuyPress()     │
│ - Fetch Balance      │
│ - Show Modal         │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Buy Modal                        │
│ - Wallet Balance: ₹500           │
│ - Energy Amount Input (kWh)      │
│ - Total Cost Calculation         │
│ - Summary Card                   │
└────────┬───────────────────┬─────┘
         │                   │
    User │ Enters Amount     │ Cancel
    Input│                   │
         ▼                   ▼
    ┌─────────────────┐  Dismiss
    │ handlePurchase()│  Modal
    └────────┬────────┘
             │
    ┌────────┴─────────────┬──────────┐
    │ Validate             │          │
    │ Amount               │ Check    │
    │                      │ Balance  │
    ▼                      ▼          ▼
┌───────────────┐  ┌──────────────────────────┐
│ Amount OK?    │  │ Balance OK?              │
└───┬───────────┘  └──────────┬───────────────┘
    │                         │
    NO          NO            YES
    │           │             │
    ▼           ▼             ▼
 Alert       Alert         ┌──────────────────┐
 Invalid     Top Up         │ marketplaceApi   │
 Amount      Button      │ .buyEnergy()     │
             │navigate    │                  │
             │TopUp       └────────┬─────────┘
                                  │
                       HTTP POST  │ /marketplace/buy-energy
                                  ▼
                       ┌──────────────────────────┐
                       │ BACKEND                  │
                       │ - Check Balance          │
                       │ - Create Transaction     │
                       │ - Deduct from Wallet     │
                       │ - Update Listing Status  │
                       │ - Lock Row (Prevent      │
                       │   Double Buy)            │
                       │ - COMMIT Transaction     │
                       └────────┬─────────────────┘
                                │
                                ▼
                       ┌──────────────────────────┐
                       │ Return Success + TxnID   │
                       └────────┬─────────────────┘
                                │
                                ▼
                       ┌──────────────────────────┐
                       │ notificationService      │
                       │ .scheduleNotification()  │
                       │ "Energy Purchased ⚡"    │
                       └────────┬─────────────────┘
                                │
                                ▼
                       ┌──────────────────────────┐
                       │ walletStore              │
                       │ .fetchBalance()          │
                       │ Update Local State       │
                       └────────┬─────────────────┘
                                │
                                ▼
                       ┌──────────────────────────┐
                       │ Alert                    │
                       │ "Purchase Successful!"   │
                       │ - View Transactions      │
                       │ - OK (Go Back)           │
                       └────────┬─────────────────┘
                                │
                                ▼
                       ┌──────────────────────────┐
                       │ Navigation               │
                       │ .goBack()                │
                       │ Return to Listing List   │
                       └──────────────────────────┘
```

## Component Hierarchy

```
App.tsx
├── RootNavigator
│   ├── AuthNavigator
│   │   ├── Login
│   │   ├── Register
│   │   └── ...
│   │
│   └── MainNavigator (Bottom Tabs)
│       ├── HomeScreen
│       ├── EnergyScreen
│       ├── MarketplaceNavigator
│       │   ├── ListingListScreen
│       │   └── ListingDetailScreen ⭐ UPDATED
│       │       └── Buy Modal (Wallet Integration)
│       │
│       ├── DiscoveryNavigator
│       │
│       ├── WalletNavigator ⭐ NEW
│       │   ├── WalletScreen
│       │   │   └── Top Up Button
│       │   └── TopUpScreen ⭐ NEW
│       │       ├── Amount Input
│       │       ├── Quick Buttons
│       │       ├── Razorpay Checkout
│       │       └── Test Banner
│       │
│       ├── DeviceStackNavigator
│       │
│       └── ProfileNavigator
```

## Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                    │
│  (Screens, Components, UI Logic)                        │
└─────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ paymentService   │ │ notification     │ │  marketplaceApi  │
│                  │ │  Service         │ │                  │
│ ✅ getRazorpay   │ │                  │ │ ✅ buyEnergy     │
│    Key()         │ │ ✅ request       │ │                  │
│ ✅ createTopup   │ │    Permissions() │ │ ✅ getListings   │
│    Order()       │ │ ✅ showPayment   │ │                  │
│ ✅ createEnergy  │ │    Success()     │ │ ✅ listingDetail │
│    PaymentOrder()│ │ ✅ showPayment   │ │                  │
│ ✅ verifyPayment │ │    Failure()     │ │                  │
│    ()            │ │ ✅ schedule      │ │                  │
│ ✅ getPayment    │ │    Notification()│ │                  │
│    History()     │ │                  │ │                  │
│ ✅ requestRefund │ │ ✅ showListing   │ │                  │
│    ()            │ │    Sold()        │ │                  │
│                  │ │ ✅ showVerif     │ │                  │
└──────────────────┘ │    ication       │ └──────────────────┘
                     │    Approved()    │
                     │                  │
                     │ ✅ Listeners     │
                     │ ✅ Badge Count   │
                     └──────────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         ▼
        ┌────────────────────────────────┐
        │    HTTP Client (axios)         │
        │                                │
        │ Base URL:                      │
        │ http://10.251.149.193:3000     │
        └────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
    ┌────────┐      ┌────────┐       ┌────────┐
    │ Razorpay    Payment   Wallet
    │ API    │      DB       DB
    └────────┘      └────────┘       └────────┘
```

## State Management Flow

```
┌──────────────────────────────────────────────────────────┐
│                 Zustand Stores                            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  useWalletStore                useAuthStore             │
│  ├─ wallet.balance      (PRESERVED)                     │
│  ├─ wallet.transactions │ ├─ user.id                    │
│  ├─ recentActivity      │ ├─ user.email                │
│  ├─ monthlySummary      │ ├─ user.role                 │
│  │                      │ └─ user.fullName             │
│  ├─ fetchBalance()      │ └─ setUser()                 │
│  ├─ fetchTransactions() │                              │
│  ├─ fetchMonthlySummary │                              │
│  ├─ loadMoreTransactions│                              │
│  └─ refresh()           │                              │
│                         │                              │
│  Persisted with         │  Persisted with             │
│  AsyncStorage ✓         │  AsyncStorage ✓             │
└──────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
    Screens          Services         Navigation
    use balance  to show data  to control flow
```

## Notification Flow

```
┌─────────────────────────────────────────┐
│         Notification Events             │
├─────────────────────────────────────────┤
│                                         │
│  Event 1: Payment Success               │
│  └─ Top-Up Completed ✓                 │
│     └─ notificationService              │
│        .showPaymentSuccess()             │
│        └─ Notification Displayed        │
│                                         │
│  Event 2: Payment Failed                │
│  └─ Card Declined ✗                    │
│     └─ notificationService              │
│        .showPaymentFailure()             │
│        └─ Notification Displayed        │
│                                         │
│  Event 3: Energy Purchased              │
│  └─ Buy Transaction ✓                  │
│     └─ notificationService              │
│        .scheduleNotification()           │
│        └─ Notification Displayed        │
│                                         │
│  Event 4: Listing Sold (Seller)         │
│  └─ Energy Sold ✓                      │
│     └─ notificationService              │
│        .showListingSold()                │
│        └─ Notification Displayed        │
│                                         │
│  Event 5: Verification Approved         │
│  └─ Host Verified ✓                    │
│     └─ notificationService              │
│        .showVerificationApproved()       │
│        └─ Notification Displayed        │
│                                         │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│     Notification Listeners              │
├─────────────────────────────────────────┤
│                                         │
│  Received: Notification arrives         │
│  └─ Callback triggered                 │
│     └─ Handle in background/foreground  │
│                                         │
│  Response: User taps notification       │
│  └─ Callback triggered                 │
│     └─ Navigate to relevant screen     │
│                                         │
│  Badge: Update app icon badge           │
│  └─ Shows count of notifications       │
│                                         │
└─────────────────────────────────────────┘
```

## Error Handling Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Error Scenarios                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Network Error                                          │
│  ├─ Offline Connection                                 │
│  ├─ Timeout                                            │
│  ├─ Server Error (5xx)                                 │
│  └─ Action: Show Alert, Allow Retry                    │
│                                                         │
│  Payment Error                                          │
│  ├─ Razorpay Initialization Failed                     │
│  ├─ User Cancelled Payment                             │
│  ├─ Card Declined                                      │
│  ├─ Invalid Card Details                               │
│  └─ Action: Show PaymentFailure Notification           │
│                                                         │
│  Validation Error                                       │
│  ├─ Amount Out of Range                                │
│  ├─ Insufficient Wallet Balance                        │
│  ├─ Energy Amount Invalid                              │
│  ├─ Listing Not Available                              │
│  └─ Action: Show Alert with Suggestion                 │
│                                                         │
│  Backend Error                                          │
│  ├─ Payment Verification Failed                        │
│  ├─ Wallet Update Failed                               │
│  ├─ Transaction Creation Failed                        │
│  └─ Action: Refund Payment, Show Alert                 │
│                                                         │
│  Notification Error                                     │
│  ├─ Permission Denied                                  │
│  ├─ Device Not Supported                               │
│  └─ Action: Silently Fail, Continue                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
              │                    │
              ▼                    ▼
        ┌─────────────┐      ┌────────────┐
        │ Alert User  │      │   Log      │
        │ with Action │      │   Error    │
        └─────────────┘      └────────────┘
```

## Security Layers

```
┌─────────────────────────────────────────────────────────┐
│                 Security Layers                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Layer 1: Client Validation                            │
│  ├─ Amount range check (₹10-₹50,000)                   │
│  ├─ Wallet balance check before payment                │
│  ├─ User authentication check                          │
│  └─ Type validation (TypeScript)                       │
│                                                         │
│  Layer 2: API Security                                 │
│  ├─ HTTPS only (in production)                         │
│  ├─ JWT token in headers                               │
│  ├─ Rate limiting (backend)                            │
│  └─ CORS validation (backend)                          │
│                                                         │
│  Layer 3: Payment Security                             │
│  ├─ Razorpay SDK (PCI Compliant)                       │
│  ├─ No card data on client                             │
│  ├─ Signature verification on backend                  │
│  └─ Order ID validation                                │
│                                                         │
│  Layer 4: Database Security                            │
│  ├─ Transaction locks (prevent double-buy)            │
│  ├─ Row-level locking (FOR UPDATE)                     │
│  ├─ ACID compliance                                    │
│  └─ Audit logging                                      │
│                                                         │
│  Layer 5: Runtime Security                             │
│  ├─ Error handling (no sensitive data in errors)       │
│  ├─ Logging (audit trail)                              │
│  ├─ Permission checks                                  │
│  └─ Session management                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

**This architecture ensures:**
✅ Secure payment processing
✅ Real-time notifications
✅ Reliable data consistency
✅ Scalable design
✅ User-friendly experience
