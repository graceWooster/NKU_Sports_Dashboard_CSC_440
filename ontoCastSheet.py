import openpyxl

#get the file names
fromFileName = input("Enter file path of input file: ")
toFileName = input("Enter file path of output file: ")

fromFile = openpyxl.load_workbook(fromFileName)
toFile = openpyxl.load_workbook(toFileName)

fromSheet = fromFile['Player Averages']     #Now in sheet of excel with info
toSheet = toFile['Player Stats']            #Now in sheet where info will be placed

row = 4        #Where info starts

while fromSheet.cell(row=row, column=2).value is not None:      #Begin data transfer
    playerNum = fromSheet.cell(row=row, column=2).value
    placement = playerNum + 2
    if playerNum == 0 or playerNum == 00:
        placement = 104
    print("\nOn Player Number " + str(playerNum))
    for i in range(5, 16):
        match i:                                                                                        #Player Averages
            case 5:
                toSheet.cell(row=placement, column=12).value = fromSheet.cell(row=row, column=i).value        #Minutes
            case 6:
                toSheet.cell(row=placement, column=5).value = fromSheet.cell(row=row, column=i).value         #Field Goal Percentage
            case 7:
                toSheet.cell(row=placement, column=6).value = fromSheet.cell(row=row, column=i).value         #Three Point Precentage
            case 8:
                toSheet.cell(row=placement, column=7).value = fromSheet.cell(row=row, column=i).value         #Free Throw Percentage
            case 11:
                toSheet.cell(row=placement, column=8).value = fromSheet.cell(row=row, column=i).value         #Rebounds
            case 12:
                toSheet.cell(row=placement, column=9).value = fromSheet.cell(row=row, column=i).value         #Assists
            case 13:
                toSheet.cell(row=placement, column=11).value = fromSheet.cell(row=row, column=i).value        #Steals
            case 14:
                toSheet.cell(row=placement, column=10).value = fromSheet.cell(row=row, column=i).value        #Blocks
            case 15:
                toSheet.cell(row=placement, column=4).value = fromSheet.cell(row=row, column=i).value         #Points
            case _:
                pass
    row += 1

splitted = toFileName.split(".")
newName = "_updated.".join(splitted)

toFile.save(newName)

fromFile.close()
toFile.close()

print("\n\nProgram Finished")