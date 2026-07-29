"""
Flask backend for the Brent Oil Change Point Analysis dashboard.
Serves historical price data, change point model results, and event data.
"""

from typing import Any, Dict, List, Optional
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import json
import os
import csv

app: Flask = Flask(__name__)
CORS(app)

DATA_DIR: str = os.path.join(os.path.dirname(__file__), '..', 'data')


def load_json(filename: str) -> Any:
    filepath: str = os.path.join(DATA_DIR, filename)
    with open(filepath, 'r') as f:
        return json.load(f)


@app.route('/api/health', methods=['GET'])
def health_check() -> Response:
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "message": "Brent Oil Analysis API is running"})


@app.route('/api/prices', methods=['GET'])
def get_prices() -> Response:
    """
    Return historical price data.
    Optional query params: start_date, end_date (YYYY-MM-DD format)
    """
    try:
        prices: List[Dict[str, Any]] = load_json('prices.json')
    except FileNotFoundError:
        return jsonify({"error": "Price data not found. Run the EDA notebook to generate data/prices.json"}), 404

    start_date: Optional[str] = request.args.get('start_date')
    end_date: Optional[str] = request.args.get('end_date')

    if start_date:
        prices = [p for p in prices if p['Date'] >= start_date]
    if end_date:
        prices = [p for p in prices if p['Date'] <= end_date]

    return jsonify({"count": len(prices), "data": prices})


@app.route('/api/changepoints', methods=['GET'])
def get_changepoints() -> Response:
    """Return Bayesian change point model results (multi-window detection)."""
    try:
        results: Dict[str, Any] = load_json('model_results.json')
    except FileNotFoundError:
        return jsonify({"error": "Model results not found. Run notebooks/02_change_point_model.ipynb first"}), 404

    return jsonify(results)


@app.route('/api/events', methods=['GET'])
def get_events() -> Response:
    """Return the curated events dataset."""
    filepath: str = os.path.join(DATA_DIR, 'events.csv')

    if not os.path.exists(filepath):
        return jsonify({"error": "Events data not found"}), 404

    events: List[Dict[str, str]] = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append(row)

    return jsonify({"count": len(events), "data": events})


@app.route('/api/summary', methods=['GET'])
def get_summary() -> Response:
    """Combined summary endpoint for dashboard overview cards."""
    try:
        results: Dict[str, Any] = load_json('model_results.json')
        prices: List[Dict[str, Any]] = load_json('prices.json')
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    changepoints: List[Dict[str, Any]] = results.get('changepoints', [])

    return jsonify({
        "date_range": {
            "start": prices[0]['Date'] if prices else None,
            "end": prices[-1]['Date'] if prices else None,
        },
        "total_observations": len(prices),
        "total_changepoints_detected": len(changepoints),
        "changepoints_summary": [
            {
                "event": cp["matched_event"],
                "detected_date": cp["detected_date"],
                "pct_change": cp["pct_change"]
            }
            for cp in changepoints
        ]
    })

@app.route('/api/reliability', methods=['GET'])
def get_reliability() -> Response:
    """Return convergence diagnostics (r-hat, ESS) for each detected change point."""
    try:
        results: Dict[str, Any] = load_json('model_results.json')
    except FileNotFoundError:
        return jsonify({"error": "Model results not found"}), 404

    changepoints: List[Dict[str, Any]] = results.get('changepoints', [])

    reliability_data = [
        {
            "label": cp["label"],
            "detected_date": cp["detected_date"],
            "reliability": cp.get("reliability", {})
        }
        for cp in changepoints
    ]

    return jsonify({"data": reliability_data})
if __name__ == '__main__':
    app.run(debug=True, port=5001)