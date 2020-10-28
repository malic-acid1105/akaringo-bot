# -*- coding: utf-8 -*-
import tweepy
import re
import os.path
import sqlite3
import random
from PrepareChain import PrepareChain

class Gentext(object):
    # 2文生成するのでn=1とする
    def __init__(self):
        self.n = 2
        #self.n = random.randrange(1,5)

    def generate(self):
        generated_text = u""

        # dbが見つからないときの例外処理
        if not os.path.exists(PrepareChain.DB_PATH):
            raise IOError("DBファイルが存在しません")

        # dbを開く
        conn = sqlite3.connect(PrepareChain.DB_PATH)
        conn.row_factory = sqlite3.Row

        for i in range(self.n):
            text = self._generate_sentence(conn)
            generated_text += text

        # dbを閉じる
        conn.close()

        generated_text=re.sub(r"#", " #" ,generated_text)

        return generated_text

    def _generate_sentence(self, conn):
        morphemes = []

        # 始まりを取得
        first_triplet = self._get_first_triplet(conn)
        morphemes.append(first_triplet[1])
        morphemes.append(first_triplet[2])

        # 文章を繋げる
        while morphemes[-1] != PrepareChain.END:
            prefix1, prefix2 = morphemes[-2], morphemes[-1]
            triplet = self._get_triplet(conn, prefix1, prefix2)
            morphemes += [triplet[2]]

        # 連結して返す
        return "".join(morphemes[:-1])

    def _get_chain_from_DB(self, conn, prefixes):
        sql = u"select prefix1, prefix2, suffix, freq from chain_freqs where prefix1 = ?"

        # prefixが2つなら条件に加える
        if len(prefixes) == 2:
            sql += u" and prefix2 = ?"

        # 結果
        result = []

        # dbから取得
        cursor = conn.execute(sql, prefixes)
        for row in cursor:
            result.append(dict(row))

        return result

    def _get_first_triplet(self, conn):
        # BEGINをprefix1としてチェーンを取得
        prefixes = (PrepareChain.BEGIN,)

        # チェーン情報を取得
        chains = self._get_chain_from_DB(conn, prefixes)

        # 取得したチェーンから、確率的に1つ選ぶ
        triplet = self._get_probable_triplet(chains)

        return (triplet["prefix1"], triplet["prefix2"], triplet["suffix"])

    def _get_triplet(self, conn, prefix1, prefix2):
        # BEGINをprefix1としてチェーンを取得
        prefixes = (prefix1, prefix2)

        # チェーン情報を取得
        chains = self._get_chain_from_DB(conn, prefixes)

        # 取得したチェーンから、確率的に1つ選ぶ
        triplet = self._get_probable_triplet(chains)

        return (triplet["prefix1"], triplet["prefix2"], triplet["suffix"])

    def _get_probable_triplet(self, chains):
        probability = []

        # 確率に合うように、インデックスを入れる
        for (index, chain) in enumerate(chains):
            for j in range(chain["freq"]):
                probability.append(index)

        # ランダムに1つを選ぶ
        chain_index = random.choice(probability)

        return chains[chain_index]

def puttweet(CK,CS,AT,AS):
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    api = tweepy.API(auth)

    generator=Gentext()

    api.update_status(generator.generate())
