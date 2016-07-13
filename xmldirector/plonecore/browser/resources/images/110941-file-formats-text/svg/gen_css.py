import os

for name in os.listdir('.'):
    if not name.endswith('.svg'):
        continue

    base, other = name.split('-', 1)
    print 'a.type-file[href*=".{}"]:before {}'.format(base, '{')
    print '    background-image: url(++resource++xmldirector.plonecore/images/110941-file-formats-text/svg/{}) !important;'.format(name)
    print '}'
    print

