from gi.repository import GObject, RB, Peas, Gtk, GConf, Gio, Gdk, GLib

from itertools import tee
import subprocess
from pyYTlistener import youtubePlaylistDL
import glob
from urllib2 import URLError

class youtubeDownloaderView (GObject.Object):

    def __init__(self,shell,plugin):
        GObject.GObject.__init__ (self)
        self.shell = shell
        self.plugin = plugin
        
        self.vbox = Gtk.VBox()

        self.username_entry = Gtk.Entry()
        self.username_label = Gtk.Label("Username")
        self.username_button = Gtk.Button("Search")
        self.username_button.connect("clicked", self.on_username_search)
        
        self.playlist_combo_box = Gtk.ComboBoxText()
        self.playlist_combo_box.connect("changed", self.on_playlist_combo_changed)
        self.playlist_label = Gtk.Label("Playlist")

        self.dir_entry = Gtk.Entry()
        self.dir_label = Gtk.Label("Directory")
        
        self.scrolled_window = Gtk.ScrolledWindow()
        self.song_list = Gtk.ListStore(str,int)
        
        self.song_list_treeView = Gtk.TreeView(self.song_list)
        self.song_list_treeView.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        song_list_TextRenderer = Gtk.CellRendererText()
        song_list_treeViewColumn = Gtk.TreeViewColumn("Songs",song_list_TextRenderer,text=0)
        song_list_progressRenderer = Gtk.CellRendererProgress()
        song_list_progressColumn =  Gtk.TreeViewColumn("Progress", song_list_progressRenderer,value=1) 

        self.song_list_treeView.append_column(song_list_treeViewColumn)
        self.song_list_treeView.append_column(song_list_progressColumn)
        
        self.scrolled_window.add(self.song_list_treeView)

        self.download_selected_button = Gtk.Button("Download Selected")
        self.download_selected_button.connect("clicked",self.on_download_selected_button)
        self.save_to_lib_button = Gtk.Button("Save to Lib")
        self.save_to_lib_button.connect("clicked",self.on_save_to_lib_but)
        self.rmv_song_button = Gtk.Button("Remove sel. Song")
        self.rmv_song_button.connect("clicked",self.on_rmv_song_but)

        self.message_list = Gtk.ListStore(str)
        self.message_list_treeView = Gtk.TreeView(self.message_list)
        message_list_TextRenderer = Gtk.CellRendererText()
        message_list_treeViewColumn = Gtk.TreeViewColumn("Messages",message_list_TextRenderer,text=0)
        self.message_list_treeView.append_column(message_list_treeViewColumn)
        self.message_scrolled_window = Gtk.ScrolledWindow()
        self.message_scrolled_window.add(self.message_list_treeView)

        #organise elements into a table
        table = Gtk.Table(15,4,True)
        table.attach(self.username_label,0,1,0,1)
        table.attach(self.username_entry,1,3,0,1)
        table.attach(self.username_button,3,4,0,1)
        table.attach(self.playlist_label,0,1,1,2)
        table.attach(self.playlist_combo_box,  1,4,1,2)
        table.attach(self.dir_label,0,1,2,3)
        table.attach(self.dir_entry,1,4,2,3)
        table.attach(self.scrolled_window,0,4,3,13)
        table.attach(self.download_selected_button,0,1,14,15)
        table.attach(self.save_to_lib_button,1,2,14,15)
        table.attach(self.rmv_song_button,2,3,14,15)
        table.attach(self.message_scrolled_window,0,4,15,19)
        
        self.vbox.pack_start(table,False,True,0)
        self.vbox.show_all()
        self.shell.add_widget (self.vbox,RB.ShellUILocation.RIGHT_SIDEBAR,True,True)
        self.youtubePLDL = youtubePlaylistDL()
        
    def on_deactivate(self):
        self.shell.remove_widget(self.vbox,RB.ShellUILocation.RIGHT_SIDEBAR)

    def on_username_search(self,button):
        self.message_list.append(["Searching for playlists..."])
        self.username = self.username_entry.get_text()
        if not self.username:
            self.message_list.append(["Error: Please enter username"])
            return
        try:
            playlists = self.youtubePLDL.getPlaylistByUsername(self.username)
        except URLError:
            self.message_list.append(["No internet connection!"])
            return
        if len(playlists)==0:
            self.message_list.append(["No playlists found"])
            return
        map( lambda x: self.playlist_combo_box.append_text(x[0]),  playlists)
        self.playlist_combo_box.set_active(0)
        
    def on_playlist_combo_changed(self,combo):
        self.destination_folder = self.dir_entry.get_text()
        if not self.destination_folder:
            self.message_list.append(["Please enter directory"])
            return
        self.song_list.clear()
        if not self.username:
            self.message_list.append(["Username not found"])
            return
        model = combo.get_model()
        playlist_selected = model [combo.get_active_iter()][:2][0]
        songs_found =self.youtubePLDL.getSonglistByPlaylist_Username(self.username,playlist_selected)
        songs_found1, songs_found2 = tee(songs_found)
        self.song_IDs = map(lambda  x: x[1], songs_found1)
        map(lambda x: self.song_list.append([x[0],
            self.search_destination_folder(x[0])]),\
            songs_found2)
        
    def download_song(self,song_ID):
        self.proc = subprocess.Popen(['youtube-dl','-o',self.destination_folder+
        '%(title)s.%(ext)s','-x',song_ID])

    def on_download_selected_button(self,button):
        model, treePath = self.song_list_treeView.get_selection().get_selected_rows()
        if len(treePath) == 0:
            self.message_list.append(["No songs selected"])
            return
        if treePath != None:
            for path in treePath:
                Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.download_song,self.song_IDs[path[0]])
        
    def on_rmv_song_but(self,button):
        model, treePath = self.song_list_treeView.get_selection().get_selected_rows()
        if len(treePath) == 0:
            self.message_list.append(["No songs selected"])
            return
        selectedIter = self.song_list.get_iter(treePath)
        self.song_list.remove(selectedIter)

    def search_destination_folder(self,filename_string):
        paths = glob.iglob(self.destination_folder+"*.m4a")
        for path in paths:
            if filename_string in path:
                return 100
        return 0

    def on_save_to_lib_but(self,button):
        model, treePath = self.song_list_treeView.get_selection().get_selected_rows()
        if len(treePath) == 0:
            self.message_list.append(["No songs selected"])
            return
        if treePath != None:
            for path in treePath:
                if self.search_destination_folder(self.song_list[path[0]][0]) is 100:
                    self.shell.load_uri("file://"+self.destination_folder+self.song_list[path[0]][0]+".m4a",True)
                            







