#!/usr/bin/python
#v.06
#status - alpha
import os, getopt, sys, shutil, yaml, re
from datetime import datetime

def usage():
	print('usage:'
	,"- first time, you '--store' '--main-dir' in 'meta.yaml' in order to be used every next time:"
	,'\tptidy.py -smc:\\scripts\\forweb -pproject1' 
	,'or longopts:' 
	,'\tptidy.py --store --main-dir=c:\\scripts\\forweb --proj-dir=project1'
	,'- next time'
	,'\tptidy.py -pproject1'
	,"- or you just want to use another --main-dir for the moment:"
	,'\tptidy.py -mc:\\scripts\\console -pproject2'
	,"- or in order to display '--main-dir' parameter stored in 'meta.yaml':"
	,'\tpidy.py -v'
	,sep='\n')

def get_fullpath(meta):
	store = False
	main_dir = ''
	proj_dir = ''
	fullpath = ''
	try:
		opts, args = getopt.getopt(sys.argv[1:],'m:p:shv',['main-dir=','proj-dir=','store','help','view'])
	except getopt.GetoptError as err:
		print(err)
		usage()
		sys.exit(2)
	
	if not opts:
		opts.append(('-h',''))
	
	for o, a in opts:
		if o in ('-h', '--help'):
			usage()
			sys.exit(0)
		elif o in ('-v', '--view'):
			try:
				inpt = open(meta, 'r') 
				yobj = yaml.load(inpt)
				if 'main_dir' in yobj:
					print('--main-dir parameter is', yobj['main_dir'])
				else:
					print('--main-dir parameter is not stored')
			except IOError as err:
				print('--main-dir parameter is not stored:', err)
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
			print("There is no '--main-dir' parameter in 'meta.yaml'")
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
	'''
	we skip here 'add.sh' file and '.git' directory
	'''
	listdir = os.listdir('./')
	p = re.compile('\\\\')
	for item in listdir:
		if os.path.isfile(item) and item != 'add.sh':
			files.append(item)
		elif os.path.isdir(item) and item != '.git':
			for root, dirs, fns in os.walk(item):
				'''
				in order to compare pathnames with those from 'project.yaml' 
				substitute every two backslashes with one slash
				'''
				root = p.sub('/',root)
				print('root:', root)
				for f in fns:
					files.append(root + '/' + f)
						
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
	
	if len(fdiff) > 0:
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
						sys.exit(1)
			shutil.move(f, os.path.join(tmpdir, f)) 
			
		print("NOT IN 'project.yaml':\n", '\n'.join(fdiff), sep='')
		print('----')
		
	print("IN 'project.yaml':\n", '\n'.join(fsame), sep='')
	
	shfile = open("add.sh", 'w+')
	print("git add", " ".join(fsame), file=shfile)

if __name__ == '__main__':
	main()