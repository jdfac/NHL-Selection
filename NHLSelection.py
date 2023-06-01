# -*- coding: utf-8 -*-

# This script allows users to enter desired countries and positions and creates seperate shapefiles broken down by
# those countries and positions, and also updates each player's record with height and weight data in metric units. 

import arcpy
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"INPUT WORKSPACE" # folder for output files

# Define input variables as the feature classes containing country data and player data
countryFC = "Countries_WGS84.shp"  # country shapefile
playerFC = "nhlrosters.shp"        # player shapefile

# Define the country and the positions that the players will be grouped by 
positions = ['C', 'G', 'RW']      # list of player positions to create files for
countries = ['United States', 'Canada', 'Russia']  # list of countries to create files for


# Set up a try/except to handle any errors that occur throughout the script
try: 

    # Set up a for loop to loop through each country provided and create position shapefiles for each
    for location in countries:
        # Set the country variable equal to the current country in the list
        country = location                 # target country name

        countryField = 'CNTRY_NAME'        # name of field which stores the country names
        positionField = 'position'         # name of field which stores the positions

        # Set up sql query and select the desired country from the the countries feature class
        whereClause = countryField + " = '" + country + "'"
        targetCountry = arcpy.SelectLayerByAttribute_management(countryFC, "NEW SELECTION", whereClause)

        # Create a new layer containing only players from the current country 
        targetPlayers = "targetplayers.shp"
        playersFromTargetCountry = arcpy.SelectLayerByLocation_management(playerFC, "CONTAINED_BY", targetCountry)
        arcpy.CopyFeatures_management(playersFromTargetCountry, targetPlayers)

        # Set up an empty list that will be appended with each new shapefile created, this will be used in a for loop 
        # to update height and weight records
        shapefiles = []
        
        # Create a for loop that loops through each poisition in the positions list and creates new shapefiles of players in Sweden
        # grouped by position
        for pos in positions:
            
            # Create the where clause variable for the SelectByAttribute tool
            positionClause = positionField + " = '" + pos + "'"
            positionLayer = arcpy.SelectLayerByAttribute_management(targetPlayers, "NEW SELECTION", positionClause)
            
            # Create new shapefiles based on these selections
            newShp = arcpy.CopyFeatures_management(positionLayer, pos + "From" + country + ".shp")
            
            # Add height_cm and weight_kg fields to the new shapefiles
            arcpy.AddFields_management(newShp, [['height_cm', 'FLOAT', 'height_cm', 4, '', ''], ['weight_kg', 'FLOAT', 'weight_kg', 4, '', '']])
            
            # Add new shapefile to the shapefiles list
            shapefiles.append(pos + "From" + country + ".shp")
        
        # Delete the feature class holding all players from the current country
        arcpy.Delete_management(targetPlayers)

        # Loop through each of the new shapefiles, set up an update cursor, and populate the fields with newly converted heights and weights    
        for shape in shapefiles: 
            with arcpy.da.UpdateCursor(shape, ('height', 'weight', 'height_cm', 'weight_kg')) as cursor:
                for row in cursor:
                    # Perform two string slices on the height field to convert to inches, then convert to centimeters
                    row[2] = round((((int(row[0][0:1]) * 12) + int(row[0][-3:-1])) * 2.54), 1)
                    
                    # Convert weight in pounds to kg
                    row[3] = round((row[1]*0.453592), 1)
                    
                    # Update rows with new data
                    cursor.updateRow(row)
        
        # Delete the row and cursor to avoid a lock
        del row, cursor

except: 
    print("Script has produced an error.")
                

                

          
