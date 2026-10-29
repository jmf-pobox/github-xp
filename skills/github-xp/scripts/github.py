"""Small gh transport and complete, normalized planning snapshots. Python stdlib only."""
import hashlib
import json
import os
import re
import subprocess
from urllib.parse import quote


class XPError(Exception):
    """Actionable error, without credential or subprocess environment dumps."""


def require(condition, message):
    if not condition:
        raise XPError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def issue_ref(value):
    match = re.fullmatch(r'(?:https://github\.com/)?([\w.-]+/[\w.-]+)(?:#|/issues/)([1-9]\d*)', value)
    require(match, 'Use owner/repo#number or a github.com issue URL: ' + str(value))
    return f'{match[1]}#{match[2]}'


def issue_path(ref):
    repo, number = issue_ref(ref).split('#')
    return f'repos/{repo}/issues/{number}'


def url(ref):
    return 'https://github.com/' + issue_ref(ref).replace('#', '/issues/')


class GitHub:
    def __init__(self, keyring=False, runner=subprocess.run):
        self.env = dict(os.environ)
        if keyring:
            self.env.pop('GH_TOKEN', None)
            self.env.pop('GITHUB_TOKEN', None)
        self.runner = runner

    def request(self, path, body=None, method='GET'):
        args = ['gh', 'api', path, '--hostname', 'github.com', '--method', method]
        if body is not None:
            args += ['--input', '-']
        try:
            result = self.runner(args, input=json.dumps(body) if body is not None else None,
                                 text=True, capture_output=True, env=self.env, timeout=90)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise XPError('GitHub call failed or timed out; reconcile before retrying: ' + path) from exc
        if result.returncode:
            # gh stderr may include server content; do not echo arbitrary credential-bearing text.
            status = re.search(r'HTTP (\d+)', result.stderr)
            code = status[1] if status else 'unknown'
            hint = {'401': 'check authentication', '403': 'check permissions or rate limits',
                    '404': 'check identity, access and host capability', '422': 'check request validation',
                    '429': 'rate limited; wait for GitHub reset before retrying'}.get(code, 'inspect gh authentication/network and reconcile state')
            raise XPError(f'GitHub HTTP {code}: {hint}; {method} {path}. No automatic mutation retry.')
        try:
            data = json.loads(result.stdout) if result.stdout.strip() else None
        except ValueError as exc:
            raise XPError('Non-JSON response: ' + path) from exc
        if isinstance(data, dict) and data.get('errors'):
            raise XPError('GraphQL errors; no success assumed: ' + json.dumps(data['errors']))
        return data

    def gql(self, query, variables=None):
        return self.request('graphql', {'query': query, 'variables': variables or {}}, 'POST')['data']

    def pages(self, path):
        result, page = [], 1
        while True:
            data = self.request(f'{path}{"&" if "?" in path else "?"}per_page=100&page={page}')
            require(isinstance(data, list), 'Expected paginated array: ' + path)
            result.extend(data)
            if len(data) < 100:
                return result
            page += 1

    def connection(self, query, variables, extract):
        nodes, cursor = [], None
        while True:
            connection = extract(self.gql(query, {**variables, 'cursor': cursor}))
            require(connection is not None, 'Inaccessible connection; refusing partial snapshot')
            nodes.extend(connection['nodes'])
            info = connection['pageInfo']
            if not info['hasNextPage']:
                return nodes
            require(info['endCursor'] and info['endCursor'] != cursor, 'Pagination did not advance')
            cursor = info['endCursor']


PAGE = 'pageInfo{hasNextPage endCursor}'
FIELDS = '''... on ProjectV2FieldCommon{id name dataType}
 ... on ProjectV2SingleSelectField{options{id name}}
 ... on ProjectV2IterationField{configuration{iterations{id title startDate duration} completedIterations{id title startDate duration}}}'''
VALUES = '''... on ProjectV2ItemFieldNumberValue{number field{... on ProjectV2FieldCommon{id name}}}
 ... on ProjectV2ItemFieldIterationValue{iterationId field{... on ProjectV2FieldCommon{id name}}}
 ... on ProjectV2ItemFieldSingleSelectValue{optionId name field{... on ProjectV2FieldCommon{id name}}}'''


def project_connection(api, pid, name, selection):
    query = f'query($id:ID!,$cursor:String){{node(id:$id){{... on ProjectV2{{{name}(first:100,after:$cursor){{{PAGE} nodes{{{selection}}}}}}}}}}}'
    return api.connection(query, {'id': pid}, lambda d: d['node'][name])


