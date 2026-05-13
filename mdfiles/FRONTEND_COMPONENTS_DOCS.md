# Frontend Components - Complete Documentation

## 4 New React Native Components Implemented ✅

### 1. **NearbyUsersListItem** - Individual Seller Card
**Location:** `/frontend/src/components/cards/NearbyUsersListItem.tsx`

Display a single seller/investor/hoster in a list with key information.

#### Features
- ✅ Profile avatar with role badge and KYC status
- ✅ User name, location, and role
- ✅ Star rating with transaction count
- ✅ Distance indicator with color coding
- ✅ Active listings count
- ✅ Available energy display (kWh/MWh)
- ✅ View Profile button
- ✅ Quick details footer

#### Props
```typescript
interface NearbyUsersListItemProps {
  user: NearbyUserListItem;      // User data
  onPress: (user) => void;        // Selection handler
  onViewProfile: (userId) => void; // Profile navigation
}
```

#### Usage Example
```tsx
import { FlatList } from 'react-native';
import NearbyUsersListItem from './components/cards/NearbyUsersListItem';

<FlatList
  data={users}
  renderItem={({ item }) => (
    <NearbyUsersListItem
      user={item}
      onPress={(user) => setSelectedUser(user)}
      onViewProfile={(id) => navigation.navigate('Profile', { userId: id })}
    />
  )}
  keyExtractor={(item) => item.id}
/>
```

#### Styling Highlights
- Responsive design (works on all screen sizes)
- Distance color coding: Green (<5km) → Blue (5-15km) → Amber (15-50km) → Red (>50km)
- Rating color based on score
- Professional card layout with shadows and borders

---

### 2. **SellerReliabilityCard** - Seller Quality Metrics
**Location:** `/frontend/src/components/cards/SellerReliabilityCard.tsx`

Display comprehensive seller reliability assessment with 0-100 score.

#### Features
- ✅ Reliability score (0-100) with color-coded circle
- ✅ Score label (Excellent/Good/Fair)
- ✅ Completion rate (% of successful transactions)
- ✅ Cancellation rate (% of cancelled orders)
- ✅ Dispute rate (% of disputed transactions)
- ✅ Average rating (out of 5)
- ✅ Avg completion hours
- ✅ Total transactions & platform tenure
- ✅ Overall reliability progress bar

#### Props
```typescript
interface SellerReliabilityCardProps {
  sellerId: number;        // Seller ID (required)
  authToken: string;       // Auth token (required)
  onPress?: () => void;    // Optional press handler
}
```

#### Scoring Formula
```
reliability_score = 
  completion_rate × 0.60 +          // 60% weight
  (100 - cancellation_rate × 5) × 0.20 +  // 20% weight
  (avg_rating / 5 × 100) × 0.20    // 20% weight
```

#### Usage Example
```tsx
import SellerReliabilityCard from './components/cards/SellerReliabilityCard';

<SellerReliabilityCard
  sellerId={user.id}
  authToken={authToken}
  onPress={() => {
    // Handle card press
    navigation.navigate('SellerDetails', { sellerId: user.id });
  }}
/>
```

#### API Integration
- Fetches from: `GET /api/v1/location/seller-reliability/:sellerId`
- Response includes: reliability_score, completion_rate, cancellation_rate, dispute_rate, avg_completion_hours, avg_rating, total_transactions, tenure_months

#### Scoring Interpretation
- **Excellent (85+)**: Highly trustworthy, buy with confidence
- **Good (70-84)**: Reliable, normal expectations
- **Fair (<70)**: Use caution, many cancellations/disputes

---

### 3. **DemandPredictionChart** - 7-Day Forecast
**Location:** `/frontend/src/components/charts/DemandPredictionChart.tsx`

Interactive 7-day energy demand forecast with trends and confidence indicators.

#### Features
- ✅ Bar chart showing daily predictions
- ✅ Trend indicators (↑ increasing, ↔ stable, ↓ decreasing)
- ✅ Confidence badges (High/Medium/Low)
- ✅ Daily energy values in kWh
- ✅ Price forecasts per day
- ✅ Summary statistics (avg, std dev, price range)
- ✅ Peak & lowest demand insights
- ✅ Model info & methodology

#### Props
```typescript
interface DemandPredictionChartProps {
  latitude: number;    // Location latitude (required)
  longitude: number;   // Location longitude (required)
  days?: number;       // Forecast days (optional, default: 7)
}
```

