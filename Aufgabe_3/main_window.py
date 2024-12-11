# Importiere das mbsModel-Modul
import mbsModel
# Importiere Path, um mit Dateipfaden zu arbeiten
from pathlib import Path
# Importiere wichtige Klassen aus PySide6 (GUI-Komponenten)
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QFileDialog, QStatusBar, QMessageBox,QMenu
from PySide6.QtCore import Qt
# Importiere das MainWidget für das Rendering
from main_widget import MainWidget
# Importiere den Renderer aus VTK
from vtkmodules.vtkRenderingCore import vtkRenderer
# Importiere QVTKRenderWindowInteractor für die Interaktion mit dem VTK-Renderfenster
import QVTKRenderWindowInteractor as QVTK
import vtk

QVTKRenderWindowInteractor = QVTK.QVTKRenderWindowInteractor  # Alias für das QVTKRenderWindowInteractor-Modul

class MainWindow(QMainWindow):
    def __init__(self):
        """Initialisiert das Hauptfenster der Anwendung."""
        super().__init__()

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

        # Setze das Widget als zentrales Widget des Fensters
        self.setCentralWidget(self.widget)

        # Initialisiere das RenderWindow, um den Hintergrund anzuzeigen
        self.widget.GetRenderWindow().Render()  # Rendere das Fenster, um den schwarzen Hintergrund zu sehen

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


    def create_status_bar(self):
        """Erstellt die Statusleiste und zeigt eine Nachricht an."""
        self.statusBar().showMessage("Kein Modell geladen")

    def load_model(self):
        """Lädt ein Modell aus einer JSON-Datei."""
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Open json File", "", "JSON and FDD Files (*.json *.fdd)", options=options) # Filter gleich nach fdd und json datein
        
        if filename:
            if filename.lower().endswith(".json"):  # Überprüfe, ob die Datei eine JSON-Datei ist
                self.load_json_model(filename)
            else:
                self.show_error_message("Ungültige Datei", "Bitte wählen Sie eine gültige JSON-Datei aus.")
        else:
            self.statusBar().showMessage("Modell-Laden abgebrochen")

    def load_json_model(self, filename):
        """Lädt das Modell aus einer JSON-Datei und zeigt es im VTK-Renderer."""
        try:
            self.myModel = mbsModel.mbsModel()  # Erstelle ein neues Modell
            self.myModel.loadDatabase(Path(filename))  # Lade das Modell aus der JSON-Datei
            self.statusBar().showMessage(f"Modell geladen: {filename}")
            self.widget.update_renderer(self.myModel)  # Aktualisiere das Rendering mit dem neuen Modell
        except Exception as e:
            self.statusBar().showMessage(f"Fehler beim Laden des Modells: {e}")

    def save_model(self):
        """Speichert das Modell in einer JSON-Datei."""
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Save Model File", "", "JSON Files (*.json)", options=options)
        if filename:
            self.myModel.saveDatabase(Path(filename))  # Speichert das Modell
            self.statusBar().showMessage(f"Modell gespeichert: {filename}")

    def import_fdd(self):
        """Importiert ein FDD-Modell aus einer Datei."""
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Import FDD File", "", "JSON and FDD Files (*.json *.fdd)", options=options) # Filter gleich nach fdd und json datein

        if filename:
            if filename.lower().endswith(".fdd"):  # Überprüfe, ob die Datei eine Fdd-Datei ist
                self.import_fdd_file(Path(filename))
            else:
                self.show_error_message("Ungültige Datei", "Bitte wählen Sie eine gültige Fdd-Datei aus.")
        else:
            self.statusBar().showMessage("Modell-Laden abgebrochen")

    def import_fdd_file(self, filename):
        """Lädt das Modell aus einer FDD-Datei."""
        try:
            self.myModel = mbsModel.mbsModel()
            self.myModel.importFddFile(filename)
            self.statusBar().showMessage(f"FDD-Datei importiert: {filename}")
            self.widget.update_renderer(self.myModel)
        except Exception as e:
            self.statusBar().showMessage(f"Fehler beim Importieren der FDD-Datei: {e}")

    def show_error_message(self, title, message):
        """Zeigt eine Fehlermeldung an."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def set_front_view(self):
        """Setzt die Kamera in die Frontansicht."""
        camera = self.widget.renderer.GetActiveCamera()  # Aktive Kamera holen
        camera.SetPosition(0, 1, 0)  # Setze die Kamera über das Modell
        camera.SetFocalPoint(0, 0, 0)  # Fokus auf den Ursprung
        camera.SetViewUp(0, 0, 1)  # Oben ist die Z-Achse
        self.widget.renderer.ResetCamera()  # Stellt sicher, dass das gesamte Modell sichtbar ist
        self.widget.GetRenderWindow().Render()  # Szene neu rendern

    def set_top_view(self):
        """Setzt die Kamera in die Draufsicht."""
        camera = self.widget.renderer.GetActiveCamera()  # Aktive Kamera holen
        camera.SetPosition(0, 0, 1)  # Setze die Kamera über das Modell
        camera.SetFocalPoint(0, 0, 0)  # Fokus auf den Ursprung
        camera.SetViewUp(0, 1, 0)  # Oben ist die Y-Achse
        self.widget.renderer.ResetCamera()  # Stellt sicher, dass das gesamte Modell sichtbar ist
        self.widget.GetRenderWindow().Render()  # Szene neu rendern

    def set_rigth_view(self):
        """Setzt die Kamera in die Draufsicht."""
        camera = self.widget.renderer.GetActiveCamera()  # Aktive Kamera holen
        camera.SetPosition(1, 0, 0)  # Setze die Kamera über das Modell
        camera.SetFocalPoint(0, 0, 0)  # Fokus auf den Ursprung
        camera.SetViewUp(0, 0, 1)  # Oben ist die Y-Achse
        self.widget.renderer.ResetCamera()  # Stellt sicher, dass das gesamte Modell sichtbar ist
        self.widget.GetRenderWindow().Render()  # Szene neu rendern

    def open_control_settings(self):
        """Öffnet die Steuerungseinstellungen und stellt die Interaktion wie in Creo ein."""
        # Diese Methode aktiviert eine benutzerdefinierte Steuerung wie in Creo
        self.set_creo_mouse_interaction()

    def set_creo_mouse_interaction(self):
        """Aktiviert die Creo-ähnliche Mausinteraktion."""
        # In Creo wird normalerweise folgendermaßen interagiert:
        # - Linksklick: Drehung der Ansicht
        # - Rechtsklick: Zoom
        # - Mittlere Maustaste oder Shift + Mausklick: Pan
        
        # Setze den Interactor auf eine benutzerdefinierte Steuerung (falls nötig)
        self.widget.SetInteractorStyle(self.create_creo_interaction_style())

    def create_creo_interaction_style(self):
        """Erstellt eine benutzerdefinierte Interaktionsweise wie in Creo."""
        # Hier könntest du mit VTKs "vtkInteractorStyle" arbeiten, um eine benutzerdefinierte Steuerung zu definieren
        # VTK bietet mehrere Interaktionsstile, die du überschreiben kannst, wie z.B. vtkInteractorStyleTrackballCamera,
        # das das Drehen und Zoomen eines Modells ermöglicht.
        interactor_style = vtk.vtkInteractorStyleTrackballCamera()

        # Stelle sicher, dass der Interactor die Maus so behandelt, wie in Creo:
        interactor_style.SetMouseWheelMotionFactor(0.1)  # Geschwindigkeit des Zoomens
        return interactor_style
    
    def set_interaction_abaqus(self):
        """Setzt die Interaktion auf 'Steuerung Abaqus'."""
        # Hier definierst du, wie die Mausinteraktion für Abaqus funktioniert
        self.widget.set_interaction("abaqus")
        self.statusBar().showMessage("Interaktion: Steuerung Abaqus")

    def set_interaction_creo(self):
        """Setzt die Interaktion auf 'Steuerung Creo'."""
        # Hier definierst du, wie die Mausinteraktion für Creo funktioniert
        self.widget.set_interaction("creo")
        self.statusBar().showMessage("Interaktion: Steuerung Creo")
