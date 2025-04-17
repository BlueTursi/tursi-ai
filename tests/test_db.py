"""Tests for the Tursi database module."""

import os
import pytest
import sqlite3
from datetime import datetime, timedelta, UTC
from tursi.db import TursiDB


@pytest.fixture
def db_path(tmp_path):
    """Provide a temporary database path."""
    return str(tmp_path / "test_tursi.db")


@pytest.fixture
def db(db_path):
    """Provide a database instance."""
    return TursiDB(db_path)


@pytest.fixture
def sample_deployment(db):
    """Create a sample deployment and return its ID."""
    config = {"model": "test-model", "quantization": "dynamic", "bits": 8}
    return db.add_deployment(
        model_name="test-model",
        process_id=12345,
        host="localhost",
        port=5000,
        config=config,
    )


def test_init_db(db_path):
    """Test database initialization."""
    db = TursiDB(db_path)
    assert os.path.exists(db_path)


def test_add_deployment(db):
    """Test adding a new deployment."""
    config = {"model": "test-model", "quantization": "dynamic", "bits": 8}
    deployment_id = db.add_deployment(
        model_name="test-model",
        process_id=12345,
        host="localhost",
        port=5000,
        config=config,
    )

    assert deployment_id > 0
    deployment = db.get_deployment(deployment_id)
    assert deployment is not None
    assert deployment["model_name"] == "test-model"
    assert deployment["status"] == "running"


def test_update_deployment_status(db, sample_deployment):
    """Test updating deployment status."""
    db.update_deployment_status(sample_deployment, "stopped")
    deployment = db.get_deployment(sample_deployment)
    assert deployment["status"] == "stopped"


def test_get_active_deployments(db, sample_deployment):
    """Test getting active deployments."""
    deployments = db.get_active_deployments()
    assert len(deployments) == 1
    assert deployments[0]["id"] == sample_deployment

    # Stop the deployment
    db.update_deployment_status(sample_deployment, "stopped")
    deployments = db.get_active_deployments()
    assert len(deployments) == 0


def test_add_and_get_logs(db, sample_deployment):
    """Test adding and retrieving logs."""
    db.add_log(sample_deployment, "INFO", "Test message")
    db.add_log(sample_deployment, "ERROR", "Test error")

    logs = db.get_logs(sample_deployment)
    assert len(logs) == 2
    assert logs[0]["level"] == "ERROR"  # Most recent first
    assert logs[1]["level"] == "INFO"


def test_add_and_get_metrics(db, sample_deployment):
    """Test adding and retrieving metrics."""
    db.add_metrics(sample_deployment, cpu_percent=50.0, memory_mb=1024.0)
    db.add_metrics(sample_deployment, cpu_percent=60.0, memory_mb=1124.0)

    metrics = db.get_metrics(sample_deployment)
    assert len(metrics) == 2
    assert metrics[0]["cpu_percent"] == 60.0  # Most recent first
    assert metrics[1]["memory_mb"] == 1024.0