#### API Integration
- Fetches from: `GET /api/v1/location/demand-prediction`
- Response includes: predictions array with trends, confidence, price_forecast

#### Chart Interpretation
- **Bar Height**: Represents predicted energy demand
- **Color Coding**: Green (increasing) → Blue (stable) → Red (decreasing)
- **Badges**: Show confidence level of prediction (High/Medium/Low)
- **Price**: Shows expected price per kWh for that day

#### Usage Example
```tsx
import DemandPredictionChart from './components/charts/DemandPredictionChart';

<DemandPredictionChart
  latitude={currentLocation.latitude}
  longitude={currentLocation.longitude}
  days={7}
/>
```

#### Insights Shown
- Peak demand day with forecast energy
- Lowest demand day
- Data quality (data points analyzed)
- Day-by-day: energy (kWh), price ($/kWh), trend, confidence

---

### 4. **DemandClusterMap** - Geographic Hotspots
**Location:** `/frontend/src/components/common/DemandClusterMap.tsx`

Visual representation of energy trading hotspots by geographic location.

#### Features
- ✅ Geographic clusters (~11km grid cells)
- ✅ Demand level classification (Very High/High/Medium/Low)
- ✅ Transaction volume per cluster
- ✅ Total energy traded per cluster
- ✅ Average price per cluster
- ✅ Buyer/seller count & ratio
- ✅ Investment potential indicator
- ✅ Cluster ranking (1-10)
- ✅ Summary statistics
- ✅ Market insights

#### Props
```typescript
interface DemandClusterMapProps {
  limit?: number;                              // Max clusters (default: 10)
  onClusterSelect?: (cluster: Cluster) => void; // Selection handler
}
```

#### Cluster Data Includes
```typescript
- id: Cluster identifier
- location: {
    approx_latitude: number
    approx_longitude: number
    city: string
    state: string
    region: string
  }
- metrics: {
    transaction_count: number
    total_energy_kwh: number
    avg_price_per_kwh: number
    unique_buyers: number
    unique_sellers: number
    buyer_seller_ratio: number
  }
- demand_level: 'very_high' | 'high' | 'medium' | 'low'
- investment_potential: 'high' | 'medium' | 'low'
```

#### Color Coding
- 🔴 **Very High**: 20+ transactions, red zone
- 🟠 **High**: 10-19 transactions, orange zone
- 🔵 **Medium**: 5-9 transactions, blue zone
- ⚪ **Low**: <5 transactions, gray zone

#### Usage Example
```tsx
import DemandClusterMap from './components/common/DemandClusterMap';

<DemandClusterMap
  limit={10}
  onClusterSelect={(cluster) => {
    console.log('Selected:', cluster.location.city);
    // Navigate to cluster details
    navigation.navigate('ClusterDetails', { cluster });
  }}
/>
```

#### API Integration
- Fetches from: `GET /api/v1/location/demand-clusters?limit=10`
- Response includes: clusters array, summary stats

#### Analytics
- Shows investment hotspots for expansion
- Identifies buyer/seller imbalances
- Highlights emerging markets
- Activity level indicators per cluster

---

## Integration Example

### Complete Dashboard Screen
```tsx
import React, { useState } from 'react';
import { View, FlatList, TouchableOpacity, Text } from 'react-native';
import {
  NearbyUsersListItem,
  SellerReliabilityCard,
  DemandPredictionChart,
  DemandClusterMap,
} from './components/index';

export const LocationDashboardScreen = () => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [activeTab, setActiveTab] = useState('nearby');

  return (
    <View style={{ flex: 1 }}>
      {/* Tab Navigation */}
      <View style={{ flexDirection: 'row' }}>
        <TouchableOpacity onPress={() => setActiveTab('nearby')}>
          <Text>Nearby</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => setActiveTab('forecast')}>
          <Text>Forecast</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => setActiveTab('hotspots')}>
          <Text>Hotspots</Text>
        </TouchableOpacity>
      </View>

      {/* Nearby Users Tab */}
      {activeTab === 'nearby' && (
        <FlatList
          data={users}
          renderItem={({ item }) => (
            <NearbyUsersListItem
              user={item}
              onPress={setSelectedUser}
              onViewProfile={(id) => navigation.navigate('Profile', { userId: id })}
            />
          )}
          keyExtractor={(item) => item.id}
        />
      )}

      {/* Forecast Tab */}
      {activeTab === 'forecast' && (
        <DemandPredictionChart
          latitude={40.7128}
          longitude={-74.0060}
          days={7}
        />
      )}

      {/* Hotspots Tab */}
      {activeTab === 'hotspots' && (
        <DemandClusterMap
          limit={10}
          onClusterSelect={(cluster) => {
            console.log('Selected cluster:', cluster);
          }}
        />
      )}

      {/* Selected User Detail */}
      {selectedUser && (
        <SellerReliabilityCard
          sellerId={parseInt(selectedUser.id)}
          authToken={authToken}
        />
      )}
    </View>
  );
};
```

