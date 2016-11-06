#!/usr/bin/python

import sys
import subprocess
from epstrim import *
from epsinterpreter import *
from graph_guess import *

##
# parse command line input
##
try:
  pdfname = sys.argv[1]
except:
  print("Error: expected input file name on command line")
  sys.exit(1)


##
# convert pdf pages to graphs and output in json format
##

def write_json(label,metadata,g,ofile):
  ofile.write("{ \"%s\": {\n" % label)
  ofile.write("  \"vertices\": [%i" % (g.v[0]+1))
  for vert in g.v[1:]:
    ofile.write(",%i" % (vert+1))
  ofile.write("],\n")
  ofile.write("  \"edges\": [[%i,%i]" % (g.e[0][0]+1,g.e[0][1]+1))
  for edge in g.e:
    ofile.write(",[%i,%i]" % (edge[0]+1,edge[1]+1))
  ofile.write("],\n")
  for pair in metadata[:-2]:
    ofile.write("  \"%s\": [\"%s\"],\n" % (pair[0],pair[1]))
  pair = metadata[-1]
  ofile.write("  \"%s\": [\"%s\"]\n" % (pair[0],pair[1]))
  ofile.write("}}\n\n")

# get number of pages for pdf
batcmd="pdfinfo %s | grep -i Pages" % pdfname
result = subprocess.check_output(batcmd, shell=True)
npages = int(str(result).split()[1].replace("\\n'",""))
print("PDF has", npages, "pages")

# for each pdf page, remove text and convert to jpeg
images = []
for ip in range(1,npages+1):
  print("Converting page %i" % ip)
  batcmd1 = "pdftocairo -f %i -l %i -eps %s page.eps" % (ip,ip,pdfname)
  result1 = subprocess.check_output(batcmd1, shell=True)

  ifile = open("page.eps")
  lines = ifile.readlines()
  ifile.close()

  
  lines = remove_text(lines);
  lines = remove_resources(lines);
  lines = remove_page_setup(lines);
  lines = remove_remainder(lines);

  content = ""
  for line in lines:
    content += " " + line

  eps_objects = get_eps_objects(content)

  graph = graph_guess(eps_objects)

  graphs = get_connected_embedded_subgraphs(graph)

  print("Found %i graphs!" % (len(graphs)))

  # generate report page
  for g in graphs:
    g.plot()
  if(len(graphs) > 0):
    plt.savefig("page_%i.png" % ip)
    plt.clf()
    ofile_name = "page_%i.json" % ip
    ofile = open(ofile_name,"w")

    metadata = [["comments", "Graph found on page %i of %s" % (ip, pdfname)],\
                ["references", pdfname]]

    for ig in range(len(graphs)):
      g = graphs[ig]
      label = "page%igraph%i" % (ip,ig)
      write_json(label,metadata,g,ofile)
  
    ofile.close()

