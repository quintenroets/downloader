import downloader

url = "https://covid-19.sciensano.be/sites/default/files/Covid19/Meest%20recente%20update.pdf"

dest = downloader.download(url)
dest.unlink()
