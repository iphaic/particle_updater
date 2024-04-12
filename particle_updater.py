import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter.ttk import Progressbar
import logging
import os
import re
import sys
import webbrowser

logging.basicConfig(filename='particle_updater.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ParticleSyntaxUpdater:
    def __init__(self, root):
        self.root = root
        self.setup_gui()

    def setup_gui(self):
        self.root.title("Phaic's Particle Updater")
        self.root.geometry("800x600")

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        icon_path = os.path.join(base_path, 'app_icon.ico')
        self.root.iconbitmap(icon_path)

        self.select_folder_button = tk.Button(self.root, text="Select Folder", command=self.select_folder)
        self.select_folder_button.pack(pady=10)

        self.folder_label = tk.Label(self.root, text="No folder selected")
        self.folder_label.pack()

        self.start_button = tk.Button(self.root, text="Start Syntax Update\nPlease make a backup before running this", command=self.start_update, state=tk.DISABLED)
        self.start_button.pack(pady=10)

        self.progress = Progressbar(self.root, length=300)
        self.progress.pack(pady=20)

        self.discord_button = tk.Button(self.root, text="Discord", command=self.open_discord_link)
        self.discord_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.log_display = scrolledtext.ScrolledText(self.root, height=10, state='disabled')
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def open_discord_link(self):
        # please join my discord lol
        webbrowser.open('https://discord.gg/sTbKDDjZ7e')

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.folder_label.config(text=self.folder_path)
            self.start_button.config(state=tk.NORMAL)
        else:
            logging.warning("No folder selected")

    def start_update(self):
        try:
            files = []
            for dirpath, dirnames, filenames in os.walk(self.folder_path):
                for f in filenames:
                    if f.endswith('.mcfunction'):
                        files.append(os.path.join(dirpath, f))

            total_files = len(files)
            self.progress['maximum'] = total_files

            for index, file_path in enumerate(files):
                self.update_file(file_path)
                self.progress['value'] = index + 1
                self.log_display.config(state='normal')
                self.log_display.insert(tk.END, f"Checked: {file_path}\n")
                self.log_display.see(tk.END)
                self.log_display.config(state='disabled')
                self.root.update_idletasks()

            messagebox.showinfo("Update Complete", "All files have been updated!\nConsider checking out my Discord")
            self.progress['value'] = 0
        except Exception as e:
            messagebox.showerror("Error", str(e))
            logging.error(f"Error during update: {e}")

    def update_file(self, file_path):
        try:
            with open(file_path, 'r+') as file:
                content = file.read()
                updated_content = self.update_syntax(content)
                file.seek(0)
                file.write(updated_content)
                file.truncate()
        except Exception as e:
            logging.error(f"Failed to update file {file_path}: {e}")

    # reformat any integers found
    def format_dust(self, match):
        parts = []
        for i in range(1, 5):
            value = match.group(i)
            if value.isdigit():
                value = f"{int(value)}.0"
            parts.append(value)
        return f"particle minecraft:dust{{color:[{parts[0]}, {parts[1]}, {parts[2]}], scale:{parts[3]}}}"

    def format_dust_color_transition(self, match):
        parts = []
        for i in range(1, 8):
            value = match.group(i)
            if value.isdigit():
                value = f"{int(value)}.0"
            parts.append(value)
        return f"particle minecraft:dust_color_transition{{from_color: [{parts[0]}, {parts[1]}, {parts[2]}], scale: {parts[3]}, to_color: [{parts[4]}, {parts[5]}, {parts[6]}]}}"

    # do updates
    def update_syntax(self, content):
        # dust
        content = re.sub(
            r"particle (?:minecraft:)?dust (\d+\.?\d*) (\d+\.?\d*) (\d+\.?\d*) (\d+\.?\d*)",
            self.format_dust,
            content
        )
        # dust_color_transition
        content = re.sub(
            r"particle (?:minecraft:)?dust_color_transition (\d+\.?\d*) (\d+\.?\d*) (\d+\.?\d*) (\d+\.?\d*) (\d+\.?\d*) (\d+\.?\d*) (\d+\.?\d*)",
            self.format_dust_color_transition,
            content
        )
        # item
        content = re.sub(
        r"particle (?:minecraft:)?item ([a-zA-Z_]+)(?:\{(?:minecraft:)?custom_model_data=(\d+)\})?",
        lambda m: f"particle item{{item:{{id:\"minecraft:{m.group(1)}\"{',components:{\"minecraft:custom_model_data\":' + m.group(2) + '}' if m.group(2) else ''}}}}}",
        content
        )
        # block, block_marker, falling_dust, dust_pillar
        content = re.sub(
            r"(particle\s+(?:minecraft:)?(block|block_marker|falling_dust|dust_pillar)) ([a-z_]+)",
            r"\1{block_state: 'minecraft:\3'}",
            content
        ) 
        # entity effect
        content = re.sub(
            r"(particle\s+(?:minecraft:)?entity_effect) (\d*\.?\d+) (\d*\.?\d+) (\d*\.?\d+) (\d*\.?\d+)",
            r"\1{color:[\2, \3, \4, \5]}",
            content
        )
        return content

if __name__ == "__main__":
    root = tk.Tk()
    app = ParticleSyntaxUpdater(root)
    root.mainloop()