# Splunk Assistant Skills Patterns

Patterns extracted from the Splunk-Assistant-Skills project (13 skills, 50+ scripts, 150+ tests).

## Project Structure

```
Splunk-Assistant-Skills/
├── .claude/
│   ├── settings.json
│   ├── commands/
│   └── skills/
│       ├── shared/
│       ├── splunk-assistant/   # Hub skill
│       ├── splunk-search/      # SPL queries
│       ├── splunk-saved/       # Saved searches
│       ├── splunk-alerts/      # Alert management
│       ├── splunk-reports/     # Report scheduling
│       ├── splunk-dashboards/  # Dashboard CRUD
│       ├── splunk-indexes/     # Index management
│       ├── splunk-inputs/      # Data inputs
│       ├── splunk-apps/        # App management
│       ├── splunk-users/       # User management
│       ├── splunk-roles/       # Role-based access
│       ├── splunk-kvstore/     # KV Store ops
│       └── splunk-admin/       # Admin operations
├── docs/
└── README.md
```

## Search-Centric Patterns

### Async Search Jobs

Splunk searches are asynchronous:

```python
# Create search job
job = client.create_search('index=main | stats count by host')

# Wait for completion with polling
while not job.is_done():
    time.sleep(1)
    job.refresh()

# Get results
results = job.results(output_mode='json')
```

### SPL Builder

```python
from spl_builder import SPLQuery

query = (SPLQuery()
    .index('main')
    .earliest('-24h')
    .search('error OR exception')
    .stats('count by host')
    .sort('-count')
    .head(10)
    .build())

# Result: index=main earliest=-24h (error OR exception) | stats count by host | sort -count | head 10
```

## Time-Series Pattern

```python
# Time range handling
from time_utils import parse_time_range, format_splunk_time

start, end = parse_time_range('-7d', 'now')
results = client.search(
    query,
    earliest_time=format_splunk_time(start),
    latest_time=format_splunk_time(end)
)
```

## REST API Pattern

Splunk uses a different REST pattern:

```python
# Splunk REST endpoints
client.get('/services/search/jobs')           # List jobs
client.post('/services/search/jobs', data)    # Create job
client.get(f'/services/search/jobs/{sid}')    # Get job
client.get(f'/services/search/jobs/{sid}/results')  # Get results
```

## Configuration Pattern

```json
{
  "splunk": {
    "default_profile": "production",
    "profiles": {
      "production": {
        "url": "https://splunk.company.com:8089",
        "app": "search",
        "owner": "admin"
      }
    },
    "search": {
      "default_earliest": "-24h",
      "default_latest": "now",
      "max_count": 10000,
      "timeout": 300
    }
  }
}
```

## Key Differences

| Aspect | Jira/Confluence | Splunk |
|--------|-----------------|--------|
| Auth | API Token | Username/Password or Token |
| API Style | REST (sync) | REST (async jobs) |
| Query | JQL/CQL | SPL |
| Results | Paginated | Job-based |
| Port | 443 | 8089 (management) |

## Async Pattern

```python
# Polling wrapper
@retry_with_backoff
def wait_for_job(job_id, timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        job = client.get_job(job_id)
        if job['dispatchState'] == 'DONE':
            return job
        time.sleep(2)
    raise TimeoutError(f"Job {job_id} did not complete")
```

## Key Metrics

| Metric | Value |
|--------|-------|
| Skills | 13 |
| Scripts | 50+ |
| Tests | 150+ |
| Focus | Search & analytics |
