from iview_class import *

ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

def Start():
    Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
    Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')


@handler('/video/aubciview', 'Australian ABC iView', art=ART, thumb=ICON)
def MainMenu():
    oc = ObjectContainer(view_group='List', title2='ABC iView')

    oc.add(DirectoryObject(
        key=Callback(list_menu, title=u'Channels', item_list=u'channel'),
        title=u'Channels'
    ))

    oc.add(DirectoryObject(
        key=Callback(list_menu, title=u'Categories', item_list=u'category'),
        title=u'Categories'
    ))

    # oc.add(DirectoryObject(
    #     key=Callback(LatestMenu),
    #     title=u'Latest'
    # ))
    #
    # oc.add(DirectoryObject(
    #     key=Callback(PopularMenu),
    #     title=u'Popular'
    # ))


    #oc.add(VideoClipObject(key = RTMPVideoURL(url = 'rtmp://203.18.195.10/ondemand' + '?auth=7B8F0402DD370FF9299E', clip = 'mp4:comedy/madashell_02_08', swf_url = 'http://www.abc.net.au/iview/images/iview.jpg'), rating_key = '123',title = 'TEST'))

    # cats = iView_Config.List_Categories()
    #
    # for key in cats:
    #     oc.add(DirectoryObject(
    #         key=Callback(GetSeriesByCaegory, category=key),
    #         title=cats[key]
    #     ))

    oc.objects.sort(key=lambda obj: obj.title)

    return oc


@route('/video/aubciview/list_menu/{item_list}')
def list_menu(title, item_list):
    oc = ObjectContainer(view_group='List', title2=title)
    if item_list == u'category':
        item_list = iview_plugin.category_list
    elif item_list == u'channel':
        item_list = iview_plugin.channel_list
    else:
        item_list = []

    for item in item_list:
        channel = JSON.ObjectFromURL(iview_plugin.API_URL + item['href'])
        thumb = channel['featuredImage'] if 'featuredImage' in channel else None
        oc.add(DirectoryObject(
            key=Callback(get_series_by_channel, channel=item['id'], title=item['title'], href=item['href']),
            title=item['title'],
            thumb=thumb
        ))
    oc.objects.sort(key=lambda obj: obj.title)

    return oc


@route('/video/aubciview/channel/{channel}')
def get_series_by_channel(channel, title, href):
    Log(u'get_series_by_channel:: channel={0}, title={1}, href={2}'.format(channel, title, href))
    oc = ObjectContainer(view_group='List', title2=title)

    href = iview_plugin.API_URL + href
    json = JSON.ObjectFromURL( href)

    for item in json['carousels']:
        Log(item)
        oc.add(DirectoryObject(
            key=Callback(get_episodes, href=href, cat=u'carousels', title=item['title']),
            title=item['title']))
    try:
        for item in json['collections']:
            Log(item)
            oc.add(DirectoryObject(
                key=Callback(get_episodes, href=href, cat=u'collections', title=item['title']),
                title=item['title']))
    except:
        pass
    
    for item in json['index']:
        Log(item)
        oc.add(DirectoryObject(
            key=Callback(get_episodes, href=href, cat=u'index', title=item['title']),
            title=item['title']))
    # oc.objects.sort(key=lambda obj: obj.title)

    return oc


@route('/video/aubciview/get_episodes')
def get_episodes(href, cat, title):
    Log(u'get_episodes:: href={0}, cat={1}'.format(href, cat))
    oc = ObjectContainer(view_group='List', title2=title)

    cat_list = JSON.ObjectFromURL(href)[cat]
    episodes = []
    for cat in cat_list:
        if 'title' in cat and cat['title'] == title:
            episodes = cat['episodes']
            break

    Log(episodes)

    for e in episodes:
        Log(e)
        episode_href = e[u'href']
        details = JSON.ObjectFromURL(iview_plugin.API_URL + episode_href)
        Log(details)
        title = u'{0} {1}'.format(
            details['seriesTitle'] if u'seriesTitle' in details else u'',
            details['title'] if u'title' in details else u'',
        )
        duration = int(details[u'duration'])*1000 if 'duration' in details else None

        streams = details[u'streams']
        url = streams[u'hls-high'][-1]
        # url = u'"http://iviewhls-i.akamaihd.net/i/playback/_definst_/_video/beautifullieextras_01_05_,650000,495000,206000,41046,.mp4.csmil/master.m3u8'

        oc.add(create_video_clip(
            url=url,
            title=title,
            summary=details[u'description'] if u'description' in details else u'',
            # originally_available_at=details[u'description'],
            duration=duration,
            # season=season,
            # index=index,
            thumb=Resource.ContentsOfURLWithFallback(url=e['thumbnail'])
        ))

    return oc


@route('/video/aubciview/cvc')
def create_video_clip(url, title=u'', summary=u'', duration=None, thumb=None, container=False):
    Log(u'create_video_clip:: url={0}'.format(url))
    vco = VideoClipObject(
        key = Callback(create_video_clip, url=url, title=title, thumb=thumb, container=True),
        #rating_key = url,
        url=url,
        title=title,
        summary=summary,
        duration=duration,
        thumb=thumb,
        items=[MediaObject(
                parts=[PartObject(key=HTTPLiveStreamURL(url=url))],
                optimized_for_streaming = True
                )
            ]
    )

    if container:
        return ObjectContainer(objects=[vco])
    else:
        return vco
