# -*- coding: utf-8 -*-
#####################################################################################################################
#                                                                                                                   #
# Парсер для социальной сети ВКонтакте                                                                              #
#                                                                                                                   #
# MIT License                                                                                                       #
# Copyright (c) 2020 Michael Nikitenko                                                                              #
#                                                                                                                   #
#####################################################################################################################

from datetime import datetime
from time import sleep
import re

import vk_api

from configs import VK_LOGIN, VK_PASSWORD
from accounts_lists import USERS_LIST


vk_session = vk_api.VkApi(VK_LOGIN, VK_PASSWORD)
vk_session.auth()
api = vk_session.get_api()

only_number_regexp = re.compile('[^\d]')


def calculate_account_type(url: str) -> str:
    """Получает ссылку на аккаунт и определяет его тип и возвращает строку с названием типа аккаунта"""
    account = url.replace('https://vk.com/', '')
    if account[0:4] == 'club':
        return 'Сообщество'
    elif account[0:6] == 'public':
        return 'Сообщество'
    else:
        return 'Личный'


def calculate_raw_account_id(url: str) -> int:
    """Получает ссылку и отфильтровывает от неё текст оставляя только цифры"""
    return int(only_number_regexp.sub('', url))


def get_user_id_from_url(url: str) -> int:
    """Полуычает url аккаунта и возвращает user_id аккаунта"""
    user_id = calculate_raw_account_id(url)
    account_type = calculate_account_type(url)
    if account_type == 'Сообщество':
        user_id = -user_id
    return user_id


def get_group_subs(group_id: int) -> int:
    """Получает id группы и возвращает количество подписчиков"""
    return int(api.groups.getById(group_id=group_id, v=5.126, fields='members_count')[0]['members_count'])

def get_account_subs(user_id: int) -> int:
    """Пошлучает id пользователя и возвращает количество подписчиков"""
    friends = api.friends.get(user_id=user_id, v=5.126, count=0, offset=0)['count']
    subs = api.users.getFollowers(user_id=user_id, v=5.126, count=0, offset=0)['count']
    res = friends + subs
    return res


def get_subs(url: str) -> int:
    """Получает количество подписчиков"""
    user_id = calculate_raw_account_id(url)
    account_type = calculate_account_type(url)
    if account_type == 'Сообщество':
        subs = get_group_subs(group_id=user_id)
    else:
        subs = get_account_subs(user_id)
    return subs



def get_data_count(comments: list, views: list, likes: list, shares: list) -> (int, int, int, int):
    """Достает максимальные значения из данных"""
    return sum(comments), sum(views), sum(likes), sum(shares)


def get_data_max(comments: list, views: list, likes: list, shares: list) -> (int, int, int, int):
    """Достает максимальные значения из данных"""
    if len(comments) == 0:
        comments_max = 0
        views_max = 0
        likes_max = 0
        shares_max = 0
    else:
        comments_max = max(comments)
        views_max = max(views)
        likes_max = max(likes)
        shares_max = max(shares)
    return comments_max, views_max, likes_max, shares_max


def get_data_min(comments: list, views: list, likes: list, shares: list) -> (int, int, int, int):
    """Достает максимальные значения из данных"""
    if len(comments) == 0:
        comments_min = 0
        views_min = 0
        likes_min = 0
        shares_min = 0
    else:
        comments_min = min(comments)
        views_min = min(views)
        likes_min = min(likes)
        shares_min = min(shares)
    return comments_min, views_min, likes_min, shares_min


def get_data_rate(comments: list, views: list, likes: list, shares: list) -> (float, float, float, float):
    """Достает максимальные значения из данных"""
    if len(comments) == 0:
        comments_rate = 0.0
        views_rate = 0.0
        likes_rate = 0.0
        shares_rate = 0.0
    else:
        comments_rate = 0.0
        views_rate = 0.0
        likes_rate = 0.0
        shares_rate = 0.0
    return comments_rate, views_rate, likes_rate, shares_rate



