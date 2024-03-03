#!/bin/bash
export PYTHONPATH=.

source venv/bin/activate
luigi --module pipelines.thecurrent.db_tasks KCMPBackfillLastXDaysData --last-x-days=7 --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=kexp --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=kutx --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=wfuv --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=wxpn --local-scheduler