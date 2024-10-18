import os

BASE_URL='' #website url
BATCH_SIZE=10 #making batches of pdfs to combine to a large pdf. change it to a higher value or lower value depending on your system.
NUM_CORES=os.cpu_count() #uses all cpu cores available. you can change this value if you want.
CHROME_DRIVER_PATH='./chromedriver'# path of the chromedriver for your chrome version.Make sure to download the correct chrome driver for your chrome version from https://googlechromelabs.github.io/chrome-for-testing/
PDF_OUTPUT_FILE='website.pdf' #output pdf name. change it if you want
