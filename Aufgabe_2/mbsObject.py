
class mbsObject:
    def __init__(self,type,text):
        self.__type = type
        
        for line in text:
            # Eine Zeile wird gespaltet in 2 oder auch mehr 
            splitted = line.split(":")
            # Nur Text übernehmen. Leerzeichen davor und danach werden nicht mitgenommen
            if(splitted[0].strip() == "mass"):
                # Suchen und speichern der Masse im file als Float
                self.mass = float(splitted[1])