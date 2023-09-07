import os
from typing import Dict, Any, Union, Tuple, List

import json
import requests

GITHUB_API_URL = os.environ.get('GITHUB_API_URL')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')


def make_request(
    path: str, http_method: str, payload: Dict[str, Any] = {}, headers: Union[Dict[str, Any], None] = {}
) -> Tuple[Dict[str, Any], int]:
    headers = {**headers, 'accept': 'application/vnd.github+json', 'Authorization': f'Bearer {GITHUB_TOKEN}'}
    response = requests.request(http_method, f'{GITHUB_API_URL}/{path}', data=json.dumps(payload), headers=headers)
    return response.json(), response.status_code


def create_repository_variable(owner: str, repo: str, variable_name: str, variable_value: str) -> None:
    make_request(f'repos/{owner}/{repo}/actions/variables', 'POST', {'name': variable_name, 'value': variable_value})


def get_branch(owner: str, repo: str, branch: str) -> Dict[str, str]:
    body, status = make_request(f'repos/{owner}/{repo}/git/refs/heads/{branch}', 'GET')
    if status != 200:
        raise Exception('Branch not found')
    return {'ref': body['ref'], 'sha': body['object']['sha'], 'url': body['object']['url']}


def create_branch(owner: str, repo: str, branch: str, from_branch: str) -> None:
    from_branch_sha = get_branch(owner, repo, from_branch)['sha']
    make_request(f'repos/{owner}/{repo}/git/refs', 'POST', {'ref': f'refs/heads/{branch}', 'sha': from_branch_sha})


def create_branchs(owner: str, repo: str, branches: List[str], from_branch: str) -> None:
    for branch in branches:
        create_branch(owner, repo, branch, from_branch)


def protect_branch(owner: str, repo: str, branch: str):
    make_request(
        f'repos/{owner}/{repo}/branches/{branch}/protection',
        'PUT',
        {
            'required_status_checks': None,
            'enforce_admins': False,
            'required_pull_request_reviews': {'dismiss_stale_reviews': True, 'require_code_owner_reviews': False},
            'restrictions': None,
        },
    )


def protect_branchs(owner: str, repo: str, branches: str) -> None:
    for branch in branches:
        protect_branch(owner, repo, branch)
