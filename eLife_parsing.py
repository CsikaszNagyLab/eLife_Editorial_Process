from bs4 import BeautifulSoup
import requests
import os
import time
import pandas as pd


def get_citations(ms_no):
    doi_url = 'http://dx.doi.org/10.7554/eLife.%05d' % ms_no
    r = requests.get(doi_url, allow_redirects=True)
    volume = r.url.split('/')[4]  # volume number

    elife_url = "http://elifesciences.org/content/%s/e%05d/article-metrics" % (volume, ms_no)
    r = requests.get(elife_url)
    soup = BeautifulSoup(r.text)

    metric_values = []
    for value in soup.find_all("span", {"class": "metric-value"}):
        try:
            metric_values.append(int(value.text))
        except ValueError:
            metric_values.append(0)

    # Get the name of the metric
    metric_names = []
    for value in soup.find_all("span", {"class": "metric-name"}):
        if value.a is not None:
            # get url:
            name = value.a['href'].split('/')[2]
        else:
            name = value.text
        metric_names.append(name)

    return zip(metric_names, metric_values)


if __name__ == "__main__":

    data_dir = os.path.join(os.getcwd(), 'data')

    decisions_df = pd.read_csv(os.path.join(data_dir, 'Decisions.csv'),
                               index_col=0)

    citations_dict = {}
    for ms_no, values in decisions_df.iterrows():
        print (ms_no)
        decision = values['Decision_Type']
        if decision == 'Accept Full Submission':
            citations_dict[ms_no] = get_citations(ms_no)

    for ms_no, cit in citations_dict.items():
        citations_dict[int(ms_no)] = dict(cit)

    citations = pd.DataFrame(citations_dict).T
    citations.rename(columns={'www.ncbi.nlm.nih.gov': 'Pubmed_Citations',
                              'www.scopus.com': 'Scopus'}, inplace=True)

    citations_fp = 'Citations_{}.csv'.format(time.strftime("%d-%m-%Y"))
    citations_fp = os.path.join(data_dir, citations_fp)
    citations.to_csv(citations_fp)
