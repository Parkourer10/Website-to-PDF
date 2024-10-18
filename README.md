# Website-to-PDF

The Website-to-PDF project is designed to archive/convert entire websites or wikis into a single PDF. It can handle lazy-loaded images, supports multi-threading for efficient processing, and generates one final PDF for the entire website. You can configure parameters like batch size, number of CPU cores, etc.

## How does it work?

It first gathers all the web pages of a website from its URL, stores the links in a file, and then converts each page into a PDF. Finally, all the PDFs are merged into a single PDF that contains the entire website.



## Installation

 Clone my github repo:

```bash
  git clone https://github.com/Parkourer10/Website-to-PDF.git
  cd Website-to-PDF/
```
 Install the dependencies:
#### Python dependencies
```bash
  pip install -r requirements.txt
```
#### Chromedriver for your chrome version:
- https://googlechromelabs.github.io/chrome-for-testing/
Put the chrome driver in the project folder or this will not work.

#### Update config.py to change the website URL, paths, and other parameters as per your needs.

 Run the project:

```bash
  python main.python
```
----


    
## Sorry for bad code lol



