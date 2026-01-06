### Diagrams

#### C4 Container Diagram
![C4 Container Diagram](diagram/images/c4_container.png)

#### Data Model Diagram
![Data Model Diagram](diagram/images/data_model.png)

#### Sequence Diagram
![Sequence Diagram](diagram/images/sequence.png)

#### Swimland Activity Diagram
![Swimlane Activity Diagram](diagram/images/swimlane_activity.png)

#### Existing Documents Diagram
![Docs With Origin Diagram](diagram/images/docs_with_origin.png)

## Configuration

CoreText is configured via `.coretext/config.yaml` in your project root.

```yaml
# CoreText Configuration
daemon_port: 8000
mcp_port: 8001
log_level: INFO
docs_dir: .  # Directory containing your markdown documents (default: project root)
system:
  memory_limit_mb: 50
  background_priority: true
```

*   **docs_dir**: Specifies the folder where CoreText should look for Markdown files. Useful for excluding irrelevant folders like `node_modules` or `build`.


