# -*- coding: utf-8 -*-
import json, urllib.request, re, sys

class Parse:
  platsrEndpoint = 'http://www.platsr.se/platsr/api/v1/'
  result = {}

  def __init__(self, id):
    collectionUrl = self.platsrEndpoint + 'collection/' + id
    Parse.result = self.parseCollection(self.call(collectionUrl))

  def call(self, url):
    # .encode(sys.stdout.encoding,'replace').decode(sys.stdout.encoding) should be removed in production
    return json.loads(urllib.request.urlopen(url).read().decode('utf-8').encode(sys.stdout.encoding,'replace').decode(sys.stdout.encoding))

  def parseCollection(self, data):
    collection = {}
    collection['title'] = data['Name']

    if 'Image' in data.keys():
      collection['image'] = self.parseImage(self.call(data['Image']['Href']))
    else:
      collection['image'] = False

    collection['author'] = self.parseAuthor(self.call(data['CreatedBy']['Href']))

    collection['places'] = []
    for place in data['Places']:
      collection['places'].append(self.parsePlace(self.call(place['Href'])))

    return collection

  def parseAuthor(self, data):
    author = {}
    author['user'] = data['Username']
    #TODO construct platsr profile link

    return author

  def parsePlace(self, data):
    place = {}
    place['title'] = data['Name']
    place['description'] = data['Description']

    coordinate = re.findall(r'([-]?[0-9]+\.[0-9]+)', data['GmlWGS84'])
    place['coordinate'] = {}
    place['coordinate']['lng'] = coordinate[0]
    place['coordinate']['lat'] = coordinate[1]

    place['author'] = self.parseAuthor(self.call(data['CreatedBy']['Href']))

    place['stories'] = []
    for story in data['Stories']:
      place['stories'].append(self.parseStory(self.call(story['Href'])))

    return place

  def parseImage(self, data):
    image = {}
    image['title'] = data['Name']
    image['description'] = data['Description']
    image['author'] = data['Upphovsman']
    image['file'] = data['Url']
    image['copyrigth'] = self.parseCopyrigth(self.call(data['Copyright']['Href']))

    return image

  def parseStory(self, data):
    story = {}
    story['title'] = data['Name']
    story['description'] = data['Description']
    story['author'] = data['Upphovsman']
    story['copyrigth'] = self.parseCopyrigth(self.call(data['Copyright']['Href']))

    if 'Image' in data.keys():
      story['image'] = self.parseImage(self.call(data['Image']['Href']))
    else:
      story['image'] = False

    return story

  def parseCopyrigth(self, data):
    copyrigth = data['Name']
    return copyrigth


Parse(sys.argv[1])
print (Parse.result)
