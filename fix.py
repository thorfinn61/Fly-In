import glob

for f in glob.glob('src/**/*.py', recursive=True):
    with open(f, 'r') as fp:
        lines = fp.read().split('\n')
    
    with open(f, 'w') as fp:
        fp.write('\n'.join(line.rstrip() for line in lines))

