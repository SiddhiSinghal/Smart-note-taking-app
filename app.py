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
        json.dump(notes, f)

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

# UI
st.set_page_config(page_title="Smart Note-Taking App", layout="centered")

st.title("📝 Smart Note-Taking App")
st.markdown("Create and manage your notes easily!")

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

# Display Notes
st.subheader("Your Notes")
notes = load_notes()
if notes:
    for i, note in enumerate(notes):
        st.markdown(f"### {note['title']}")
        st.write(note['content'])
        if st.button(f"🗑️ Delete", key=f"delete_{i}"):
            delete_note(i)
            st.experimental_rerun()
else:
    st.info("No notes found. Add one above!")

