#!/bin/bash

cd /var/projects/thecurrent
export PYTHONPATH=.

source /var/projects/thecurrent/venv/bin/activate
luigi --module pipelines.thecurrent.db_tasks BackfillLastXDaysData --last-x-days=7 --local-scheduler
luigi --module pipelines.kexp.db_tasks BackfillLastXDaysData --last-x-days=7 --local-scheduler
luigi --module pipelines.kutx.db_tasks BackfillLastXDaysData --last-x-days=7 --local-scheduler
luigi --module pipelines.wxpn.db_tasks BackfillLastXDaysData --last-x-days=7 --local-scheduler
luigi --module pipelines.wfuv.db_tasks BackfillLastXDaysData --last-x-days=7 --local-scheduler