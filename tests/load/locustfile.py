"""
Load Testing Scripts

Locust load tests for HOPE API endpoints.
Tests panic session concurrency and WebSocket performance.

USAGE:
    locust -f tests/load/locustfile.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between, events
from locust.contrib.fasthttp import FastHttpUser
import json
import random


class HopeApiUser(FastHttpUser):
    """
    Simulated HOPE API user.
    
    Focuses on realistic panic session patterns.
    """
    
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    
    def on_start(self):
        """Setup for each simulated user."""
        self.session_id = None
        self.user_id = f"test_user_{random.randint(1000, 9999)}"
    
    @task(10)
    def health_check(self):
        """Health check - most common request."""
        with self.client.get("/health/live", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(5)
    def readiness_check(self):
        """Readiness probe."""
        self.client.get("/health/ready")
    
    @task(3)
    def metrics_endpoint(self):
        """Prometheus metrics scrape."""
        self.client.get("/metrics")
    
    @task(2)
    def start_panic_session(self):
        """Start a panic session."""
        payload = {
            "user_id": self.user_id,
            "initial_message": "I'm feeling really anxious right now",
        }
        
        with self.client.post(
            "/api/v1/session/panic",
            json=payload,
            catch_response=True,
        ) as response:
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    self.session_id = data.get("session_id")
                    response.success()
                except Exception:
                    response.failure("Invalid JSON response")
            elif response.status_code == 429:
                response.failure("Rate limited")
            else:
                response.failure(f"Failed: {response.status_code}")
    
    @task(1)
    def send_panic_message(self):
        """Send message during panic session."""
        if not self.session_id:
            return
        
        messages = [
            "I can't breathe",
            "My heart is racing",
            "I feel like something bad is going to happen",
            "I'm trying to calm down",
            "The breathing is helping a little",
        ]
        
        payload = {
            "session_id": self.session_id,
            "message": random.choice(messages),
        }
        
        self.client.post(
            f"/api/v1/session/{self.session_id}/message",
            json=payload,
        )


class WebSocketUser(HttpUser):
    """
    WebSocket panic session user.
    
    Tests real-time WebSocket connections.
    """
    
    wait_time = between(0.5, 2)
    
    @task
    def websocket_session(self):
        """Simulate WebSocket panic session."""
        # Note: Locust doesn't natively support WebSocket well
        # This is a placeholder for WebSocket testing
        # Use locust-plugins or custom WebSocket client for real tests
        pass


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Log test start."""
    print("Load test starting...")


@events.test_stop.add_listener  
def on_test_stop(environment, **kwargs):
    """Log test completion."""
    print("Load test complete.")
    print(f"Total requests: {environment.stats.total.num_requests}")
    print(f"Failures: {environment.stats.total.num_failures}")
    print(f"Avg response time: {environment.stats.total.avg_response_time:.2f}ms")
