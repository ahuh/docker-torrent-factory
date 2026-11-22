import os
import pause
from croniter import croniter
from datetime import datetime
import threading
import job
from webapp import JobController, create_server


def run_scheduler(controller):
    print("Registering schedule cron ...")
    schedule_cron = os.getenv("SCHEDULE_CRON")
    schedule = croniter(schedule_cron, datetime.now())

    while True:
        next_exec = schedule.get_next(datetime)
        controller.set_next_execution(next_exec)
        print("Waiting for job next execution scheduled at: {} ...".format(str(next_exec)))
        pause.until(next_exec)
        print("=====================================")
        print("Job starting ...")
        controller.run_scheduled_job(job.job)
        print("... Job ended !")

# ======================================
# Main
def main():
    controller = JobController()
    threading.Thread(
        target=run_scheduler,
        args=(controller,),
        daemon=True,
    ).start()

    port = int(os.getenv("WEB_PORT", "8080"))
    server = create_server(controller, port=port)
    print("Pyphotorg web app listening on port {} ...".format(port))
    server.serve_forever()

if __name__ == "__main__":
    # execute only if run as a script
    main()