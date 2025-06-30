# VLC-Android-RemoteAccess-API
Python code to use the VLC Android Remote Access web server as an API

## Summary
- This is basic and not-full-featured python code for connecting to and using the VLC Android Remote Access web server as a headless API.
- This code should cover basic needs for getting and setting common items.
- API endpoints not included in this code: organizing albums, artists, genres; downloading/uploading media files; accessing artwork. 
- Someone could use this as a starting point to make a more fully featured class or module. But for many needs it should be sufficient. 

## Background
- The VLC Android app's (version 3.6 and later) Remote Access feature gives the VLC APK the ability to run a web server that serves a vue.js front-end that controls the VLC app.
- It is possible to interact with this web server programmatically and "headless", ie as an API, with a couple caveats.

# Notes

Original VLC forum post/question: 
https://forum.videolan.org/viewtopic.php?f=35&t=166709

### Caveat 1:
You may have to allow the VLC Android app the permission to "display over other apps", otherwise VLC must be in the foreground and the device screen must be on. 
"This is due to an Android limitation: an app cannot launch itself (anymore) without being in foreground. It's only true for launching an activity. So you can start an audio playback, but not a video one. [If] your app is running on the same device, you can just launch the app, wait a few seconds and then issue your commands." If you attempt to play a video without these conditions, requests to the VLC web server will error with a 500 status code with a message like "app not in foreground". I tested my code solely on a Kindle Fire 8 (12th gen), so you may get different results on different devices or android OS's. 
I also disabled battery optimizations and allowed the "Display over other apps" permission for Termux, Termux:API, and VLC. Those actions may also may be necessary for a truly "headless" API operation.

### Caveat 2:
This code uses the Termux:API command "termux-notification-list" to automatically grab the one-time-password (OTP, 4 digits) from the android notifications list. This is optional; it's nice to have if you don't want to manually input the OTP code to the script. (It is a bit of a security consideration. Perhaps better to go with a manual input if your device is used for important things.) This specific Termux:API command requires permission to "read notifications" to be enabled. This permission may be hard to find. You may have to run the command in order for the permission to show up in the android settings.

## On Connecting to the server
Upon enabling the web server, an android notification will pop up saying that the web server is running on port "8080" which is for HTTP requests. In actuallity the web server requires you to interact with it via HTTPS on the 8443 port. When interacting with the server via the front-end, the front-end will prompt you to use HTTPS: you manually approve your browser to accept the VLC's self-signed SSL certificate.

In my code, I use the 8443 port for all requests, and I tell the requests library to not verify the SSL certificate when making HTTPS calls. There may (or may not) be a good way to actually verify VLC's certificate within the python code.

In addition to HTTP(S) calls, the web server also has a websocket feature; my code does not use it (directly). Note that the websocket has a different authentication scheme so my code would be insufficient for that. However, all websocket API commands can be interacted with via HTTP(s) calls via the "/playback-event?message=<COMMAND>" endpoint. Where <COMMAND> could be play, pause, next, previous, set-volume, etc. And getting response data can be retrieved via the "/longpolling" endpoint HTTPS call. (See below for the websocket API source code link, which will have all possible commands.)

My python code interacts with the web server from the same device, so it uses the "localhost" url but it can be modified to work from any device connected to your LAN--you'd just need to use your android device's IP address, and you'd have to input the OTP code manually to your remote script (Or, have a local script that gets the OTP automatically and sends it to your remote script. A tad complicated but doable.).

## Authentication notes
When the OTP code is verified with the server, the server sends back a cookie called "user_session" which must be supplied when making requests. The cookie is sent from the server to the client within redirect requests (status codes 302 or 301).

In this code, I use the request module's Session object which automatically takes in redirect responses and stores cookie headers. This is very nice: the cookie updating is handled automatically. If you try to make requests using just a 'request' object, you will be confused because the 200-code response will not contain the cookie; the cookie is contained in the "hidden" 301/302-status redirect responses that must be captured somehow. There are multiple solutions but using a Session object here is the easiest.

The cookie value should have a TTL of 1 year.

## Websocket API notes:
Command/message format example: if you see "SET_PROGRESS" in the VLC source code, the message should be "set-progress". Lowercase and dashes.
There are other parameters that certain websocket commands use:
- id, floatValue, longValue, stringValue. Different commands will require different values.
- E.g., you set the volume with an integer in 'id', but for setting the speed you use a float in 'floatValue'

If you mess up a websocket API command with /playback-event, it will return a 403 Forbidden error, regardless of what the error was.
- E.g., if you do "set_progress" instead of the correct "set-progress", it'll return 403.

If you do "get-volume" on the /playback-event HTTPS call, the volume value will not be in the returned response. You must make a separate call to the "/longpolling" endpoint to retrieve the value. 

## Misc

Optional VLC setting for "headless" operation: For Background/PiP mode: set this to "Play videos in background"

This code was tested on June 2025:
- a Kindle Fire 8 (12th gen) running Fire OS 8.3.3.5
- VLC 3.6.5 (2025-5-11) | Termux version 0.118.3 | Termux:API version 0.52.0

## Relevant Source Code
To see all API endpoints that are possible, you'll have to read the source code in these files:
The main API endpoints:
- [https://code.videolan.org/videolan/vlc- ... type=heads](https://code.videolan.org/videolan/vlc-android/-/blob/master/application/remote-access-server/src/main/java/org/videolan/vlc/remoteaccessserver/RemoteAccessRouting.kt?ref_type=heads)

Another view of the API endpoints from the front-end / client perspective:
- [https://code.videolan.org/videolan/remo ... ins/api.js](https://code.videolan.org/videolan/remoteaccess/-/blob/main/src/plugins/api.js)

Websocket API that can be accessed via HTTPS calls via the "/playback-event?message=<COMMAND>" endpoint:
- [https://code.videolan.org/videolan/vlc- ... Sockets.kt](https://code.videolan.org/videolan/vlc-android/-/blob/master/application/remote-access-server/src/main/java/org/videolan/vlc/remoteaccessserver/websockets/RemoteAccessWebSockets.kt)

Authentication System Description
- https://code.videolan.org/videolan/vlc-android/-/wikis/Remote-access/Security
