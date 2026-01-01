In all csv_tasks.py the played_at date is used to determine the play year and play week using  played_at.strftime("%Y") and  played_at.strftime("%U") when the year changes. %U will return week 00 and makes reporting break.

Update all csv_tasks.py to use the isocalendar() instead for year and week:
iso_year, iso_week, iso_weekday = d.isocalendar()