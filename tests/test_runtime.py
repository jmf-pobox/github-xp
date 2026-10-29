"""Behavioral tests using synthetic snapshots and fake gh processes; never calls GitHub."""
import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/github-xp/scripts'
sys.path.insert(0, str(SCRIPTS))
import github  # noqa: E402
import xp  # noqa: E402


CTX = {'owner': 'acme', 'repos': ['acme/app'], 'project': 1, 'history': 'acme/app#99'}
PR = 'https://github.com/acme/app/pull/21'


def state():
    fields = [
        {'id': 'points', 'name': 'Points', 'dataType': 'NUMBER'},
        {'id': 'status', 'name': 'Status', 'dataType': 'SINGLE_SELECT', 'options': [
            {'id': 'todo', 'name': 'Todo'}, {'id': 'doing', 'name': 'In Progress'}, {'id': 'done', 'name': 'Done'}]},
        {'id': 'iteration', 'name': 'Iteration', 'dataType': 'ITERATION', 'configuration': {
            'iterations': [], 'completedIterations': [
                {'id': 'i1', 'title': 'One', 'startDate': '2020-01-01', 'duration': 7},
                {'id': 'i2', 'title': 'Two', 'startDate': '2020-01-08', 'duration': 7},
                {'id': 'i3', 'title': 'Three', 'startDate': '2020-01-15', 'duration': 7}]}}
    ]
    result = {'owner': {'login': 'acme', 'id': 'owner', 'kind': 'user'},
              'project': {'id': 'project', 'number': 1, 'title': 'XP', 'url': 'https://github.com/users/acme/projects/1'},
              'repos': {'acme/app': {'id': 'repo', 'default_branch': 'trunk', 'owner_type': 'User'}},
              'issues': {}, 'fields': fields, 'items': [], 'records': [], 'views': [], 'workflows': [], 'warnings': [],
              'prs': {'acme/app#21': {'merged': True, 'base': {'ref': 'trunk'}, 'head': {'sha': 'abc'}, 'merged_at': '2020-01-02T01:30:00Z'}}}
    add_issue(result, 1, 'story', points=3, children=['acme/app#2', 'acme/app#3'])
    add_issue(result, 2, 'task')
    add_issue(result, 3, 'task', closed=True)
    return result


def add_issue(s, number, kind, *, points=None, closed=False, children=None, repo='acme/app'):
    ref = f'{repo}#{number}'
    issue = {'ref': ref, 'number': number, 'node_id': f'I_{repo}_{number}', 'id': number,
             'title': 'Example ' + str(number), 'body': '## Acceptance\nAC1 useful outcome',
             'state': 'closed' if closed else 'open', 'state_reason': 'completed' if closed else None,
             'kind': kind, 'children': children or [], 'blockers': [], 'assignees': [],
             'updated_at': '2020-01-01T00:00:00Z', 'milestone': {'number': 1}}
    s['issues'][ref] = issue
    values = {'iteration': {'iterationId': 'i1'}, 'status': {'optionId': 'done' if closed else 'todo'}}
    if points is not None:
        values['points'] = {'number': points}
    s['items'].append({'id': 'item-' + str(number), 'ref': ref, 'isArchived': False, 'values': values})
    return issue


def evidence():
    return {'revision': 'abc', 'verified_revision': 'abc', 'tests': ['unit suite passed'],
            'criteria': {'AC1': 'demo recording at revision abc'}, 'gates_passed': True,
            'prs': [PR], 'pr_revisions': {PR: 'abc'}}


def acceptance():
    return {'story': 'acme/app#1', 'iteration': 'i1',
            'criteria': {'source': 'spec.md#acceptance', 'revision': 'spec-a', 'items': ['AC1'], 'verified': True},
            'evidence': evidence(), 'decision': {'authority': 'owner', 'reference': 'recorded operator demo',
            'accepted': True, 'revision': 'abc', 'at': '2020-01-02T01:00:00Z'},
            'completed_at': '2020-01-02T02:00:00Z'}


def planner(s=None, data=None, op='test'):
    return xp.Planner(s or state(), CTX, data or {}, op)


def set_iteration(s, ref, iteration):
    next(i for i in s['items'] if i['ref'] == ref)['values']['iteration']['iterationId'] = iteration


def persist_records(p, s):
    s['records'] = copy.deepcopy(list(p.records.values()))


