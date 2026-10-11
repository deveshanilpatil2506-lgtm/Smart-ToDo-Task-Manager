
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import database


class TaskManager:
    def __init__(self, parent):
        self.parent = parent
        self.tasks = []
        self.visible_tasks = []
        
        
        # Professional application theme
        style = ttk.Style(self.parent)
        style.theme_use("clam")

        self.parent.configure(bg="#F3F5FA")

        style.configure(
            "TFrame",
            background="#F3F5FA"
        )

        style.configure(
            "TLabel",
            background="#F3F5FA",
            foreground="#243047",
            font=("Segoe UI", 10)
        )

        style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(10, 7),
            background="#E1E7F0",
            foreground="#243047"
        )

        style.map(
            "TButton",
            background=[("active", "#CCD7E8")]
        )

        style.configure(
            "TEntry",
            padding=7,
            font=("Segoe UI", 10)
        )

        style.configure(
            "TCombobox",
            padding=5,
            font=("Segoe UI", 10)
        )


        database.initialize_db()

        self.frame = ttk.Frame(parent, padding=20)
        self.frame.pack(fill="both", expand=True, padx=30, pady=10)

        ttk.Label(
            self.frame,
            text="Task Dashboard",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", pady=(0, 8))

        # Dashboard statistics
        stats = ttk.Frame(self.frame)
        stats.pack(fill="x", pady=(0, 12))

        self.total_label = ttk.Label(stats, text="Total: 0")
        self.total_label.pack(side="left", padx=(0, 18))

        self.pending_label = ttk.Label(stats, text="Pending: 0")
        self.pending_label.pack(side="left", padx=(0, 18))

        self.completed_label = ttk.Label(stats, text="Completed: 0")
        self.completed_label.pack(side="left", padx=(0, 18))

        self.overdue_label = ttk.Label(stats, text="Overdue: 0")
        self.overdue_label.pack(side="left")

        # Task input
        input_frame = ttk.Frame(self.frame)
        input_frame.pack(fill="x", pady=5)

        ttk.Label(input_frame, text="Task:").pack(side="left")

        self.task_input = ttk.Entry(
            input_frame, font=("Segoe UI", 11)
        )
        self.task_input.pack(
            side="left", fill="x", expand=True, padx=8
        )
        self.task_input.bind(
            "<Return>", lambda event: self.add_task()
        )

        # Priority and deadline
        options_frame = ttk.Frame(self.frame)
        options_frame.pack(fill="x", pady=8)

        ttk.Label(options_frame, text="Priority:").pack(side="left")

        self.priority = tk.StringVar(value="Medium")

        ttk.Combobox(
            options_frame,
            textvariable=self.priority,
            values=["High", "Medium", "Low"],
            state="readonly",
            width=10
        ).pack(side="left", padx=(6, 18))

        ttk.Label(
            options_frame, text="Deadline (YYYY-MM-DD):"
        ).pack(side="left")

        self.deadline_input = ttk.Entry(
            options_frame, width=14
        )
        self.deadline_input.pack(side="left", padx=6)

        # Search
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill="x", pady=(12, 5))

        ttk.Label(search_frame, text="Search:").pack(side="left")

        self.search_input = ttk.Entry(search_frame)
        self.search_input.pack(
            side="left", fill="x", expand=True, padx=8
        )
        self.search_input.bind(
            "<KeyRelease>", lambda event: self.refresh_tasks()
        )

        # Filters
        filter_frame = ttk.Frame(self.frame)
        filter_frame.pack(fill="x", pady=5)

        ttk.Label(filter_frame, text="Priority:").pack(side="left")

        self.priority_filter = tk.StringVar(value="All")

        ttk.Combobox(
            filter_frame,
            textvariable=self.priority_filter,
            values=["All", "High", "Medium", "Low"],
            state="readonly",
            width=10
        ).pack(side="left", padx=6)

        ttk.Label(filter_frame, text="Status:").pack(
            side="left", padx=(12, 0)
        )

        self.status_filter = tk.StringVar(value="All")

        ttk.Combobox(
            filter_frame,
            textvariable=self.status_filter,
            values=["All", "Pending", "Completed"],
            state="readonly",
            width=12
        ).pack(side="left", padx=6)

        self.priority_filter.trace_add(
            "write", lambda *_: self.refresh_tasks()
        )
        self.status_filter.trace_add(
            "write", lambda *_: self.refresh_tasks()
        )

        # Task list
        self.task_list = tk.Listbox(
            self.frame,
            font=("Segoe UI", 10),
            height=9,
            selectmode=tk.SINGLE,
            activestyle="none",
            borderwidth=0,
            highlightthickness=1
        )
        self.task_list.pack(fill="both", expand=True, pady=12)

        # Action buttons
        buttons = ttk.Frame(self.frame)
        buttons.pack(fill="x", pady=5)

        ttk.Button(
            buttons,
            text="Add Task",
            command=self.add_task
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            buttons,
            text="Edit Task",
            command=self.edit_task
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            buttons,
            text="Complete Task",
            command=self.complete_task
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            buttons,
            text="Delete Task",
            command=self.delete_task
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            buttons,
            text="Clear Filters",
            command=self.clear_filters
        ).pack(side="left")

        self.status = ttk.Label(self.frame, text="")
        self.status.pack(anchor="w", pady=(10, 0))

        self.refresh_tasks()

    def add_task(self):
        title = self.task_input.get().strip()
        priority = self.priority.get()
        deadline = self.deadline_input.get().strip()

        if not title:
            messagebox.showwarning(
                "Missing Task", "Please enter a task title."
            )
            return

        if deadline:
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning(
                    "Invalid Date",
                    "Use YYYY-MM-DD, for example 2026-10-25."
                )
                return

        database.add_task(title, priority, deadline)

        self.task_input.delete(0, tk.END)
        self.deadline_input.delete(0, tk.END)
        self.priority.set("Medium")

        self.refresh_tasks()

    def edit_task(self):
        selection = self.task_list.curselection()

        if not selection:
            messagebox.showinfo(
                "Select Task",
                "Please select a task to edit."
            )
            return

        task = self.visible_tasks[selection[0]]
        task_id, title, completed, priority, deadline = task

        # Create popup
        popup = tk.Toplevel(self.parent)
        popup.title("Edit Task")
        popup.geometry("400x300")
        popup.resizable(False, False)
        popup.transient(self.parent)
        popup.grab_set()

        container = ttk.Frame(popup, padding=20)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="Edit Your Task",
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", pady=(0, 15))

        ttk.Label(container, text="Task title:").pack(anchor="w")

        title_entry = ttk.Entry(container, width=45)
        title_entry.pack(fill="x", pady=(4, 12))
        title_entry.insert(0, title)

        ttk.Label(container, text="Priority:").pack(anchor="w")

        priority_var = tk.StringVar(value=priority)

        ttk.Combobox(
            container,
            textvariable=priority_var,
            values=["High", "Medium", "Low"],
            state="readonly"
        ).pack(fill="x", pady=(4, 12))

        ttk.Label(
            container,
            text="Deadline (YYYY-MM-DD, optional):"
        ).pack(anchor="w")

        deadline_entry = ttk.Entry(container)
        deadline_entry.pack(fill="x", pady=(4, 15))
        deadline_entry.insert(0, deadline)

        def save_changes():
            new_title = title_entry.get().strip()
            new_priority = priority_var.get()
            new_deadline = deadline_entry.get().strip()

            if not new_title:
                messagebox.showwarning(
                    "Missing Title",
                    "Task title cannot be empty.",
                    parent=popup
                )
                return

            if new_priority not in ["High", "Medium", "Low"]:
                messagebox.showwarning(
                    "Invalid Priority",
                    "Please select a valid priority.",
                    parent=popup
                )
                return

            if new_deadline:
                try:
                    datetime.strptime(
                        new_deadline, "%Y-%m-%d"
                    )
                except ValueError:
                    messagebox.showwarning(
                        "Invalid Date",
                        "Enter the date as YYYY-MM-DD.",
                        parent=popup
                    )
                    return

            database.update_task(
                task_id,
                new_title,
                new_priority,
                new_deadline
            )

            popup.destroy()
            self.refresh_tasks()

        button_frame = ttk.Frame(container)
        button_frame.pack(fill="x")

        ttk.Button(
            button_frame,
            text="Save Changes",
            command=save_changes
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy
        ).pack(side="left")

        title_entry.focus_set()

    def complete_task(self):
        selection = self.task_list.curselection()

        if not selection:
            messagebox.showinfo(
                "Select Task", "Please select a task first."
            )
            return

        task = self.visible_tasks[selection[0]]

        if task[2]:
            messagebox.showinfo(
                "Already Completed",
                "This task is already completed."
            )
            return

        database.complete_task(task[0])
        self.refresh_tasks()

    def delete_task(self):
        selection = self.task_list.curselection()

        if not selection:
            messagebox.showinfo(
                "Select Task", "Please select a task first."
            )
            return

        database.delete_task(
            self.visible_tasks[selection[0]][0]
        )
        self.refresh_tasks()

    def clear_filters(self):
        self.search_input.delete(0, tk.END)
        self.priority_filter.set("All")
        self.status_filter.set("All")
        self.refresh_tasks()

    def refresh_tasks(self):
        self.tasks = database.get_tasks()
        today = date.today()

        total = len(self.tasks)
        completed = sum(task[2] == 1 for task in self.tasks)
        pending = total - completed

        overdue = sum(
            not task[2]
            and bool(task[4])
            and task[4] < today.isoformat()
            for task in self.tasks
        )

        self.total_label.config(text=f"Total: {total}")
        self.pending_label.config(text=f"Pending: {pending}")
        self.completed_label.config(text=f"Completed: {completed}")
        self.overdue_label.config(text=f"Overdue: {overdue}")

        search_text = self.search_input.get().strip().lower()
        priority_choice = self.priority_filter.get()
        status_choice = self.status_filter.get()

        self.visible_tasks = [
            task for task in self.tasks
            if search_text in task[1].lower()
            and (
                priority_choice == "All"
                or task[3] == priority_choice
            )
            and (
                status_choice == "All"
                or (status_choice == "Completed" and task[2] == 1)
                or (status_choice == "Pending" and task[2] == 0)
            )
        ]

        self.task_list.delete(0, tk.END)

        for index, task in enumerate(self.visible_tasks):
            task_id, title, completed, priority, deadline = task

            if completed:
                label = "[DONE]"
                color = "#dff5e1"
            elif deadline and deadline < today.isoformat():
                label = "[OVERDUE]"
                color = "#ffdede"
            elif deadline == today.isoformat():
                label = "[DUE TODAY]"
                color = "#fff0cc"
            else:
                label = "[TODO]"
                color = "white"

            due = deadline if deadline else "No deadline"

            self.task_list.insert(
                tk.END,
                f"{label} [{priority}] {title} | Due: {due}"
            )
            self.task_list.itemconfig(index, background=color)

        self.status.config(
            text=f"Showing {len(self.visible_tasks)} of {total} tasks"
        )
