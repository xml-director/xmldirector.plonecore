<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:method="html" encoding="UTF-8"/>
	<xsl:template match="/">
		<html>
			<xsl:apply-templates/>		
		</html>
	</xsl:template>

	<xsl:template match="play">
		<xsl:variable name="title">			
			<xsl:apply-templates select="title"/>
		</xsl:variable>
		<head>
			<title>
				<xsl:value-of select="$title"/>
			</title>
		</head>
		<body>
			<h1>
				<xsl:value-of select="$title"/>
			</h1>
			<h2>
				<xsl:value-of select="playwright"/>
            </h2>			

			<div>
				<xsl:value-of select="edition"/>
			</div>

			<xsl:apply-templates select="personae"/>
			
			<xsl:apply-templates select="act"/>
			
			<xsl:apply-templates select="sourcedetails"/>
		</body>
	</xsl:template>
	
	<xsl:template match="title">
		<xsl:apply-templates/>
	</xsl:template>

	<xsl:template match="lb">
		<xsl:text>&#10;</xsl:text>
	</xsl:template>

	<xsl:template match="personae">
		<div>
			<h6>
				<xsl:value-of select="@playtitle"/>
			</h6>
			<ul>
				<xsl:for-each select="persona">
					<li>
						<span>
							<xsl:value-of select="persname/@short"/>
							<xsl:text> - </xsl:text>
							<xsl:value-of select="persname/text()"/>

							<xsl:text> ( </xsl:text>
							<xsl:for-each select="persaliases/persname">
								<xsl:value-of select="@short"/>
								<xsl:if test="position() != last()">
									<xsl:text>, </xsl:text>
								</xsl:if>
							</xsl:for-each>
							<xsl:text> ) </xsl:text>

							<xsl:text> - </xsl:text>
							<xsl:value-of select="@gender"/>

						</span>
					</li>
				</xsl:for-each>
			</ul>
		</div>
	</xsl:template>

	<xsl:template match="act">
		<div>
			<xsl:attribute name="id" select="concat('act_', position())"/>
			<h2 style="color:Blue;">
				<xsl:value-of select="acttitle"/>
			</h2>
			<xsl:apply-templates select="scene"/>			
		</div>
	</xsl:template>

	<xsl:template match="scene">
		<div>
			<xsl:attribute name="id" select="concat('scene_', parent::act/position(),'_',position())"/>
			<h5 style="color:red;">
				<xsl:value-of select="scenetitle"/>
			</h5>
			
			<xsl:apply-templates select="* "/>	
			<hr/>		
		</div>
	</xsl:template>

	<xsl:template match="stagedir">		
		<h6 style="color:green;">
			<xsl:value-of select="text()"/>
		</h6>
	</xsl:template>

	<xsl:template match="speech">		
        <div>
            <b>  <xsl:value-of select="speaker"/></b>
				<xsl:text>: </xsl:text>
		</div>
		<xsl:for-each select="* ">			
			<xsl:apply-templates select="."/>
		</xsl:for-each>
	</xsl:template>

	<xsl:template match="line">
		<p style="margin:10px;">
			<xsl:apply-templates/>
		</p>
	</xsl:template>

	<xsl:template match="dropcap">
		<span class="dropcap">
			<xsl:value-of select="."/>
		</span>
	</xsl:template>
	
	<xsl:template match="nameref">
		<span class="nameref">
			<xsl:value-of select="."/>
		</span>
	</xsl:template>

	<xsl:template match="finis">
		<h3 id="finish">
			<xsl:value-of select="finistitle"/>
		</h3>
	</xsl:template>
	
	<xsl:template match="sourcedetails">
		<div id="details">
			<p>
				<xsl:value-of select="source"/>
			</p>
			<p>
				<xsl:value-of select="sourceurl"/>
			</p>
			<p>
				<xsl:value-of select="copyright"/>
			</p>
			<p>
				<xsl:value-of select="version"/>
			</p>
			<p>
				<xsl:value-of select="license"/>
			</p>
			<p>
				<xsl:value-of select="licenseurl"/>
			</p>
			<p>
				<xsl:value-of select="termsurl"/>
			</p>			
		</div>
	</xsl:template>
</xsl:stylesheet><!-- Stylus Studio meta-information - (c) 2004-2009. Progress Software Corporation. All rights reserved.

<metaInformation>
	<scenarios>
		<scenario default="yes" name="Scenario1" userelativepaths="yes" externalpreview="no" url="hamlet_ff.xml" htmlbaseurl="" outputurl="result.html" processortype="saxon8" useresolver="yes" profilemode="0" profiledepth="" profilelength=""
		          urlprofilexml="" commandline="" additionalpath="" additionalclasspath="" postprocessortype="none" postprocesscommandline="" postprocessadditionalpath="" postprocessgeneratedext="" validateoutput="no" validator="internal"
		          customvalidator="">
			<advancedProp name="sInitialMode" value=""/>
			<advancedProp name="bXsltOneIsOkay" value="true"/>
			<advancedProp name="bSchemaAware" value="true"/>
			<advancedProp name="bXml11" value="false"/>
			<advancedProp name="iValidation" value="0"/>
			<advancedProp name="bExtensions" value="true"/>
			<advancedProp name="iWhitespace" value="0"/>
			<advancedProp name="sInitialTemplate" value=""/>
			<advancedProp name="bTinyTree" value="true"/>
			<advancedProp name="bWarnings" value="true"/>
			<advancedProp name="bUseDTD" value="false"/>
			<advancedProp name="iErrorHandling" value="fatal"/>
		</scenario>
	</scenarios>
	<MapperMetaTag>
		<MapperInfo srcSchemaPathIsRelative="yes" srcSchemaInterpretAsXML="no" destSchemaPath="" destSchemaRoot="" destSchemaPathIsRelative="yes" destSchemaInterpretAsXML="no"/>
		<MapperBlockPosition></MapperBlockPosition>
		<TemplateContext></TemplateContext>
		<MapperFilter side="source"></MapperFilter>
	</MapperMetaTag>
</metaInformation>
-->
