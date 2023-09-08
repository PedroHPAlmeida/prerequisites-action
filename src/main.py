import os

import github


default_branch = os.getenv('INPUT_DEFAULT_BRANCH')
branches = os.getenv('INPUT_BRANCHES').split(',')
repo_owner, repo_name = os.getenv('INPUT_REPO').split('/')

print(f'Creating branchs: {branches}')
github.create_branchs(repo_owner, repo_name, branches, default_branch)

print('Defining branch protection')
github.protect_branchs(repo_owner, repo_name, [default_branch, *branches])

print('Defining application name to be used in other actions')
github.create_repository_variable(repo_owner, repo_name, 'APP_NAME', repo_name)

print('Success')
