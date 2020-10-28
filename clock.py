# -*- coding: utf-8 -*-
from apscheduler.schedulers.blocking import BlockingScheduler
import os
import TextTweet
from PrepareChain import PrepareChain
import DataPrep
import GetTweet

# APIの秘密鍵
CK,CS,AT,AS=os.environ["CK"], os.environ["CS"], os.environ["AT"], os.environ["AS"]

twische = BlockingScheduler()

# 30分に一度ツイート
@twische.scheduled_job('interval',minutes=20)
def timed_job():
    #data.txtの作成
    DataPrep.DataPrep("data_orig.txt", "data.txt")
    GetTweet.gettweet(CK,CS,AT,AS)
    f = open("data.txt",encoding="utf-8")
    text = f.read()
    f.close()
    chain = PrepareChain(text)
    triplet_freqs = chain.make_triplet_freqs()
    chain.save(triplet_freqs, True)
    TextTweet.puttweet(CK,CS,AT,AS)

if __name__ == "__main__":
    twische.start()
