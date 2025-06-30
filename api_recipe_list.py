from vlc_api_class_small import VLCRemoteAccessAPI
import json

vlc_api = VLCRemoteAccessAPI()
vlc_api.authenticate()

#get list of all audio tracks (won't include video files)
response = vlc_api.api_call("get","/track-list")
tracks = json.loads(response.text)  # list of dicts
song1_id = tracks[0]['id']

#get list of all video files (won't include audio files like mp3s, etc.)
response = vlc_api.api_call("get","/video-list")
vids = json.loads(response.text)  # list of dicts
vids = vids['content']
vid1_id = vids[0]['id']

#play a media file by it's id
vlc_api.api_call("get", "/play", id=song1_id)
#play a video, or play it as audio. 
vlc_api.api_call("get", "/play", id=vid1_id)
vlc_api.api_call("get", "/play", id=vid1_id, audio="true")
#play a media file but append it to a queue, don't play it immediately  
vlc_api.api_call("get", "/play", id=vid1_id, append="true")

#play whatever is currently queued.
vlc_api.api_call("get", "/playback-event", message="play")

#Goto the beginning of the media file (that's currently playing. Playback wont be interrupted.)
#the following 2 lines do the same thing. Just different formats.
vlc_api.api_call("get", "/playback-event?message=set-progress&id=0")
vlc_api.api_call("get", "/playback-event", message="set-progress", id=0)

#=========================================================================
vlc_api.api_call("get", "/playback-event", message="pause")
#goto previous item
vlc_api.api_call("get", "/playback-event", message="previous")
#goto next item
vlc_api.api_call("get", "/playback-event", message="next")
#go backward 10 seconds
vlc_api.api_call("get", "/playback-event", message="previous10")
#go forward 10 seconds
vlc_api.api_call("get", "/playback-event", message="next10")
#shuffle the current playlist (or group or queue?)
vlc_api.api_call("get", "/playback-event", message="shuffle")
#cycle through the repeat modes. 
vlc_api.api_call("get", "/playback-event", message="repeat")
#set volume. Here, we set it to 40%.
vlc_api.api_call("get", "/playback-event", message="set-volume", id=40)
#set the progress/cursor of the playback in milliseconds. Here, we goto the 5 seconds timestamp.
vlc_api.api_call("get", "/playback-event", message="set-progress", id=5000)
#play a chapter by number
vlc_api.api_call("get", "/playback-event", message="play-chapter", id=1)
#set the speed of playback
vlc_api.api_call("get", "/playback-event", message="speed", floatValue=1.2)
#set sleep timer duration from now in milliseconds. Here, we set to sleep 10 mins from now. 
vlc_api.api_call("get", "/playback-event", message="sleep-timer", longValue=1000*60*10)

#set mode: whether to wait for the currently playing media to end before enacting the sleep timer.
#stringValue should be a string "true" or "false", exactly. 
vlc_api.api_call("get", "/playback-event", message="sleep-timer-wait", stringValue="true")
#set mode: whether to reset the sleep timer after every interaction
vlc_api.api_call("get", "/playback-event", message="sleep-timer-reset", stringValue="true")

#=====================
#Other API calls that aren't covered in this file: 
#Other playback-event API calls: bookmark, play-media, delete-media, move-media-bottom, move-media-top, remote???

#Other non-playback-event API calls: 
#getting lists of albums, genres, artists, playlists. Creating playlists. Adding files to a playlist. 