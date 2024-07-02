import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.simpledialog import askstring
from PIL import Image, ImageTk
import subprocess
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable for language
lang = {}

# 1. execute_command: Executes a shell command and displays the result
def execute_command(command):
    logging.debug(f"Executing command: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            logging.info(f"Command succeeded: {command}")
            messagebox.showinfo("Success", f"Command succeeded: {command}")
        else:
            logging.error(f"Command failed: {command}\n{result.stderr}")
            messagebox.showerror("Error", f"Command failed: {command}\n{result.stderr}")
    except Exception as e:
        logging.error(f"Command execution error: {str(e)}")
        messagebox.showerror("Error", f"Command execution error: {str(e)}")

# 2. load_language: Loads language translations from a JSON file
def load_language(language_code):
    global lang
    file_path = os.path.join('language', f'gui_{language_code}.json')
    logging.debug(f"Loading language: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lang = json.load(file)
    except Exception as e:
        logging.error(f"Failed to load language file: {file_path} - {str(e)}")
        messagebox.showerror("Error", f"Failed to load language file: {str(e)}")

# 3. update_language: Updates the interface language
def update_language():
    logging.debug("Updating interface with selected language")
    try:
        app.notebook.tab(0, text=lang['produzione_srt'])
        app.notebook.tab(1, text=lang['test_srt'])
        app.notebook.tab(2, text=lang['translitterazione'])
        app.notebook.tab(3, text=lang['produzione_json'])
        app.notebook.tab(4, text=lang['setup_lingua'])
        
        app.label_video_locale.config(text=lang['carica_video_locale'])
        app.label_video_url.config(text=lang['url_video'])
        app.audio_only_button.config(text=lang['scarica_solo_audio'])
        app.label_language.config(text=lang['lingua'])
        app.save_srt_button.config(text=lang['salva_srt'])
        app.run_produzione_srt_button.config(text=lang['lancia_procedura'])
        app.label_output_srt_file.config(text=lang['output_srt_file'])

        app.label_test_video.config(text=lang['file_video'])
        app.label_test_srt.config(text=lang['file_srt'])
        app.play_video_button.config(text=lang['play_video'])

        app.label_sorgenti.config(text=lang['sorgenti'])
        app.add_source_button.config(text=lang['aggiungi_sorgente'])
        app.remove_source_button.config(text=lang['rimuovi_sorgente'])
        app.label_dest_txt.config(text=lang['destinazione_txt'])
        app.browse_dest_txt_button.config(text=lang['sfoglia'])
        app.run_translitterazione_button.config(text=lang['esegui_traslitterazione'])

        app.label_parole_chiave.config(text=lang['parole_chiave'])
        app.add_keyword_button.config(text=lang['aggiungi_parola_chiave'])
        app.remove_keyword_button.config(text=lang['rimuovi_parola_chiave'])
        app.label_dest_json.config(text=lang['destinazione_json'])
        app.browse_dest_json_button.config(text=lang['sfoglia'])
        app.run_produzione_json_button.config(text=lang['esegui_produzione_json'])

        app.label_local_dirs.config(text=lang['directory_locali'])
        app.add_local_directory_button.config(text=lang['aggiungi_directory'])
        app.remove_local_directory_button.config(text=lang['rimuovi_directory'])
        app.label_cloud_sources.config(text=lang['sorgenti_cloud'])
        app.label_ignore_dirs.config(text=lang['directory_da_ignorare'])
        app.add_ignore_directory_button.config(text=lang['aggiungi_directory'])
        app.remove_ignore_directory_button.config(text=lang['rimuovi_directory'])
        app.search_subdirs_button.config(text=lang['cerca_nelle_sottodirectory'])
        app.label_search_limits.config(text=lang['limiti_di_ricerca'])
        app.save_config_button.config(text=lang['salva_configurazione'])
        app.load_config_button.config(text=lang['carica_configurazione'])
        
    except KeyError as e:
        logging.error(f"Missing language key: {str(e)}")
        messagebox.showerror("Error", f"Missing language key: {str(e)}")

# 4. save_configuration: Saves the configuration to a JSON file
def save_configuration(config, file_path):
    logging.debug(f"Saving configuration: {file_path}")
    try:
        with open(file_path, 'w', encoding='utf-8') as config_file:
            json.dump(config, config_file, indent=4)
        logging.info(f"Configuration saved successfully: {file_path}")
        messagebox.showinfo("Success", lang.get('configurazione_salvata', "Configurazione salvata."))
    except Exception as e:
        logging.error(f"Failed to save configuration: {str(e)}")
        messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

# 5. load_configuration: Loads the configuration from a JSON file
def load_configuration(file_path):
    logging.debug(f"Loading configuration: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
            logging.info(f"Configuration loaded successfully: {file_path}")
            return config
    except Exception as e:
        logging.error(f"Failed to load configuration: {str(e)}")
        messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
        return {}

# 6. GaloraGUI: Main GUI class
class GaloraGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        logging.debug("Initializing GUI")
        self.title("Galora Management")

        self.animating = True
        load_language('eng')

        self.start_animation()

    # 7. start_animation: Starts the animation
    def start_animation(self):
        logging.debug("Starting animation")
        self.animation_image_path = "galora.png"
        self.animation_image = Image.open(self.animation_image_path)

        self.animation_image = self.animation_image.resize((self.animation_image.width // 2, self.animation_image.height // 2), Image.LANCZOS)
        self.animation_image = ImageTk.PhotoImage(self.animation_image)

        cm_to_pixels = lambda cm: int(cm * 37.7952755906)

        self.new_width = self.animation_image.width() + cm_to_pixels(2)
        self.new_height = self.animation_image.height() + cm_to_pixels(3)

        self.geometry(f"{self.new_width}x{self.new_height}")

        self.animation_label = tk.Label(self, image=self.animation_image)
        self.animation_label.image = self.animation_image
        self.animation_label.place(relx=0.5, rely=0.5, anchor='center')

        self.after(2000, self.run_animation)

    # 8. run_animation: Runs the animation
    def run_animation(self):
        logging.debug("Running animation")
        self.animate_image(self.animation_label)

    # 9. animate_image: Animates the image
    def animate_image(self, label):
        logging.debug("Animating image")
        width, height = self.animation_image.width(), self.animation_image.height()

        def update_image(scale):
            nonlocal width, height
            if scale <= 0:
                label.destroy()
                self.init_gui()
                return

            scaled_width = int(width * scale)
            scaled_height = int(height * scale)

            scaled_image = self.animation_image._PhotoImage__photo.subsample(int(1 / scale))
            label.configure(image=scaled_image)
            label.image = scaled_image
            label.place(x=0, y=0)

            self.update()
            self.after(50, lambda: update_image(scale - 0.05))

        update_image(1)

    # 10. init_gui: Initializes the main GUI
    def init_gui(self):
        logging.debug("Initializing main GUI")
        image_path = "galora.png"
        img = Image.open(image_path)

        cm_to_pixels = lambda cm: int(cm * 37.7952755906)
        img = img.resize((cm_to_pixels(3), cm_to_pixels(3)), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)

        img_label = tk.Label(self, image=img)
        img_label.image = img
        img_label.place(x=10, y=10)

        self.languages = {
            "English": "eng",
            "Italiano": "ita",
            "Français": "fra",
            "Español": "esp",
            "Deutsch": "deu",
            "Polski": "pol",
            "Português": "por",
            "Română": "rom",
            "Swahili": "swa"
        }
        self.current_language = tk.StringVar(value="English")
        self.language_menu = tk.OptionMenu(self, self.current_language, *self.languages.keys(), command=self.change_language)
        self.language_menu.place(x=self.new_width - 150, y=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.place(x=10, y=cm_to_pixels(3) + 20, width=self.new_width - 20, height=self.new_height - cm_to_pixels(3) - 30)

        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        self.tab4 = ttk.Frame(self.notebook)
        self.tab5 = ttk.Frame(self.notebook)

        self.notebook.add(self.tab1, text=lang.get('produzione_srt', "Produzione SRT"))
        self.notebook.add(self.tab2, text=lang.get('test_srt', "Test SRT"))
        self.notebook.add(self.tab3, text=lang.get('translitterazione', "Translitterazione"))
        self.notebook.add(self.tab4, text=lang.get('produzione_json', "Produzione JSON"))
        self.notebook.add(self.tab5, text=lang.get('setup_lingua', "Setup e Lingua"))

        self.create_srt_tab()
        self.create_test_srt_tab()
        self.create_translitterazione_tab()
        self.create_produzione_json_tab()
        self.create_setup_tab()

    # 11. change_language: Changes the language of the interface
    def change_language(self, language):
        logging.debug(f"Changing language: {language}")
        load_language(self.languages[language])
        update_language()

    # 12. create_srt_tab: Creates the SRT tab
    def create_srt_tab(self):
        logging.debug("Creating SRT tab")
        self.label_video_locale = tk.Label(self.tab1, text=lang.get('carica_video_locale', "Carica video locale"))
        self.label_video_locale.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.video_local_path = tk.Entry(self.tab1, width=50)
        self.video_local_path.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        tk.Button(self.tab1, text=lang.get('sfoglia', "Sfoglia"), command=self.browse_video_local).grid(row=0, column=2, padx=10, pady=10, sticky='ew')

        self.label_video_url = tk.Label(self.tab1, text=lang.get('url_video', "URL video (YouTube/Vimeo)"))
        self.label_video_url.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.video_url = tk.Entry(self.tab1, width=50)
        self.video_url.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

        self.audio_only = tk.BooleanVar()
        self.audio_only_button = tk.Checkbutton(self.tab1, text=lang.get('scarica_solo_audio', "Scarica solo audio"), variable=self.audio_only)
        self.audio_only_button.grid(row=2, column=1, padx=10, pady=10, sticky='w')

        self.label_language = tk.Label(self.tab1, text=lang.get('lingua', "Lingua"))
        self.label_language.grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.languages_menu = ["en-US", "it-IT", "fr-FR", "de-DE", "es-ES", "pt-PT", "ro-RO", "pl-PL"]
        self.selected_language = tk.StringVar(value="en-US")
        tk.OptionMenu(self.tab1, self.selected_language, *self.languages_menu).grid(row=3, column=1, padx=10, pady=10, sticky='w')

        self.save_srt_button = tk.Button(self.tab1, text=lang.get('salva_srt', "Salva SRT"), command=self.save_srt)
        self.save_srt_button.grid(row=4, column=0, padx=10, pady=10, sticky='ew')
        self.run_produzione_srt_button = tk.Button(self.tab1, text=lang.get('lancia_procedura', "Lancia Procedura"), command=self.run_produzione_srt)
        self.run_produzione_srt_button.grid(row=4, column=1, padx=10, pady=10, sticky='ew')

        # New output SRT file path field
        self.label_output_srt_file = tk.Label(self.tab1, text=lang.get('output_srt_file', "Output SRT File"))
        self.label_output_srt_file.grid(row=5, column=0, padx=10, pady=10, sticky='w')
        self.output_srt_file = tk.Entry(self.tab1, width=50, state='readonly')
        self.output_srt_file.grid(row=5, column=1, padx=10, pady=10, sticky='ew')

    # 13. create_test_srt_tab: Creates the Test SRT tab
    def create_test_srt_tab(self):
        logging.debug("Creating Test SRT tab")
        self.label_test_video = tk.Label(self.tab2, text=lang.get('file_video', "File video"))
        self.label_test_video.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.test_video_path = tk.Entry(self.tab2, width=50)
        self.test_video_path.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        tk.Button(self.tab2, text=lang.get('sfoglia', "Sfoglia"), command=self.browse_test_video).grid(row=0, column=2, padx=10, pady=10, sticky='ew')

        self.label_test_srt = tk.Label(self.tab2, text=lang.get('file_srt', "File SRT"))
        self.label_test_srt.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.test_srt_path = tk.Entry(self.tab2, width=50)
        self.test_srt_path.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        tk.Button(self.tab2, text=lang.get('sfoglia', "Sfoglia"), command=self.browse_test_srt).grid(row=1, column=2, padx=10, pady=10, sticky='ew')

        self.play_video_button = tk.Button(self.tab2, text=lang.get('play_video', "Play Video"), command=self.play_video)
        self.play_video_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

    # 14. create_translitterazione_tab: Creates the Transliteration tab
    def create_translitterazione_tab(self):
        logging.debug("Creating Transliteration tab")
        self.label_sorgenti = tk.Label(self.tab3, text=lang.get('sorgenti', "Sorgenti"))
        self.label_sorgenti.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.source_listbox = tk.Listbox(self.tab3)
        self.source_listbox.grid(row=1, column=0, padx=10, pady=10, sticky='ew')
        self.add_source_button = tk.Button(self.tab3, text=lang.get('aggiungi_sorgente', "Aggiungi Sorgente"), command=self.add_source)
        self.add_source_button.grid(row=2, column=0, padx=10, pady=10, sticky='ew')
        self.remove_source_button = tk.Button(self.tab3, text=lang.get('rimuovi_sorgente', "Rimuovi Sorgente"), command=self.remove_source)
        self.remove_source_button.grid(row=3, column=0, padx=10, pady=10, sticky='ew')

        self.label_dest_txt = tk.Label(self.tab3, text=lang.get('destinazione_txt', "Destinazione TXT"))
        self.label_dest_txt.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        self.dest_txt = tk.Entry(self.tab3, width=50)
        self.dest_txt.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        self.browse_dest_txt_button = tk.Button(self.tab3, text=lang.get('sfoglia', "Sfoglia"), command=self.browse_dest_txt)
        self.browse_dest_txt_button.grid(row=1, column=2, padx=10, pady=10, sticky='ew')

        self.run_translitterazione_button = tk.Button(self.tab3, text=lang.get('esegui_traslitterazione', "Esegui Traslitterazione"), command=self.run_translitterazione)
        self.run_translitterazione_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

    # 15. create_produzione_json_tab: Creates the JSON Production tab
    def create_produzione_json_tab(self):
        logging.debug("Creating JSON Production tab")
        self.label_parole_chiave = tk.Label(self.tab4, text=lang.get('parole_chiave', "Parole Chiave"))
        self.label_parole_chiave.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.keyword_listbox = tk.Listbox(self.tab4)
        self.keyword_listbox.grid(row=1, column=0, padx=10, pady=10, sticky='ew')
        self.add_keyword_button = tk.Button(self.tab4, text=lang.get('aggiungi_parola_chiave', "Aggiungi Parola Chiave"), command=self.add_keyword)
        self.add_keyword_button.grid(row=2, column=0, padx=10, pady=10, sticky='ew')
        self.remove_keyword_button = tk.Button(self.tab4, text=lang.get('rimuovi_parola_chiave', "Rimuovi Parola Chiave"), command=self.remove_keyword)
        self.remove_keyword_button.grid(row=3, column=0, padx=10, pady=10, sticky='ew')

        self.label_dest_json = tk.Label(self.tab4, text=lang.get('destinazione_json', "Destinazione JSON"))
        self.label_dest_json.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        self.dest_json = tk.Entry(self.tab4, width=50)
        self.dest_json.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        self.browse_dest_json_button = tk.Button(self.tab4, text=lang.get('sfoglia', "Sfoglia"), command=self.browse_dest_json)
        self.browse_dest_json_button.grid(row=1, column=2, padx=10, pady=10, sticky='ew')

        self.run_produzione_json_button = tk.Button(self.tab4, text=lang.get('esegui_produzione_json', "Esegui Produzione JSON"), command=self.run_produzione_json)
        self.run_produzione_json_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

    # 16. create_setup_tab: Creates the Setup tab
    def create_setup_tab(self):
        logging.debug("Creating Setup tab")
        self.label_local_dirs = tk.Label(self.tab5, text=lang.get('directory_locali', "Directory locali"))
        self.label_local_dirs.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.local_dirs_listbox = tk.Listbox(self.tab5)
        self.local_dirs_listbox.grid(row=1, column=0, padx=10, pady=10, sticky='ew')
        self.add_local_directory_button = tk.Button(self.tab5, text=lang.get('aggiungi_directory', "Aggiungi Directory"), command=self.add_local_directory)
        self.add_local_directory_button.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        self.remove_local_directory_button = tk.Button(self.tab5, text=lang.get('rimuovi_directory', "Rimuovi Directory"), command=self.remove_local_directory)
        self.remove_local_directory_button.grid(row=1, column=2, padx=10, pady=10, sticky='ew')

        self.label_cloud_sources = tk.Label(self.tab5, text=lang.get('sorgenti_cloud', "Sorgenti Cloud"))
        self.label_cloud_sources.grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.cloud_sources = ["Google Drive", "AWS", "Azure", "Aruba Drive"]
        self.selected_cloud_sources = tk.StringVar(value=self.cloud_sources)
        self.cloud_sources_listbox = tk.Listbox(self.tab5, listvariable=self.selected_cloud_sources, selectmode="multiple")
        self.cloud_sources_listbox.grid(row=3, column=0, padx=10, pady=10, sticky='ew')

        self.label_ignore_dirs = tk.Label(self.tab5, text=lang.get('directory_da_ignorare', "Directory da ignorare"))
        self.label_ignore_dirs.grid(row=4, column=0, padx=10, pady=10, sticky='w')
        self.ignore_dirs_listbox = tk.Listbox(self.tab5)
        self.ignore_dirs_listbox.grid(row=5, column=0, padx=10, pady=10, sticky='ew')
        self.add_ignore_directory_button = tk.Button(self.tab5, text=lang.get('aggiungi_directory', "Aggiungi Directory"), command=self.add_ignore_directory)
        self.add_ignore_directory_button.grid(row=5, column=1, padx=10, pady=10, sticky='ew')
        self.remove_ignore_directory_button = tk.Button(self.tab5, text=lang.get('rimuovi_directory', "Rimuovi Directory"), command=self.remove_ignore_directory)
        self.remove_ignore_directory_button.grid(row=5, column=2, padx=10, pady=10, sticky='ew')

        self.search_subdirs = tk.BooleanVar()
        self.search_subdirs_button = tk.Checkbutton(self.tab5, text=lang.get('cerca_nelle_sottodirectory', "Cerca nelle sottodirectory"), variable=self.search_subdirs)
        self.search_subdirs_button.grid(row=6, column=0, padx=10, pady=10, sticky='w')

        self.label_search_limits = tk.Label(self.tab5, text=lang.get('limiti_di_ricerca', "Limiti di ricerca"))
        self.label_search_limits.grid(row=7, column=0, padx=10, pady=10, sticky='w')
        self.search_limits = ["No limit", "Last produced per type", "Last produced in folder", "Last produced with similarity"]
        self.selected_search_limit = tk.StringVar(value="No limit")
        tk.OptionMenu(self.tab5, self.selected_search_limit, *self.search_limits).grid(row=7, column=1, padx=10, pady=10, sticky='w')

        self.save_config_button = tk.Button(self.tab5, text=lang.get('salva_configurazione', "Salva Configurazione"), command=self.save_config)
        self.save_config_button.grid(row=8, column=1, padx=10, pady=10, sticky='ew')
        self.load_config_button = tk.Button(self.tab5, text=lang.get('carica_configurazione', "Carica Configurazione"), command=self.load_config)
        self.load_config_button.grid(row=8, column=2, padx=10, pady=10, sticky='ew')

    # 17. browse_video_local: Opens a file dialog to browse for a local video file
    def browse_video_local(self):
        logging.debug("Browsing local video")
        video_path = filedialog.askopenfilename(title=lang.get('seleziona_file_video', "Seleziona File Video"))
        if video_path:
            self.video_local_path.delete(0, tk.END)
            self.video_local_path.insert(0, video_path)

    # 18. browse_test_video: Opens a file dialog to browse for a test video file
    def browse_test_video(self):
        logging.debug("Browsing test video")
        video_path = filedialog.askopenfilename(title=lang.get('seleziona_file_video', "Seleziona File Video"))
        if video_path:
            self.test_video_path.delete(0, tk.END)
            self.test_video_path.insert(0, video_path)

    # 19. browse_test_srt: Opens a file dialog to browse for a test SRT file
    def browse_test_srt(self):
        logging.debug("Browsing test SRT file")
        srt_path = filedialog.askopenfilename(title=lang.get('seleziona_file_srt', "Seleziona File SRT"))
        if srt_path:
            self.test_srt_path.delete(0, tk.END)
            self.test_srt_path.insert(0, srt_path)

    # 20. browse_dest_txt: Opens a file dialog to browse for a destination TXT directory
    def browse_dest_txt(self):
        logging.debug("Browsing destination TXT directory")
        dest = filedialog.askdirectory(title=lang.get('seleziona_directory_destinazione_txt', "Seleziona Directory Destinazione TXT"))
        if dest:
            self.dest_txt.delete(0, tk.END)
            self.dest_txt.insert(0, dest)

    # 21. browse_dest_json: Opens a file dialog to browse for a destination JSON directory
    def browse_dest_json(self):
        logging.debug("Browsing destination JSON directory")
        dest = filedialog.askdirectory(title=lang.get('seleziona_directory_destinazione_json', "Seleziona Directory Destinazione JSON"))
        if dest:
            self.dest_json.delete(0, tk.END)
            self.dest_json.insert(0, dest)

    # 22. save_srt: Opens a file dialog to save an SRT file
    def save_srt(self):
        logging.debug("Saving SRT file")
        file_path = filedialog.asksaveasfilename(defaultextension=".srt", filetypes=[("SRT files", "*.srt")])
        if file_path:
            self.srt_save_path = file_path
            self.output_srt_file.config(state='normal')
            self.output_srt_file.delete(0, tk.END)
            self.output_srt_file.insert(0, file_path)
            self.output_srt_file.config(state='readonly')

    # 23. run_produzione_srt: Runs the SRT production command
    def run_produzione_srt(self):
        logging.debug("Running SRT production")
        video_local = self.video_local_path.get()
        video_url = self.video_url.get()
        audio_only = self.audio_only.get()
        language = self.selected_language.get()
        output_dir = os.path.dirname(self.output_srt_file.get())
        output_srt_file = self.output_srt_file.get()
        if audio_only:
            command = f"python galora.py --operation generate_srt --file_path \"{video_local}\" --audio_only --language {language} --output_dir \"{output_srt_file}\""
        else:
            command = f"python galora.py --operation generate_srt --file_path \"{video_local}\" --language {language} --output_dir \"{output_srt_file}\""

        execute_command(command)

    # 24. add_source: Opens a directory dialog to add a source directory
    def add_source(self):
        logging.debug("Adding source")
        source = filedialog.askdirectory(title=lang.get('seleziona_directory_sorgente', "Seleziona Directory Sorgente"))
        if source:
            self.source_listbox.insert(tk.END, source)

    # 25. remove_source: Removes the selected source from the listbox
    def remove_source(self):
        logging.debug("Removing source")
        selected = self.source_listbox.curselection()
        if selected:
            self.source_listbox.delete(selected)

    # 26. run_translitterazione: Runs the transliteration command
    def run_translitterazione(self):
        logging.debug("Running transliteration")
        sources = list(self.source_listbox.get(0, tk.END))
        dest_txt = self.dest_txt.get()
        command = f"python galora.py --operation handle_directory --directory_path {' '.join(sources)} --output_dir {dest_txt}"
        execute_command(command)

    # 27. add_keyword: Opens a dialog to add a new keyword
    def add_keyword(self):
        logging.debug("Adding keyword")
        keyword = askstring(lang.get('input', "Input"), lang.get('nuova_parola_chiave', "Nuova Parola Chiave:"))
        if keyword:
            self.keyword_listbox.insert(tk.END, keyword)

    # 28. remove_keyword: Removes the selected keyword from the listbox
    def remove_keyword(self):
        logging.debug("Removing keyword")
        selected = self.keyword_listbox.curselection()
        if selected:
            self.keyword_listbox.delete(selected)

    # 29. run_produzione_json: Runs the JSON production command
    def run_produzione_json(self):
        logging.debug("Running JSON production")
        keywords = list(self.keyword_listbox.get(0, tk.END))
        dest_json = self.dest_json.get()
        sources = list(self.source_listbox.get(0, tk.END))
        command = f"python galora.py --operation process_keywords --directory_path {' '.join(sources)} --output_dir {dest_json} --keywords {' '.join(keywords)}"
        execute_command(command)

    # 30. play_video: Runs the command to play video with SRT
    def play_video(self):
        logging.debug("Playing video")
        video_path = self.test_video_path.get()
        srt_path = self.test_srt_path.get()
        command = f"python galora.py --play_video --video_path \"{video_path}\" --srt_path \"{srt_path}\""
        execute_command(command)

    # 31. add_local_directory: Opens a directory dialog to add a local directory
    def add_local_directory(self):
        logging.debug("Adding local directory")
        directory = filedialog.askdirectory(title=lang.get('seleziona_directory_locale', "Seleziona Directory Locale"))
        if directory:
            self.local_dirs_listbox.insert(tk.END, directory)

    # 32. remove_local_directory: Removes the selected local directory from the listbox
    def remove_local_directory(self):
        logging.debug("Removing local directory")
        selected = self.local_dirs_listbox.curselection()
        if selected:
            self.local_dirs_listbox.delete(selected)

    # 33. add_ignore_directory: Opens a directory dialog to add an ignore directory
    def add_ignore_directory(self):
        logging.debug("Adding ignore directory")
        directory = filedialog.askdirectory(title=lang.get('seleziona_directory_da_ignorare', "Seleziona Directory da Ignorare"))
        if directory:
            self.ignore_dirs_listbox.insert(tk.END, directory)

    # 34. remove_ignore_directory: Removes the selected ignore directory from the listbox
    def remove_ignore_directory(self):
        logging.debug("Removing ignore directory")
        selected = self.ignore_dirs_listbox.curselection()
        if selected:
            self.ignore_dirs_listbox.delete(selected)

    # 35. save_config: Opens a file dialog to save the current configuration
    def save_config(self):
        logging.debug("Saving configuration")
        config = {
            "sources": list(self.source_listbox.get(0, tk.END)),
            "dest_txt": self.dest_txt.get(),
            "dest_json": self.dest_json.get(),
            "keywords": list(self.keyword_listbox.get(0, tk.END)),
            "language": self.current_language.get(),
            "local_dirs": list(self.local_dirs_listbox.get(0, tk.END)),
            "cloud_sources": [self.cloud_sources[i] for i in self.cloud_sources_listbox.curselection()],
            "ignore_dirs": list(self.ignore_dirs_listbox.get(0, tk.END)),
            "search_subdirs": self.search_subdirs.get(),
            "search_limit": self.selected_search_limit.get()
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            save_configuration(config, file_path)

    # 36. load_config: Opens a file dialog to load a configuration
    def load_config(self):
        logging.debug("Loading configuration")
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            config = load_configuration(file_path)
            self.source_listbox.delete(0, tk.END)
            for source in config.get("sources", []):
                self.source_listbox.insert(tk.END, source)
            self.dest_txt.delete(0, tk.END)
            self.dest_txt.insert(0, config.get("dest_txt", ""))
            self.dest_json.delete(0, tk.END)
            self.dest_json.insert(0, config.get("dest_json", ""))
            self.keyword_listbox.delete(0, tk.END)
            for keyword in config.get("keywords", []):
                self.keyword_listbox.insert(tk.END, keyword)
            self.current_language.set(config.get("language", "eng"))
            self.local_dirs_listbox.delete(0, tk.END)
            for directory in config.get("local_dirs", []):
                self.local_dirs_listbox.insert(tk.END, directory)
            self.cloud_sources_listbox.selection_clear(0, tk.END)
            for source in config.get("cloud_sources", []):
                index = self.cloud_sources.index(source)
                self.cloud_sources_listbox.selection_set(index)
            self.ignore_dirs_listbox.delete(0, tk.END)
            for directory in config.get("ignore_dirs", []):
                self.ignore_dirs_listbox.insert(tk.END, directory)
            self.search_subdirs.set(config.get("search_subdirs", False))
            self.selected_search_limit.set(config.get("search_limit", "No limit"))

if __name__ == "__main__":
    app = GaloraGUI()
    app.mainloop()
