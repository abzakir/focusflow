"""Streak engine for FocusFlow - streak tracking and behavioral reinforcement."""
from datetime import date, timedelta


class StreakEngine:
    """Manages streak tracking, consistency stats, and behavioral messages."""

    def __init__(self, db_manager):
        self.db = db_manager

    def get_streak_data(self):
        """Get current streak information."""
        streak = self.db.get_streak()
        consistency = self._calculate_consistency()
        total_days = self._count_disciplined_days()
        return {
            'current_streak': streak['current_streak'],
            'longest_streak': streak['longest_streak'],
            'consistency_percent': consistency,
            'total_disciplined_days': total_days,
            'last_completed_date': streak.get('last_completed_date'),
        }

    def process_day_completion(self):
        """Call when a daily goal is completed. Returns behavioral message or None."""
        today_str = date.today().strftime('%Y-%m-%d')
        streak = self.db.get_streak()

        if streak['last_completed_date'] == today_str:
            return None  # Already processed today

        last_date = streak.get('last_completed_date')
        current = streak['current_streak']
        longest = streak['longest_streak']

        if last_date:
            last = date.fromisoformat(last_date)
            diff = (date.today() - last).days
            if diff == 1:
                current += 1
            elif diff > 1:
                current = 1
        else:
            current = 1

        longest = max(longest, current)
        self.db.update_streak(current, longest, today_str)

        return self._get_milestone_message(current)

    def process_missed_day(self):
        """Call when checking at start of day and yesterday was missed."""
        streak = self.db.get_streak()
        last_date = streak.get('last_completed_date')

        if last_date:
            last = date.fromisoformat(last_date)
            diff = (date.today() - last).days
            if diff > 1:
                current = 0
                self.db.update_streak(current, streak['longest_streak'], last_date)
                return self._get_missed_message(diff - 1)
        return None

    def _get_milestone_message(self, streak_count):
        """Return milestone message for streak achievements."""
        milestones = {
            3: "🔥 3-day streak! You're building momentum!",
            7: "⚡ 7-day streak! One full week of discipline!",
            14: "🌟 2-week streak! You're unstoppable!",
            21: "💎 21 days! A new habit is forming!",
            30: "🏆 30-day streak! Legendary discipline!",
            50: "👑 50-day streak! You're in the top 1%!",
            100: "🎯 100-day streak! Absolute dedication!",
        }
        return milestones.get(streak_count)

    def _get_missed_message(self, missed_days):
        """Return gentle accountability message."""
        if missed_days >= 3:
            return "It's been a few days. Remember, consistency beats intensity. Start small today! 💙"
        elif missed_days == 2:
            return "You missed 2 days. No worries — today is a fresh start! 🌅"
        else:
            return "Yesterday was quiet. Let's make today count! 💪"

    def get_behavioral_message(self):
        """Check for behavioral reinforcement triggers."""
        streak = self.db.get_streak()
        last_date = streak.get('last_completed_date')

        if last_date:
            last = date.fromisoformat(last_date)
            days_since = (date.today() - last).days
            if days_since >= 2:
                return "warning", self._get_missed_message(days_since)

        # Check for productivity drop (compare last 7 days vs previous 7 days)
        today = date.today()
        recent_start = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        recent_end = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        prev_start = (today - timedelta(days=14)).strftime('%Y-%m-%d')
        prev_end = (today - timedelta(days=8)).strftime('%Y-%m-%d')

        recent = self.db.get_sessions_range(recent_start, recent_end)
        prev = self.db.get_sessions_range(prev_start, prev_end)

        recent_total = sum(s['total_minutes'] for s in recent) if recent else 0
        prev_total = sum(s['total_minutes'] for s in prev) if prev else 0

        if prev_total > 0 and recent_total < prev_total * 0.7:
            return "encourage", "📉 Your study time dipped this week. You've got this — even 15 minutes makes a difference! 🌱"

        return None, None

    def _calculate_consistency(self):
        """Calculate consistency percentage over last 30 days."""
        today = date.today()
        start = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        end = today.strftime('%Y-%m-%d')
        sessions = self.db.get_sessions_range(start, end)
        active_days = len(sessions)
        return round((active_days / 30) * 100, 1)

    def _count_disciplined_days(self):
        """Count total days with at least one focus session."""
        today = date.today()
        start = (today - timedelta(days=365)).strftime('%Y-%m-%d')
        end = today.strftime('%Y-%m-%d')
        sessions = self.db.get_sessions_range(start, end)
        return len(sessions)
