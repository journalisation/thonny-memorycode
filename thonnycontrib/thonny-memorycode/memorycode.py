from git import Repo, exc
import os

class Memorycode:
    def __init__(self, path=None, output=lambda x:x):
        self.output = output
        try:
            if path == None:
                self.repo = Repo(search_parent_directories=True)
            else:
                self.repo = Repo(path)
                
        except exc.InvalidGitRepositoryError:
            self.repo = None
            
    def save(self, message="commit from Thonny"):
        self.__commit(message)
        self.__push_with_ssh(".ssh/id_ed25519")
      #  self.__push_with_http("ja-edu", "Ejp45314531$")
    
    def list_save(self):
        if self.repo is not None:
            commits = list(self.repo.iter_commits())
            for commit in commits:
                self.output(commit.hexsha[-8:] + "  " + commit.message)

    
    def git_diagnostic(self):
        if self.repo is not None:
            try:
                self.output("Repo:", self.repo)
                self.output("Remote:", self.repo.remotes)
            except Exception as e:
                self.output("No git" + str(e))
    
    def __commit(self, commit_message):
        if self.repo is not None:
            try:
                self.repo.git.add('--all')
                self.repo.index.commit(commit_message)
                self.output("Code committed successfully.")
            except Exception as e:
                self.output("Failed to commit code " + str(e))

    def __push_with_ssh(self,ssh_key_path):
        if self.repo is not None and self.repo.remotes:
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


if __name__ == "__main__":
    memorycode = Memorycode(path="./test",output=print)
    memorycode.create_and_checkout_branch("essai")
    memorycode.git_diagnostic()
    memorycode.list_save()
    memorycode.save()
    memorycode.list_save()