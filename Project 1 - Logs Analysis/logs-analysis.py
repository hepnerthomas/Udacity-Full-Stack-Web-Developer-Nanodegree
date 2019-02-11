#!/usr/bin/env python3
import psycopg2


def getThreeMostPopularArticles(DBNAME):
    """ Accepts DBNAME string and output_txt string as inputs.
        Returns output, a list of tuples of the most popular articles.
    """
    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()
    c.execute("""
        select articles.title, count(*) as views
        from log
        left join articles on articles.slug = LTRIM(log.path, '/articles/')
        where articles.slug is not null
        group by articles.title, articles.slug order by count(*) desc
        limit 3;
    """)
    output = c.fetchall()
    db.close()
    return output


def getMostPopularAuthors(DBNAME):
    """ Accepts DBNAME string and output_txt string as inputs.
        Returns output, a list of tuples of the most popular authors.
    """
    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()
    c.execute("""
        select authors.name, count(*) as views
        from log
        left join articles on articles.slug = LTRIM(log.path, '/articles/')
        left join authors on authors.id = articles.author
        where articles.slug is not null
        group by authors.name order by count(*) desc;
    """)
    output = c.fetchall()
    db.close()
    return output


def getDayswithErrors(DBNAME):
    """ Accepts DBNAME string and output_txt string as inputs.
        Returns output, a list of tuples of the days with more than 1% errors.
    """
    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()
    c.execute("""
    select date
        , concat(views_percentage, '%') as error_percentage

    from (
        select date
        , status
        , views
        , round(100.0 * views / sum(views)
            over (partition by date), 2) as views_percentage

        from (
            select to_char(time, 'YYYY-MM-DD') as date
                , status
                , count(*) as views
            from log
            group by to_char(time, 'YYYY-MM-DD'), status
            order by to_char(time, 'YYYY-MM-DD'), status

        ) as status_table

    ) as error_table

    where status = '404 NOT FOUND' and views_percentage > 1.0;
    """)
    output = c.fetchall()
    db.close()
    return output


if __name__ == '__main__':
    """ Executes code to complete the Logs Analysis project.
        Outputs a text file.
    """

    print("\nDefine DBNAME and output_text variables.")
    DBNAME = "news"
    output_text = ""

    print("\nWrite query results to a text file.")
    with open('logs-analysis-output.txt', 'w') as f:

        print("\n1. The 3 Most Popular Articles:")
        topThreeArticles = getThreeMostPopularArticles(DBNAME)
        f.write("1. The 3 Most Popular Articles." + "\n")
        f.write('\n'.join(
                    '%s - %s views'
                    % article for article in topThreeArticles
                    )
                )
        f.write('\n')

        print("\n2. The Most Popular Authors:")
        mostPopularAuthors = getMostPopularAuthors(DBNAME)
        f.write("\n2. The Most Popular Authors." + "\n")
        f.write('\n'.join(
                    '%s - %s views'
                    % author for author in mostPopularAuthors
                    )
                )
        f.write('\n')

        print("\n3. The Days with More than 1% Errors:")
        dayswithErrors = getDayswithErrors(DBNAME)
        f.write("\n3. The Days with More than 1% Errors." + "\n")
        f.write('\n'.join(
                    "%s - %s errors"
                    % error for error in dayswithErrors
                    )
                )
        f.write('\n')
        f.close()

        print("\nComplete!")
