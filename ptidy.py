#!/usr/bin/python
#v.04
#status - alpha
import os, getopt, sys, shutil, yaml, re
from datetime import datetime

def usage():
	print('usage:'
	,"- first time, you '--store' '--main-dir' in 'meta.yaml' in order to be used every next time"
	,'\tptidy.py -smc:\\scripts\\forweb -pproject1' 
	,'or longopts:' 
	,'\tptidy.py --store --main-dir=c:\\scripts\\forweb --proj-dir=project1'
	,'- next time'
	,'\tptidy.py -pproject1'
	,"- or you just want to use another --main-dir for the moment"
	,'\tptidy.py -mc:\\scripts\\console -pproject2'
	,sep='\n')

def get_fullpath(meta):
	store = False
	main_dir = ''
	proj_dir = ''
	fullpath = ''
	try:
		opts, args = getopt.getopt(sys.argv[1:],'m:p:sh',['main-dir=','proj-dir=','store','help'])
	except getopt.GetoptError as err:
		print(err)
		usage()
		sys.exit(2)
		
	for o, a in opts:
		if o in ('-h', '--help'):
			usage()
			sys.exit(0)
		elif o in ('-s', '--store'):
			store = True
		elif o in ('-m', '--main-dir'):
			if not os.path.isdir(a):
				print('You didn\'t provide valid path in --main-dir parameter')
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
			print("--main-dir parameter in 'meta.yaml' is not valid path")
			sys.exit(2)		
	else:
		print("You didn't specify --main-dir prameter nor 'meta.yaml' config file exists")
		sys.exit(2)
		
	if not proj_dir:
		print("You must specify --proj-dir parameter ie project folder")
		sys.exit(2)
	
	fullpath = os.path.join(main_dir, proj_dir)
	if not os.path.isdir(fullpath):
		print("Project directory you provided: '" + fullpath + "' doesn't exist")
		sys.exit(2)
	
	return fullpath
	
def failsafe_makedirs(dir):
	try: 
		os.makedirs(dir)
	except: 
		return False
	else: 
		return True

def main():
	# hardcoded
	meta = 'meta.yaml'
	proj_file = 'project.yaml'
	
	fullpath = get_fullpath(meta)
	
	os.chdir(fullpath)
	files = []
	p = re.compile('^\.\/')		
	for root, dirs, fns in os.walk('./'):
		for f in fns:
			root = p.sub('', root) 
			if root:
				files.append(root + '/' + f)
			else:
				files.append(f)
	print(files)	

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
		if len(f.split('/'))>1:
			sp = os.path.split(f)[0]
			mkpath = os.path.join(tmpdir, sp)
			if not os.path.isdir(mkpath):
				if not failsafe_makedirs(mkpath):
					print("can't create dir", mkpath)
					sys.exit(2)
		shutil.move(f, os.path.join(tmpdir, f)) 
			
	print('\n'.join(fdiff))
	print('----\n')
	print('\n'.join(fsame))

if __name__ == '__main__':
	main()