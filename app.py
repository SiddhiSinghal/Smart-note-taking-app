import streamlit as st
import json
import os

NOTES_FILE = "notes.json"

def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    return []

def save_notes(notes):
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)

def delete_note(index):
    notes = load_notes()
    notes.pop(index)
    save_notes(notes)

def add_note(title, content):
    notes = load_notes()
    notes.append({"title": title, "content": content})
    save_notes(notes)

st.set_page_config(page_title="Smart Note-Taking App", layout="centered")

st.title("📝 Smart Note-Taking App")
st.markdown("Create, search and manage your notes easily!")

with st.form("note_form"):
    title = st.text_input("Title")
    content = st.text_area("Content")
    submitted = st.form_submit_button("Add Note")
    if submitted:
        if title and content:
            add_note(title, content)
            st.success("Note added!")
        else:
            st.warning("Please fill in both title and content.")

search_query = st.text_input("🔍 Search notes", "")

st.subheader("📚 Your Notes")
notes = load_notes()
filtered_notes = [note for note in notes if search_query.lower() in note["title"].lower() or search_query.lower() in note["content"].lower()]

if filtered_notes:
    for i, note in enumerate(filtered_notes):
        st.markdown(f"### {note['title']}")
        st.write(note['content'])
        if st.button("🗑️ Delete", key=f"del_{i}"):
            orig_index = notes.index(note)
            delete_note(orig_index)
else:
    st.info("No matching notes found." if search_query else "No notes added yet.")
