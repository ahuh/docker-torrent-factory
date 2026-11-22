import json
import os
import threading
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import job
import manual_clean_cache


WORK_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(WORK_DIR)


def _asset_path(asset_name):
    for asset_dir in (WORK_DIR, PROJECT_DIR):
        asset_path = os.path.join(asset_dir, asset_name)
        if os.path.isfile(asset_path):
            return asset_path
    return os.path.join(WORK_DIR, asset_name)


FAVICON_PATH = _asset_path("pyphotorg_favicon.ico")
FAVICON_PNG_PATH = _asset_path("pyphotorg_favicon.png")


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <link rel="icon" type="image/png" href="/favicon.png">
  <link rel="alternate icon" href="/favicon.ico">
  <title>Pyphotorg</title>
  <style>
    :root {
      color-scheme: dark;
      font-family: Inter, "Segoe UI Variable", system-ui, sans-serif;
      color: #edf2fb;
      background: #0b1020;
      font-synthesis: none;
      text-rendering: optimizeLegibility;
      -webkit-font-smoothing: antialiased;
    }
    * { box-sizing: border-box; }
    body {
      min-height: 100vh;
      margin: 0;
      padding: 3rem 1.25rem;
      background: radial-gradient(ellipse at 50% 0%, #172443 0%, #0b1020 55%);
    }
    main { width: min(100%, 42rem); margin: 0 auto; }
    .brand { display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem; }
    .brand img { width: 48px; height: 48px; border-radius: .75rem; }
    h1 { margin: 0; font-size: clamp(2rem, 7vw, 2.75rem); letter-spacing: -.045em; }
    section {
      margin: 1rem 0;
      padding: 1.5rem;
      border: 1px solid #27334c;
      border-radius: 1rem;
      background: rgb(18 27 46 / 88%);
      box-shadow: 0 1rem 2.5rem rgb(0 0 0 / 18%);
    }
    h2 { margin: 0 0 1rem; font-size: 1.1rem; letter-spacing: -.02em; }
    .schedule { margin: 0; color: #aab8d0; }
    .schedule strong { display: block; margin-top: .45rem; color: #f3f6fc; font-size: 1.05rem; }
    progress {
      display: block;
      width: 100%;
      height: .6rem;
      overflow: hidden;
      border: 0;
      border-radius: 1rem;
      background: #293650;
      accent-color: #8b9cff;
    }
    progress::-webkit-progress-bar { border-radius: 1rem; background: #293650; }
    progress::-webkit-progress-value { border-radius: 1rem; background: linear-gradient(90deg, #6478f5, #9b8cff); }
    progress::-moz-progress-bar { border-radius: 1rem; background: linear-gradient(90deg, #6478f5, #9b8cff); }
    #message { min-height: 1.5rem; margin: 1rem 0 .5rem; color: #aab8d0; }
    .actions { display: flex; flex-wrap: wrap; gap: .75rem; margin-top: 1.25rem; }
    button {
      min-height: 2.75rem;
      padding: .65rem 1rem;
      border: 1px solid #3c4964;
      border-radius: .7rem;
      background: #202b42;
      color: #edf2fb;
      font: inherit;
      font-size: .9rem;
      font-weight: 650;
      cursor: pointer;
      transition: background .15s ease, border-color .15s ease, transform .15s ease;
    }
    button:hover:not(:disabled) { border-color: #6678d8; background: #2a3856; transform: translateY(-1px); }
    button:focus-visible { outline: 2px solid #a6b0ff; outline-offset: 3px; }
    button.primary { border-color: #7181ff; background: #6575ed; color: #fff; }
    button.primary:hover:not(:disabled) { border-color: #9aa5ff; background: #7887ff; }
    button:disabled { cursor: wait; opacity: .55; }
    @media (max-width: 34rem) {
      body { padding: 2rem 1rem; }
      section { padding: 1.25rem; }
      .actions { flex-direction: column; }
      button { width: 100%; }
    }
  </style>
</head>
<body>
  <main>
    <header class="brand">
      <img src="/favicon.png" alt="">
      <h1>Pyphotorg</h1>
    </header>
    <section>
      <h2>Schedule</h2>
      <p class="schedule">Next execution<strong id="next-execution">Loading...</strong></p>
    </section>
    <section>
      <h2>Manual job</h2>
      <progress id="progress" max="100" value="0" aria-label="Job progress"></progress>
      <p id="message" aria-live="polite">Loading status...</p>
      <div class="actions">
        <button class="primary" id="run-job">Run job now</button>
        <button id="clean-cache">Clean hash cache</button>
      </div>
    </section>
  </main>
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
            encoded = body if isinstance(body, bytes) else body.encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(encoded)

        def do_GET(self):
            if self.path == "/":
                self._send(200, PAGE, "text/html; charset=utf-8")
            elif self.path in ("/favicon.ico", "/favicon.png"):
                asset_path = FAVICON_PATH if self.path.endswith(".ico") else FAVICON_PNG_PATH
                try:
                    with open(asset_path, "rb") as favicon:
                        body = favicon.read()
                except OSError:
                    self._send(404, "Not found", "text/plain; charset=utf-8")
                    return
                content_type = "image/x-icon" if self.path.endswith(".ico") else "image/png"
                self._send(200, body, content_type)
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
