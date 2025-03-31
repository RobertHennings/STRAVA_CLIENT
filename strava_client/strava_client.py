from typing import Dict, List, Callable
import os
import webbrowser
import json
import datetime as dt
import inspect
import requests
import pandas as pd
import gpxpy
import gpxpy.gpx


import config as cfg
# from . import config as cfg
# Set the static global variables
CLIENT_ID = cfg.CLIENT_ID
CLIENT_SECRET = cfg.CLIENT_SECRET
CLIENT_CREDENTIAL_PATH = cfg.CLIENT_CREDENTIAL_PATH
CLIENT_CREDENTIAL_FILE_NAME = cfg.CLIENT_CREDENTIAL_FILE_NAME
BASE_URL = cfg.BASE_URL
OAUTH_URL = cfg.OAUTH_URL
ERROR_CODES_DICT = cfg.ERROR_CODES_DICT
SUCCESS_CODES_DICT = cfg.SUCCESS_CODES_DICT
COLOR_MAP = cfg.COLOR_MAP
SPLIT_COLNAMES_DICT = cfg.SPLIT_COLNAMES_DICT
REQUEST_TIMEOUT = cfg.REQUEST_TIMEOUT

# For type hint checking and overall data type integrity import self written
# checking function
from util.TypeHintCheck import check_data_types, check_data_types_decorator, apply_decorator_to_methods

