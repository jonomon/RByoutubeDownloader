#! /usr/bin/python2
# python program to listen to a youtube playst

from xml.dom.minidom import parse, parseString
import urllib2
import subprocess
import sys
import os
import itertools

class youtubePlaylistDL:

    def __init__(self):
        return

    def getPlaylistByUsername(self,username):
        print "Getting playlist from " + username
        html_string = 'https://gdata.youtube.com/feeds/api/users/'
        html = self._get_html_feed(html_string+username+'/playlists?v=2')
        playlist_titles = self._parse_gdata_xml_feed(html,'content&&src')
        return playlist_titles

    def getSonglistByPlaylist_Username(self,username,playlist_name):
        print "Getting playlist from " + username
        html_string = 'https://gdata.youtube.com/feeds/api/users/'
        html = self._get_html_feed(html_string+username+'/playlists?v=2')
        playlist_titles = self._parse_gdata_xml_feed(html,'content&&src')
        
        playlist_chosen = filter(lambda x: x[0]== playlist_name , playlist_titles)[0]
        if  len(playlist_chosen)==0:
            print "error has occured, playlist not found "

        html = self._get_html_feed(playlist_chosen[1])
        songs_found = self._parse_gdata_xml_feed(html,'media:player&&url')
        return songs_found
        
    def _get_html_feed (self,url):
        ## This function gets URL feed from google data
        try: 
            response = urllib2.urlopen(url)
        except urllib2.HTTPError:
            print "Unable to connect to the internet"
            return
        html = response.read()
        #check for correct response
        html = parseString(html)
        return html

    def _parse_gdata_xml_feed(self,value,tag_value):
        ##This function parses gdata xml
        ## and returns the turple containing the item title and 
        ## element with  tag_value provided
        ## if the desired tag_value is an attribute of a tag enter
        ## tag_value as "TagName&&attribute_name"
        item_found = value.getElementsByTagName('entry')

        for item in item_found:
            item_titles=item.getElementsByTagName('title')[0].firstChild\
              .nodeValue.encode('utf-8')

            if '&&' in tag_value:     ##Check tag value to look for tags or attributes
                tag_attributes = tag_value.split('&&')
                item_tag =  item.getElementsByTagName(tag_attributes[0])[0]
                item_ID = item_tag.attributes[tag_attributes[1]].value
            else:
                item_ID=  item.getElementsByTagName(tag_value)[0].firstChild\
                  .nodeValue.encode('utf-8')

            yield (item_titles,item_ID)


def main(username, playlist_name,destination_folder):
    youtubePLDL = youtubePlaylistDL()
    songlist = youtubePLDL.getSonglistByPlaylist_Username("fatbackyarddog","chinese")
    itertools.tee(songlist)
    # for song in songs_found:
    #         print 'Downloading', song[0]
    #         subprocess.call(['youtube-dl','-o',destination_folder+ '%(title)s-%(id)s.%(ext)s','-x',song[1]])
     
if __name__ == '__main__':
        #Testing
    username = 'fatbackyarddog'
    playlist_name = 'chinese'
    destination_folder = '/home/jonomon/devel/pyYTlistener/pyYTlistener/data/'
    ## add command line inputs
    
    main(username,playlist_name,destination_folder)
