/**
 * TESTING GUIDE - Solar Sharing Location & AI/ML Endpoints
 * 
 * Run these tests after starting the backend server
 * Base URL: http://localhost:5000/api/v1/location
 */

// ============================================
// PUBLIC ENDPOINTS (No Authentication Required)
// ============================================

/**
 * 1. GET /nearby-users
 * Find sellers/investors/hosters near a location
 */
const testNearbyUsers = async () => {
  const response = await fetch('http://localhost:5000/api/v1/location/nearby-users?latitude=40.7128&longitude=-74.0060&radius=50&sort=distance&limit=10');
  const data = await response.json();
  console.log('Nearby Users:', data);
  // Expected: Array of users with distance, rating, city (NO raw coordinates)
};

/**
 * 2. GET /nearby-listings
 * Find energy listings near a location
 */
const testNearbyListings = async () => {
  const response = await fetch('http://localhost:5000/api/v1/location/nearby-listings?latitude=40.7128&longitude=-74.0060&sort=price&limit=20');
  const data = await response.json();
  console.log('Nearby Listings:', data);
  // Expected: Array of listings sorted by price
};

/**
 * 3. GET /demand-prediction
 * Get 7-day energy demand forecast with trends
 */
const testDemandPrediction = async () => {
  const response = await fetch('http://localhost:5000/api/v1/location/demand-prediction?latitude=40.7128&longitude=-74.0060&days=7');
  const data = await response.json();
  console.log('Demand Prediction:', data);
  // Expected: Array of 7 daily predictions with trend, confidence, price forecast
};

/**
 * 4. GET /demand-clusters
 * Identify geographic hotspots of energy trading
 */
const testDemandClusters = async () => {
  const response = await fetch('http://localhost:5000/api/v1/location/demand-clusters?limit=10');
  const data = await response.json();
  console.log('Demand Clusters:', data);
  // Expected: Array of 10 geographic clusters with transaction volume, demand level
};

// ============================================
// PROTECTED ENDPOINTS (Require Authentication)
// ============================================

/**
 * 5. GET /seller-reliability/:sellerId
 * Get seller quality metrics and reliability score (0-100)
 */
const testSellerReliability = async (sellerId, authToken) => {
  const response = await fetch(
    `http://localhost:5000/api/v1/location/seller-reliability/${sellerId}`,
    {
      headers: { 'Authorization': `Bearer ${authToken}` }
    }
  );
  const data = await response.json();
  console.log('Seller Reliability:', data);
  // Expected: Reliability score (0-100), completion rate, dispute rate, avg rating
};

/**
 * 6. PUT /update
 * Update user's current location
 */
const testLocationUpdate = async (latitude, longitude, authToken) => {
  const response = await fetch(
    'http://localhost:5000/api/v1/location/update',
    {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ latitude, longitude })
    }
  );
  const data = await response.json();
  console.log('Location Updated:', data);
};

/**
 * 7. POST /optimal-allocation
 * Get AI-driven energy allocation recommendation
 */
const testOptimalAllocation = async (energyNeeded, budget, authToken) => {
  const response = await fetch(
    'http://localhost:5000/api/v1/location/optimal-allocation',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        energy_needed_kwh: energyNeeded,
        budget_per_kwh: budget,
        preferences: {
          prefer_renewable: true,
          listing_type: 'forward'
        }
      })
    }
  );
  const data = await response.json();
  console.log('Optimal Allocation:', data);
  // Expected: Ranked list of listings with composite scores
};

// ============================================
// VALIDATION TESTS
// ============================================

/**
 * Test: Invalid latitude/longitude should be rejected
 */
const testInvalidCoordinates = async () => {
  // Test 1: Latitude > 90
  let response = await fetch('http://localhost:5000/api/v1/location/nearby-users?latitude=95&longitude=-74');
  let data = await response.json();
  console.log('Invalid Lat Test:', data.error); // Should show error
  
  // Test 2: Longitude > 180
  response = await fetch('http://localhost:5000/api/v1/location/nearby-users?latitude=40&longitude=190');
  data = await response.json();
  console.log('Invalid Lng Test:', data.error); // Should show error
  
  // Test 3: Radius > 200km should be capped
  response = await fetch('http://localhost:5000/api/v1/location/nearby-users?latitude=40&longitude=-74&radius=300');
  data = await response.json();
  console.log('Radius Capped Test:', data.search_params.radius_km); // Should be 200
};

/**
 * Test: Limit should be capped at 100
 */
const testLimitCapping = async () => {
  const response = await fetch('http://localhost:5000/api/v1/location/nearby-listings?latitude=40&longitude=-74&limit=500');
  const data = await response.json();
  console.log('Limit Cap Test:', data.search_params.limit); // Should be 100 or less
};

/**
 * Test: Sort options validation
 */
