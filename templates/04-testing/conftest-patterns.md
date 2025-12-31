# Conftest.py Patterns

## Purpose

Document standardized pytest fixtures for testing skill scripts, including mock clients, sample data, and test utilities.

## Standard conftest.py Template

```python
"""
Pytest fixtures for {skill-name} tests.

Provides:
- Mock API client
- Sample response data
- Temporary file fixtures
- Configuration mocks
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import shutil
import json


# ============================================================================
# Mock Client Fixtures
# ============================================================================

@pytest.fixture
def mock_client():
    """
    Create a mock API client for testing.

    Usage in tests:
        def test_get_resource(mock_client):
            mock_client.get.return_value = {'id': '123', 'name': 'Test'}
            result = get_resource(client=mock_client, resource_id='123')
            assert result['name'] == 'Test'
    """
    client = MagicMock()

    # Default responses
    client.get.return_value = {}
    client.post.return_value = {}
    client.put.return_value = {}
    client.delete.return_value = None

    return client


@pytest.fixture
def mock_client_factory():
    """
    Factory for creating configured mock clients.

    Usage:
        def test_with_specific_response(mock_client_factory):
            client = mock_client_factory(get_response={'id': '123'})
            # Use client...
    """
    def create_client(
        get_response=None,
        post_response=None,
        put_response=None,
        delete_response=None,
        get_side_effect=None,
    ):
        client = MagicMock()
        client.get.return_value = get_response or {}
        client.post.return_value = post_response or {}
        client.put.return_value = put_response or {}
        client.delete.return_value = delete_response

        if get_side_effect:
            client.get.side_effect = get_side_effect

        return client

    return create_client


@pytest.fixture
def patch_get_client(mock_client):
    """
    Patch the get_client function to return mock client.

    Usage:
        def test_script(patch_get_client, mock_client, capsys):
            mock_client.get.return_value = {'id': '123'}
            # Run script...
    """
    with patch('config_manager.get_client', return_value=mock_client):
        yield mock_client


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_resource():
    """Sample resource response for testing."""
    return {
        'id': '12345',
        'name': 'Test Resource',
        'status': 'active',
        'createdAt': '2024-01-15T10:30:00Z',
        'updatedAt': '2024-01-15T14:45:00Z',
        'version': {
            'number': 1,
            'message': 'Initial version'
        },
        '_links': {
            'self': '/api/resources/12345',
            'webui': 'https://example.com/resources/12345'
        }
    }


@pytest.fixture
def sample_resource_list(sample_resource):
    """Sample list of resources for pagination testing."""
    return {
        'results': [
            {**sample_resource, 'id': str(i), 'name': f'Resource {i}'}
            for i in range(1, 6)
        ],
        '_links': {
            'next': '/api/resources?cursor=abc123'
        }
    }


@pytest.fixture
def sample_error_responses():
    """Sample API error responses for error handling tests."""
    return {
        '400': {'errors': [{'title': 'Bad Request', 'detail': 'Invalid input'}]},
        '401': {'message': 'Authentication required'},
        '403': {'message': 'You do not have permission'},
        '404': {'errors': [{'title': 'Not Found', 'detail': 'Resource not found'}]},
        '409': {'message': 'Version conflict'},
        '429': {'message': 'Rate limit exceeded'},
        '500': {'message': 'Internal server error'},
    }


# ============================================================================
# File and Directory Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """
    Create a temporary directory for tests.

    Automatically cleaned up after test.
    """
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp, ignore_errors=True)


@pytest.fixture
def temp_file(temp_dir):
    """
    Create a temporary file for tests.

    Returns a factory function for creating temp files.
    """
    def create_file(name: str, content: str = "") -> Path:
        file_path = temp_dir / name
        file_path.write_text(content)
        return file_path

    return create_file


@pytest.fixture
def sample_project(temp_dir):
    """
    Create a sample project structure for testing.

    Returns the project root path.
    """
    project_path = temp_dir / "Test-Skills"
    project_path.mkdir()

    # Create basic structure
    claude_dir = project_path / ".claude"
    skills_dir = claude_dir / "skills"
    shared_dir = skills_dir / "shared" / "scripts" / "lib"

    shared_dir.mkdir(parents=True)

    # Create settings
    settings = claude_dir / "settings.json"
    settings.write_text(json.dumps({
        'default_profile': 'default',
        'profiles': {
            'default': {'url': 'https://api.example.com'}
        }
    }))

    return project_path


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
        'url': 'https://api.example.com',
        'email': 'test@example.com',
        'default_space': 'TEST',
    }


@pytest.fixture
def env_vars(monkeypatch):
    """
    Factory for setting environment variables in tests.

    Usage:
        def test_with_env(env_vars):
            env_vars(API_TOKEN='secret', API_URL='https://...')
            # Test code...
    """
    def set_env(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)

    return set_env


# ============================================================================
# HTTP Response Fixtures
# ============================================================================

@pytest.fixture
def mock_response_factory():
    """
    Factory for creating mock HTTP response objects.

    Usage:
        def test_error_handling(mock_response_factory):
            response = mock_response_factory(status_code=404, json_data={'error': 'Not found'})
            # Use response...
    """
    def create_response(
        status_code: int = 200,
        json_data: dict = None,
        text: str = "",
        headers: dict = None,
    ):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = json_data or {}
        response.text = text or json.dumps(json_data or {})
        response.headers = headers or {}
        response.ok = 200 <= status_code < 300
        return response

    return create_response


@pytest.fixture
def mock_error_response(mock_response_factory, sample_error_responses):
    """
    Factory for creating error response mocks.

    Usage:
        def test_404_error(mock_error_response):
            response = mock_error_response(404)
            # Use response...
    """
    def create_error(status_code: int):
        error_data = sample_error_responses.get(str(status_code), {'message': 'Error'})
        return mock_response_factory(
            status_code=status_code,
            json_data=error_data
        )

    return create_error


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def capture_output(capsys):
    """
    Helper for capturing and asserting output.

    Usage:
        def test_output(capture_output):
            print("Hello")
            output = capture_output()
            assert "Hello" in output.out
    """
    def get_output():
        return capsys.readouterr()

    return get_output


@pytest.fixture
def run_script():
    """
    Helper for running script main functions.

    Usage:
        def test_script(run_script, mock_client):
            exit_code = run_script(main, ['arg1', '--option', 'value'])
            assert exit_code == 0
    """
    def runner(main_func, args, expected_exit=0):
        import sys
        original_argv = sys.argv
        sys.argv = ['script'] + args

        try:
            main_func()
            return 0
        except SystemExit as e:
            return e.code
        finally:
            sys.argv = original_argv

    return runner
```

