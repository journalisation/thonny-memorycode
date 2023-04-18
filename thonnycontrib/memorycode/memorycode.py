from git import Repo, exc
from thonnycontrib.memorycode.repoManager import RepoManager


class Memorycode:
    def __init__(self, output=lambda x: x):
        self.repo_manager = None
        self.repo_managers = {}
        self.output = output
    #    self.output("Memorycode loaded.")

    def set_directory(self, path=None):
        try:
            if path is None:
                tmp_repo = Repo(search_parent_directories=True)
            else:
                tmp_repo = Repo(path, search_parent_directories=True)
            if tmp_repo.working_dir not in self.repo_managers:
                self.repo_managers[tmp_repo.working_dir] = RepoManager(tmp_repo, self.output)
                self.repo_managers[tmp_repo.working_dir].start()
            self.repo_manager = self.repo_managers[tmp_repo.working_dir]

        except exc.InvalidGitRepositoryError:
            pass
            #self.output("No repository set.")

    def save(self, message="commit from Thonny"):
        if self.repo_manager is not None:
            self.repo_manager.commit(message)

    def load(self, branch_name=None):
        if branch_name == None:
            branch_name = self.get_current_project_name()
        self.repo_manager.pull(branch_name)
        self.repo_manager.checkout(branch_name)

    def get_saves(self):
        if self.repo_manager is not None:
            commits = list(self.repo_manager.iter_commits())
            return commits
        #    for commit in commits:
        #        self.output(commit.hexsha[-8:] + "  " + commit.message)

    def get_current_project_name(self):
        if self.repo_manager is not None:
            return self.repo_manager.get_branch_name()


    def git_diagnostic(self):
        if self.repo_manager is not None:
            try:
                self.output("Repo:" + str(self.repo_manager.repo))
                self.output("Remote:" + str(self.repo_manager.repo.remotes))
            except Exception as e:
                self.output("No git" + str(e))








if __name__ == "__main__":
    memorycode = Memorycode(output=print)
   # memorycode.create_and_checkout_branch("essai")
   # memorycode.git_diagnostic()
   # memorycode.list_save()
   # memorycode.save()
   # memorycode.list_save()