const testSortOptions = async () => {
  // Valid sorts: distance, price, rating
  let tests = [
    { sort: 'distance', endpoint: '/nearby-users' },
    { sort: 'rating', endpoint: '/nearby-users' },
    { sort: 'distance', endpoint: '/nearby-listings' },
    { sort: 'price', endpoint: '/nearby-listings' }
  ];
  
  for (let test of tests) {
    const response = await fetch(
      `http://localhost:5000/api/v1/location${test.endpoint}?latitude=40&longitude=-74&sort=${test.sort}`
    );
    const data = await response.json();
    console.log(`Sort ${test.sort} on ${test.endpoint}:`, data.search_params?.sorted_by || 'OK');
  }
};

// ============================================
// PRIVACY TESTS
// ============================================

/**
 * Test: Verify no raw coordinates in responses
 */
const testPrivacyShaping = async () => {
  const response = await fetch('http://localhost:5000/api/v1/location/nearby-users?latitude=40&longitude=-74&limit=1');
  const data = await response.json();
  
  if (data.data && data.data.length > 0) {
    const user = data.data[0];
    
    // These SHOULD be present (privacy-safe)
    console.log('✓ Has distance_km:', user.distance_km !== undefined);
    console.log('✓ Has city:', user.city !== undefined);
    console.log('✓ Has state:', user.state !== undefined);
    
    // These should NOT be present (privacy-sensitive)
    console.log('✓ No latitude:', user.latitude === undefined);
    console.log('✓ No longitude:', user.longitude === undefined);
    console.log('✓ No email:', user.email === undefined);
    console.log('✓ No address_type:', user.address_type === undefined);
  }
};

// ============================================
// ALGORITHM TESTS
// ============================================

/**
 * Test: Demand prediction trend detection
 */
const testDemandTrends = async () => {
  const response = await fetch('http://localhost:5000/api/v1/location/demand-prediction?latitude=40&longitude=-74');
  const data = await response.json();
  
  if (data.data && data.data.predictions) {
    console.log('Trend Detection Results:');
    data.data.predictions.forEach((pred, i) => {
      console.log(`Day ${i+1}: ${pred.predicted_energy_kwh} kWh, Trend: ${pred.trend}, Confidence: ${pred.confidence}`);
    });
  }
};

/**
 * Test: Seller reliability scoring
 */
const testReliabilityScoring = async (sellerId, authToken) => {
  const response = await fetch(
    `http://localhost:5000/api/v1/location/seller-reliability/${sellerId}`,
    { headers: { 'Authorization': `Bearer ${authToken}` } }
  );
  const data = await response.json();
  
  if (data.data) {
    console.log('Seller Reliability Scoring:');
    console.log(`- Reliability Score: ${data.data.reliability_score}/100`);
    console.log(`- Completion Rate: ${data.data.completion_rate}%`);
    console.log(`- Cancellation Rate: ${data.data.cancellation_rate}%`);
    console.log(`- Avg Rating: ${data.data.avg_rating}/5`);
    console.log(`- Total Transactions: ${data.data.total_transactions}`);
  }
};

/**
 * Test: Demand clustering
 */
const testDemandClustering = async () => {
  const response = await fetch('http://localhost:5000/api/v1/location/demand-clusters?limit=5');
  const data = await response.json();
  
  if (data.data && data.data.clusters) {
    console.log('Demand Clusters (Hotspots):');
    data.data.clusters.forEach((cluster, i) => {
      console.log(`Cluster ${i+1}: ${cluster.location.city}, ${cluster.location.state}`);
      console.log(`  - Demand Level: ${cluster.demand_level}`);
      console.log(`  - Transactions: ${cluster.metrics.transaction_count}`);
      console.log(`  - Total Energy: ${cluster.metrics.total_energy_kwh} kWh`);
      console.log(`  - Avg Price: $${cluster.metrics.avg_price_per_kwh}/kWh`);
      console.log(`  - Buyer/Seller Ratio: ${cluster.metrics.buyer_seller_ratio.toFixed(2)}`);
    });
  }
};

// ============================================
// RUN TESTS
// ============================================

/**
 * Uncomment to run specific tests
 */

// Public endpoint tests
// testNearbyUsers();
// testNearbyListings();
// testDemandPrediction();
// testDemandClusters();

// Validation tests
// testInvalidCoordinates();
// testLimitCapping();
// testSortOptions();

// Privacy tests
// testPrivacyShaping();

// Algorithm tests
// testDemandTrends();

// Protected endpoint tests (need valid authToken)
// const authToken = 'your-jwt-token-here';
// testSellerReliability(42, authToken);
// testReliabilityScoring(42, authToken);
// testDemandClustering();
// testLocationUpdate(40.7128, -74.0060, authToken);
// testOptimalAllocation(500, 5.5, authToken);

console.log('Testing guide ready. Uncomment tests in the file to run them.');

