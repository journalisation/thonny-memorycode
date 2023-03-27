from git import Repo, exc

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
            pass
            #self.output("No repository set.")

    def save(self, message="commit from Thonny"):
        if self.__commit(message):
            self.__push_with_ssh(".ssh/id_ed25519")

    def load(self, branch_name=None):
        self.__fetch_with_ssh(".ssh/id_ed25519")
        if branch_name is None:
            branch_name = self.get_current_project_name()
        else:
            self.__create_and_checkout_branch(branch_name)
        self.__pull_with_ssh(".ssh/id_ed25519", branch_name)

    def get_saves(self):
        if self.repo is not None:
            commits = list(self.repo.iter_commits())
            return commits
        #    for commit in commits:
        #        self.output(commit.hexsha[-8:] + "  " + commit.message)

    # Return name of current project (= git branch if not main), else None
    def get_current_project_name(self):
        if self.repo is not None:
            return self.__get_active_branch() if str(self.__get_active_branch()) != "main" else None

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
        if self.repo is not None and self.get_current_project_name() and self.repo.head.commit.diff(None):
            try:
                self.repo.git.add('--all')
                self.repo.index.commit(commit_message)
                self.output("Code committed successfully.")
            except Exception as e:
                self.output("Failed to commit code " + str(e))
            return True
        return False

    def __push_with_ssh(self, ssh_key_path):
        if self.repo is not None and self.repo.remotes:
            if self.get_current_project_name():
                # Important not to check for known_hosts
                ssh_command = f"ssh -v -i {ssh_key_path} -o StrictHostKeyChecking=no"
                #  os.system("ssh-agent bash -c 'ssh-add .ssh/id_ed25519 ; git push '")
                with self.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_command):
                    self.repo.remote().push(refspec=self.repo.head.reference)
                    self.output("Pushed successfully.")

    def __pull_with_ssh(self, ssh_key_path, branch_name):
        if self.repo is not None and self.repo.remotes:
            if "origin/" + str(branch_name) in self.repo.references:
                # Important not to check for known_hosts
                ssh_command = f"ssh -v -i {ssh_key_path} -o StrictHostKeyChecking=no"
                with self.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_command):
                    self.repo.remote().pull(refspec=branch_name)
                    self.output("Pulled successfully.")

    def __fetch_with_ssh(self, ssh_key_path):
        if self.repo is not None and self.repo.remotes:
            # Important not to check for known_hosts
            ssh_command = f"ssh -v -i {ssh_key_path} -o StrictHostKeyChecking=no"
            with self.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_command):
                self.repo.remote().fetch()


    def __create_and_checkout_branch(self, branch_name):
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




if __name__ == "__main__":
    memorycode = Memorycode(path="./test",output=print)
    memorycode.create_and_checkout_branch("essai")
    memorycode.git_diagnostic()
    memorycode.list_save()
    memorycode.save()
    memorycode.list_save()
