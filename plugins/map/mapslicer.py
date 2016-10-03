
from __future__ import division

import dric
import dric.support
from logging import getLogger
from os import listdir, mkdir
from os.path import join, split, splitext, exists, abspath, basename
from shutil import rmtree
from builtins import range
from PIL import Image
from hashlib import sha1 as hashfunc
from multiprocessing import Pool
from timeit import default_timer



_logger = getLogger('dric.mapslicer')

@dric.support.Configurable('config.yml', 'config')
@dric.support.Configurable('maps.ini', 'maps')
class MapSlicerPlugin(dric.Plugin):
    def setup(self, eventbus):
        if(self.config['invoke'] != 'NEVER'):
            for file in listdir(self.get_source_dir()):
                dest_dir = self.get_dest_dir(file)
                if (exists(dest_dir) is False):
                    _logger.debug('MKDIR %s', dest_dir)
                    mkdir(dest_dir)
                source_file = join(self.get_source_dir(), file)
                if(self.config['invoke'] == 'ALWAYS'):
                    self.slice(source_file, dest_dir)
                elif(self.config['invoke'] == 'IF_CHANGED'):
                    if(self.source_has_changed(source_file, dest_dir)):
                        self.slice(source_file, dest_dir)
            
    def configure(self, configuration):
        if(configuration.id == 'config'):
            slicer_config = configuration.configuration['map']['slicer']
            self.config = slicer_config
        elif(configuration.id == 'maps'):
            self.maps = configuration.configuration
    
    def slice(self, source_file, dest_dir):
        _logger.info('Slicing %s', source_file)
        
        # open source file
        image = Image.open(source_file)

        # clear destination directory
        rmtree(dest_dir)
        mkdir(dest_dir)

        source_file_name = basename(source_file)
        
        if(source_file_name in self.maps):
            max_zoom = int(self.maps[source_file_name]['zoom']) + 1
        else:
            max_zoom = int(self.config['zoom']) + 1

        for zoom_level in range(0, max_zoom):
            start_time = default_timer()     
            self.slice_for_zoom_level(image, zoom_level, dest_dir, self.config['zoom'])
            elapsed = default_timer() - start_time     
            _logger.debug('Sliced zoom level %d/%d in %f ms', zoom_level, max_zoom, elapsed)

        image.close()
        
        # add the hash for IF_CHANGED feature
        self.add_hash(source_file, dest_dir)

    def slice_for_zoom_level(self, image, zoom_level, dest_dir, max_zoom):
        zoom_dir = join(dest_dir, str(zoom_level))
        mkdir(zoom_dir)

        for col in range(0, 2**zoom_level):
            col_dir = join(zoom_dir, str(col))
            mkdir(col_dir)
            for row in range(0, 2**zoom_level):
                row_filename = str(row) + '.png'
                row_file = join(col_dir, row_filename)

                side = image.size[0] / (2**zoom_level)
                region = (side*col, side*row, side*(col+1), side*(row+1))

                self.create_tile (image, region, row_file) 

    def create_tile(self, image, region, row_file):
        small = image.crop(region)
        tile = small.resize((256,256))
        tile.save(row_file)
    
    def source_has_changed(self, source_file, dest_dir):
        hash_file = join(dest_dir, '.source_hash')
        if(exists(hash_file) is False):
            return True
        f = file(hash_file, 'r')
        old_hash = f.read()
        new_hash = self.calculate_hash(source_file)
        return old_hash != new_hash

    def add_hash(self, source_file, dest_dir):
        hash = self.calculate_hash(source_file)
        f = file(join(dest_dir, '.source_hash'), 'w')
        f.write(hash)
        f.close()

    def calculate_hash(self, source_file):
        _logger.debug('Calculating hash for source file %s', source_file)
        hash = hashfunc()
        chunck_size = 1024*8    # read by block of 8MB
        f = open(source_file)
        while True:
            chunck = f.read(chunck_size)
            if chunck == '':
                break
            hash.update(chunck)
        return hash.digest()

    def get_dest_dir(self, file):
        filename = split(file)[1]
        dir_name = splitext(filename)[0]
        dir = join(self.config['destination'], dir_name)
        return abspath(dir)

    def get_source_dir(self):
        return abspath(self.config['source'])

dric.register(__name__, MapSlicerPlugin())
