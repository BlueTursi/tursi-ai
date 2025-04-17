"""
Tursi Daemon (tursid) - Background process for managing AI model deployments.
"""
import os
import sys
import signal
import logging
import atexit
import time
import json
import multiprocessing as mp
import threading
from pathlib import Path
from typing import Optional, Dict
import psutil
from .db import TursiDB
from .engine import TursiEngine
from .api import TursiAPI

class ModelProcess:
    """Wrapper for a model deployment process."""

    def __init__(self, model_name: str, host: str, port: int, config: Dict):
        self.model_name = model_name
        self.host = host
        self.port = port
        self.config = config
        self.process: Optional[mp.Process] = None
        self._stop_event = mp.Event()

    def start(self):
        """Start the model process."""
        self.process = mp.Process(
            target=self._run_model,
            args=(self._stop_event,),
            daemon=True
        )
        self.process.start()
        return self.process.pid

    def stop(self):
        """Stop the model process."""
        if self.process and self.process.is_alive():
            self._stop_event.set()
            self.process.join(timeout=5)
            if self.process.is_alive():
                self.process.terminate()
                self.process.join(timeout=5)
                if self.process.is_alive():
                    self.process.kill()

    def _run_model(self, stop_event):
        """Run the model in a separate process."""
        try:
            engine = TursiEngine()
            app = engine.create_app(
                model_name=self.model_name,
                rate_limit=self.config.get("rate_limit")
            )

            # Run the Flask app with the stop event
            from werkzeug.serving import make_server
            server = make_server(self.host, self.port, app)

            # Run server in a separate thread so we can check the stop event
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.start()

            # Wait for stop event
            while not stop_event.is_set():
                time.sleep(1)

            # Cleanup
            server.shutdown()
            server_thread.join()

        except Exception as e:
            logging.error(f"Error in model process: {e}")
            sys.exit(1)

