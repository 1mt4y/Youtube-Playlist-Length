import os, isodate
from datetime import timedelta

import googleapiclient.discovery
from flask import Flask, Response, request, render_template

def getTotalDuration(playlistId):
    DEVELOPER_KEY = os.getenv('API_KEY') 

    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = DEVELOPER_KEY)

    pageToken = ""
    totalDuration = timedelta(0)
    while True:
        videosId = ""
        # 1) request video IDs of a playlist
        response_ids = youtube.playlistItems().list(
            part="contentDetails",
            maxResults=50, # maximum is 50
            pageToken=pageToken,
            playlistId=playlistId
        ).execute()
        for video in response_ids ['items']:
            videosId += video['contentDetails']['videoId'] + ','

        # 2) get the duration of each video from step 1 and add it to the totalDuration
        response_duration = youtube.videos().list(
            part="contentDetails",
            maxResults=50,
            id=videosId.strip(','),
        ).execute()
        for video in response_duration['items']:
            totalDuration += isodate.parse_duration(video['contentDetails']['duration'])

        # we can only get results less than 50 videos at a time, if nextPageToken is not in the response then that means we have received all the response, otherwise we change the pageToken the nextPageToken to get the rest of the response
        if 'nextPageToken' not in response_ids: 
            break
        else:
            pageToken = response_ids['nextPageToken']
    return totalDuration

def days_hours_minutes_seconds(td):
    return "{} days, {} hours, {} minutes, {} seconds".format(
        td.days,
        td.seconds//3600,
        (td.seconds//60)%60,
        td.seconds % 60)

def create_app():
    app = Flask(__name__)

    @app.route("/", methods=['GET', 'POST'])
    def home():
        if(request.method == 'GET'):
            return render_template("index.html")
        else:
            playlist_id = request.form.get("playlist_id")
            try:
                data = days_hours_minutes_seconds(getTotalDuration(playlist_id))
                return render_template("index.html", data=data)
            except:
                return render_template("index.html", data="Enter the Playlist ID only")
    return app