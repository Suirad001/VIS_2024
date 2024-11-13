
import mbsObject

# Öffnen Free Dyn Files
f = open("Aufgabe_2/test.fdd","r")

# Lesen des Files
fileContent = f.read().splitlines() #Hier speichern wir eine Liste mit mehrer python strings

# Schließt die Datei nach dem speichern 
f.close()

# Suche nach der Anzahl der starren Köper in Code 
numOfRigidBodies = 0 # Initalisieren Variable AnzahlStarrkörper
numOFConstraint = 0
currentTextBlock = []
currentBlockTyp = ""
search4Objects = ["RIGID_BODY","CONSTRAINT"]

listOfMbsObject = []

for line in fileContent:
    if(line.find("$") >= 0): # neuen Block gefunden
        # Wenn der Block nicht leer ist geh in die If Verzweigung rein
        if(currentBlockTyp != ""):
            # Überprüfen auf Starre Körper
            if(currentBlockTyp == "RIGID_BODY"):
                listOfMbsObject.append(mbsObject.mbsObject("body",currentTextBlock))
            # Überprüfen auf Constraints 
            elif(currentBlockTyp == "CONSTRAINT"):
                numOFConstraint +=1 # Mitzählen der Anzahl von Constraints
            currentBlockTyp = ""

    
    for type_i in search4Objects:
        # ,1, weil dollerzeichen an erster stelle steht
        if(line.find(type_i,1,len(type_i)+1)>=0):
            currentBlockTyp=type_i
            # Löschen der Objekte 
            currentTextBlock.clear()

    currentTextBlock.append(line)


# Ausgeben der Anzahl der Starren Körper
print(numOfRigidBodies)
print(numOFConstraint)
print(len(listOfMbsObject))