def field_updates(p, field='iteration'):
    return [a['body']['variables']['input'] for a in p.actions
            if a['path'] == 'graphql' and 'updateProjectV2ItemFieldValue' in a['body']['query']
            and a['body']['variables']['input']['fieldId'] == field]


class PlanningTests(unittest.TestCase):
    def test_plan_only_moves_open_children_and_keeps_points(self):
        p = planner(data={'iteration': 'i2', 'stories': ['acme/app#1'], 'availability': 'one review hour'})
        p.plan()
        self.assertEqual({a['itemId'] for a in field_updates(p)}, {'item-1', 'item-2'})
        self.assertFalse(field_updates(p, 'points'))
        self.assertEqual(p.output['points'], 3)
        self.assertEqual(p.actions[0]['description'], 'Record plan')

    def test_partial_plan_retry_does_not_duplicate_record_or_move_completed_task(self):
        s = state()
        request = {'iteration': 'i2', 'stories': ['acme/app#1'], 'availability': 'one review hour'}
        first = planner(s, request)
        first.plan()
        persist_records(first, s)
        set_iteration(s, 'acme/app#1', 'i2')
        retry = planner(s, request)
        retry.plan()
        self.assertEqual([x['itemId'] for x in field_updates(retry)], ['item-2'])
        self.assertFalse(any(a['description'] == 'Record plan' for a in retry.actions))

    def test_retry_refuses_concurrent_assignment(self):
        s = state()
        request = {'iteration': 'i2', 'stories': ['acme/app#1'], 'availability': 'one hour'}
        first = planner(s, request)
        first.plan()
        persist_records(first, s)
        set_iteration(s, 'acme/app#2', 'i3')
        with self.assertRaisesRegex(github.XPError, 'Concurrent iteration edit'):
            planner(s, request).plan()

    def test_changed_request_cannot_reuse_plan_operation(self):
        s = state()
        request = {'iteration': 'i2', 'stories': ['acme/app#1'], 'availability': 'one hour'}
        first = planner(s, request)
        first.plan()
        persist_records(first, s)
        with self.assertRaisesRegex(github.XPError, 'Changed plan request'):
            planner(s, {**request, 'iteration': 'i3'}).plan()

    def test_missing_points_is_unknown_not_zero(self):
        s = state()
        s['items'][0]['values'].pop('points')
        with self.assertRaisesRegex(github.XPError, 'unknown'):
            planner(s, {'iteration': 'i2', 'stories': ['acme/app#1'], 'availability': 'one hour'}).plan()

    def test_archive_is_not_silently_changed(self):
        s = state()
        s['items'][0]['isArchived'] = True
        with self.assertRaisesRegex(github.XPError, 'Unarchive'):
            planner(s, {'iteration': 'i2', 'stories': ['acme/app#1'], 'availability': 'one hour'}).plan()

    def test_close_report_precedes_rollover_and_resume_uses_original_target(self):
        s = state()
        setup = planner(s, {'iteration': 'i1', 'stories': ['acme/app#1'], 'availability': 'one hour'}, 'plan-op')
        setup.plan()
        persist_records(setup, s)
        request = {'iteration': 'i1', 'next_iteration': 'i2', 'reflection': 'smaller slices'}
        first = planner(s, request)
        first.close_iteration()
        self.assertEqual(first.actions[0]['description'], 'Record close')
        self.assertEqual(first.output['report']['points'], 0)
        self.assertEqual({a['itemId'] for a in field_updates(first)}, {'item-1', 'item-2'})
        persist_records(first, s)
        set_iteration(s, 'acme/app#1', 'i2')
        retry = planner(s, request)
        retry.close_iteration()
        self.assertEqual([a['itemId'] for a in field_updates(retry)], ['item-2'])
        with self.assertRaisesRegex(github.XPError, 'original close request'):
            planner(s, {**request, 'next_iteration': 'i3'}).close_iteration()

    def test_close_without_plan_refuses_fabricated_commitment(self):
        with self.assertRaisesRegex(github.XPError, 'No recorded commitment'):
            planner(data={'iteration': 'i1', 'next_iteration': 'i2'}).close_iteration()

    def test_unknown_next_iteration_refused(self):
        with self.assertRaises(github.XPError):
            planner(data={'iteration': 'i1', 'next_iteration': 'missing'}).close_iteration()


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.s = state()
        self.s['issues']['acme/app#2'].update(state='closed', state_reason='completed')
        self.d = acceptance()

    def test_valid_acceptance_has_pending_and_final_records_with_closure_guard(self):
        p = planner(self.s, self.d)
        p.accept()
        descriptions = [a['description'] for a in p.actions]
        self.assertEqual(descriptions[0], 'Record accept-intent')
        self.assertEqual(descriptions[-1], 'Record accept')
        self.assertEqual(p.actions[-1]['guard']['state_reason'], 'completed')
        self.assertEqual(p.output['points'], 3)

    def test_open_task_blocks_acceptance_even_if_tests_pass(self):
        self.s['issues']['acme/app#2']['state'] = 'open'
        with self.assertRaisesRegex(github.XPError, 'Task incomplete'):
            planner(self.s, self.d).accept()

    def test_cancelled_task_is_not_completed(self):
        self.s['issues']['acme/app#2']['state_reason'] = 'not_planned'
        with self.assertRaisesRegex(github.XPError, 'Task incomplete/cancelled'):
            planner(self.s, self.d).accept()

    def test_cancelled_story_cannot_earn_credit(self):
        self.s['issues']['acme/app#1'].update(state='closed', state_reason='not_planned')
        with self.assertRaisesRegex(github.XPError, 'Cancelled Story'):
            planner(self.s, self.d).accept()

    def test_stale_review_refused(self):
        self.d['evidence']['verified_revision'] = 'old'
        with self.assertRaisesRegex(github.XPError, 'stale'):
            planner(self.s, self.d).accept()

    def test_stale_decision_refused(self):
        self.d['decision']['revision'] = 'old'
        with self.assertRaisesRegex(github.XPError, 'different revision'):
            planner(self.s, self.d).accept()

    def test_absent_customer_decision_refused(self):
        del self.d['decision']
        with self.assertRaisesRegex(github.XPError, 'acceptance decision'):
            planner(self.s, self.d).accept()

    def test_empty_criteria_refused(self):
        self.d['criteria']['items'] = []
        with self.assertRaisesRegex(github.XPError, 'nonempty'):
            planner(self.s, self.d).accept()

    def test_missing_criterion_evidence_refused(self):
        self.d['criteria']['items'].append('AC2')
        with self.assertRaisesRegex(github.XPError, 'Missing criterion evidence'):
            planner(self.s, self.d).accept()

    def test_merged_pr_must_target_actual_non_main_default_branch(self):
        planner(self.s, self.d).accept()  # trunk is the actual default; succeeds.
        self.s['prs']['acme/app#21']['base']['ref'] = 'main'
        with self.assertRaisesRegex(github.XPError, 'actual default branch'):
            planner(self.s, self.d).accept()

    def test_pr_head_must_match_inspected_revision(self):
        self.s['prs']['acme/app#21']['head']['sha'] = 'changed'
        with self.assertRaisesRegex(github.XPError, 'inspected revision'):
            planner(self.s, self.d).accept()

    def test_intent_without_final_credit_does_not_count(self):
        first = planner(self.s, self.d)
        first.accept()
        self.s['records'] = [r for r in first.records.values() if r['kind'] == 'accept-intent']
        retry = planner(self.s, self.d)
        self.assertEqual(retry.credits(), [])
        retry.accept()
        self.assertFalse(any(a['description'] == 'Record accept-intent' for a in retry.actions))
        self.assertEqual(retry.actions[-1]['description'], 'Record accept')

    def test_reaccept_reopened_story_closes_without_second_credit(self):
        first = planner(self.s, self.d)
        first.accept()
        persist_records(first, self.s)
        retry = planner(self.s, self.d, 'reaccept-op')
        retry.accept()
        self.assertTrue(any(a['method'] == 'PATCH' and a['body'].get('state') == 'closed' for a in retry.actions))
        self.assertFalse(any(a['description'] == 'Record accept' for a in retry.actions))

    def test_credit_cannot_precede_required_integration(self):
        self.s['prs']['acme/app#21']['merged_at'] = '2020-01-09T01:30:00Z'
        with self.assertRaises(github.XPError):
            planner(self.s, self.d).accept()

    def test_tiny_story_requires_explicit_unsplit(self):
        self.s['issues']['acme/app#1']['children'] = []
        with self.assertRaisesRegex(github.XPError, 'unsplit'):
            planner(self.s, self.d).accept()
        self.d['unsplit'] = True
        planner(self.s, self.d).accept()

    def test_finish_unsplit_story_does_not_close_it(self):
        self.s['issues']['acme/app#1']['children'] = []
        p = planner(self.s, {'issue': 'acme/app#1', 'unsplit': True, 'evidence': evidence()})
        p.finish()
        self.assertFalse(any(a['method'] == 'PATCH' for a in p.actions))
        self.assertTrue(p.output['story_left_open'])


