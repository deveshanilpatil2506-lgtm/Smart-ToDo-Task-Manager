
import tkinter as tk
import database
from task_manager import TaskManager


def main():
    database.initialize_db()

    root = tk.Tk()
    root.title("Smart To-Do Task Manager")
    root.geometry("800x550")
    root.minsize(650, 450)
    root.configure(bg="#f4f6f9")

    title = tk.Label(
        root,
        text="Smart To-Do Task Manager",
        font=("Segoe UI", 22, "bold"),
        bg="#f4f6f9",
        fg="#243447"
    )
    title.pack(pady=(25, 5))

    subtitle = tk.Label(
        root,
        text="Organize your day. Complete your goals.",
        font=("Segoe UI", 11),
        bg="#f4f6f9",
        fg="#667085"
    )
    subtitle.pack(pady=(0, 5))

    TaskManager(root)

    root.mainloop()


if __name__ == "__main__":
    main()


