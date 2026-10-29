#!/usr/bin/env python3
"""XP planning helpers. Preview by default; GitHub is the durable state store."""
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True  # Preview must not create __pycache__ in an installed skill.

from github import (GitHub, XPError, digest, encoded, issue_path, issue_ref,  # noqa: E402
                    require, snapshot, url)

COMMANDS = ('setup', 'story', 'split', 'plan', 'start', 'finish', 'accept',
            'close-iteration', 'velocity', 'release', 'correct-history')
DEFAULTS = {'points': 'Points', 'iteration': 'Iteration', 'status': 'Status',
            'todo': 'Todo', 'in_progress': 'In Progress', 'done': 'Done'}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def timestamp(value):
    require(isinstance(value, str), 'Timestamp required')
    try:
        result = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise XPError('Invalid timestamp: ' + value) from exc
    require(result.tzinfo is not None, 'Timestamp needs an explicit timezone')
    return result


class Planner:
    def __init__(self, state, context, data, operation, api=None):
        self.s, self.c, self.d, self.op, self.api = state, context, data, operation, api
        self.actions, self.output = [], {}
        self.items = {x['ref']: x for x in state['items'] if x.get('ref')}
        self.records = {x['key']: x for x in state['records']}
        self.pid = state['project']['id'] if state['project'] else None
        self.fields = {}
        for key in ('points', 'iteration', 'status'):
            name = context.get('fields', {}).get(key, DEFAULTS[key])
            matches = [x for x in state['fields'] if x['name'] == name]
            require(len(matches) <= 1, 'Ambiguous field: ' + name)
            if matches:
                self.fields[key] = matches[0]
        self.iterations = []
        if 'iteration' in self.fields:
            config = self.fields['iteration']['configuration']
            self.iterations = config['iterations'] + config['completedIterations']

    def action(self, description, path, body, method='POST', guard=None):
        key = 'step' + str(len(self.actions) + 1)
        self.actions.append({'id': key, 'description': description, 'path': path,
                             'method': method, 'body': body, 'guard': guard})
        return {'$ref': key}

    def mutation(self, name, input_type, data, selection):
        query = f'mutation($input:{input_type}!){{{name}(input:$input){{{selection}}}}}'
        ref = self.action(name, 'graphql', {'query': query, 'variables': {'input': data}})
        return {'$ref': ref['$ref'] + '.data.' + name}

    def field(self, key):
        require(key in self.fields, 'Missing field; run setup: ' + key)
        return self.fields[key]

    def issue(self, ref, kind=None):
        ref = issue_ref(ref)
        require(ref in self.s['issues'], 'Issue absent/inaccessible; include its repository: ' + ref)
        value = self.s['issues'][ref]
        require(not kind or value['kind'] == kind, f'{ref} must be {kind}')
        return value

    def value(self, ref, field):
        item = self.items.get(ref)
        if not item:
            return None
        value = item['values'].get(self.field(field)['id'], {})
        return value.get({'points': 'number', 'iteration': 'iterationId', 'status': 'optionId'}[field])

    def iteration(self, ident):
        matches = [x for x in self.iterations if x['id'] == ident]
        require(len(matches) == 1, 'Use an existing unambiguous Iteration ID, not a title')
        return matches[0]

    def member(self, issue):
        ref = issue['ref']
        if ref in self.items:
            require(not self.items[ref]['isArchived'], 'Unarchive explicitly before changing ' + ref)
            return self.items[ref]['id']
        result = self.mutation('addProjectV2ItemById', 'AddProjectV2ItemByIdInput',
                               {'projectId': self.pid, 'contentId': issue['node_id']}, 'item{id}')
        item_id = {'$ref': result['$ref'] + '.item.id'}
        self.items[ref] = {'id': item_id, 'values': {}, 'isArchived': False}
        return item_id

    def set_field(self, issue, key, value):
        field = self.field(key)
        old = self.value(issue['ref'], key)
        item_id = self.member(issue)
        if old == value:
            return
        mapping = {'points': 'number', 'iteration': 'iterationId', 'status': 'singleSelectOptionId'}
        payload = {'projectId': self.pid, 'itemId': item_id, 'fieldId': field['id']}
        if value is None:
            self.mutation('clearProjectV2ItemFieldValue', 'ClearProjectV2ItemFieldValueInput', payload, 'projectV2Item{id}')
        else:
            payload['value'] = {mapping[key]: value}
            self.mutation('updateProjectV2ItemFieldValue', 'UpdateProjectV2ItemFieldValueInput', payload, 'projectV2Item{id}')
        if isinstance(item_id, str):
            self.actions[-1]['guard'] = {'item': item_id, 'field_name': field['name'],
                                         'value_key': {'points': 'number', 'iteration': 'iterationId', 'status': 'optionId'}[key],
                                         'expected': old, 'target': value}

    def status(self, issue, role):
        name = self.c.get('status', {}).get(role, DEFAULTS[role])
        options = [x for x in self.field('status')['options'] if x['name'] == name]
        require(len(options) == 1, 'Resolve status mapping for ' + role)
        self.set_field(issue, 'status', options[0]['id'])

    def safe_workflows(self):
        require(not any(w['enabled'] and w['name'] == 'Auto-close issue' for w in self.s['workflows']),
                'Disable Done-to-close in Project Workflows before acceptance-sensitive mutations')

    def history(self, key, kind, payload):
        require(self.c.get('history'), 'Select a GitHub history issue in context.history')
        require(not set(payload) & {'schema', 'key', 'kind', 'project', 'operation', 'recorded_at'},
                'History payload contains reserved metadata keys')
        fullkey = f'{self.pid}:{key}'
        record = {'schema': 1, 'key': fullkey, 'kind': kind, 'project': self.pid,
                  'operation': self.op, **payload}
        existing = self.records.get(fullkey)
        if existing:
            require({k: v for k, v in existing.items() if k != 'recorded_at'} == record,
                    'History conflicts with this request: ' + fullkey)
            return existing
        record['recorded_at'] = now()
        body = '<!-- github-xp:v1:' + fullkey + ' -->\n```json\n' + json.dumps(record, indent=2) + '\n```'
        self.action('Record ' + kind, issue_path(self.c['history']) + '/comments', {'body': body})
        self.records[fullkey] = record
        return record

    def find_record(self, key):
        return self.records.get(f'{self.pid}:{key}')

    def blockers(self, issue):
        return [r for r in issue['blockers'] if self.issue(r)['state'] != 'closed'
                or self.issue(r).get('state_reason') != 'completed']

    def points(self, issue):
        number = self.value(issue['ref'], 'points')
        require(isinstance(number, (int, float)) and not isinstance(number, bool) and number >= 0,
                'Story Points are unknown/invalid: ' + issue['ref'])
        return number

    def change_issue(self, issue, body):
        self.action('Update ' + issue['ref'], issue_path(issue['ref']), body, 'PATCH',
                    {'path': issue_path(issue['ref']), 'updated_at': issue['updated_at']})

    def create_issue(self, spec, kind, key):
        repo = spec['repo']
        require(repo in self.s['repos'], 'Select repository in context.repos')
        marker = f'<!-- github-xp:issue:{self.op}:{key} -->'
        candidates = [i for i in self.s['issues'].values() if marker in (i.get('body') or '')]
        require(len(candidates) <= 1, 'Duplicate operation marker; reconcile manually')
        title, body = spec.get('title', '').strip(), spec.get('body', '').strip()
        require(title and body, 'Nonempty title and rendered issue body required')
        if kind == 'story':
            require(spec.get('criteria_reviewed') is True, 'Agent must verify nonempty inline or linked criteria')
        if kind == 'spike':
            require(spec.get('timebox') and spec.get('question'), 'Spike needs timebox and learning question')
        if candidates:
            issue = candidates[0]
            require(issue['ref'].split('#')[0] == repo and issue['kind'] == kind and issue['title'] == title and
                    issue['body'] == body + '\n\n' + marker, 'Operation ID reused for changed issue content')
            self.member(issue)
            return issue
        payload = {'title': title, 'body': body + '\n\n' + marker}
        if self.s['repos'][repo]['owner_type'] == 'Organization' and self.c.get('types', {}).get(kind):
            payload['type'] = self.c['types'][kind]
        else:
            payload['labels'] = [self.c.get('labels', {}).get(kind, 'type:' + kind)]
        if spec.get('milestone'):
            payload['milestone'] = spec['milestone']
        created = self.action('Create ' + kind, 'repos/' + repo + '/issues', payload)
        issue = {'ref': f'{repo}#pending-{key}', 'node_id': {'$ref': created['$ref'] + '.node_id'},
                 'id': {'$ref': created['$ref'] + '.id'}, 'number': {'$ref': created['$ref'] + '.number'},
                 'kind': kind, 'state': 'open', 'children': [], 'blockers': [], 'created_ref': created}
        self.member(issue)
        return issue

    def story(self):
        kind = self.d.get('kind', 'story')
        require(kind in ('story', 'spike'), 'Use split for Tasks')
        issue = self.create_issue(self.d, kind, 'story')
        if self.d.get('points') is not None:
            require(kind == 'story' and isinstance(self.d['points'], (int, float)) and
                    not isinstance(self.d['points'], bool) and self.d['points'] >= 0, 'Only Stories receive nonnegative Points')
            self.set_field(issue, 'points', self.d['points'])
        self.output = {'issue': issue['ref'], 'estimate': self.d.get('points', 'unknown')}

    def split(self):
        parent = self.issue(self.d['story'], 'story')
        require(parent['state'] == 'open', 'Cannot split a closed Story')
        tasks = self.d.get('tasks', [])
        require(tasks, 'Provide a nonempty reviewed Task list')
        require(len({x['key'] for x in tasks}) == len(tasks), 'Task keys must be unique')
        for spec in tasks:
            require(re.fullmatch(r'[\w.-]+', spec['key']), 'Task key must be a stable identifier')
            require('points' not in spec, 'Tasks never receive Points')
            issue = self.create_issue(spec, 'task', spec['key'])
            if issue['ref'] not in parent['children']:
                # Existing Task may already belong to another parent; do not reparent it.
                owners = [x['ref'] for x in self.s['issues'].values() if issue['ref'] in x['children']]
                require(not owners, 'Task already has a different parent')
                self.action('Link native sub-issue', issue_path(parent['ref']) + '/sub_issues', {'sub_issue_id': issue['id']})
            iteration = self.value(parent['ref'], 'iteration')
            if iteration and issue['state'] == 'open':
                self.set_field(issue, 'iteration', iteration)
            for dependency in spec.get('blocked_by', []):
                target = self.issue(dependency)
                require(target['ref'] != issue['ref'], 'Self-dependency forbidden')
                visited, stack = set(), [target['ref']]
                while stack:
                    current = stack.pop()
                    require(current != issue['ref'], 'Dependency cycle')
                    if current not in visited:
                        visited.add(current)
                        stack.extend(self.issue(current)['blockers'])
                if target['ref'] not in issue['blockers']:
                    path = issue_path(issue['ref']) if 'created_ref' not in issue else {
                        '$path': ['repos/', spec['repo'], '/issues/', {'$ref': issue['created_ref']['$ref'] + '.number'}]}
                    if isinstance(path, dict):
                        path['$path'].append('/dependencies/blocked_by')
                    else:
                        path += '/dependencies/blocked_by'
                    self.action('Add native blocker', path, {'issue_id': target['id']})

    def scope(self, refs):
        result = []
        for ref in refs:
            story = self.issue(ref, 'story')
            require(story['state'] == 'open', 'Planning requires open Story: ' + ref)
            require(not self.blockers(story), 'Open Story blocker: ' + ref)
            children = [self.issue(r) for r in story['children']]
            result.append({'story': story['ref'], 'points': self.points(story),
                           'from': self.value(story['ref'], 'iteration'),
                           'tasks': [{'ref': t['ref'], 'from': self.value(t['ref'], 'iteration')}
                                     for t in children if t['state'] == 'open']})
        return result

    def assignments(self, scope, iteration):
        for row in scope:
            for entry in [{'ref': row['story'], 'from': row['from']}] + row['tasks']:
                issue = self.issue(entry['ref'])
                current = self.value(issue['ref'], 'iteration')
                require(current in (entry['from'], iteration), 'Concurrent iteration edit: ' + issue['ref'])
                if issue['state'] == 'open':
                    self.set_field(issue, 'iteration', iteration)

    def plan(self):
        iteration = self.iteration(self.d['iteration'])['id']
        require(self.d.get('availability'), 'Include human product/review/integration availability')
        require(isinstance(self.d.get('stories'), list) and len(set(self.d['stories'])) == len(self.d['stories']), 'Ordered unique Story refs required; an explicit empty list records a zero-scope plan')
        old = self.find_record('plan:' + self.op)
        fingerprint = digest(self.d)
        if old:
            require(old['request_hash'] == fingerprint, 'Changed plan request under same operation ID')
            scope = old['scope']
        else:
            scope = self.scope(self.d['stories'])
        self.history('plan:' + self.op, 'plan', {'iteration': iteration, 'scope': scope,
                     'availability': self.d['availability'], 'request_hash': fingerprint})
        self.assignments(scope, iteration)
        self.output = {'iteration': iteration, 'ordered_scope': scope,
                       'points': sum(x['points'] for x in scope), 'note': 'Order is supplied customer order, not inferred API rank'}

    def start(self):
        issue = self.issue(self.d['issue'])
        require(issue['kind'] in ('task', 'story'), 'Start a Task or explicitly unsplit Story')
        require(issue['state'] == 'open' and not self.blockers(issue), 'Work is closed or blocked')
        if issue['kind'] == 'story':
            require(not issue['children'] and self.d.get('unsplit') is True, 'Use a Task, or declare an unsplit Story')
        parents = [x for x in self.s['issues'].values() if issue['ref'] in x['children']]
        for parent in parents:
            require(parent['state'] == 'open' and not self.blockers(parent), 'Parent closed or blocked')
        brief = self.d.get('brief', {})
        required = ('criteria', 'scope', 'instructions', 'workflow', 'dependencies', 'allowed_actions', 'expected_evidence', 'executor')
        require(all(brief.get(k) for k in required), 'Work brief requires: ' + ', '.join(required))
        require(brief.get('started') is True, 'Record In Progress only after work actually starts')
        if self.d.get('assignee'):
            existing = [a['login'] for a in issue.get('assignees', [])]
            require(not existing or self.d['assignee'] in existing, 'Preserve existing assignees; resolve ownership first')
            if not existing:
                self.change_issue(issue, {'assignees': [self.d['assignee']]})
        self.history('start:' + self.op, 'handoff', {'issue': issue['ref'], 'brief': brief})
        self.status(issue, 'in_progress')
        self.output = {'brief': brief, 'parent_stories': [x['ref'] for x in parents],
                       'execution': 'Existing workflow owns branches, coding, review, merge and cleanup'}

    def evidence(self, issue, evidence):
        require(evidence.get('revision') and evidence.get('tests') and evidence.get('criteria'),
                'Evidence needs revision, actual test results and criterion-to-evidence mapping')
        require(evidence.get('verified_revision') == evidence['revision'], 'Review/demo evidence is stale')
        require(evidence.get('gates_passed') is True, 'Existing workflow gates have not passed')
        require(not self.blockers(issue), 'Open blockers remain')
        prs = evidence.get('prs', [])
        require(prs or (evidence.get('non_code') is True and evidence.get('completion_evidence')),
                'Code work requires merged PR evidence; non-code work needs explicit completion evidence')
        for ref in prs:
            match = re.fullmatch(r'https://github\.com/([\w.-]+/[\w.-]+)/pull/([1-9]\d*)', ref)
            require(match and match[1] in self.s['repos'], 'PR must be in a selected repository')
            key = match[1] + '#' + match[2]
            pr = self.api.request(f'repos/{match[1]}/pulls/{match[2]}') if self.api else self.s.get('prs', {}).get(key)
            require(pr, 'PR evidence unavailable: ' + ref)
            require(pr.get('merged') and pr['base']['ref'] == self.s['repos'][match[1]]['default_branch'],
                    'PR is not merged into the actual default branch: ' + ref)
            if self.d.get('completed_at'):
                require(timestamp(pr.get('merged_at')) <= timestamp(self.d['completed_at']),
                        'Credit time precedes required PR integration: ' + ref)
            verified = evidence.get('pr_revisions', {}).get(ref)
            require(verified and verified == pr['head']['sha'], 'PR head differs from inspected revision: ' + ref)
        return evidence

    def finish(self):
        issue = self.issue(self.d['issue'])
        require(issue['kind'] in ('task', 'story'), 'Finish a Task or unsplit Story')
        if issue['kind'] == 'story':
            require(not issue['children'] and self.d.get('unsplit') is True, 'Finish Tasks separately')
        evidence = self.evidence(issue, self.d.get('evidence', {}))
        self.history('finish:' + self.op, 'finish', {'issue': issue['ref'], 'evidence': evidence})
        if issue['kind'] == 'task':
            require(issue['state_reason'] != 'not_planned', 'Cancelled Task is not completed')
            if issue['state'] != 'closed':
                self.change_issue(issue, {'state': 'closed', 'state_reason': 'completed'})
            self.status(issue, 'done')
        self.output = {'issue': issue['ref'], 'story_left_open': issue['kind'] == 'story',
                       'traceability': 'Task PR: Closes ' + issue['ref'] if issue['kind'] == 'task' else 'Story PR: Refs ' + issue['ref']}

    def acceptance_payload(self, story):
        require(story['state_reason'] != 'not_planned', 'Cancelled Story cannot earn credit')
        require(story['children'] or self.d.get('unsplit') is True, 'Declare intentional unsplit Story')
        for child in story['children']:
            task = self.issue(child)
            require(task['state'] == 'closed' and task['state_reason'] == 'completed',
                    'Required Task incomplete/cancelled: ' + child)
        criteria = self.d.get('criteria', {})
        require(criteria.get('source') and criteria.get('revision') and criteria.get('items'),
                'Criteria need source, revision and nonempty identified items')
        require(criteria.get('verified') is True and all(str(x).strip() for x in criteria['items']),
                'Agent must inspect real inline/linked criteria; placeholders are not evidence')
        evidence = self.evidence(story, self.d.get('evidence', {}))
        require(set(criteria['items']) <= set(evidence['criteria']), 'Missing criterion evidence')
        require(all(evidence['criteria'][k] for k in criteria['items']), 'Empty criterion evidence')
        decision = self.d.get('decision', {})
        require(decision.get('authority') and decision.get('reference') and decision.get('accepted') is True,
                'Recorded customer or explicitly delegated acceptance decision required')
        require(decision.get('revision') == evidence['revision'], 'Acceptance decision is for a different revision')
        decision_time = timestamp(decision.get('at'))
        credit_time = timestamp(self.d.get('completed_at'))
        require(decision_time <= credit_time <= dt.datetime.now(dt.timezone.utc), 'Invalid decision/completion chronology')
        iteration = self.iteration(self.d['iteration'])
        start = dt.datetime.combine(dt.date.fromisoformat(iteration['startDate']), dt.time(), dt.timezone.utc)
        require(start <= credit_time < start + dt.timedelta(days=iteration['duration']),
                'Completion time outside credit iteration (UTC); resolve breaks/overlaps explicitly')
        matching = [i for i in self.iterations if dt.date.fromisoformat(i['startDate']) <= credit_time.date() <
                    dt.date.fromisoformat(i['startDate']) + dt.timedelta(days=i['duration'])]
        require(len(matching) == 1, 'Ambiguous overlapping credit iterations')
        return {'story': story['ref'], 'iteration': iteration['id'], 'points': self.points(story),
                'criteria': criteria, 'evidence': evidence, 'decision': decision, 'completed_at': self.d['completed_at']}

    def accept(self):
        story = self.issue(self.d['story'], 'story')
        payload = self.acceptance_payload(story)
        key = 'accept:' + story['node_id']
        prior = self.find_record(key)
        if prior:
            require(not any(r['kind'] == 'correction' and r.get('target') == prior['key'] and r.get('revoke') is True
                            for r in self.s['records']), 'Original credit was revoked; resolve scope with a new Story or explicit reviewed history repair')
            require(prior['story'] == story['ref'], 'Conflicting Story identity')
            if story['state'] == 'open':
                self.history('reaccept:' + self.op, 'reaccept', payload)
                self.set_field(story, 'iteration', prior['iteration'])
                self.change_issue(story, {'state': 'closed', 'state_reason': 'completed'})
                self.status(story, 'done')
            self.output = {'credit': 'already recorded; no second credit', 'record': prior['key'],
                           'reaccepted': story['state'] == 'open'}
            return
        require(not self.find_record('close:' + payload['iteration']),
                'Period already published; use explicit history correction rather than silently restating it')
        intent_key = 'accept-intent:' + story['node_id']
        self.history(intent_key, 'accept-intent', payload)
        self.set_field(story, 'iteration', payload['iteration'])
        if story['state'] != 'closed':
            self.change_issue(story, {'state': 'closed', 'state_reason': 'completed'})
        self.status(story, 'done')
        # Executor verifies closure immediately before final credit.
        self.history(key, 'accept', payload)
        if self.actions and self.actions[-1]['description'] == 'Record accept':
            self.actions[-1]['guard'] = {'path': issue_path(story['ref']), 'state': 'closed', 'state_reason': 'completed'}
        self.output = {'accepted': story['ref'], 'points': payload['points'], 'iteration': payload['iteration']}

    def credits(self):
        records = [r for r in self.s['records'] if r.get('project') == self.pid and r['kind'] == 'accept']
        require(len({r['story'] for r in records}) == len(records), 'Duplicate Story credit')
        revoked = {r['target'] for r in self.s['records'] if r['kind'] == 'correction' and r.get('revoke') is True}
        return [r for r in records if r['key'] not in revoked]

    def close_iteration(self):
        source = self.iteration(self.d['iteration'])
        target = self.iteration(self.d['next_iteration'])
        require(dt.date.fromisoformat(target['startDate']) >= dt.date.fromisoformat(source['startDate']) + dt.timedelta(days=source['duration']), 'Next iteration must follow source')
        require(dt.date.fromisoformat(source['startDate']) + dt.timedelta(days=source['duration']) <= dt.datetime.now(dt.timezone.utc).date(), 'Cannot publish an incomplete calendar period')
        old = self.find_record('close:' + source['id'])
        request_hash = digest(self.d)
        if old:
            require(old['request_hash'] == request_hash, 'Use original close request and next iteration to resume')
            scope = old['carried']
        else:
            require(not self.s['warnings'], 'Resolve incomplete/archived Project scope before closing: ' + '; '.join(self.s['warnings']))
            plans = [r for r in self.s['records'] if r['kind'] == 'plan' and r['project'] == self.pid and r['iteration'] == source['id']]
            require(plans, 'No recorded commitment; do not manufacture original scope')
            original = plans[0]['scope']
            current = [ref for ref in self.items if self.issue(ref)['kind'] == 'story' and self.value(ref, 'iteration') == source['id']]
            open_refs = [ref for ref in current if self.issue(ref)['state'] == 'open']
            # Carry blocked work too; close reports blockers rather than treating them as completed.
            scope = []
            for ref in open_refs:
                story = self.issue(ref)
                scope.append({'story': ref, 'points': self.points(story), 'from': source['id'],
                              'tasks': [{'ref': r, 'from': self.value(r, 'iteration')} for r in story['children'] if self.issue(r)['state'] == 'open']})
            accepted = [r for r in self.credits() if r['iteration'] == source['id']]
            known = {r['story'] for r in accepted}
            require(all(self.issue(r)['state'] == 'open' or self.issue(r)['state_reason'] == 'not_planned' or r in known for r in current), 'Closed Story without verified acceptance history')
            cancelled = [r for r in current if self.issue(r)['state_reason'] == 'not_planned']
            require(all(self.d.get('cancellations', {}).get(r) for r in cancelled),
                    'Cancelled Stories require explicit scope decisions in cancellations')
            initial = {r['story'] for r in original}
            payload = {'iteration': source['id'], 'next_iteration': target['id'], 'planned': original,
                       'added': sorted(set(current) - initial), 'removed': sorted(initial - set(current)),
                       'cancelled': {r: self.d['cancellations'][r] for r in cancelled},
                       'accepted': [{'story': r['story'], 'points': r['points']} for r in accepted],
                       'points': sum(r['points'] for r in accepted), 'carried': scope,
                       'reflection': self.d.get('reflection', ''), 'request_hash': request_hash}
            self.history('close:' + source['id'], 'close', payload)
        self.assignments(scope, target['id'])
        self.output = {'report': self.find_record('close:' + source['id']), 'rollover': scope}

    def velocity(self):
        count = self.d.get('count', 6)
        require(isinstance(count, int) and count > 0, 'count must be a positive integer')
        completed = sorted([i for i in self.iterations if dt.date.fromisoformat(i['startDate']) + dt.timedelta(days=i['duration']) <= dt.datetime.now(dt.timezone.utc).date()], key=lambda i: i['startDate'])
        reports = []
        for iteration in completed[-max(count, 3):]:
            record = self.find_record('close:' + iteration['id'])
            corrections = [r for r in self.s['records'] if r['kind'] == 'correction' and r.get('target') == (record or {}).get('key')]
            total = record['points'] if record else None
            for correction in corrections:
                total = correction['replacement_points']
            reports.append({'iteration': iteration, 'points': total, 'status': 'missing' if record is None else 'restated' if corrections else 'recorded'})
        recent = reports[-3:]
        complete = bool(recent) and all(r['points'] is not None for r in recent)
        self.output = {'periods': reports[-count:], 'planning_sample_size': sum(r['points'] is not None for r in recent),
                       'planning_average': sum(r['points'] for r in recent) / len(recent) if complete else None,
                       'history_complete': complete, 'warnings': self.s['warnings'] +
                       ['Acceptance revoked; inspect and explicitly restate affected published periods: ' + r['target']
                        for r in self.s['records'] if r['kind'] == 'correction' and r.get('revoke') is True],
                       'meaning': 'Accepted Story Points; missing is not zero; no agent or individual productivity ranking'}

    def correct_history(self):
        target = self.records.get(self.d['target'])
        require(target and target['kind'] in ('close', 'accept') and target['project'] == self.pid, 'Correction targets a close report or acceptance record')
        require(self.d.get('reason') and self.d.get('decision') and self.d.get('evidence'), 'Correction needs reason, explicit authorizing decision and evidence')
        if target['kind'] == 'accept':
            require(self.d.get('revoke') is True, 'Acceptance correction requires explicit revoke:true')
            require(not self.find_record('revoke:' + target['story'].replace('/', '.').replace('#', '.'))
                    or self.find_record('revoke:' + target['story'].replace('/', '.').replace('#', '.'))['operation'] == self.op,
                    'Acceptance already revoked; inspect existing correction')
            self.history('revoke:' + target['story'].replace('/', '.').replace('#', '.'), 'correction', self.d)
            self.output = {'revoked': target['key'], 'next': 'Restate any published affected close total explicitly; original report remains visible until then'}
            return
        points = self.d.get('replacement_points')
        require(isinstance(points, (int, float)) and not isinstance(points, bool) and points >= 0, 'Nonnegative replacement total required')
        self.history('correction:' + self.op, 'correction', self.d)
        self.output = {'restated': target['key'], 'points': points}

    def release(self):
        repo = self.d['repo']
        require(repo in self.s['repos'], 'Select release repository')
        require(self.d.get('tag') and re.fullmatch(r'[0-9a-fA-F]{40}', self.d.get('target', '')), 'Provide release tag and full target commit SHA')
        milestone = self.d['milestone']
        require(isinstance(milestone, int), 'Milestone must be numeric')
        issues = [i for i in self.s['issues'].values() if i['ref'].split('#')[0] == repo and (i.get('milestone') or {}).get('number') == milestone]
        require(issues and all(i['state'] == 'closed' for i in issues), 'Milestone empty or has open issues')
        credit = {r['story'] for r in self.credits()}
        cancellations = self.d.get('cancellations', {})
        for issue in issues:
            if issue['state_reason'] == 'not_planned':
                require(cancellations.get(issue['ref']), 'Cancellation needs explicit scope decision: ' + issue['ref'])
            elif issue['kind'] == 'story':
                require(issue['ref'] in credit, 'Story lacks recorded acceptance: ' + issue['ref'])
        existing = self.api.pages(f'repos/{repo}/releases') if self.api else self.s.get('releases', [])
        matches = [r for r in existing if r['tag_name'] == self.d['tag']]
        require(len(matches) <= 1, 'Ambiguous release tag')
        if self.api:
            commit = self.api.request(f'repos/{repo}/commits/{encoded(self.d["target"])}')
            require(commit['sha'] == self.d['target'], 'Target commit did not resolve exactly')
            tags = self.api.pages(f'repos/{repo}/tags')
            matching_tags = [t for t in tags if t['name'] == self.d['tag']]
            require(not matching_tags or matching_tags[0]['commit']['sha'] == self.d['target'], 'Existing tag targets another commit')
        body = '\n'.join('- ' + i['title'] + ' (' + url(i['ref']) + ')' for i in issues if i['kind'] == 'story' and i['state_reason'] == 'completed')
        body += '\n\n<!-- github-xp:release:' + self.op + ':' + self.d['target'] + ' -->'
        if matches:
            require(matches[0]['draft'] and matches[0]['body'] == body, 'Existing release differs or is already published; inspect explicitly')
        else:
            self.action('Create draft release', f'repos/{repo}/releases', {'tag_name': self.d['tag'], 'target_commitish': self.d['target'], 'name': self.d.get('name', self.d['tag']), 'body': body, 'draft': True})
        self.action('Close release milestone', f'repos/{repo}/milestones/{milestone}', {'state': 'closed'}, 'PATCH')
        self.output = {'draft': self.d['tag'], 'target': self.d['target'], 'publication': 'left to existing release workflow'}

    def setup(self):
        if not self.pid:
            require(self.d.get('title'), 'New Project needs title; select context.project to reuse one')
            title = self.d['title'] + ' [xp:' + self.op + ']'
            existing = []
            if self.api:
                kind = self.s['owner']['kind']
                query = f'query($owner:String!,$cursor:String){{{kind}(login:$owner){{projectsV2(first:100,after:$cursor){{pageInfo{{hasNextPage endCursor}} nodes{{id number title url}}}}}}}}'
                existing = self.api.connection(query, {'owner': self.c['owner']}, lambda d: d[kind]['projectsV2'])
            matches = [p for p in existing if p['title'] == title]
            require(len(matches) <= 1, 'Duplicate setup identity; select a Project number explicitly')
            if matches:
                self.output = {'next': 'Set context.project to this number and rerun setup', 'project': matches[0]}
            else:
                self.mutation('createProjectV2', 'CreateProjectV2Input', {'ownerId': self.s['owner']['id'], 'title': title}, 'projectV2{id number url}')
                self.output = {'next': 'Use returned Project number in context.project, then rerun setup',
                               'identity': 'Title includes operation marker to reconcile creation after timeout'}
            return
        self.output = {'project': self.s['project'], 'fields': self.s['fields'], 'views': self.s['views'],
                       'workflows': self.s['workflows'], 'warnings': self.s['warnings'],
                       'manual': ['Inspect and disable Done-to-close; keep closed-to-Done',
                                  'Verify Planning grouping, Points sums and customer Backlog order',
                                  'Configure Story-filtered Insights scope chart and roadmap Iteration mapping',
                                  'Verify saved settings after reload; preserve existing templates through repository review']}
        if not self.d.get('configure'):
            return
        for key, datatype in [('points', 'NUMBER'), ('iteration', 'ITERATION')]:
            if key in self.fields:
                require(self.fields[key]['dataType'] == datatype, 'Existing field has wrong type: ' + key)
                continue
            payload = {'projectId': self.pid, 'name': self.c.get('fields', {}).get(key, DEFAULTS[key]), 'dataType': datatype}
            if key == 'iteration':
                definitions = self.d.get('iterations')
                require(definitions and all(x.get('title') and x.get('startDate') and isinstance(x.get('duration'), int) and x['duration'] > 0 for x in definitions), 'Provide iteration titles, startDate and positive duration')
                for definition in definitions:
                    dt.date.fromisoformat(definition['startDate'])
                payload['iterationConfiguration'] = {'startDate': definitions[0]['startDate'], 'duration': definitions[0]['duration'], 'iterations': definitions}
            self.mutation('createProjectV2Field', 'CreateProjectV2FieldInput', payload, 'projectV2Field{... on ProjectV2FieldCommon{id name}}')
        for repo in self.c['repos']:
            if repo not in {r['nameWithOwner'] for r in self.s.get('linked_repositories', [])}:
                self.mutation('linkProjectV2ToRepository', 'LinkProjectV2ToRepositoryInput',
                              {'projectId': self.pid, 'repositoryId': self.s['repos'][repo]['id']}, 'repository{id}')
            labels = self.api.pages(f'repos/{repo}/labels') if self.api else self.s.get('labels', {}).get(repo, [])
            names = {x['name'] for x in labels}
            for kind in ('story', 'task', 'spike'):
                if self.c.get('types', {}).get(kind) and self.s['repos'][repo]['owner_type'] == 'Organization':
                    # Type support is validated through the read endpoint, never guessed from a 403.
                    types = self.api.pages(f'repos/{repo}/issue-types') if self.api else self.s.get('types', {}).get(repo, [])
                    require(self.c['types'][kind] in {t['name'] for t in types}, 'Configured issue type is unavailable')
                    continue
                name = self.c.get('labels', {}).get(kind, 'type:' + kind)
                if name not in names:
                    self.action('Create XP classification label', f'repos/{repo}/labels', {'name': name, 'color': '0969da'})
            if 'xp:attention' not in names:
                self.action('Create attention label', f'repos/{repo}/labels', {'name': 'xp:attention', 'color': 'bf8700'})
        if not self.c.get('history'):
            repo = self.c['repos'][0]
            marker = '<!-- github-xp:history:' + self.pid + ' -->'
            matches = [i for i in self.s['issues'].values() if marker in (i.get('body') or '')]
            require(len(matches) <= 1, 'Multiple history issues; select explicitly')
            if matches:
                self.output['history'] = matches[0]['ref']
            else:
                self.action('Create planning history issue', f'repos/{repo}/issues', {'title': 'XP planning history', 'body': 'Plans, acceptance and iteration reports. Excluded from delivery scope.\n\n' + marker})
            self.output['history_next'] = 'Set context.history to the created/reused issue reference; do not add it to release milestones'
        # Only explicitly named views are configured; unrelated views are preserved.
        views = self.d.get('views', [])
        require(len({v['name'] for v in views}) == len(views), 'Duplicate requested view names')
        for view in views:
            matches = [v for v in self.s['views'] if v['name'] == view['name']]
            require(len(matches) <= 1, 'Ambiguous existing view; select/rename explicitly')
            require(view['layout'] in ('TABLE_LAYOUT', 'BOARD_LAYOUT', 'ROADMAP_LAYOUT'), 'Unsupported view layout')
            payload = {'name': view['name'], 'layout': view['layout'], 'filter': view['filter']}
            if view.get('visible_fields'):
                require(view['layout'] != 'ROADMAP_LAYOUT', 'Roadmap does not accept visible fields')
                ids = []
                for name in view['visible_fields']:
                    fields = [f for f in self.s['fields'] if f['name'] == name]
                    require(len(fields) == 1, 'Create fields first, then rerun view setup: ' + name)
                    ids.append(fields[0]['id'])
                payload['configuration'] = {'visibleFieldIds': ids}
            if matches:
                view_id = matches[0]['id']
            else:
                created = self.mutation('createProjectV2View', 'CreateProjectV2ViewInput',
                                        {'projectId': self.pid, 'name': view['name'], 'layout': view['layout']},
                                        'projectV2View{id name number}')
                view_id = {'$ref': created['$ref'] + '.projectV2View.id'}
            self.mutation('updateProjectV2View', 'UpdateProjectV2ViewInput',
                          {'viewId': view_id, **payload}, 'projectV2View{id name number filter}')


