import json, urllib.request, re, html, codecs, sys

def removeNonAscii(string):
  #Platsr.se does not return utf-8 encoded stuff so remove non supported Ascii(150)
  return ''.join(i for i in string if 150 != ord(i))

class Parse:
  platsrEndpoint = 'http://www.platsr.se/platsr/api/v1/'
  result = {}

  def __init__(self, id):
    collectionUrl = self.platsrEndpoint + 'collection/' + id
    Parse.result = self.parseCollection(self.call(collectionUrl))

  def call(self, url):
    print('Hämtar: ' + url)
    return json.loads(urllib.request.urlopen(url).read().decode('utf-8'))

  def parseCollection(self, data):
    collection = {}
    collection['title'] = data['Name']
    collection['description'] = data['Description']

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
    place['coordinate']['lng'] = coordinate[1]
    place['coordinate']['lat'] = coordinate[0]

    place['author'] = self.parseAuthor(self.call(data['CreatedBy']['Href']))

    if 'Stories' in data.keys():
      place['stories'] = []
      for story in data['Stories']:
        place['stories'].append(self.parseStory(self.call(story['Href'])))
    else:
      place['stories'] = False

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
    story['content'] = data['Description']
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

class OdysseyMarkdown:
  markdown = ''

  def __init__(self, data):
    self.config(data)

    for place in data['places']:
      self.place(place)

  def config(self, data):
    self.markdown = '```\n' + '-title: "' + data['title'] + '"\n-author: "' + data['author']['user'] + '"\n' + '```\n'

  def place(self, data):
    self.markdown += '#' + data['title'] + '\n```\n' + '- center: [' + data['coordinate']['lng'] + ', ' + data['coordinate']['lat'] + ']\n' + '- zoom: 15\n' + 'L.marker([' + data['coordinate']['lng'] + ', ' + data['coordinate']['lat'] + ']).actions.addRemove(S.map)\n```\n'
    self.markdown += '**' + data['description'] + '**\n'

    if data['stories'] != False:
      for story in data['stories']:
        self.story(story)

  def story(self, data):
    self.markdown += '##' + data['title'] + '\n'
    self.markdown += '*Av ' + data['author'] + ' \nCopyright: ' + data['copyrigth'] + '*\n\n'

    if data['image'] != False:
      self.image(data['image'])

    # There is probably more HTML tags that needs to be converted
    storyContent = data['content'].replace('<p>', '').replace('</p>', '\n\n')
    storyContent = storyContent.replace('<em>', '*').replace('</em>', '*')
    storyContent = storyContent.replace('<strong>', '**').replace('</strong>', '**')


    self.markdown += storyContent + '\n'

  def image(self, data):
    self.markdown += '![' + data['description'] + '](' + data['file'] + ')\n'
    self.markdown += '**' + data['title'] + '**\n'
    self.markdown += '*Upphovsman: ' + data['author'] + ' Copyright: ' + data['copyrigth'] + '*\n'

Parse(sys.argv[1])
output = OdysseyMarkdown(Parse.result)

outputFile = open('output/markdown.txt', 'w')
outputFile.write(removeNonAscii(html.unescape(output.markdown)))

odysseyHtml = open('template.html', 'r').read()
odysseyHtml = odysseyHtml.replace('content=""', 'content="' + Parse.result['description'] + '"').replace('<script id="md_template" type="text/template"></script>', '<script id="md_template" type="text/template">' + removeNonAscii(html.unescape(output.markdown)) + '</script>')
outputOdysseyFile = codecs.open('output/odyssey/index.html', 'w', 'utf-8')
outputOdysseyFile.write(odysseyHtml)

print('\nKlar')
