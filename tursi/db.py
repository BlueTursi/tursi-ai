"""SQLite database integration for Tursi daemon state persistence."""
import sqlite3
import json
from pathlib import Path
from datetime import datetime, UTC, timedelta
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class TursiDB:
    """Database manager for Tursi daemon."""

    # Current schema version
    CURRENT_VERSION = 1

    # Base schema
    SCHEMA = """
    -- Schema version tracking
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY,
        applied_at TIMESTAMP NOT NULL
    );

    -- Model deployments table
    CREATE TABLE IF NOT EXISTS model_deployments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT NOT NULL,
        process_id INTEGER,
        host TEXT NOT NULL,
        port INTEGER NOT NULL,
        status TEXT NOT NULL,  -- running, stopped, failed
        config TEXT NOT NULL,  -- JSON of model config
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL
    );

    -- Model logs table
    CREATE TABLE IF NOT EXISTS model_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deployment_id INTEGER NOT NULL,
        level TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL,
        FOREIGN KEY (deployment_id) REFERENCES model_deployments (id)
    );

    -- Resource metrics table
    CREATE TABLE IF NOT EXISTS resource_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deployment_id INTEGER NOT NULL,
        cpu_percent REAL,
        memory_mb REAL,
        created_at TIMESTAMP NOT NULL,
        FOREIGN KEY (deployment_id) REFERENCES model_deployments (id)
    );
    """

    # Migration scripts for each version
    MIGRATIONS = {
        # Example migration for future use:
        # 2: """
        #     ALTER TABLE model_deployments ADD COLUMN gpu_id TEXT;
        # """
    }

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file. If None, uses ~/.tursi/data/tursi.db
        """
        if db_path is None:
            db_path = str(Path.home() / ".tursi" / "data" / "tursi.db")

        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self._init_db()
        self._run_migrations()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with proper configuration.

        Returns:
            SQLite connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize database schema."""
        try:
            with self._get_connection() as conn:
                conn.executescript(self.SCHEMA)

                # Check if this is a new database
                cursor = conn.execute("SELECT COUNT(*) FROM schema_version")
                if cursor.fetchone()[0] == 0:
                    # Insert initial schema version
                    conn.execute(
                        "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
                        (1, datetime.now(UTC).isoformat())
                    )
                logger.info(f"Database initialized at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def _get_current_version(self) -> int:
        """Get the current schema version from the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT MAX(version) FROM schema_version")
                version = cursor.fetchone()[0]
                return version or 0
        except sqlite3.Error as e:
            logger.error(f"Failed to get schema version: {e}")
            raise

    def _run_migrations(self):
        """Run any pending database migrations."""
        current_version = self._get_current_version()

        if current_version >= self.CURRENT_VERSION:
            logger.debug("Database schema is up to date")
            return

        try:
            with self._get_connection() as conn:
                for version in range(current_version + 1, self.CURRENT_VERSION + 1):
                    if version in self.MIGRATIONS:
                        logger.info(f"Applying migration to version {version}")
                        conn.executescript(self.MIGRATIONS[version])
                        conn.execute(
                            "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
                            (version, datetime.now(UTC).isoformat())
                        )
                logger.info("Database migrations completed successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to run migrations: {e}")
            raise

    def add_deployment(self, model_name: str, process_id: int, host: str, port: int,
                      config: Dict) -> int:
        """Add a new model deployment record.

        Args:
            model_name: Name of the model being deployed
            process_id: PID of the model process
            host: Host address the model is serving on
            port: Port number the model is serving on
            config: Model configuration dictionary

        Returns:
            ID of the new deployment record
        """
        now = datetime.now(UTC).isoformat()
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO model_deployments
                    (model_name, process_id, host, port, status, config, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (model_name, process_id, host, port, "running",
                     json.dumps(config), now, now)
                )
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Failed to add deployment: {e}")
            raise

    def update_deployment_status(self, deployment_id: int, status: str):
        """Update the status of a deployment.

        Args:
            deployment_id: ID of the deployment to update
            status: New status (running, stopped, failed)
        """
        now = datetime.now(UTC).isoformat()
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    UPDATE model_deployments
                    SET status = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (status, now, deployment_id)
                )
        except sqlite3.Error as e:
            logger.error(f"Failed to update deployment status: {e}")
            raise

    def get_deployment(self, deployment_id: int) -> Optional[Dict]:
        """Get deployment details by ID.

        Args:
            deployment_id: ID of the deployment to fetch

        Returns:
            Dictionary with deployment details or None if not found
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM model_deployments WHERE id = ?",
                    (deployment_id,)
                )
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except sqlite3.Error as e:
            logger.error(f"Failed to get deployment: {e}")
            raise

    def get_active_deployments(self) -> List[Dict]:
        """Get all currently running deployments.

        Returns:
            List of dictionaries with deployment details
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM model_deployments WHERE status = 'running'"
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get active deployments: {e}")
            raise

    def add_log(self, deployment_id: int, level: str, message: str):
        """Add a log entry for a deployment.

        Args:
            deployment_id: ID of the related deployment
            level: Log level (INFO, WARNING, ERROR, etc.)
            message: Log message
        """
        now = datetime.now(UTC).isoformat()
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO model_logs
                    (deployment_id, level, message, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (deployment_id, level, message, now)
                )
        except sqlite3.Error as e:
            logger.error(f"Failed to add log: {e}")
            raise

    def get_logs(self, deployment_id: int, limit: int = 100) -> List[Dict]:
        """Get recent logs for a deployment.

        Args:
            deployment_id: ID of the deployment
            limit: Maximum number of log entries to return

        Returns:
            List of dictionaries with log entries
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT * FROM model_logs
                    WHERE deployment_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (deployment_id, limit)
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get logs: {e}")
            raise

    def add_metrics(self, deployment_id: int, cpu_percent: float, memory_mb: float):
        """Add resource usage metrics for a deployment.

        Args:
            deployment_id: ID of the deployment
            cpu_percent: CPU usage percentage
            memory_mb: Memory usage in megabytes
        """
        now = datetime.now(UTC).isoformat()
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO resource_metrics
                    (deployment_id, cpu_percent, memory_mb, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (deployment_id, cpu_percent, memory_mb, now)
                )
        except sqlite3.Error as e:
            logger.error(f"Failed to add metrics: {e}")
            raise

    def get_metrics(self, deployment_id: int, limit: int = 60) -> List[Dict]:
        """Get recent resource metrics for a deployment.

        Args:
            deployment_id: ID of the deployment
            limit: Maximum number of metric entries to return

        Returns:
            List of dictionaries with metric entries
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT * FROM resource_metrics
                    WHERE deployment_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (deployment_id, limit)
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get metrics: {e}")
            raise

    def cleanup_old_metrics(self, max_age_hours: int = 24):
        """Clean up old metric entries.

        Args:
            max_age_hours: Maximum age of metrics to keep in hours
        """
        try:
            cutoff_time = (datetime.now(UTC) - timedelta(hours=max_age_hours)).isoformat()
            with self._get_connection() as conn:
                conn.execute(
                    """
                    DELETE FROM resource_metrics
                    WHERE created_at < ?
                    """,
                    (cutoff_time,)
                )
        except sqlite3.Error as e:
            logger.error(f"Failed to cleanup metrics: {e}")
            raise
