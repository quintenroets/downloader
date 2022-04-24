import downloader

urls = [
    "https://covid-19.sciensano.be/sites/default/files/Covid19/Meest%20recente%20update.pdf",
    "https://www.orimi.com/pdf-test.pdf",
]

dests = downloader.download_urls(urls)
for dest in dests:
    dest.unlink()
