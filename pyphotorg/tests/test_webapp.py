import json
from pathlib import Path
import sys
import threading
import time
import unittest
from urllib.request import Request, urlopen
from unittest import mock

# Make the app's script modules importable when tests run from pyphotorg/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "work"))

import webapp


class WebAppTests(unittest.TestCase):
    def test_server_serves_page_and_status(self):
        controller = webapp.JobController()
        server = webapp.create_server(controller, host="127.0.0.1", port=0)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.start()
        try:
            with urlopen("http://127.0.0.1:{}/".format(server.server_port)) as response:
                page = response.read().decode("utf-8")
            self.assertIn("Next execution", page)
            self.assertIn("window.confirm", page)
            self.assertIn('content="dark"', page)
            self.assertIn("font-family: Inter", page)
            self.assertIn('src="/favicon.png"', page)
            self.assertIn("width: 48px; height: 48px", page)
            self.assertNotIn("Photo library manager", page)

            with urlopen("http://127.0.0.1:{}/favicon.png".format(server.server_port)) as response:
                self.assertEqual(response.headers.get_content_type(), "image/png")
                self.assertEqual(response.read(), Path(webapp.FAVICON_PNG_PATH).read_bytes())
            with urlopen("http://127.0.0.1:{}/favicon.ico".format(server.server_port)) as response:
                self.assertEqual(response.headers.get_content_type(), "image/x-icon")
                self.assertEqual(response.read(), Path(webapp.FAVICON_PATH).read_bytes())

            with urlopen(
                "http://127.0.0.1:{}/api/status".format(server.server_port)
            ) as response:
                status = json.loads(response.read().decode("utf-8"))
            self.assertFalse(status["running"])
            self.assertIsNone(status["next_execution"])

            with mock.patch.object(controller, "start_manual_job", return_value=True):
                request = Request(
                    "http://127.0.0.1:{}/api/job".format(server.server_port),
                    data=b"",
                    method="POST",
                )
                with urlopen(request) as response:
                    result = json.loads(response.read().decode("utf-8"))
                self.assertEqual(response.status, 202)
                self.assertTrue(result["accepted"])
        finally:
            server.shutdown()
            server.server_close()
            server_thread.join()

    def test_manual_job_reports_progress_and_serializes_operations(self):
        controller = webapp.JobController()
        started = threading.Event()
        release_job = threading.Event()

        def fake_job(progress_callback):
            progress_callback(40, "Processing files")
            started.set()
            release_job.wait(timeout=3)

        with mock.patch.object(webapp.job, "job", side_effect=fake_job):
            self.assertTrue(controller.start_manual_job())
            self.assertTrue(started.wait(timeout=3))
            self.assertFalse(controller.start_manual_job())
            self.assertFalse(controller.start_cache_clean())
            status = controller.get_status()
            self.assertTrue(status["running"])
            self.assertEqual(status["progress"], 40)
            self.assertEqual(status["message"], "Processing files")

            release_job.set()
            deadline = time.monotonic() + 3
            while controller.get_status()["running"] and time.monotonic() < deadline:
                time.sleep(0.01)

        status = controller.get_status()
        self.assertFalse(status["running"])
        self.assertEqual(status["progress"], 100)
        self.assertEqual(status["message"], "Complete")


if __name__ == "__main__":
    unittest.main()
