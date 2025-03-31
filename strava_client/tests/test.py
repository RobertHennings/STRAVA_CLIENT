import sys
import os
import pandas as pd
import plotly.graph_objs as go
import datetime as dt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config as cfg
client_credential_path = cfg.CLIENT_CREDENTIAL_PATH
from strava_client import strava_client

MANUAL_TEST = False



if MANUAL_TEST:
    # Load data
    activities_df = strava_client.get_strava_activities(
        save_activities=False,
        activities_file_name="activities.csv",
        activities_path=client_credential_path
        )
    print(activities_df)

