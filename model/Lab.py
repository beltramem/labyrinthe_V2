#!/usr/bin/python3

import random as rdm
import numpy as np


class Block:
    
    def __init__(self, id, neighbors = None):
        self.id = id
        self.neighbors = [] if neighbors is None else neighbors
    
    def look_around(self):
        return [tuple([x+(i==ind)*incr for i,x in enumerate(self.id)])
                for ind in range(len(self.id)) for incr in (-1,1)]
    
    def make_connection(self, block):
        if block not in self.neighbors:
            self.neighbors.append(block)
        block.be_connected(self)
    
    def be_connected(self, block):
        if block not in self.neighbors:
            self.neighbors.append(block)
            
        
    
class Wall(Block):
    
    def __init__(self, id, neighbors = None):
        super().__init__(id, neighbors)
    
    def __str__(self):
        return '0'
    
    def __repr__(self) -> str:
        return str({'id':self.id})
    
class Way(Block):
    
    def __init__(self, id, value, neighbors = None):
        super().__init__(id, neighbors)
        for n in self.neighbors:
            self.make_connection(n)
        self.value = value
    
    def break_wall(self, wall:Wall):
        if isinstance(wall, Wall):
            if wall in self.neighbors:
                return Way(wall.id, self.value, wall.neighbors)
            else:
                raise ValueError('{} is not a neighbor'.format(wall))
        else:
            raise TypeError('{}'.format(type(wall)))
        
    def __str__(self):
        # return str(self.value)
        return ' '
    
    def __repr__(self) -> str:
        return str({'id':self.id, 'value':self.value})
    
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, val):
        self.__value = val
        for n in self.neighbors:
            if isinstance(n, Way) and n.value != val:
                n.value = val
    
class Labyrinth:
    
    def __init__(self, shape, nb_exit, nb_internal_break):
        self.__shape = tuple(shape)
        self.__labyrinth = {}
        
        indexes = self.generate_indexes()
        
        cpt = 1
        prod = lambda li : li[0] if len(li) == 1 else li[0]*prod(li[1:])
        for ind in indexes:
            if prod(ind)%2 == 0:
                block = Wall(ind)
            else:
                block = Way(ind, cpt)
                cpt += 1
            
            self[ind] = block
            
            for n in block.look_around():
                if self.check_index(n) and n in self:
                    block.make_connection(self[n])
        
        self.__aff = len(str(cpt))
        
        exit_walls = self.find_exit_walls()
        
        e = 0
        while exit_walls and e < nb_exit:
            exit_wall = exit_walls.pop(rdm.choice(range(len(exit_walls))))
            exit_way = [self[ind] for ind in exit_wall.look_around()
                        if self.check_index(ind)
                        and isinstance(self[ind],Way)][0]
            
            self[exit_wall.id] = exit_way.break_wall(exit_wall)
            e+=1
        
        internal_walls = self.find_internal_walls()
        intra_area_walls = []
        while self.get_number_of_areas() != 1:
            wall = internal_walls.pop(rdm.choice(range(len(internal_walls))))
            way_1, way_2 = [block for block in wall.neighbors
                            if isinstance(block,Way)]
            
            if way_1.value != way_2.value:
                self[wall.id] = way_1.break_wall(wall)
            else:
                intra_area_walls.append(wall)
        
        internal_walls.extend(intra_area_walls)
        b = 0
        while internal_walls and b < nb_internal_break:
            wall = internal_walls.pop(rdm.choice(range(len(internal_walls))))
            way = rdm.choice([block for block in wall.neighbors
                                if isinstance(block,Way)])
            self[wall.id] = way.break_wall(wall)
            b += 1
    
    def generate_indexes(self, shape = None):
        if shape is None:
            shape = self.shape
            
        prod = lambda li : li[0] if len(li) == 1 else li[0]*prod(li[1:])
        rep = [1]+[prod(shape[0:i]) for i in range(1,len(shape))]
        return [tuple([j%(rep[i]*shape[i])//rep[i]
                 for i in range(len(shape))])
                for j in range(prod(shape))]
    
    def check_index(self, index):
        return False if [x for i,x in enumerate(index)
                         if (x<0 or x>=self.shape[i])] else True
    
    def find_exit_walls(self):
        prod = lambda li : li[0] if len(li) == 1 else li[0]*prod(li[1:])
        return [self[ind] for ind in self
                if len([x for i,x in enumerate(ind)
                        if x in (0, self.shape[i]-1)]) == 1
                and prod([x for i,x in enumerate(ind)
                          if x not in (0, self.shape[i]-1)])%2 != 0
                and isinstance(self[ind], Wall)]
    
    def find_internal_walls(self):
        prod = lambda li : li[0] if len(li) == 1 else li[0]*prod(li[1:])
        return [self[ind] for ind in self if prod(ind)%2 == 0
                and not [x for i,x in enumerate(ind)
                         if x in (0,self.shape[i]-1)]
                and [n for n in self[ind].neighbors if isinstance(n,Way)]]
                
    
    def get_number_of_areas(self):
        return len(set([self[ind].value for ind in self
                        if isinstance(self[ind],Way)]))
    
    def to_array(self):
        array = np.zeros(self.shape)
        for ind in self:
            array[ind] = 0 if isinstance(self[ind],Way) else 1
        
        return array
        
    def __str__(self):
        if len(self.shape) > 2:
            plans = self.generate_indexes(self.shape[2:])
            p_indexes = [sorted(sorted([ind for ind in self if ind[2:] == p ],
                                       key=lambda x:x[0]),
                                key=lambda x:x[1])
                         for p in plans]
        else:
            p_indexes = [sorted(sorted(list(self), key=lambda x:x[0]),
                                key=lambda x:x[1])]
        
        txt_li = []
        for p in p_indexes:
            txt_li.append('\n')
            txt_li.append(
                '(., .{})'.format(''.join([', {}'.format(x)
                                           for x in p[0][2:]]))
            )
            
            
            txt_li.append(
                '\n'.join(
                    [' '.join(
                        ['{{:>{}}}'.format(1).format(
                            str(self[p[i+j*self.shape[0]]]))
                         for i in range(self.shape[0])])
                     for j in range(self.shape[1])])
            )
        
        return '\n'.join(txt_li)
    
    def __getitem__(self, key):
        return self.__labyrinth[key]
    
    def __setitem__(self, key, block:Block):
        self.__labyrinth[key] = block
    
    def __contains__(self, index):
        return True if index in self.__labyrinth else False
    
    def __iter__(self):
        return iter(self.__labyrinth)
    
    def __next__(self):
        return next(self.__labyrinth)
    
    @property
    def shape(self):
        return self.__shape