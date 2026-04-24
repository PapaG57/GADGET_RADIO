try:
    from pyvda import AppView
    HAS_PYVDA = True
except ImportError:
    HAS_PYVDA = False

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

# Chemin vers ton index.html
html_path = get_resource_path(os.path.join('MaRadioPerso.gadget', 'index.html'))
# On ajoute un paramètre unique pour éviter le cache
html_path_with_cache_breaker = f"file:///{html_path.replace(os.sep, '/')}?v=1.1"

def setup_gadget(window):
    """ Configuration avancée au démarrage de la fenêtre """
    if not HAS_PYVDA:
        print("Note: pyvda non installé. L'épinglage sur tous les bureaux est désactivé.")
        return

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
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")
            return False

    def load_settings(self):
        """ Charge les réglages depuis settings.json """
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")
        return None

    def close_app(self):
        if self.window:
            self.window.destroy()

def start_app():
    # Définir un dossier de stockage pour le cache WebView2
    # On le place dans APPDATA pour éviter les conflits et faciliter le nettoyage
    user_data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'RadioStarGadget_Cache')
    
    # Suppression du cache au démarrage pour forcer la mise à jour des fichiers (en mode dev)
    if not getattr(sys, 'frozen', False):
        import shutil
        try:
            if os.path.exists(user_data_dir):
                shutil.rmtree(user_data_dir)
        except Exception as e:
            print(f"Note: Impossible de vider tout le cache : {e}")

    api = Api()
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
    # On force l'utilisation de 'qt' (PyQt6) pour éviter pythonnet qui échoue sur Python 3.14
    webview.start(setup_gadget, window, storage_path=user_data_dir, gui='qt')

if __name__ == '__main__':
    start_app()
