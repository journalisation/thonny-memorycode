MODULE_NAME = "memorycode"

import os
from thonny import get_workbench, get_shell
from tkinter.messagebox import showinfo, showerror
from tkinter.simpledialog import askstring
from thonnycontrib.memorycode.memorycodeView import MemorycodeView
from thonnycontrib.memorycode.memorycode import Memorycode
from queue import Queue

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


memorycode = None
current_directory = None
output_queue = None

def info(memorycode):
    current_tab = get_workbench().get_editor_notebook().get_current_editor()
    showinfo(MODULE_NAME, eval(askstring(MODULE_NAME, "Entrez votre demande")))


#    showinfo(MODULE_NAME, get_current_file_directory())
#    showinfo(MODULE_NAME, str(dir(get_workbench().get_editor_notebook().get_current_editor())))

#    showinfo(MODULE_NAME, "Changed" if memorycode.repo.index.diff("HEAD") else "no change")
# showinfo(MODULE_NAME, str(repo.active_branch.name))


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

def save(message="commit from Thonny"):
    editor = get_workbench().get_editor_notebook().get_current_editor()
    editor.save_file()
    memorycode.save(askstring(MODULE_NAME, "Entrez le nom de votre sauvegarde"))
    get_workbench().get_view("MemorycodeView").from_saves(memorycode.get_saves())

def load(branch_name=None):
    memorycode.load(branch_name)
    get_workbench().get_view("MemorycodeView").from_saves(memorycode.get_saves())

def show_view(arg):
    global memorycode
    if arg.view_id == "MemorycodeView":
        get_workbench().get_view("MemorycodeView").from_saves(memorycode.get_saves())

def switch_tab(arg):
    global memorycode
    global current_directory
    new_dir = get_current_file_directory()
    if new_dir and current_directory != new_dir and os.path.isfile(f"{new_dir}/.memorycode"):
        memorycode.set_directory(path=get_current_file_directory())
        load()
        current_directory = get_current_file_directory()

def periodic_output_check():
    global output_queue
    if not output_queue.empty():
        showinfo(MODULE_NAME, output_queue.get())
    get_workbench().get_view("MemorycodeView").from_saves(memorycode.get_saves())
    current_project = memorycode.get_current_project_name()
    get_workbench().get_view("MemorycodeView").set_projects_list(memorycode.get_projects(), current_project, lambda x : showinfo(MODULE_NAME, str(x)))

    get_workbench().after(100, periodic_output_check)

def print_to_shell(str, stderr=False):
    text = get_shell().text
    text._insert_text_directly(str, ("io", "stderr") if stderr else ("io",))
    text.see("end")

def print_error(*args):
    get_shell().print_error(" ".join([str(arg) for arg in args]))


def load_plugin():
    global memorycode
    global output_queue
    output_queue = Queue()
    # unload function
    get_workbench().bind("WorkbenchClose", unload_plugin, True)

    # init_module()
    workbench = get_workbench()
    #memorycode = Memorycode(output=lambda x: workbench.event_generate("MemorycodeOutput", message="message " + x))
    #memorycode = Memorycode(output=lambda x: workbench.after(0, lambda : showinfo(MODULE_NAME, x)))
    memorycode = Memorycode(output=lambda x: output_queue.put(x))
    workbench.add_command(command_id="info",
                          menu_name="tools",
                          command_label="info",
                          handler=lambda: info(memorycode))
    workbench.add_command(command_id="save",
                          menu_name="tools",
                          command_label="sauvegarde",
                          handler=save)
    workbench.add_command(command_id="project",
                          menu_name="tools",
                          command_label="projet",
                          handler=lambda: load(
                              askstring(MODULE_NAME, "Entrez le nom de votre projet")))

    # workbench.bind("WorkbenchClose", before_running)
    # workbench.bind("NewFile", lambda arg: showinfo("new", arg))
    # workbench.bind("RunFile", lambda arg: showinfo("run1", arg))
    # workbench.bind("Save", lambda x: memorycode.save())
    # workbench.bind("RemoteFilesChanged", lambda arg: showinfo("run3", arg))
    workbench.bind("ShowView", show_view)
    workbench.bind("<<NotebookTabChanged>>", switch_tab)
    #workbench.bind("MemorycodeOutput", message)
    # workbench.bind("<<TextChange>>", lambda arg: showinfo("run4", arg))
    #lambda arg: showinfo("run3", f"{arg.keycode} {arg.num} {arg.widget} {arg.state}"))
    # create a panel in ui


    workbench.add_view(MemorycodeView, "Memorycode", "se")
    get_workbench().after(100, periodic_output_check)


def unload_plugin(event=None):
    global memorycode
   # showinfo("run4", "arg")
    try:
        memorycode.save()
    except Exception as e:
        showinfo("run4", str(e))
