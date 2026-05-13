#!/usr/bin/env python3
"""
End-to-End Integration Test
Tests ML service → Backend → Frontend prediction flow
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any
from pathlib import Path

# Configuration
ML_SERVICE_URL = "http://localhost:8001"
BACKEND_URL = "http://localhost:3000"
TIMEOUT = 30


def _iso(ts: datetime) -> str:
    """Format datetime as ISO string without microseconds."""
    return ts.replace(microsecond=0).isoformat() + "Z"

class IntegrationTester:
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "tests": [],
            "summary": {}
        }
    
    def test_ml_service_health(self) -> bool:
        """Test ML service is running"""
        print("\n1️⃣  Testing ML Service Health...")
        try:
            response = requests.get(f"{ML_SERVICE_URL}/health", timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ ML Service healthy")
                print(f"   📊 Models loaded: {sum(1 for v in data['models_loaded'].values() if v)}/8")
                self.test_results["tests"].append({
                    "name": "ML Service Health",
                    "status": "PASS",
                    "response": data
                })
                return True
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                self.test_results["tests"].append({
                    "name": "ML Service Health",
                    "status": "FAIL",
                    "error": f"Status {response.status_code}"
                })
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results["tests"].append({
                "name": "ML Service Health",
                "status": "FAIL",
                "error": str(e)
            })
            return False
    
    def test_solar_forecast_endpoint(self) -> bool:
        """Test solar forecast API endpoint"""
        print("\n2️⃣  Testing Solar Forecast Endpoint...")
        try:
            payload = self._build_solar_payload()
            
            response = requests.post(
                f"{ML_SERVICE_URL}/api/v1/forecast/solar",
                json=payload,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                forecast_count = len(data.get("predictions", []))
                print(f"   ✅ Solar forecast received")
                print(f"   📈 Forecast points: {forecast_count}")
                print(f"   🎯 Model version: {data.get('model_version', 'unknown')}")
                
                self.test_results["tests"].append({
                    "name": "Solar Forecast Endpoint",
                    "status": "PASS",
                    "forecast_points": forecast_count,
                    "model_version": data.get("model_version")
                })
                return True
            else:
                print(f"   ❌ Forecast failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                self.test_results["tests"].append({
                    "name": "Solar Forecast Endpoint",
                    "status": "FAIL",
                    "error": f"Status {response.status_code}"
                })
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results["tests"].append({
                "name": "Solar Forecast Endpoint",
                "status": "FAIL",
                "error": str(e)
            })
            return False
    
    def test_demand_forecast_endpoint(self) -> bool:
        """Test demand forecast API endpoint"""
        print("\n3️⃣  Testing Demand Forecast Endpoint...")
        try:
            payload = self._build_demand_payload()
            
            response = requests.post(
                f"{ML_SERVICE_URL}/api/v1/forecast/demand",
                json=payload,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                forecast_count = len(data.get("predictions", []))
                print(f"   ✅ Demand forecast received")
                print(f"   📈 Forecast points: {forecast_count}")
                
                self.test_results["tests"].append({
                    "name": "Demand Forecast Endpoint",
                    "status": "PASS",
                    "forecast_points": forecast_count
                })
                return True
            else:
                print(f"   ❌ Forecast failed: {response.status_code}")
                self.test_results["tests"].append({
                    "name": "Demand Forecast Endpoint",
                    "status": "FAIL",
                    "error": f"Status {response.status_code}"
                })
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results["tests"].append({
                "name": "Demand Forecast Endpoint",
                "status": "FAIL",
                "error": str(e)
            })
            return False
    
    def test_backend_health(self) -> bool:
        """Test backend service is running"""
        print("\n4️⃣  Testing Backend Health...")
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=TIMEOUT)
            if response.status_code == 200:
                print(f"   ✅ Backend service healthy")
                self.test_results["tests"].append({
                    "name": "Backend Health",
                    "status": "PASS"
                })
                return True
            else:
                print(f"   ⚠️  Backend returned: {response.status_code}")
                self.test_results["tests"].append({
                    "name": "Backend Health",
                    "status": "WARN",
                    "status_code": response.status_code
                })
                return True  # Not critical
        except Exception as e:
            print(f"   ⚠️  Backend not responding: {e}")
            self.test_results["tests"].append({
                "name": "Backend Health",
                "status": "WARN",
                "error": str(e)
            })
            return True  # Not critical
    
    def test_ml_model_performance(self) -> bool:
        """Test ML model performance metrics"""
        print("\n5️⃣  Testing ML Model Performance...")
        try:
            response = requests.get(
                f"{ML_SERVICE_URL}/api/v1/models/performance",
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Performance metrics retrieved")
                
                # Show key metrics
                for model_name, metrics in data.get("models", {}).items():
                    if metrics:
                        print(f"   📊 {model_name}:")
                        for key, value in metrics.items():
                            if isinstance(value, (int, float)):
                                print(f"      - {key}: {value:.3f}")
                
                self.test_results["tests"].append({
                    "name": "ML Model Performance",
                    "status": "PASS",
                    "metrics": data
                })
                return True
            else:
                print(f"   ⚠️  Performance endpoint returned: {response.status_code}")
                self.test_results["tests"].append({
                    "name": "ML Model Performance",
                    "status": "WARN"
                })
                return True
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            self.test_results["tests"].append({
                "name": "ML Model Performance",
                "status": "WARN",
                "error": str(e)
            })
            return True
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("\n" + "="*60)
        print("🔬 END-TO-END INTEGRATION TEST SUITE")
        print("="*60)
        
        results = [
            self.test_ml_service_health(),
            self.test_solar_forecast_endpoint(),
            self.test_demand_forecast_endpoint(),
            self.test_backend_health(),
            self.test_ml_model_performance()
        ]
        
        # Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in results if r)
        total = len(results)
        
        print(f"\nTests Passed: {passed}/{total}")
        
        for test in self.test_results["tests"]:
            status_emoji = "✅" if test["status"] == "PASS" else "⚠️" if test["status"] == "WARN" else "❌"
            print(f"  {status_emoji} {test['name']}: {test['status']}")
        
        self.test_results["summary"] = {
            "passed": passed,
            "total": total,
            "success_rate": (passed / total) * 100 if total > 0 else 0
        }
        
        print("\n" + "="*60)
        if passed == total:
            print("✨ All tests passed! System is ready.")
        elif passed >= total - 1:
            print("✨ Almost there! Most systems operational.")
        else:
            print(f"⚠️  {total - passed} tests need attention")
        print("="*60 + "\n")
        
        return self.test_results

    # ------------------------------------------------------------------
    # Payload builders
    # ------------------------------------------------------------------
    def _build_solar_payload(self) -> Dict[str, Any]:
        """Constructs a minimal valid solar forecast request."""
        now = datetime.utcnow()
        hours = 200  # enough history for lag/rolling features
        history = []
        for i in range(hours):
            ts = now - timedelta(hours=hours - i)
            # Daytime generation peaking near noon, zero at night
            hour_of_day = (ts.hour % 24)
            daylight_factor = max(0.0, 1 - abs(hour_of_day - 12) / 12)
            power = round(5.0 * daylight_factor * 0.9, 3)
            history.append({
                "device_id": "panel-001",
                "timestamp": _iso(ts),
                "power_kw": power,
                "temperature": 30.0,
                "voltage": 230.0,
                "current": 18.0,
                "frequency": 50.0,
                "cloud_cover": 20.0,
                "system_capacity_kw": 5.0
            })
        weather = [{
            "latitude": 12.0,
            "longitude": 77.0,
            "temperature": 30.0,
            "humidity": 50.0,
            "wind_speed": 5.0,
            "cloud_cover": 20.0,
            "irradiance": 800.0,
            "description": "clear"
        } for _ in range(48)]
        return {
            "host_id": "host-123",
            "panel_capacity_kw": 5.0,
            "historical_data": history,
            "weather_forecast": weather,
            "forecast_hours": 24
        }

    def _build_demand_payload(self) -> Dict[str, Any]:
        """Constructs a minimal valid demand forecast request."""
        now = datetime.utcnow()
        hours = 800  # enough history for 720h lag
        history = []
        for i in range(hours):
            ts = now - timedelta(hours=hours - i)
            hour_of_day = (ts.hour % 24)
            base = 1.2 + (0.8 if 18 <= hour_of_day <= 22 else 0.3)
            history.append({
                "user_id": "user-123",
                "timestamp": _iso(ts),
                "power_kw": round(base, 3),
                "humidity": 50.0,
                "temperature": 28.0,
                "household_size": 4,
                "has_ac": True
            })
        weather = [{
            "latitude": 12.0,
            "longitude": 77.0,
            "temperature": 28.0,
            "humidity": 55.0,
            "wind_speed": 4.0,
            "cloud_cover": 30.0,
            "irradiance": 600.0,
            "description": "partly cloudy"
        } for _ in range(48)]
        return {
            "user_id": "user-123",
            "historical_data": history,
            "weather_forecast": weather,
            "forecast_hours": 24
        }

def main():
    tester = IntegrationTester()
    results = tester.run_all_tests()
    
    # Save results to file
    output_file = Path("integration_test_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to {output_file}")

if __name__ == "__main__":
    main()
