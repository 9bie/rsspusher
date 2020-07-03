import feedparser

import models
from bot import send_all_follows

def check(target):
    result = feedparser.parse(target)
    if result.feed  == {}:
        return ""
    else:
        if "title" in result.feed:
            return result.feed.title
        else:
            return "NoneTitle"

def main(first_run=False):
    rss = models.RssList.select()
    report = ""

    for r in rss:
        report_s = ""
        #try:
        print("[RSS]Now:{}".format(r.Rss))
        data = feedparser.parse(r.Rss)
        for entries in data.entries:

            models.DataBase.create(
                Title=entries.title,
                Url=entries.link,
                Summary=entries.summary,
                Form=r,
            )
            print("title:{}\n\tsummary:{}\n".format(entries.title,entries.summary))
            report_s += '\t<a href="{}">{}</a>\n'.format(entries.link, entries.title)
            print(report_s)

        if report_s != "":
            report += "{} - {}:\n".format(data.feed.title, data.feed.subtitle) + report_s

        if first_run is False and report != "":
            send_all_follows(r,report)
        '''except Exception as e:
            print("Some Error:{}".format(e))'''


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 2:
        main(first_run=True)
    else:
        main(first_run=False)