class HandoffTests(unittest.TestCase):
    def brief(self):
        return {'criteria': ['AC1'], 'scope': 'Task #2 only', 'instructions': ['AGENTS.md'],
                'workflow': 'existing repo workflow', 'dependencies': 'none',
                'allowed_actions': ['edit Task files', 'run tests'], 'expected_evidence': ['revision', 'tests'],
                'executor': 'human or existing engineering agent', 'started': True}

    def test_start_reuses_workflow_without_branch_or_pr_calls(self):
        p = planner(data={'issue': 'acme/app#2', 'brief': self.brief()})
        p.start()
        self.assertTrue(field_updates(p, 'status'))
        self.assertTrue(all(a['path'] in ('graphql', 'repos/acme/app/issues/99/comments') for a in p.actions))

    def test_start_refuses_open_blocker(self):
        s = state()
        add_issue(s, 4, 'spike')
        s['issues']['acme/app#2']['blockers'] = ['acme/app#4']
        with self.assertRaisesRegex(github.XPError, 'blocked'):
            planner(s, {'issue': 'acme/app#2', 'brief': self.brief()}).start()

    def test_cancelled_blocker_needs_explicit_scope_resolution(self):
        s = state()
        blocker = add_issue(s, 4, 'spike', closed=True)
        blocker['state_reason'] = 'not_planned'
        s['issues']['acme/app#2']['blockers'] = ['acme/app#4']
        with self.assertRaises(github.XPError):
            planner(s, {'issue': 'acme/app#2', 'brief': self.brief()}).start()

    def test_start_preserves_someone_elses_assignment(self):
        s = state()
        s['issues']['acme/app#2']['assignees'] = [{'login': 'someone'}]
        with self.assertRaisesRegex(github.XPError, 'Preserve existing assignees'):
            planner(s, {'issue': 'acme/app#2', 'brief': self.brief(), 'assignee': 'new-owner'}).start()

    def test_shared_credentials_do_not_create_review_approval(self):
        p = planner(data={'issue': 'acme/app#2', 'brief': self.brief(), 'assignee': 'owner'})
        p.start()
        self.assertFalse(any('review' in str(a['path']) for a in p.actions))
        self.assertEqual([a['body']['assignees'] for a in p.actions if a['method'] == 'PATCH'], [['owner']])


