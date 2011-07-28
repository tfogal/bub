#!python
import pygtk
pygtk.require('2.0')
import gtk
import gobject

def event_hs_changed(get, set):
  set.page_size = get.page_size
  

class FilterUI(gobject.GObject):
  __gsignals__ = {
    'execution-success' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
  }
  def __init__(self, in_filter):
    gobject.GObject.__init__(self)
    self._filter = in_filter
    self._window = None

  def create_ui(self, parent=None):
    self._window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self._vbox = gtk.VBox(True, 0)

    params = self._filter.get_all_parameters()
    for k in params.keys():
      param = params[k]
      param_name = k
      param_type = param[1]

      hbox = gtk.HBox(True, 0)
      hbox.set_homogeneous(False)
      if param_type == float:
        lbl_name = gtk.Label(param_name)
        lbl_name.show()
        hbox.pack_start(lbl_name)
        # Create a horizontal scroll bar; a step will be a 100th of the range,
        # and a "page jump" will be a 10th of the range.
        minmax = param[2]
        step_increment = (minmax[1]-minmax[0]) * 0.01
        page_increment = (minmax[1]-minmax[0]) * 0.1
        page_size = minmax[1] # right?
        sbar = gtk.HScale()
        sbar.set_range(minmax[0], minmax[1])
        sbar.set_value(param[0])
        # TODO FIXME: calculate the number of digits required instead of
        # hardcoding it.
        sbar.set_digits(2)
        sbar.set_increments(step_increment, step_increment)
        sbar.set_update_policy(gtk.UPDATE_CONTINUOUS)
        sbar.connect("value-changed", self._update_float, param_name)
        sbar.show()
        hbox.pack_start(sbar)
      if param_type == bool:
        checked = params[k][0]
        cbox = gtk.CheckButton(label=param_name)
        cbox.set_active(checked)
        cbox.connect("toggled", self._update_boolean, param_name)
        cbox.show()
        hbox.pack_start(cbox)
        
      hbox.show()
      self._vbox.pack_start(hbox)

    hb = gtk.HBox(True, 0)
    lbl_nothing = gtk.Label()
    lbl_nothing.show()
    hb.pack_start(lbl_nothing)
    btn_execute = gtk.Button("Execute", stock=gtk.STOCK_EXECUTE)
    btn_execute.set_alignment(1.0, 0.5) # push it to the right
    btn_execute.connect("clicked", self._execute)
    btn_execute.show()
    hb.pack_start(btn_execute, False)
    hb.show()
    self._vbox.pack_start(hb, False, False)

    self._vbox.set_homogeneous(False)
    self._vbox.show()
    self._window.add(self._vbox)
    self._window.show()

  def get_filter(self): return self._filter

  def destroy(self):
    self._window.destroy()
    self._window = None

  def _execute(self, button):
    print "Running filter '%s' with parameters:" % self._filter.name()
    for k in self._filter.get_all_parameters().keys():
      print "\t", k, "->", self._filter.get_parameter(k)
    self._filter.execute()
    self.emit("execution-success")

  def _update_float(self, sbar, parameter_name):
    self._filter.update_value(parameter_name, sbar.get_value())

  def _update_boolean(self, srcobj, parameter_name):
    self._filter.update_value(parameter_name, srcobj.get_active())