def test_cleanup_old_metrics(db, sample_deployment):
    """Test cleaning up old metrics."""
    # Add old metrics
    old_time = (datetime.now(UTC) - timedelta(hours=25)).isoformat()
    with db._get_connection() as conn:
        conn.execute(
            """
            INSERT INTO resource_metrics
            (deployment_id, cpu_percent, memory_mb, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (sample_deployment, 50.0, 1024.0, old_time),
        )

    # Add recent metrics
    db.add_metrics(sample_deployment, cpu_percent=60.0, memory_mb=1124.0)

    # Clean up old metrics
    db.cleanup_old_metrics(max_age_hours=24)

    # Check that only recent metrics remain
    metrics = db.get_metrics(sample_deployment)
    assert len(metrics) == 1
    assert metrics[0]["cpu_percent"] == 60.0


def test_get_nonexistent_deployment(db):
    """Test getting a deployment that doesn't exist."""
    deployment = db.get_deployment(999)
    assert deployment is None


def test_log_limit(db, sample_deployment):
    """Test log retrieval limit."""
    # Add more logs than the default limit
    for i in range(150):
        db.add_log(sample_deployment, "INFO", f"Test message {i}")

    # Get logs with default limit (100)
    logs = db.get_logs(sample_deployment)
    assert len(logs) == 100

    # Get logs with custom limit
    logs = db.get_logs(sample_deployment, limit=50)
    assert len(logs) == 50


def test_metrics_limit(db, sample_deployment):
    """Test metrics retrieval limit."""
    # Add more metrics than the default limit
    for i in range(100):
        db.add_metrics(sample_deployment, cpu_percent=50.0 + i, memory_mb=1024.0 + i)

    # Get metrics with default limit (60)
    metrics = db.get_metrics(sample_deployment)
    assert len(metrics) == 60

    # Get metrics with custom limit
    metrics = db.get_metrics(sample_deployment, limit=30)
    assert len(metrics) == 30


def test_initial_schema_creation(db_path):
    """Test that the initial schema is created correctly."""
    # Create database
    db = TursiDB(db_path)

    # Verify tables exist
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name IN
            ('schema_version', 'model_deployments', 'model_logs', 'resource_metrics')
            """
        )
        tables = [row[0] for row in cursor.fetchall()]

        assert len(tables) == 4
        assert "schema_version" in tables
        assert "model_deployments" in tables
        assert "model_logs" in tables
        assert "resource_metrics" in tables

        # Verify initial schema version
        cursor = conn.execute("SELECT version FROM schema_version")
        version = cursor.fetchone()[0]
        assert version == 1


def test_migration_tracking(db_path):
    """Test that migrations are properly tracked."""
    # Create database with initial schema
    db = TursiDB(db_path)

    # Add a test migration
    db.MIGRATIONS[2] = "ALTER TABLE model_deployments ADD COLUMN test_column TEXT;"
    db.CURRENT_VERSION = 2

    # Run migrations
    db._run_migrations()

    # Verify migration was applied
    with sqlite3.connect(db_path) as conn:
        # Check schema version was updated
        cursor = conn.execute(
            "SELECT version FROM schema_version ORDER BY version DESC"
        )
        version = cursor.fetchone()[0]
        assert version == 2

        # Verify new column exists
        cursor = conn.execute("PRAGMA table_info(model_deployments)")
        columns = [row[1] for row in cursor.fetchall()]
        assert "test_column" in columns


def test_migration_idempotency(db_path):
    """Test that migrations are not reapplied."""
    # Create database
    db = TursiDB(db_path)

    # Add test migration
    db.MIGRATIONS[2] = "ALTER TABLE model_deployments ADD COLUMN test_column TEXT;"
    db.CURRENT_VERSION = 2

    # Run migrations twice
    db._run_migrations()
    db._run_migrations()

    # Verify migration was only applied once
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM schema_version WHERE version = 2")
        count = cursor.fetchone()[0]
        assert count == 1


def test_sequential_migrations(db_path):
    """Test that migrations are applied in correct order."""
    # Create database
    db = TursiDB(db_path)

    # Add multiple migrations
    db.MIGRATIONS.update(
        {
            2: "ALTER TABLE model_deployments ADD COLUMN test_column1 TEXT;",
            3: "ALTER TABLE model_deployments ADD COLUMN test_column2 TEXT;",
            4: "ALTER TABLE model_deployments ADD COLUMN test_column3 TEXT;",
        }
    )
    db.CURRENT_VERSION = 4

    # Run migrations
    db._run_migrations()

    # Verify migrations were applied in order
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT version FROM schema_version ORDER BY version")
        versions = [row[0] for row in cursor.fetchall()]
        assert versions == [1, 2, 3, 4]

        # Verify columns were added in order
        cursor = conn.execute("PRAGMA table_info(model_deployments)")
        columns = [row[1] for row in cursor.fetchall()]

        # Check columns exist and are in correct order
        col_indices = {col: idx for idx, col in enumerate(columns)}
        assert col_indices["test_column1"] < col_indices["test_column2"]
        assert col_indices["test_column2"] < col_indices["test_column3"]


def test_failed_migration_rollback(db_path):
    """Test that failed migrations are rolled back."""
    # Create database
    db = TursiDB(db_path)

    # Add an invalid migration
    db.MIGRATIONS[2] = "ALTER TABLE nonexistent_table ADD COLUMN test_column TEXT;"
    db.CURRENT_VERSION = 2

    # Attempt migration
    with pytest.raises(sqlite3.Error):
        db._run_migrations()

    # Verify database is still at version 1
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT MAX(version) FROM schema_version")
        version = cursor.fetchone()[0]
        assert version == 1


def test_get_current_version(db_path):
    """Test getting current schema version."""
    # Create database
    db = TursiDB(db_path)

    # Verify initial version
    assert db._get_current_version() == 1

    # Add and apply a migration
    db.MIGRATIONS[2] = "ALTER TABLE model_deployments ADD COLUMN test_column TEXT;"
    db.CURRENT_VERSION = 2
    db._run_migrations()

    # Verify updated version
    assert db._get_current_version() == 2


def test_empty_migrations(db_path):
    """Test behavior when no migrations are needed."""
    # Create database
    db = TursiDB(db_path)

    # Run migrations when already at current version
    db._run_migrations()  # Should do nothing

    # Verify still at version 1
    assert db._get_current_version() == 1

    # Verify only one version record exists
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM schema_version")
        count = cursor.fetchone()[0]
        assert count == 1
