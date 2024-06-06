from datetime import datetime
import requests
import json

url = 'https://webapi.dw.com/graphql'

def get_videos(lang):
    videos = []

    query = '''query getVideoList($lang: Language!) {
    playoutRootNavigation(lang: $lang) {
        latestMediaChildren {
            id
            templateType
            contentComposition {
                informationSpaces {
                    id
                    compositionComponents {
                        ... on CompositionComponent {
                            type
                            order
                        }
                        contents {
                            ... on Video {
                                id
                                title
                                duration
                                regions { name }
                                categories { name }
                                duration
                                contentDate
                                mainContentImage {
                                    staticUrl
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
    '''

    variables = {
        'lang': lang
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    response = requests.post(url, json={
        'query': query,
        'variables': variables,
    }, headers=headers)

    if response.status_code != 200:
        print("Failed to fetch data: Status code", response.status_code)
        return []

    p = response.json()['data']['playoutRootNavigation']['latestMediaChildren']
    for x in p:
        if x['templateType'] != 'WEBAPP_VIDEO':
            print(f"Skipped {x['templateType']}")
            continue
        count = 0
        for space in x['contentComposition']['informationSpaces']:
            for comp in space['compositionComponents']:
                for content in comp['contents']:
                    if not 'id' in content:
                        continue

                    if content['duration'] > 600:
                        print(f"Skipped {content['id']}: {content['title']} ({int(content['duration']/60)}m)")
                        continue

                    now = datetime.now().isoformat()
                    if not 'mainContentImage' in content or content['mainContentImage'] == None:
                        continue
                    
                    image_url = content['mainContentImage']['staticUrl']

                    sub_category = content['categories'][1]['name'] if len(content['categories']) > 1 else None

                    videos.append({
                        'titleText': content['title'],
                        'category': content['categories'][0]['name'],
                        'subCategory': sub_category,
                        'regions': [r['name'] for r in content['regions']],
                        'runningTime': content['duration'],
                        'updateTime': content['contentDate'],
                        'onClick': {
                            'targetAppId': 'com.dw.app.dwforsmarttv',
                            'contentId': f"v={content['id']}&list={comp['type']}:{comp['order']}",
                            'launchParam': None
                        },
                        'providerLogo': {
                            'url': 'https://dwapps.de/feed/dw_white_800.png',
                            'width': 800,
                            'height': 800,
                            'bgColor': '',
                        },
                        'image': {
                            'url': image_url.replace('${formatId}', '6'),
                            'width': 940,
                            'height': 529,
                            'bgColor': ''
                        },
                        'image4k': {
                            'url': image_url.replace('${formatId}', '7'),
                            'width': 3997,
                            'height': 2250,
                            'bgColor': ''
                        }
                    })
    return videos
            

if __name__ == '__main__':
    for l, lang in {
        'en': 'ENGLISH',
        'es': 'SPANISH',
        'de': 'GERMAN'
    }.items():
        fname = f"videos_{l}.json"  
        with open(fname, 'w') as f:
            f.write(json.dumps(get_videos(lang), indent=2))
        print(f"Saved {fname}")
