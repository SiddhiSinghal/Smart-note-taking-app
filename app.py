import streamlit as st
import json
import os

NOTES_FILE = "notes.json"

# Load notes from file
def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    return []

# Save notes to file
def save_notes(notes):
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)

# Delete a note by index
def delete_note(index):
    notes = load_notes()
    notes.pop(index)
    save_notes(notes)

# Add a new note
def add_note(title, content):
    notes = load_notes()
    notes.append({"title": title, "content": content})
    save_notes(notes)

# UI setup
st.set_page_config(page_title="Smart Note-Taking App", layout="centered")

st.title("📝 Smart Note-Taking App")
st.markdown("Create, search and manage your notes easily!")

# Add Note Section
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

# Search Notes
search_query = st.text_input("🔍 Search notes", "")

# Display Notes
st.subheader("📚 Your Notes")
notes = load_notes()
filtered_notes = [note for note in notes if search_query.lower() in note["title"].lower() or search_query.lower() in note["content"].lower()]

if filtered_notes:
    for i, note in enumerate(filtered_notes):
        st.markdown(f"### {note['title']}")
        st.write(note['content'])
        if st.button("🗑️ Delete", key=f"del_{i}"):
            # Get original index from notes list
            orig_index = notes.index(note)
            delete_note(orig_index)
else:
    st.info("No matching notes found." if search_query else "No notes added yet.")
