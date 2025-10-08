"""
Token Tracker Utility
Extracts and stores token metrics from agent and team run events.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

TOKEN_METRICS_FILE = Path('data/token_metrics.json')


class TokenTracker:
    """
    Tracks and persists token usage metrics from agent and team runs.
    """

    def __init__(self, file_path: Path | str = TOKEN_METRICS_FILE):
        """
        Initialize the token tracker.

        Args:
            file_path: Path to the JSON file for storing token metrics
        """
        self.file_path = Path(file_path)
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Ensure the metrics file and its parent directory exist."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text('[]')
            logger.info(f'Created token metrics file at {self.file_path}')

    def _load_metrics(self) -> list[dict[str, Any]]:
        """
        Load existing metrics from the JSON file.

        Returns:
            List of metric dictionaries
        """
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f'Error loading metrics file: {e}. Starting fresh.')
            return []

    def _save_metrics(self, metrics: list[dict[str, Any]]) -> None:
        """
        Save metrics to the JSON file.

        Args:
            metrics: List of metric dictionaries to save
        """
        try:
            with open(self.file_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            logger.info(f'Saved token metrics to {self.file_path}')
        except Exception as e:
            logger.error(f'Error saving metrics to file: {e}')

    def track_event(
        self,
        event_name: str,
        agent_id: str | None,
        agent_name: str | None,
        team_name: str | None,
        metrics: dict[str, Any],
        run_id: str | None = None,
        session_id: str | None = None,
        parent_run_id: str | None = None,
    ) -> None:
        """
        Track a run event with token metrics.

        Args:
            event_name: Name of the event (e.g., 'RunCompleted', 'TeamRunCompleted')
            agent_id: ID of the agent (if applicable)
            agent_name: Name of the agent (if applicable)
            team_name: Name of the team (if applicable)
            metrics: Dictionary containing token metrics
            run_id: Unique run ID
            session_id: Session ID
            parent_run_id: Parent run ID (if applicable)
        """
        if not metrics:
            logger.debug(f'No metrics found for {event_name}')
            return

        token_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_name,
            'run_id': run_id,
            'session_id': session_id,
            'parent_run_id': parent_run_id,
            'team_name': team_name,
            'agent_id': agent_id,
            'agent_name': agent_name,
            'metrics': {
                'input_tokens': metrics.get('input_tokens', 0),
                'output_tokens': metrics.get('output_tokens', 0),
                'total_tokens': metrics.get('total_tokens', 0),
                'cache_read_tokens': metrics.get('cache_read_tokens', 0),
                'time_to_first_token': metrics.get('time_to_first_token', 0),
                'duration': metrics.get('duration', 0),
            },
        }

        all_metrics = self._load_metrics()

        all_metrics.append(token_data)

        self._save_metrics(all_metrics)

        logger.info(
            f'Tracked tokens for {agent_name or team_name}: '
            f'{token_data["metrics"]["total_tokens"]} total tokens'
        )

    def get_metrics(
        self,
        agent_name: str | None = None,
        team_name: str | None = None,
        session_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve metrics with optional filtering.

        Args:
            agent_name: Filter by agent name
            team_name: Filter by team name
            session_id: Filter by session ID

        Returns:
            List of metric dictionaries matching the filters
        """
        all_metrics = self._load_metrics()

        if not any([agent_name, team_name, session_id]):
            return all_metrics

        filtered = []
        for metric in all_metrics:
            if agent_name and metric.get('agent_name') != agent_name:
                continue
            if team_name and metric.get('team_name') != team_name:
                continue
            if session_id and metric.get('session_id') != session_id:
                continue
            filtered.append(metric)

        return filtered

    def get_summary(self) -> dict[str, Any]:
        """
        Get a summary of all token usage.

        Returns:
            Dictionary containing aggregated token statistics
        """
        all_metrics = self._load_metrics()

        if not all_metrics:
            return {
                'total_runs': 0,
                'total_tokens': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'by_agent': {},
                'by_team': {},
            }

        total_tokens = 0
        total_input_tokens = 0
        total_output_tokens = 0
        by_agent: dict[str, Any] = {}
        by_team: dict[str, Any] = {}

        for metric in all_metrics:
            metrics_data = metric.get('metrics', {})
            total_tokens += metrics_data.get('total_tokens', 0)
            total_input_tokens += metrics_data.get('input_tokens', 0)
            total_output_tokens += metrics_data.get('output_tokens', 0)

            agent_name = metric.get('agent_name')
            if agent_name:
                if agent_name not in by_agent:
                    by_agent[agent_name] = {
                        'runs': 0,
                        'total_tokens': 0,
                        'input_tokens': 0,
                        'output_tokens': 0,
                    }
                by_agent[agent_name]['runs'] += 1
                by_agent[agent_name]['total_tokens'] += metrics_data.get(
                    'total_tokens', 0
                )
                by_agent[agent_name]['input_tokens'] += metrics_data.get(
                    'input_tokens', 0
                )
                by_agent[agent_name]['output_tokens'] += metrics_data.get(
                    'output_tokens', 0
                )

            team_name = metric.get('team_name')
            if team_name:
                if team_name not in by_team:
                    by_team[team_name] = {
                        'runs': 0,
                        'total_tokens': 0,
                        'input_tokens': 0,
                        'output_tokens': 0,
                    }
                by_team[team_name]['runs'] += 1
                by_team[team_name]['total_tokens'] += metrics_data.get(
                    'total_tokens', 0
                )
                by_team[team_name]['input_tokens'] += metrics_data.get(
                    'input_tokens', 0
                )
                by_team[team_name]['output_tokens'] += metrics_data.get(
                    'output_tokens', 0
                )

        return {
            'total_runs': len(all_metrics),
            'total_tokens': total_tokens,
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'by_agent': by_agent,
            'by_team': by_team,
        }

    def clear_metrics(self) -> None:
        """Clear all stored metrics."""
        self._save_metrics([])
        logger.info('Cleared all token metrics')


token_tracker = TokenTracker()
