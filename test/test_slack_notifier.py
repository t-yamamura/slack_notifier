# encoding : utf-8

import sys
import os
import unittest
sys.path.append(os.pardir)
from slack_notifier.slack_notifier import SlackNotifier
from slack_notifier.slack_notifier import sec2dhms

class TestSlack(unittest.TestCase):
    """
    """

    def test_notify_completion(self):
        """
        _notify_completion()のテスト
        """
        s = SlackNotifier(url=os.environ['WEBHOOK_URL'], end=False)
        # 1. 正常終了時
        self.assertEqual(s._notify_completion(), 0)
        # 2. 異常終了時
        s.except_flag = True
        self.assertEqual(s._notify_completion(), 1)

    def test_post_payload(self):
        """
        _post_payload()のテスト

        テスト内容
        1. 投稿に失敗する場合
        2. 投稿に成功する場合
        """
        # 1. 投稿に失敗する場合
        s = SlackNotifier(url=os.environ['WEBHOOK_URL'], end=False)
        self.assertNotEqual(s._post_payload(payload={"wrong_key":"hello"}), 200)
        # 2. 投稿に成功する場合
        s = SlackNotifier(url=os.environ['WEBHOOK_URL'], end=False)
        self.assertEqual(s._post_payload(payload={"text": "_post_payload()のテスト", "username": "Test", "icon_emoji": ":ok_woman:"}), 200)

    def test_update_elapsed_time(self):
        """
        update_elapsed_time()のテスト

        テスト内容
        1. update_elapsed_time()が返す型の確認
        2. update_elapsed_time()が返す値の確認
        """
        s = SlackNotifier(url="https://hooks.slack.com/services/DUMMY_WEBHOOK_URL", end=False)
        # 1. update_elapsed_time()が返す型の確認
        day, hour, minute, second = s.update_elapsed_time()
        self.assertIsInstance(day, int)
        self.assertIsInstance(hour, int)
        self.assertIsInstance(minute, int)
        self.assertIsInstance(second, int)
        # 2. update_elapsed_time()が返す値の確認
        self.assertEqual(s.elapsed_time, s.current_time - s.start_time)
        self.assertEqual((day, hour, minute, second), sec2dhms(s.elapsed_time))

    def test_sec2dhms(self):
        """
        sec2dhms()のテスト

        テスト内容:
        1. 0[sec] < t < 1[min]
        2. 1[min] <= t < 1[hour]
        3. 1[hour] <= t < 1[day]
        4. 1[day] <= t < 1[day] + 1[min]
        5. 1[day] + 1[min] <= t < 1[day] + 1[hour]
        6. 1[day] + 1[hour] <= t < 2[day]
        """
        # 1. 0[sec] < t < 1[min]
        self.assertEqual(sec2dhms(sec=0), (0, 0, 0, 0))
        self.assertEqual(sec2dhms(sec=59), (0, 0, 0, 59))
        # 2. 1[min] <= t < 1[hour]
        self.assertEqual(sec2dhms(sec=60), (0, 0, 1, 0))
        self.assertEqual(sec2dhms(sec=3599), (0, 0, 59, 59))
        # 3. 1[hour] <= t < 1[day]
        self.assertEqual(sec2dhms(sec=3600), (0, 1, 0, 0))
        self.assertEqual(sec2dhms(sec=86399), (0, 23, 59, 59))
        # 4. 1[day] <= t < 1[day] + 1[min]
        self.assertEqual(sec2dhms(sec=86400), (1, 0, 0, 0))
        self.assertEqual(sec2dhms(sec=86459), (1, 0, 0, 59))
        # 5. 1[day] + 1[min] <= t < 1[day] + 1[hour]
        self.assertEqual(sec2dhms(sec=86460), (1, 0, 1, 0))
        self.assertEqual(sec2dhms(sec=89999), (1, 0, 59, 59))
        # 6. 1[day] + 1[hour] <= t
        self.assertEqual(sec2dhms(sec=90000), (1, 1, 0, 0))
        self.assertEqual(sec2dhms(sec=172799), (1, 23, 59, 59))
        self.assertEqual(sec2dhms(sec=172800), (2, 0, 0, 0))


if __name__ == '__main__':
    unittest.main()