---

## Import Usage

### Option 1: From Index (Recommended)
```tsx
import {
  NearbyUsersListItem,
  SellerReliabilityCard,
  DemandPredictionChart,
  DemandClusterMap,
} from '../components/index';
```

### Option 2: Direct Imports
```tsx
import NearbyUsersListItem from '../components/cards/NearbyUsersListItem';
import SellerReliabilityCard from '../components/cards/SellerReliabilityCard';
import DemandPredictionChart from '../components/charts/DemandPredictionChart';
import DemandClusterMap from '../components/common/DemandClusterMap';
```

---

## API Endpoints Used

All components connect to these backend endpoints:

### Public Endpoints (No Auth)
- `GET /api/v1/location/nearby-users` - Gets nearby users
- `GET /api/v1/location/demand-prediction` - Gets 7-day forecast
- `GET /api/v1/location/demand-clusters` - Gets geographic hotspots

### Protected Endpoints (Require Auth Token)
- `GET /api/v1/location/seller-reliability/:sellerId` - Gets seller score

---

## Styling & Customization

All components use React Native StyleSheet for consistent, performant styling:

- **Colors**: Follow Material Design (blue primary, green success, red alert)
- **Spacing**: 4px base unit (4, 8, 12, 16, 24 px)
- **Typography**: 11-20px font sizes, 600-700 fontWeight for emphasis
- **Shadows**: iOS-style shadows with elevation for Android
- **Borders**: Soft grays (#e5e7eb) for dividers

### Overriding Styles
All styles are defined in StyleSheet.create() within each component. To customize:

```tsx
// Create a themed variant by wrapping
const ThemedNearbyUsersListItem = (props) => (
  <View style={{ backgroundColor: '#f0f0f0' }}>
    <NearbyUsersListItem {...props} />
  </View>
);
```

---

## Error Handling

All components include:
- ✅ Loading states with ActivityIndicator
- ✅ Error states with user-friendly messages
- ✅ Network error handling
- ✅ Empty state handling
- ✅ Graceful fallbacks

---

## Performance Optimizations

- ✅ Lazy loading of data
- ✅ Memoization of expensive operations
- ✅ Optimized re-renders
- ✅ Efficient FlatList usage
- ✅ Image optimization

---

## Testing

### Unit Tests Needed
```
- NearbyUsersListItem rendering with various user data
- SellerReliabilityCard score calculation
- DemandPredictionChart trend detection
- DemandClusterMap clustering logic
```

### Integration Tests Needed
```
- API fetching from all components
- Navigation from list items
- Error handling and retries
- Loading states
```

---

## Next Steps

1. ✅ **Components Created** - All 4 components implemented
2. ⏳ **Integration** - Wire up to real screens
3. ⏳ **Testing** - Write unit and integration tests
4. ⏳ **Styling** - Fine-tune colors and spacing
5. ⏳ **Performance** - Optimize with real data
6. ⏳ **Analytics** - Track component usage

---

## File Locations

| Component | Path |
|-----------|------|
| NearbyUsersListItem | `frontend/src/components/cards/NearbyUsersListItem.tsx` |
| SellerReliabilityCard | `frontend/src/components/cards/SellerReliabilityCard.tsx` |
| DemandPredictionChart | `frontend/src/components/charts/DemandPredictionChart.tsx` |
| DemandClusterMap | `frontend/src/components/common/DemandClusterMap.tsx` |
| Index | `frontend/src/components/index.ts` |
| Integration Guide | `frontend/COMPONENT_INTEGRATION_GUIDE.ts` |

---

**Status:** ✅ All 4 components implemented and ready for integration
**Created:** January 16, 2026
**Framework:** React Native (Expo)
**TypeScript:** Full type support