def resolve(value, results):
    if isinstance(value, dict):
        if set(value) == {'$ref'}:
            parts = value['$ref'].split('.')
            result = results[parts[0]]
            for part in parts[1:]:
                result = result[part]
            return result
        if set(value) == {'$path'}:
            return ''.join(str(resolve(x, results)) for x in value['$path'])
        return {k: resolve(v, results) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(x, results) for x in value]
    return value


def execute(api, actions):
    results = {}
    for action in actions:
        try:
            if action.get('guard'):
                guard = action['guard']
                if 'item' in guard:
                    query = '''query($id:ID!,$name:String!){node(id:$id){... on ProjectV2Item{
                        fieldValueByName(name:$name){... on ProjectV2ItemFieldNumberValue{number}
                        ... on ProjectV2ItemFieldIterationValue{iterationId}
                        ... on ProjectV2ItemFieldSingleSelectValue{optionId}}}}}'''
                    current = api.gql(query, {'id': guard['item'], 'name': guard['field_name']})['node']['fieldValueByName']
                    actual_value = (current or {}).get(guard['value_key'])
                    require(actual_value in (guard['expected'], guard['target']), 'Concurrent Project field edit; replan')
                    if actual_value == guard['target']:
                        results[action['id']] = {'already_applied': True}
                        continue
                else:
                    actual = api.request(guard['path'])
                    require(all(actual.get(k) == v for k, v in guard.items() if k != 'path'),
                            'Concurrent edit or failed completion guard: ' + guard['path'])
            result = api.request(resolve(action['path'], results), resolve(action['body'], results), action['method'])
            results[action['id']] = result
            print(json.dumps({'completed': action['id'], 'description': action['description'], 'result': result}), flush=True)
        except (XPError, KeyError, TypeError) as exc:
            raise XPError(f'Stopped at {action["id"]}; completed {list(results)}. Re-read GitHub and rerun the same operation ID/request. {exc}') from exc
    return results


