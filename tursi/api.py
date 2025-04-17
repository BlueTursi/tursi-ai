"""API server for Tursi daemon communication."""

from pathlib import Path
import json
from typing import List, Any
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from .db import TursiDB
from .model import ModelManager

logger = logging.getLogger(__name__)


class TursiAPI:
    """API server for communicating with the Tursi daemon."""

    def __init__(self, db: TursiDB):
        """Initialize the API server.

        Args:
            db: Database instance for state management
        """
        self.db = db
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        """Configure API routes."""
        # Model deployment endpoints
        self.app.route("/api/v1/models", methods=["POST"])(self.deploy_model)
        self.app.route("/api/v1/models/<int:deployment_id>", methods=["DELETE"])(
            self.stop_model
        )
        self.app.route("/api/v1/models", methods=["GET"])(self.list_models)
        self.app.route("/api/v1/models/<int:deployment_id>", methods=["GET"])(
            self.get_model_status
        )

        # Logging endpoints
        self.app.route("/api/v1/models/<int:deployment_id>/logs", methods=["GET"])(
            self.get_logs
        )

        # Metrics endpoints
        self.app.route("/api/v1/models/<int:deployment_id>/metrics", methods=["GET"])(
            self.get_metrics
        )

        # Health check endpoint
        self.app.route("/api/v1/health", methods=["GET"])(self.health_check)

    def deploy_model(self):
        """Deploy a new model instance.

        Expected JSON payload:
        {
            "model_name": "model-name",
            "host": "localhost",
            "port": 5000,
            "config": {
                "quantization": "dynamic",
                "bits": 8,
                "rate_limit": "100/minute"
            }
        }
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            required_fields = ["model_name", "host", "port", "config"]
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                return (
                    jsonify(
                        {
                            "error": f"Missing required fields: {', '.join(missing_fields)}"
                        }
                    ),
                    400,
                )

            # Add deployment to database
            deployment_id = self.db.add_deployment(
                model_name=data["model_name"],
                process_id=None,  # Will be set by daemon when process starts
                host=data["host"],
                port=data["port"],
                config=data["config"],
            )

            return jsonify({"deployment_id": deployment_id, "status": "pending"}), 202

        except Exception as e:
            logger.error(f"Error deploying model: {e}")
            return jsonify({"error": str(e)}), 500

    def stop_model(self, deployment_id: int):
        """Stop a running model deployment."""
        try:
            deployment = self.db.get_deployment(deployment_id)
            if not deployment:
                return jsonify({"error": "Deployment not found"}), 404

            # Update status to stopping - daemon will handle actual process termination
            self.db.update_deployment_status(deployment_id, "stopping")

            return jsonify({"deployment_id": deployment_id, "status": "stopping"}), 202

        except Exception as e:
            logger.error(f"Error stopping model: {e}")
            return jsonify({"error": str(e)}), 500

    def list_models(self):
        """List all active model deployments."""
        try:
            deployments = self.db.get_active_deployments()
            return jsonify({"deployments": deployments}), 200

        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return jsonify({"error": str(e)}), 500

    def get_model_status(self, deployment_id: int):
        """Get status of a specific model deployment."""
        try:
            deployment = self.db.get_deployment(deployment_id)
            if not deployment:
                return jsonify({"error": "Deployment not found"}), 404

            return jsonify(deployment), 200

        except Exception as e:
            logger.error(f"Error getting model status: {e}")
            return jsonify({"error": str(e)}), 500

    def get_logs(self, deployment_id: int):
        """Get logs for a specific model deployment."""
        try:
            deployment = self.db.get_deployment(deployment_id)
            if not deployment:
                return jsonify({"error": "Deployment not found"}), 404

            limit = request.args.get("limit", default=100, type=int)
            logs = self.db.get_logs(deployment_id, limit=limit)

            return jsonify({"deployment_id": deployment_id, "logs": logs}), 200

        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return jsonify({"error": str(e)}), 500

    def get_metrics(self, deployment_id: int):
        """Get resource metrics for a specific model deployment."""
        try:
            deployment = self.db.get_deployment(deployment_id)
            if not deployment:
                return jsonify({"error": "Deployment not found"}), 404

            limit = request.args.get("limit", default=60, type=int)
            metrics = self.db.get_metrics(deployment_id, limit=limit)

            return jsonify({"deployment_id": deployment_id, "metrics": metrics}), 200

        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return jsonify({"error": str(e)}), 500

    def health_check(self):
        """API health check endpoint."""
        return (
            jsonify(
                {
                    "status": "healthy",
                    "version": "0.1.0",  # TODO: Get from package version
                }
            ),
            200,
        )

    def run(self, host: str = "localhost", port: int = 5000):
        """Run the API server.

        Args:
            host: Host address to bind to
            port: Port number to listen on
        """
        self.app.run(host=host, port=port)
