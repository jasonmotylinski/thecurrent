# The Current Parser
A python script for parsing a given hour's playlist from http://thecurrent.org

## Setup
Create a Python virtual environment and install dependencies
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running
```
import playlist
playlist.get_hour(2016, 1, 24, 0)
```
