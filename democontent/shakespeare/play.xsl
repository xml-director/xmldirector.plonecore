<xsl:stylesheet 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0">

<!-- parameter "dir" must be set from the command line: it represents the output directory -->

<xsl:variable name="backcolor" select="'#FFFFCC'" />
<xsl:variable name="panelcolor" select="'#88FF88'" />


<xsl:output name="play" method="html"/>
<xsl:output name="scene" method="html"/>

<xsl:template match="play">
    <html>
      <head>
        <title><xsl:apply-templates select="TITLE"/></title>
      </head>
      <body bgcolor='{$backcolor}'>
        <center>
            <h1><xsl:value-of select="TITLE"/></h1>
            <h3><xsl:apply-templates select="PLAYSUBT"/></h3>
            <i><xsl:apply-templates select="SCNDESCR"/></i>
        </center>
        <br/><br/>
        <table>
          <tr>
            <td width='350' valign='top' bgcolor='{$panelcolor}'>
              <xsl:apply-templates select="PERSONAE"/>
            </td>
            <td width='30'></td>
            <td valign='top'>
              <xsl:apply-templates select="PROLOGUE | ACT | EPILOGUE"/>
            </td>
          </tr>
        </table>
        <hr/>
      </body>
    </html>
    </xsl:result-document>
</xsl:template>

<xsl:template match="act/title">
    <center>
      <h3>
	    <xsl:apply-templates/>
      </h3>
    </center>
</xsl:template>

<xsl:template match="playsubt">
	<xsl:apply-templates/>
</xsl:template>

<xsl:template match="personae">
	<xsl:apply-templates/>
</xsl:template>

<xsl:template match="personae/title">
    <center>
      <h3>
	    <xsl:apply-templates/>
      </h3>
    </center>
</xsl:template>

<xsl:template match="personae/persona">
    <table>
      <tr>
        <td valign="top">
	      <xsl:apply-templates/>
        </td>
      </tr>
    </table>
</xsl:template>

<xsl:template match="pgroup">
    <table>
      <tr>
        <td width="160" valign="top">
	      <xsl:apply-templates select="PERSONA"/>
	    </td>
	    <td width="20"></td>
	    <td valign="bottom">
	      <i>
	        <xsl:apply-templates select="GRPDESCR"/>
	      </i>
	    </td>
	  </tr>
	</table>
</xsl:template>

<xsl:template match="pgroup/persona">
    <xsl:apply-templates/>
    <br/>
</xsl:template>

<xsl:template match="pgroup/grpdescr">
    <xsl:apply-templates/>
    <br/>
</xsl:template>

<xsl:template match="scndescr">
	<xsl:apply-templates/>
</xsl:template>

<xsl:template match="act">
    <hr/>
	<xsl:apply-templates/>
    <xsl:if test="position()=last()"><hr/></xsl:if>
</xsl:template>

<xsl:template match="scene|prologue|epilogue">
    <xsl:variable name="NR"><xsl:number count="SCENE|PROLOGUE|EPILOGUE" level="any"/></xsl:variable>
    <xsl:variable name="play"><xsl:value-of select="ancestor::PLAY/TITLE"/></xsl:variable>
    <xsl:variable name="act"><xsl:value-of select="ancestor::ACT/TITLE"/></xsl:variable>

    <a href="scene{$NR}.html">
        <xsl:value-of select="TITLE" />
    </a>
    <br/>

    <xsl:result-document href="{$dir}/scene{$NR}.html" format="scene">
      <html>
        <head>
          <title>
            <xsl:value-of select="concat($play, ' ', $act, ': ', TITLE)"/>
          </title>
        </head>
        <body bgcolor='{$backcolor}'>
          <p>
            <a href="play.html"><xsl:value-of select="$play"/></a>
            <br/>
            <b><xsl:value-of select="$act"/></b>
            <br/>
          </p>
          <xsl:apply-templates/>
        </body>
      </html>
    </xsl:result-document>
</xsl:template>

<xsl:template match="scene/title | prologue/title | epilogue/title">
    <h1>
      <center>
	    <xsl:apply-templates/>
	  </center>
	</h1>
	<hr/>
</xsl:template>

<xsl:template match="speech">
    <table>
      <tr>
        <td width="160" valign="top">
	      <xsl:apply-templates select="SPEAKER"/>
        </td>
        <td table="top">
          <xsl:apply-templates select="STAGEDIR|LINE"/>
        </td>
	  </tr>
	</table>
</xsl:template>

<xsl:template match="speaker">
    <b>
      <xsl:apply-templates/>
      <xsl:if test="not(position()=last())"><br/></xsl:if>
    </b>
</xsl:template>

<xsl:template match="scene/stagedir">
    <center>
      <h3>
	    <xsl:apply-templates/>
	  </h3>
	</center>
</xsl:template>

<xsl:template match="speech/stagedir">
    <p>
      <i>
	    <xsl:apply-templates/>
	  </i>
	</p>
</xsl:template>

<xsl:template match="line/stagedir">
    <xsl:text> [ </xsl:text>
    <i>
	  <xsl:apply-templates/>
	</i>
	<xsl:text> ] </xsl:text>
</xsl:template>

<xsl:template match="scene/subhead">
    <center>
      <h3>
	    <xsl:apply-templates/>
	  </h3>
	</center>
</xsl:template>

<xsl:template match="speech/subhead">
    <p>
      <b>
	    <xsl:apply-templates/>
	  </b>
	</p>
</xsl:template>

<xsl:template match="line">
	<xsl:apply-templates/>
	<br/>
</xsl:template>

</xsl:stylesheet>	
