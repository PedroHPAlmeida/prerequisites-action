from unittest.mock import MagicMock, patch, call

import pytest

import src.github as github


def test_make_request(mock_requests, mock_response, mock_json):
    mock_json.dumps = MagicMock(return_value='{"data": "anything"}')
    mock_requests.request = MagicMock(return_value=mock_response)

    path = 'path/to/anything'
    http_method = 'ANY'
    payload = {'data': 'anything'}
    response = github.make_request(path, http_method, payload)

    mock_json.dumps.assert_called_once_with(payload)
    mock_requests.request.assert_called_once_with(
        http_method,
        f'{github.GITHUB_API_URL}/{path}',
        data='{"data": "anything"}',
        headers={
            'accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {github.GITHUB_TOKEN}',
            'X-GitHub-Api-Version': '2022-11-28',
        },
    )
    assert response == (dict(), 200)


@patch('src.github.make_request')
def test_create_repository_variable(mock_make_request):
    owner = 'any'
    repo = 'repo-name'
    variable_name = 'any_variable'
    variable_value = 'any_variable_value'

    github.create_repository_variable(owner, repo, variable_name, variable_value)

    mock_make_request.assert_called_once_with(
        f'repos/{owner}/{repo}/actions/variables', 'POST', {'name': variable_name, 'value': variable_value}
    )


@patch('src.github.make_request')
def test_get_branch(mock_make_request, mock_get_branch_response_success):
    mock_make_request.return_value = mock_get_branch_response_success

    owner = 'any'
    repo = 'repo-name'
    branch = 'master'
    response = github.get_branch(owner, repo, branch)

    mock_body = mock_get_branch_response_success[0]
    expected = {'ref': mock_body['ref'], 'sha': mock_body['object']['sha'], 'url': mock_body['object']['url']}
    assert response == expected
    mock_make_request.assert_called_once_with(f'repos/{owner}/{repo}/git/refs/heads/{branch}', 'GET')


@patch('src.github.make_request')
def test_get_branch_that_doesnt_exist(mock_make_request):
    mock_make_request.return_value = (dict(), 404)

    with pytest.raises(Exception):
        github.get_branch('any', 'any', 'any')


@patch('src.github.get_branch')
@patch('src.github.make_request')
def test_create_branch(mock_make_request, mock_get_branch):
    mock_get_branch.return_value = {'sha': 'any-sha'}
    mock_make_request.return_value = (dict(), 201)

    owner = 'any'
    repo = 'repo-name'
    branch = 'develop'
    from_branch = 'master'
    github.create_branch(owner, repo, branch, from_branch)

    mock_get_branch.assert_called_once_with(owner, repo, from_branch)
    mock_make_request.assert_called_once_with(
        f'repos/{owner}/{repo}/git/refs', 'POST', {'ref': f'refs/heads/{branch}', 'sha': 'any-sha'}
    )


@patch('src.github.get_branch')
@patch('src.github.make_request')
def test_create_branch_that_already_exists(mock_make_request, mock_get_branch):
    mock_get_branch.return_value = {'sha': 'any-sha'}
    mock_make_request.return_value = (dict(), 400)

    with pytest.raises(Exception):
        github.create_branch('any', 'repo-name', 'branch-that-already-exists', 'master')


@patch('src.github.create_branch')
def test_create_branchs(mock_create_branch):
    owner = 'any'
    repo = 'repo-name'
    branches = ['develop', 'release', 'preprod']
    from_branch = 'master'
    github.create_branchs(owner, repo, branches, from_branch)

    assert mock_create_branch.call_count == len(branches)

    expected_calls = [call(owner, repo, branch, from_branch) for branch in branches]
    assert mock_create_branch.call_args_list == expected_calls


@patch('src.github.create_branch')
def test_create_branchs_that_already_exists(mock_create_branch):
    mock_create_branch.side_effect = Exception
    owner = 'any'
    repo = 'repo-name'
    branches = ['develop', 'release', 'branch-that-already-exists']
    from_branch = 'master'
    github.create_branchs(owner, repo, branches, from_branch)

    assert mock_create_branch.call_count == len(branches)

    expected_calls = [call(owner, repo, branch, from_branch) for branch in branches]
    assert mock_create_branch.call_args_list == expected_calls


@patch('src.github.make_request')
def test_protect_branch(mock_make_request):
    mock_make_request.return_value = (dict(), 200)

    owner = 'any'
    repo = 'repo-name'
    branch = 'master'

    github.protect_branch(owner, repo, branch)

    mock_make_request.assert_called_once_with(
        f'repos/{owner}/{repo}/branches/{branch}/protection',
        'PUT',
        {
            'required_status_checks': None,
            'enforce_admins': False,
            'required_pull_request_reviews': {'dismiss_stale_reviews': True, 'require_code_owner_reviews': False},
            'restrictions': None,
        },
    )


@patch('src.github.make_request')
def test_protect_branch_error(mock_make_request):
    mock_make_request.return_value = (dict(), 403)

    with pytest.raises(Exception):
        owner = 'any'
        repo = 'repo-name'
        branch = 'master'
        github.protect_branch(owner, repo, branch)


@patch('src.github.protect_branch')
def test_protect_branchs(mock_protect_branch):
    owner = 'any'
    repo = 'repo-name'
    branches = ['develop', 'release', 'preprod', 'master']

    github.protect_branchs(owner, repo, branches)

    mock_protect_branch.call_count == 4

    expected_calls = [call(owner, repo, branch) for branch in branches]

    assert mock_protect_branch.call_args_list == expected_calls
