        named_image = NamedImage()
        named_image.data = img_data
        named_image.filename = u'test.jpg'
        named_image.contentType = 'image/jpg'
        self.doc.xml_set('xml_image', named_image)
