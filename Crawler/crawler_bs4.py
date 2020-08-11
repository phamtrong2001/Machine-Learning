from requests import Session
from bs4 import BeautifulSoup as bs
import lxml
import pandas as pd

login = "http://qac.uet.vnu.edu.vn/survey/login/index.php"
main_site = "http://qac.uet.vnu.edu.vn/survey/my/"

def export_csv(soup, file_name):
        section = 0
        list_section = []
        list_item = []
        list_rate = []
        itemId = 0
        for table in soup.find_all('table', class_="individual"):
            section += 1
            empty = 0
            for tr in table.find_all('tr'):
                if empty == 0:
                    empty = 1
                    continue
                itemId += 1
                rate = -1
                for td in tr.find_all('td'):
                    rate += 1
                    if rate == 0: continue
                    if td.get('class')[0] == "selected":
                        break
                list_section.append(section)
                list_item.append(itemId)
                list_rate.append(rate)
        df = pd.DataFrame()
        df['Section'] = list_section
        df['Item'] = list_item
        df['Rate'] = list_rate
        df.to_csv(file_name, index = False)

if __name__ == '__main__':
    print("username:", end= ' ')
    username = input()
    print("password:", end= ' ')
    password = input()

    login_data = {"username": username, "password": password}

    site = None
    course_id = []

    with Session() as s:
        site = s.get(login)
        # print(site.text)
        bs_content = bs(site.content, "lxml")
        token = bs_content.find("input", {"name": "logintoken"})['value']
        #
        login_data.update({"logintoken": token})
        s.post(login, login_data)
        home_page = s.get(main_site)
        main_content = bs(home_page.content, "lxml")
        courses = main_content.find_all("p", {"class": "tree_item branch", "data-node-type": "20"})
        
        for c in courses:
            id = int(c['data-node-key']) + 1
            course_id.append(id)
        for cid in course_id:
            questionnaire = "http://qac.uet.vnu.edu.vn/survey/mod/questionnaire/myreport.php?instance={}&user=3806&byresponse=1&action=vresp&group=0".format(cid)
            res = s.get(questionnaire).content
            res_content = bs(res, "lxml")
            course_name = "19020024_"+res_content.find("h1").text+".csv"
            print(course_name)
            export_csv(res_content, course_name)
            