def snapshot(api, context):
    owner = context['owner']
    require(re.fullmatch(r'[\w.-]+', owner), 'Invalid owner')
    repos = context.get('repos', [])
    require(repos and all(re.fullmatch(r'[\w.-]+/[\w.-]+', r) for r in repos), 'repos must contain owner/repo names')
    user = api.request('users/' + owner)
    owner_kind = 'organization' if user['type'] == 'Organization' else 'user'
    project = None
    number = context.get('project')
    if number:
        require(isinstance(number, int) and number > 0, 'project must be a positive number')
        q = f'query($owner:String!,$number:Int!){{{owner_kind}(login:$owner){{projectV2(number:$number){{id number title url readme}}}}}}'
        project = api.gql(q, {'owner': owner, 'number': number})[owner_kind]['projectV2']
        require(project, 'Project inaccessible or absent')
    state = {'owner': {'login': owner, 'id': user['node_id'], 'kind': owner_kind},
             'project': project, 'repos': {}, 'issues': {}, 'fields': [], 'items': [],
             'views': [], 'workflows': [], 'records': [], 'warnings': [], 'linked_repositories': []}
    if project:
        pid = project['id']
        state['linked_repositories'] = project_connection(api, pid, 'repositories', 'id nameWithOwner')
        state['fields'] = project_connection(api, pid, 'fields', FIELDS)
        state['views'] = project_connection(api, pid, 'views', 'id name number layout filter')
        state['workflows'] = project_connection(api, pid, 'workflows', 'id name enabled')
        state['items'] = project_connection(api, pid, 'items', 'id isArchived content{__typename ... on Issue{id url}}')
        for item in state['items']:
            q = f'query($id:ID!,$cursor:String){{node(id:$id){{... on ProjectV2Item{{fieldValues(first:100,after:$cursor){{{PAGE} nodes{{{VALUES}}}}}}}}}}}'
            values = api.connection(q, {'id': item['id']}, lambda d: d['node']['fieldValues'])
            item['values'] = {v['field']['id']: v for v in values if v.get('field')}
            content = item.get('content')
            if not content or content.get('__typename') != 'Issue':
                state['warnings'].append('Non-issue or inaccessible Project item: ' + item['id'])
            elif content['url'].startswith('https://github.com/'):
                item['ref'] = issue_ref(content['url'])
                repo = item['ref'].split('#')[0]
                if repo not in repos:
                    state['warnings'].append('Project item outside selected repos: ' + item['ref'])
            if item['isArchived']:
                state['warnings'].append('Archived Project item: ' + item['id'])
    for repo in repos:
        metadata = api.request('repos/' + repo)
        state['repos'][repo] = {'id': metadata['node_id'], 'default_branch': metadata['default_branch'],
                                'owner_type': metadata['owner']['type']}
        for issue in api.pages('repos/' + repo + '/issues?state=all'):
            if 'pull_request' in issue:
                continue
            ref = repo + '#' + str(issue['number'])
            issue['ref'] = ref
            issue['kind'] = classify(issue, context)
            state['issues'][ref] = issue
    # Fetch all relationships separately: no silently truncated nested connection.
    for ref, issue in state['issues'].items():
        issue['children'] = [issue_ref(x['html_url']) for x in api.pages(issue_path(ref) + '/sub_issues')]
        issue['blockers'] = [issue_ref(x['html_url']) for x in api.pages(issue_path(ref) + '/dependencies/blocked_by')]
    for issue in state['issues'].values():
        for related in issue['children'] + issue['blockers']:
            require(related in state['issues'], 'Include related repository in context.repos: ' + related)
    history = context.get('history')
    if history:
        require(issue_ref(history) in state['issues'], 'History issue must be in selected repositories')
        state['records'] = read_records(api.pages(issue_path(history) + '/comments'))
    return state


def classify(issue, context):
    names = {x['name'] for x in issue.get('labels', [])}
    issue_type = (issue.get('type') or {}).get('name')
    kinds = [k for k in ('story', 'task', 'spike')
             if context.get('labels', {}).get(k, 'type:' + k) in names
             or issue_type == context.get('types', {}).get(k, k.title())]
    require(len(kinds) <= 1, 'Conflicting XP classifications on issue ' + str(issue.get('number')))
    return kinds[0] if kinds else None


def read_records(comments):
    records, seen = [], set()
    for comment in comments:
        body = comment.get('body') or ''
        if '<!-- github-xp:v1:' not in body:
            continue
        match = re.search(r'<!-- github-xp:v1:([\w.:-]+) -->\s*```json\n(.*?)\n```', body, re.S)
        require(match, 'Malformed XP history comment: ' + str(comment['id']))
        try:
            record = json.loads(match[2])
        except ValueError as exc:
            raise XPError('Malformed XP JSON history') from exc
        require(record.get('schema') == 1 and record.get('key') == match[1], 'Invalid XP history schema/key')
        require(record['key'] not in seen, 'Duplicate history key: ' + record['key'])
        seen.add(record['key'])
        records.append(record)
    return records


def encoded(value):
    return quote(str(value), safe='')
