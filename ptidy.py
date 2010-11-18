#!/usr/bin/python
''''
 status - alpha
 v.08
 last changes: thanks to ['ignore']['files'] and ['ignore']['dirs'] arrays in 'project.yaml'
 you can skip particular files and files in sub-directories in your disk project folder 
 you don't want these files to be compared  against those ones stored in 'project.yaml'
 v.07 
 last changes: if 'project.yaml' contains 'ignore' and 'units' arrays then they'll be used, e.g.

project.yaml example:
---
#general 
ignore:
 files:
 - .cache
 dirs:
 - .git
 
units:
 -
 #a
  name: upload an image to the server
  description: it's a cgi-bin perl script that allows you to upload an image to the server
  files:
   - &a1 uploader.pl
   - &a2 upload2.pl
   - &a3 config/config.pl
   - &a4 views/_template.html
   - &a5 views/test/test.txt
  main:
   *a1: [*a3, *a4]
  components:
   *a4: [*a2:[*a3]]
'''

import os, getopt, sys, shutil, yaml, re, copy
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
	
def file2re(path):
	begin_dot = re.compile('^\.')
	if begin_dot.match(path):
		path = begin_dot.sub('.+?\.', path)
	else:
		dot = re.compile('\.')
		path = dot.sub('\.', path)
	
	slash = re.compile('\/')
	path = slash.sub('\/', path)
	print(path)
	return path
	
def dir2re(path):
	def repl(m):
		if  m.group(0) == '':
			return '\.\/'
		else:
			return m.group(0)
		
	begin_dot = re.compile('^\.\/(.*)')
	path = re.sub('^\.\/(.*)', repl, path)
	
	dot = re.compile('\.')
	path = dot.sub('\.', path)
	
	slash = re.compile('\/')
	path = slash.sub('\/', path)
	print(path)
	return path
	
	
def my_walk(path, skip_files, skip_dirs):	
	files = []
	start_path_re = re.compile('^' + dir2re(path))
	backsl_re = re.compile('\\\\')
	
	skip_files_re = ''
	
	if type(skip_files).__name__ == 'list' and len(skip_files)>0:
		for index, item in enumerate(skip_files):
			skip_files[index] = file2re(item)
		pat = '(?:' + '|'.join(skip_files) + ')' + '\Z'
		print(pat)
		skip_files_re = re.compile(pat)
	
	skip_dirs_re = ''
	if type(skip_dirs).__name__ == 'list' and len(skip_dirs)>0:
		for index, item in enumerate(skip_dirs):
			skip_dirs[index] = dir2re(item)
		pat = '^' + dir2re(path) + '(?:' + '|'.join(skip_dirs) + ')'
		print(pat)
		skip_dirs_re = re.compile(pat)
	
	def process_walk(path, skip_files_re, skip_dirs_re):
		for item in os.listdir(path):
			# combined path
			p = os.path.join(path, item)
			if os.path.isfile(p) and (not skip_files_re or not skip_files_re.match(item)):
				files.append(backsl_re.sub('/', start_path_re.sub('', p)))
			if os.path.isdir(p) and (not skip_dirs_re or not skip_dirs_re.match(p)):
				process_walk(p, skip_files_re, skip_dirs_re)
		return files
	return process_walk(path, skip_files_re, skip_dirs_re)
	
	
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
	# 1
	yfile = open(os.path.join(fullpath, proj_file), 'r')
	yobj = yaml.load(yfile)
	yfiles = [proj_file]
	
	skip_files = []
	skip_dirs = []
	if 'ignore' in yobj:
		if 'files' in yobj['ignore']:
			skip_files = yobj['ignore']['files']
		if 'dirs' in yobj['ignore']:
			skip_dirs = yobj['ignore']['dirs']	
	
	# 2 
	os.chdir(fullpath)
	files = my_walk('./', skip_files, skip_dirs)
									
	units = yobj['units'] if 'units' in yobj else yobj
	for o in units:
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