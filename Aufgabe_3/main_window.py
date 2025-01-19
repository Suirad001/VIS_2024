# Importiere das mbsModel-Modul
import mbsModel
# Importiere Path, um mit Dateipfaden zu arbeiten
from pathlib import Path
# Importiere wichtige Klassen aus PySide6 (GUI-Komponenten)
from PySide6.QtGui import QAction, QKeySequence, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QMainWindow, QFileDialog, QStatusBar, QMessageBox, QMenu, QTreeView, QWidget, QHBoxLayout, QSplitter, QInputDialog
from PySide6.QtCore import Qt, QRect
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
        super().__init__() # Ruft den Konstruktor der Elternklasse auf

        # Initialisiere das Modell
        self.myModel = None  # Anfangs kein Modell geladen

        # Hauptfenster konfigurieren
        self.setWindowTitle("3D Modell in Qt mit VTK")  # Setze den Titel des Fensters
        self.setGeometry(100, 100, 800, 600)  # Setze die Fenstergröße und Position
        
        # Menüleiste erstellen
        self.create_menu()

        # Statusleiste erstellen
        self.create_status_bar()

        # VTK-Widget und -Renderer initialisieren
        self.widget = MainWidget(self)  # Erstelle ein VTK-Widget
        
        # Setze den Hintergrund des Renderers auf Schwarz
        self.widget.renderer.SetBackground(0.0, 0.0, 0.0)  # Hintergrund für den Renderer auf Schwarz

        # Layout für das Hauptfenster erstellen
        main_layout = QHBoxLayout()

        # QSplitter erstellen, um den Stammbaum und das VTK-Widget zu trennen
        self.splitter = QSplitter(Qt.Horizontal)

        # Erstelle und füge den Stammbaum hinzu
        self.treeView = QTreeView(self)  # Erstelle das QTreeView-Widget
        self.treeModel = QStandardItemModel()
        self.treeModel.setHorizontalHeaderLabels(['Strukturbaum'])  # Setze die Header
        self.treeView.setModel(self.treeModel)  # Setze das Modell für den Baum

        # Füge das Kontextmenü für den Strukturbaum hinzu
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)  # Aktiviere Kontextmenü
        self.treeView.customContextMenuRequested.connect(self.show_context_menu)  # Verknüpfe mit der Methode

        # Füge die Strukturbaumdaten hinzu (dies muss nach dem Laden des Modells geschehen)
        self.add_structure_tree()

        # **Setze eine Startbreite von 100 Pixel für den Baum**
        self.initial_tree_width = 100  # Startbreite für den Baum
        
        self.treeView.setMinimumWidth(80)  # Mindestbreite setzen
        self.treeView.setMaximumWidth(600)  # Maximale Breite für den Baum (optional, anpassbar)

        # Füge das TreeView und das VTK-Widget zum Splitter hinzu
        self.splitter.addWidget(self.treeView)
        self.splitter.addWidget(self.widget)

        # Setze den Splitter so, dass der Baum eine Startbreite von 200 Pixel hat
        self.splitter.setSizes([self.initial_tree_width, self.width() - self.initial_tree_width])

        # Füge den Splitter zum Layout hinzu
        main_layout.addWidget(self.splitter)

        # Container erstellen und das Layout setzen
        container = QWidget(self)
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Fenster anzeigen
        self.setGeometry(100, 100, 1000, 600)
        self.show()

        # Initialisiere das RenderWindow
        self.widget.GetRenderWindow().Render()

