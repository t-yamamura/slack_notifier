# encoding : utf-8

import sys
import time
import json
import atexit
import requests
import traceback

class SlackNotifier:

    def __init__(self, url, end=False, default_user='python '+' '.join(sys.argv), default_icon=':snake:', default_channel='#python_webhook', default_link=0, end_message=''):
        self.url             = url                        # str   Webhook URL
        self.command_name    = " ".join(sys.argv)         # str   実行したコマンド
        self.start_time      = time.time()                # float プログラム開始時刻(インスタンス生成時)
        self.current_time    = float()                    # float プログラム終了時刻(関数呼び出し時)
        self.elapsed_time    = float()                    # float プログラム実行時間(end_time - start_time)
        self.except_flag     = False                      # bool  例外発生フラグ(例外発生時:True)
        self.tb_text         = str()                      # str   トレースバックの情報(例外発生時)
        self.default_user    = default_user               # str   デフォルトユーザ名
        self.default_icon    = default_icon               # str   デフォルトアイコン
        self.default_channel = default_channel            # str   デフォルトチャンネル(投稿先)
        self.default_link    = default_link               # int   デフォルト
        self.end_message     = end_message                # str   終了通知のメッセージ
        self.success_icon    = ':v:'                      # str   正常終了時のアイコン
        self.success_msg     = 'Successfully completed !' # str   正常終了時のメッセージ
        self.error_icon      = ':x:'                      # str   異常終了時のアイコン
        self.error_msg       = 'Errors occurred !'        # str   異常終了時のメッセージ
        # excepthookをオーバーライド
        sys.excepthook = self.my_excepthook
        # endがTrueのとき_notify_completion()を実行
        if end: atexit.register(self._notify_completion)

    def my_excepthook(self, type, value, tb):
        """
        sys.excepthookをオーバライドした関数(https://docs.python.jp/3/library/sys.html)
        例外発生時に，トレースバック情報を保持
        終了通知を行う場合は，エラー情報を送るフラグを設定

        :return: None
        :rtype: None
        """
        self.except_flag = True
        self.tb_text = "".join(traceback.format_exception(type, value, tb)) + "\n"
        sys.stderr.write(self.tb_text)

        return

    def send_message(self, msg, username=None, icon_emoji=None, channel=None, link_names=None, add_command_info=False, add_elapsed_time=False, **requests_kwargs):
        """
        Slackにメッセージを投稿

        :param str msg: 投稿テキスト
        :param str username: (optional) ユーザ名
        :param str icon_emoji: (optional) アイコン
        :param str channel: (optional) 投稿先のチャンネル
        :param int link_names: (optional) メンションを有効にするかどうか(1なら有効)
        :param bool add_command_info: (optional) 投稿テキストにコマンド情報を付与するかどうか(Trueなら付与)
        :param bool add_elapsed_time: (optional) 投稿テキストに経過時間情報を付与するかどうか(Trueなら付与)
        :param **requests_kwargs: requests.postに与えるキーワード引数
        :return: ステータスコード(投稿に成功した場合は200)
        :rtype: int
        """
        msgs = [msg]
        if username == None: username = self.default_user
        if icon_emoji == None: icon_emoji = self.default_icon
        if channel == None: channel = self.default_channel
        if link_names == None: link_names = self.default_link
        if add_command_info: msgs.append("command: {}".format(self.command_name))
        if add_elapsed_time: msgs.append("elapsed time: {0[0]}[d]{0[1]}[h]{0[2]}[m]{0[3]}[s]".format(self.update_elapsed_time()))
        payload_dic = {
            "text"       : "\n".join(msgs),
            "username"   : username,
            "icon_emoji" : icon_emoji,
            "channel"    : channel,
            "link_names" : link_names
        }

        return self._post_payload(payload_dic, **requests_kwargs)

    def update_elapsed_time(self):
        """
        現在時刻と経過時間のUNIXタイムを更新し，経過時間を[日時分秒]形式で返す

        :return: 経過時間の(日数, 時間, 分, 秒)のタプル
        :rtype: tuple of (int, int, int, int)
        """
        self.current_time = time.time()
        self.elapsed_time = self.current_time - self.start_time

        return sec2dhms(self.elapsed_time)

    def _post_payload(self, payload, **requests_kwargs):
        """
        Incoming Webhookを利用してSlackに投稿(post)する

        :params dic payload: 辞書化した投稿内容
        :params **requests_kwargs: requests.postのキーワード引数(proxiesなど)
        :return: ステータスコード(投稿に成功した場合は200)
        :rtype: int
        """
        r = requests.post(url=self.url, data=json.dumps(payload), **requests_kwargs)
        if r.status_code != 200:
            sys.stderr.write("POST ERROR : status_code {}\n".format(r.status_code))

        return r.status_code

    def _notify_completion(self):
        """
        プログラムの終了時に，正常終了・異常終了の通知を送る

        :return: 正常終了の場合0, 異常終了の場合1
        :rtype: int
        """
        if self.except_flag:
            self.send_message(msg="{}\n{}\n{}".format(self.error_msg, self.tb_text, self.end_message), username='Finish', icon_emoji=self.error_icon, add_command_info=True, add_elapsed_time=True)
            return 1
        else:
            self.send_message(msg="{}\n{}".format(self.success_msg, self.end_message), username='Finish', icon_emoji=self.success_icon, add_command_info=True, add_elapsed_time=True)
            return 0

def sec2dhms(sec):
    """
    秒(sec)を日時分秒(Day, Hour, Minute, Second)の形式に変換しタプルを返す

    :param float sec: 秒数
    :return: (日数, 時間, 分, 秒)のタプル
    :rtype: tuple of (int, int, int, int)
    """
    # 日数
    day = int(sec / 86400)
    sec %= 86400
    # 時
    hour = int(sec / 3600)
    sec %= 3600
    # 分
    minute = int(sec / 60)
    sec %= 60
    # 秒
    second = int(sec)

    return (day, hour, minute, second)