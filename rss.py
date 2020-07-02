import feedparser

import models
from bot import send_all_follows


def main(first_run=False):
    items = models.RssChannel.select()
    report = ""

    for item in items:

        rss = models.RssList.select().where(
            models.RssList.Form == item
        )
        for r in rss:
            report_s = ""
            try:
                print("[RSS]Now:{}".format(r.Rss))
                data = feedparser.parse(r.Rss)
                for entries in data.entries:
                    try:
                        models.DataBase.create(
                            Title=entries.title,
                            Url=entries.link,
                            Suummary=entries.summary,
                            Form=item.Title,
                        )
                        report_s += '\t<a href="{}">{}</a>\n'.format(entries.link, entries.title)
                        print(report_s)
                    except:
                        print("[!RSS]{} in database.passing.".format(entries.title))
                if report_s != "":
                    report += "{} - {}:\n".format(data.feed.title, data.feed.subtitle) + report_s

                if first_run is False and report != "":
                    send_all_follows(r.ID,report)
            except Exception as e:
                print("Some Error:{}".format(e))


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 2:
        main(first_run=True)
    else:
        main(first_run=False)
