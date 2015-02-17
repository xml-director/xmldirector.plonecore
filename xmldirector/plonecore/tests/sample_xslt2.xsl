<xsl:stylesheet version='2.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
     xmlns:previous='http://www.example.com/v1'>
  <xsl:output encoding='UTF-8' indent='yes' method='xml'/>
  <xsl:variable name='oldUri' select='namespace-uri((//previous:*)[1])' />

  <!-- Identity transform -->
  <xsl:template match='@*|node()'>
    <xsl:copy>
      <xsl:apply-templates select='@*|node()'/>
    </xsl:copy>
  </xsl:template>
  <!-- Previous namespace -> current. No other changes required. -->
  <xsl:template match='previous:*'>
    <xsl:element name='{local-name()}' namespace='http://www.example.com/v2'>
      <xsl:copy-of select='namespace::*[not(. = $oldUri)]' />
      <xsl:apply-templates select='@* | node()' />
    </xsl:element>
  </xsl:template>
</xsl:stylesheet>
