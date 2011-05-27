#!python
import pygtk
pygtk.require('2.0')
import gtk
import logging as log

class BUB:
  """Holds the main BUB window.  The basic layout is a 3-element VBox
     (self._mainvbox).  The first elem of that VBox is the menus; last elem is
     the status bar.  All the real 'meat' is in the middle, configured in
     self._create_main."""
  def __init__(self):
    self._window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self._window.connect("destroy", self.destroy)
    self._mainvbox = gtk.VBox(False, 0)
    self._window.add(self._mainvbox)
    self._create_menus()
    self._create_statusbar()
    self._create_main()
    self._mainvbox.show()
    self._window.show()

  def destroy(self, widget, data=None):
    log.info("Shutting down...")
    self._window.hide()
    gtk.main_quit()

  def _menuitem(self, arg):
    print "arg:", arg

  def _create_menus(self):
    m_file = gtk.Menu()
    m_file_open = gtk.MenuItem("Open")
    m_file_quit = gtk.MenuItem("Quit")
    m_file.append(m_file_open)
    m_file.append(m_file_quit)

    m_file_open.connect_object("activate", self._menuitem, "file.open")
    m_file_quit.connect_object("activate", self.destroy, "file.quit")

    m_bar = gtk.MenuBar()
    self._mainvbox.pack_start(m_bar, False, False, 0)
    m_bar.show()

    m_file_blah = gtk.MenuItem("File")
    m_file_blah.show()
    m_file_blah.set_submenu(m_file)
    m_bar.append(m_file_blah)

    m_file_open.show()
    m_file_quit.show()
    m_bar.show()

  def _create_statusbar(self):
    self._status = gtk.Statusbar()
    self._status.show()
    self._mainvbox.pack_end(self._status, False)

  def _create_main(self):
    hb_main = gtk.HBox(False, 5)
    vb_channels = gtk.VBox(True, 0)

    hb_main.pack_start(vb_channels, False)

    lbl_raw = gtk.Label("Raw")
    lbl_zn70 = gtk.Label("Zn70")
    lbl_cu63 = gtk.Label("Cu63")
    vb_channels.pack_start(lbl_raw, False)
    vb_channels.pack_start(lbl_zn70, False)
    vb_channels.pack_start(lbl_cu63, False)

    lbl_raw.show(); lbl_zn70.show(); lbl_cu63.show()
    vb_channels.show()

    lbl_test = gtk.Label("This is where the zoomable/scrollable image will go")
    lbl_test.show()
    hb_main.pack_end(lbl_test, True, True)

    hb_main.show()
    self._mainvbox.pack_start(hb_main)

if __name__ == "__main__":
  app = BUB()
  gtk.main()
