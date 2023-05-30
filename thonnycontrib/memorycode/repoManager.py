from threading import Thread
from time import time, sleep
from queue import Queue


class RepoManager(Thread):
    def __init__(self, repo, output=lambda x: x, autosave=True):
        super().__init__()
        self.repo = repo
        self.output = output
        self.autosave = autosave
        self.ssh_key_path = str(repo.working_dir).replace("\\", "/") + "/.ssh/id_ed25519"  # git needs forward slashes
        self.task_queue = Queue()
        self.errors = []
        self.commits = list(self.repo.iter_commits())

    def run(self):
        t_autosave = time()

        while True:
            sleep(1)
            if self.autosave and (time() - t_autosave > 60):
                self.commit()
                self.__push()
                t_autosave = time()

            while not self.task_queue.empty():
                task = self.task_queue.get()
                try:
                    if task[0] == "commit":
                        self.__commit(task[1])
                    elif task[0] == "push":
                        self.__push()
                    elif task[0] == "pull":
                        self.__pull(task[1])
                    elif task[0] == "fetch":
                        self.__fetch()
                    elif task[0] == "checkout":
                        self.__checkout(task[1], task[2])
                    elif task[0] == "stop":
                        self.task_queue.task_done()
                        return
                except Exception as e:
                    self.output("Task failed: " + str(e))

                self.commits = list(self.repo.iter_commits())  # TODO improve the efficiency (0.2s each call)
                self.task_queue.task_done()

    def commit(self, commit_message=None):
        self.output("Committing code...")
        self.task_queue.put(["commit", commit_message])

    def push(self):
        self.task_queue.put(["push"])

    def pull(self, branch_name):
        self.task_queue.put(["pull", branch_name])

    def fetch(self):
        self.task_queue.put(["fetch"])

    def checkout(self, branch_name, create_if_not_exists=False):
        self.task_queue.put(["checkout", branch_name, create_if_not_exists])

    def is_busy(self):
        return (not self.task_queue.empty()) or (self.task_queue.unfinished_tasks != 0)

    # Return name of current project (= git branch if not main), else None
    def get_branch_name(self):
        if self.repo is not None:
            return str(self.__get_active_branch()) if str(self.__get_active_branch()) != "main" else None

    # Return name of current branches
    def get_branches(self):
        if self.repo is not None:
            branches = [str(b) for b in self.__get_branches()]
            branches = [b for b in branches if not str(b).endswith("main") and not str(b).endswith("HEAD")]
            branches = [b.split("/")[-1] if b.startswith("origin/") else b for b in branches]
            branches = list(dict.fromkeys(branches))  # Remove duplicates
            branches.sort()
            return branches

    def iter_commits(self):
        if self.repo is not None:
            return self.commits

    def diagnostic(self):
        diag = []
        if self.repo is None:
            diag += ["no_repo"]
        if self.get_branch_name() is None:
            diag += ["no_project"]
        # if self.repo.head.commit.diff(None) or self.repo.untracked_files:# or self.repo.is_dirty():
        #    diag += ["dirty"]
        if self.is_busy():
            diag += ["busy"]
        return diag

    def stop(self):
        self.task_queue.put(["stop"])

    def __get_active_branch(self):
        return self.repo.active_branch

    def __get_branches(self):
        return self.repo.references

    def __commit(self, commit_message):
        if self.repo is None:
            return False
        if not (commit_message or self.repo.head.commit.diff(
                None) or self.repo.untracked_files or self.repo.is_dirty()):
            return False
        if self.get_branch_name() is None:
            self.output("Cannot commit to main branch.")
            return False
        try:
            self.repo.git.add('--all')
            self.repo.index.commit(commit_message if commit_message else "autosave")
            self.output("Code committed successfully.")
        except Exception as e:
            self.output("Failed to commit code " + str(e))
        return True

    def __push(self):
        if self.repo is not None and self.repo.remotes:
            if self.get_branch_name():
                # Important not to check for known_hosts
                ssh_command = f"ssh -v -i {self.ssh_key_path} -o StrictHostKeyChecking=no"
                #  os.system("ssh-agent bash -c 'ssh-add .ssh/id_ed25519 ; git push '")
                with self.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_command):
                    self.repo.remote().push(refspec=self.repo.head.reference)
                    self.output("Pushed successfully.")
            else:
                self.output("Cannot push to main branch.")
        else:
            self.output("No remote repository.")

    def __pull(self, branch_name):
        if self.repo is not None and self.repo.remotes:
            if "origin/" + str(branch_name) in self.repo.references:
                # Important not to check for known_hosts
                ssh_command = f"ssh -v -i {self.ssh_key_path} -o StrictHostKeyChecking=no"
                with self.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_command):
                    self.repo.remote().pull(refspec=branch_name)
                    self.output("Pulled successfully.")
            else:
                self.output("Cannot pull from main branch.")
                self.__fetch()
        else:
            self.output("No remote repository.")

    def __fetch(self):
        if self.repo is not None and self.repo.remotes:
            # Important not to check for known_hosts
            ssh_command = f"ssh -v -i {self.ssh_key_path} -o StrictHostKeyChecking=no"
            with self.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_command):
                self.repo.remote().fetch()
        else:
            self.output("No remote repository.")

    # Checkout branch in local or remote, create if create_if_not_exists is True and branch does not exist
    def __checkout(self, branch_name, create_if_not_exists=False):
        if self.repo is not None:
            # Check if the branch already exists
            if branch_name in self.repo.branches:
                # Branch exists, checkout
                self.repo.git.checkout(branch_name)
            elif "origin/" + str(branch_name) in self.repo.references:
                # Branch exists on remote, checkout
                self.repo.git.checkout("-b", branch_name, "origin/" + branch_name)
            elif create_if_not_exists:
                # Branch does not exist yet, create it and checkout
                self.repo.git.branch(branch_name)
                self.repo.git.checkout(branch_name)
            else:
                self.output("Branch does not exist.")
        else:
            self.output("No repository.")


class EmptyRepoManager:
    def __init__(self, repo, output=lambda x: x, autosave=True):
        self.output = output

    def commit(self, commit_message):
        pass

    def push(self):
        pass

    def pull(self, branch_name):
        pass

    def fetch(self):
        pass

    def checkout(self, branch_name, create_if_not_exists=False):
        pass

    def is_busy(self):
        return False

    def get_branch_name(self):
        return None

    def get_branches(self):
        return []

    def iter_commits(self):
        return []

    def diagnostic(self):
        return ["no_repo"]