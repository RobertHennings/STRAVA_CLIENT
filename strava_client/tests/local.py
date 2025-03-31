import os
import sys
import gpxpy
import gpxpy.gpx
import plotly.express as px
import plotly.graph_objs as go

# Testing related variables
MANUAL_TEST = False
FIRST_TIME_USER_TEST = False
SAVE_FILES = False
USE_PREDEFINED_SETTING = True
CREATE_HEATMAP = False
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

import config as cfg
# settings
CLIENT_ID = cfg.CLIENT_ID
CLIENT_SECRET = cfg.CLIENT_SECRET
PROJECT_PATH = cfg.PROJECT_PATH
BASE_URL = cfg.BASE_URL
ERROR_CODES_DICT = cfg.ERROR_CODES_DICT
CLIENT_CREDENTIAL_FILE_NAME = cfg.CLIENT_CREDENTIAL_FILE_NAME
CLIENT_CREDENTIAL_PATH = cfg.CLIENT_CREDENTIAL_PATH
SUCCESS_CODES_DICT = cfg.SUCCESS_CODES_DICT
COLOR_MAP = cfg.COLOR_MAP
SPLIT_COLNAMES_DICT = cfg.SPLIT_COLNAMES_DICT
BOUNDING_BOX = cfg.BOUNDING_BOX

