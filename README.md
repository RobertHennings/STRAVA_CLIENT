# Strava Client API (for activity heatmap generation)
<p align="center">
  <img src="https://raw.githubusercontent.com/RobertHennings/Strava_CLIENT/master/strava_client/src/Logo/Strava_Logo.svg" 
       width="200"/>
</p>

# DISCLAIMER: This API Client is not associated with the Strava brand or registered trademark in any kind - it is a pure personal - nonprofit/non commercial open source software project
The main purpose of this simple API client is the comfortable retrieval of athlete activities data and epecially the storing of the GPS coordinates of activities in order to be able to generate a custom, high resolution activity heatmap. The [Strava API](https://developers.strava.com) provides a comprehensive [documentation](https://developers.strava.com/docs/reference/#api-models-StreamSet), as well as the already existing API client [Strava lib](https://stravalib.readthedocs.io/en/latest/).

The client here features additional saving methods for the purpose of generating an activity heatmap, like other example projects that can be found [here](https://github.com/roboes/strava-local-heatmap-tool?tab=readme-ov-file) or [here](). The disadvantage here is, that they miss comfotable data updating routines to always be up to date with the users of Strava athletes activity data. This API Client combines both of these ideas.
<br>Further resources that were used for development and that need to be credited:
- 1) [Towards Data Science](https://towardsdatascience.com/using-the-strava-api-and-pandas-to-explore-your-activity-data-d94901d9bfde/)
- 2) [Medium Article](https://medium.com/swlh/using-python-to-connect-to-stravas-api-and-analyse-your-activities-dummies-guide-5f49727aac86)
- 3) [Michael Hainke Blogpost](https://www.hainke.ca/index.php/2018/08/23/using-the-strava-api-to-retrieve-activity-data/)
- 4) [GPX from Strava Library](https://github.com/PhysicsDan/GPXfromStravaAPI/blob/main/GPXFromStrava/main.py)
- 5) [Towards Data Science](https://towardsdatascience.com/data-science-for-cycling-how-to-read-gpx-strava-routes-with-python-e45714d5da23/)
- 6) [Existing Strava Client](https://github.com/sshevlyagin/strava-api-v3.1/tree/master)

<br>[Other interesting Strava projects](https://github.com/zwinslett/strava-shoe-explore)

Since especially the authorization imposed a little challenge, the [official documentation](https://developers.strava.com/docs/authentication/) can also be quite helpful.

## Installation - Not yet available on PyPi
`pip install strava_client`
<br>or:</br>
`pip3 install strava_client`
# Setting up the personal Strava API in the Strava (Web) platform and obtain client id and client secret
In order to interact with the Strava API endpoint, the perosnal API has to be set up in the Web platform of Strava to receive the needed authorization parameters.
The following quick guide shows to get there:
- 1. Visit: https://www.strava.com/settings/api
- 2. Create a new personal API and obtain the following parameters:
     <p align="center">
     <img src="https://raw.githubusercontent.com/RobertHennings/STRAVA_CLIENT/refs/heads/master/strava_client/src/Installation/StravaPersonal_API_View.png" 
          width="800"/>
     </p>
- 3. Clone the repository or download the client via `pip` or `pip3`
- 4. Rename the `example_config.py` to `config.py` and fill in the personal data
here: 
```python
CLIENT_ID = 123456 # personal client id - stays constant
CLIENT_SECRET = "bbudo82z92phdpd8E28014714" # personal client secret - stays constant
CLIENT_CREDENTIAL_PATH = r'path/to/StravaProject' # location of project
```
# Example Usage
There are two main ways how to use and set up the client:
<br>(<strong>Rename the `example_config.py` to `config.py`</strong> after cloning or downloading anf fill in your data)
- 1. Defining all necessary default parameters in the `config.py` file, importing them via: `import config as cfg` into the <strong>scripting file (.py file)</strong>, then setting the needed client instance arguments from the `cfg` variables explicitly when instantiating the client intance
- 2. Defining all necessary default parameters in the `config.py` file, importing them via: `import config as cfg` into the <strong>`strava_client.py`</strong>, there setting up the default variant of the strava client that can be directly imported with these pre-setting into the scripting file (.py file)


<strong>IMPORTANT</strong>
<br>For the first time use, it is necessary to follow the first procedure, described in more detail down below.
After the credentials have been obtained, saved and the needed static path and file name variables have been set, the second procedure can be used comfortably.

With custom settings (imported from the config.py file into the scripting file(.py) or directly set in the scripting file) - ASSUMED: first time use and no credentials are saved or existing:
```python
import config as cfg
CLIENT_ID = cfg.CLIENT_ID
CLIENT_SECRET = cfg.CLIENT_SECRET
DIFFERENT_BASE_URL = "https://www.strava.com/different/version/number"

from strava_client import StravaClient
strava_client_instance = StravaClient(
     base_url=DIFFERENT_BASE_URL,
     client_id=CLIENT_ID,
     client_secret=CLIENT_SECRET
     )
```
If the client has already been used and set up - credentials were loaded - they have to be provided:
```python
import config as cfg
CLIENT_ID = cfg.CLIENT_ID
CLIENT_SECRET = cfg.CLIENT_SECRET
DIFFERENT_BASE_URL = "https://www.strava.com/different/version/number"
CLIENT_CREDENTIAL_FILE_NAME = cfg.CLIENT_CREDENTIAL_FILE_NAME
CLIENT_CREDENTIAL_PATH = cfg.CLIENT_CREDENTIAL_PATH

from strava_client import StravaClient
strava_client_instance = StravaClient(
     base_url=DIFFERENT_BASE_URL,
     client_id=CLIENT_ID,
     client_secret=CLIENT_SECRET,
     client_credential_file_name=CLIENT_CREDENTIAL_FILE_NAME,
     client_credential_path=CLIENT_CREDENTIAL_PATH
     )
```
With using the defined default settings (imported from the config.py in the strava_client.py):
```python
from strava_client import strava_client
strava_client_instance = strava_client
```
In the `strava_client.py` file, the default settings can be changed:
```python
strava_client = StravaClient(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_credential_file_name=CLIENT_CREDENTIAL_FILE_NAME,
    client_credential_path=CLIENT_CREDENTIAL_PATH
    )
```
With proxy settings:
```python
from strava_client import StravaClient
proxies = {
     'https':'https--proxy',
     'http': 'http--proxy'
}
verify = True
strava_client_instance = StravaClient(
     proxies=proxies,
     verify=verify
     )
```
## 1. First time use and authentification
After installation or cloning of the respository, there are the following files present at the regarding location, that are important to obtain the needed credentials:
- 1) `example_config.py`
- 2) `credentials.json`

<strong>Rename the `example_config.py` to `config.py`</strong>
<br>In the `config.py` define the following parameters, that will appear as:
```python
CLIENT_ID = 123456
CLIENT_SECRET = "bbudo82z92phdpd8E28014714"
CLIENT_CREDENTIAL_PATH = r'path/to/StravaProject'
```
### 1.1 Other config parameters found in the config.py
Other not utterly important static variables that can be imported, used and/or further customized are the following present:
```python
PROJECT_PATH = r"path/to/StravaProject"
CLIENT_CREDENTIAL_FILE_NAME = r'credentials.json'
BASE_URL = "https://www.strava.com/api/v3/"
OAUTH_URL = "https://www.strava.com/oauth/authorize"
ERROR_CODES_DICT = {
        400: {
            "message": "Error",
            "return_": None
        },
        401: {
            "message": "Error",
            "return_": None
        }
    }
SUCCESS_CODES_DICT = {
    200: {
        "message": "URL succesfully retrived",
        "return_": "Success"
        }
}
COLOR_MAP = {
    'Run': '#FF4500',
    'Ride': '#1E90FF',
    'Swim': '#00CED1',
    'Walk': '#32CD32'
}

SPLIT_COLNAMES_DICT = {
    "Run": [
        'average_speed',
        'distance',
        'elapsed_time',
        'elevation_difference',
        'moving_time',
        'pace_zone', 
        'split',
        'id',
        'date'],
    "Walk": [], # add the data item names
    "Ride": [], # add the data item names
    "Rowing": [], # add the data item names
    "Swim": [], # add the data item names
    "Workout": [], # add the data item names
    "Elliptical": [] # add the data item names
    # add more activity types
}
REQUEST_TIMEOUT = 90

BOUNDING_BOX = {
    'latitude_top_right': 54.5,
    'longitude_top_right': 10.3,
    'latitude_top_left': 54.5,
    'longitude_top_left': 10.0,
    'latitude_bottom_left': 54.2,
    'longitude_bottom_left': 10.0,
    'latitude_bottom_right': 54.2,
    'longitude_bottom_right': 10.3,
}
```
Brief explanation of the <strong>main config parameters</strong>:
| Parameter | Setting (example) | Data type (python) | Description |
| :--------- | :-------------: | :----------: | :---------- |
| CLIENT_ID| 123456| int | The obtained athlete or user id that is displayed in the online API section of the Strava website.|
| CLIENT_SECRET | "bbudo82z92phdpd8E28014714" | str | The obtained athlete or user secret that is displayed in the online API section of the Strava website.|
| CLIENT_CREDENTIAL_PATH | "path/to/StravaProject" | raw str | This defines where the credential file `credentials.json` exists and will be read from. |

<br>Brief explanation of the <strong>optional config parameters</strong>:
| Parameter | Setting (example) | Data type (python) | Description |
| :-------- | :---------------: | :----------------: | :---------- |
| PROJECT_PATH | "path/to/StravaProject" | raw str | Defining the general, overarching project loaction. Can be used in f-strings to define where the `credentials.json` is or should be saved and where the files should be saved or loaded from.
| CLIENT_CREDENTIAL_FILE_NAME | r'credentials.json' | raw str | Name of the file that holds the credentials, saved as .josn format|
| BASE_URL | "https://www.strava.com/api/v3/" | str | Base endpoint of the Strava API |
| OAUTH_URL | "https://www.strava.com/oauth/authorize" | str | Endpoint for authorization |
| ERROR_CODES_DICT | {400: {"message": "Error", "return_": None}, 401: {"message": "Error", "return_": None}} | Dict[int, Dict[str, str]] | Customizable error codes dict for more precise logging and control flows |
| SUCCESS_CODES_DICT | {200: {"message": "URL succesfully retrived", "return_": "Success"}} | Dict[int, Dict[str, str]] | Customizable success codes dict for more precise logging and control flows |
| COLOR_MAP | {'Run': '#FF4500', 'Ride': '#1E90FF', 'Swim': '#00CED1', 'Walk': '#32CD32'} | Dict[str, str] | Mapping activity types to the color that they will appear in the heatmap |
| SPLIT_COLNAMES_DICT | {"Run": ['average_speed', 'distance', 'elapsed_time', 'elevation_difference' 'moving_time', 'pace_zone', 'split', 'id', 'date'], "Walk": [], "Ride": [], "Rowing": [], "Swim": [], "Workout": [], "Elliptical": []} | Dict[str, List[str]] | The column names for the activity specific split data that can be loaded per activity type |
| REQUEST_TIMEOUT | 90 | int | Default seconds before a request timeout will be raised |
| BOUNDING_BOX | {'latitude_top_right': 54.5, 'longitude_top_right': 10.3, 'latitude_top_left': 54.5, 'longitude_top_left': 10.0, 'latitude_bottom_left': 54.2, 'longitude_bottom_left': 10.0, 'latitude_bottom_right': 54.2, 'longitude_bottom_right': 10.3} | Dict[str, float] | Bonding box of a specific area that can be used for filtering the activities in it and therefore the heatmap cutout |

### 1.2 Initialize the Strava Client (for the first time):
<strong>IMPORTANT</strong>
<br>Do not set parameters for the arguments: `client_credential_path` and `client_credential_file_name` as these have to evaluate to `None` (as set per default) to trigger the first time authorization procedure.
```python
import config as cfg
CLIENT_ID = cfg.CLIENT_ID
CLIENT_SECRET = cfg.CLIENT_SECRET

strava_client_instance = StravaClient(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
    )
```
After calling, the command line will display the one-time use local authorization url that needs to be opened:
```zsh
https://www.strava.com/oauth/authorize?client_id=CLIENT_ID&amp;redirect_uri=http://localhost&amp;response_type=code&amp;scope=activity:read_all
```
<br>Per default the parameters in the __init__ for `client_credential_file_name` and `client_credential_path`
are set to `None`, triggering in the `load_credentials` method the process to obtain the initially and only once needed code to obtain the actually, valid credentials that will be saved under the later given `client_credential_file_name` at the location of `client_credential_path`, once they are loaded.

The `get_authorization_url` method is triggered and provides the needed URL, the user needs to open manually by clicking or posting it into the webbrowser of choice. As alternative by setting the input argument `open_in_webbrowser=True` the URL will be automatically opened.
The user needs to click the Authorize Button, the afterwards following URL needs to be copied into the method `get_code_from_localhost_url`.
```python
auth_url = "http://localhost/?state=&code=SOME_CODE&scope=read,activity:read_all"
new_code = strava_client_instance.get_code_from_localhost_url(url=auth_url)

Code: 8249hinkbefkaöjra920q4
```
The returned one-time code needs to be provided to the method `get_new_strava_credentials` that returns the actual and valid Strava credentials. Optional arguments that can be specified are: `client_credential_file_name, save_credentials, client_credential_path`.
In case 'save_credentials' is set to 'True', the loaded credentials are saved at the provided location (`client_credential_path`, which is optional, else the credential file will be saved in the current working directory) with the provided file name (`client_credential_file_name`).
```python
client_credential_file_name = "credentials.json"
client_credential_path = "path/to/StravaProject"

credentials = strava_client_instance.get_new_strava_credentials(
          code=new_code,
          client_credential_file_name=client_credential_file_name,
          save_credentials=True,
          client_credential_path=client_credential_path
          )
print(credentials)
{'token_type': 'Bearer', 'expires_at': 178783878265, 'expires_in': 11475, 'refresh_token': 'kljsleuz923zr23haöeaä90930202', 'access_token': 'jklahr93z92z93zrbbdoa28084000kafka'}
```
Afterwards the active client instance can be used for all remaining methods.
<br>Here an example:
```python
activities_df = strava_client_instance.get_strava_activities(
            save_activities=True,
            activities_file_name="activities.csv",
            activities_path=CLIENT_CREDENTIAL_PATH
            )
print(activities_df)
id  ...                                        external_id
0    13897858819  ...           5FF71376-1E53-4B9D-919B-81E95F65F003.fit
1    13884299829  ...           D9433E71-E25E-474A-9292-58CAE17D4562.fit
2    13876026753  ...           EDFD44C5-309D-4269-BDC6-6CBB6AB0C949.fit
3    13854570273  ...           0E5FB4F5-9509-44AD-B334-D4BE835EA564.fit
4    13833626341  ...           E301F172-3923-49E1-8930-16C49F45252B.fit
..           ...  ...                                                ...
451   4049928779  ...  AA6F9352-B481-4D2E-8C9F-0002496DF332-activity.fit
452   4043759253  ...  E0381C18-3C76-4EEA-9458-E092B56FB7EA-activity.fit
453   4025099437  ...  891E5CA4-97D6-4F47-8761-9C63F3F0A8D7-activity.fit
454   4025099386  ...  23B9C2D4-63CF-4A97-BAB3-1018506AD4D4-activity.fit
455   4010358456  ...  CE11525B-B308-4F6E-A2B2-0689F3B5D294-activity.fit
```
At a later stage when a new instance is initiated or used, the saving location and the credential file name can be directly set:
```python
from strava_client import StravaClient
strava_client_instance = StravaClient(
     client_credential_file_name="credentials.json",
     client_credential_path="path/to/credentials",
     client_id=CLIENT_ID,
     client_secret=CLIENT_SECRET
     )
```
Alternatively the arguments `client_credential_file_name and client_credential_path` can be specified in the `config.py` and directly loaded in the `strava_client.py` or in the scripting file itself set and imported from the `config.py`.
Here the respective part in the `strava_client.py` file:
```python
strava_client = StravaClient(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_credential_file_name=CLIENT_CREDENTIAL_FILE_NAME,
    client_credential_path=CLIENT_CREDENTIAL_PATH
    )
```
Later in the scripting file us the client:
```python
from strava_client import strava_client
strava_client_instance = strava_client
```

## 2. Later time use and authentification
At a later stage when a new instance is initiated or used, the saving location and the credential file name can be directly set and used from now on:
```python
from strava_client import StravaClient
strava_client_instance = StravaClient(
     client_credential_file_name="credentials.json",
     client_credential_path="path/to/StravaProject",
     client_id=CLIENT_ID,
     client_secret=CLIENT_SECRET
     )
```
Alternatively the arguments `client_credential_file_name and client_credential_path` can be specified in the `config.py` and directly loaded in the `strava_client.py` or in the scripting file itself set and imported from the `config.py`.

The easiest and fastest way to create an instance is then:
```python
from strava_client import strava_client
strava_client_instance = strava_client
```

## 3. The starting point: Load the users activities (overview DataFrame)
After the client has been loaded and instanciated, the first go to point is to load the overview of the activities of the user. This overview provides the
unique activity ids that are needed in order to load the (GPS) activity stream later and all other more relevant details of the activity.
Access and load the activities overview via the method: `get_strava_activities` in the following way:
```python
save_activities = True
activities_file_name = "activities.csv"
activities_path = "path/to/StravaProject"
activities_df = strava_client_instance.get_strava_activitie
(save_activities=save_activities,
activities_file_name=activities_file_name,
activities_path=activities_path)
print(activities_df)

              id  ...                                        external_id
0    13897858819  ...           5FF71376-1E53-4B9D-919B-81E95F65F003.fit
1    13884299829  ...           D9433E71-E25E-474A-9292-58CAE17D4562.fit
2    13876026753  ...           EDFD44C5-309D-4269-BDC6-6CBB6AB0C949.fit
3    13854570273  ...           0E5FB4F5-9509-44AD-B334-D4BE835EA564.fit
4    13833626341  ...           E301F172-3923-49E1-8930-16C49F45252B.fit
..           ...  ...                                                ...
451   4049928779  ...  AA6F9352-B481-4D2E-8C9F-0002496DF332-activity.fit
452   4043759253  ...  E0381C18-3C76-4EEA-9458-E092B56FB7EA-activity.fit
453   4025099437  ...  891E5CA4-97D6-4F47-8761-9C63F3F0A8D7-activity.fit
454   4025099386  ...  23B9C2D4-63CF-4A97-BAB3-1018506AD4D4-activity.fit
455   4010358456  ...  CE11525B-B308-4F6E-A2B2-0689F3B5D294-activity.fit
```
## 4. Load and analyze single user activities
From this starting point the user can inspect and load additional details for single activities, using their distinct activity id via the method: `get_strava_activity`:
```python
activity_id = activities_df["id"][0]
print(strava_client_instance.get_strava_activity
(activity_id=activity_id)
)
{'resource_state': 3, 'athlete': {'id': 68482490001400, 'resource_state': 1}, 'name': 'Spaziergang am Nachmittag', 'distance': 4658.0, 'moving_time': 3331, 'elapsed_time': 3794, 'total_elevation_gain': 18.6, 'type': 'Walk', 'sport_type': 'Walk', 'id': 9244017101, 'start_date': '2025-02-22T16:37:15Z', 'start_date_local': '2025-02-22T17:37:15Z', 'timezone': '(GMT+01:00) Europe/Berlin', 'utc_offset': 3600.0, 'location_city': None, 'location_state': None, 'location_country': None, 'achievement_count': 0, 'kudos_count': 4, 'comment_count': 0, 'athlete_count': 1, 'photo_count': 0, 'map': {'id': 'a13699275079', 'polyline': 'u}x~HmionAWJ[FK?CKK{@GIG?WLm@l@YTQXO^ONg@\\a@LsB@UIi@g@UIM?[`@O\\Y`@c@|@_@rAYvAe@rAS^?VBD@PBbE\\~SAbADhC@XDDCLALFjFPxBBNFFJ?d@QhBa@POLGxACHGDIAeBMeF?cCGeB@{AD{A?mAEu@IcAGyB@qAH{A@aBAmDS_H@SDKFCP?lAGnAp@VHjB^^Lt@J`@Bv@Ll@BPCLBl@Xv@NXBz@@t@PJ?bAYNIDIDYGmADUHMPGxAWr@CbBWh@QLUDSJaBDMV[x@Sx@YZCh@H~@Ab@M^Ct@OZ?v@Mj@At@Qp@C~@Ql@Gb@DPGv@Mz@Sp@EFE?SQo@', 'resource_state': 3, 'summary_polyline': 'u}x~HmionAWJ[FK?CKK{@GIG?WLm@l@YTQXO^ONg@\\a@LsB@UIi@g@UIM?[`@O\\Y`@c@|@_@rAYvAe@rAS^?VBD@PBbE\\~SAbADhC@XDDCLALFbFNvBDXFFJ?d@QhBa@POLGxACHGDIAeBMeF?cCGeB@{AD{A?mAEu@IcAGyB@qAH{A@aBAmDS_H@SDKFCP?lAGnAp@VHjB^^Lt@J`@Bv@Ll@BPCLBl@Xv@NXBz@@t@PJ?bAYNIDIDYGmADUHMPGxAWr@CbBWh@QLUDSJaBDMV[x@Sx@YZCh@H~@Ab@M^Ct@OZ?v@Mj@At@Qp@C~@Ql@Gb@DPGv@Mz@Sp@EFE?SQo@'}, 'trainer': False, 'commute': False, 'manual': False, 'private': False, 'visibility': 'everyone', 'flagged': False, 'gear_id': None, 'start_latlng': [XX.YYYYY, XX.YYYYY], 'end_latlng': [XX.YYYYY, XX.YYYYY], 'average_speed': 1.398, 'max_speed': 6.594, 'has_heartrate': True, 'average_heartrate': 103.4, 'max_heartrate': 114.0, 'heartrate_opt_out': False, 'display_hide_heartrate_option': True, 'elev_high': 37.4, 'elev_low': 29.6, 'upload_id': 4994104014, 'upload_id_str': '4994104014', 'external_id': 'o822oho-4CCE-9887-99ono2.fit', 'from_accepted_tag': False, 'pr_count': 0, 'total_photo_count': 0, 'has_kudoed': False, 'description': None, 'calories': 230.0, 'perceived_exertion': None, 'prefer_perceived_exertion': None, 'segment_efforts': [], 'splits_metric': [{'distance': 1004.9, 'elapsed_time': 926, 'elevation_difference': 0.0, 'moving_time': 680, 'split': 1, 'average_speed': 1.48, 'average_grade_adjusted_speed': None, 'average_heartrate': 98.38030303030303, 'pace_zone': 0}, {'distance': 998.4, 'elapsed_time': 805, 'elevation_difference': -1.8, 'moving_time': 652, 'split': 2, 'average_speed': 1.53, 'average_grade_adjusted_speed': None, 'average_heartrate': 104.56, 'pace_zone': 0}, {'distance': 999.2, 'elapsed_time': 826, 'elevation_difference': 2.0, 'moving_time': 762, 'split': 3, 'average_speed': 1.31, 'average_grade_adjusted_speed': None, 'average_heartrate': 104.03542234332426, 'pace_zone': 0}, {'distance': 999.0, 'elapsed_time': 754, 'elevation_difference': 0.2, 'moving_time': 754, 'split': 4, 'average_speed': 1.32, 'average_grade_adjusted_speed': None, 'average_heartrate': 106.07272727272728, 'pace_zone': 0}, {'distance': 654.9, 'elapsed_time': 483, 'elevation_difference': 2.6, 'moving_time': 483, 'split': 5, 'average_speed': 1.36, 'average_grade_adjusted_speed': None, 'average_heartrate': 109.40304182509506, 'pace_zone': 0}], 'splits_standard': [{'distance': 1611.2, 'elapsed_time': 1419, 'elevation_difference': -1.2, 'moving_time': 1020, 'split': 1, 'average_speed': 1.58, 'average_grade_adjusted_speed': None, 'average_heartrate': 99.88950276243094, 'pace_zone': 0}, {'distance': 1609.7, 'elapsed_time': 1303, 'elevation_difference': 0.8, 'moving_time': 1239, 'split': 2, 'average_speed': 1.3, 'average_grade_adjusted_speed': None, 'average_heartrate': 104.74749163879599, 'pace_zone': 0}, {'distance': 1435.5, 'elapsed_time': 1072, 'elevation_difference': 3.4, 'moving_time': 1072, 'split': 3, 'average_speed': 1.34, 'average_grade_adjusted_speed': None, 'average_heartrate': 107.53146853146853, 'pace_zone': 0}], 'laps': [{'id': 964916420104, 'resource_state': 2, 'name': 'Lap 1', 'activity': {'id': 13699275079, 'visibility': 'everyone', 'resource_state': 1}, 'athlete': {'id': 67576589, 'resource_state': 1}, 'elapsed_time': 3794, 'moving_time': 3794, 'start_date': '2025-02-22T16:37:15Z', 'start_date_local': '2025-02-22T17:37:15Z', 'distance': 4656.41, 'average_speed': 1.23, 'max_speed': 6.594, 'lap_index': 1, 'split': 1, 'start_index': 0, 'end_index': 2702, 'total_elevation_gain': 18.6, 'device_watts': False, 'average_heartrate': 103.4, 'max_heartrate': 114.0}], 'photos': {'primary': None, 'count': 0}, 'stats_visibility': [{'type': 'heart_rate', 'visibility': 'everyone'}, {'type': 'pace', 'visibility': 'everyone'}, {'type': 'power', 'visibility': 'everyone'}, {'type': 'speed', 'visibility': 'everyone'}, {'type': 'calories', 'visibility': 'everyone'}], 'hide_from_home': False, 'device_name': 'Apple Watch Series 5', 'embed_token': '6cbdb36ed3dba7510946eafcffb441476e6ab67a', 'available_zones': []}
```
On a single activity level, the user can also load the GPS coordinates, and if available the completed distance at the given GPS-coordinate via the method: `get_activity_stream`:
```python
activity_id = activities_df["id"][0]
activity_stream = strava_client_instance.get_activity_stream(
    activity_id=activity_id,
)
```
Since the returned stream object is a nested `Dict`object, the method `unpack_activity_stream` makes it easier to interact with it:
```python
stream = strava_client_instance.unpack_activity_stream(stream_response=activity_stream)
```
The available data can be looked up via:
```python
print(stream.keys())
```
```zsh
dict_keys(['distance'])
```

In this case, for the given activity id, there is only the distance available but not the GPS-coordinates.

The GPS-coordinates can be saved in two ways:
- 1. As .gpx file (in an xml like file format)
- 2. As .csv file (for easier interaction)

This can be achieved via the two methods: `save_activity_gpx and save_activity_csv`:

Save .gpx file:
```python
strava_client_instance.save_activity_gpx(
    stream=stream,
    activitiy_gpx_file_name=f"{activity_id}.gpx",
    activitiy_gpx_path=f"StravaProject/activitiy_gpx",
    )
```
Save .csv file:
```python
strava_client_instance.save_activity_csv(
    stream=stream,
    activitiy_gpx_file_name=f"{activity_id}.csv",
    activitiy_gpx_path=f"StravaProject/activitiy_csv",
    )
```
For simple plotting purposes, the relevant data can be transformed into a long format, well suited to be used in plotly plots via the method: `get_long_format_stream_data`:
```python
activity_id = activities_df["id"][0]
activity_type = activity_data.get("type")
activity_stream_data_long_format = strava_client_instance.get_long_format_stream_data(
    activity_id=activity_id,
    activity_type=activity_type,
    stream=stream
    )
print(activity_stream_data_long_format)
```
## 5. Load and analyze multiple user activities
The above described methods are used here in a larger scope for multiple activities as well via the following methods.

If the user wants to download directly multiple .gpx and/or .csv GPS-coordinates files, this can be done by first checking which activity id (files) are already present and loaded using: `get_nonexisting_activity_ids`:
```python
existing_activity_ids=activities_df["id"]
ids_not_existing = strava_client_instance.get_nonexisting_activity_ids(
    existing_activity_ids=existing_activity_ids
    )
print(f"IDs not existing: {ids_not_existing}")
IDs not existing: [13876026753, 13854570273, 13833626341, 13773377598, 13744399617, 13744399616, 13627621627, 13611395907, 13593488171, 13558836251, 13466599714, 13466599704, 13335908064, 13318258604, 13318257818, 13256351233, 13218351234, 13202872284, 13195971004, 13116332217, 13102113511, 13082169418, 13061236019, 13023249538, 13023249540, 13010195971, 12997338878, 12982743271, 12964006846, 12947963067, 12924386941, 12924386956, 12924386955, 12901620493, 12901620486, 12847350566, 12791781818, 12736467979, 12699054856, 12686744251, 12680253384, 12643485631, 12640010404, 12631971440, 12623798553, 12623798651, 12599942525, 12592182565, 12588963035, 12575160178, 12558443888, 12474207740, 12435090352, 12435090351, 12415872709, 12385507375, 12357477037, 12354832219, 12342839567, 12309907896, 12309907908, 12300766323, 12282479038, 12266746864, 12265498665, 12249696569, 12238468134, 12223006001, 12197795228, 12189268734, 12182350953, 12171882580, 12163564738, 12147963277, 12127620174, 12127618269, 12112142057, 12096746395, 12078960041, 12078799092, 12059192919, 12001297381, 11994890342, 11994695896, 11972307774]
```
After the missing ids have been identified, the user can directly save both .gpx and .csv files via: `save_not_existing_data`:
```python
strava_client_instance.save_not_existing_data(
    activities_df=activities_df,
    ids_not_existing=ids_not_existing
    )
```
Optional arguments here are: `save_gpx_files, save_csv_files` for deciding whether to save both file types or only one specific and the according file locations: `activitiy_gpx_path, activitiy_csv_path`.

Once all the missing files are loaded and saved, the long format data can be created from these files via: `load_data_from_gpx_files`:
```python
stream_data_long_format_df_ = strava_client_instance.load_data_from_gpx_files(
        activities_df=activities_df
        )
print(stream_data_long_format_df_)
          lat        lon  activity_id activity_type    color
0     52.397876  13.026957  13699275079          Walk  #32CD32
1     52.397876  13.026957  13699275079          Walk  #32CD32
2     52.397876  13.026957  13699275079          Walk  #32CD32
3     52.397876  13.026957  13699275079          Walk  #32CD32
4     52.397876  13.026957  13699275079          Walk  #32CD32
...         ...        ...          ...           ...      ...
3622  54.328471  10.127527  13641221160           Run  #FF4500
3623  54.328477  10.127530  13641221160           Run  #FF4500
3624  54.328489  10.127532  13641221160           Run  #FF4500
3625  54.328501  10.127534  13641221160           Run  #FF4500
3626  54.328501  10.127534  13641221160           Run  #FF4500
```
Optional arguments here are: `color_map, type_column_name, activitiy_gpx_path`.

## 6. Creating the activity heatmap - Load and analyze multiple user activities
Since the main purpose of the client is to create and maintain the needed input data for the activity heatmap, we now turn to its set up.

The needed input data consists out of the two main data sources:
- 1. The activity overview (called activity_df in the code snippets from above)
- 2. The activity coordinates (in a long format)

These can be loaded via:
```python
from strava_client import strava_client
strava_client_instance = strava_client

activities_df = strava_client_instance.get_strava_activities(
            save_activities=True,
            activities_file_name="activities.csv",
            activities_path=CLIENT_CREDENTIAL_PATH
            )

ids_not_existing = strava_client_instance.get_nonexisting_activity_ids(
            existing_activity_ids=activities_df["id"]
            )

strava_client_instance.save_not_existing_data(
                activities_df=activities_df,
                ids_not_existing=ids_not_existing
                )

stream_data_long_format_df_ = strava_client_instance.load_data_from_gpx_files(
                activities_df=activities_df
                )

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
BOUNDING_BOX = cfg.BOUNDING_BOX 
bounding_box_kiel = BOUNDING_BOX
# Apply filters
stream_data_long_format_df_filtered = strava_client_instance.activities_filter(
     activities_df=activities_df,
     activities_coordinates_df=stream_data_long_format_df_,
     activity_type=activity_type, # only include the activities that fall into one of the types
     activity_year=activity_year, # only include the activities that fall into one of the years
     activity_name=activity_name, # only include the activities that match one of the names
     bounding_box=bounding_box # only include the activities that fall into the location area
     )

# Actually create the heatmap
from util.ActivityHeatmap import StravaActivitiesHeatmap
import config as cfg

PROJECT_PATH = cfg.PROJECT_PATH
COLOR_MAP = cfg.COLOR_MAP

heatmap_filename = "strava-activities-heatmap"
saving_file_path = f"{PROJECT_PATH}/src/Output/"
# centered Kiel coordinates
heatmap_center = [
          54.32133, # latitude
          10.13489, # longitude
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
          return_map_data=True
          )
# create and save the .png file
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
```

## 7. Running the strava client locally in a scripting file (.py)
To run the strava client locally (i.e. after cloning the repository), one can just simply create a virtual environment. See the dedetailed documentation [here](https://docs.python.org/3/library/venv.html)
Depending on your python version, open a terminal window, move to the desired loaction via `cd` and create a new virtual environment.
### 7.1 Creating a virtual environment 
<br><strong>ON MAC</strong></br>
Python < 3:
```zsh
python -m venv name_of_your_virtual_environment
```
Or provide the full path directly:
```zsh
python -m venv /path/to/new/virtual/name_of_your_virtual_environment
```
Python >3:
```zsh
python3 -m venv name_of_your_virtual_environment
```
Or provide the full path directly:
```zsh
python3 -m venv /path/to/new/virtual/name_of_your_virtual_environment
```
### 7.2 Activating a virtual environment
Activate the virtual environment by:
```zsh
source /path/to/new/virtual/name_of_your_virtual_environment/bin/activate
```
or move into the virtual environment directly and execute:
```zsh
source /bin/activate
```
### 7.3 Deactivating a virtual environment
Deactivate the virtual environment from anywhere via:
```zsh
deactivate
```
### 7.4 Downloading dependencies inside the virtual environment
Move to the virtual environment or create a new one, activate it and install the dependencies from the requirements.txt file via:
```zsh
pip install -r requirements.txt
```
or:
```zsh
pip3 install -r requirements.txt
```
Alternatively by providing the full path to the requirements.txt file:
```zsh
pip3 install -r /Users/path/to/project/requirements.txt
```
Make sure the dependencies were correctly loaded:
```zsh
pip list
```
or:
```zsh
pip3 list
```
## Examples
Examples of the produced graphs (as .png and as .pdf):
<br>PNG:
<p align="center">
  <img src="https://raw.githubusercontent.com/RobertHennings/STRAVA_CLIENT/refs/heads/master/strava_client/src/Output/strava-activities-heatmap.png" 
       width="800"/>
</p>

Some further examples on how to run and set up the client in a scripting file can be found
in the `tests` folder in the `local.py` file.
## Author
Robert Hennings, 2025