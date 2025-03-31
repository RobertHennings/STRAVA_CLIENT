from typing import List, Dict
import os
import webbrowser
from datetime import timedelta
import io
import pandas as pd
import folium
from PIL import Image, ImageDraw, ImageFont

class StravaActivitiesHeatmap(object):
    def __init__(
        self,
        activities_df: pd.DataFrame,
        activities_coordinates_df: pd.DataFrame,
        heatmap_filename: str,
        activity_colors: Dict[str, str]=None
        ):
        self.activity_colors = activity_colors
        self.heatmap_filename = heatmap_filename
        self.activities_folium_map_object = None
        # Check if the daraframes are not empty
        if not activities_df.empty and not activities_coordinates_df.empty:
            self.activities_df = activities_df
            self.activities_coordinates_df = activities_coordinates_df
        else:
            raise Exception(f"activity_colors and or activities_coordinates_df is empty: activity_colors.empty: {activity_colors.empty}\
                              activities_coordinates_df.empty: {activities_coordinates_df.empty}")

    def create_html(
        self,
        heatmap_html_file_path: str,
        heatmap_center: List[float],
        open_in_webbrowser: bool=False,
        save_html: bool=True,
        map_tile: str='dark_all',
        map_zoom_start: float=13,
        line_weight: float=1.0,
        line_opacity: float=0.6,
        line_smooth_factor: float=1.0,
        return_map_data: bool=False,
        **kwargs
        ) -> folium.Map:
        """Create Heatmap based on inputted activities DataFrame."""
        # Remove all activities from the overview that dont hold values for the parameter
        # end_latlng since they dont have any relevant coordinates
        activities_df = self.activities_df.query(expr='end_latlng != "[]"').reset_index(drop=True)

        if 'distance' not in activities_df.columns:
            activities_df = activities_df.assign(distance=0)
        # Transform the starting date and time
        activities_df["start_date_local"] = pd.to_datetime(activities_df["start_date_local"])
        if "start_date_local" not in activities_df.columns:
            activities_df = activities_df.assign(start_date_local=pd.Timestamp.now(tz='UTC').replace(tzinfo=None))

        activities_coordinates_df = (
            self.activities_coordinates_df
            # Filter activities coordinates given the filtered activities
            .query(expr='activity_id.isin(@activities_df["id"])')
            # Select columns - select all present
            .filter(items=self.activities_coordinates_df.columns)
            # Left join 'activities_df'
            .merge(
                right=activities_df.filter(items=activities_df.columns),
                how='left',
                left_on=['activity_id'],
                right_on=["id"],
                indicator=False)
        )

        # Transform columns
        activities_coordinates_df['coordinates'] = list(zip(activities_coordinates_df['lat'], activities_coordinates_df['lon']))

        # Define map tile
        if map_tile in ['dark_all', 'dark_nolabels', 'light_all', 'light_nolabels']:
            map_tile = 'https://a.basemaps.cartocdn.com/' + map_tile + '/{z}/{x}/{y}@2x.png'

        if map_tile == 'terrain_background':
            map_tile = 'http://tile.stamen.com/terrain-background/{z}/{x}/{y}.png'

        if map_tile == 'toner_lite':
            map_tile = 'http://tile.stamen.com/toner-lite/{z}/{x}/{y}.png'

        if map_tile == 'ocean_basemap':
            map_tile = 'https://server.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}'

        # Create Folium map
        activities_folium_map_object = folium.Map(
            tiles=map_tile,
            attr='tile',
            location=heatmap_center,
            zoom_start=map_zoom_start,
        )
        folium.LayerControl().add_to(activities_folium_map_object)

        # Plot activities into Folium map (adapted from: https://github.com/andyakrn/activities_heatmap)
        for activity_type in activities_coordinates_df['activity_type'].unique():
            df_activity_type = activities_coordinates_df[activities_coordinates_df['activity_type'] == activity_type]

            for activity in df_activity_type['activity_id'].unique():
                date = df_activity_type[df_activity_type['activity_id'] == activity]['start_date_local'].dt.date.iloc[0]
                distance = round(df_activity_type[df_activity_type['activity_id'] == activity]['distance'].iloc[0] / 1000, 1)

                coordinates = tuple(df_activity_type[df_activity_type['activity_id'] == activity]['coordinates'])
                folium.PolyLine(
                    locations=coordinates,
                    color=self.activity_colors[activity_type],
                    weight=line_weight,
                    opacity=line_opacity,
                    control=True,
                    name=activity_type,
                    popup=folium.Popup(
                        html=(
                            'Activity type: '
                            + activity_type
                            + '<br>'
                            + 'Date: '
                            + str(date)
                            + '<br>'
                            + 'Distance: '
                            + str(distance)
                            + ' km'
                            + '<br>'
                            + '<br>'
                            + '<a href=https://www.strava.com/activities/'
                            + str(activity)
                            + '>'
                            + 'Open in Strava'
                            + '</a>'
                        ),
                        min_width=100,
                        max_width=100,
                    ),
                    tooltip=activity_type,
                    smooth_factor=line_smooth_factor,
                    overlay=True,
                ).add_to(activities_folium_map_object)

        self.activities_folium_map_object = activities_folium_map_object
        # Save to .html file
        if save_html:
            # check if there was provided a different file name in the **kwargs
            heatmap_html_filename = rf"{self.heatmap_filename}.html"
            if kwargs:
                heatmap_html_filename = kwargs.get("heatmap_html_filename") # expected with .html ending
                if not ".html" in heatmap_html_filename:
                    raise AttributeError("heatmap_html_filename is expected to include file ending: .html")
                else:
                    heatmap_html_full_save_path = rf"{heatmap_html_file_path}/{heatmap_html_filename}"
                    activities_folium_map_object.save(outfile=heatmap_html_full_save_path)
                    print(f"{heatmap_html_filename} succesfully saved at: {heatmap_html_full_save_path}")
        if open_in_webbrowser:
            activities_folium_map_object.show_in_browser()
            # heatmap_html_file_url = f"file://{strava_activities_heatmap_output_path}"
            # webbrowser.open(url=heatmap_html_file_url)
        if return_map_data:
            return activities_folium_map_object


    def __create_activities_statistics(
        self
        ) -> str:
        # Summary statistics
        activities_df = self.activities_df

        total_activities = activities_df['id'].nunique()
        total_distance = round(activities_df['distance'].sum() / 1000, 1)
        total_moving_time = timedelta(seconds=int((activities_df.assign(moving_time=activities_df['moving_time'] * 60)['moving_time']).sum()))
        total_elevation_gain = round(activities_df['total_elevation_gain'].sum() / 1000, 1)
        longest_activity = round(activities_df[activities_df['distance'] == activities_df['distance'].max()].filter(items=['distance']) / 1000, 1).to_string(index=False, header=False)
        longest_activity_date = activities_df[activities_df['distance'] == activities_df['distance'].max()] \
            .filter(items=['start_date_local']) \
            .assign(activity_date=lambda row: row['start_date_local'].dt.strftime(date_format='%b %Y')) \
            .to_string(index=False, header=False)
        # max_speed = round(activities_df['max_speed'].max(), 1)
        # avg_speed = round(activities_df['average_speed'].mean(), 1)

        # Add the summary statistics to the saved activities_map.png file
        full_text_str = f"\n\
        Total activities: {total_activities}\n\
        Total distance (in km): {total_distance}\n\
        Total moving time (in days, hours, minutes, seconds): {total_moving_time}\n\
        Total elevation gain (in km): {total_elevation_gain}\n\
        Longest activity (in km): {longest_activity} ({longest_activity_date})\n\
        "
        return full_text_str


    def create_png(
        self,
        heatmap_png_file_path: str,
        png_size: tuple,
        png_dpi: tuple,
        font_path_statistics: os.path,
        font_size_statistics: int,
        text_color_statistics: tuple,
        display_statistics: bool=True,
        **kwargs
        ):
        if self.activities_folium_map_object is not None:
            activities_map = self.activities_folium_map_object
            # Transfer to png file format
            activities_map_data = activities_map._to_png(5)
            activities_map_img = Image.open(io.BytesIO(activities_map_data))
            # resize the given data to the set size
            activities_map_img_resized = activities_map_img.resize(png_size, Image.LANCZOS)
            # Create a drawing object
            activities_map_draw_object = ImageDraw.Draw(activities_map_img_resized)
            # Load a font (you may need to specify the path to a .ttf font file)
            text_font = ImageFont.truetype(font_path_statistics, font_size_statistics)
            # Calculate text size
            if display_statistics:
                full_text_str = self.__create_activities_statistics()
                text_bbox = activities_map_draw_object.textbbox((0, 0), full_text_str, font=text_font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                # Calculate position for lower right corner
                margin = 50  # Adjust this value to change the distance from the edges
                text_position = (png_size[0] - text_width - margin, png_size[1] - text_height - margin)
                # Draw text with a simple background for better readability
                text_bbox = activities_map_draw_object.textbbox(text_position, full_text_str, font=text_font)
                # draw.rectangle([text_bbox[0]-5, text_bbox[1]-5, text_bbox[2]+5, text_bbox[3]+5], fill=(0, 0, 0, 128))
                activities_map_draw_object.text(text_position, full_text_str, font=text_font, fill=text_color_statistics)
            # Save the image with higher quality
            # check if there was provided a different file name in the **kwargs
            heatmap_png_filename = rf"{self.heatmap_filename}.png"
            if kwargs:
                heatmap_png_filename = kwargs.get("heatmap_png_filename") # expected with .png ending
                if not ".png" in heatmap_png_filename:
                    raise AttributeError("heatmap_png_filename is expected to include file ending: .png")
                else:
                    heatmap_png_full_save_path = rf"{heatmap_png_file_path}/{heatmap_png_filename}"
                    activities_map_img_resized.save(
                        heatmap_png_full_save_path,
                        format='PNG',
                        optimize=True,
                        quality=95,
                        dpi=png_dpi
                            )
                    print(f"{heatmap_png_filename} succesfully saved at: {heatmap_png_full_save_path}")
        else:
            print("Create the .html heatmap first")


    def create_pdf(
            self,
            heatmap_png_file_path: str,
            heatmap_png_filename: str,
            heatmap_pdf_file_path: str,
            resolution: float=900.0,
            **kwargs
            ):
        heatmap_png_full_save_path = rf"{heatmap_png_file_path}/{heatmap_png_filename}"
        img = Image.open(heatmap_png_full_save_path)
        img_converted = img.convert('RGB')

        heatmap_pdf_filename = rf"{self.heatmap_filename}.pdf"
        if kwargs:
            heatmap_pdf_filename = kwargs.get("heatmap_pdf_filename") # expected with .png ending
            if not ".pdf" in heatmap_pdf_filename:
                raise AttributeError("heatmap_pdf_filename is expected to include file ending: .pdf")
            else:
                heatmap_pdf_full_save_path = rf"{heatmap_pdf_file_path}/{heatmap_pdf_filename}"
                img_converted.save(heatmap_pdf_full_save_path,
                           'PDF',
                           resolution=resolution)
                print(f"{heatmap_pdf_filename} succesfully saved at: {heatmap_pdf_full_save_path}")
