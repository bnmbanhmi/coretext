# Story 4.3: Resource Consumption Management

**Status:** ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want `coretext` to be a "good neighbor" on my local machine, consuming minimal system resources,
so that it doesn't negatively impact the performance of other applications while running in the background.

## Acceptance Criteria

1.  **Idle Memory Cap**: When the daemon is idle (no active queries or syncs), it consumes less than **50MB RAM** (RSS).
2.  **Background Priority**: Long-running background operations (specifically embedding generation and full re-indexing) run at the lowest process priority:
    *   **Unix/Linux/macOS**: `nice` value of 19.
    *   **Windows**: `IDLE_PRIORITY_CLASS` or `BELOW_NORMAL_PRIORITY_CLASS`.
3.  **Memory Watchdog**: A background routine actively monitors the daemon's memory usage and triggers a warning or garbage collection if it exceeds the configured soft limit (default: 50MB).
4.  **Configurable Limits**: The memory limit is configurable via `config.yaml` (default: 50MB) and environment variables.

## Tasks / Subtasks

- [ ] **Implement Cross-Platform Priority Manager**
  - [ ] Create `coretext/core/system/process.py` to abstract `psutil` priority setting.
  - [ ] Implement `set_background_priority()` handling Unix `nice` and Windows `priority_class`.
  - [ ] Add unit tests mocking `psutil` for both platforms.
- [ ] **Implement Memory Watchdog & Profiler**
  - [ ] Create `coretext/core/system/memory.py` with `MemoryWatchdog` class.
  - [ ] Implement async loop to check `psutil.Process().memory_info().rss` every 60s (configurable).
  - [ ] Trigger Python `gc.collect()` if usage > soft_limit (50MB).
  - [ ] Log warnings if usage remains high after GC.
- [ ] **Optimize Embedding Generation for Low Resource**
  - [ ] Update `coretext/core/vector/embedder.py` to explicitly call `set_background_priority()` during batch processing.
  - [ ] Ensure `sentence-transformers` model is loaded only when needed or kept efficiently (verify model size vs 50MB limit - *Critical: 50MB might be too aggressive if model is loaded. refined requirement: 50MB applies to DAEMON overhead, model memory excluded or loaded on-demand*).
  - [ ] **REFINEMENT**: If the model (approx 100-300MB) is loaded, 50MB is impossible.
  - [ ] **Task Update**: Implement "On-Demand Model Loading" or "Separate Process" strategy if 50MB is strict hard cap for *idle* daemon.
  - [ ] *Decision*: 50MB is for *idle* state. Model should be unloaded or mapped out when idle if possible, OR acceptance criteria adjusted to "50MB + Model Size". Let's stick to **50MB overhead** + Model.
- [ ] **Integrate with Daemon Lifecycle**
  - [ ] Initialize `MemoryWatchdog` in `coretext/server/app.py` startup event.
  - [ ] Ensure proper cleanup on shutdown.
- [ ] **Configuration Updates**
  - [ ] Add `system.memory_limit_mb` to `coretext/config.py`.
  - [ ] Add `system.background_priority` toggle.

## Dev Notes

- **Library**: `psutil` is already in the dependency tree (checked via `poetry.lock` or add if missing).
- **Cross-Platform**: Windows handles priority differently. Use `psutil.BELOW_NORMAL_PRIORITY_CLASS`.
- **Memory Reality Check**: Python overhead + FastAPI + Uvicorn + SurrealDB connection can easily hit 30-40MB. The 50MB idle target is tight.
  - **Strategy**: Aggressive `gc.collect()`.
  - **Fallback**: If 50MB is unrealistic for Python, document baseline usage and set limit to "Baseline + 20%".
- **Testing**:
  - Use `pytest-asyncio` for the watchdog loop.
  - Mock `psutil` to avoid actually changing system priority during tests.

### Project Structure Notes

- **New Module**: `coretext/core/system/` for OS-level interactions (`process.py`, `memory.py`).
- **Config**: Update `config.py` Pydantic models.

### References

- [psutil documentation - Process Management](https://psutil.readthedocs.io/en/latest/#process-management)
- [Python Garbage Collector interface](https://docs.python.org/3/library/gc.html)

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- None

### Completion Notes List

- Verified `psutil` capabilities for nice/priority.
- Identified potential risk with 50MB limit vs Model size (addressed via idle definition).

### File List

- `coretext/core/system/__init__.py`
- `coretext/core/system/process.py`
- `coretext/core/system/memory.py`
- `coretext/server/app.py` (modification)
- `coretext/config.py` (modification)
