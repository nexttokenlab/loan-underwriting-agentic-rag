import unittest
from underwriting.core import Workspace, run
from underwriting.models import Replay

class Sequence:
    def __init__(self, actions):
        self.actions = iter(actions)
        self.observations = []
    def respond(self, messages, tools, system):
        self.observations.append(str(messages))
        return next(self.actions)

def call(name, args, ident='1'):
    return {'type':'tool_use','id':ident,'name':name,'input':args}

class CoreTests(unittest.TestCase):
    def test_applicant_isolation(self):
        ws = Workspace()
        self.assertNotIn('A2-APPLICATION', [d['id'] for d in ws.search('salary income')])
        with self.assertRaises(ValueError):
            ws.execute('search_documents', {'query':'salary','application_id':'APP-002'})

    def test_policy_version_and_product(self):
        self.assertEqual([d['id'] for d in Workspace().search('bonus', True)], ['P-BONUS-V2'])
        self.assertEqual([d['id'] for d in Workspace(as_of='2025-12-31').search('bonus', True)], ['P-BONUS-V1'])
        self.assertEqual(Workspace(as_of='2027-01-01').search('bonus', True), [])

    def test_dti_requires_retrieved_authorized_source(self):
        ws = Workspace()
        with self.assertRaises(ValueError): ws.execute('calculate_dti', {'source_id':'A1-APPLICATION'})
        ws.search('income')
        self.assertEqual(ws.execute('calculate_dti', {'source_id':'A1-APPLICATION'})['illustrative_dti_percent'], '30.00')
        with self.assertRaises(ValueError): ws.execute('calculate_dti', {'source_id':'A2-APPLICATION'})

    def test_fabricated_citation_rejected(self):
        with self.assertRaises(ValueError):
            Workspace().execute('submit_assessment', {'summary':'x','citations':['invented'],'missing_evidence':[]})

    def test_budget_counts_individual_calls(self):
        model = Sequence([[call('list_documents', {}), call('search_policy', {'query':'bonus'}, '2')]])
        result = run(model, Workspace(), 'review', max_calls=1)
        self.assertEqual(len(result['trace']), 1)
        self.assertEqual(result['reason'], 'Tool budget exhausted')

    def test_repeated_action_returns_error(self):
        model = Sequence([[call('list_documents', {})], [call('list_documents', {}, '2')]])
        result = run(model, Workspace(), 'review', 2)
        self.assertIn('Repeated', result['trace'][1]['result']['error'])

    def test_evidence_is_returned_to_model(self):
        model = Sequence([[call('search_documents', {'query':'bonus'})], []])
        run(model, Workspace(), 'review')
        self.assertIn('variable bonus', model.observations[1])

    def test_direct_unvalidated_answer_not_accepted(self):
        model = Sequence([[{'type':'text','text':'Approved'}]])
        result = run(model, Workspace(), 'review')
        self.assertNotIn('assessment', result)
        self.assertEqual(result['status'], 'human_review_required')

    def test_replay_completes_with_missing_history(self):
        result = run(Replay(), Workspace(), 'review')
        self.assertEqual(len(result['trace']), 6)
        self.assertIn('2024', result['assessment']['missing_evidence'][0])
        self.assertEqual(result['assessment']['status'], 'human_review_required')

    def test_unknown_tool_cannot_execute(self):
        with self.assertRaises(ValueError): Workspace().execute('approve_loan', {})

if __name__ == '__main__': unittest.main()
