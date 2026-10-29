"""Explicit credit revocation and published total restatement are distinct operations."""
import unittest

from test_runtime import acceptance, github, persist_records, planner, state


class CorrectionTests(unittest.TestCase):
    def setUp(self):
        self.s = state()
        self.s['issues']['acme/app#2'].update(state='closed', state_reason='completed')
        first = planner(self.s, acceptance())
        first.accept()
        persist_records(first, self.s)
        self.credit = next(r for r in self.s['records'] if r['kind'] == 'accept')

    def revoke(self):
        request = {'target': self.credit['key'], 'revoke': True, 'reason': 'Demo used wrong data',
                   'decision': 'Owner explicitly invalidated acceptance', 'evidence': 'Recorded correction'}
        p = planner(self.s, request, 'revoke')
        p.correct_history()
        persist_records(p, self.s)

    def test_revoked_credit_excluded_from_future_close_and_release(self):
        self.revoke()
        self.assertEqual(planner(self.s).credits(), [])

    def test_revoked_story_cannot_silently_earn_new_credit(self):
        self.revoke()
        with self.assertRaisesRegex(github.XPError, 'revoked'):
            planner(self.s, acceptance(), 'again').accept()

    def test_velocity_warns_about_revocation_without_rewriting_report(self):
        self.s['records'].append({'schema': 1, 'key': 'project:close:i1', 'kind': 'close',
                                 'project': 'project', 'iteration': 'i1', 'points': 3})
        self.revoke()
        p = planner(self.s)
        p.velocity()
        self.assertEqual(p.output['periods'][0]['points'], 3)
        self.assertTrue(p.output['warnings'])
        correction = planner(self.s, {'target': 'project:close:i1', 'replacement_points': 0,
                                     'reason': 'Invalid credit revoked', 'decision': 'Owner agreed',
                                     'evidence': self.credit['key']}, 'restate')
        correction.correct_history()
        persist_records(correction, self.s)
        p = planner(self.s)
        p.velocity()
        self.assertEqual(p.output['periods'][0]['points'], 0)
        self.assertEqual(p.output['periods'][0]['status'], 'restated')
