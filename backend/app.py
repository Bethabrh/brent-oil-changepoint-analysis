"""
Flask backend for the Brent Oil Change Point Analysis dashboard.
Serves historical price data, change point model results, and event data.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import csv

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def load_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'r') as f:
        return json.load(f)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "message": "Brent Oil Analysis API is running"})


@app.route('/api/prices', methods=['GET'])
def get_prices():
    """
    Return historical price data.
    Optional query params: start_date, end_date (YYYY-MM-DD format)
    """
    try:
        prices = load_json('prices.json')
    except FileNotFoundError:
        return jsonify({"error": "Price data not found. Run the EDA notebook to generate data/prices.json"}), 404

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date:
        prices = [p for p in prices if p['Date'] >= start_date]
    if end_date:
        prices = [p for p in prices if p['Date'] <= end_date]

    return jsonify({"count": len(prices), "data": prices})


@app.route('/api/changepoints', methods=['GET'])
def get_changepoints():
    """Return Bayesian change point model results (multi-window detection)."""
    try:
        results = load_json('model_results.json')
    except FileNotFoundError:
        return jsonify({"error": "Model results not found. Run notebooks/02_change_point_model.ipynb first"}), 404

    return jsonify(results)


@app.route('/api/events', methods=['GET'])
def get_events():
    """Return the curated events dataset."""
    filepath = os.path.join(DATA_DIR, 'events.csv')

    if not os.path.exists(filepath):
        return jsonify({"error": "Events data not found"}), 404

    events = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append(row)

    return jsonify({"count": len(events), "data": events})


@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Combined summary endpoint for dashboard overview cards."""
    try:
        results = load_json('model_results.json')
        prices = load_json('prices.json')
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    changepoints = results.get('changepoints', [])

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


if __name__ == '__main__':
    app.run(debug=True, port=5001)