import feedparser
from bot import send_all_follows
import models


def main(first_run=False):
    items = models.RssList.select()
    report = ""
    for item in items:
        try:
            report_s = ""
            data = feedparser.parse(item.rss)
            for entries in data.entries:
                if models.DataBase.select(
                    models.DataBase.Url ==entries.link
                ).exists is False:
                    models.DataBase.create(
                        Title=entries.title,
                        Url=entries.link,
                        Suummary=entries.summary
                    )
                report_s += '\t<a href="{}">{}</href>\n'.format(entries.link,entries.title)
            if report_s != "":
                report += "{} - {}:\n".format(data.feed.title,data.feed.subtitle)+report_s
            if first_run is False:
                send_all_follows(report)
        except Exception as e:
            print("Some Error{}".format(e))


if __name__ == '__main__':
    main(first_run=False)