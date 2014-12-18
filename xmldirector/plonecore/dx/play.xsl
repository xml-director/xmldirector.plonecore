<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <h1><xsl:value-of select="//title" /></h1>
        <xsl:apply-templates/>
    </xsl:template>
</xsl:stylesheet>
