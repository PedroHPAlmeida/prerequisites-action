import os
from typing import Dict, Any, Union, Tuple, List

import json
import requests

GITHUB_API_URL = os.environ.get('GITHUB_API_URL', 'https://api.github.com')
GITHUB_TOKEN = os.environ.get('INPUT_GITHUB_TOKEN', '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')


def make_request(
    path: str, http_method: str, payload: Dict[str, Any] = {}, headers: Union[Dict[str, Any], None] = {}
) -> Tuple[Dict[str, Any], int]:
    headers = {
        **headers,
        'accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    response = requests.request(http_method, f'{GITHUB_API_URL}/{path}', data=json.dumps(payload), headers=headers)
    return response.json(), response.status_code


def create_repository_variable(owner: str, repo: str, variable_name: str, variable_value: str) -> None:
    make_request(f'repos/{owner}/{repo}/actions/variables', 'POST', {'name': variable_name, 'value': variable_value})


def get_branch(owner: str, repo: str, branch: str) -> Dict[str, str]:
    body, status = make_request(f'repos/{owner}/{repo}/git/refs/heads/{branch}', 'GET')
    if status != 200:
        raise Exception(f'Branch {branch} not found')
    return {'ref': body['ref'], 'sha': body['object']['sha'], 'url': body['object']['url']}


def create_branch(owner: str, repo: str, branch: str, from_branch: str) -> None:
    from_branch_sha = get_branch(owner, repo, from_branch)['sha']
    _, status = make_request(
        f'repos/{owner}/{repo}/git/refs', 'POST', {'ref': f'refs/heads/{branch}', 'sha': from_branch_sha}
    )
    if status != 201:
        raise Exception(f'Branch {branch} already exists')


def create_branchs(owner: str, repo: str, branches: List[str], from_branch: str) -> None:
    for branch in branches:
        try:
            create_branch(owner, repo, branch, from_branch)
        except Exception as ex:
            print(ex)


def protect_branch(owner: str, repo: str, branch: str):
    body, status = make_request(
        f'repos/{owner}/{repo}/branches/{branch}/protection',
        'PUT',
        {
            'required_status_checks': None,
            'enforce_admins': False,
            'required_pull_request_reviews': {'dismiss_stale_reviews': True, 'require_code_owner_reviews': False},
            'restrictions': None,
        },
    )
    if status != 200:
        raise Exception(f'Error setting branch {branch} protection: {status} - {body}')


def protect_branchs(owner: str, repo: str, branches: str) -> None:
    for branch in branches:
        protect_branch(owner, repo, branch)
