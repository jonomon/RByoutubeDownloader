from gi.repository import GObject, RB, Peas, Gtk, GConf, Gio

from youtube_downloader_view import youtubeDownloaderView
#location of context plugin is /usr/lib/rhythmbox/context


class youtubeDownloader (GObject.Object, Peas.Activatable):

    __gtype_name__ = 'youtubeDownloadPlugin'
    object = GObject.property(type=GObject.Object)
    
    def __init__(self):
        GObject.Object.__init__ (self)

    def do_activate(self):
        print "Started Youtube Downloader Plugin"
        self.shell = self.object
        self.ytdl_view = youtubeDownloaderView(self.object,self)
        
        
    def do_deactivate(self):
        print "Closed Youtube Downloader Plugin"
        self.ytdl_view.on_deactivate()
        
