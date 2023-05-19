import shutil
import subprocess
import os


path2class = "C:/jenkins/sikuli/scripts/system_functions.sikuli/system_functions.py"
destnation = "C:/tmp/html/"
destnation_final = "C:/jenkins/sikuli/HOW TO START SCRIPTS/Jeeves menu class documentation.html"
filename = "system_functions.py"
filename_html = "system_functions.html"


shutil.copy(path2class, destnation + filename)

# Get rid of 1st line of file
with open(destnation + filename, 'r') as fin:
    data = fin.read().splitlines(True)
with open(destnation + filename, 'w') as fout:
    fout.writelines(data[1:])

# generate documentation
subprocess.run(["pdoc","--html",filename], cwd=destnation)

# Copy docs to proper folder
shutil.copy("{0}html/{1}".format(destnation, filename_html), destnation_final)

# Delete temp data
shutil.rmtree(destnation + "html")
os.remove(destnation + filename)
