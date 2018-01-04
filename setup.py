#!/usr/bin/env python

from distutils.core import setup

setup(name='hueify',
      version='0.0.1',
      description='Utility to set Hue lights to match the currently playing Spotify song\'s album artwork',
      author='Ben Wiebe',
      author_email='me@t3kbau5.com',
      url='https://github.com/benwiebe/hueify',
      packages=['hueify'],
      license='GPL-3.0',
      install_requires=[
          #'pyhue',
          'phue',
          'spotipy==2.4.4.1',
          'pillow',
          'scipy',
          'numpy'
      ],
      dependency_links=[
      	'https://github.com/plamere/spotipy/tarball/master#egg=spotipy-2.4.4.1'
      ]
     )