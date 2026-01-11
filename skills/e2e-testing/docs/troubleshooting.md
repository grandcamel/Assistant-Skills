# E2E Testing Troubleshooting

## No authentication configured

```bash
# Option 1: API Key
export ANTHROPIC_API_KEY="sk-ant-..."

# Option 2: OAuth (creates ~/.claude.json)
claude auth login
```

## Tests timing out

```bash
E2E_TEST_TIMEOUT=300 ./scripts/run-e2e-tests.sh
```

## Docker permission denied

```bash
sudo usermod -aG docker $USER
# Then log out and back in
```

## Tests showing "Reached max turns"

This usually means prompts are triggering file exploration. Fix by:
1. Redesigning prompts (see `test-prompt-best-practices.md`)
2. Increasing turn limit for complex tests:
```bash
E2E_MAX_TURNS=10 ./scripts/run-e2e-tests.sh
```

## Tests fail with "cannot use with root privileges"

The Docker container runs as non-root user (`testuser`) to support `--dangerously-skip-permissions`. If you encounter permission issues with mounted volumes, check ownership settings in docker-compose.yml.

## Docker volume permission errors

If you see "Operation not permitted" errors on `.claude` directory:
```bash
# Remove stale Docker volume and rebuild
docker volume rm e2e_claude-data
docker compose -f docker/e2e/docker-compose.yml build --no-cache e2e-tests
```

## Tests skip with "E2E tests disabled"

Ensure API key is passed to the container:
```bash
# Verify key is set
echo "Key length: ${#ANTHROPIC_API_KEY}"

# Run with explicit key passing
docker run --rm --entrypoint bash \
  -e "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" \
  -w /workspace/plugin-source \
  e2e_e2e-tests \
  -c 'python -m pytest tests/e2e/ -v'
```
