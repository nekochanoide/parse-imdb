#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup, NavigableString
import json
import webbrowser
import multiprocessing as mp
import sys

# import f


# In[2]:


headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "ru-RU,ru;q=0.9",
    "content-type": "application/x-www-form-urlencoded"
}


# In[3]:


def openInChrome(soup):
    url = 'out.html'
    html = soup.prettify()
    with open(url, "w", encoding='utf-8') as out:
        for i in range(0, len(html)):
            try:
                out.write(html[i])
            except Exception:
                1+1

    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

    webbrowser.get(chrome_path).open(url)


# In[4]:


# data = "title_type=feature,tv_movie,tv_series,tv_episode,tv_special,tv_miniseries,documentary,video_game,short,video,tv_short
# &
# release_date=1990-01-01,2000-12-31
# &
# user_rating=1.0,10.0
# &
# genres=action,adventure,animation,biography,comedy,crime,documentary,drama,family,fantasy,film-noir,game-show,history,horror,music,musical,mystery,news,reality-tv,romance,sci-fi,sport,talk-show,thriller,war,western
# &
# countries=af,ax,al,dz,as,ad,ao,ai,aq,ag,ar,am,aw,au,at,az,bs,bh,bd,bb,by,be,bz,bj,bm,bt,bo,bq,ba,bw,bv,br,io,vg,bn,bg,bf,bumm,bi,kh,cm,ca,cv,ky,cf,td,cl,cn,cx,cc,co,km,cg,ck,cr,ci,hr,cu,cy,cz,cshh,cd,dk,dj,dm,do,ddde,ec,eg,sv,gq,er,ee,et,fk,fo,yucs,fm,fj,fi,fr,gf,pf,tf,ga,gm,ge,de,gh,gi,gr,gl,gd,gp,gu,gt,gg,gn,gw,gy,ht,hm,va,hn,hk,hu,is,in,id,ir,iq,ie,im,il,it,jm,jp,je,jo,kz,ke,ki,xko,xkv,kw,kg,la,lv,lb,ls,lr,ly,li,lt,lu,mo,mg,mw,my,mv,ml,mt,mh,mq,mr,mu,yt,mx,md,mc,mn,me,ms,ma,mz,mm,na,nr,np,nl,an,nc,nz,ni,ne,ng,nu,nf,kp,vdvn,mp,no,om,pk,pw,xpi,ps,pa,pg,py,pe,ph,pl,pt,pn,pr,qa,mk,re,ro,ru,rw,bl,sh,kn,lc,mf,pm,vc,ws,sm,st,sa,sn,rs,csxx,sc,xsi,sl,sg,sk,si,sb,so,za,gs,kr,suhh,es,lk,sd,sr,sj,sz,se,ch,sy,tw,tj,tz,th,tl,tg,tk,to,tt,tn,tr,tm,tc,tv,vi,ug,ua,ae,gb,us,um,uy,uz,vu,ve,vn,wf,xwg,eh,ye,xyu,zrcd,zm,zw"


# In[5]:


def parse_details_block(soup) -> list:
    detailsTokens = []
    # details
    detailsSoup = soup.find("div", {"class": "article", "id": "titleDetails"})
    # tokens are blocks with info from 'Details' block
    detailsTags = detailsSoup.find_all(lambda x: x.has_attr(
        "class") and "txt-block" in x.get("class") and x.h4)

    for detailsTag in detailsTags:
        details = {}

        # remove all spans
        for span in detailsTag.find_all("span"):
            span.extract()

        # remove all whitespace
        spaces = []
        for s in detailsTag.strings:
            if (s.isspace()):
                spaces.append(s)
        for s in spaces:
            s.extract()

        # obtain details name
        details["name"] = detailsTag.find("h4").text.strip(":")

        # obtain details values
        values = []
        for child in detailsTag:
            if child.name == "a":
                values.append({
                    "type": "link",
                    "label": child.string.strip(),
                    "link": child["href"]
                })
            elif child.name is None:
                values.append({
                    "type": "string",
                    "value": child.strip()
                })
            elif child.name == "time":
                values.append({
                    "type": "time",
                    "datetime": child["datetime"],
                    "label": child.string.strip()
                })

        details["values"] = values
        detailsTokens.append(details)

    return detailsTokens


def parse_title_page(link) -> dict:
    # this lets you obtain title page by its link
    response = requests.get("https://www.imdb.com" + link, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    # title page contains some info in json object
    jsonSoup = soup.find("script", {"type": "application/ld+json"})
    jsonObject = json.loads("".join(jsonSoup.contents))

    # ru title
    jsonObject["ruTitle"] = soup.find(
        "div", {"class": "title_wrapper"}).find("h1").next_element.strip()

    # details
    jsonObject["detailsBlock"] = parse_details_block(soup)

    # remove @context token
    try:
        del jsonObject["@context"]
    except:
        pass
    # jsonObject.pop("@context", None)

    return jsonObject


# In[6]:


def obtain_links_from_page(soup) -> list:
    # from list of titles get links to titles pages
    films_headers = soup.find_all("h3", {"class": "lister-item-header"})

    links = []

    for header in films_headers:
        links.append(header.a["href"])

    return links


def obtain_all_links(**params) -> list:
    allLinks = []
    for i in range(4):
        params["count"] = "250"
        params["start"] = str(250 * i + 1)

        res = requests.post("https://www.imdb.com/search/title/",
                            headers=headers, params=params)
        soup = BeautifulSoup(res.text, "lxml")

        # openInChrome(soup)
        # raise ""

        links = obtain_links_from_page(soup)
        allLinks += links

        if (len(links) < 250):
            break

    return allLinks


# In[32]:


def main(**kwargs):
    """
    hello :)
    """

    print(kwargs)
    links = obtain_all_links(**kwargs)


# In[33]:

    pool = mp.Pool(mp.cpu_count())
    try:
        f
    except NameError:
        f = None
    if f:
        res = pool.map_async(f.parse_title_page, links)
    else:
        res = pool.map_async(parse_title_page, links)
    pool.close()
    pool.join()
    titles = res.get()


# In[34]:

    with open("titles.json", "w", encoding="utf-8") as outfile:
        try:
            json.dump(titles, outfile, ensure_ascii=False)
        except Exception:
            try:
                return titles
            except:
                return 1

    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = json.loads(sys.argv[1])
        main(**args)
    else:
        main(title_type="feature", release_date="1990-05-20,1995-06-21")
