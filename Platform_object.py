import json
import time
from random import choice
import tkinter as tk
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from requests_html import HTMLSession
Request = HTMLSession()

"""
有任何问题请联系本人邮箱:2601664329@qq.com
"""

"""
解题思路:
    1,找到用户信息的url,然后获取用户的基本信息，----->username
    2,找到已报名了的课程url,提取全部课程，---------->parent_id，course_Id
    3,找到课程的全部课时url,提取全部课时，---------->section_Id,chapter_Id
    4,找到课程已完成的url，提取全部已获取课时，------>accomplish_count
    5,找到提交任务的url，将任务提交进服务器，-------->return  
    6,最后找到添加参数的url，将参数提交进服务器，----->得到反馈
"""


class platform():
    def __init__(self,user_id):
        self.headers_referer = 'http://www.cqooc.net/my/learn'
        self.headers = {
            'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            'Referer':self.headers_referer,
            'Cookie': 'Hm_lvt_deeb6849ac84929e8ae01644f8d27145=1605496234; xsid={}; Hm_lpvt_deeb6849ac84929e8ae01644f8d27145=1605496801'.format(user_id),
        }

        self.user_id = user_id
        self.user_url = 'http://www.cqooc.net/user/session?xsid={}',
        # 公开课课程
        self.lesson_url = "http://www.cqooc.net/json/mcs?sortby=id&reverse=true&del=2&courseType=2&ownerId={}&limit=100"
        # 单个课程课堂个数
        #http://www.cqooc.net/json/chapters?limit=200&start=1&sortby=selfId&status=1&courseId=334567485&select=id,title,level,selfId,parentId&ts=1605578890638
        self.class_number_url = 'http://www.cqooc.net/json/mooc/lessons?limit=100&start={}&select=id,title,category,testId,forumId,parentId,selfId&sortby=id&reverse=false&courseId={}'
        # 已完成的课程
        self.accomplish_url = 'http://www.cqooc.net/json/learnLogs?limit=100&start=1&courseId={}&select=sectionId&username={}'
        # 任务添加进服务器
        self.test_url = "http://www.cqooc.net/json/learnLogs?sectionId={}&username={}"
        #添加参数
        self.request_url = "http://www.cqooc.net/learnLog/api/add"
        #time
        self.start_url = 'http://www.cqooc.net/account/session/api/login/time'
        self.sectionlist = 'http://www.cqooc.net/json/chapter/lessons?courseId={}'
    #获取用户具体信息--->ownerid and username
    def User_infomation(self)->str:
        User_url = self.user_url[0].format(self.user_id)
        # print(User_url)
        User_info = Request.get(url=User_url,headers=self.headers).json()
        # print(User_info)
        #用户id值
        ownerId_id = User_info['id']
        #username值
        User_name = User_info['username']
        return ownerId_id,User_name

    #获取parent_id and course_id
    def Public_Class_Infomation(self,ownerId_id)->list:
        Public_url = self.lesson_url.format(ownerId_id)
        Public_class_data = Request.get(url=Public_url,headers=self.headers).json()
        # print(Public_class_data)
        lesson_data_list = []
        for key, i in enumerate(Public_class_data['data']):
            print(key+1, '\n' +
                  i['course']['title'],
                  )
            lesson_data_list.append({
                'title': i['title'],
                'parent_id': i['id'],
                'course_Id': i['courseId'],
                # 'ownerId' : i['ownerId']
            })
        return lesson_data_list

    # 单个课程课堂个数
    def course_number(self,start_id,course_Id)->list:
        cource_url = self.class_number_url.format(start_id,course_Id)
        self.referer = "http://www.cqooc.net/learn/mooc/progress?id={}".format(course_Id)

        self.headers_1 = {
            'Cookie': 'Hm_lvt_deeb6849ac84929e8ae01644f8d27145=1605496234; xsid={}; Hm_lpvt_deeb6849ac84929e8ae01644f8d27145=1605496801'.format(user_id),
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            'Referer':self.referer
        }
        course_data = Request.get(url=cource_url,headers=self.headers_1).json()
        #课程总个数
        course_length = course_data['meta']['total']
        # print(course_length)
        course_list = []
        for i in course_data['data']:
            course_list.append({
                'section_Id': i['id'],
                'chapter_Id': i['chapter']['id']
            })
        course_count = len(course_list)
        return course_length,course_list

    # 已完成的课程
    def complete_course(self,courseId,username)->list:
        self.referer = "http://www.cqooc.net/learn/mooc/progress?id={}".format(courseId)
        self.headers_1 = {
            'Cookie': 'Hm_lvt_deeb6849ac84929e8ae01644f8d27145=1605496234; xsid={}; Hm_lpvt_deeb6849ac84929e8ae01644f8d27145=1605496801'.format(user_id),
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            'Referer': self.referer
        }

        complete_url = self.accomplish_url.format(courseId,username)
        complete_data = Request.get(url=complete_url,headers=self.headers_1).json()
        complete_length = complete_data['meta']['total']
        # print(complete_length)
        complete_code_list = []
        for data in complete_data['data']:
            complete_code_list.append(data['sectionId'])
        # complete_count = len(complete_code_list)
        return complete_length,complete_code_list

    def add_server(self,sectionId,username,course_Id):
        server_url = self.test_url.format(sectionId,username)
        referer_1 = 'http://www.cqooc.net/learn/mooc/structure?id={}'.format(course_Id)
        self.headers_2 = {
            'Cookie': 'Hm_lvt_deeb6849ac84929e8ae01644f8d27145=1605496234; xsid={}; Hm_lpvt_deeb6849ac84929e8ae01644f8d27145=1605496801'.format(user_id),
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            'Referer': referer_1
        }
        test = Request.get(url=server_url,headers=self.headers_2).json()
        return test

    def request_code(self,chapterId,courseId,ownerId,parentid,sectionId,username):
        referer_6 = 'http://www.cqooc.net/learn/mooc/structure?id={}'.format(courseId)
        self.headers_5 = {
            'Cookie': 'Hm_lvt_deeb6849ac84929e8ae01644f8d27145=1605496234; xsid={}; Hm_lpvt_deeb6849ac84929e8ae01644f8d27145=1605496801'.format(user_id),
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            'Referer': referer_6
        }
        json_code = {
            'action': 0,
            'category': 2,
            'chapterId': str(chapterId),
            'courseId': str(courseId),
            'ownerId': int(ownerId),
            'parentId': str(parentid),
            'sectionId': str(sectionId),
            'username': str(username)
        }
        json_data = json.dumps(json_code)
        # print(json_data)
        request_code = Request.post(url=self.request_url,headers=self.headers_5,data=json_data).json()
        # print(request_code)

    def start_time(self,username,course_Id):
        self.referer_2 = 'http://www.cqooc.net/learn/mooc/structure?id={}'.format(course_Id)
        json_data = {
            'username':username
        }
        self.headers_3 = {
            'Cookie': 'Hm_lvt_deeb6849ac84929e8ae01644f8d27145=1605496234; xsid={}; Hm_lpvt_deeb6849ac84929e8ae01644f8d27145=1605496801'.format(user_id),
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            'Referer': self.referer_2
        }
        start_time = Request.post(url=self.start_url,headers=self.headers_3,json=json_data).json()
        # print(start_time)

    def section(self,courseId):
        headers_4 = {
            'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            'Cookie': 'Hm_lvt_deeb6849ac84929e8ae01644f8d27145=1605496234; xsid={}; Hm_lpvt_deeb6849ac84929e8ae01644f8d27145=1605496801'.format(user_id),
        }
        section_url = self.sectionlist.format(courseId)
        # print(section_url)
        section_data = Request.get(url=section_url,headers=headers_4).json()['data'][0]['body']
        # print(section_data.items())
        return section_data

    #新增函数
    def judge_bool(self,courseId,username):
        #获取已完成的个数
        #此函数主要通过判断，如果判断成立，则循环继续，条件不成立则停止循环
        self.complete_length,complete_list = self.complete_course(courseId,username)
        self.course_length,course_list = self.course_number(self.complete_length,courseId)
        self.boolean = int(self.course_length) -  int(self.complete_length)
        # print(course_length,complete_length,boolean)
        if self.boolean:
            return True
        else:
            return False

    def run(self):
        owner_id, User_name = self.User_infomation()
        # 获取报了多少课程
        lesson_data_list = self.Public_Class_Infomation(owner_id)
        # print(lesson_data_list)
        while True:
            try:
                id = input('请选择课程(id序号):')
                title = lesson_data_list[int(id) - 1]['title']
                print('\n{}\n'.format(title))
                break
            except:
                print('输入错误,请重新输入！')
                continue

        parentId = lesson_data_list[int(id) - 1]['parent_id']
        courseId = lesson_data_list[int(id) - 1]['course_Id']
        # print(parentId,courseId)

        # platforms.section(courseId)
        # print(complete_code_list)
        self.start_time(User_name, courseId)

        sections = self.section(courseId).items()

        complete_length,complete_list = self.complete_course(courseId,User_name)

        # 课程列表与课程总数以及课程长度


        # print(course_list)
        while self.judge_bool(courseId,User_name):
            self.course_length, course_list = self.course_number(int(complete_length), courseId)
            for i in course_list:
                section_Id = i['section_Id']
                chapter_Id = i['chapter_Id']
                # 已完成课程编码列表，与个数
                self.complete_length,complete_code_list = self.complete_course(courseId, User_name)
                #获取未完成的课程
                unfinished = int(self.course_length) - int(self.complete_length)
                print('总课程{}/未完成{}/已完成{}'.format(int(self.course_length), unfinished, self.complete_length))
                if section_Id not in complete_code_list:
                    print('-----访问成功,等待半分钟----')
                    self.start_time(User_name, courseId)
                    self.add_server(section_Id, User_name, courseId)
                    time.sleep(30)
                    self.start_time(User_name, courseId)
                    time.sleep(2)
                    self.request_code(chapter_Id, courseId, owner_id, parentId, section_Id, User_name)
                    print('-----课程完成------')
                else:
                    print('-----已完成，跳过此课程-----')
                    time.sleep(5)
                    continue


if __name__ == '__main__':
    user_id = input('请输入你的xsid以获取用户信息:')
    platforms = platform(user_id)
    platforms.run()





