import subprocess as sp
import sys
import os
import shutil
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoLoader(object):
    """Base class for automatic loaders (e.g. Git)"""
    pass

class Git(AutoLoader):
    def __init__(self, url, path, git_bin = '/usr/bin/git', import_as=None, branch=None):
        """Creates a temporary directory full of a git repo.
        args::
            url: .git url for the repository
            path: where to clone the repo to
            
        kwargs:
            git_bin: override location of git binary. Must be >1.9
            import_as: Override default repo folder name
            branch: name of the branch to clone (default master)"""

        self.url = url
        self.path = path
        logger.info("Importing Cagliari tools from {} using git".format(self.url))

        #find the name of the working copy top level folder
        if not import_as:
            repo_folder_name = url.split('/')[-1].split('.')[0]
        else:
            repo_folder_name = import_as

        #build absolute path to working copy
        repo_folder_path = (os.path.join(path, repo_folder_name))
        logger.debug("Importing as {} ".format(repo_folder_path))

        #if this has already been cloned, pull latest version instead
        if os.path.exists(repo_folder_path):
            git_cmd = '{git} -C {dir} pull origin '.format(
                    dir=repo_folder_path,
                    git=git_bin).split(' ')
            if not branch:
                git_cmd.append('master')
            else:
                git_cmd.append(branch)
        
        #clone a clean working copy of the repo if folder does not exist
        else:
            git_cmd ="{git} -C {dir} clone {url}".format(
                    git=git_bin,
                    dir=self.path, 
                    url=self.url).split(" ") 
            if import_as is not None:
                git_cmd.append(import_as)
            if branch is not None:
                git_cmd.extend(["-b", branch])

        logger.debug(' '.join(['Executing:'] + git_cmd))
        sp.check_call(git_cmd)


if __name__ == "__main__":

    #parameters for remote origin url, tools path and git executable
    git_bin = '/cvmfs/sft.cern.ch/lcg/contrib/git/bin/git'
    url = 'https://github.com/alibenn/python-tools.git'

    path = os.environ['HOME']+'/.ca_tools/'

    if not os.path.exists(path):
            os.makedirs(path)
    
    git = Git(url, path, git_bin=git_bin)
    
    chmod_cmd = 'find {} -type f -iname "*.py" -exec chmod +x {{}} \;'.format(git.path).split(' ')
    logger.debug(' '.join(['Executing:'] + chmod_cmd))
    sp.check_call(chmod_cmd, shell=True)
