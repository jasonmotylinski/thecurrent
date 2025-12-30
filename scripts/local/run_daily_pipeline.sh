#!/bin/bash
export PYTHONPATH=.

source venv/bin/activate
luigi --module pipelines.thecurrent.db_tasks KCMPBackfillLastXDaysData --last-x-days=7 --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=kexp --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=kutx --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=wfuv --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=wxpn --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=kcrw --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=kuom --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=wfmu --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=ksbr --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=kwss --local-scheduler
luigi --module pipelines BackfillLastXDaysData --last-x-days=7 --service-name=wext --local-scheduler

# Spotify artist enrichment (runs after all station data is loaded)
luigi --module pipelines.spotify.db_tasks SpotifyArtistsBackfillLastXDays --last-x-days=7 --local-scheduler