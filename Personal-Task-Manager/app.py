import streamlit as st
from utils import load_tasks, save_tasks
from datetime import datetime

st.title("My Task Manager")

# Add Task
new_task = st.text_input("Add new task")
if st.button("Add") and new_task:
    tasks = load_tasks()
    tasks.append({
        "task": new_task,
        "done": False,
        "created": datetime.now().isoformat()
    })
    save_tasks(tasks)
    st.rerun()

# Display tasks

tasks = load_tasks()
for i, task in enumerate(tasks):
    col1, col2 = st.columns([4, 1])
    with col1:
        if st.checkbox(task['task'], task['done'], key=i):
            tasks[i]['done'] = True
            save_tasks(tasks)
    with col2:
        if st.button("🗑️", key=f"del_{i}"):
            tasks.pop(i)
            save_tasks(tasks)
            st.rerun()

