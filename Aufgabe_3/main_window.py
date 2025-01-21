# Importiere das mbsModel-Modul
import mbsModel
# Importiere Path, um mit Dateipfaden zu arbeiten
from pathlib import Path
# Importiere wichtige Klassen aus PySide6 (GUI-Komponenten)
from PySide6.QtGui import QAction, QStandardItemModel, QStandardItem, QGuiApplication
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QMenu, QTreeView, QWidget, QHBoxLayout, QSplitter, QInputDialog
from PySide6.QtCore import Qt
# Importiere das MainWidget für das Rendering
from main_widget import MainWidget
# Importiere den Renderer aus VTK
from vtkmodules.vtkRenderingCore import vtkRenderer
# Importiere QVTKRenderWindowInteractor für die Interaktion mit dem VTK-Renderfenster
import QVTKRenderWindowInteractor as QVTK
import vtk

# Alias für das QVTKRenderWindowInteractor-Modul
QVTKRenderWindowInteractor = QVTK.QVTKRenderWindowInteractor

# ===================================================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        """Initialisiert das Hauptfenster der Anwendung."""
        super().__init__()  # Ruft den Konstruktor der Elternklasse auf

        # --------------------- Initialisierung und Basiskonfiguration --------------------------------
        # Initialisiere das Modell
        self.myModel = None  # Anfangs kein Modell geladen
        self.setWindowTitle("3D Modell in Qt mit VTK")  # Setze den Titel des Fensters
        
        # Bildschirmgröße herauslesen
        screen_geometry = QGuiApplication.primaryScreen().geometry()  # Bildschirmauflösung
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Berechne 70 % der Bildschirmgröße
        window_width = int(screen_width * 0.7)
        window_height = int(screen_height * 0.7)
        # Setze die Größe und zentriere das Fenster
        self.resize(window_width, window_height)


        # --------------------- VTK-Widget -------------------------------------------------------------
        self.widget = MainWidget(self)  # Erstelle ein VTK-Widget
        self.widget.renderer.SetBackground(0.0, 0.0, 0.0)  # Hintergrund für den Renderer auf Schwarz

        # --------------------- Strukturbaum -----------------------------------------------------------
        self.treeModel = QStandardItemModel()
        self.treeModel.setHorizontalHeaderLabels(['Strukturbaum'])  # Header für den Baum
        self.treeView = QTreeView(self)  # Erstelle das QTreeView-Widget
        self.treeView.setModel(self.treeModel)  # Verknüpfe den Baum mit dem Modell
        # Strukturbaum größe definieren
        self.treeView.setMinimumWidth(80)  # Mindestbreite
        self.treeView.setMaximumWidth(600)  # Maximale Breite
        # Kontextmenü für den Strukturbaum aktivieren
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)  # Kontextmenü aktivieren
        self.treeView.customContextMenuRequested.connect(self.show_context_menu)  # Methode verknüpfen

        # --------------------- Layout ----------------------------------------------------------------
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.treeView)  # Strukturbaum
        splitter.addWidget(self.widget)  # VTK-Widget
        splitter.setSizes([120, self.width() - 120])

        container = QWidget(self)
        layout = QHBoxLayout(container)
        layout.addWidget(splitter)
        self.setCentralWidget(container)

        # --------------------- GUI-Komponenten erstellen ----------------------------------------------
        self.create_menu() # Menüleiste
        self.statusBar().showMessage("Kein Modell geladen") # Statusleiste

        # --------------------- Rendering initialisieren ---------------------
        self.widget.GetRenderWindow().Render()

