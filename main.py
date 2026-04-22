from pyvda import AppView
import webview
import os
import sys
import json

def get_resource_path(relative_path):
    """ Pour que le .exe retrouve le fichier HTML une fois compilé """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Chemin vers ton index.html (on cherche dans le dossier du projet)
html_path = get_resource_path(os.path.join('MaRadioPerso.gadget', 'index.html'))

def setup_gadget(window):
    """ Configuration avancée au démarrage de la fenêtre """
    try:
        # Récupère l'identifiant (HWND) de la fenêtre Windows
        hwnd = int(window.native.Handle)
        # Épingle la fenêtre sur tous les bureaux virtuels
        AppView(hwnd).pin()
    except Exception as e:
        print(f"Erreur lors de l'épinglage : {e}")

class Api:
    def __init__(self):
        self.window = None
        # Déterminer le dossier de l'application (même si compilé en .exe)
        if getattr(sys, 'frozen', False):
            self.app_dir = os.path.dirname(sys.executable)
        else:
            self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.settings_path = os.path.join(self.app_dir, 'settings.json')

    def save_settings(self, settings):
        """ Sauvegarde les réglages dans settings.json """
        try:
            import json
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")
            return False

    def load_settings(self):
        """ Charge les réglages depuis settings.json """
        try:
            import json
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")
        return None

    def close_app(self):
        if self.window:
            self.window.destroy()

def start_app():
    # Définir un dossier de stockage persistant dans APPDATA pour conserver les réglages
    storage_path = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'RadioStarGadget')
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)

    api = Api()
    # frameless=True : Pas de bordures
    # easy_drag=True : Déplaçable au clic
    # on_top=False : Pas toujours au-dessus (plus discret)
    window = webview.create_window(
        'Radio Star', 
        html_path, 
        width=260, 
        height=400, 
        frameless=True, 
        easy_drag=True, 
        on_top=False,
        transparent=True,
        js_api=api
    )
    api.window = window
    # On lance setup_gadget une fois que la fenêtre est créée, avec le chemin de stockage
    webview.start(setup_gadget, window, storage_path=storage_path)

if __name__ == '__main__':
    start_app()