# ===================================================================================================    
 #Erstellen der Menübar und Befüllen 

    def create_menu(self):
        """Erstellt die Menüleiste und ihre Aktionen."""
        menubar = self.menuBar()
        
        # Menü unterpunkt File hinzugefügt
        file_menu = menubar.addMenu('File')
        
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

        # Menü Unterpunkt view hinzugefügt
        view_menu = menubar.addMenu('view')

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

        # Menü unterpunkt Einstellungen hinzugefügt
        settings_menu = menubar.addMenu('Einstellungen')

        # Steuerung Untermenü hinzufügen
        steuerung_menu = QMenu("Steuerung", self)

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

    def create_status_bar(self):
        """Erstellt die Statusleiste und zeigt eine Nachricht an."""
        self.statusBar().showMessage("Kein Modell geladen")

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
    """Funktionen für die Unterpunkte von view""" 

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

    def open_control_settings(self):
        """Öffnet die Steuerungseinstellungen und stellt die Interaktion wie in Creo ein."""
        # Diese Methode aktiviert eine benutzerdefinierte Steuerung wie in Creo
        self.set_creo_mouse_interaction()

# ===================================================================================================  

    def set_creo_mouse_interaction(self):
        """Aktiviert die Creo-ähnliche Mausinteraktion."""
        # In Creo wird normalerweise folgendermaßen interagiert:
        # - Linksklick: Drehung der Ansicht
        # - Rechtsklick: Zoom
        # - Mittlere Maustaste oder Shift + Mausklick: Pan
        
        # Setze den Interactor auf eine benutzerdefinierte Steuerung (falls nötig)
        self.widget.SetInteractorStyle(self.create_creo_interaction_style())

# ===================================================================================================  

    def create_creo_interaction_style(self):
        """Erstellt eine benutzerdefinierte Interaktionsweise wie in Creo."""
        # Hier könntest du mit VTKs "vtkInteractorStyle" arbeiten, um eine benutzerdefinierte Steuerung zu definieren
        # VTK bietet mehrere Interaktionsstile, die du überschreiben kannst, wie z.B. vtkInteractorStyleTrackballCamera,
        # das das Drehen und Zoomen eines Modells ermöglicht.
        interactor_style = vtk.vtkInteractorStyleTrackballCamera()

        # Stelle sicher, dass der Interactor die Maus so behandelt, wie in Creo:
        interactor_style.SetMouseWheelMotionFactor(0.1)  # Geschwindigkeit des Zoomens
        return interactor_style

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

        # Verknüpfe die Aktionen mit den Methoden
        rename_action.triggered.connect(lambda: self.rename_object(index))
        properties_action.triggered.connect(lambda: self.show_properties(index))

        # Füge die Aktionen zum Menü hinzu
        menu.addAction(rename_action)
        menu.addAction(properties_action)
        
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

            # Aktualisiere den Baum mit dem neuen Namen
            index.model().dataChanged.emit(index, index)  # Signal, dass sich der Name geändert hat

# ===================================================================================================  

    def show_properties(self, index):
        """Zeigt die Eigenschaften des Objekts an."""

        mbs_objects = self.myModel.get_mbs_object_list()  # Zugriff auf die Objektliste

        obj = self.get_object_from_index(index)
        
        # Eigenschaften des Objekts abrufen (z.B. Position und Masse)
        position = obj.parameter.get('position', {}).get('value', 'Nicht gesetzt')
        mass = obj.parameter.get('mass', {}).get('value', 'Nicht gesetzt')

        # Erstelle die Nachricht, die die Eigenschaften anzeigt
        properties_message = f"Position: {position}\nMasse: {mass}"

        # Zeige die Eigenschaften in einer MessageBox
        QMessageBox.information(self, "Eigenschaften", properties_message)

# ===================================================================================================  

    def get_object_from_index(self, index):
        """Holt das Modellobjekt basierend auf dem Index."""
        # Wir gehen davon aus, dass jedes Baumobjekt eine Referenz auf das Modellobjekt enthält.
        # Hier musst du den Index auf das tatsächliche Modellobjekt übersetzen.
        # In diesem Fall gehe ich davon aus, dass du eine Methode wie 'get_mbs_object_list' hast.
        return self.myModel.get_mbs_object_list()[index.row()]