class CreationAndHistoryTests(unittest.TestCase):
    def test_story_retry_recovers_after_create_before_membership(self):
        s = state()
        issue = add_issue(s, 8, 'story')
        issue.update(title='Useful outcome', body='AC1: works\n\n<!-- github-xp:issue:test:story -->')
        s['items'] = [i for i in s['items'] if i['ref'] != issue['ref']]
        p = planner(s, {'repo': 'acme/app', 'title': 'Useful outcome', 'body': 'AC1: works', 'criteria_reviewed': True, 'points': 2})
        p.story()
        self.assertFalse(any(a['description'] == 'Create story' for a in p.actions))
        self.assertEqual(p.actions[0]['description'], 'addProjectV2ItemById')

    def test_operation_marker_in_other_repo_cannot_reuse_wrong_issue(self):
        s = state()
        s['repos']['acme/other'] = {'id': 'other', 'owner_type': 'User', 'default_branch': 'main'}
        issue = add_issue(s, 8, 'story', repo='acme/other')
        issue.update(title='Useful outcome', body='AC1: works\n\n<!-- github-xp:issue:test:story -->')
        p = planner(s, {'repo': 'acme/app', 'title': 'Useful outcome', 'body': 'AC1: works', 'criteria_reviewed': True})
        try:
            p.story()
        except github.XPError:
            return  # Explicit operation conflict is safe too.
        self.assertTrue(any(a['description'] == 'Create story' for a in p.actions))

    def test_tasks_never_get_points(self):
        with self.assertRaisesRegex(github.XPError, 'Tasks never receive Points'):
            planner(data={'story': 'acme/app#1', 'tasks': [{'key': 't', 'points': 2}]}).split()

    def test_spikes_never_get_points(self):
        with self.assertRaisesRegex(github.XPError, 'Only Stories'):
            planner(data={'repo': 'acme/app', 'kind': 'spike', 'title': 'Learn', 'body': 'Question', 'timebox': '30m', 'question': 'Why?', 'points': 2}).story()

    def test_duplicate_history_markers_refused(self):
        rec = {'schema': 1, 'key': 'project:plan:a', 'kind': 'plan'}
        body = '<!-- github-xp:v1:project:plan:a -->\n```json\n' + json.dumps(rec) + '\n```'
        with self.assertRaisesRegex(github.XPError, 'Duplicate history key'):
            github.read_records([{'id': 1, 'body': body}, {'id': 2, 'body': body}])

    def test_history_payload_cannot_override_identity_metadata(self):
        p = planner()
        with self.assertRaises(github.XPError):
            p.history('correction:test', 'correction', {'key': 'other-project:accept:fake', 'points': 100})

    def test_malformed_history_not_silently_ignored(self):
        with self.assertRaisesRegex(github.XPError, 'Malformed XP history'):
            github.read_records([{'id': 1, 'body': '<!-- github-xp:v1:bad -->not json'}])

    def test_zero_periods_in_average_missing_period_not_manufactured(self):
        s = state()
        for ident, points in [('i1', 6), ('i2', 0), ('i3', 3)]:
            s['records'].append({'schema': 1, 'key': 'project:close:' + ident, 'kind': 'close', 'project': 'project', 'iteration': ident, 'points': points})
        p = planner(s)
        p.velocity()
        self.assertEqual(p.output['planning_average'], 3)
        s['records'].pop(1)
        p = planner(s)
        p.velocity()
        self.assertIsNone(p.output['planning_average'])
        self.assertEqual(p.output['planning_sample_size'], 2)
        self.assertEqual(p.output['periods'][1]['status'], 'missing')

    def test_no_history_reports_unknown(self):
        p = planner()
        p.velocity()
        self.assertIsNone(p.output['planning_average'])
        self.assertEqual(p.output['planning_sample_size'], 0)
        self.assertFalse(p.actions)

    def test_auto_close_workflow_refused(self):
        s = state()
        s['workflows'] = [{'name': 'Auto-close issue', 'enabled': True}]
        with self.assertRaisesRegex(github.XPError, 'Disable Done-to-close'):
            planner(s).safe_workflows()

    def test_release_retry_reuses_draft_after_partial_success(self):
        s = state()
        for issue in s['issues'].values():
            issue.update(state='closed', state_reason='completed')
        s['records'] = [{'schema': 1, 'key': 'project:accept:I_acme/app_1', 'kind': 'accept', 'project': 'project', 'story': 'acme/app#1', 'points': 3, 'iteration': 'i1'}]
        request = {'repo': 'acme/app', 'milestone': 1, 'tag': 'v1', 'target': 'a' * 40}
        first = planner(s, request)
        first.release()
        body = first.actions[0]['body']['body']
        s['releases'] = [{'tag_name': 'v1', 'draft': True, 'body': body}]
        retry = planner(s, request)
        retry.release()
        self.assertEqual(len(retry.actions), 1)
        self.assertEqual(retry.actions[0]['description'], 'Close release milestone')


