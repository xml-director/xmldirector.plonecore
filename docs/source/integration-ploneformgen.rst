Integration with PloneFormGen
=============================

Using Produce & Publish with PloneFormGen - generating PDF
documents from form data.

Installation
~~~~~~~~~~~~

-  Install **PloneFormGen**

Converting form data to PDF
~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  use a script adapter with the following code

::

    view = context.restrictedTraverse('@@asPFGPDF')
    pdf =  view()
    R = context.REQUEST.RESPONSE
    R.setHeader('content-type', 'application/pdf')
    R.setHeader('content-length', len(pdf))
    R.setHeader('content-disposition', 'attachment; filename=%s.pdf' % context.getId())
    R.write(pdf)


e  You can access PFG form values within your PDF template using
   (in this case we have a form parameter ``fullname``)

::

    <span tal:replace="options/request/fullname | nothing">Fullname</span>
