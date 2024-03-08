MODULE_NAME = "memorycode"

import os
from thonny import get_workbench, get_shell
from tkinter.messagebox import showinfo, showerror
from tkinter.simpledialog import askstring
from thonnycontrib.memorycode.memorycodeView import MemorycodeView
from thonnycontrib.memorycode.memorycode import Memorycode
from queue import Queue
from time import time
from thonnycontrib.memorycode.log import add_to_file

# Git and GitPython localisation attempt
try:
    git_dir = [os.path.join(os.getcwd(), "PortableGit", "cmd"),
               os.path.join(os.getcwd(), "..", "PortableGit", "cmd"),
               os.path.join(os.getcwd(), "..", "Git", "cmd")]
    os.environ["PATH"] = os.pathsep.join(git_dir) + os.pathsep + os.environ["PATH"]
    from git import Repo
except ImportError as err:
    # [print(e, ".........", eval("err." + e)) for e in dir(err)]
    if err.msg.find("module") >= 0:
        showerror("MODULE_NAME", "GitPython is not installed.")
    elif err.msg.find("executable") >= 0:
        showerror("MODULE_NAME", "No git executable found.")


def get_current_file_directory():
    # Get the current editor notebook
    editor = get_workbench().get_editor_notebook().get_current_editor()
    if editor:
        # Get the filename of the current file
        filename = editor.get_filename()
        if filename:
            # Get the directory containing the file
            directory = os.path.dirname(filename)
            return directory


def print_to_shell(str, stderr=False):
    text = get_shell().text
    text._insert_text_directly(str, ("io", "stderr") if stderr else ("io",))
    text.see("end")


def print_error(*args):
    get_shell().print_error(" ".join([str(arg) for arg in args]))


class Manager:
    def __init__(self):
        self.current_directory = None
        self.output_queue = Queue()
        self.enabled = False
        self.memorycode = Memorycode(output=self.output_queue.put)

    def info(self):
        current_tab = get_workbench().get_editor_notebook().get_current_editor()
        showinfo(MODULE_NAME, eval(askstring(MODULE_NAME, "Entrez votre demande")))

    #    showinfo(MODULE_NAME, get_current_file_directory())
    #    showinfo(MODULE_NAME, str(dir(get_workbench().get_editor_notebook().get_current_editor())))

    #    showinfo(MODULE_NAME, "Changed" if memorycode.repo.index.diff("HEAD") else "no change")
    # showinfo(MODULE_NAME, str(repo.active_branch.name))

    def save(self):
        if self.enabled:
            editor = get_workbench().get_editor_notebook().get_current_editor()
            editor.save_file()
            save_name = askstring(MODULE_NAME, "Entrez le nom de votre sauvegarde")
            save_name = None if save_name == "" else save_name
            self.memorycode.save(save_name)
            get_workbench().get_view("MemorycodeView").from_saves(self.memorycode.get_saves())

    def load_project(self, branch_name=None):
        if self.enabled:
            self.memorycode.save()
            self.memorycode.load(branch_name)

    def new_project(self, name):
        if self.enabled:
            self.memorycode.save()
            self.memorycode.new_project(name)

    def show_view(self, arg):
        if arg.view_id == "MemorycodeView":
            get_workbench().get_view("MemorycodeView").from_saves(self.memorycode.get_saves())

    def switch_tab(self, arg):
        new_dir = get_current_file_directory()
        if new_dir and self.current_directory != new_dir:
            self.memorycode.set_directory(path=get_current_file_directory())
            self.memorycode.load()
            self.current_directory = get_current_file_directory()
            if self.memorycode.is_trackable():
                self.enabled = True
                get_workbench().get_view("MemorycodeView").trackable()
            else:
                self.enabled = False
                get_workbench().get_view("MemorycodeView").untrackable()

    def periodic_output_check(self):
        if get_workbench().get_view("MemorycodeView"):
            self.enabled = not get_workbench().get_view("MemorycodeView").stop_tracking()
        view = get_workbench().get_view("MemorycodeView")
        view.from_saves(self.memorycode.get_saves())
        current_project = self.memorycode.get_current_project_name()
        view.set_projects_list(self.memorycode.get_projects(), current_project, self.load_project)
        view.display_flags(self.memorycode.diagnostic())
        if not self.output_queue.empty():
            view.display_communication(self.output_queue.get())

        get_workbench().after(100, self.periodic_output_check)

    def periodic_file_save(self):
        if self.enabled:
            editor = get_workbench().get_editor_notebook().get_current_editor()
            if editor and not editor.check_for_external_changes():
                editor.save_file()
        get_workbench().after(1000, self.periodic_file_save)

    def close(self, event=None):
        try:
            self.memorycode.close()
            self.enabled = False
        except Exception as e:
            showinfo(MODULE_NAME, str(e))
            
    def text_inserted(self, event):
        if self.enabled:
            if 'shell' in str(event.text_widget): # in shell
                log_file =  os.path.join(self.current_directory, ".log")
            #    add_to_file(log_file, event.text)

def load_plugin():
    try:
        # init_module()
        workbench = get_workbench()

        # unload function
        workbench.bind("WorkbenchClose", manager.close, True)

        # memorycode = Memorycode(output=lambda x: workbench.event_generate("MemorycodeOutput", message="message " + x))
        # memorycode = Memorycode(output=lambda x: workbench.after(0, lambda : showinfo(MODULE_NAME, x)))
        workbench.add_command(command_id="info",
                              menu_name="tools",
                              command_label="info",
                              handler=manager.info)
        workbench.add_command(command_id="save",
                              menu_name="tools",
                              command_label="sauvegarde",
                              handler=manager.save)
        workbench.add_command(command_id="nouveau projet",
                              menu_name="tools",
                              command_label="projet",
                              handler=lambda: manager.new_project(
                                  askstring(MODULE_NAME, "Entrez le nom de votre projet")))

        # workbench.bind("WorkbenchClose", before_running)
        # workbench.bind("NewFile", lambda arg: showinfo("new", arg))
        workbench.bind("<<Run>>", lambda arg: showinfo("run1", arg))
        workbench.bind("<<RunFile>>", lambda arg: showinfo("run", arg))
        get_workbench().bind("TextInsert", manager.text_inserted)
        #get_workbench().bind("TextDelete", lambda arg: showinfo("text delete", arg))
        #workbench.bind("Runner", lambda arg: showinfo("run2", arg))
        # workbench.bind("WindowFocusIn", lambda arg: showinfo("run1", arg))
        # workbench.bind("Save", lambda x: memorycode.save())
        # workbench.bind("RemoteFilesChanged", lambda arg: showinfo("run3", arg))
        workbench.bind("ShowView", manager.show_view)
        workbench.bind("<<NotebookTabChanged>>", manager.switch_tab)
        # workbench.bind("MemorycodeOutput", message)
        # workbench.bind("<<TextChange>>", lambda arg: showinfo("run4", arg))
        # lambda arg: showinfo("run3", f"{arg.keycode} {arg.num} {arg.widget} {arg.state}"))
        # create a panel in ui

        workbench.add_view(MemorycodeView, "Memorycode", "se")
        get_workbench().after(100, manager.periodic_output_check)
        get_workbench().after(1000, manager.periodic_file_save)

    except Exception as e:
        showinfo(MODULE_NAME, str(e))

try:
    manager = Manager()

except Exception as e:
    showinfo(MODULE_NAME, str(e))