def load_json(path):
    return json.load(sys.stdin) if path == '-' else json.loads(Path(path).read_text())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=COMMANDS, help='Also accepts xp- prefixed command names')
    parser.add_argument('--context', required=True, help='Target configuration JSON; see references/github.md')
    parser.add_argument('--input', default=None, help='Reviewed request JSON file, or - for stdin')
    parser.add_argument('--operation-id', default='inspect', help='Stable unique ID reused for retries; required for mutations')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--apply', action='store_true', help='Execute after preview and concurrent-state check; authorization must already exist')
    modes.add_argument('--dry-run', action='store_true', help='Read/preview only (the default); no local or remote writes')
    parser.add_argument('--fixture', help='Offline snapshot JSON; mutations forbidden')
    parser.add_argument('--keyring', action='store_true', help='Explicitly ignore GH_TOKEN/GITHUB_TOKEN for this subprocess only')
    args_list = sys.argv[1:] if argv is None else argv
    if args_list and args_list[0].startswith('xp-'):
        args_list = [args_list[0][3:]] + args_list[1:]
    args = parser.parse_args(args_list)
    try:
        context = load_json(args.context)
        data = load_json(args.input) if args.input else {}
        require(re.fullmatch(r'[A-Za-z0-9_.-]+', args.operation_id), 'Operation ID must contain letters, digits, dot, underscore or hyphen')
        require(not (args.fixture and args.apply), 'Offline fixtures cannot authorize writes')
        api = None if args.fixture else GitHub(keyring=args.keyring)
        state = load_json(args.fixture) if args.fixture else snapshot(api, context)
        planner = Planner(state, context, data, args.operation_id, api)
        if args.command not in ('setup', 'velocity'):
            require(planner.pid, 'Select a Project first')
            planner.safe_workflows()
        getattr(planner, args.command.replace('-', '_'))()
        if planner.actions:
            require(args.operation_id != 'inspect', 'Supply stable --operation-id for a mutation plan, including dry-run')
        print(json.dumps({'mode': 'apply' if args.apply else 'preview', 'output': planner.output,
                          'actions': planner.actions}, indent=2), flush=True)
        if args.apply and planner.actions:
            fresh = snapshot(api, context)
            require(digest(fresh) == digest(state), 'GitHub changed during planning. Re-read and review a fresh preview.')
            execute(api, planner.actions)
        return 0
    except (XPError, KeyError, ValueError, TypeError) as exc:
        print(json.dumps({'error': str(exc), 'writes': 'none, or completed steps already printed; inspect before retrying'}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