class TransportTests(unittest.TestCase):
    def test_rest_pagination_includes_second_page(self):
        calls = []
        class API(github.GitHub):
            def request(self, path, body=None, method='GET'):
                calls.append(path)
                return list(range(100)) if path.endswith('&page=1') else [100]
        values = API().pages('repos/acme/app/issues?state=all')
        self.assertEqual(len(values), 101)
        self.assertIn('&per_page=100&page=2', calls[-1])

    def test_graphql_pagination_advances_cursor(self):
        calls = []
        class API(github.GitHub):
            def gql(self, query, variables=None):
                calls.append(variables['cursor'])
                return {'nodes': [1 if variables['cursor'] is None else 2],
                        'pageInfo': {'hasNextPage': variables['cursor'] is None, 'endCursor': 'next'}}
        self.assertEqual(API().connection('q', {}, lambda d: d), [1, 2])
        self.assertEqual(calls, [None, 'next'])

    def test_graphql_error_even_with_successful_exit_is_failure(self):
        def runner(*args, **kwargs):
            return subprocess.CompletedProcess(args, 0, '{"errors":[{"message":"denied"}]}', '')
        with self.assertRaisesRegex(github.XPError, 'GraphQL errors'):
            github.GitHub(runner=runner).request('graphql', {'query': 'query{x}'}, 'POST')

    def test_user_text_is_json_stdin_never_shell_code(self):
        captured = {}
        malicious = 'a `touch /tmp/nope` $(echo token) " \\n'
        def runner(args, **kwargs):
            captured.update(args=args, kwargs=kwargs)
            return subprocess.CompletedProcess(args, 0, '{}', '')
        github.GitHub(runner=runner).request('repos/acme/app/issues', {'title': malicious}, 'POST')
        self.assertNotIn(malicious, captured['args'])
        self.assertNotIn('shell', captured['kwargs'])
        self.assertEqual(json.loads(captured['kwargs']['input'])['title'], malicious)

    def test_mutation_timeout_is_not_blindly_retried(self):
        calls = []
        def runner(args, **kwargs):
            calls.append(args)
            raise subprocess.TimeoutExpired(args, 90)
        with self.assertRaisesRegex(github.XPError, 'reconcile before retrying'):
            github.GitHub(runner=runner).request('repos/acme/app/issues', {'title': 'x'}, 'POST')
        self.assertEqual(len(calls), 1)

    def test_executor_checks_guard_before_write_and_stops(self):
        calls = []
        class API:
            def request(self, path, body=None, method='GET'):
                calls.append(method)
                return {'updated_at': 'new'}
        action = {'id': 'step1', 'description': 'close', 'path': 'issue', 'method': 'PATCH',
                  'body': {'state': 'closed'}, 'guard': {'path': 'issue', 'updated_at': 'old'}}
        with self.assertRaisesRegex(github.XPError, 'Concurrent edit'):
            xp.execute(API(), [action])
        self.assertEqual(calls, ['GET'])

    def project_field_action(self):
        p = planner()
        p.set_field(p.issue('acme/app#1'), 'iteration', 'i2')
        return p.actions[0]

    def test_project_field_conflict_after_preflight_stops_before_write(self):
        calls = []
        class API:
            def gql(self, query, variables):
                calls.append(('read', variables))
                return {'node': {'fieldValueByName': {'iterationId': 'i3'}}}

            def request(self, *args):
                calls.append(('write', args))
                raise AssertionError('Must not write after conflicting field change')
        action = self.project_field_action()
        with self.assertRaisesRegex(github.XPError, 'Concurrent Project field edit'):
            xp.execute(API(), [action])
        self.assertEqual([kind for kind, _ in calls], ['read'])

    def test_project_field_already_at_target_skips_mutation(self):
        class API:
            def gql(self, query, variables):
                return {'node': {'fieldValueByName': {'iterationId': 'i2'}}}

            def request(self, *args):
                raise AssertionError('Already applied value must not be written again')
        result = xp.execute(API(), [self.project_field_action()])
        self.assertEqual(result['step1'], {'already_applied': True})

    def test_project_field_expected_value_permits_one_mutation(self):
        calls = []
        class API:
            def gql(self, query, variables):
                return {'node': {'fieldValueByName': {'iterationId': 'i1'}}}

            def request(self, *args):
                calls.append(args)
                return {'data': {'updateProjectV2ItemFieldValue': {'projectV2Item': {'id': 'item-1'}}}}
        with contextlib.redirect_stdout(io.StringIO()):
            xp.execute(API(), [self.project_field_action()])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1]['variables']['input']['value']['iterationId'], 'i2')

    def test_offline_dry_run_has_no_subprocess_or_filesystem_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'context.json').write_text(json.dumps(CTX))
            (root / 'state.json').write_text(json.dumps(state()))
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            with patch('subprocess.run', side_effect=AssertionError('No subprocess allowed')):
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    status = xp.main(['velocity', '--context', str(root / 'context.json'), '--fixture', str(root / 'state.json'), '--dry-run'])
            self.assertEqual(status, 0)
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})

    def test_apply_fixture_is_refused_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'context.json').write_text(json.dumps(CTX))
            with patch('subprocess.run', side_effect=AssertionError('No subprocess allowed')):
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    status = xp.main(['velocity', '--context', str(root / 'context.json'), '--fixture', str(root / 'missing.json'), '--apply'])
            self.assertEqual(status, 1)


if __name__ == '__main__':
    unittest.main()
