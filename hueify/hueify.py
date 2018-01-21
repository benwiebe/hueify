#!/usr/bin/env python

### Imports ###
import colorsys
import json
import phue
import spotipy
import spotipy.util as util
import sys
import time

from PIL import Image
import requests
from io import BytesIO

import numpy as np
import scipy
import scipy.misc
import scipy.cluster

### Constants ###
scope = "user-read-playback-state"
NUM_CLUSTERS = 8
POLL_TIME = 5

### Functions ###

### Begin Main ###
def main():
	# Spotify Configuration
	conf = json.load(open('config.json'))

	username = conf["spotify"]["user"]
	if username == "":
	    print("Bad config.json")
	    sys.exit()

	token = util.prompt_for_user_token(username, scope, client_id=conf["spotify"]["client_id"], client_secret=conf["spotify"]["client_secret"], redirect_uri=conf["spotify"]["redirect_uri"])

	if token:
	    sp = spotipy.Spotify(auth=token)
	else:
	    print("Can't get token for ", username)
	    sys.exit()

	# Philips Hue Configuration
	br = phue.Bridge(ip=conf["hue"]["ip"], username=conf["hue"]["user"],config_file_path="./")
	br.connect()

	if conf["hue"]["target_type"].lower() == "light":
		light_names = br.get_light_objects('name')
		print(light_names)

		if not conf["hue"]["target_name"] in light_names:
			print("Error: Light '" + conf["hue"]["target_name"] + "' not found!")
			sys.exit(1)

	else:
		print("Error: Invalid target type!")
		sys.exit(1)

	# State Variables
	last_track = None

	# Main Loop
	while 1:
		playback = sp.current_playback()
		if playback:
			track = playback["item"]
			if track != None and track != last_track:
				last_track = track
				img_uri = track["album"]["images"][0]["url"]
				print(img_uri)

				# see https://stackoverflow.com/a/23489503/1896516
				response = requests.get(img_uri)
				im = Image.open(BytesIO(response.content))
				print("got image")

				# see https://stackoverflow.com/a/3244061/1896516
				ar = np.asarray(im)
				shape = ar.shape
				ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)

				codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)

				vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
				counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences

				goodColor = False
				color = None
				while not goodColor:
					index_max = scipy.argmax(counts)                    # find most frequent
					peak = codes[index_max]
					
					print(peak)
					peak = [x / 255 for x in peak]
					print(peak)
					color = colorsys.rgb_to_hsv(*peak)
					print(color)
					color = [int(color[0]*65535), int(color[1]*254), int(color[2]*253 + 1)]
					print(color)
					if color[1] >= conf["hueify"]["thresh_sat"] and color[2] >= conf["hueify"]["thresh_bri"]:
						goodColor = True
					else:
						counts[index_max] = -1;
						codes[index_max] = None;

				if conf["hueify"]["force_bright"]:
					color[2] = 254

				cmd = {'on': True, 'hue': color[0], 'sat': color[1], 'bri': color[2]}
				print(cmd)
				br.set_light(conf["hue"]["target_name"], cmd)

				#br.set_light(conf["hue"]["target_name"], 'hue', color[0])
				#br.set_light(conf["hue"]["target_name"], 'sat', color[1])
				#br.set_light(conf["hue"]["target_name"], 'bri', color[2])
			else: #same or no song
				print("No Change in Song")
		else: # if playback
			print("No Song Playing")

		time.sleep(POLL_TIME)

### Handle Script Run Directly ###
if __name__ == "__main__":
	main()