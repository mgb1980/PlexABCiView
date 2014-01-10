from iview_class import *

ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

def Start():
    HTTP.RandomizeUserAgent(browser='Safari')
    Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
    Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

@handler('/video/iview', 'ABC iView', art=ART, thumb=ICON)
def MainMenu():
    
    oc = ObjectContainer(view_group='List', title2='ABC iView')
    cats = iView_Config.List_Categories()

    for key in cats:
        oc.add(DirectoryObject(
            key=Callback(GetSeriesByCaegory, category=key),
            title=cats[key]
        ))

    oc.objects.sort(key=lambda obj: obj.title)
    return oc


@route('/video/iview/category/{category}')
def GetSeriesByCaegory(category):
    
    cat = iView_Category(category)
    oc = ObjectContainer(view_group='List', title2=cat.title)
    series = cat.series_list

    for item in series:
        oc.add(DirectoryObject(
            key=Callback(GetEpisodesBySeries, series=item[0]),
            title=item[1]
        ))
        
    oc.objects.sort(key=lambda obj: obj.title)
    return oc


@route('/video/iview/series/{series}')
def GetEpisodesBySeries(series):
    show = iView_Series(series)
    json = JSON.ObjectFromURL('http://iview.abc.net.au/api/legacy/flash/?series=' + series)
    oc = ObjectContainer(view_group='InfoList', title2=show.title, no_cache=True)
    episodes = show.episodes
    rtmp_url = iView_Config.RTMP_URL()
 
    for item in episodes:
        oc.add(Play_iView(item['id'], item['title'], item['description'], item['url'], item['thumb'], item['duration'], rtmp_url, item['live']))

    oc.objects.sort(key=lambda obj: obj.title)

    return oc


@route('/video/iview/episode/play')
def Play_iView(video_id, iView_Title, iView_Summary, iView_Path, iView_Thumb, iView_Duration, video_url, iView_live=0,
               include_container=False):
    HTTP.ClearCache()
    iView_live = int(iView_live)

    call_args = {
        "video_id": video_id,
        "iView_Title": iView_Title,
        "iView_Summary": iView_Summary,
        "iView_Path": iView_Path,
        "iView_Thumb": iView_Thumb,
        "iView_Duration": int(iView_Duration),
        "video_url": video_url,
        "iView_live": iView_live,
        "include_container": True,
    }

    Log('==== Video ====')
    Log('Title: ' + iView_Title)
    Log('RTMP Path: ' + video_url)
    Log('Clip Path: ' + iView_Config.CLIP_PATH())
    Log('Video Path: ' + iView_Path)
    Log('==== End Video ====')
    
    vco = VideoClipObject(
        url= 'http://abc.net.au/iview/#/view/' + video_id, #Callback(Play_iView, **call_args),
        rating_key=iView_Path,
        title=iView_Title,
        summary=iView_Summary,
        thumb=iView_Thumb,
        duration=int(iView_Duration),
    )

    if include_container:
        return ObjectContainer(objects=[vco])
    else:
        return vco
