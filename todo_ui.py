import customtkinter as ctk
import json
import os
from datetime import datetime

# =========================
# THEME CONFIG (BLACK / WHITE)
# =========================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

TASKS_FILE = "tasks.json"
USERS_FILE = "users.json"
SYNC_FILE = "cloud_sync.json"

BLACK = "#000000"
CARD = "#0f0f0f"
WHITE = "#ffffff"
GRAY = "#8a8a8a"
LINE = "#1c1c1c"


# =========================
# JSON HELPERS
# =========================
def read_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_tasks():
    return read_json(TASKS_FILE, [])


def save_tasks(tasks):
    write_json(TASKS_FILE, tasks)
    write_json(SYNC_FILE, tasks)


def load_users():
    return read_json(USERS_FILE, {})


def save_users(users):
    write_json(USERS_FILE, users)


# =========================
# SPLASH SCREEN
# =========================
class SplashScreen(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.overrideredirect(True)
        self.configure(fg_color=BLACK)

        w, h = 520, 300
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        self.title_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=WHITE
        )
        self.title_label.place(relx=0.5, rely=0.40, anchor="center")

        self.by_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=14),
            text_color=GRAY
        )
        self.by_label.place(relx=0.5, rely=0.55, anchor="center")

        self.progress = ctk.CTkProgressBar(self, width=300, progress_color=WHITE, fg_color=LINE)
        self.progress.place(relx=0.5, rely=0.75, anchor="center")
        self.progress.set(0)

        self.text = "todo."
        self.index = 0
        self.value = 0
        self.after(250, self.animate_text)

    def animate_text(self):
        if self.index <= len(self.text):
            self.title_label.configure(text=self.text[:self.index])
            self.index += 1
            self.after(90, self.animate_text)
        else:
            self.by_label.configure(text="by Orestis Kerkines")
            self.after(200, self.animate_bar)

    def animate_bar(self):
        if self.value < 100:
            self.value += 2
            self.progress.set(self.value / 100)
            self.after(18, self.animate_bar)
        else:
            self.after(300, self.finish)

    def finish(self):
        self.destroy()
        self.callback()


# =========================
# AUTH PAGE
# =========================
class AuthPage(ctk.CTkFrame):
    def __init__(self, parent, on_login):
        super().__init__(parent, fg_color=BLACK)
        self.on_login = on_login
        self.pack(fill="both", expand=True)

        container = ctk.CTkFrame(self, fg_color=CARD, corner_radius=24)
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.45, relheight=0.62)

        ctk.CTkLabel(container, text="todo.", font=ctk.CTkFont(size=40, weight="bold"), text_color=WHITE).pack(pady=(35, 5))
        ctk.CTkLabel(container, text="by Orestis Kerkines", text_color=GRAY).pack()

        self.username = ctk.CTkEntry(container, placeholder_text="Username", height=48)
        self.username.pack(fill="x", padx=40, pady=(30, 10))

        self.password = ctk.CTkEntry(container, placeholder_text="Password", show="*", height=48)
        self.password.pack(fill="x", padx=40, pady=10)

        buttons = ctk.CTkFrame(container, fg_color="transparent")
        buttons.pack(pady=25)

        ctk.CTkButton(buttons, text="Sign In", fg_color=WHITE, text_color=BLACK, command=self.sign_in).pack(side="left", padx=6)
        ctk.CTkButton(buttons, text="Sign Up", fg_color="#1f1f1f", command=self.sign_up).pack(side="left", padx=6)

        self.status = ctk.CTkLabel(container, text="", text_color=GRAY)
        self.status.pack()

    def sign_up(self):
        users = load_users()
        u = self.username.get().strip()
        p = self.password.get().strip()
        if not u or not p:
            self.status.configure(text="Fill all fields")
            return
        if u in users:
            self.status.configure(text="Username exists")
            return
        users[u] = {"password": p}
        save_users(users)
        self.status.configure(text="Account created")

    def sign_in(self):
        users = load_users()
        u = self.username.get().strip()
        p = self.password.get().strip()
        if u in users and users[u]["password"] == p:
            self.on_login(u)
        else:
            self.status.configure(text="Wrong login")