# =======================================================================================================   

    def create_menu(self):
        # Erstellen der Menübar und Befüllen
        """Erstellt die Menüleiste und ihre Aktionen."""
        menubar = self.menuBar() # Anlegen der Menüleiste

    # ===================================================================================================
    # Anlegen der Hauptpunkte in der Menüleiste

        file_menu = menubar.addMenu('File') # Menü Hauptpunkt File hinzugefügt
        view_menu = menubar.addMenu('View') # Menü Hauptpunkt View hinzugefügt
        settings_menu = menubar.addMenu('Einstellungen') # Menü Hauptpunkt Einstellungen hinzugefügt

    # ===================================================================================================
    # Anlegen der Unterpunkte in File

        # 'Load' Aktion hinzufügen
        load_action = QAction('Load', self)
        load_action.triggered.connect(self.load_model)
        file_menu.addAction(load_action)

        # 'Save' Aktion hinzufügen
        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_model)
        file_menu.addAction(save_action)

        # 'Import FDD' Aktion hinzufügen
        import_action = QAction('ImportFdd', self)
        import_action.triggered.connect(self.import_fdd)
        file_menu.addAction(import_action)

        # 'Exit' Aktion hinzufügen
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    # ==================================================================================================
    # Unterpunkte von View anlegen

        # Front Ansicht hinzufügen
        front_action = QAction('Front Ansicht', self)
        front_action.triggered.connect(self.set_front_view)  # Verknüpfe die Aktion mit einer Methode
        view_menu.addAction(front_action)

        # Top Ansicht hinzufügen
        top_action = QAction('Top Ansicht', self)
        top_action.triggered.connect(self.set_top_view)  # Verknüpfe die Aktion mit einer Methode
        view_menu.addAction(top_action)
                
        # Ansicht von Rechts hinzufügen
        top_action = QAction('Rechts Ansicht', self)
        top_action.triggered.connect(self.set_rigth_view)  # Verknüpfe die Aktion mit einer Methode
        view_menu.addAction(top_action)

    # ==================================================================================================
    # Unterpunkte von Einstellungen anlegen

        # Steuerung Untermenü hinzufügen
        steuerung_menu = QMenu("Steuerung", self)

        # ==============================================================================================
        # Unterpunkte von Steuerung

        # 'Steuerung Abaqus' hinzufügen
        abaqus_action = QAction('Steuerung Abaqus', self)
        abaqus_action.triggered.connect(self.set_interaction_abaqus)
        steuerung_menu.addAction(abaqus_action)

        # 'Steuerung Creo' hinzufügen
        creo_action = QAction('Steuerung Creo', self)
        creo_action.triggered.connect(self.set_interaction_creo)
        steuerung_menu.addAction(creo_action)

        settings_menu.addMenu(steuerung_menu)

# ===================================================================================================  

    def load_model(self):
        """Lädt ein Modell aus einer JSON-Datei."""
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Open json File", "", "JSON and FDD Files (*.json *.fdd)", options=options) # Filter gleich nach fdd und json datein
        
        if filename:
            if filename.lower().endswith(".json"):  # Überprüfe, ob die Datei eine JSON-Datei ist
                """""Lädt das Modell aus einer json-Datei."""
                try:
                    self.myModel = mbsModel.mbsModel()  # Erstelle ein neues Modell
                    print(f"Lade Modell aus Datei: {filename}")
                    self.myModel.loadDatabase(Path(filename))  # Lade das Modell aus der JSON-Datei
                    self.statusBar().showMessage(f"Modell geladen: {filename}")
                    self.widget.update_renderer(self.myModel)  # Aktualisiere das Rendering mit dem neuen Modell
                    self.add_structure_tree()  # Hier den Strukturbaum hinzufügen, nach dem Modell laden
                except Exception as e:
                    self.statusBar().showMessage(f"Fehler beim Laden des Modells: {e}")
                    print(f"Fehler beim Laden des Modells: {e}")
            else:
                self.show_error_message("Ungültige Datei", "Bitte wählen Sie eine gültige JSON-Datei aus.")
        else:
            self.statusBar().showMessage("Modell-Laden abgebrochen")
            
