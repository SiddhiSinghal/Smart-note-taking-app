import os
import json
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import re
from ttkthemes import ThemedTk

class Note:
    def __init__(self, title="", content="", tags=None, category="General"):
        self.id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.title = title
        self.content = content
        self.tags = tags if tags else []
        self.category = category
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "category": self.category,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        note = cls()
        note.id = data["id"]
        note.title = data["title"]
        note.content = data["content"]
        note.tags = data["tags"]
        note.category = data["category"]
        note.created_at = data["created_at"]
        note.updated_at = data["updated_at"]
        return note


class NoteManager:
    def __init__(self, data_file="notes.json"):
        self.data_file = data_file
        self.notes = []
        self.categories = ["General"]
        self.load_notes()

    def load_notes(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    self.notes = [Note.from_dict(note_data) for note_data in data["notes"]]
                    self.categories = data["categories"]
            except (json.JSONDecodeError, KeyError) as e:
                messagebox.showerror("Error", f"Failed to load notes: {str(e)}")
                self.notes = []
                self.categories = ["General"]

    def save_notes(self):
        data = {
            "notes": [note.to_dict() for note in self.notes],
            "categories": self.categories
        }
        
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)

    def add_note(self, note):
        self.notes.append(note)
        if note.category not in self.categories:
            self.categories.append(note.category)
        self.save_notes()
        return note

    def update_note(self, note_id, title, content, tags, category):
        for note in self.notes:
            if note.id == note_id:
                note.title = title
                note.content = content
                note.tags = tags
                note.category = category
                note.updated_at = datetime.datetime.now().isoformat()
                
                if category not in self.categories:
                    self.categories.append(category)
                
                self.save_notes()
                return note
        return None

    def delete_note(self, note_id):
        for i, note in enumerate(self.notes):
            if note.id == note_id:
                del self.notes[i]
                self.save_notes()
                return True
        return False

    def get_note(self, note_id):
        for note in self.notes:
            if note.id == note_id:
                return note
        return None

    def get_all_notes(self):
        return self.notes
    
    def get_notes_by_category(self, category):
        return [note for note in self.notes if note.category == category]
    
    def search_notes(self, query):
        results = []
        query = query.lower()
        
        for note in self.notes:
            if (query in note.title.lower() or 
                query in note.content.lower() or 
                any(query in tag.lower() for tag in note.tags)):
                results.append(note)
                
        return results


class SmartNoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Note Taking App")
        self.root.geometry("1000x600")
        
        self.note_manager = NoteManager()
        self.current_note = None
        self.displayed_notes = []  
        
        self.create_widgets()
        self.refresh_notes_list()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_panel = ttk.Frame(main_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        search_frame = ttk.Frame(left_panel)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        search_button = ttk.Button(search_frame, text="Search", command=self.on_search_button)
        search_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        category_frame = ttk.LabelFrame(left_panel, text="Categories")
        category_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.category_var = tk.StringVar()
        self.category_var.set("All")
        
        categories = ["All"] + self.note_manager.categories
        for category in categories:
            rb = ttk.Radiobutton(category_frame, text=category, value=category, 
                                variable=self.category_var, command=self.on_category_select)
            rb.pack(anchor=tk.W, padx=5, pady=2)
        
        notes_frame = ttk.LabelFrame(left_panel, text="Notes")
        notes_frame.pack(fill=tk.BOTH, expand=True)
        
        self.notes_listbox = tk.Listbox(notes_frame, selectmode=tk.SINGLE)
        self.notes_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.notes_listbox.bind("<<ListboxSelect>>", self.on_note_select)
        
        buttons_frame = ttk.Frame(left_panel)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        new_button = ttk.Button(buttons_frame, text="New Note", command=self.new_note)
        new_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        delete_button = ttk.Button(buttons_frame, text="Delete", command=self.delete_note)
        delete_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        editor_top = ttk.Frame(right_panel)
        editor_top.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(editor_top, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(editor_top, textvariable=self.title_var)
        title_entry.grid(row=0, column=1, sticky=tk.EW)
        
        ttk.Label(editor_top, text="Category:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.note_category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(editor_top, textvariable=self.note_category_var)
        self.category_combo.grid(row=0, column=3, sticky=tk.EW)
        self.update_categories_combo()
        
        editor_top.columnconfigure(1, weight=2)
        editor_top.columnconfigure(3, weight=1)

        tags_frame = ttk.Frame(right_panel)
        tags_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(tags_frame, text="Tags (comma separated):").pack(side=tk.LEFT, padx=(0, 5))
        self.tags_var = tk.StringVar()
        tags_entry = ttk.Entry(tags_frame, textvariable=self.tags_var)
        tags_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(right_panel, text="Content:").pack(anchor=tk.W)
        self.content_text = scrolledtext.ScrolledText(right_panel, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        save_button = ttk.Button(right_panel, text="Save", command=self.save_note)
        save_button.pack(fill=tk.X)

    def refresh_notes_list(self):
        selected_category = self.category_var.get()
        search_query = self.search_var.get()

        self.notes_listbox.delete(0, tk.END)
        
        if search_query:
            notes = self.note_manager.search_notes(search_query)
        elif selected_category == "All":
            notes = self.note_manager.get_all_notes()
        else:
            notes = self.note_manager.get_notes_by_category(selected_category)
        
        notes.sort(key=lambda x: x.updated_at, reverse=True)
        
        self.displayed_notes = notes

        for note in notes:
            self.notes_listbox.insert(tk.END, note.title)
    
    def update_categories_combo(self):
        self.category_combo['values'] = self.note_manager.categories
    
    def new_note(self):
        self.current_note = None
        self.title_var.set("")
        self.note_category_var.set("General")
        self.tags_var.set("")
        self.content_text.delete(1.0, tk.END)
    
    def on_note_select(self, event):
        selection = self.notes_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.displayed_notes):
                note = self.displayed_notes[index]
                self.current_note = note
                self.title_var.set(note.title)
                self.note_category_var.set(note.category)
                self.tags_var.set(", ".join(note.tags))
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(tk.END, note.content)
    
    def save_note(self):
        title = self.title_var.get().strip()
        category = self.note_category_var.get().strip()
        tags_text = self.tags_var.get().strip()
        content = self.content_text.get(1.0, tk.END).strip()
        
        if not title:
            messagebox.showerror("Error", "Title cannot be empty")
            return
        
        if not category:
            category = "General"
        
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
        
        if self.current_note:
            self.note_manager.update_note(
                self.current_note.id, title, content, tags, category
            )
        else:
            note = Note(title, content, tags, category)
            self.note_manager.add_note(note)
            self.current_note = note
        
        self.update_categories_combo()
        self.refresh_notes_list()
        messagebox.showinfo("Success", "Note saved successfully")
    
    def delete_note(self):
        if self.current_note:
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this note?"):
                if self.note_manager.delete_note(self.current_note.id):
                    self.current_note = None
                    self.new_note()
                    self.refresh_notes_list()
                    messagebox.showinfo("Success", "Note deleted successfully")
                else:
                    messagebox.showerror("Error", "Failed to delete note")
        else:
            messagebox.showinfo("Info", "No note selected")
    
    def on_category_select(self, *args):
        self.refresh_notes_list()
    
    def on_search(self, *args):
        self.root.after(300, self.refresh_notes_list)
    
    def on_search_button(self):
        self.refresh_notes_list()


def main():
    root = ThemedTk(theme="arc")
    app = SmartNoteApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()