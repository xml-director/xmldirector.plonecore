Adding custom content-types to the Plone Client Connector
=========================================================

This documentation explains how to extend the Plone Client Connector with your
own or custom Plone content-types.

Custom content-types can be registered with the Produce & Publish server using
the Zope Component Architecture. The one single contact of the P&P server with a
content-type is the existence of a ``@@asHTML`` view for the related content-type.
The ``@@asHTML`` view must return a HTML snippet that will be used by the P&P
within the main body of its own rendering PDF template.

As an example look at the ``@@asHTML`` view for Plone news items.

The ``@@asHTML`` view is configured through ZCML (within your
configure.zcml file):

::

        <browser:page
          name="asHTML"
          for="Products.ATContentTypes.interface.news.IATNewsItem"
          permission="zope2.View"
          class=".newsitem.HTMLView"
          />

and implemented as browser view (newsitem.py):

::

    from Globals import InitializeClass
    from Products.Five.browser import BrowserView
    from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
    
    class HTMLView(BrowserView):
        """ This view renders a HMTL fragment for the configured content type """
    
        template = ViewPageTemplateFile('newsitem_raw.pt')
    
        def __call__(self, *args, **kw):
            return self.template(self.context)
    
    InitializeClass(HTMLView)

The related templates renders a snippet of code for a news item
object:
::

    <div class="type-newsitem document-body">
        <h1 class="title bookmark-title" tal:content="context/Title" />
        <div class="description" tal:content="context/Description" />
        <div>
            <div class="image-box" tal:condition="nocall: context/image | nothing">    
                <img class="teaser-image" src="image" />
                <div class="image-caption" tal:content="context/getImageCaption | nothing" />
            </div>
    
            <div class="body" tal:content="structure context/getText" />
        </div>
    </div>

In addition your content-type implementation **must** provide the
``pp.client.plone.interfaces.IPPContent`` interface - either by
specifying this interface as part of the class definition in your code

::

    class MyContentType(...):

        implements(IPPContent)

or you add the interfaces as a marker interface through ``ZCML``

::

    <five:implements
        class="my.package.contents.mytype.MyContentType"
        interface="pp.client.plone.interfaces.IPPContent"
    />

Only content objects providing the ``IPPContent`` interface are being considered
during the aggregation phase of the Plone Client Connector.

For further example code, please refer to the
*pp/client/plone/browser* directory. The ``folder`` integration
*(folder.py)* shows you a more complex example and involves aggregation of
other content.

