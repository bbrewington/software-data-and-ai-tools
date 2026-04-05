# Python Utils

## Common uv commands I use

Lint Markdown:

```bash
uv run --with pymarkdownlnt pymarkdown \
    --disable-rules line-length \
    scan --respect-gitignore .
```

Validate Agent Skill (from [Agent Skills "skills-ref" Python package](https://github.com/agentskills/agentskills/tree/main/skills-ref))

```bash
uvx --from skills-ref agentskills validate \
    path/to/skill_folder
```
