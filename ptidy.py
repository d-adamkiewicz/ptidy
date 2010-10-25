#!/usr/bin/python
#v.02
#status - alpha
import os, getopt, sys, shutil, yaml
from datetime import datetime

def usage():
	print('usage:'
	,"- first time, you 'store' 'main_dir' in 'meta.yaml' in order to be used every next time"
	,'\tptidy.py -smc:\\scripts\\forweb -pproject1' 
	,'- next time'
	,'\tptidy.py -pproject1'
	,"- or you just want to use another main_dir for the moment"
	,'\tptidy.py -mc:\\scripts\\console -pproject2'
	,sep='\n')


def main():
	store = False
	meta = 'meta.yaml'
	# hardcoded
	proj_file = 'project.yaml'
	main_dir = ''
	proj_dir =''
	fullpath = ''
	try:
		opts, args = getopt.getopt(sys.argv[1:],'m:p:sh',['main_dir=','proj_dir','store','help'])
	except getopt.GetoptError as err:
		print(err)
		usage()
		sys.exit(2)
		
	for o, a in opts:
		if o in ('-h', '--help'):
			usage()
		elif o in ('-s', '--store'):
			store = True
		elif o in ('-m', '--main_dir'):
			if not os.path.isdir(a):
				print('You didn\'t provide valid path in --main_dir parameter')
				sys.exit(2)
			else:
				main_dir = a
		elif o in ('-p', '--proj-dir'): 
			proj_dir = a
	
	# in order to get main_dir parameter
	if main_dir:
		if store:
			out = open(meta, 'w+')
			print(yaml.dump({'main_dir':main_dir}, default_flow_style=False), file=out)
		
	elif os.path.isfile(meta):
		inpt = open(meta, 'r')
		yobj = yaml.load(inpt)
		if not 'main_dir' in yobj:
			print("There is no 'main_dir' parameter in 'meta.yaml'")
			sys.exit(2)
		main_dir = yobj['main_dir']	
		#just in case
		if not os.path.isdir(main_dir):
			print("--main_dir parameter in 'meta.yaml' is not valid path")
			sys.exit(2)		
	else:
		print("You didn't specify --main_dir prameter nor 'meta.yaml' config file exists")
		sys.exit(2)
		
	if not proj_dir:
		print("You must specify --proj_dir parameter ie project folder")
		sys.exit(2)
	
	fullpath = os.path.join(main_dir, proj_dir)
	if not os.path.isdir(fullpath):
		print("Project directory you provided: '" + fullpath + "' doesn't exist")
		sys.exit(2)
	#debug
	print(fullpath)
	
	os.chdir(fullpath)
	paths = os.listdir('./')
	files = []
	for p in paths:
		if os.path.isfile(p):
			files.append(p)

	yfile = open(os.path.join(fullpath, proj_file), 'r')
	yobj = yaml.load(yfile)
	yfiles = [proj_file]
	for o in yobj:
		yfiles[len(yfiles):] += o['files']

	fdiff = []
	fsame = []
	for f in files:
		if not f in yfiles:
			fdiff.append(f)
		else:
			fsame.append(f)
			
	for f in yfiles:
		if not f in fsame:
			print('file ' + f + ' is listed in ' + proj_file + ' but it doesn\'t exist!!!')
			
	dt = datetime.now()
	tmpdir = dt.strftime("%Y%m%d-%H%M%S")
	if not os.path.isdir(tmpdir):
		os.mkdir(tmpdir)
		
	for f in fdiff:
		shutil.move(f, tmpdir + '/' + f) 
			
	print('\n'.join(fdiff))
	print('----\n')
	print('\n'.join(fsame))

if __name__ == '__main__':
	main()