# =========================
# MAIN APP
# =========================
class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("todo. Pro")
        self.geometry("1180x760")
        self.configure(fg_color=BLACK)

        self.tasks = []
        self.current_user = None
        self.filter_mode = "All"
        self.edit_index = None

        self.withdraw()
        SplashScreen(self, self.show_auth)

    def show_auth(self):
        self.deiconify()
        self.auth = AuthPage(self, self.launch_app)

    def launch_app(self, username):
        self.current_user = username
        self.auth.destroy()
        self.tasks = load_tasks()
        self.build_ui()
        self.refresh()

    def build_ui(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, fg_color=CARD, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="todo.", font=ctk.CTkFont(size=34, weight="bold"), text_color=WHITE).pack(pady=(35, 0))
        ctk.CTkLabel(self.sidebar, text="by Orestis Kerkines", text_color=GRAY).pack(pady=(0, 25))
        ctk.CTkLabel(self.sidebar, text=f"Welcome, {self.current_user}", text_color=GRAY).pack(pady=10)

        for tab in ["All", "Active", "Done"]:
            ctk.CTkButton(
                self.sidebar,
                text=tab,
                height=42,
                fg_color="#141414",
                hover_color="#1d1d1d",
                command=lambda t=tab: self.change_filter(t)
            ).pack(fill="x", padx=20, pady=6)

        ctk.CTkButton(self.sidebar, text="Sync", height=42, fg_color=WHITE, text_color=BLACK, command=self.sync_tasks).pack(fill="x", padx=20, pady=(25, 8))

        # Main content
        self.main = ctk.CTkFrame(self, fg_color=BLACK)
        self.main.pack(side="left", fill="both", expand=True, padx=25, pady=25)

        top = ctk.CTkFrame(self.main, fg_color="transparent")
        top.pack(fill="x")

        self.search_var = ctk.StringVar()
        self.search = ctk.CTkEntry(top, textvariable=self.search_var, placeholder_text="🔍 Search tasks by title...", height=48)
        self.search.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.search.bind("<KeyRelease>", lambda e: self.refresh())

        self.entry = ctk.CTkEntry(top, placeholder_text="✍️ Enter a new task here...", height=48)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 12))

        self.priority_var = ctk.StringVar(value="Medium")
        self.priority = ctk.CTkOptionMenu(top, values=["🔴 High", "🟠 Medium", "🟢 Low"], variable=self.priority_var, height=48)
        self.priority_var.set("🟠 Medium")
        self.priority.pack(side="left", padx=(0, 12))

        self.add_btn = ctk.CTkButton(top, text="Add", fg_color=WHITE, text_color=BLACK, width=90, height=48, command=self.add_or_edit_task)
        self.add_btn.pack(side="left")

        self.progress = ctk.CTkProgressBar(self.main, progress_color=WHITE, fg_color=LINE)
        self.progress.pack(fill="x", pady=18)

        self.stats = ctk.CTkLabel(self.main, text="", text_color=GRAY)
        self.stats.pack(anchor="w", pady=(0, 10))

        self.task_area = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        self.task_area.pack(fill="both", expand=True)

    def sync_tasks(self):
        self.tasks = read_json(SYNC_FILE, self.tasks)
        self.refresh()

    def change_filter(self, mode):
        self.filter_mode = mode
        self.refresh()

    def add_or_edit_task(self):
        title = self.entry.get().strip()
        if not title:
            return

        task = {
            "title": title,
            "done": False,
            "priority": self.priority_var.get().replace("🔴 ", "").replace("🟠 ", "").replace("🟢 ", ""),
            "due_date": datetime.now().strftime("Tomorrow 18:00"),
            "streak": 1,
            "created": datetime.now().strftime("%d/%m/%Y %H:%M")
        }

        if self.edit_index is not None:
            task["done"] = self.tasks[self.edit_index]["done"]
            self.tasks[self.edit_index] = task
            self.edit_index = None
            self.add_btn.configure(text="Add")
        else:
            self.tasks.append(task)

        save_tasks(self.tasks)
        self.entry.delete(0, "end")
        self.refresh()

    def refresh(self):
        for widget in self.task_area.winfo_children():
            widget.destroy()

        search = self.search_var.get().lower() if hasattr(self, "search_var") else ""
        visible = []
        for i, task in enumerate(self.tasks):
            if search not in task["title"].lower():
                continue
            if self.filter_mode == "Active" and task["done"]:
                continue
            if self.filter_mode == "Done" and not task["done"]:
                continue
            visible.append((i, task))

        done_count = sum(1 for t in self.tasks if t["done"])
        total = len(self.tasks)
        self.progress.set(done_count / total if total else 0)
        self.stats.configure(text=f"📊 {done_count}/{total} completed • 🏆 Productivity Score: {done_count*10} • 🔥 Streak: {done_count}")

        for i, task in visible:
            self.task_card(i, task)

    def task_card(self, i, task):
        priority_colors = {"High": "#ff4d4d", "Medium": "#ffb84d", "Low": "#4dff88"}

        card = ctk.CTkFrame(self.task_area, fg_color=CARD, corner_radius=18)
        card.pack(fill="x", pady=7)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(14, 6))

        ctk.CTkLabel(
            header,
            text=task["title"],
            font=ctk.CTkFont(size=16, weight="bold", overstrike=task["done"]),
            text_color=GRAY if task["done"] else WHITE
        ).pack(side="left")

        ctk.CTkLabel(header, text=f"● {task['priority']}", text_color=priority_colors.get(task['priority'], WHITE), font=ctk.CTkFont(size=13, weight='bold')).pack(side="left", padx=12)
        ctk.CTkLabel(header, text=f"📅 {task.get('due_date', 'No deadline')}", text_color=GRAY).pack(side="left", padx=12)
        ctk.CTkLabel(header, text=task.get("created", ""), text_color=GRAY).pack(side="right")

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=18, pady=(0, 14))

        ctk.CTkButton(actions, text="✓ Done", width=90, fg_color=WHITE, text_color=BLACK, command=lambda idx=i: self.toggle_task(idx)).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="✎ Edit", width=90, fg_color="#1a1a1a", command=lambda idx=i: self.start_edit(idx)).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="✕ Delete", width=90, fg_color="#111111", hover_color="#1d1d1d", command=lambda idx=i: self.delete_task(idx)).pack(side="left", padx=4)

    def toggle_task(self, i):
        self.tasks[i]["done"] = not self.tasks[i]["done"]
        save_tasks(self.tasks)
        self.refresh()

    def start_edit(self, i):
        self.entry.delete(0, "end")
        self.entry.insert(0, self.tasks[i]["title"])
        self.priority_var.set(self.tasks[i].get("priority", "Medium"))
        self.edit_index = i
        self.add_btn.configure(text="Save")

    def delete_task(self, i):
        self.tasks.pop(i)
        save_tasks(self.tasks)
        self.refresh()


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