# ===================================================================================================  

    def import_fdd(self):
        """Importiert ein FDD-Modell aus einer Datei."""
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Import FDD File", "", "JSON and FDD Files (*.json *.fdd)", options=options) # Filter gleich nach fdd und json datein

        if filename:
            if filename.lower().endswith(".fdd"):  # Überprüfe, ob die Datei eine Fdd-Datei ist
                """""Lädt das Modell aus einer FDD-Datei."""
                try:
                    self.myModel = mbsModel.mbsModel()
                    self.myModel.importFddFile(filename)
                    self.statusBar().showMessage(f"FDD-Datei importiert: {filename}")
                    self.widget.update_renderer(self.myModel)
                    self.add_structure_tree()  # Hier den Strukturbaum hinzufügen, nach dem Modell laden
                except Exception as e:
                    self.statusBar().showMessage(f"Fehler beim Importieren der FDD-Datei: {e}")
            else:
                self.show_error_message("Ungültige Datei", "Bitte wählen Sie eine gültige Fdd-Datei aus.")
        else:
            self.statusBar().showMessage("Modell-Laden abgebrochen")
            
# ===================================================================================================  

    def save_model(self):
        """Speichert das Modell in einer JSON-Datei."""
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Save Model File", "", "JSON Files (*.json)", options=options)
        if filename:
            self.myModel.saveDatabase(Path(filename))  # Speichert das Modell
            self.statusBar().showMessage(f"Modell gespeichert: {filename}")

