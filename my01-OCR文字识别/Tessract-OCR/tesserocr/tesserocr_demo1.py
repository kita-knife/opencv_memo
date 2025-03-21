# -*-coding:utf8-*-#

__author__ = 'play4fun'
"""
create time:16/10/21 11:44
"""

from tesserocr import PyTessBaseAPI

images = ['sample.jpg', 'sample2.jpeg','sample3.jpeg']

with PyTessBaseAPI() as api:
    for img in images:
        api.SetImageFile(img)
        print('text:', api.GetUTF8Text())
        print('-----')
        print(api.AllWordConfidences())
        print('-----')
# api is automatically finalized when used in a with-statement (context manager).
# otherwise api.End() should be explicitly called when it's no longer needed.
