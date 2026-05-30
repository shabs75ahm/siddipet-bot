#!/usr/bin/env python3
"""
Report generation for district activities
Hourly summaries and daily digests
"""

from datetime import datetime, timedelta
from typing import List
import logging

from database import get_activities, get_stats, Activity

logger = logging.getLogger(__name__)

ACTIVITY_EMOJIS = {
    'incident': '🚨',
    'event': '🎉',
    'announcement': '📢',
    'traffic': '🚗',
    'service': '🔧',
    'emergency': '🆘',
    'weather': '🌤️',
    'other': '📌'
}

SEVERITY_EMOJIS = {
    'low': '🟢',
    'medium': '🟡',
    'high': '🔴',
    'critical': '⛔'
}


class ReportGenerator:
    """Generate reports and summaries"""

    def generate_hourly_report(self) -> str:
        """Generate hourly activity report"""
        activities = get_activities(limit=50, hours=1)
        stats = get_stats(hours=1)

        if not activities:
            return "📊 **Hourly Report** - No new activities in the past hour."

        report = f"📊 **Hourly Activity Report**\n"
        report += f"⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC\n"
        report += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        # Summary stats
        report += f"**Summary:**\n"
        report += f"• Total Activities: {stats.get('total_24h', 0)}\n"

        # Category breakdown
        categories = stats.get('category_breakdown', {})
        if categories:
            report += f"\n**By Category:**\n"
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                emoji = ACTIVITY_EMOJIS.get(cat, '📌')
                report += f"  {emoji} {cat.title()}: {count}\n"

        # Critical/High severity
        critical_high = [a for a in activities if a.severity in ['critical', 'high']]
        if critical_high:
            report += f"\n🔴 **Critical/High Severity ({len(critical_high)}):**\n"
            for activity in critical_high[:5]:
                emoji = SEVERITY_EMOJIS.get(activity.severity)
                report += f"  {emoji} {activity.category.title()} @ {activity.location}\n"
                report += f"     {activity.description[:80]}...\n"

        # Top locations
        top_areas = stats.get('top_areas', [])
        if top_areas:
            report += f"\n📍 **Most Active Areas:**\n"
            for area, count in top_areas[:5]:
                report += f"  • {area}: {count} activities\n"

        report += f"\n💡 Use `/recent` to see all activities or visit the dashboard for details."

        return report

    def generate_daily_summary(self) -> str:
        """Generate daily activity summary"""
        activities = get_activities(limit=100, hours=24)
        stats = get_stats(hours=24)

        report = f"📋 **Daily Activity Summary**\n"
        report += f"📅 {datetime.utcnow().strftime('%Y-%m-%d')} UTC\n"
        report += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        # Overall stats
        total = stats.get('total_24h', 0)
        report += f"**Overview:**\n"
        report += f"• Total Activities: {total}\n"
        report += f"• Incidents: {stats.get('incidents_24h', 0)}\n"
        report += f"• Events: {stats.get('events_24h', 0)}\n"
        report += f"• Emergencies: {stats.get('emergencies_24h', 0)}\n"

        # Category distribution
        categories = stats.get('category_breakdown', {})
        if categories:
            report += f"\n**Activity Distribution:**\n"
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                emoji = ACTIVITY_EMOJIS.get(cat, '📌')
                percentage = (count / total * 100) if total > 0 else 0
                bar = '█' * int(percentage / 5) + '░' * (20 - int(percentage / 5))
                report += f"  {emoji} {cat.title():12} {bar} {percentage:5.1f}% ({count})\n"

        # Severity breakdown
        severity = stats.get('severity_24h', {})
        if severity:
            report += f"\n**By Severity:**\n"
            for sev, count in sorted(severity.items(), key=lambda x: x[1], reverse=True):
                emoji = SEVERITY_EMOJIS.get(sev)
                report += f"  {emoji} {sev.title()}: {count}\n"

        # Critical incidents
        critical = [a for a in activities if a.severity == 'critical']
        if critical:
            report += f"\n⛔ **Critical Incidents ({len(critical)}):**\n"
            for activity in critical[:3]:
                report += f"  • {activity.category.title()} @ {activity.location}\n"
                report += f"    {activity.description[:75]}...\n"
                report += f"    Reported by: {activity.reported_by}\n"

        # Top active areas
        top_areas = stats.get('top_areas', [])
        if top_areas:
            report += f"\n🗺️ **Top 5 Most Active Areas:**\n"
            for i, (area, count) in enumerate(top_areas[:5], 1):
                report += f"  {i}. {area}: {count} activities\n"

        # Trending activity types
        trending = self._get_trending_categories(stats.get('category_breakdown', {}))
        if trending:
            report += f"\n📈 **Trending Categories:**\n"
            for cat, count in trending[:3]:
                report += f"  • {cat.title()}: ↑ {count} today\n"

        # Recommendations
        report += f"\n💡 **Insights:**\n"
        if stats.get('critical_week', 0) > 5:
            report += f"  ⚠️ High critical incident rate this week\n"
        if len(top_areas) > 0:
            report += f"  📍 Focus on {top_areas[0][0]} for maximum impact\n"
        report += f"  📊 View detailed analytics at: [Dashboard URL]\n"

        return report

    def generate_location_report(self, location: str) -> str:
        """Generate report for specific location"""
        activities = get_activities(location=location, limit=50, hours=24)

        if not activities:
            return f"📍 No recent activities in {location}"

        report = f"📍 **Activity Report: {location}**\n"
        report += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        report += f"📊 **Statistics:**\n"
        report += f"• Total Activities (24h): {len(activities)}\n"

        # Category breakdown
        categories = {}
        severities = {}
        for activity in activities:
            categories[activity.category] = categories.get(activity.category, 0) + 1
            severities[activity.severity] = severities.get(activity.severity, 0) + 1

        report += f"\n**Categories:**\n"
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            emoji = ACTIVITY_EMOJIS.get(cat, '📌')
            report += f"  {emoji} {cat.title()}: {count}\n"

        report += f"\n**Severity Distribution:**\n"
        for sev, count in sorted(severities.items(), key=lambda x: x[1], reverse=True):
            emoji = SEVERITY_EMOJIS.get(sev)
            report += f"  {emoji} {sev.title()}: {count}\n"

        # Recent incidents
        critical_high = [a for a in activities if a.severity in ['critical', 'high']]
        if critical_high:
            report += f"\n🔴 **Critical/High Incidents:**\n"
            for activity in critical_high[:5]:
                emoji = SEVERITY_EMOJIS.get(activity.severity)
                time_ago = self._time_ago(activity.created_at)
                report += f"  {emoji} {activity.category.title()} - {time_ago} ago\n"
                report += f"     {activity.description[:70]}...\n"

        # Recent activities
        report += f"\n📋 **Recent Activities:**\n"
        for activity in activities[:5]:
            emoji = ACTIVITY_EMOJIS.get(activity.category)
            time_ago = self._time_ago(activity.created_at)
            report += f"  {emoji} {activity.category.title()} - {time_ago} ago\n"
            report += f"     {activity.description[:70]}...\n"

        return report

    def generate_incident_report(self, activity_id: int) -> str:
        """Generate detailed incident report"""
        from database import get_activity, get_updates

        activity = get_activity(activity_id)
        if not activity:
            return "❌ Activity not found"

        updates = get_updates(activity_id)

        report = f"🔍 **Incident Details**\n"
        report += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        emoji = ACTIVITY_EMOJIS.get(activity.category)
        severity_emoji = SEVERITY_EMOJIS.get(activity.severity)

        report += f"**Type:** {emoji} {activity.category.title()}\n"
        report += f"**Severity:** {severity_emoji} {activity.severity.title()}\n"
        report += f"**Location:** 📍 {activity.location}\n"
        report += f"**Status:** {activity.status.upper()}\n"
        report += f"**Reported by:** {activity.reported_by}\n"
        report += f"**Time:** ⏰ {activity.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"

        report += f"**Description:**\n"
        report += f"{activity.description}\n\n"

        if activity.latitude and activity.longitude:
            report += f"**Location Coordinates:**\n"
            report += f"Latitude: {activity.latitude}\n"
            report += f"Longitude: {activity.longitude}\n\n"

        if updates:
            report += f"**Updates ({len(updates)}):**\n"
            for update in updates[:10]:
                time_ago = self._time_ago(update.created_at)
                report += f"  • {update.updated_by} ({time_ago} ago):\n"
                report += f"    {update.update_text}\n"
        else:
            report += f"**No updates yet.**\n"

        report += f"\n**Engagement:** {activity.view_count} views\n"

        return report

    @staticmethod
    def _time_ago(dt: datetime) -> str:
        """Format time ago"""
        now = datetime.utcnow()
        diff = now - dt

        if diff.seconds < 60:
            return f"{diff.seconds}s"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60}m"
        elif diff.days == 0:
            return f"{diff.seconds // 3600}h"
        elif diff.days < 7:
            return f"{diff.days}d"
        else:
            return f"{diff.days // 7}w"

    @staticmethod
    def _get_trending_categories(category_dict: dict) -> List[tuple]:
        """Get trending categories"""
        return sorted(category_dict.items(), key=lambda x: x[1], reverse=True)
