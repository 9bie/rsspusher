import feedparser
from bot import send_all_follows
import models


def main(first_run=False):
    items = models.RssList.select()
    report = ""
    for item in items:
        try:
            report_s = ""
            data = feedparser.parse(item.Rss)
            for entries in data.entries:

                try:
                    models.DataBase.create(
                        Title=entries.title,
                        Url=entries.link,
                        Suummary=entries.summary,
                        Form=item.Title,
                    )
                    report_s += '\t<a href="{}">{}</a>\n'.format(entries.link,entries.title)
                    print(report_s)
                except:
                    pass
            if report_s != "":
                report += "{} - {}:\n".format(data.feed.title,data.feed.subtitle)+report_s

            if first_run is False and report != "":
                send_all_follows(report)
        except Exception as e:
            print("Some Error:{}".format(e))


if __name__ == '__main__':
    main(first_run=False)