import json
import os
import threading
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import job
import manual_clean_cache


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pyphotorg</title>
  <style>
    body { font: 16px system-ui, sans-serif; max-width: 38rem; margin: 3rem auto; padding: 0 1rem; color: #222; }
    h1 { margin-bottom: 1.5rem; }
    section { border: 1px solid #ddd; border-radius: .5rem; padding: 1rem; margin: 1rem 0; }
    button { font: inherit; padding: .55rem .9rem; margin: .5rem .5rem 0 0; cursor: pointer; }
    button:disabled { cursor: wait; opacity: .6; }
    progress { width: 100%; height: 1.2rem; }
    #message { min-height: 1.5rem; }
  </style>
</head>
<body>
  <h1>Pyphotorg</h1>
  <section>
    <h2>Schedule</h2>
    <p>Next execution: <strong id="next-execution">Loading...</strong></p>
  </section>
  <section>
    <h2>Manual job</h2>
    <progress id="progress" max="100" value="0"></progress>
    <p id="message" aria-live="polite">Loading status...</p>
    <button id="run-job">Run job now</button>
    <button id="clean-cache">Clean hash cache</button>
  </section>
  <script>
    const nextExecution = document.getElementById('next-execution');
    const progress = document.getElementById('progress');
    const message = document.getElementById('message');
    const runButton = document.getElementById('run-job');
    const cleanButton = document.getElementById('clean-cache');

    async function refresh() {
      try {
        const response = await fetch('/api/status', { cache: 'no-store' });
        if (!response.ok) throw new Error('Status request failed');
        const status = await response.json();
        nextExecution.textContent = status.next_execution
          ? new Date(status.next_execution).toLocaleString()
          : 'Not scheduled';
        progress.value = status.progress;
        message.textContent = status.error
          ? `${status.message}: ${status.error}`
          : `${status.message} (${status.progress}%)`;
        runButton.disabled = status.running;
        cleanButton.disabled = status.running;
      } catch (error) {
        message.textContent = 'Could not load application status.';
      }
    }

    async function postAction(path) {
      const response = await fetch(path, { method: 'POST' });
      const result = await response.json();
      if (!response.ok) message.textContent = result.error || 'Could not start operation.';
      await refresh();
    }

    runButton.addEventListener('click', () => postAction('/api/job'));
    cleanButton.addEventListener('click', () => {
      if (window.confirm('Clear all cached file hashes?')) postAction('/api/clean-cache');
    });
    refresh();
    window.setInterval(refresh, 1000);
  </script>
</body>
</html>
"""


class JobController:
    """Track and serialize scheduled and manually requested operations."""

    def __init__(self):
        self._condition = threading.Condition()
        self._status = {
            "running": False,
            "kind": None,
            "progress": 0,
            "message": "Idle",
            "error": None,
            "next_execution": None,
        }

    def get_status(self):
        with self._condition:
            return self._status.copy()

    def set_next_execution(self, next_execution):
        with self._condition:
            if next_execution.tzinfo is None:
                next_execution = next_execution.astimezone()
            self._status["next_execution"] = next_execution.isoformat()

    def _begin_locked(self, kind):
        if self._status["running"]:
            return False
        self._status.update(
            running=True,
            kind=kind,
            progress=0,
            message="Starting",
            error=None,
        )
        return True

    def _execute(self, task):
        def report_progress(progress, message):
            with self._condition:
                self._status["progress"] = max(0, min(100, round(progress)))
                self._status["message"] = message

        error = None
        try:
            task(report_progress)
        except Exception as exception:
            error = str(exception)
            traceback.print_exc()
        with self._condition:
            self._status["running"] = False
            self._status["error"] = error
            if error is None:
                self._status["progress"] = 100
                self._status["message"] = "Complete"
            else:
                self._status["message"] = "Failed"
            self._condition.notify_all()

    def _start_background(self, kind, task):
        with self._condition:
            if not self._begin_locked(kind):
                return False
        threading.Thread(target=self._execute, args=(task,), daemon=True).start()
        return True

    def start_manual_job(self):
        return self._start_background("Manual job", lambda report: job.job(report))

    def start_cache_clean(self):
        def clean_cache(report):
            report(5, "Cleaning hash cache")
            manual_clean_cache.main()
            report(100, "Cache clean complete")

        return self._start_background("Clean cache", clean_cache)

    def run_scheduled_job(self, task):
        with self._condition:
            while self._status["running"]:
                self._condition.wait()
            self._begin_locked("Scheduled job")
        self._execute(lambda report: task(report))


def create_server(controller, host="0.0.0.0", port=None):
    class RequestHandler(BaseHTTPRequestHandler):
        def _send(self, status_code, body, content_type):
            encoded = body.encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(encoded)

        def do_GET(self):
            if self.path == "/":
                self._send(200, PAGE, "text/html; charset=utf-8")
            elif self.path == "/api/status":
                self._send(
                    200,
                    json.dumps(controller.get_status()),
                    "application/json; charset=utf-8",
                )
            else:
                self._send(404, "Not found", "text/plain; charset=utf-8")

        def do_POST(self):
            if self.path == "/api/job":
                accepted = controller.start_manual_job()
                error = None if accepted else "An operation is already running."
            elif self.path == "/api/clean-cache":
                accepted = controller.start_cache_clean()
                error = None if accepted else "An operation is already running."
            else:
                self._send(404, "Not found", "text/plain; charset=utf-8")
                return

            status_code = 202 if accepted else 409
            self._send(
                status_code,
                json.dumps({"accepted": accepted, "error": error}),
                "application/json; charset=utf-8",
            )

        def log_message(self, format_string, *args):
            return

    return ThreadingHTTPServer(
        (host, int(os.getenv("WEB_PORT", "8080")) if port is None else port),
        RequestHandler,
    )