## Fixture Categories

### 1. Mock Client Fixtures

Essential for testing scripts without making real API calls.

```python
def test_get_resource(mock_client):
    # Configure mock response
    mock_client.get.return_value = {
        'id': '123',
        'name': 'Test Resource'
    }

    # Test the function
    result = get_resource(client=mock_client, resource_id='123')

    # Assert
    assert result['name'] == 'Test Resource'
    mock_client.get.assert_called_once_with('/api/resources/123')
```

### 2. Sample Data Fixtures

Provide consistent test data across all tests.

```python
def test_format_resource(sample_resource):
    output = format_resource(sample_resource)
    assert 'Test Resource' in output
    assert '12345' in output
```

### 3. Error Response Fixtures

Test error handling systematically.

```python
def test_handles_404(mock_client, mock_error_response):
    from error_handler import NotFoundError

    mock_client.get.side_effect = NotFoundError("Not found", status_code=404)

    with pytest.raises(NotFoundError):
        get_resource(client=mock_client, resource_id='999')
```

### 4. File Fixtures

For testing file operations.

```python
def test_read_from_file(temp_file):
    input_file = temp_file("input.txt", "content here")

    result = process_file(str(input_file))
    assert result == "content here"
```

## Fixture Scopes

```python
# Function scope (default) - created for each test
@pytest.fixture
def mock_client():
    return MagicMock()

# Module scope - shared across all tests in module
@pytest.fixture(scope="module")
def expensive_resource():
    return create_expensive_resource()

# Session scope - shared across entire test session
@pytest.fixture(scope="session")
def shared_config():
    return load_config()
```

## Parametrized Fixtures

```python
@pytest.fixture(params=[
    ('page', 'pages'),
    ('blogpost', 'blogposts'),
    ('comment', 'comments'),
])
def content_types(request):
    """Parametrized fixture for testing multiple content types."""
    return {
        'singular': request.param[0],
        'plural': request.param[1]
    }


def test_list_content(mock_client, content_types):
    # Test runs once for each content type
    endpoint = f"/api/{content_types['plural']}"
    mock_client.get.return_value = {'results': []}
    # ...
```

## Best Practices

1. **Keep fixtures focused** - One responsibility per fixture
2. **Use fixture factories** - When you need configurable fixtures
3. **Document fixtures** - Clear docstrings with usage examples
4. **Prefer function scope** - Unless sharing state is intentional
5. **Use autouse sparingly** - Only for truly universal setup
6. **Name clearly** - `sample_*` for data, `mock_*` for mocks

## Directory Structure

```
tests/
├── conftest.py          # Shared fixtures for all tests
├── test_list.py
├── test_create.py
├── test_update.py
├── test_delete.py
└── live_integration/    # Optional: live API tests
    ├── conftest.py      # Fixtures for live tests
    └── test_live.py
```

## Live Integration Test Fixtures

```python
# tests/live_integration/conftest.py
import pytest
import os

@pytest.fixture(scope="session")
def live_client():
    """Create a real API client for integration tests."""
    from config_manager import get_client

    # Require credentials
    if not os.environ.get('API_TOKEN'):
        pytest.skip("API_TOKEN not set")

    return get_client(profile='test')


@pytest.fixture(scope="session")
def test_resource(live_client):
    """Create a test resource for the session, clean up after."""
    # Create
    resource = live_client.post('/api/resources', json_data={
        'name': 'Integration Test Resource'
    })

    yield resource

    # Cleanup
    try:
        live_client.delete(f"/api/resources/{resource['id']}")
    except Exception:
        pass  # Ignore cleanup errors
```