def get_posts_data(url: str, parsing_date: datetime):
    """Получает id пользователя/паблика/группы, тип аккаунта и дату парсинга и возвращает спарсенные данные"""
    posts = get_wall_posts_of_month(user_id=get_user_id_from_url(url), parsing_date=parsing_date)
    subs = get_subs(url)
    pubs = len(posts)
    pub_rate = round((pubs / parsing_date.day), 2)
    comments = []
    views = []
    likes = []
    shares = []
    for post in posts:
        comments.append(post['comments']['count'])
        likes.append(post['likes']['count'])
        shares.append(post['reposts']['count'])
        views.append(post['views']['count'])
    comments_count, views_count, likes_count, shares_count = get_data_count(comments, views, likes, shares)
    comments_max, views_max, likes_max, shares_max = get_data_max(comments, views, likes, shares)
    comments_min, views_min, likes_min, shares_min = get_data_min(comments, views, likes, shares)
    comments_rate, views_rate, likes_rate, shares_rate = get_data_rate(comments, views, likes, shares)
    print(f"url {url} subs {subs} pubs {pubs}, pub_rate {pub_rate},\n"
          f"comments count {comments_count}, views count {views_count}, "
          f"likes count {likes_count} shares count {shares_count}\n"
          f"comments min {comments_min}, views min {views_min}, likes min {likes_min}, shares min {shares_min}\n"
          f"comments max {comments_max}, views max {views_max}, likes max {likes_max}, shares max {shares_max}\n"
          f"comments rate {comments_rate} views rate {views_rate}, likes rate {likes_rate} shares rate {shares_rate}")
    return {
        'url': url,
        'subs': subs,
        'pubs': pubs,
        'pub_rate': pub_rate,
        'comments_count': comments_count,
        'views_count': views_count,
        'likes_count': likes_count,
        'shares_count': shares_count,
        'comments_min': comments_min,
        'views_min': views_min,
        'likes_min': likes_min,
        'shares_min': shares_min,
        'comments_max': comments_max,
        'views_max': views_max,
        'likes_max': likes_max,
        'shares_max': shares_max,
        'comments_rate': comments_rate,
        'views_rate': views_rate,
        'likes_rate': likes_rate,
        'shares_rate': shares_rate,
    }


def get_wall_posts_of_month(user_id: int, parsing_date: datetime) -> list:
    """Прогружает все посты на стене за конкретный месяц"""
    res = api.wall.get(owner_id=user_id, domain=user_id, count=100, filter='owner', extended=True)['items']
    if len(res) < 100:
        return res
    need_to_load_more = True
    offset = 100
    while need_to_load_more:
        print(f'load more data, offset = {offset}')
        subres = api.wall.get(
            owner_id=user_id, domain=user_id, offset=offset, count=100, filter='owner', extended=True)['items']
        last_post_datetime = datetime.fromtimestamp(subres[-1]['date'])
        if parsing_date.year >= last_post_datetime.year:    # Отсекаем прошлогодние посты
            if parsing_date.month == last_post_datetime.month:  # Отсекаем слишком старые посты
                offset = offset + 100
                res = res + subres
            elif (parsing_date.month + 1) == last_post_datetime.month:
                offset = offset + 100
                res = res + subres
            elif parsing_date.month == 1 and last_post_datetime.month == 1:
                offset = offset + 100
                res = res + subres
            else:
                res = res + subres
                need_to_load_more = False
        else:
            res = res + subres
            need_to_load_more = False
    res = filter_posts(res, parsing_date)
    return res


def filter_posts(posts: list, parsing_date: datetime) -> list:
    """Отфильтровывает лишние посты, которые не входят в месяц парсинга"""
    res = []
    for post in posts:
        post_date = datetime.fromtimestamp(post['date'])
        if post_date.month == parsing_date.month:
            res.append(post)
    return res


def parse_vk():
    """Парсит аккаунты в ВК и сохраняет данные в базу"""
    # milestone_id, milestone_date = create_parsing_date()
    # accounts = get_vk_accounts()
    parsed_data = []
    # for account in accounts:
    #     parsed_data.append(get_posts_data(account, milestone_date))
    # insert_parsed_data_in_db(milestone_id, parsed_data)
    # print(f'{milestone_date} VK parsed data saved to db')


def get_subscribers_list(public_id):
    """Получает список подписчиков паблика"""
    subs = api.groups.getMembers(group_id=public_id, sort='id_asc', offset=0, count=100, v=5.126)['items']
    # print(subs)
    offset = 100
    end_of_list = True
    while end_of_list:
        next_subs = api.groups.getMembers(group_id=public_id, sort='id_asc', offset=offset, count=100, v=5.126)['items']
        subs = subs + next_subs
        print(subs)
        if len(next_subs) == 0:
            end_of_list = False
        offset = offset + 100
        sleep(1)
    return subs


if __name__ == '__main__':
    print('vk_parser')
    # parsing_date_id, parsing_date = create_parsing_date()
    # current_date = datetime.now()
    # posts_data = get_posts_data(75962000, 'Сообщество', current_date)
    # accounts = get_vk_accounts()
    # for account in accounts:
    #     print(account)
    #     subs = get_group_subs(account)
    #     print(subs)
    #     # get_posts_data(account, current_date)
    #     sleep(5)
    # print(get_account_subs(17001690))
    # parse_vk()
    print('ER!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    er_subscribers = get_subscribers_list(18483909)
    for user in USERS_LIST:
        for sub in er_subscribers:
            if user == sub:
                print(f'https://vk.com/id{user} является подписчиков ЕР')
    print('ER YANAO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    er_yanao = get_subscribers_list(62997808)
    for user in USERS_LIST:
        for sub in er_yanao:
            if user == sub:
                print(f'https://vk.com/id{user} является подписчиков ЕР ЯНАО')