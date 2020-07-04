import feedparser
import re
import models
from config import *
from bot import send_all_follows,bot


def delete_html(html):
    dr = re.compile(r'<[^>]+>', re.S)
    dd = dr.sub('', html)
    return dd


def check(target):
    result = feedparser.parse(target)
    if result.feed == {}:
        return ""
    else:
        if "title" in result.feed:
            return result.feed.title
        else:
            return "NoneTitle"


def main():
    rss = models.RssList.select()
    report = ""

    for r in rss:
        report_s = ""
        try:
            print("[RSS]Now:{}".format(r.Rss))
            data = feedparser.parse(r.Rss)
            for entries in data.entries:
                summary = delete_html(entries.summary)
                if summary != "" and len(summary) >= 20:
                    summary = summary[:50]
                if models.DataBase.select().where(
                        models.DataBase.Url == entries.link
                ).exists():
                    continue
                models.DataBase.create(
                    Title=entries.title,
                    Url=entries.link,
                    Summary=summary,
                    Form=r,
                )
                print("title:{}\n\tsummary:{}\n".format(entries.title, entries.summary))
                report_s += '\t<a href="{}">{}</a>\n'.format(entries.link, entries.title)
                print(report_s)

            if report_s != "":
                report += "<b>{} - {}</b>:\n".format(data.feed.title, data.feed.subtitle) + report_s

            if report != "":
                send_all_follows(r, report)
        except Exception as e:
            print("Some Error:{}".format(e))


if __name__ == '__main__':
    main()