if MANUAL_TEST:
    if FIRST_TIME_USER_TEST:
        print("First time user test")
        from strava_client import StravaClient

        strava_client_instance = StravaClient(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
            )
        # Open the provided one time use URL
        auth_url = "http://localhost/?state=&code=SOME_CODE&scope=read,activity:read_all"
        new_code = strava_client_instance.get_code_from_localhost_url(url=auth_url)
        # With the new obtained one time use code load and save
        # the actual valid credentials
        client_credential_file_name = "credentials.json"
        client_credential_path = "path/to/StravaProject"
        
        credentials = strava_client_instance.get_new_strava_credentials(
                    code=new_code,
                    client_credential_file_name=client_credential_file_name,
                    save_credentials=True,
                    client_credential_path=client_credential_path
                    )
        # the loaded and saved credentials have been automatically set as
        # attributes for the client instance, the client instance can therefore
        # be directly used to load data:
        activities_df = strava_client_instance.get_strava_activities(
            save_activities=True,
            activities_file_name="activities.csv",
            activities_path=CLIENT_CREDENTIAL_PATH
            )
        print(activities_df)
    else:
        # Either directly use the finished specified client
        # from the strava_client.py file
        # or load the general class and set the needed credential relevant
        # settings here in the scripting file
        if USE_PREDEFINED_SETTING:
            # First variant
            from strava_client import strava_client
            strava_client_instance = strava_client
        else:
            # Second variant
            from strava_client import StravaClient
            strava_client_instance = StravaClient(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                client_credential_file_name=CLIENT_CREDENTIAL_FILE_NAME, # NEEDS TO BE PROVIDED
                client_credential_path=CLIENT_CREDENTIAL_PATH   # NEEDS TO BE PROVIDED
            )
        # load the overview of all activities of the athlete and save it directly
        activities_df = strava_client_instance.get_strava_activities(
            save_activities=False,
            activities_file_name="activities.csv",
            activities_path=CLIENT_CREDENTIAL_PATH
            )
        print(activities_df)
        # Next check which activity ids need to be downloaded and are new since the last
        # saving of the activities
        ids_not_existing = strava_client_instance.get_nonexisting_activity_ids(
            existing_activity_ids=activities_df["id"]
            )
        print(f"IDs not existing: {ids_not_existing}")
        # Load the data for the remaining non existing activity ids
        # per default the .gpx and the .csv files are saved for the later
        # created heatmap of the selected activities
        if SAVE_FILES:
            strava_client_instance.save_not_existing_data(
                activities_df=activities_df,
                ids_not_existing=ids_not_existing
                )
        # OPTIONAL: Look at the specifics of one activity
        activity_id = activities_df["id"][0]
        activity_data = strava_client_instance.get_strava_activity(
                    activity_id=activity_id,
                    )
        activity_type = activity_data.get("type")
        activity_stream = strava_client_instance.get_activity_stream(
            activity_id=activity_id,
        )
        stream = strava_client_instance.unpack_activity_stream(stream_response=activity_stream)
        # save the latitude and longitude parameters as gpx file
        if SAVE_FILES:
            strava_client_instance.save_activity_gpx(
                stream=stream,
                activitiy_gpx_file_name=f"{activity_id}.gpx",
                activitiy_gpx_path=f"{CLIENT_CREDENTIAL_PATH}/activitiy_gpx",
                )
            strava_client_instance.save_activity_csv(
                stream=stream,
                activitiy_csv_file_name=f"{activity_id}.csv",
                activitiy_csv_path=f"{CLIENT_CREDENTIAL_PATH}/activitiy_csv"
                )
        # bring the latitude and longitude parameters in a plotting format
        activity_stream_data_long_format = strava_client_instance.get_long_format_stream_data(
            activity_id=activity_id,
            activity_type=activity_type,
            stream=stream
            )

        # Transform the following simple plot to a method as well
        fig = px.scatter_mapbox(
            activity_stream_data_long_format,
            lat='lat',
            lon='lon',
            # mapbox_style="open-street-map",
            mapbox_style="carto-darkmatter",
            color="activity_type",
            color_discrete_map=COLOR_MAP,
            zoom=10
            )
        fig.show()

        # PLOTTING THE ACTIVITY HEATMAP FOR ALL SELECTED ACTIVITIES
        stream_data_long_format_df_ = strava_client_instance.load_data_from_gpx_files(
                activities_df=activities_df
                )
        print(stream_data_long_format_df_)
        # Apply potential filters to the data that should be plotted
        activity_type = ["Run", "Ride", "Walk"]
        activity_year = [2020, 2021, 2022, 2023, 2024, 2025]
        activity_name = None
        # Include all coordinates
        bounding_box={
            'latitude_top_right': None, 'longitude_top_right': None,
            'latitude_top_left': None, 'longitude_top_left': None,
            'latitude_bottom_left': None, 'longitude_bottom_left': None,
            'latitude_bottom_right': None, 'longitude_bottom_right': None
            }
        # Include specific area - like the Kiel area
        bounding_box_kiel = BOUNDING_BOX
        # Apply filters
        stream_data_long_format_df_filtered = strava_client_instance.activities_filter(
            activities_df=activities_df,
            activities_coordinates_df=stream_data_long_format_df_,
            activity_type=activity_type,
            activity_year=activity_year,
            activity_name=activity_name,
            bounding_box=bounding_box
            )

        # Next create the activity heatmap
        if CREATE_HEATMAP:
            from util.ActivityHeatmap import StravaActivitiesHeatmap
            import pandas as pd
            stream_data_long_format_df_ = pd.read_csv(f"{PROJECT_PATH}/stream_data_long_format_df.csv")
            activities_df = pd.read_csv(f"{PROJECT_PATH}/activities.csv")
            heatmap_filename = "strava-activities-heatmap"
            saving_file_path = f"{PROJECT_PATH}/src/Output/"
            # centered Kiel coordinates
            heatmap_center = [
                        54.340608, # latitude
                        10.151013, # longitude
                    ]
            activity_colors = COLOR_MAP

            strava_activities_heatmap_instance = StravaActivitiesHeatmap(
                activities_df=activities_df,
                activities_coordinates_df=stream_data_long_format_df_,
                heatmap_filename=heatmap_filename,
                activity_colors=activity_colors
            )
            # create and save the .html file
            strava_activities_heatmap_object = strava_activities_heatmap_instance.create_html(
                        heatmap_html_file_path=saving_file_path,
                        heatmap_center=heatmap_center,
                        return_map_data=True,
                        save_html=False,
                        map_zoom_start=13,
                        )
            print(type(strava_activities_heatmap_object))
            strava_activities_heatmap_object.show_in_browser()
            # Display json data
            # strava_activities_heatmap_object.to_json()
            # create and save the .png file
            if SAVE_FILES:
                strava_activities_heatmap_instance.create_png(
                    heatmap_png_file_path=saving_file_path,
                    png_size=(4000, 2000),
                    png_dpi=(1000, 1000),
                    font_path_statistics=os.path.join(r"/Library/Fonts/Arial Unicode.ttf"),
                    font_size_statistics=30, # must be an int
                    text_color_statistics=(255, 255, 255) # white
                    )
                # create and save the .pdf file from the .png file
                strava_activities_heatmap_instance.create_pdf(
                    heatmap_png_file_path=saving_file_path,
                    heatmap_png_filename=f"{heatmap_filename}.png",
                    heatmap_pdf_file_path=saving_file_path
                    )