class TursiDaemon:
    """
    Daemon process for managing Tursi AI model deployments.
    Handles process management, signal handling, and state persistence.
    """

    def __init__(self, pid_file: str = "/tmp/tursid.pid", db_path: Optional[str] = None,
                 api_host: str = "localhost", api_port: int = 5000):
        self.pid_file = pid_file
        self.is_running = False
        self.logger = self._setup_logging()
        self.db = TursiDB(db_path)
        self.api_host = api_host
        self.api_port = api_port
        self.api_server = None
        self.api_thread = None

        # Register signal handlers
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGHUP, self._handle_signal)

        # Register cleanup on exit
        atexit.register(self.cleanup)

        # Initialize state
        self.model_processes: Dict[int, ModelProcess] = {}  # deployment_id -> ModelProcess

    def _setup_logging(self) -> logging.Logger:
        """Configure daemon logging."""
        logger = logging.getLogger("tursid")
        logger.setLevel(logging.INFO)

        # Create logs directory if it doesn't exist
        log_dir = Path.home() / ".tursi" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        # File handler for persistent logging
        fh = logging.FileHandler(log_dir / "tursid.log")
        fh.setLevel(logging.INFO)

        # Console handler for development
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatting
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    def _handle_signal(self, signum: int, frame) -> None:
        """Handle incoming signals for graceful shutdown."""
        sig_name = signal.Signals(signum).name
        self.logger.info(f"Received signal: {sig_name}")

        if signum in (signal.SIGTERM, signal.SIGINT):
            self.logger.info("Initiating graceful shutdown...")
            self.stop()
        elif signum == signal.SIGHUP:
            self.logger.info("Reloading configuration...")
            self._reload_config()

    def _reload_config(self) -> None:
        """Reload daemon configuration on SIGHUP."""
        self.logger.info("Reloading active deployments...")
        active_deployments = self.db.get_active_deployments()

        # Stop any processes not in active deployments
        current_ids = set(self.model_processes.keys())
        active_ids = {d["id"] for d in active_deployments}

        for deployment_id in current_ids - active_ids:
            self._stop_deployment(deployment_id)

        # Start any new deployments
        for deployment in active_deployments:
            if deployment["id"] not in self.model_processes:
                self._start_deployment(deployment)

    def _write_pid_file(self) -> None:
        """Write the PID file."""
        pid = str(os.getpid())
        self.logger.info(f"Writing PID {pid} to {self.pid_file}")
        Path(self.pid_file).write_text(pid)

    def _check_pid(self, pid: int) -> bool:
        """Check if a process with given PID is running."""
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def _start_deployment(self, deployment: Dict) -> None:
        """Start a model deployment."""
        try:
            deployment_id = deployment["id"]
            config = json.loads(deployment["config"])

            # Create and start the model process
            process = ModelProcess(
                model_name=deployment["model_name"],
                host=deployment["host"],
                port=deployment["port"],
                config=config
            )

            pid = process.start()
            self.model_processes[deployment_id] = process

            # Update database
            self.db.update_deployment_status(deployment_id, "running")
            self.db.add_log(
                deployment_id,
                "INFO",
                f"Started model process with PID {pid}"
            )

            self.logger.info(f"Started deployment {deployment_id} with PID {pid}")

        except Exception as e:
            self.logger.error(f"Failed to start deployment {deployment['id']}: {e}")
            self.db.update_deployment_status(deployment["id"], "failed")
            self.db.add_log(
                deployment["id"],
                "ERROR",
                f"Failed to start deployment: {str(e)}"
            )

    def _stop_deployment(self, deployment_id: int) -> None:
        """Stop a model deployment."""
        try:
            if deployment_id in self.model_processes:
                process = self.model_processes[deployment_id]
                process.stop()
                del self.model_processes[deployment_id]

                # Update database
                self.db.update_deployment_status(deployment_id, "stopped")
                self.db.add_log(
                    deployment_id,
                    "INFO",
                    "Stopped model process"
                )

                self.logger.info(f"Stopped deployment {deployment_id}")
        except Exception as e:
            self.logger.error(f"Error stopping deployment {deployment_id}: {e}")
            self.db.add_log(
                deployment_id,
                "ERROR",
                f"Error stopping deployment: {str(e)}"
            )

    def _update_metrics(self) -> None:
        """Update resource metrics for all running deployments."""
        for deployment_id, process in self.model_processes.items():
            try:
                if process.process and process.process.is_alive():
                    # Get process metrics
                    p = psutil.Process(process.process.pid)
                    cpu_percent = p.cpu_percent()
                    memory_info = p.memory_info()
                    memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB

                    # Store metrics
                    self.db.add_metrics(deployment_id, cpu_percent, memory_mb)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            except Exception as e:
                self.logger.error(f"Error updating metrics for deployment {deployment_id}: {e}")

    def _start_api_server(self):
        """Start the API server in a separate thread."""
        self.api_server = TursiAPI(self.db)
        self.api_thread = threading.Thread(
            target=self.api_server.run,
            args=(self.api_host, self.api_port),
            daemon=True
        )
        self.api_thread.start()
        self.logger.info(f"API server started on {self.api_host}:{self.api_port}")

    def start(self) -> None:
        """Start the daemon process."""
        # Check if already running
        if os.path.exists(self.pid_file):
            with open(self.pid_file) as f:
                pid = int(f.read().strip())
                if self._check_pid(pid):
                    self.logger.error(f"Daemon already running with PID {pid}")
                    sys.exit(1)
                else:
                    os.unlink(self.pid_file)

        # Initialize and migrate database before daemonization
        try:
            self.logger.info("Initializing database...")
            self.db.initialize()
            self.db.migrate()
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            sys.exit(1)

        # Daemonize the process
        self._daemonize()

        # Write PID file
        self._write_pid_file()

        # Start main loop
        self.run()

    def _daemonize(self) -> None:
        """Daemonize the process using double-fork method."""
        # First fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit first parent
        except OSError as err:
            self.logger.error(f"First fork failed: {err}")
            sys.exit(1)

        # Decouple from parent environment
        os.chdir('/')
        os.umask(0)
        os.setsid()

        # Second fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit from second parent
        except OSError as err:
            self.logger.error(f"Second fork failed: {err}")
            sys.exit(1)

        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()

        with open(os.devnull, 'r') as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        with open(os.devnull, 'a+') as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
            os.dup2(f.fileno(), sys.stderr.fileno())

        # Write pidfile
        self._write_pid_file()

    def stop(self) -> None:
        """Stop the daemon process."""
        if not os.path.exists(self.pid_file):
            self.logger.warning("PID file not found. Daemon not running?")
            return

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Try to terminate the process
            process = psutil.Process(pid)
            process.terminate()

            # Wait for process to terminate
            try:
                process.wait(timeout=10)
            except psutil.TimeoutExpired:
                self.logger.warning("Process didn't terminate. Forcing...")
                process.kill()

            os.remove(self.pid_file)
            self.logger.info("Daemon stopped")

        except (ProcessLookupError, psutil.NoSuchProcess):
            self.logger.warning("Process not found. Removing stale PID file.")
            os.remove(self.pid_file)
        except Exception as e:
            self.logger.error(f"Error stopping daemon: {e}")
            sys.exit(1)

    def restart(self) -> None:
        """Restart the daemon process."""
        self.stop()
        time.sleep(1)  # Wait briefly to ensure cleanup
        self.start()

    def cleanup(self) -> None:
        """Clean up resources on exit."""
        self.logger.info("Cleaning up daemon resources...")

        # Stop all running model processes
        for deployment_id in list(self.model_processes.keys()):
            self._stop_deployment(deployment_id)

        # Remove PID file
        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)

        # Clean up old metrics
        try:
            self.db.cleanup_old_metrics()
        except Exception as e:
            self.logger.error(f"Error cleaning up metrics: {e}")

    def run(self) -> None:
        """Main daemon loop."""
        self.is_running = True
        self.logger.info("Daemon started successfully")

        # Start API server
        self._start_api_server()

        # Restore any active deployments from database
        active_deployments = self.db.get_active_deployments()
        for deployment in active_deployments:
            self._start_deployment(deployment)

        metrics_interval = 60  # Update metrics every 60 seconds
        last_metrics_update = 0

        try:
            while self.is_running:
                # Update metrics periodically
                now = time.time()
                if now - last_metrics_update >= metrics_interval:
                    self._update_metrics()
                    last_metrics_update = now

                # Check process health
                for deployment_id, process in list(self.model_processes.items()):
                    if not process.process or not process.process.is_alive():
                        self.logger.error(f"Process for deployment {deployment_id} died unexpectedly")
                        self.db.update_deployment_status(deployment_id, "failed")
                        self.db.add_log(
                            deployment_id,
                            "ERROR",
                            "Process died unexpectedly"
                        )
                        del self.model_processes[deployment_id]

                time.sleep(1)

        except Exception as e:
            self.logger.error(f"Error in daemon main loop: {e}")
            self.stop()

def main():
    """Entry point for the daemon process."""
    import argparse

    parser = argparse.ArgumentParser(description="Tursi Daemon (tursid)")
    parser.add_argument('action', choices=['start', 'stop', 'restart'],
                       help='Action to perform')
    parser.add_argument('--pid-file', default='/tmp/tursid.pid',
                       help='Path to PID file')
    parser.add_argument('--db-path',
                       help='Path to SQLite database file')

    args = parser.parse_args()

    daemon = TursiDaemon(pid_file=args.pid_file, db_path=args.db_path)

    if args.action == 'start':
        daemon.start()
    elif args.action == 'stop':
        daemon.stop()
    elif args.action == 'restart':
        daemon.restart()

if __name__ == '__main__':
    main()
