#!python
import pygtk
pygtk.require('2.0')
import gtk
import logging as log
import findir

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

  def _menu_open(self, arg):
    print "arg:", arg
    fsel = gtk.FileChooserDialog(title="FIN Directory", parent=self._window,
                                 action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                 buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
                                          gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    response = fsel.run()
    directory = None
    if response == gtk.RESPONSE_OK:
      directory = fsel.get_filename()
      print "selected:", directory
    elif response == gtk.RESPONSE_CANCEL:
      print "no file selected."
    else:
      print "inconceivable!"
    fsel.destroy()
    if directory is None: return

    self._findir = findir.FINDir(directory, "*FIN2")
    print "Loaded FINDir with date", self._findir.date()
    print "Elements:", self._findir.elements()

    print "okay"
    self.set_elements(self._findir.elements())

  def set_elements(self, elems):
    self._vb_channels.destroy()
    self._vb_chnnels = gtk.VBox(True, 0)

    lbl_raw = gtk.Label("Raw")
    self._vb_channels.pack_start(lbl_raw, False)
    for e in elems:
      if e != "Time":
        lbl_elem = gtk.Label(e)
        self._vb_channels.pack_start(lbl_elem, False)
        lbl_elem.show()
    self._vb_channels.show()

    self._hb_main.pack_start(self._vb_channels, False)

  def _create_menus(self):
    m_file = gtk.Menu()
    m_file_open = gtk.MenuItem("Open")
    m_file_quit = gtk.MenuItem("Quit")
    m_file.append(m_file_open)
    m_file.append(m_file_quit)

    m_file_open.connect_object("activate", self._menu_open, "file.open")
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
    """The central part of the window.  On the left, we have a vbox, with each
       entry being a channel in the data.  On the right we have a scrollable
       image that details the currently selected channel."""
    self._hb_main = gtk.HBox(False, 5)
    self._vb_channels = gtk.VBox(True, 0)

    self._hb_main.pack_start(self._vb_channels, False)

    # LHS: channels
    lbl_raw = gtk.Label("Raw")
    lbl_zn70 = gtk.Label("Zn70")
    lbl_cu63 = gtk.Label("Cu63")
    self._vb_channels.pack_start(lbl_raw, False)
    self._vb_channels.pack_start(lbl_zn70, False)
    self._vb_channels.pack_start(lbl_cu63, False)

    lbl_raw.show(); lbl_zn70.show(); lbl_cu63.show()
    self._vb_channels.show()

    # RHS: scrollable image viewer
    swindow = gtk.ScrolledWindow()
    swindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    swindow.set_border_width(10)
    lbl_test = gtk.Label("This is where the zoomable/scrollable image will go")
    lbl_test.show()
    self._hb_main.pack_end(lbl_test, True, True)

    self._hb_main.show()
    self._mainvbox.pack_start(self._hb_main)

if __name__ == "__main__":
  app = BUB()
  gtk.main()
