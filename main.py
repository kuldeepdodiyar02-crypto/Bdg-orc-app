
# BDG OCR + Prediction Kivy App with in-app OCR.space API key input
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import mainthread
from kivy.storage.jsonstore import JsonStore
import base64, json, os
import requests

KV = """
ScreenManager:
    id: sm
    MenuScreen:
        name: 'menu'
    MainScreen:
        name: 'main'

<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(12)
        spacing: dp(10)
        Label:
            text: '🔒 Enter OCR.space API Key'
            size_hint_y: None
            height: dp(36)
        TextInput:
            id: api_input
            hint_text: 'Paste your OCR.space API key here'
            multiline: False
            size_hint_y: None
            height: dp(48)
        BoxLayout:
            size_hint_y: None
            height: dp(44)
            spacing: dp(8)
            Button:
                text: 'Save Key'
                on_release: root.save_key(api_input.text)
            Button:
                text: 'Skip (Use without OCR)'
                on_release: root.skip_key()
        Label:
            id: stored_label
            text: ''
            size_hint_y: None
            height: dp(28)
        Widget:

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(8)

        BoxLayout:
            size_hint_y: None
            height: dp(48)
            spacing: dp(8)
            Button:
                text: "Select Screenshot"
                on_release: root.select_image()
            Button:
                text: "Predict Next"
                on_release: root.predict_next()

        Image:
            id: img_view
            size_hint_y: .6
            allow_stretch: True
            keep_ratio: True

        Label:
            id: detected_label
            text: "Detected: -"
            size_hint_y: None
            height: dp(36)
        Label:
            id: pred_label
            text: "Prediction: -"
            size_hint_y: None
            height: dp(36)
        BoxLayout:
            size_hint_y: None
            height: dp(48)
            spacing: dp(8)
            Button:
                text: "Add R"
                on_release: root.add_color('R')
            Button:
                text: "Add G"
                on_release: root.add_color('G')
            Button:
                text: "Add V"
                on_release: root.add_color('V')
            Button:
                text: "Settings"
                on_release: root.open_settings()
        Label:
            id: stats_label
            text: "Wins: 0  Losses: 0"
            size_hint_y: None
            height: dp(28)

<SettingsPopup@BoxLayout>:
    orientation: 'vertical'
    spacing: dp(8)
    padding: dp(8)
    Label:
        text: 'Settings'
    Button:
        text: 'Clear Saved API Key'
        on_release: app.clear_api_key()
    Button:
        text: 'Close'
        on_release: root.parent.dismiss()
"""

