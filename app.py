from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

def scrap(url):
    #This is fuction for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information
    table = soup.find_all('div', attrs={'class':'lister-item-content'})

    temp = [] #initiating a tuple

    for i in range(0, len(table)):
        judul1 = table[i].find('h3',attrs={'class':'lister-item-header'})
        judul2 = judul1.find('a').text.strip()

        rating1 = table[i].find('div', attrs={'class':'inline-block ratings-imdb-rating'})
        rating2 = rating1.find('strong',attrs={'':''}).text.strip()

        votes1 = table[i].find('p', attrs={'class':'sort-num_votes-visible'})
        votes2 = votes1.find('span',attrs={'name':'nv'}).text.strip()

        if(table[i].find('span', attrs={'class':'metascore favorable'}) is None):
            meta = 0
        else:
            meta = table[i].find('span', attrs={'class':'metascore favorable'}).text.strip()

        temp.append((judul2, rating2, votes2, meta)) 
    

    df = pd.DataFrame(temp, columns = ('Title','Rating','Votes', 'MetaScore'))
    df['Rating'] = df['Rating'].astype('float64')
    df['Votes'] = df['Votes'].str.replace(",","")
    df['Votes'] = df['Votes'].astype('int64')
    df['MetaScore'] = df['MetaScore'].astype('float64')

    return df

@app.route("/")
def index():
    df = scrap('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31') #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    df.plot()
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()
