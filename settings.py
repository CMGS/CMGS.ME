# -*- coding: utf-8 -*-
#: settings for liquidluck

#: site information
site = {
    'name': 'Nolla',
    'url': 'http://cmgs.me',
    'feed': 'http://cmgs.me/feed.xml',
}

config = {
    'source': 'content',

    #: generate html to ouput
    'output': '_site',
    'static': '_site/static',
    #'static_prefix': '/static/',
    'permalink': '{{category}}/{{filename}}',
    'relative_url': False,
    'timezone': '+08:00',
}


author = {
    'default': 'CMGS',
    'vars': {
        'CMGS': {
            'name': 'Kelvin Peng',
            'website': 'http://cmgs.me',
            'email': 'ilskdw@gmail.com',
        }
    }
}

#: active readers
reader = {
    'active': [
        'liquidluck.readers.markdown.MarkdownReader',
        'liquidluck.readers.restructuredtext.RestructuredTextReader',
    ],
}

#: active writers
writer = {
    'active': [
        'liquidluck.writers.core.PostWriter',
        'liquidluck.writers.core.PageWriter',
        'liquidluck.writers.core.ArchiveWriter',
        'liquidluck.writers.core.ArchiveFeedWriter',
        'liquidluck.writers.core.FileWriter',
        'liquidluck.writers.core.StaticWriter',
        'liquidluck.writers.core.YearWriter',
        'liquidluck.writers.core.CategoryWriter',
        'liquidluck.writers.core.CategoryFeedWriter',
        #'liquidluck.writers.core.TagWriter',
        'liquidluck.writers.core.TagCloudWriter',
    ],
    'vars': {
        'archive_output': 'archive.html',
    }
}

#: theme variables
theme = {
    'name': 'moment',
    'vars': {
        'disqus': 'Nolla',
        'analytics': 'UA-11479633-1',
        'allow_comment_on_secret_post': True,

        'navigation': [
            {'title': 'Life', 'link': '/life/'},
            {'title': 'Tag', 'link': '/tag/'},
            {'title': 'Archive', 'link': '/archive'},
        ],
        'elsewhere': [
            {'name': 'Photo', 'link': 'http://mem.cmgs.me'},
            {'name': 'GitHub', 'link': 'https://github.com/CMGS'},
            {'name': 'Bitbucket', 'link': 'https://bitbucket.org/CMGS'},
            {'name': 'Twitter', 'link': 'https://twitter.com/CMGS1988'},
            {'name': 'Facebook', 'link': 'http://facebook.com/cmgs1988'},
            {'name': 'Douban', 'link': 'http://www.douban.com/people/CMGS'},
            {'name': 'Weibo', 'link': 'http://weibo.com/cmgs'},
        ],

        'descriptions': {
            'life': u'直到世界的尽头……',
        },
    }
}
