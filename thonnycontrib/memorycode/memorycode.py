from git import Repo, exc
from thonnycontrib.memorycode.repoManager import RepoManager, EmptyRepoManager
from os import path as os_path


class Memorycode:
    def __init__(self, output=lambda x: x):
        self.output = output
        self.repo_manager = EmptyRepoManager(None, self.output)
        self.repo_managers = {}
    #    self.output("Memorycode loaded.")

    def set_directory(self, path=None):
        if not os_path.isfile(f"{path}/.memorycode"):
            self.repo_manager = EmptyRepoManager(None, self.output)
            self.output("Directory not tracked by Memorycode.")
        else:
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
                self.repo_manager = EmptyRepoManager(path, self.output)
                self.output("No repository set.")

    def save(self, message=None):
        if self.repo_manager is not None:
            self.repo_manager.commit(message)
            self.repo_manager.push()

    def load(self, branch_name=None):
        if self.repo_manager is not None:
            if branch_name is None:
                branch_name = self.get_current_project_name()
            self.repo_manager.checkout(branch_name)
            self.repo_manager
            self.repo_manager.pull(branch_name)

    def new_project(self, project_name):
        if self.repo_manager is not None:
            self.repo_manager.checkout("main")
            self.repo_manager.checkout(project_name, create_if_not_exists=True)

    def get_saves(self):
        if self.repo_manager is not None:
            commits = list(self.repo_manager.iter_commits())
            return commits
        #    for commit in commits:
        #        self.output(commit.hexsha[-8:] + "  " + commit.message)

    def get_current_project_name(self):
        if self.repo_manager is not None:
            return self.repo_manager.get_branch_name()

    def get_projects(self):
        if self.repo_manager is not None:
            return self.repo_manager.get_branches()


    def git_diagnostic(self):
        if self.repo_manager is not None:
            try:
                self.output("Repo:" + str(self.repo_manager.repo))
                self.output("Remote:" + str(self.repo_manager.repo.remotes))
            except Exception as e:
                self.output("No git" + str(e))

    def is_busy(self):
        return self.repo_manager.is_busy()

    def diagnostic(self):
        return self.repo_manager.diagnostic()

    def close(self, commit_msg=None):
        for repo_manager in self.repo_managers.values():
            if type(repo_manager) is RepoManager: # and not an EmptyRepoManager or None
                repo_manager.commit(commit_msg)
                repo_manager.push()
                repo_manager.stop()
                repo_manager.join()







if __name__ == "__main__":
    memorycode = Memorycode(output=print)
   # memorycode.create_and_checkout_branch("essai")
   # memorycode.git_diagnostic()
   # memorycode.list_save()
   # memorycode.save()
   # memorycode.list_save()
