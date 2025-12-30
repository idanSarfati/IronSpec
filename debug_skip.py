def should_skip_validation(pr_title: str) -> bool:
    skip_keywords = [
        'infra', 'ci', 'workflow', 'github action', 'permissions',
        'dependencies', 'setup', 'config', 'build', 'lint', 'docker',
        'readme', 'documentation', 'chore', 'refactor', 'test'
    ]
    title_lower = pr_title.lower()
    matches = [kw for kw in skip_keywords if kw in title_lower]
    return bool(matches), matches

title = 'feat: update login button color specification [ENG-9]'
skip, matches = should_skip_validation(title)
print(f'Title: {title}')
print(f'Should skip: {skip}')
print(f'Matching keywords: {matches}')
