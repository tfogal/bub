#!python
import logging as log
import pygtk
pygtk.require('2.0')
import gtk
from PIL import Image, ImageDraw

import findir
from outlier import Outlier
from filter_ui import FilterUI

def lerp(x, x0,x1, y0,y1): return y0 + (x - x0)*(float(y1-y0) / float(x1-x0))

def linearcolor(x, color0,color1, data0,data1):
  '''Generates a color through linear interpolation in a range.
     color0 is the color at data0; color1 is the color at data1.'''
  assert(data0 <= x and x <= data1)
  return (
    int(lerp(x, data0,data1, color0[0],color1[0])),
    int(lerp(x, data0,data1, color0[1],color1[1])),
    int(lerp(x, data0,data1, color0[2],color1[2]))
  )

def create_pil_image(data, dims):
  '''Creates a PIL image from raw, single-component image data.'''
  w,h = (dims[0], dims[1])
  img = Image.new('RGB', dims)
  draw = ImageDraw.Draw(img)
  minmax = (min(data), max(data))

  five_percent = minmax[0] + (minmax[1]-minmax[0]) * 0.05
  twenty_percent = minmax[0] + (minmax[1]-minmax[0]) * 0.2

  for y in (xrange(0, dims[1])):
    for x in (xrange(0, dims[0])):
      v = data[y*dims[0]+x]
      c = None # final color
      if v <= five_percent: c = (0,0,0)
      elif v <= twenty_percent:
        c = linearcolor(v, (0,0,0),(254,254,254), five_percent,twenty_percent)
      else:
        c = linearcolor(v, (128,255,0),(255,0,100), minmax[0],minmax[1])
      draw.point((x,y), fill=c)

  return img

class BUB:
  """Holds the main BUB window.  The basic layout is a 3-element VBox
     (self._mainvbox).  The first elem of that VBox is the menus; last elem is
     the status bar.  All the real 'meat' is in the middle, configured in
     self._create_main."""
  def __init__(self):
    self._findir = None
    self._elements = []
    self._active_field = None
    self._window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self._window.connect("destroy", self.destroy)
    self._mainvbox = gtk.VBox(False, 0)
    self._window.add(self._mainvbox)
    self._swindow = None
    self._img = None
    self._hb_main = None
    self._vb_channels = None
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
    self._elements = self._findir.elements()

    self._create_main()

  def _outlier_finished(self, outf, data=None):
    raw_img = self._findir.element(self._active_field)
    width, height = (self._findir.x(), self._findir.y())
    self._set_image(outf.get_filter().get_output(), (width,height))
    outf.destroy()

  def _outlier_filter(self, something):
    raw_img = self._findir.element(self._active_field)
    width, height = (self._findir.x(), self._findir.y())
    outf = Outlier()
    outf.set_input(raw_img, (width,height))
    outf_ui = FilterUI(outf)
    outf_ui.connect("execution-success", self._outlier_finished)
    outf_ui.create_ui()

  def _create_elements(self):
    if self._vb_channels != None: self._vb_channels.destroy()
    self._vb_channels = gtk.VBox(True, 0)

    elems = ["Raw"]
    self._elements.append("Raw")
    # convert to a set and back -- removes duplicates.
    self._elements = list(set(self._elements))
    self._elements.sort()
    for e in self._elements:
      if e != "Time":
        bt_elem = gtk.Button(e)
        bt_elem.connect_object("clicked", self._element, e)
        self._vb_channels.pack_start(bt_elem, False)
        bt_elem.show()
    self._vb_channels.show()

  def _element(self, element):
    '''Called when a user wants to change which element is active.'''
    log.info("Button press of %s" % element)
    self._active_field = element
    raw_img = self._findir.element(element)
    width, height = (self._findir.x(), self._findir.y())
    self._set_image(raw_img, (width, height))
    self._swindow.set_size_request(width+20, height+20)

  def _set_image(self, img_data, dimensions):
    pil_img = create_pil_image(img_data, dimensions)
    assert(pil_img.size[0] == dimensions[0])
    assert(pil_img.size[1] == dimensions[1])
    is_rgba = (pil_img.mode == 'RGBA')
    pb = gtk.gdk.pixbuf_new_from_data(pil_img.tostring(),
                                      gtk.gdk.COLORSPACE_RGB,
                                      is_rgba, 8, dimensions[0], dimensions[1],
                                      (is_rgba and 4 or 3) * pil_img.size[0])
    self._img = gtk.Image()
    self._img.set_from_pixbuf(pb)
    self._create_main()

  def _create_swindow(self):
    if self._swindow != None: self._swindow.destroy()
    self._swindow = gtk.ScrolledWindow()
    self._swindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self._swindow.set_border_width(10)
    if self._img != None:
      self._swindow.add_with_viewport(self._img)
      self._img.show()
    self._swindow.show()

  def _create_hbox(self):
    if self._hb_main != None: self._hb_main.destroy()
    self._hb_main = gtk.HBox(False, 5)
    self._create_elements()
    self._create_swindow()
    self._hb_main.pack_start(self._vb_channels, False)
    self._hb_main.pack_end(self._swindow)
    self._hb_main.show()

  def _create_menus(self):
    m_bar = gtk.MenuBar()
    self._mainvbox.pack_start(m_bar, False, False, 0)
    m_bar.show()

    m_file = gtk.Menu()
    m_file_open = gtk.MenuItem("Open")
    m_file_quit = gtk.MenuItem("Quit")
    m_file.append(m_file_open)
    m_file.append(m_file_quit)

    m_file_open.connect_object("activate", self._menu_open, "file.open")
    m_file_quit.connect_object("activate", self.destroy, "file.quit")

    m_file_blah = gtk.MenuItem("File")
    m_file_blah.show()
    m_file_blah.set_submenu(m_file)
    m_bar.append(m_file_blah)

    m_filter = gtk.Menu()
    m_filter_outlier = gtk.MenuItem("Outlier")
    m_filter_outlier.connect_object("activate", self._outlier_filter, "outlier")
    m_filter_outlier.show()
    m_filter.append(m_filter_outlier)
    m_filter.show()

    m_filter_blah = gtk.MenuItem("Filter")
    m_filter_blah.show()
    m_filter_blah.set_submenu(m_filter)
    m_bar.append(m_filter_blah)

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
    self._create_hbox()
    self._mainvbox.pack_start(self._hb_main)
    self._mainvbox.show()

if __name__ == "__main__":
  app = BUB()
  gtk.main()
