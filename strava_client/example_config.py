CLIENT_ID = 123456 # personal client id - stays constant
CLIENT_SECRET = "bbudo82z92phdpd8E28014714" # personal client secret - stays constant
PROJECT_PATH = r"path/to/StravaProject"
CLIENT_CREDENTIAL_PATH = PROJECT_PATH
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
    "Walk": [],
    "Ride": [],
    "Rowing": [],
    "Swim": [],
    "Workout": [],
    "Elliptical": []

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