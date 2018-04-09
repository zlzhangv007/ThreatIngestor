import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import sources.twitter


class TestTwitter(unittest.TestCase):

    @patch('twitter.Twitter')
    def setUp(self, Twitter):
        self.twitter = sources.twitter.Twitter('a', 'b', 'c', 'd')

    def teadDown(self):
        self.twitter.api.reset_mock()

    @patch('twitter.Twitter')
    def test_init_detects_search_type(self, Twitter):
        # default to search
        twitter = sources.twitter.Twitter('a', 'b', 'c', 'd')
        self.assertEquals(twitter.endpoint._mock_name, 'tweets')

        # slug and owner_screen_name => list
        twitter = sources.twitter.Twitter('a', 'b', 'c', 'd', slug='test', owner_screen_name='test')
        self.assertEquals(twitter.endpoint._mock_name, 'statuses')
        twitter = sources.twitter.Twitter('a', 'b', 'c', 'd', slug='test')
        self.assertEquals(twitter.endpoint._mock_name, 'tweets')
        twitter = sources.twitter.Twitter('a', 'b', 'c', 'd', owner_screen_name='test')
        self.assertEquals(twitter.endpoint._mock_name, 'tweets')

        # screen_name or user_id => user
        twitter = sources.twitter.Twitter('a', 'b', 'c', 'd', screen_name='test')
        self.assertEquals(twitter.endpoint._mock_name, 'user_timeline')
        twitter = sources.twitter.Twitter('a', 'b', 'c', 'd', user_id=1)
        self.assertEquals(twitter.endpoint._mock_name, 'user_timeline')

    def test_run_respects_saved_state(self):
        self.twitter.run('12345')
        self.twitter.endpoint.assert_called_once_with(since_id='12345')

    def test_run_returns_newest_tweet_id_as_saved_state(self):
        self.twitter.endpoint.return_value = [
            {
                'text': 'test',
                'id_str': '12346',
            },
            {
                'text': 'test',
                'id_str': '12345',
            },
            {
                'text': 'test',
                'id_str': '12344',
            },
        ]
        saved_state, artifact_list = self.twitter.run(None)
        self.assertEquals(saved_state, '12346')

    def test_run_supports_all_endpoints(self):
        # both supported return formats
        self.twitter.endpoint.return_value = [
            {
                'text': 'test',
                'id_str': '12345',
            },
        ]
        saved_state, artifact_list = self.twitter.run(None)
        self.assertEquals(saved_state, '12345')

        self.twitter.endpoint.return_value = {
            'statuses': [
                {
                    'text': 'test',
                    'id_str': '12345',
                },
            ]
        }
        saved_state, artifact_list = self.twitter.run(None)
        self.assertEquals(saved_state, '12345')

    def test_run_returns_artifacts_correctly(self):
        self.twitter.endpoint.return_value = [
            {
                'text': 'hxxp://someurl.com/test',
                'id_str': '12345',
            },
        ]
        saved_state, artifact_list = self.twitter.run(None)
        self.assertEquals(len(artifact_list), 2)
        self.assertIn('someurl.com', [str(x) for x in artifact_list])
        self.assertIn('http://someurl.com/test', [str(x) for x in artifact_list])
