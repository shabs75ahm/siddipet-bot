#!/usr/bin/env python3
"""
Web dashboard for real-time activity monitoring
"""

import os
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import json

from database import get_activities, get_stats, get_activity
from reporter import ReportGenerator

dashboard = Flask(__name__)
CORS(dashboard)

# HTML template for dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>District Activity Monitor - Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        h1 {
            color: #333;
            margin-bottom: 5px;
        }

        .timestamp {
            color: #666;
            font-size: 14px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .stat-card h3 {
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }

        .stat-card .number {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }

        .stat-card.critical .number {
            color: #ff6b6b;
        }

        .stat-card.warning .number {
            color: #ffa94d;
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .chart-container h3 {
            margin-bottom: 15px;
            color: #333;
        }

        .activity-list {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-top: 20px;
        }

        .activity-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .activity-item:last-child {
            border-bottom: none;
        }

        .activity-info {
            flex: 1;
        }

        .activity-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }

        .activity-meta {
            font-size: 12px;
            color: #666;
        }

        .severity-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }

        .severity-critical {
            background: #ff6b6b;
            color: white;
        }

        .severity-high {
            background: #ffa94d;
            color: white;
        }

        .severity-medium {
            background: #ffd43b;
            color: #333;
        }

        .severity-low {
            background: #51cf66;
            color: white;
        }

        .loading {
            text-align: center;
            padding: 20px;
            color: white;
        }

        .refresh-btn {
            background: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            color: #667eea;
            float: right;
            margin-bottom: 10px;
        }

        .refresh-btn:hover {
            background: #f0f0f0;
        }

        @media (max-width: 768px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }

            .activity-item {
                flex-direction: column;
                align-items: flex-start;
            }

            .severity-badge {
                margin-top: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏘️ District Activity Monitor</h1>
            <p class="timestamp">Last updated: <span id="timestamp">loading...</span></p>
            <button class="refresh-btn" onclick="loadDashboard()">🔄 Refresh</button>
        </header>

        <div class="stats-grid" id="stats-grid">
            <div class="stat-card">
                <h3>Total Activities</h3>
                <div class="number" id="total-activities">--</div>
            </div>
            <div class="stat-card">
                <h3>Incidents</h3>
                <div class="number" id="total-incidents">--</div>
            </div>
            <div class="stat-card critical">
                <h3>Critical</h3>
                <div class="number" id="critical-count">--</div>
            </div>
            <div class="stat-card warning">
                <h3>High Severity</h3>
                <div class="number" id="high-count">--</div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-container">
                <h3>📊 Activities by Category</h3>
                <canvas id="categoryChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>⚠️ Severity Distribution</h3>
                <canvas id="severityChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>📍 Top Active Areas</h3>
                <canvas id="areasChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>📈 24-Hour Trend</h3>
                <canvas id="trendChart"></canvas>
            </div>
        </div>

        <div class="activity-list">
            <h3 style="padding: 20px 20px 0 20px;">📋 Recent Activities</h3>
            <div id="activities-container"></div>
        </div>
    </div>

    <script>
        let charts = {};

        async function loadDashboard() {
            try {
                // Update timestamp
                document.getElementById('timestamp').textContent = new Date().toLocaleTimeString();

                // Fetch stats
                const statsRes = await fetch('/api/v1/stats');
                const statsData = await statsRes.json();

                if (!statsData.success) throw new Error('Failed to load stats');

                const stats = statsData.stats;

                // Update stat cards
                document.getElementById('total-activities').textContent = stats.total_24h;
                document.getElementById('total-incidents').textContent = stats.incidents_24h;
                document.getElementById('critical-count').textContent = stats.severity_24h.critical || 0;
                document.getElementById('high-count').textContent = stats.severity_24h.high || 0;

                // Update charts
                updateCategoryChart(stats.category_breakdown);
                updateSeverityChart(stats.severity_24h);
                updateAreasChart(stats.top_areas);

                // Load recent activities
                const activitiesRes = await fetch('/api/v1/activities?limit=20');
                const activitiesData = await activitiesRes.json();

                if (activitiesData.success) {
                    displayActivities(activitiesData.activities);
                }

            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }

        function updateCategoryChart(data) {
            const ctx = document.getElementById('categoryChart');
            if (!ctx) return;

            const labels = Object.keys(data);
            const values = Object.values(data);

            if (charts.category) {
                charts.category.data.labels = labels;
                charts.category.data.datasets[0].data = values;
                charts.category.update();
            } else {
                charts.category = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: [
                                '#667eea', '#764ba2', '#f093fb', '#4facfe',
                                '#43e97b', '#fa709a', '#feca57', '#ff9ff3'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }
        }

        function updateSeverityChart(data) {
            const ctx = document.getElementById('severityChart');
            if (!ctx) return;

            const labels = ['Critical', 'High', 'Medium', 'Low'];
            const values = [
                data.critical || 0,
                data.high || 0,
                data.medium || 0,
                data.low || 0
            ];

            if (charts.severity) {
                charts.severity.data.datasets[0].data = values;
                charts.severity.update();
            } else {
                charts.severity = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Count',
                            data: values,
                            backgroundColor: ['#ff6b6b', '#ffa94d', '#ffd43b', '#51cf66']
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        plugins: {
                            legend: { display: false }
                        }
                    }
                });
            }
        }

        function updateAreasChart(data) {
            const ctx = document.getElementById('areasChart');
            if (!ctx) return;

            const labels = data.map(a => a[0]).slice(0, 10);
            const values = data.map(a => a[1]).slice(0, 10);

            if (charts.areas) {
                charts.areas.data.labels = labels;
                charts.areas.data.datasets[0].data = values;
                charts.areas.update();
            } else {
                charts.areas = new Chart(ctx, {
                    type: 'horizontalBar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Activities',
                            data: values,
                            backgroundColor: '#667eea'
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        plugins: {
                            legend: { display: false }
                        }
                    }
                });
            }
        }

        function displayActivities(activities) {
            const container = document.getElementById('activities-container');
            container.innerHTML = activities.map(activity => `
                <div class="activity-item">
                    <div class="activity-info">
                        <div class="activity-title">${activity.category.toUpperCase()} - ${activity.location}</div>
                        <div class="activity-meta">
                            ${activity.description.substring(0, 100)}...
                            <br>
                            Reported by: ${activity.reported_by}
                            <br>
                            ${new Date(activity.created_at).toLocaleString()}
                        </div>
                    </div>
                    <span class="severity-badge severity-${activity.severity}">
                        ${activity.severity.toUpperCase()}
                    </span>
                </div>
            `).join('');
        }

        // Load dashboard on page load
        loadDashboard();

        // Auto-refresh every 30 seconds
        setInterval(loadDashboard, 30000);
    </script>
</body>
</html>
"""


@dashboard.route('/')
def index():
    """Dashboard home"""
    return render_template_string(DASHBOARD_TEMPLATE)


@dashboard.route('/api/v1/stats', methods=['GET'])
def stats_endpoint():
    """Stats API endpoint"""
    try:
        hours = request.args.get('hours', 24, type=int)
        stats = get_stats(hours=hours)
        return jsonify({
            'success': True,
            'timestamp': datetime.utcnow().isoformat(),
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard.route('/api/v1/activities', methods=['GET'])
def activities_endpoint():
    """Activities API endpoint"""
    try:
        limit = request.args.get('limit', 50, type=int)
        activities = get_activities(limit=limit)
        return jsonify({
            'success': True,
            'count': len(activities),
            'activities': [a.to_dict() for a in activities]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard.route('/api/v1/report/<int:activity_id>', methods=['GET'])
def activity_report(activity_id: int):
    """Get detailed report for activity"""
    try:
        reporter = ReportGenerator()
        report = reporter.generate_incident_report(activity_id)
        return jsonify({
            'success': True,
            'report': report
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def setup_dashboard():
    """Setup dashboard"""
    return dashboard