#@apply_decorator_to_methods(check_data_types_decorator)
class StravaClient():
    """Main pruposes of the Strava Client:
        1) Download activity related files (.gpx and .csv files)
        2) Create the activity heatmap
    """
    def __init__(
            self,
            client_id: int=CLIENT_ID,
            client_secret: str=CLIENT_SECRET,
            error_codes_dict: Dict[int, Dict[str, str]]=ERROR_CODES_DICT,
            success_codes_dict: Dict[int, Dict[str, str]]=SUCCESS_CODES_DICT,
            base_url: str=BASE_URL,
            client_credential_file_name: str=None,
            client_credential_path: str=None,
            proxies: Dict[str, str]=None,
            verify: bool=None
            ):
        """Initialisation of the Strava Client
           Expected:
                    1) a config.py file for the default settings
                    2) a credentials.json file for the client secrets
           An established application with the abive mentioned parameters obtained
           from the official Strava application procedure.

        Args:
            client_id (int): id of the athlete obtained from the API website
            client_secret (str): seceret of the athlete obtained from the API website
            error_codes_dict (Dict[int, Dict[str, str]], optional): Custom Error Message and return types that the user can specify.
                                                                    Defaults to ERROR_CODES_DICT.
            success_codes_dict (Dict[int, Dict[str, str]], optional): Custom Success Message and return types that the user can specify.
                                                                      Defaults to SUCCESS_CODES_DICT.
            base_url (str, optional): The default Strava API base endpoint.
                                      Defaults to BASE_URL.
            client_credential_file_name (str, optional): File name of the credentials. Can be left out with None
                                                         if a first time user has none stored yet.
                                                         Defaults to None.
            client_credential_path (str, optional): Place where the potential credentials file is stored.
                                                    Defaults to None.
        """
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_credential_path = client_credential_path
        self.client_credential_file_name = client_credential_file_name
        self.error_codes_dict = error_codes_dict
        self.success_codes_dict = success_codes_dict
        self.proxies = proxies
        self.verify = verify
        if self.client_credential_path is not None and self.client_credential_file_name is not None:
            self.__check_path_existence(path=client_credential_path)
            # Check if credentils file is existend at provided location
            if self.client_credential_file_name in os.listdir(self.client_credential_path):
                self.credentials = self.load_credentials()
            else:
                raise FileExistsError(f"{self.client_credential_file_name} not existend in location: {self.client_credential_path}")
        else:
            print(self.get_authorization_url())

    def __resilient_request(
            self,
            response: requests.models.Response,
            ):
        """Internal helper method - serves as generous requests
           checker using the custom defined error and sucess code dicts
           for general runtime robustness

        Args:
            response (requests.models.Response): generous API response

        Raises:
            Exception: _description_

        """
        status_code = response.status_code
        response_url = response.url
        status_code_message = [
            dict_.get(status_code).get("message")
            for dict_ in [self.error_codes_dict, self.success_codes_dict]
            if status_code in dict_.keys()]
        # If status code is not present in the defined dicts
        if status_code_message == []:
            print(f"Status code: {status_code} not defined")
        else: # if status code is definded in the dicts
            # get the defined message for the status code
            status_code_message = f"{"".join(status_code_message)} for URL: {response_url}"
            # get the defined return (type) for the status code
            status_code_return = [
                dict_.get(status_code).get("return_")
                for dict_ in [self.error_codes_dict, self.success_codes_dict]
                if status_code in dict_.keys()]

            if status_code_return is not None:
                print(status_code_message)
            else:
                raise Exception("Error")


    def __check_path_existence(
        self,
        path: str
        ):
        """Internal helper method - serves as generous path existence
           checker when saving and reading of an kind of data from files
           suspected at the given location
           
           !!!!If given path does not exist it will be created!!!!

        Args:
            path (str): full path where expected data is saved
        """
        folder_name = path.split("/")[-1]
        path = "/".join(path.split("/")[:-1])
        # FileNotFoundError()
        # os.path.isdir()
        if folder_name not in os.listdir(path):
            print(f"{folder_name} not found in path: {path}")
            folder_path = f"{path}/{folder_name}"
            os.mkdir(folder_path)
            print(f"Folder: {folder_name} created in path: {path}")

    ########### credential and authorization related methods ###########
    def get_authorization_url(
            self,
            redirect_uri: str="http://localhost",
            strava_oauth_url: str=OAUTH_URL,
            open_in_webbrowser: bool=False
            ) -> str:
        """Internal helper method - set up for first time users that
           initially need a valid code for obtaining valid credentials

           !!!!Function only needs to be called once overall to get the
               initial valid code for credentials!!!!

        Args:
            redirect_uri (str, optional): Redirected URL on the local machine.
                                          Defaults to "http://localhost".
            strava_oauth_url (str, optional): OAUTH URL from Strava.
                                              Defaults to OAUTH_URL.
            open_in_webbrowser (bool, optional): Should the URL be directly
                                                 be opened up in a browser tab
                                                 or just displayed.
                                                 Defaults to False.

        Returns:
            str: OAUTH URL
        """
        auth_url = f"{strava_oauth_url}?client_id={self.client_id}&amp;redirect_uri={redirect_uri}&amp;response_type=code&amp;scope=activity:read_all"
        if open_in_webbrowser:
            webbrowser.open(auth_url)
        return auth_url


    def get_code_from_localhost_url(
            self,
            url: str
            ) -> str:
        """helper method - after the once opened up OAUTH URL, after clicking
           authorize, the now displayed URL needs to be put in to obtain valid
           credentials, inlcuding the refresh token with which new credentials
           will be returned and saved.

        Args:
            url (str): Copied URL by the user from the browser tab

        Returns:
            str: Code to obtain valid credentials
        """
        start_sequence = "code="
        end_sequence = "&scope"
        len_start_sequence = len(start_sequence)
        start_sequence_index = url.rfind(start_sequence)
        end_sequence_index = url.rfind(end_sequence)
        code = url[len_start_sequence + start_sequence_index: end_sequence_index]
        print(f"Code: {code}")
        return code


    def get_new_strava_credentials(
            self,
            code: str,
            client_credential_file_name: str,
            url: str='https://www.strava.com/oauth/token',
            save_credentials: bool=False,
            request_timeout: int=REQUEST_TIMEOUT,
            **kwargs
            ) -> Dict[str, str]:
        """helper method - from the obtained one time use code obtain the
           actual valid credentials and save them accordingly.

           Why do we need a **kwargs method argument?
           Use case: If the user provides the specific but completely optional
                     argument: client_credential_path, the credentials are saved
                     at this location, otherwise the credentials are saved in the
                     current working directory.

        Args:
            code (str): Obtained one time use code.
            client_credential_file_name (str): file name of the credentials
                                               inlcuding file format ending.
            url (str, optional): OAUTH URL from Strava. Set with default value in case
                                 it is changed over time.
                                 Defaults to 'https://www.strava.com/oauth/token'.
            save_credentials (bool, optional): Save the credentials.
                                               Defaults to False.
            request_timeout (int, optional): Default timeout parameter for
                                             requests.
                                             Defaults to REQUEST_TIMEOUT.

        Returns:
            Dict[str, str]: JSON structured credentials
        """
        self.client_credential_file_name = client_credential_file_name
        # Make Strava auth API call with your client_code, client_secret and code
        response = requests.post(
                            url = url,
                            data = {
                                    'client_id': self.client_id,
                                    'client_secret': self.client_secret,
                                    'code': code, # from refreshed URL after clicking Authorize
                                    'grant_type': 'authorization_code'
                                    },
                                    timeout=request_timeout,
                            proxies=self.proxies,
                            verify=self.verify
                        )
        self.__resilient_request(response=response)
        strava_tokens = None
        if response.status_code == 200:
            # Save json response as a variable
            strava_tokens = response.json()
            del strava_tokens["athlete"]
            self.credentials = strava_tokens # directly set the credentials to the active instance
            if save_credentials:
                # Save credentials to file
                client_credential_path = ""
                if kwargs:
                    client_credential_path = kwargs.get("client_credential_path")
                    # directly set the given path to the active instance
                    self.client_credential_path = client_credential_path
                    self.__check_path_existence(path=client_credential_path)
                    credentials_full_save_path = rf'{client_credential_path}/{client_credential_file_name}'
                else:
                    credentials_full_save_path = rf'{client_credential_file_name}'
                if strava_tokens is not None:
                    with open(credentials_full_save_path, 'w') as outfile:
                        json.dump(strava_tokens, outfile)
                    print(f"Strava credentials saved at: {credentials_full_save_path}")
        else:
            raise Exception(f"Failed to load new credentials, strava_tokens: {strava_tokens}")
        return strava_tokens


    def refresh_credentials(
                  self,
                  credentials: Dict[str, str],
                  url: str='https://www.strava.com/oauth/token',
                  save_credentials: bool=True,
                  request_timeout: int=REQUEST_TIMEOUT
                  ) -> Dict[str, str]:
        if dt.datetime.now() > dt.datetime.fromtimestamp(credentials["expires_at"]):
            # a new access token must be retrived using the old ones refresh token
            print("Refreshing access token")
            response = requests.post(
                url=url,
                data={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'refresh_token',
                    'refresh_token': credentials['refresh_token']
                },
                timeout=request_timeout,
                proxies=self.proxies,
                verify=self.verify
            )
            self.__resilient_request(response=response)
            strava_tokens = None
            if response.status_code == 200:
                # Save json response as a variable
                strava_tokens = response.json()
            if save_credentials:
                # Save credentials to file
                client_credential_path = ""
                if self.client_credential_path:
                    client_credential_path = self.client_credential_path
                    self.__check_path_existence(path=client_credential_path)
                    credentials_full_save_path = rf'{client_credential_path}/{self.client_credential_file_name}'
                else:
                    credentials_full_save_path = rf'{self.client_credential_file_name}'
                if strava_tokens is not None:
                    with open(credentials_full_save_path, 'w') as outfile:
                        json.dump(strava_tokens, outfile)
                    print(f"Strava credentials saved at: {credentials_full_save_path}")
            return strava_tokens
        else:
            return credentials


    def load_credentials(
              self
              ):
        # First check if a secrets file is already present at the provided path
        if self.client_credential_file_name is not None and self.client_credential_path is not None:
            self.__check_path_existence(path=self.client_credential_path)
            if self.client_credential_file_name in os.listdir(self.client_credential_path):
                file_path_full = f"{self.client_credential_path}/{self.client_credential_file_name}"
                with open(file_path_full) as json_file:
                    strava_tokens = json.load(json_file)
                return strava_tokens
            else:
                raise KeyError(f"{self.client_credential_file_name} not found in path: {self.client_credential_path}")
        else:
            print("No credentials provided, obtain initial credentials via the following URL")
            initial_authorization_url = self.get_authorization_url(open_in_webbrowser=False)
            print(initial_authorization_url)
            return None

    ########### activity and Strava API model related methods ###########
    def get_strava_activities(
            self,
            page:int=1,
            items_per_page: int=200,
            save_activities: bool=False,
            activities_file_name: str=None,
            activities_path: str=None,
            request_timeout: int=REQUEST_TIMEOUT
            ) -> pd.DataFrame:
        # get the access token from the credentials and check if they are still valid
        credentials = self.refresh_credentials(credentials=self.credentials)
        access_token = credentials["access_token"]

        activities_df = pd.DataFrame(
            columns = [
                "id",
                "name",
                "start_date_local",
                "type",
                "distance",
                "moving_time",
                "elapsed_time",
                "total_elevation_gain",
                "end_latlng",
                "external_id"
                ]
                )
        while True:
            # get page of activities from Strava
            print(f"Requesting data from page: {page}")
            params = {
                 "per_page": f"{items_per_page}",
                 "page": f"{page}"
                }
            headers = {"Authorization": f"Bearer {access_token}"}
            url = f"{BASE_URL}activities"
            response = requests.get(
                url=url,
                params=params,
                headers=headers,
                timeout=request_timeout,
                proxies=self.proxies,
                verify=self.verify
                )
            self.__resilient_request(response=response)
            if response.status_code != 200:
                break
            r = response.json()
            # if no results then exit loop
            if not r:
                break

            # otherwise add new data to dataframe
            for x in range(len(r)):
                activities_df.loc[x + (page-1)*items_per_page,'id'] = r[x]['id']
                activities_df.loc[x + (page-1)*items_per_page,'name'] = r[x]['name']
                activities_df.loc[x + (page-1)*items_per_page,'start_date_local'] = r[x]['start_date_local']
                activities_df.loc[x + (page-1)*items_per_page,'type'] = r[x]['type']
                activities_df.loc[x + (page-1)*items_per_page,'distance'] = r[x]['distance']
                activities_df.loc[x + (page-1)*items_per_page,'moving_time'] = r[x]['moving_time']
                activities_df.loc[x + (page-1)*items_per_page,'elapsed_time'] = r[x]['elapsed_time']
                activities_df.loc[x + (page-1)*items_per_page,'total_elevation_gain'] = r[x]['total_elevation_gain']
                activities_df.loc[x + (page-1)*items_per_page,'end_latlng'] = r[x]['end_latlng']
                activities_df.loc[x + (page-1)*items_per_page,'external_id'] = r[x]['external_id']
            # increment page
            page += 1
        if save_activities:
            if (activities_file_name and activities_path) is not None:
                self.__check_path_existence(path=activities_path)
                activities_full_save_path = f"{activities_path}/{activities_file_name}"
                activities_df.to_csv(activities_full_save_path, index=False)
                print(f"Activities successfully saved: {activities_full_save_path}")
        return activities_df


    def get_strava_activity(
            self,
            activity_id: str,
            request_timeout: int=REQUEST_TIMEOUT
            ) -> Dict:
        """Retrieve details for a certain activity id

        Args:
            activity_id (str): ID of the activity
            request_timeout (int, optional): Default timeout parameter for
                                             requests.
                                             Defaults to REQUEST_TIMEOUT.

        Returns:
            Dict: _description_
        """
        # get the access token from the credentials and check if they are still valid
        credentials = self.refresh_credentials(credentials=self.credentials)
        access_token = credentials["access_token"]

        url = f"{self.base_url}activities/{activity_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            url=url,
            headers=headers,
            timeout=request_timeout,
            proxies=self.proxies,
            verify=self.verify            
            )
        self.__resilient_request(response=response)
        return response.json()


    def get_activity_stream(
            self,
            activity_id: str,
            request_timeout: int=REQUEST_TIMEOUT
            ) -> Dict[str, Dict[str, List[List[float]]]]:
        """Retrieve the latitude and longitude data from an activity to be
           used in the activity heatmap.

        Args:
            activity_id (str): ID of the activity
            request_timeout (int, optional): Default timeout parameter for
                                             requests.
                                             Defaults to REQUEST_TIMEOUT.

        Returns:
            Dict[str, Dict[str, List[List[float]]]]: activity stream dict
        """
        # get the access token from the credentials and check if they are still valid
        credentials = self.refresh_credentials(credentials=self.credentials)
        access_token = credentials["access_token"]

        url = f"{self.base_url}activities/{activity_id}/streams"
        params = {
            "keys": "latlng",
            "key_by_type": True
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            url=url,
            params=params,
            headers=headers,
            timeout=request_timeout,
            proxies=self.proxies,
            verify=self.verify
            )
        self.__resilient_request(response=response)
        if response.status_code == 200:
            print(f"Data Request successfull for stream for id: {activity_id}")
        return response.json()


    def unpack_activity_stream(
            self,
            stream_response: Dict[str, Dict[str, List[float]]]
            ) -> Dict[str, List[float]]:
        """Unpack the activity stream dictionary and reduce it down to the keys
           distance and latlng for the geographic coordinates.

        Args:
            stream_response (Dict[str, Dict[str, List[float]]]): activity stream dict

        Returns:
            Dict[str, List[float]]: _description_
        """
        stream_distance_latlon_dict = {key: stream_response.get(key).get("data") for key in stream_response.keys()}
        return stream_distance_latlon_dict

    ########### activity and file saving related methods ###########
    def save_activity_gpx(
            self,
            stream: Dict[str, List[float]],
            activitiy_gpx_file_name: str=None,
            activitiy_gpx_path: str=None,
            location_item_identifier: str="latlng"
            ):
        """Save the activity stream route coordinates as .gpx file
           for later use and plotting in the activity heatmap.

        Args:
            stream (Dict[str, List[float]]): activity stream dict
            activitiy_gpx_file_name (str, optional): File name of the gpx file.
                                                     Expected to be just the activity id
                                                     and the .gpx ending.
                                                     Defaults to None.
            activitiy_gpx_path (str, optional): Place where to save the .gpx files.
                                                Defaults to None.
            location_item_identifier (str, optional): Key of the coordinates
                                                      in the activtity stream dict.
                                                      Defaults to "latlng".
        """
        gpx = gpxpy.gpx.GPX()
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        if location_item_identifier in stream.keys():
            for point in stream.get(location_item_identifier):
                gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(point[0], point[1]))

            if (activitiy_gpx_file_name and activitiy_gpx_path) is not None:
                activity_gpx_full_save_path = f"{activitiy_gpx_path}/{activitiy_gpx_file_name}"
                self.__check_path_existence(path=activitiy_gpx_path)
                with open(activity_gpx_full_save_path, "w") as f:
                    f.write(gpx.to_xml())
                print(f"Activity gpx file saved: {activity_gpx_full_save_path}")


    def save_activity_csv(
            self,
            stream: Dict[str, List[float]],
            activitiy_csv_file_name: str=None,
            activitiy_csv_path: str=None,
            location_item_identifier: str="latlng"
            ):
        """Save the activity stream route coordinates as .csv file
           for later use and plotting in the activity heatmap.

        Args:
            stream (Dict[str, List[float]]): activity stream dict
            activitiy_csv_file_name (str, optional): File name of the csv file.
                                                     Expected to be just the activity id
                                                     and the .csv ending.
                                                     Defaults to None.
            activitiy_csv_path (str, optional): Place where to save the .csv files.
                                                Defaults to None.
            location_item_identifier (str, optional): Key of the coordinates
                                                      in the activtity stream dict.
                                                      Defaults to "latlng".
        """
        stream_data = stream.get(location_item_identifier, [])
        stream_df = pd.DataFrame(
            data=stream_data,
            columns=["lat", "lon"]
        )
        if location_item_identifier in stream.keys():
            if (activitiy_csv_file_name and activitiy_csv_path) is not None:
                activity_csv_full_save_path = f"{activitiy_csv_path}/{activitiy_csv_file_name}"
                self.__check_path_existence(path=activitiy_csv_path)
                stream_df.to_csv(activity_csv_full_save_path, index=False)
                print(f"Activity csv file saved: {activity_csv_full_save_path}")


    def save_not_existing_data(
        self,
        activities_df: pd.DataFrame,
        ids_not_existing: List[int],
        save_gpx_files: bool=True,
        save_csv_files: bool=True,
        activitiy_gpx_path: str=f"{CLIENT_CREDENTIAL_PATH}/activitiy_gpx",
        activitiy_csv_path: str=f"{CLIENT_CREDENTIAL_PATH}/activitiy_csv",
        ):
        """First checking which activity ids are already present as files
           and which are still missing. Then loading and saving the .gpx 
           and/or the .csv files for the coordinates.

        Args:
            activities_df (pd.DataFrame): _description_
            ids_not_existing (List[int]): _description_
            save_gpx_files (bool, optional): _description_. Defaults to True.
            save_csv_files (bool, optional): _description_. Defaults to True.
            activitiy_gpx_path (str, optional): _description_. Defaults to f"{CLIENT_CREDENTIAL_PATH}/activitiy_gpx".
            activitiy_csv_path (str, optional): _description_. Defaults to f"{CLIENT_CREDENTIAL_PATH}/activitiy_csv".
        """
        for path in [activitiy_gpx_path, activitiy_csv_path]:
            self.__check_path_existence(path=path)

        activities_df_to_load = activities_df.query("id.isin(@ids_not_existing)").reset_index(drop=True).copy()
        for activity_id in activities_df_to_load["id"]:
            activity_stream = strava_client.get_activity_stream(
                activity_id=activity_id,
            )
            stream = self.unpack_activity_stream(stream_response=activity_stream)
            # save the latitude and longitude parameters as gpx file
            if save_gpx_files:
                self.save_activity_gpx(
                    stream=stream,
                    activitiy_gpx_file_name=f"{activity_id}.gpx",
                    activitiy_gpx_path=activitiy_gpx_path,
                    )
            if save_csv_files:
                self.save_activity_csv(
                    stream=stream,
                    activitiy_csv_file_name=f"{activity_id}.csv",
                    activitiy_csv_path=activitiy_csv_path
                    )


    def get_long_format_stream_data(
        self,
        activity_id: int,
        activity_type: str,
        stream: Dict[str, List[float]],
        color_map: Dict[str, str]=COLOR_MAP,
        location_item_identifier: str="latlng"
        ) -> pd.DataFrame:
        stream_data = stream.get(location_item_identifier, [])
        stream_df = pd.DataFrame(
            data=stream_data,
            columns=["lat", "lon"]
        )
        stream_df['activity_type'] = activity_type
        stream_df['color'] = stream_df['activity_type'].map(color_map)
        stream_df['activity_id'] = activity_id
        return stream_df


    def get_nonexisting_activity_ids(
            self,
            existing_activity_ids: List[int],
            activitiy_gpx_path: str=f"{CLIENT_CREDENTIAL_PATH}/activitiy_gpx",
            ) -> List[int]:
        self.__check_path_existence(path=activitiy_gpx_path)
        existing_files = os.listdir(activitiy_gpx_path)
        existing_files = [file for file in existing_files if ".gpx" in file]
        existing_ids = [int(file.split(".gpx")[0]) for file in existing_files]
        ids_not_existing = [id for id in existing_activity_ids if id not in existing_ids]
        return ids_not_existing


    def load_data_from_gpx_files(
        self,
        activities_df: pd.DataFrame,
        color_map: Dict[str, str]=COLOR_MAP,
        type_column_name: str="type",
        activitiy_gpx_path: str=f"{CLIENT_CREDENTIAL_PATH}/activitiy_gpx",
        ) -> pd.DataFrame:
        self.__check_path_existence(path=activitiy_gpx_path)
        gpx_files = os.listdir(activitiy_gpx_path)
        gpx_files = [gpx_file for gpx_file in gpx_files if ".gpx" in gpx_file]
        gpx_files_full_path = [f"{activitiy_gpx_path}/{gpx_file}" for gpx_file in gpx_files]
        stream_data_long_format_df_ = pd.DataFrame()

        for gpx_file_path in gpx_files_full_path:
            activity_id = gpx_file_path.split("/")[-1].split(".")[0]
            activity_id = int(activity_id)
            with open(gpx_file_path, 'r', encoding="utf-8") as gpx_file:
                gpx = gpxpy.parse(gpx_file)

            activity_data = [(point.latitude, point.longitude)
                    for track in gpx.tracks
                    for segment in track.segments
                    for point in segment.points]
            activity_df = pd.DataFrame(
                activity_data,
                columns=["lat", "lon"]
                )
            activity_df["activity_id"] = activity_id
            activity_df["activity_type"] = activities_df.query("id == @activity_id")[type_column_name].values[0]
            activity_df['color'] = activity_df['activity_type'].map(color_map)
            stream_data_long_format_df_ = pd.concat([
                stream_data_long_format_df_,
                activity_df
            ])
        return stream_data_long_format_df_


    def get_activity_splits(
            self,
        activity_type: str,
        activities_df: pd.DataFrame,
        base_url: str=BASE_URL,
        split_colnames_dict: Dict[str, List[str]]=SPLIT_COLNAMES_DICT,
        request_timeout: int=REQUEST_TIMEOUT
        ) -> pd.DataFrame:
        # get the access token from the credentials and check if they are still valid
        credentials = self.refresh_credentials(credentials=self.credentials)
        access_token = credentials["access_token"]
        # filter for the activity
        activity_type_df = activities_df[activities_df.type == activity_type]
        col_names = split_colnames_dict.get(activity_type, None)
        if col_names is not None:
            activity_type_splits_df = pd.DataFrame(columns=col_names)
        else:
            raise KeyError(f"No defined split col names in config for activity type: {activity_type}")
        # loop through each activity id and retrieve data
        for activity_type_id in activity_type_df['id']:
            # Load activity data
            url = f"{base_url}activities/{activity_type_id}"
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(
                url=url,
                headers=headers,
                timeout=request_timeout,
                proxies=self.proxies,
                verify=self.verify
                )
            self.__resilient_request(response=response)
            r = response.json()
            # Extract Activity Splits
            activity_splits = pd.DataFrame(r['splits_metric'])
            activity_splits['id'] = activity_type_id
            activity_splits['date'] = r['start_date']

            # Add to total list of splits
            activity_type_splits_df = pd.concat([activity_type_splits_df, activity_splits])
        return activity_type_splits_df


    def activities_filter(
            self,
            activities_df: pd.DataFrame,
            activities_coordinates_df: pd.DataFrame,
            activity_type: List[str]=None,
            activity_year: List[int]=None,
            activity_name: List[str]=None,
            bounding_box: Dict[str, float]=None
            ) -> pd.DataFrame:
        # Check whether the provided DataFrames are empty
        if not activities_df.empty and not activities_coordinates_df.empty:
            expected_columns = [
                'lat', 'lon', 'activity_id', 'activity_type', 'color', 'id', 'name',
                'start_date_local', 'type', 'distance', 'moving_time', 'elapsed_time',
                'total_elevation_gain', 'end_latlng', 'external_id'
            ]

            existing_columns = set(activities_df.columns) | set(activities_coordinates_df.columns)
            all_needed_columns_present = set(expected_columns).issubset(existing_columns)
            if all_needed_columns_present:
                activities_coordinates_df = (
                    activities_coordinates_df
                    # Filter activities coordinates given the filtered activities
                    .query(expr='activity_id.isin(@activities_df["id"])')
                    # Select columns - select all present
                    .filter(items=activities_coordinates_df.columns)
                    # Left join 'activities_df'
                    .merge(
                        right=activities_df.filter(items=activities_df.columns),
                        how='left',
                        left_on=['activity_id'],
                        right_on=["id"],
                        indicator=False)
                        )
                # Filter activities by year(s)
                activities_coordinates_df["start_date_local"] = pd.to_datetime(activities_coordinates_df["start_date_local"])
                if activity_year is not None:
                    activities_coordinates_df = activities_coordinates_df.query(expr='start_date_local.dt.year.isin(@activity_year)')
                # Filter activities by name(s)
                if activity_name is not None:
                    activities_coordinates_df = activities_coordinates_df.query(expr='name.isin(@activity_name)')
                # Filter activities by type(s)
                if activity_type is not None:
                    activities_coordinates_df = activities_coordinates_df.query(expr='type.isin(@activity_type)')

                # Filter activities inside a bounding box
                if all(value is not None for value in bounding_box.values()):
                    activities_coordinates_df = activities_coordinates_df[
                        activities_coordinates_df['lat'].between(
                            min(bounding_box['latitude_bottom_left'], bounding_box['latitude_bottom_right']),
                            max(bounding_box['latitude_top_left'], bounding_box['latitude_top_right']),
                        )
                    ]
                    activities_coordinates_df = activities_coordinates_df[
                        activities_coordinates_df['lon'].between(
                            min(bounding_box['longitude_bottom_left'], bounding_box['longitude_top_left']),
                            max(bounding_box['longitude_bottom_right'], bounding_box['longitude_top_right']),
                        )
                    ]

                # Return objects
                return activities_coordinates_df


# Test the class methods
strava_client = StravaClient(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_credential_file_name=CLIENT_CREDENTIAL_FILE_NAME,
    client_credential_path=CLIENT_CREDENTIAL_PATH
    )
