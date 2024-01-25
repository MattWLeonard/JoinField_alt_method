import arcpy as a
from arcpy import env


# access current mxd
a.mapping.MapDocument('CURRENT')   # use if running within ArcMap
mxd = a.mapping.MapDocument('CURRENT')   # use if running within ArcMap


gdb = ""
a.env.workspace = gdb


################################################################################

######  FUNCTION DOESN'T CHANGE  vvvvvvvvvvvvvvvvvv

# DEFINE FUNCTION
def joinfieldsfunction(targettable,targetkey,targetwhere,jointable,joinkey,joinwhere,joinfields,joinprefix):
						# joinfields should be list of field names like ["name1","name2"] ^
	# define joinpre
	if joinprefix:
		joinpre = joinprefix
	else:
		joinpre = "JOINED"

##	# OR, define joinsuf instead of prefix
##	if joinsuffix:
##		joinsuf = joinsuffix
##	else:
##		joinsuf = "JOINED"

	# establish list of field names in target
	targetfieldlist = []
	for f in a.ListFields(targettable):
		targetfieldlist.append(f.name)

	# add empty join field(s) to be populated to target table
	for f in a.ListFields(jointable):
		if f.name in joinfields:
			# get field properties to add (name, type, length, domain)
			fieldprops = [f.name,f.type,f.length,f.domain]
			if f.name in targetfieldlist: # field already exists in target	# works
				addfield = 	joinpre + "_" + fieldprops[0]
##				addfield = 	fieldprops[0] + "_" + joinsuf	# alternate suffix instead of prefix
			else: # field does NOT already exist in target
				addfield = 	fieldprops[0]
			addtype = 	fieldprops[1]
			addlength = fieldprops[2]
			alias = 	addfield
			domain = 	fieldprops[3]
			# add field with matching properties to target table
			a.AddField_management(targettable,addfield,addtype,"","",addlength,alias,"","",domain)

	# build dictionary of values in join fields
	join_dict = {}
	cursordata =	jointable
	cursorfields =	[joinkey]
	for f in joinfields:
		cursorfields.append(f)
	whereclause = 	joinwhere
	with a.da.SearchCursor(cursordata, cursorfields, whereclause) as cursor:
		for row in cursor:
			joinvalues = []
			i = 1
			while i <= len(joinfields):
				joinvalues.append(row[i])
				i +=1
			join_dict[row[0]] = joinvalues
	del cursor

	# cursor to populate join fields in target table from dictionary
	cursordata = 	targettable
	cursorfields =	[targetkey]
	for f in joinfields:
		if f in targetfieldlist: # field already exists in target	# works
			cursorfields.append(joinpre + "_" + f)
##			cursorfields.append(f + "_" + joinsuf)	# alternate suffix instead of prefix
		else: # field does NOT already exist in target
			cursorfields.append(f)
	whereclause = 	targetwhere
	with a.da.UpdateCursor(cursordata, cursorfields, whereclause) as cursor:
		for row in cursor:
			if row[0] in join_dict:		# account for target records with no match
				i = 1
				while i <= len(joinfields):
					row[i] = join_dict[row[0]][i-1]
					i += 1
				cursor.updateRow(row)
##			else:						# Enable this part to delete target features with no match
##				cursor.deleteRow()		#   (like KEEP_COMMON)
	del cursor
	del join_dict

######  FUNCTION DOESN'T CHANGE  ^^^^^^^^^^^^^^^^^^^


# function inputs

targettable =	""
targetkey =		""
targetwhere	=	""  # optional - leave as is, or complete

jointable =		""
joinkey =		""
joinwhere = 	""  # optional - leave as is, or complete

joinprefix = 	""  # optional - leave as is, or complete

joinfields = 	[
				"---field1---",
				"---field2---",
				"---field3---",
				]

# RUN JOIN FIELDS FUNCTION
joinfieldsfunction(targettable,targetkey,targetwhere,jointable,joinkey,joinwhere,joinfields,joinprefix)