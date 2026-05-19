"""Goal engine for FocusFlow - daily goal tracking and status."""
from datetime import date, timedelta
from utils.helpers import is_weekend


class GoalEngine:
    """Manages daily goal tracking, status colors, and motivational text."""

    def __init__(self, db_manager):
        self.db = db_manager

    def get_daily_goal_minutes(self):
        """Get today's goal in minutes."""
        if is_weekend():
            return int(self.db.get_setting('weekend_goal', self.db.get_setting('daily_goal', '120')))
        return int(self.db.get_setting('daily_goal', '120'))

    def get_today_status(self):
        """Get comprehensive status for today."""
        goal_min = self.get_daily_goal_minutes()
        completed = self.db.get_total_minutes_today()
        remaining = max(0, goal_min - completed)
        percentage = (completed / goal_min * 100) if goal_min > 0 else 0

        return {
            'goal_minutes': goal_min,
            'completed_minutes': completed,
            'remaining_minutes': remaining,
            'percentage': min(percentage, 999),
            'color_state': self._get_color_state(percentage),
            'motivational_text': self._get_motivational_text(percentage),
            'is_completed': percentage >= 100,
        }

    def _get_color_state(self, percentage):
        """Return color state based on goal completion percentage."""
        if percentage >= 100:
            return 'gold'
        elif percentage >= 80:
            return 'green'
        elif percentage >= 50:
            return 'yellow'
        else:
            return 'red'

    def _get_motivational_text(self, percentage):
        """Return motivational message based on progress."""
        if percentage >= 100:
            return "🏆 Goal crushed! You're on fire!"
        elif percentage >= 80:
            return "🔥 Almost there! Keep pushing!"
        elif percentage >= 50:
            return "💪 Great progress! Halfway and beyond!"
        elif percentage >= 25:
            return "📚 Good start! Keep the momentum going!"
        elif percentage > 0:
            return "🚀 You've started! Every minute counts!"
        else:
            return "⏰ Ready to begin your focus journey today?"

    def get_color_hex(self, color_state):
        """Return hex color for the state."""
        colors = {
            'red': '#FF6B6B',
            'yellow': '#FFD93D',
            'green': '#6BCB77',
            'gold': '#FFD700',
        }
        return colors.get(color_state, '#FFFFFF')

    def check_yesterday_completion(self):
        """Check if yesterday's goal was met."""
        yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        goal_data = self.db.get_or_create_daily_goal(yesterday, self.get_daily_goal_minutes())
        return goal_data.get('status') == 'completed'
