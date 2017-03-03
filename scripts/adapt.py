import argparse

parser = argparse.ArgumentParser(description='Run the data processing tool without GUI.')
parser.add_argument('configfile', metavar='file', help='the name of the configfile')

args = parser.parse_args()
print(args)


from core import configParserFileAccess
from core import processListBuilder
from core import serialExecutor


#~ configfilename = ""
#~ 
#~ runconfig = configParserFileAccess.ConfigParserFileAccess().read(configfilename)
#~ processes = processListBuilder.ProcessListBuilder().createProcessList(runconfig)
#~ 
#~ serialExecutor.SerialExecutor().run(processes)
