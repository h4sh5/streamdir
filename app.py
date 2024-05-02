#!/usr/bin/env python3

from flask import Flask, request, render_template_string
import sqlite3
import requests
import re
from urllib.parse import unquote

app = Flask(__name__)
db = sqlite3.connect('content.db', check_same_thread=False)

gcur = db.cursor()
gcur.execute("CREATE TABLE IF NOT EXISTS shows(id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, title TEXT)")
gcur.execute("CREATE TABLE IF NOT EXISTS episode(id INTEGER, show_id INTEGER, url TEXT)")
gcur.execute("CREATE TABLE IF NOT EXISTS progress(show_id INT, episode_url TEXT, seen BOOL)")

VID_EXTS = ['mp4', 'mov', 'mpg', 'mpeg', 'm4a', 'avi','wmv', 'avi','mkv','webm','asf','m4v','flv']

'''
a little streaming app for open HTTP dirs
'''

def add_show(link, title, episode_links):
	cur = db.cursor()
	# remove last entry
	cur.execute("DELETE FROM shows WHERE url = ? or title= ?", (link,title))
	cur.execute("INSERT INTO shows (id, url, title) values(NULL, ?,?)" , (link, title))
	db.commit()
	cur1 = db.cursor()
	cur1.execute("SELECT id from shows where url = ?", (link,))
	show_id = cur1.fetchone()[0]

	cur2 = db.cursor()
	ep_id = 1
	for epurl in episode_links:
		cur2.execute("INSERT INTO episode (id, show_id, url) values(?, ?,?)", (ep_id, show_id, epurl))
		ep_id += 1

	db.commit()

def get_shows():
	cur = db.cursor()
	cur.execute("SELECT id, url,title FROM shows")
	rows = cur.fetchall()
	d = []
	for r in rows:
		d.append({'id':r[0],'link':r[1], 'title':r[2]})
	return d

def get_show_episodes(show_id):

	cur = db.cursor()
	cur.execute("SELECT id, url,title FROM shows")
	rows = cur.fetchall()
	return rows

def get_episode_url(show_id, ep_id):
	cur = db.cursor()
	cur.execute("SELECT url FROM episode WHERE show_id = ? AND id = ?",(int(show_id), int(ep_id)))
	return cur.fetchone()[0]


@app.route('/')
def index():
	url = request.args.get('url')

	if url != None:
		r = requests.get(url, allow_redirects=True)
		urls = re.findall(r'href=[\'"]?([^\'" >]+)', r.text)
		print('found urls via regex:',urls)
		video_links = []
		for vidurl in urls:
			# if url not in ['..', '../' ,'.' , './']:
			for ext in VID_EXTS:
				if vidurl.lower().endswith(ext):
					video_links.append(url+ vidurl)
		print('video links:', video_links)
		if len(video_links) > 0:
			title = r.text.split('<title>')[1].split('</title>')[0]
			if title.endswith('/'):
				title = title.split('/')[-2]
			else:
				title = title.split('/')[-1]
			add_show(url, title, video_links)

	d = get_shows()



	return render_template_string('''
		<title>streamdir</title>
		<form action=/ method=GET>url of http index with video files: <input name=url></input><input type=submit></form>

		{% for show in shows %}
		<p><a href="/show?id={{show.id}}">{{show.title}}</a></p>
		{% endfor %}
		''', shows=d)



@app.route('/show')
def display_show():
	show_id = int(request.args.get('id'))
	# show episodes
	cur = db.cursor()
	cur.execute("SELECT id, url FROM episode WHERE show_id = ?", (show_id,))
	rows = cur.fetchall()
	episodes = []
	for r in rows:
		episodes.append({'id':r[0], 'title':unquote(r[1].split('/')[-1])})
	# print('episodes:',episodes)
	return render_template_string('''

		{% for episode in episodes %}
		<p><a href="/play?show_id={{show_id}}&ep_id={{episode.id}}">{{episode.id}}: {{episode.title}}</a></p>
		{% endfor %}
		''', episodes=episodes,show_id=show_id)

@app.route('/play')
def play():

	# TODO auto play next EP (might need some kind of iframe)
	show_id = int(request.args.get('show_id'))
	ep_id = int(request.args.get('ep_id'))
	url = get_episode_url(show_id, ep_id)

	last_ep_id = int(get_show_episodes(show_id)[-1][0])
	next_ep_id = 0
	if ep_id != last_ep_id:
		next_ep_id = ep_id + 1

	vidtype = url.split('.')[-1].lower() # e.g. mp4 

	return render_template_string('''
<title>streamdir</title>
<style>
	video {
		 width:99vw;
		 height: 100vh;
	}
</style>

<video  id="myVideo" controls autoplay>
 <source src="{{vidurl}}" type="video/{{vidtype}}">
  video not supported
</video>

<script type='text/javascript'>
    document.getElementById('myVideo').addEventListener('ended',myHandler,false);
    function myHandler(e) {
        // What you want to do after the event
        window.location = '/play?show_id={{show_id}}&ep_id={{next_ep_id}}';
    }

    function keydownHandler(evt){

    	if (evt.key == 'f'){  // f for fullscreen
		   var elem = document.getElementById("myVideo");
			if (elem.requestFullscreen) {
			  elem.requestFullscreen();
			} else if (elem.mozRequestFullScreen) {
			  elem.mozRequestFullScreen();
			} else if (elem.webkitRequestFullscreen) {
			  elem.webkitRequestFullscreen();
			} else if (elem.msRequestFullscreen) { 
			  elem.msRequestFullscreen();
			}
		}
    	 
    }

    document.addEventListener("keydown", keydownHandler);


</script>

		''', vidurl=url, next_ep_id=next_ep_id, show_id=show_id, vidtype=vidtype)



app.run(port=5005,debug=True)