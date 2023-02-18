import pandas as pd
class Article:

    def __init__(self,type,author,content):
        self.type=type
        self.author=author
        self.time=pd.Timestamp('now', tz='Asia/Kolkata').date()
        self.content=content
