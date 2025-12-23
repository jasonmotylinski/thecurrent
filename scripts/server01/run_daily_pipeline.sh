#!/bin/bash

cd /home/jason/code/thecurrent
export PYTHONPATH=.
source /home/jason/code/thecurrent/venv/bin/activate
luigi --module pipelines.thecurrent.db_tasks KCMPBackfillLastXDaysData --last-x-days=7 --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=kexp --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=kutx --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=wfuv --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=wxpn --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=kcrw --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=kuom --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=kkxt --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=wehm --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=wnxp --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=wyep --local-scheduler

# Spotify artist enrichment (runs after all station data is loaded)
luigi --module pipelines.spotify.db_tasks SpotifyArtistsBackfillLastXDays --last-x-days=7 --local-scheduler