class MenuScreen(Screen):
    def on_enter(self):
        store = self.manager.app.store
        key = store.get('ocr').get('key') if store.exists('ocr') else None
        if key:
            self.ids.stored_label.text = 'Stored key: (saved)'
        else:
            self.ids.stored_label.text = 'No API key saved.'

    def save_key(self, key_text):
        key_text = key_text.strip()
        if not key_text:
            self.ids.stored_label.text = 'Enter a valid key.'
            return
        store = self.manager.app.store
        store.put('ocr', key=key_text)
        self.ids.stored_label.text = 'Key saved locally.'
        # switch to main
        self.manager.current = 'main'

    def skip_key(self):
        # allow using app without OCR: switch to main screen
        self.manager.current = 'main'

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history = []
        self.last_pred = None
        self.wins = 0
        self.losses = 0
        self.store = None

    def on_enter(self):
        self.store = self.manager.app.store

    def select_image(self):
        from plyer import filechooser
        filechooser.open_file(on_selection=self._on_selected)

    @mainthread
    def _on_selected(self, selection):
        if not selection:
            return
        path = selection[0]
        self.ids.img_view.source = path
        self.detect_from_image(path)

    def detect_from_image(self, path):
        # Read file and send to OCR.space if key available, else try basic filename heuristics
        try:
            key = None
            if self.store and self.store.exists('ocr'):
                key = self.store.get('ocr').get('key')
            parsed = None
            if key:
                with open(path, 'rb') as f:
                    b = f.read()
                payload = {'isOverlayRequired': False, 'apikey': key, 'language': 'eng'}
                files = {'file': ('screenshot.png', b)}
                r = requests.post('https://api.ocr.space/parse/image', data=payload, files=files, timeout=30)
                data = r.json()
                if data.get('IsErroredOnProcessing'):
                    self.ids.detected_label.text = 'OCR Error: ' + str(data.get('ErrorMessage', [''])[0])
                    return
                parsed_text = ''
                for p in data.get('ParsedResults', []):
                    parsed_text += p.get('ParsedText', '') + '\n'
                parsed_text = parsed_text.strip()
                t = parsed_text.lower()
                if 'red' in t or '\nr' in t or t.strip() == 'r':
                    parsed = 'R'
                elif 'green' in t or '\ng' in t or t.strip() == 'g':
                    parsed = 'G'
                elif 'violet' in t or 'vio' in t or '\nv' in t or t.strip() == 'v':
                    parsed = 'V'
                else:
                    for ln in parsed_text.splitlines()[::-1]:
                        ln = ln.strip()
                        if ln in ('r','g','v'):
                            parsed = ln.upper(); break
            else:
                # no key: attempt filename-based guess (e.g., 'red' in filename)
                fname = os.path.basename(path).lower()
                if 'red' in fname: parsed = 'R'
                elif 'green' in fname: parsed = 'G'
                elif 'violet' in fname or 'vio' in fname or 'purple' in fname: parsed = 'V'

            if parsed:
                self.ids.detected_label.text = f"Detected: {parsed} (from OCR)"
                self.history.append(parsed)
            else:
                self.ids.detected_label.text = 'Detected: - (no match)'
        except Exception as e:
            self.ids.detected_label.text = f'OCR failed: {e}'

    def add_color(self, c):
        self.history.append(c)
        self.ids.detected_label.text = f'Added: {c}'

    def predict_next(self):
        if len(self.history) < 3:
            import random
            p = random.choice(['R','G','V'])
            conf = 33.3
        else:
            last3 = self.history[-3:]
            if last3[0]==last3[1]==last3[2]:
                opts = [x for x in ['R','G','V'] if x!=last3[0]]
                import random; p = random.choice(opts); conf = 60.0
            else:
                counts = {c:self.history.count(c) for c in ['R','G','V']}
                min_c = min(counts, key=counts.get)
                total = sum(counts.values()) or 1
                conf = max(35, round((1 - counts[min_c]/total)*100,1))
                p = min_c
        self.last_pred = p
        self.ids.pred_label.text = f"Prediction: {p}  ({conf}%)"

    def open_settings(self):
        from kivy.uix.popup import Popup
        content = Builder.load_string('''
BoxLayout:
    orientation: 'vertical'
    padding: dp(8)
    spacing: dp(8)
    Button:
        text: 'Clear Saved API Key'
        on_release: app.clear_api_key(); root.parent.dismiss()
    Button:
        text: 'Close'
        on_release: root.parent.dismiss()
        ''')
        popup = Popup(title='Settings', content=content, size_hint=(.8,.4))
        popup.open()

class BDGApp(App):
    def build(self):
        self.store = JsonStore(self.user_data_dir + '/bdg_store.json')
        Builder.load_string(KV)
        sm = ScreenManager(transition=NoTransition())
        sm.app = self
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(MainScreen(name='main'))
        # start on menu unless key exists
        if self.store.exists('ocr') and self.store.get('ocr').get('key'):
            sm.current = 'main'
        else:
            sm.current = 'menu'
        return sm

    def clear_api_key(self):
        if self.store.exists('ocr'):
            self.store.delete('ocr')
        # restart to menu
        from kivy.base import EventLoop
        EventLoop.close()
        BDGApp().run()

if __name__ == '__main__':
    BDGApp().run()
