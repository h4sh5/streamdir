## features

- super simple and hackable

- no stupid JS frameworks

- auto plays next episode

- remembers watched episodes using browsing history default link highlighting

- parses open HTTP indexes (`Index of ..` pages) for episodes

- press 'f' for fullscreen


## usage

### Docker

You can run this with docker

`docker run -it -p 80:5000 h4sh5/streamdir`

or use the docker-compose file in this repo:

`docker-compose up -d`

Then visit http://localhost

### Run directly

`pip3 install -r requirements.txt` 

`./app.py`

For the URL of http index with videos, put in the link to the folder with videos inside, for example:

http://192.168.1.1/tv-show/season1/
