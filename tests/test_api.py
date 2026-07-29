"""
Integration tests for the Flask API (backend/app.py).
Run with: pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# ---------- /api/health ----------

class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200

    def test_health_returns_ok_status(self, client):
        response = client.get('/api/health')
        data = response.get_json()
        assert data['status'] == 'ok'


# ---------- /api/prices ----------

class TestPricesEndpoint:
    def test_prices_returns_200(self, client):
        response = client.get('/api/prices')
        assert response.status_code == 200

    def test_prices_returns_data_list(self, client):
        response = client.get('/api/prices')
        data = response.get_json()
        assert 'data' in data
        assert 'count' in data
        assert isinstance(data['data'], list)
        assert data['count'] > 0

    def test_prices_records_have_expected_keys(self, client):
        response = client.get('/api/prices')
        data = response.get_json()
        first_record = data['data'][0]
        assert 'Date' in first_record
        assert 'Price' in first_record

    def test_prices_date_filter_start_date(self, client):
        response = client.get('/api/prices?start_date=2020-01-01')
        data = response.get_json()
        for record in data['data']:
            assert record['Date'] >= '2020-01-01'

    def test_prices_date_filter_end_date(self, client):
        response = client.get('/api/prices?end_date=2000-01-01')
        data = response.get_json()
        for record in data['data']:
            assert record['Date'] <= '2000-01-01'

    def test_prices_date_range_filter(self, client):
        response = client.get('/api/prices?start_date=2020-01-01&end_date=2020-12-31')
        data = response.get_json()
        for record in data['data']:
            assert '2020-01-01' <= record['Date'] <= '2020-12-31'


# ---------- /api/changepoints ----------

class TestChangepointsEndpoint:
    def test_changepoints_returns_200(self, client):
        response = client.get('/api/changepoints')
        assert response.status_code == 200

    def test_changepoints_returns_expected_structure(self, client):
        response = client.get('/api/changepoints')
        data = response.get_json()
        assert 'changepoints' in data
        assert len(data['changepoints']) == 5

    def test_changepoint_records_have_expected_keys(self, client):
        response = client.get('/api/changepoints')
        data = response.get_json()
        cp = data['changepoints'][0]
        for key in ['label', 'detected_date', 'matched_event', 'price_before', 'price_after', 'pct_change']:
            assert key in cp


# ---------- /api/events ----------

class TestEventsEndpoint:
    def test_events_returns_200(self, client):
        response = client.get('/api/events')
        assert response.status_code == 200

    def test_events_returns_16_events(self, client):
        response = client.get('/api/events')
        data = response.get_json()
        assert data['count'] == 16

    def test_event_records_have_expected_keys(self, client):
        response = client.get('/api/events')
        data = response.get_json()
        event = data['data'][0]
        assert 'Event_Name' in event
        assert 'Event_Date' in event
        assert 'Category' in event


# ---------- /api/summary ----------

class TestSummaryEndpoint:
    def test_summary_returns_200(self, client):
        response = client.get('/api/summary')
        assert response.status_code == 200

    def test_summary_has_expected_keys(self, client):
        response = client.get('/api/summary')
        data = response.get_json()
        for key in ['date_range', 'total_observations', 'total_changepoints_detected']:
            assert key in data

    def test_summary_date_range_matches_brief(self, client):
        response = client.get('/api/summary')
        data = response.get_json()
        assert data['date_range']['start'] == '1987-05-21'
        assert data['date_range']['end'] == '2022-09-30'
        class TestReliabilityEndpoint:
    def test_reliability_returns_200(self, client):
        response = client.get('/api/reliability')
        assert response.status_code == 200

    def test_reliability_has_data_for_all_changepoints(self, client):
        response = client.get('/api/reliability')
        data = response.get_json()
        assert len(data['data']) == 5

    def test_reliability_contains_rhat(self, client):
        response = client.get('/api/reliability')
        data = response.get_json()
        assert 'r_hat_max' in data['data'][0]['reliability']