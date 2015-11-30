class iview_plugin():
    BASE_URL = 'http://iview.abc.net.au/'
    API_URL = BASE_URL + 'api/'

    CHANNEL_URL = API_URL + 'channels'
    channel_json = JSON.ObjectFromURL(CHANNEL_URL)

    CATEGORY_URL = API_URL + 'category'
    category_json = JSON.ObjectFromURL(CATEGORY_URL)
    i = 0
    j = 0
    channel_list = []
    for key in channel_json['channels']:
        c = channel_json['channels'][i]
        channel = {'id': c['categoryID'],
                   'title': c['title'],
                   'href': c['href'],
                   'num_series': len(c['episodes'])}
        i = i + 1           
        channel_list.append(channel)

    Log(channel_list)
    
    category_list = []
    for key in category_json['categories']:
        c = category_json['categories'][j]
        category = {'id': c['categoryID'],
                    'title': c['title'],
                    'href': c['href'],
                    'num_series': len(c['episodes'])}
        j = j + 1            
        category_list.append(category)

    Log(category_list)
