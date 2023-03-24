MODULE_NAME = "memorycode"

import os
from thonny import get_workbench
from tkinter.messagebox import showinfo, showerror
from tkinter.simpledialog import askstring
from thonnycontrib.memorycode.memorycodeView import MemorycodeView
from git import Repo, exc


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


# from memorycode import Memorycode

class Memorycode:
    def __init__(self, output=lambda x: x):
        self.repo = None
        self.output = output

    def set_directory(self, path=None):
        try:
            if path is None:
                self.repo = Repo(search_parent_directories=True)
            else:
                self.repo = Repo(path)

        except exc.InvalidGitRepositoryError:
            self.output("No repository set.")

    def save(self, message="commit from Thonny"):
        self.__commit(message)
        self.__push_with_ssh(".ssh/id_ed25519")

    def list_save(self):
        if self.repo is not None:
            commits = list(self.repo.iter_commits())
            for commit in commits:
                self.output(commit.hexsha[-8:] + "  " + commit.message)

    # Return name of current project (= git branch if not main), else None
    def get_current_project_name(self):
        if self.repo is not None:
            return self.__get_active_branch() if self.__get_active_branch() != "main" else None

    def git_diagnostic(self):
        if self.repo is not None:
            try:
                self.output("Repo:", self.repo)
                self.output("Remote:", self.repo.remotes)
            except Exception as e:
                self.output("No git" + str(e))

    def __get_active_branch(self):
        return self.repo.active_branch

    def __commit(self, commit_message):
        if self.repo is not None and self.get_current_project_name() and memorycode.repo.head.commit.diff(None):
            try:
                self.repo.git.add('--all')
                self.repo.index.commit(commit_message)
                self.output("Code committed successfully.")
            except Exception as e:
                self.output("Failed to commit code " + str(e))

    def __push_with_ssh(self, ssh_key_path):
        if self.repo is not None and self.repo.remotes:
            if self.get_current_project_name():
                # Important not to check for known_hosts
                ssh_command = f"ssh -v -i {ssh_key_path} -o StrictHostKeyChecking=no"
                #  os.system("ssh-agent bash -c 'ssh-add .ssh/id_ed25519 ; git push '")
                with self.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_command):
                    self.repo.remote().push(refspec=self.repo.head.reference)
                    self.output("Pushed successfully.")

    def create_and_checkout_branch(self, branch_name):
        if self.repo is not None:
            # Vérifier si la branche existe déjà
            if branch_name in self.repo.branches:
                # La branche existe, checkout
                self.repo.git.checkout(branch_name)
            else:
                # La branche n'existe pas, la créer et checkout
                self.repo.git.branch(branch_name)
                self.repo.git.checkout(branch_name)


memorycode = None


def info(memorycode):
    current_tab = get_workbench().get_editor_notebook().get_current_editor()
    showinfo(MODULE_NAME, eval(askstring(MODULE_NAME, "Entrez le nom de votre projet")))


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


def before_running():
    showinfo(MODULE_NAME, "before_running")
    # commit_code()


def save(message="commit from Thonny"):
    editor = get_workbench().get_editor_notebook().get_current_editor()
    editor.save_file()
    memorycode.save(message)


def load_plugin():
    global memorycode
    # unload function
    get_workbench().bind("WorkbenchClose", unload_plugin, True)

    # init_module()
    memorycode = Memorycode(output=lambda x: showinfo(MODULE_NAME, x))
    workbench = get_workbench()
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
                          handler=lambda: memorycode.create_and_checkout_branch(
                              askstring(MODULE_NAME, "Entrez le nom de votre projet")))

    # workbench.bind("WorkbenchClose", before_running)
    # workbench.bind("NewFile", lambda arg: showinfo("new", arg))
    # workbench.bind("RunFile", lambda arg: showinfo("run1", arg))
    # workbench.bind("Save", lambda x: memorycode.save())
    # workbench.bind("RemoteFilesChanged", lambda arg: showinfo("run3", arg))
    workbench.bind("<<NotebookTabChanged>>", lambda x: memorycode.set_directory(path=get_current_file_directory()))
    # workbench.bind("<<TextChange>>", lambda arg: showinfo("run4", arg))
    #lambda arg: showinfo("run3", f"{arg.keycode} {arg.num} {arg.widget} {arg.state}"))
    # create a panel in ui


    workbench.add_view(MemorycodeView, "Memorycode", "se")

def unload_plugin(event=None):
    global memorycode
    showinfo("run4", "arg")
    try:
        memorycode.save()
    except Exception as e:
        showinfo("run4", str(e))
