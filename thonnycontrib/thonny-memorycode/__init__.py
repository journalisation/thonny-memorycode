from thonny import get_workbench
from tkinter.messagebox import showinfo, showerror
from memorycode import Memorycode
import os

MODULE_NAME = "memorycode"

def commit():
    try:
        repo = git.Repo(search_parent_directories=True)
        repo.git.add('--all')
        repo.index.commit("commit from Thonny")
        showinfo("MODULE_NAME", "Code committed successfully.")
    except Exception as e:
        showerror("Failed to commit code", str(e))


def info():
    current_tab = get_workbench().get_editor_notebook().get_current_editor()
    showinfo(MODULE_NAME, get_current_file_directory())
#    showinfo(MODULE_NAME, str(repo))
#showinfo(MODULE_NAME, str(repo.active_branch.name))


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


def switch_tab():
    showinfo(MODULE_NAME, "New tab")

def before_running():
    showinfo(MODULE_NAME, "before_running")
    # commit_code()


def load_plugin():
    #init_module()
    workbench = get_workbench()
    workbench.add_command(command_id="info",
                          menu_name="tools",
                          command_label="info",
                          handler=info)
    workbench.add_command(command_id="git",
                          menu_name="tools",
                          command_label="git",
                          handler=commit)

    workbench.bind("WorkbenchClose", before_running)
    workbench.bind("NewFile", lambda arg: showinfo("new", arg))
    workbench.bind("RunFile", lambda arg: showinfo("run1", arg))
    workbench.bind("Save", lambda arg: showinfo("run2", arg))
    workbench.bind("RemoteFilesChanged", lambda arg: showinfo("run3", arg))
    workbench.bind("<<NotebookTabChanged>>", lambda arg: showinfo("run4", arg))
    # workbench.bind("<<TextChange>>", lambda arg: showinfo("run4", arg))

