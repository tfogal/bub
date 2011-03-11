#!python
from __future__ import with_statement
from optparse import OptionParser
import os
import sys

from PIL import Image, ImageDraw

import fin
import findir
import sls

def status(string): print string
def validate(): return os.getenv("BUB_NO_VALIDATE") is None

def validate_spot_size(findir, sls):
  x = sls.stop()[0] - sls.start()[0]
  microns_per_pt = x / findir.scanning_time_per_line()
  spot = sls.spot_size()
  if validate() and microns_per_pt < (spot*2.0):
    raise UserWarning("Every data point in these data represents " +
                      `microns_per_pt` + " microns, yet the data were " +
                      "scanned with a spot size of " + `spot` + ".  " +
                      "This might mean you are using the wrong SLS file.  " +
                      "If you're sure you've paired the correct data files, " +
                      "then these data are probably invalid; you're ablating" +
                      " too much data each scan, invalidating future samples" +
                      ".  You can set the BUB_NO_VALIDATE environment " +
                      "variable to ignore this warning.")

def lerp(x, x0,x1, y0,y1): return y0 + (x - x0)*(float(y1-y0) / float(x1-x0))

def linearcolor(x, color0,color1, data0,data1):
  '''Generates a color through linear interpolation in a range.
     color0 is the color at data0; color1 is the color at data1.'''
  assert(data0 <= x and x <= data1)
  return (
    lerp(x, data0,data1, color0[0],color1[0]),
    lerp(x, data0,data1, color0[1],color1[1]),
    lerp(x, data0,data1, color0[2],color1[2])
  )

def write_nrrd(field, field_data, dims):
  '''Write out a detached nrrd from the given data.  Assumes the data are
     64bit FP values, and 2 dimensional.  Also applies a 2.6 scaling factor in
     X.'''
  # write raw data
  import numpy
  numpy.array(field_data).tofile(field)

  # now write the header.
  with open(field + ".nhdr", "w") as nhdr:
    nhdr.write("NRRD0001\n") # or 1?  5?  no idea.
    nhdr.write("dimension: 2\n")
    nhdr.write("type: double\n")
    nhdr.write("encoding: raw\n")
    nhdr.write("endian: %s\n" % sys.byteorder)
    nhdr.write("content: %s\n" % field)
    nhdr.write("min: %f\n" % min(field_data))
    nhdr.write("max: %f\n" % max(field_data))
    nhdr.write("datafile: %s\n" % field)
    nhdr.write("sizes: %d %d\n" % (dims[0], dims[1]))
    nhdr.write("spacings: 2.6 1.0\n")

def write_image(filename, dimensions, data, color):
  img = None
  if color:
    img = Image.new('RGB', dimensions)
  else:
    img = Image.new('I', dimensions)
  draw = ImageDraw.Draw(img)
  minmax = (min(data), max(data))
  five_percent = minmax[0] + (minmax[1]-minmax[0]) * 0.05
  twenty_percent = minmax[0] + (minmax[1]-minmax[0]) * 0.2

  for y in xrange(0, dimensions[1]):
    for x in xrange(0, dimensions[0]):
      v = data[y*dimensions[0]+x]

      if color:
        c = None
        if v <= five_percent:
          c = (0,0,0)
        elif v <= twenty_percent:
          c = linearcolor(v, (0,0,0),(254,254,254), five_percent,twenty_percent)
        else:
          c = linearcolor(v, (128,255,0),(255,0,100), minmax[0],minmax[1])
        draw.point((x,y), fill=c)
      else:
        # despite being represented internally as 32-bit values, no PIL
        # exporter (that I can find) can actually write out a 32-bit greyscale
        # image.  Thus we move the data range to 16-bit.
        v = ((v - minmax[0]) / (minmax[1]-minmax[0])) * pow(2,16)
        draw.point((x,y), fill=v)

  with open(filename, "w") as png:
    # upsample the data to be a size Noel and Tim seem to like.
    i = img.resize((int(dimensions[0]*2.6), dimensions[1]))
    i.save(png, 'PNG')

def validate_options(options):
  if options.findir is None:
    print >> sys.stderr, "--findir must be supplied."
    sys.exit(1)
  if options.sls is None:
    print >> sys.stderr, "--sls must be supplied."
    sys.exit(1)
  if options.finglob is None:
    print >> sys.stderr, "This should not be possible..."
    sys.exit(1)

if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("-f", "--findir", dest="findir",
                    help="Read FIN files from DIR", metavar="DIR")
  parser.add_option("-s", "--sls", dest="sls",
                    help="Read sizing information from SLS", metavar="SLS")
  parser.add_option("-g", "--glob", dest="finglob", default="*FIN2",
                    help="Filename glob to use for FIN files ('*FIN2').")
  options,args = parser.parse_args()

  validate_options(options)

  status("Reading table of elements...")
  fdir = findir.FINDir(options.findir, options.finglob)
  fields = fdir.elements()

  status("Reading SLS information..")
  s = sls.SLS(options.sls)
  validate_spot_size(fdir, s)

  dimensions = (fdir.x(), fdir.y())

  for field in fields:
    if field != "Time":
      status("Processing field: '%s'..." % field)
      field_data = fdir.element(field)
      use_color = True
      write_image(field + ".png", dimensions, field_data, use_color)
      write_nrrd(field, field_data, dimensions)
