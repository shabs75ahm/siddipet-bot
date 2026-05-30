#!/usr/bin/env python3
"""
API handler for external data sources
Allows other systems to submit activities via REST API
"""

import os
import logging
from datetime import datetime
from typing import Dict, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
import hmac
import hashlib

from database import add_activity, get_activities, get_stats, get_activity

logger = logging.getLogger(__name__)

# Flask app for API
api_app = Flask(__name__)
CORS(api_app)

# Secret key for request verification
API_SECRET = os.getenv('API_SECRET', 'your-secret-key-change-in-production')


def verify_api_signature(data: bytes, signature: str) -> bool:
    """Verify API request signature"""
    expected_sig = hmac.new(
        API_SECRET.encode(),
        data,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_sig, signature)


@api_app.route('/api/v1/activity', methods=['POST'])
def create_activity():
    """API endpoint to create activity"""
    try:
        # Verify signature if provided
        signature = request.headers.get('X-Signature')
        if signature:
            if not verify_api_signature(request.data, signature):
                return jsonify({'error': 'Invalid signature'}), 401

        data = request.get_json()

        # Validate required fields
        required = ['category', 'description', 'location']
        if not all(field in data for field in required):
            return jsonify({
                'error': 'Missing required fields',
                'required': required
            }), 400

        # Create activity
        activity = add_activity(
            category=data.get('category'),
            description=data.get('description'),
            location=data.get('location'),
            severity=data.get('severity', 'low'),
            reported_by=data.get('reported_by', 'API'),
            reporter_id=data.get('reporter_id', 0),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )

        logger.info(f"Activity created via API: {activity.id}")

        return jsonify({
            'success': True,
            'activity_id': activity.id,
            'timestamp': activity.created_at.isoformat()
        }), 201

    except Exception as e:
        logger.error(f"Error creating activity: {e}")
        return jsonify({'error': str(e)}), 500


@api_app.route('/api/v1/activities', methods=['GET'])
def list_activities():
    """API endpoint to list activities"""
    try:
        limit = request.args.get('limit', 50, type=int)
        category = request.args.get('category', type=str)
        location = request.args.get('location', type=str)
        hours = request.args.get('hours', 24, type=int)
        severity = request.args.get('severity', type=str)

        activities = get_activities(
            limit=limit,
            category=category,
            location=location,
            hours=hours,
            severity=severity
        )

        return jsonify({
            'success': True,
            'count': len(activities),
            'activities': [a.to_dict() for a in activities]
        }), 200

    except Exception as e:
        logger.error(f"Error listing activities: {e}")
        return jsonify({'error': str(e)}), 500


@api_app.route('/api/v1/activity/<int:activity_id>', methods=['GET'])
def get_activity_detail(activity_id: int):
    """Get single activity details"""
    try:
        from database import get_activity as db_get_activity
        activity = db_get_activity(activity_id)

        if not activity:
            return jsonify({'error': 'Activity not found'}), 404

        return jsonify({
            'success': True,
            'activity': activity.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error getting activity: {e}")
        return jsonify({'error': str(e)}), 500


@api_app.route('/api/v1/stats', methods=['GET'])
def get_stats_endpoint():
    """Get district statistics"""
    try:
        hours = request.args.get('hours', 24, type=int)
        stats = get_stats(hours=hours)

        return jsonify({
            'success': True,
            'timestamp': datetime.utcnow().isoformat(),
            'stats': stats
        }), 200

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500


@api_app.route('/api/v1/activity/<int:activity_id>/update', methods=['POST'])
def update_activity_status(activity_id: int):
    """Update activity status"""
    try:
        # Verify signature
        signature = request.headers.get('X-Signature')
        if signature:
            if not verify_api_signature(request.data, signature):
                return jsonify({'error': 'Invalid signature'}), 401

        data = request.get_json()
        status = data.get('status')

        if not status:
            return jsonify({'error': 'Status field required'}), 400

        from database import update_activity
        update_activity(activity_id, status, updated_by=data.get('updated_by', 'API'))

        return jsonify({
            'success': True,
            'activity_id': activity_id,
            'status': status
        }), 200

    except Exception as e:
        logger.error(f"Error updating activity: {e}")
        return jsonify({'error': str(e)}), 500


@api_app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# Webhook for external systems
@api_app.route('/api/v1/webhook/traffic', methods=['POST'])
def traffic_webhook():
    """Webhook for traffic data"""
    try:
        data = request.get_json()

        activity = add_activity(
            category='traffic',
            description=data.get('description', 'Traffic update'),
            location=data.get('location', 'Unknown'),
            severity=data.get('severity', 'low'),
            reported_by='Traffic System',
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )

        return jsonify({'success': True, 'activity_id': activity.id}), 201

    except Exception as e:
        logger.error(f"Error processing traffic webhook: {e}")
        return jsonify({'error': str(e)}), 500


@api_app.route('/api/v1/webhook/weather', methods=['POST'])
def weather_webhook():
    """Webhook for weather alerts"""
    try:
        data = request.get_json()

        activity = add_activity(
            category='weather',
            description=data.get('description', 'Weather alert'),
            location=data.get('location', 'District-wide'),
            severity=data.get('severity', 'medium'),
            reported_by='Weather Service',
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )

        return jsonify({'success': True, 'activity_id': activity.id}), 201

    except Exception as e:
        logger.error(f"Error processing weather webhook: {e}")
        return jsonify({'error': str(e)}), 500


@api_app.route('/api/v1/webhook/incident', methods=['POST'])
def incident_webhook():
    """Webhook for incident reports from emergency systems"""
    try:
        data = request.get_json()

        activity = add_activity(
            category=data.get('category', 'incident'),
            description=data.get('description', 'Incident report'),
            location=data.get('location', 'Unknown'),
            severity=data.get('severity', 'high'),
            reported_by='Emergency System',
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )

        return jsonify({'success': True, 'activity_id': activity.id}), 201

    except Exception as e:
        logger.error(f"Error processing incident webhook: {e}")
        return jsonify({'error': str(e)}), 500


@api_app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@api_app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


def setup_external_api():
    """Setup external API"""
    logger.info("External API endpoints initialized")
    return api_app
