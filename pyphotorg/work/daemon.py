import os
import pause
from croniter import croniter
from datetime import datetime
import job

def executeJob():
    print("=====================================")
    print("Job starting ...")

    job.job()

    print("... Job ended !")

# ======================================
# Main
def main():
    print("Registering schedule cron ...")
    schedule_cron = os.getenv("SCHEDULE_CRON")

    schedule = croniter(schedule_cron, datetime.now())

    while True:
        next_exec = schedule.get_next(datetime)
        print("Waiting for job next execution scheduled at: {} ...".format(str(next_exec)))
        pause.until(next_exec)
        executeJob()

if __name__ == "__main__":
    # execute only if run as a script
    main()