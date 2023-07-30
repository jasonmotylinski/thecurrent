import config
import json
import sqlite3
from file_helpers import load_json_data


con = sqlite3.connect(config.DB)

def insert_artist(artist):
    t = """SELECT artist
            FROM artist
            WHERE artist=?
            LIMIT 1"""
    results=con.execute(t, (artist,)).fetchall()

    if(len(results))==0:
        t="INSERT INTO artist(artist) VALUES(?)"
        con.execute(t, (artist,))
        con.commit()

def insert_genres(artist, genres, source):

    for g in genres:
        t = """SELECT artist, genre, source
            FROM artist_genres
            WHERE artist=?
            AND genre=?
            AND source=?
            LIMIT 1"""
        results=con.execute(t, (artist,g, source)).fetchall()

        if(len(results))==0:
            t="INSERT INTO artist_genres(artist, genre, source) VALUES(?, ?, ?)"
            con.execute(t, (artist,g, source))
            con.commit()

def insert_images(artist, images, source):

    for i in images:
        t = """SELECT artist, height, width, url, source
            FROM artist_images
            WHERE artist=?
            AND height=?
            AND width=?
            AND url=?
            AND source=?
            LIMIT 1"""
        results=con.execute(t, (artist, i['height'], i['width'], i['url'], source)).fetchall()

        if(len(results))==0:
            t="INSERT INTO artist_images(artist, height, width, url, source) VALUES(?, ?, ?, ?, ?)"
            con.execute(t, (artist,i['height'], i['width'], i['url'], source))
            con.commit()

if __name__ == '__main__':
    artists=load_json_data(config.SPOTIFY_ARTISTS_JSON, 'artist')  

    for key in artists.keys():
        artist=key.strip()
        artist_data=json.loads(artists[key])
        insert_artist(artist)
        if 'genres' in  artist_data['data']:
            insert_genres(artist, artist_data['data']['genres'], 'spotify')
        if 'images' in  artist_data['data']:
            insert_images(artist, artist_data['data']['images'], 'spotify')

 