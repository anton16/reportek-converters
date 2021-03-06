# AWK script to check WFD Art. 13 codes
#
# Code mapping: XML data versus shapefiles
# ------------------------------------------
# ID  Element in XML        Attribute in DBF
# ------------------------------------------
# PA  EUProtectedAreaCode        EU_CD_PA
# CW  EUSurfaceWaterBodyCode     EU_CD_CW
# LW  EUSurfaceWaterBodyCode     EU_CD_LW
# RW  EUSurfaceWaterBodyCode     EU_CD_RW
# TW  EUSurfaceWaterBodyCode     EU_CD_TW
# GW  EUGroundWaterBodyCode      EU_CD_GW
# RB  EURBDCode                  EU_CD_RB
# SU  EUSubUnitCode              EU_CD_SU
# ------------------------------------------
#
# Additional checks of attribute values:
# PA_TYPE  (for PA = protected areas)
# Horizon  (for GW = groundwater bodies)
# CONTINUA (for RW = river water bodies)
#
# Usage: the script is started via id_check.sh
#
# Hermann, March 2010

BEGIN {
	# Field separator
	{ FS = "\t" }

	# XML element name in file_xml
	code_xml  =	id == "PA" ? "EUProtectedAreaCode" :
			id ~ /^(C|L|R|T)W$/ ? "EUSurfaceWaterBodyCode" :
			id == "GW" ? "EUGroundWaterBodyCode" :
			id == "RB" ? "EURBDCode" :
			id == "SU" ? "EUSubUnitCode" : "UNDEFINED"

	# Shapefile attribute name in file_dbf
	code_dbf  =	"EU_CD_" id

	# PA_TYPE check: legal values, attribute name
	if (id == "PA") {
		str = "{'BA','BI','FI','SH','HA','NI','UW','A7','EU','NA','LO'}"
		att = "PA_TYPE"

		# str =	"{'Bathing','BA','Birds','BI','Fish','FI','Shellfish','SH','Habitats','HA',\
		#		'Nitrates','NI','UWWT','UW','Article 7 Abstraction for drinking water','A7',\
		#		'EuropeanOther','EU','National','NA','Local','LO'}"
		# gsub(/[\t]/, "", str)
	}

	# GW Horizon check: legal values, attribute name
	else if (id == "GW") {
		str = "{'1','2','3','4'}"
		att = "HORIZON"
	}

	# RW CONTINUA check: legal values, attribute name
	else if (id == "RW") {
		str = "{'Y','N','L','R','T','C','V'}"
		att = "CONTINUA"
	}
}

# Remember values in XML file
NR == FNR {
	if ($1 == code_xml)
		XML[$2]
	next
}

# Now processing the dumped DBF file

# Attribute names to UPPER, trim values
NF {
	sub(/: /, "\t")

	if ($1 != "Record")
		HDR[$1]

	$1 = toupper($1)
	$2 = trim($2)
}

# Remember attribute values
$1 == code_dbf {
	DBF[$2]

	# Remove virtual river segments
	if (id == "RW" && $2 == "(NULL)")
		delete DBF[$2]
}

# Additional check: PA_TYPE, HORIZON or CONTINUA
str && $1 == att { 

	if (index(str, toupper($2)))
		DEF[$2]++
	else
		UND[$2]++
}

# Make some simple tests
END {
	print ORS "Checking results for:"
	print f1 "/manage_document"
	print f2 "/manage_document"
	print ""

	# Number of array elements
	lenXML = length(XML)
	lenDBF = length(DBF)
	lenDEF = length(DEF)
	lenUND = length(UND)

	# str is only defined in case of additional checks
	if (str) {

		if (! (lenDEF + lenUND)) {
			print "Attribute NOT found:", att, str ORS

			print "Shapefile attributes:"
			for (i in HDR)
				print "    '" i "'"

			print ""

		} else {

			if (lenDEF) {

			#	print "Legal values for attribute:", att, str

			#	for (i in DEF)
			#		printf "%8d occurrence%s of %s\n", DEF[i], (DEF[i]>1?"s":" "), "'" i "'"

			#	print ""

			} else {

				print "NO legal values found for attribute:", att, str ORS
			}

			if (lenUND) {

				print "Undefined values for attribute:", att, lenDEF ? str : ""

				for (i in UND)
					printf "%8d occurrence%s of %s\n", UND[i], (UND[i]>1?"s":" "), "'" i "'"

				print ""

			} else {

			#	print "No undefined values found for attribute:", att ORS ORS
			}
		}
	}

	# print  "Code values in XML data and shapefile"
	# printf "%8d unique %s value%s in XML data\n",  lenXML, code_xml, (lenXML > 1 ? "s" : "")
	# printf "%8d unique %s value%s in shapefile\n", lenDBF, code_dbf, (lenDBF > 1 ? "s" : "")

	# If one or even both arrays are empty
	if ( ! (lenXML + lenDBF))
		printf "\nNO code values found in either file\n"

	else if ( ! lenXML)
		printf "\nNO %s values found in XML data\n", code_xml

	else if ( ! lenDBF) {
		printf "\nNO %s values found in shapefile\n\n", code_dbf

		print "Shapefile attributes:"
		for (i in HDR)
			print "    '" i "'"

	}

		
	# If there is something to cross-check
	else {
		for (i in DBF)
			if ( ! (i in XML)) {
				not = not sep sprintf("%8d %s", ++cnt, "'" i "'")
				sep = ORS
			}

		if (cnt) {

			sfx = cnt > 1 ? "s" : ""

			print  "Code values in XML data and shapefile"
			printf "%8d unique %s value%s in XML data\n",  lenXML, code_xml, (lenXML > 1 ? "s" : "")
			printf "%8d unique %s value%s in shapefile\n", lenDBF, code_dbf, (lenDBF > 1 ? "s" : "")

			printf "\n%8d %s %s %s %s\n\n%s\n", cnt, code_dbf,
			"value" sfx " from shapefile NOT found as", code_xml, "in XML data", not

		} else {

		#	printf "\nAll %s %s %s %s\n", code_dbf,
		#	"values from shapefile found as", code_xml,	"in XML data"
		}
	}

	printf "\n----------------------------------------\n"
}

# Remove leading and trailing [[:space:]] characters
function trim(str)
{
	sub(/^[[:space:]]+/, "", str)
	if (str "")  sub(/[[:space:]]+$/, "", str)
	return str
}

# Trim first, then reduce internal sequences
# of [[:space:]] characters to a single space
function normalize_space(str)
{
	str = trim(str)
	if (str "") gsub(/[[:space:]]+/, " ", str)
	return str
}

# vim: tw=100 ts=4 sw=4
