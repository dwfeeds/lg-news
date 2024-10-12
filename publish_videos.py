from copy import deepcopy as clone
from datetime import datetime, timezone
import re
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
                                regions { name originId }
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

                    if not 'mainContentImage' in content or content['mainContentImage'] == None:
                        continue
                    
                    image_url = content['mainContentImage']['staticUrl']

                    sub_category = content['categories'][1]['name'] if len(content['categories']) > 1 else None

                    videos.append({
                        'titleText': content['title'],
                        'category': content['categories'][0]['name'],
                        'subCategory': sub_category,
                        'region_ids': dict([ (r['originId'], r['name']) for r in content['regions'] ]),
                        'regions': [ r['name'] for r in content['regions'] ],
                        'runningTime': content['duration'],
                        'updateTime': content['contentDate'],
                        'onClick': {
                            'targetAppId': 'com.dw.app.dwforsmarttv',
                            'contentId': f"v={content['id']}&list={comp['type']}:{comp['order']}",
                            'type': 'video',
                            'id': content['id'],
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
    
    results = {
        'en-us': [], 
        'es-us': [],
        'de-de': [],
        'en-de': [],
        'de-de': [],
        'en-uk': [],
    }

    all_videos = []

    for l, lang in {
        'en': 'ENGLISH',
        'es': 'SPANISH',
        'de': 'GERMAN'
    }.items():
        videos = sorted(get_videos(lang), reverse=True, key=lambda v: v['updateTime'])
        
        for v in videos:
            v['language'] = l
            all_videos.append(clone(v))

            if l == 'en':
                if not v['region_ids']:
                    results['en-us'].append(v)
                    results['en-de'].append(v)
                    results['en-uk'].append(v)
                else:
                    for origin, name in v['region_ids'].items():
                        if re.match('region:northamerica:', origin) or re.match('region:cala:', origin):
                            results['en-us'].append(v)
                            break
                        elif re.match('region:europe:', origin) or re.match('region:global:', origin):
                            results['en-de'].append(v)
                            results['en-uk'].append(v)
                            break
            elif l == 'es':
                if not v['region_ids']:
                    results['es-us'].append(v)
                else:
                    for origin, name in v['region_ids'].items():
                        if re.match('region:northamerica:', origin) or re.match('region:cala:', origin):
                            results['es-us'].append(v)
                            break
            elif l == 'de':
                if not v['region_ids']:
                    results['de-de'].append(v)
                else:
                    for origin, name in v['region_ids'].items():
                        if re.match('region:europe:', origin) or re.match('region:global', origin):
                            results['de-de'].append(v)
                            break

            del v['region_ids']
            del v['regions']

    fname = "videos_all.json"
    with open(fname, 'w') as f:
        f.write(json.dumps(all_videos, indent=2, ensure_ascii=False))
    print(f"Saved {fname}")

    for locale, videos in results.items():
        fname = f"videos_{locale}.json"
        with open(fname, 'w') as f:
            f.write(json.dumps(videos, indent=2, ensure_ascii=False)) 
        print(f"Saved {fname}")

    now = datetime.now(timezone.utc).isoformat()[:16].replace("T", " ")
    html = ''
    with open("index.tpl") as f:
        html = f.read()
    with open("index.html", 'w') as f:
        f.write(html.replace("%NOW%", now))
    print("Saved index.html")
