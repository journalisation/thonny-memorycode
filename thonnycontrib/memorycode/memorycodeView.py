from tkinter import ttk, Canvas, Frame, Label, Scrollbar, Text, IntVar
from time import strftime, localtime

EMOJI_TIME = chr(128336)
EMOJI_OK = chr(10004)
EMOJI_ERROR = chr(9888)
EMOJI_UNSAVED = chr(128190)
EMOJI_DISCONNECTED = chr(128683)

class MemorycodeView (ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self._parent = parent

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.top_frame = ttk.Frame(self)
        self.top_frame.grid(row=0, column=0, sticky="nsew")
        combobox = ttk.Combobox(self.top_frame, state="readonly")
        combobox.grid(row=0, column=0, sticky="nsew")
        self.flags_label = ttk.Label(self.top_frame, text=" "*10)
        self.flags_label.grid(row=0, column=1, sticky="nsew")
        self.comm_label = ttk.Label(self.top_frame, text=" "*10)
        self.comm_label.grid(row=2, column=1, sticky="nsew")

        self.stop_tracking_var = IntVar()
        self.stop_tracking_checkbutton = ttk.Checkbutton(self.top_frame, text="suspendre suivi", variable=self.stop_tracking_var, state="disabled")
        self.stop_tracking_var.set(1) # 1 = checked, 0 = unchecked
        #self.stop_tracking_checkbutton.grid(row=1, column=0, sticky="ne")

        canvas = Canvas(self, bg="white")

        scrollbar = Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = Frame(canvas, bg="white")
        self.saves = None
        self.projects = None

     #   self.scrollable_frame.bind(
      #      "<Configure>",
       #     lambda e: canvas.configure(
        #        scrollregion=canvas.bbox("all")
         #   )
        #)

#        self.scrollable_frame.update_idletasks()  # Update frame info before adding it to canvas
        canvas.create_window((0, 0), anchor="nw", window=self.scrollable_frame)
     #   canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=0, sticky="nse")

        #self.from_saves([i for i in range(50)])

    def set_projects_list(self, projects, active=None, callback=None):
        if self.projects != projects:
            self.projects = projects
            self.top_frame.children["!combobox"].config(values=projects)
        if active is not None:
            if type(active) == int:
                self.top_frame.children["!combobox"].current(active)
            elif type(active) == str:
                self.top_frame.children["!combobox"].current(projects.index(active))
        elif len(projects) > 0:
            self.top_frame.children["!combobox"].set("Select project")
        else:
            self.top_frame.children["!combobox"].set("No projects")
        if callback is not None:
            self.top_frame.children["!combobox"].bind("<<ComboboxSelected>>", lambda x : callback(self.top_frame.children["!combobox"].get()))

    def from_saves(self, saves):
        if self.saves == saves:
            return
        self.saves = saves
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        same_save_count = 0
        text = None
        string = ""
        for i in range(len(saves)):
            if(i == 0 or
                    ((saves[i].summary != saves[i-1].summary and saves[i].summary != "autosave")
                     or (saves[i].committer.name != saves[i-1].committer.name)
                     or (strftime("%d %b %Y", localtime(saves[i].committed_date)) != strftime("%d %b %Y", localtime(saves[i-1].committed_date))))):
                rect = Canvas(self.scrollable_frame, bg="blue", height=50)
                rect.grid(row=i, column=0, sticky="nsew")
                rect.bind("<1>", lambda x : print(x))
                text = Text(rect, fg="white", bg="blue", height=rect.winfo_height()*3)
                string = saves[i].summary + "\n" + saves[i].committer.name + "\n" + strftime("%a, %d %b %Y %H:%M", localtime(saves[i].committed_date))
                text.insert("1.0", string)
                text.config(state=('disabled' if i != 0 else 'normal'), cursor=('arrow' if i != 0 else 'xterm'))
                text.save = saves[i]
                #text.bindtags(tuple(list(text.bindtags()).insert(1, rect)))
                if i != 0:
                    text.bind("<1>", lambda x : print(str(x.widget.save.hexsha) + "  " + str(x) + '\n' + '\n'.join(map(str, [x.num, x.widget, x.widget.get(2.0, '2.end')]))))
                text.grid(row=0, column=0, sticky="nw")
                #label.place(relx=0.5, rely=0.5, anchor="center")

                rect.columnconfigure(1, weight=1)
                rect.rowconfigure(1, weight=1)
                same_save_count = 0
            else:
                same_save_count += 1
                text.config(state='normal')
                text.delete("1.0", "end")
                text.insert("1.0", string + "    " + (str(same_save_count + 1) + " saves"))
                text.config(state='disabled')

    def display_flags(self, flags):
        text = self.flags_label.cget("text")
        text = " " if not ("busy" in flags) else (EMOJI_TIME if ord(text[0]) < ord(EMOJI_TIME) or ord(text[0]) > ord(EMOJI_TIME) + 11 else chr(ord(text[0]) + 1))
        if "no_repo" in flags:
            text += EMOJI_ERROR + " Dossier non initialisé"
        elif "no_project" in flags:
            text += EMOJI_ERROR + " Projet non sélectionné"
        elif "dirty" in flags:
            text += EMOJI_UNSAVED + " Changements en cours"
        elif "busy" not in flags:
            text += EMOJI_OK
        self.flags_label.config(text=text)

    def display_communication(self, comm):
        self.comm_label.config(text=comm)

    def stop_tracking(self):
        return "selected" in self.stop_tracking_checkbutton.state()

    def untrackable(self):
        self.stop_tracking_checkbutton.state(["disabled"])
        self.stop_tracking_var.set(1)

    def trackable(self):
        self.stop_tracking_checkbutton.state(["!disabled"])
        self.stop_tracking_var.set(0)




if __name__ == "__main__":
    # For testing
    from tkinter import Tk
    from time import time
    root = Tk()
    root.geometry("400x400")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    memorycode = MemorycodeView(root)
    memorycode.grid(row=0, column=0, sticky="nsew")
    class FakeAuthor:
        def __init__(self, name):
            self.name = name
    class FakeCommit:
        def __init__(self, message, hexsha="1234567890abcdef1234567890abcdef12345678"):
            self.message = message
            self.committed_date = time()
            self.committer = FakeAuthor("Harold")
            self.summary = message
            self.hexsha = hexsha
    memorycode.from_saves([FakeCommit(f"summary {i}", i) for i in range(50)])
    projects = ["Project 1", "Project 2", "Project 3"]
    memorycode.set_projects_list(projects, projects.index("Project 2"))

    root.mainloop()