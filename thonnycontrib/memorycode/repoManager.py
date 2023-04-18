from threading import Thread
from time import time, sleep
from queue import Queue

class RepoManager(Thread):
    def __init__(self, repo, output=lambda x: x, autosave=True):
        super().__init__()
        self.repo = repo
        self.output = output
        self.autosave = autosave
        self.ssh_key_path = str(repo.working_dir).replace("\\", "/") + "/.ssh/id_ed25519" # git needs forward slashes
        self.task_queue = Queue()

    def run(self):
        t_commit = time()
        t_remote = time()
        while True:
            sleep(1)
            if self.autosave and time() - t_commit > 60:
                #self.__commit()
                t_commit = time()
            if time() - t_remote > 60:
                #self.__push()
                t_remote = time()

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
                        self.__checkout(task[1])
                    self.task_queue.task_done()
                except Exception as e:
                    self.output("Task failed: " + str(e))

    def commit(self, commit_message):
        self.output("Committing code...")
        self.task_queue.put(["commit", commit_message])

    def push(self):
        self.task_queue.put(["push"])

    def pull(self, branch_name):
        self.task_queue.put(["pull", branch_name])

    def fetch(self):
        self.task_queue.put(["fetch"])

    def checkout(self, branch_name):
        self.task_queue.put(["checkout", branch_name])

    def is_busy(self):
        return not self.task_queue.empty() and self.task_queue.unfinished_tasks == 0

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
            branches = list(dict.fromkeys(branches)) # Remove duplicates
            branches.sort()
            return  branches

    def iter_commits(self):
        if self.repo is not None:
            return self.repo.iter_commits()

    def __get_active_branch(self):
        return self.repo.active_branch

    def __get_branches(self):
        return self.repo.references

    def __commit(self, commit_message):
        if self.repo is not None and self.get_branch_name() and self.repo.head.commit.diff(None):
            try:
                self.repo.git.add('--all')
                self.repo.index.commit(commit_message)
                self.output("Code committed successfully.")
            except Exception as e:
                self.output("Failed to commit code " + str(e))
            return True
        return False

    def __push(self):
        if self.repo is not None and self.repo.remotes:
            if self.get_branch_name():
                # Important not to check for known_hosts
                ssh_command = f"ssh -v -i {self.ssh_key_path} -o StrictHostKeyChecking=no"
                #  os.system("ssh-agent bash -c 'ssh-add .ssh/id_ed25519 ; git push '")
                with self.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_command):
                    self.repo.remote().push(refspec=self.repo.head.reference)
                    self.output("Pushed successfully.")

    def __pull(self, branch_name):
        if self.repo is not None and self.repo.remotes:
            if "origin/" + str(branch_name) in self.repo.references:
                # Important not to check for known_hosts
                ssh_command = f"ssh -v -i {self.ssh_key_path} -o StrictHostKeyChecking=no"
                with self.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_command):
                    self.repo.remote().pull(refspec=branch_name)
                    self.output("Pulled successfully.")

    def __fetch(self):
        if self.repo is not None and self.repo.remotes:
            # Important not to check for known_hosts
            ssh_command = f"ssh -v -i {self.ssh_key_path} -o StrictHostKeyChecking=no"
            with self.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_command):
                self.repo.remote().fetch()


    def __checkout(self, branch_name):
        if self.repo is not None:
            # Check if the branch already exists
            if branch_name in self.repo.branches:
                # Branch exists, checkout
                self.repo.git.checkout(branch_name)
                return
            elif "origin/" + str(branch_name) in self.repo.references:
                # Branch exists on remote, checkout
                self.repo.git.checkout("origin/" + branch_name)
            # Branch does not exist yet, create it and checkout
            self.repo.git.branch(branch_name)
            self.repo.git.checkout(branch_name)