# ===================================================================================================  

    def show_error_message(self, title, message):
        """Zeigt eine Fehlermeldung an."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()
        
# =================================================================================================== 

    def set_front_view(self):
        """Setzt die Kamera in die Frontansicht."""
        camera = self.widget.renderer.GetActiveCamera()  # Aktive Kamera holen
        camera.SetPosition(0, 1, 0)  # Setze die Kamera über das Modell
        camera.SetFocalPoint(0, 0, 0)  # Fokus auf den Ursprung
        camera.SetViewUp(0, 0, 1)  # Oben ist die Z-Achse
        self.widget.renderer.ResetCamera()  # Stellt sicher, dass das gesamte Modell sichtbar ist
        self.widget.GetRenderWindow().Render()  # Szene neu rendern
        
# ===================================================================================================  

    def set_top_view(self):
        """Setzt die Kamera in die Draufsicht."""
        camera = self.widget.renderer.GetActiveCamera()  # Aktive Kamera holen
        camera.SetPosition(0, 0, 1)  # Setze die Kamera über das Modell
        camera.SetFocalPoint(0, 0, 0)  # Fokus auf den Ursprung
        camera.SetViewUp(0, 1, 0)  # Oben ist die Y-Achse
        self.widget.renderer.ResetCamera()  # Stellt sicher, dass das gesamte Modell sichtbar ist
        self.widget.GetRenderWindow().Render()  # Szene neu rendern
        
    # ===================================================================================================  

    def set_rigth_view(self):
        """Setzt die Kamera in die Draufsicht."""
        camera = self.widget.renderer.GetActiveCamera()  # Aktive Kamera holen
        camera.SetPosition(1, 0, 0)  # Setze die Kamera über das Modell
        camera.SetFocalPoint(0, 0, 0)  # Fokus auf den Ursprung
        camera.SetViewUp(0, 0, 1)  # Oben ist die Y-Achse
        self.widget.renderer.ResetCamera()  # Stellt sicher, dass das gesamte Modell sichtbar ist
        self.widget.GetRenderWindow().Render()  # Szene neu rendern

# ===================================================================================================  

    def set_interaction_abaqus(self):
        """Setzt die Interaktion auf 'Steuerung Abaqus'."""
        # Hier definierst du, wie die Mausinteraktion für Abaqus funktioniert
        self.widget.set_interaction("abaqus")
        self.statusBar().showMessage("Interaktion: Steuerung Abaqus")

# ===================================================================================================  

    def set_interaction_creo(self):
        """Setzt die Interaktion auf 'Steuerung Creo'."""
        # Hier definierst du, wie die Mausinteraktion für Creo funktioniert
        self.widget.set_interaction("creo")
        self.statusBar().showMessage("Interaktion: Steuerung Creo")

# ===================================================================================================  

    def add_structure_tree(self):
        """Fügt die Strukturbaumknoten und Unterpunkte basierend auf den geladenen Modellobjekten hinzu."""
        if not self.myModel:
            return

        self.treeModel.clear() # Entferne alle aktuellen Knoten im Baum (leere den Baum)

        self.treeModel.setHorizontalHeaderLabels(['Strukturbaum'])  # Setze die Header

        mbs_objects = self.myModel.get_mbs_object_list()  # Zugriff auf die Objektliste

        # Kategorien für die verschiedenen Objektarten
        bodies_item = QStandardItem('Bodys')
        constraints_item = QStandardItem('Constraints')
        forces_item = QStandardItem('Forces')
        measures_item = QStandardItem('Measures')

        # Füge die Knoten aus dem Modell in die entsprechenden Kategorien ein.
        for obj in mbs_objects:
            # Name des Objekts extrahieren
            object_name = obj.parameter.get('name', {}).get('value', 'Unbenannt')  # Standardname: Unbenannt

            # Überprüfe den Typ jedes Objekts und füge es der entsprechenden Kategorie hinzu
            if obj.getType() == "Body":
                body_item = QStandardItem(f"{object_name}")
                bodies_item.appendRow(body_item)
            elif obj.getType() == "Constraint":
                constraint_item = QStandardItem(f"{object_name}")
                constraints_item.appendRow(constraint_item)
            elif obj.getType() == "Force":
                force_item = QStandardItem(f"{object_name}")
                forces_item.appendRow(force_item)
            elif obj.getType() == "Measure":
                measure_item = QStandardItem(f"{object_name}")
                measures_item.appendRow(measure_item)

        # Füge alle Kategorien zum Baum hinzu.
        self.treeModel.appendRow(bodies_item)
        self.treeModel.appendRow(constraints_item)
        self.treeModel.appendRow(forces_item)
        self.treeModel.appendRow(measures_item)

# ===================================================================================================  

    def show_context_menu(self, pos):
        """Zeigt das Kontextmenü für den Strukturbaum an."""
        index = self.treeView.indexAt(pos)  # Hole den Baumknoten unter der Maus
        if not index.isValid():  # Wenn der Knoten ungültig ist, tue nichts
            return

        menu = QMenu(self.treeView)  # Erstelle das Kontextmenü
        rename_action = QAction("Umbennen", self)  # Aktion zum Umbennen
        properties_action = QAction("Eigenschaften", self)  # Aktion zum Anzeigen der Eigenschaften
        display_action = QAction("Anzeigen", self)  # Aktion zum  hervorheben des Körpers

        # Verknüpfe die Aktionen mit den Methoden
        rename_action.triggered.connect(lambda: self.rename_object(index))
        properties_action.triggered.connect(lambda: self.show_properties(index))
        #display_action.triggered.connect(lambda: self.highlight_body(index))

        # Füge die Aktionen zum Menü hinzu
        menu.addAction(rename_action)
        menu.addAction(properties_action)
        menu.addAction(display_action)
        
        # Zeige das Menü an der Position des Rechtsklicks
        menu.exec_(self.treeView.mapToGlobal(pos))
# ===================================================================================================  

    def rename_object(self, index):
        """Ermöglicht das Umbennen des Objekts."""
        current_name = index.data()  # Der aktuelle Name des Objekts
        new_name, ok = QInputDialog.getText(self, "Umbennen", "Neuer Name:", text=current_name)

        if ok and new_name:
            # Hole das Objekt aus dem Modell und setze den neuen Namen
            obj = self.get_object_from_index(index)
            obj.parameter['name']['value'] = new_name  # Aktualisiere den Namen des Objekts im Modell

            # Hole das Modell, das mit dem Baum verbunden ist
            item = self.treeModel.itemFromIndex(index)  # Hole das TreeView-Item für den ausgewählten Knoten

            # Setze den neuen Namen im Strukturbaum
            item.setText(new_name)

            # Sende ein Signal, dass sich der Dateninhalt geändert hat
            self.treeModel.dataChanged.emit(index, index)  # Signal an den Baum, dass sich die Daten geändert haben

# ===================================================================================================  

    def show_properties(self, index):
        """Zeigt die Eigenschaften des Objekts an."""
        obj = self.get_object_from_index(index)
        
        if obj is None:
            return
        
        obj_type = obj.getType()  # Den Typ des Objekts ermitteln
        obj_subtype = obj.getSubType() # Den Subtype wird bestimmt 
        
        if obj_type == "Body":
            # Für "Body"-Objekte zeige den Schwerpunkt und Position an
            position = obj.parameter.get('position', {}).get('value', 'Nicht gesetzt')
            mass = obj.parameter.get('mass', {}).get('value', 'Nicht gesetzt')

            properties_message = f"Position: {position}\nMasse: {mass}" 
            QMessageBox.information(self, "Eigenschaften", properties_message)  # Zeige die Eigenschaften in einer MessageBox an

        elif obj_type == "Constraint":
            # Für "Constraint"-Objekte zeige nur die Position an
            position = obj.parameter.get('position', {}).get('value', 'Nicht gesetzt')
            properties_message = f"Position: {position}"
            QMessageBox.information(self, "Eigenschaften", properties_message)

        elif obj_type == "Force":
            # Für "Force"-Objekte zeige die Kraft und Position an
            if obj_subtype == "GenericForce":
                point1 = obj.parameter.get('PointOfApplication_Body1', {}).get('value', 'Nicht gesetzt')
                point2 = obj.parameter.get('PointOfApplication_Body2', {}).get('value', 'Nicht gesetzt')
                force = obj.parameter.get('ForceExpression', {}).get('value', 'Nicht gesetzt')
                properties_message = (
                    f"PointOfApplication_Body1: {point1}\n" 
                    f"PointOfApplication_Body2: {point2}\n"
                    f"force: {force}\n")
                QMessageBox.information(self, "Eigenschaften", properties_message)

            elif obj_subtype == "GenericTorque":
                body1 = obj.parameter.get('body1', {}).get('value', 'Nicht gesetzt')
                body2 = obj.parameter.get('body2', {}).get('value', 'Nicht gesetzt')
                direction = obj.parameter.get('direction', {}).get('value', 'Nicht gesetzt')
                Torque = obj.parameter.get('TorqueExpression', {}).get('value', 'Nicht gesetzt')
                properties_message = (
                    f"Body 1: {body1}\n"
                    f"Body 2: {body2}\n"
                    f"Direction: {direction}\n"
                    f"Torque Expression: {Torque}")
                QMessageBox.information(self, "Eigenschaften", properties_message)

        elif obj_type == "Measure":
            # Für "Measure"-Objekte zeige die gemessene Größe an
            measure_value = obj.parameter.get('value', {}).get('value', 'Nicht gesetzt')
            properties_message = f"Messwert: {measure_value}"
            QMessageBox.information(self, "Eigenschaften", properties_message)

        else:
            # Falls der Typ nicht erkannt wird, zeige eine allgemeine Nachricht an
            properties_message = "Keine spezifischen Eigenschaften verfügbar."
            QMessageBox.information(self, "Eigenschaften", properties_message)

# ===================================================================================================  

    def get_object_from_index(self, index):
        """Holt das Modellobjekt basierend auf dem Index."""
        # Der Baumindex entspricht einer Zeile in der Modell-Datenstruktur
        if not index.isValid():
            return None
        
        # Das Objekt im Modell (z. B. Body, Constraint, etc.) wird hier aus der Baumstruktur abgerufen.
        item = self.treeModel.itemFromIndex(index)  # Hole das TreeView-Item für den ausgewählten Knoten
        object_name = item.text()  # Holen den Namen des Objekts aus dem Baum (diese ist notwendig für das Objekt)
        
        # Gehe durch die Objektliste und finde das passende Objekt
        for obj in self.myModel.get_mbs_object_list():
            if obj.parameter.get('name', {}).get('value', '') == object_name:
                return obj  # Gib das Objekt zurück, wenn der Name übereinstimmt
        
        return None
# ====================================================================================================

