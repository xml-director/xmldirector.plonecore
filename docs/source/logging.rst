Logging
=======

Standard logging
----------------

``xmldirector.plonecore`` comes has its own logger that will write
its output to the standard configured Plone logger which is usally
bound to ``var/log/instance.log`` if not configured otherwise. The 
``LOG`` object is just a tiny wrapper for the standard Python 
logging facility (see https://docs.python.org/2/library/logging.html).


Usage::

    from xmldirector.plonecore.logger import LOG

    def my_code(...):
        
        LOG.debug('debug message')
        LOG.info('info message')
        LOG.warn('warn message')
        LOG.error('error message')


Persistent logging
------------------

``xmldirector.plonecore`` also support persistent logging where
the log data is stored on an arbitrary persistent Plone object.
This functionality can be used for logging object specific data
(e.g. XML conversion results).

Usage::

    from xmldirector.plonecore.logger import IPersistentLogger


    def convert_it(...):

        # ``context`` represents the current context object
        
        adapter = IPersistentLogger(context)
        adapter.log(u'this is a logging message')
        adapter.log(u'this is an error message', level='error')
        adapter.log(u'this is an error message', level='error', details='....')

