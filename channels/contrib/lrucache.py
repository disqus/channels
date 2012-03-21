#!/bin/env python
# vim:ts=4:sw=4


#
#   mpycache - a LRU Cache implementation in python
#   author: Saurav Mohapatra (mohaps@gmail.com)
#   website: http://code.google.com/p/mpycache
#   version: 1.0.0
#   date: 01/01/2010
#   license: Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0.html)
#   Copyright (c) 2010 Saurav Mohapatra (mohaps@gmail.com)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import os;
import sys;
import time;

# a marker object to indicate not found
class _NotFound (object):
    def __init__(self):
        pass;
NOT_FOUND = _NotFound();

# a basic lru cache class

class LRUCache (object):
    DEBUG_DUMP_ENABLED = False;
    @classmethod
    def currentTimeMicros(cls):
        return long(time.time() * 1000.0 * 1000.0);
    # -------------------------------------------------------------------------------------
    #   Create an LRU Cache. (Set maxSize/Age to 0 to turn off the pruning logic)
    #   maxSize = maximum number of elements to keep in cache
    #   maxAgeMs = oldest entry to keep
    #   sizeElasiticity = allow cache to grow till maxSize + sizeElasticity before pruning
    # -------------------------------------------------------------------------------------
    def __init__(self, maxSize=32, maxAgeMs=0.0, sizeElasticity=10):
        self.maxSize = maxSize;
        self.maxAge = long(maxAgeMs * 1000.0);
        self.elasticity = sizeElasticity;
        self.cache = {};    # the actual cache Table
        self.keyTable = {}; # time vs. key
        self.timeStampTable = {}; #key vs. time
    # set key = value in cache
    def put(self, key, value):
        if value:
            self.cache[key] = value;
            self._freshen(key);
        self._prune();
    # get the value for key from cache (default to supplied value)
    def get(self, key, value=None):
        ret = self.cache.get(key, NOT_FOUND);
        # key was not found return default value
        if ret == NOT_FOUND:
            return value;
        # check if value is within acceptable age
        elif not self.maxAge == 0:
            ts = self.timeStampTable[key];
            age = LRUCache.currentTimeMicros() - ts;

            if age > self.maxAge:
                self.erase(key);
                return value;
        # we found the key in cache return it
        else:
            self._freshen(key);
            return ret;
    # erase key
    def erase(self, key):
        if self.has_key(key):
            del self.cache[key];
            ts = self.timeStampTable[key];
            del self.timeStampTable[key];
            del self.keyTable[ts];
    # check if the key is present
    def has_key(self, key):
        return self.cache.has_key(key);
    # the cache current size
    def size(self):
        return len(self.cache);
    # clear the cache of all elements
    def clear(self):
        self.cache.clear();
        self.keyTable.clear();
        self.timeStampTable.clear();

    # "freshen" the key i.e. change the timestamp to current time
    def _freshen(self, key):
        oldTs = self.timeStampTable.get(key, NOT_FOUND);
        if not oldTs == NOT_FOUND:
            del self.timeStampTable[key];
            del self.keyTable[oldTs];
        newTs = LRUCache.currentTimeMicros();
        self.timeStampTable[key] = newTs;
        self.keyTable[newTs] = key;

    # we got to clear off all elements in excess of maxSize or maxAge
    def _prune(self):
        if self.maxSize == 0:
            pass;
        elif self.size()> (self.maxSize + self.elasticity):
            print 'size [%d] is greater than [%d]. pruning...' % (self.size(), self.maxSize + self.elasticity);
            toDel = self.size() - self.maxSize;
            timeStamps = sorted(self.keyTable.keys());
            timeStamps = timeStamps[0:toDel];
            for ts in timeStamps:
                key = self.keyTable[ts];
                del self.keyTable[ts];
                del self.timeStampTable[key];
                del self.cache[key];

    def __str__(self):
        ret = 'LRU Cache (cur=%d, max=%d (+%d),maxAge=%f ms)' % (self.size(), self.maxSize, self.elasticity, 0.001 * self.maxAge);
        return ret;
    #
    # a debug method to dump out the state of the cache
    #
    def dumpState(self, out=sys.stdout):

        out.write(str(self)+'\n');
        if not LRUCache.DEBUG_DUMP_ENABLED:
            return;
        if self.size() > 0:
            out.write('CACHE\n');
            for k,v in self.cache.items():
                out.write('   [%s]=[%s]\n'%(k,v));
            ts = LRUCache.currentTimeMicros();
            out.write('>> KEY TABLE\n');
            keys = sorted(self.keyTable.keys());
            for k in keys:
                out.write('   [%s]=[%s] (AGE=%d usec)\n'%(k,self.keyTable[k], ts - k));

            out.write('>> TSTAMP TABLE\n');
            for k,v in self.timeStampTable.items():
                out.write('   [%s]=[%s]\n'%(k,v));

            out.write('\n');
# sample usage
if __name__ == '__main__':
    lc = LRUCache(3,0.300,0);
    print 'initialized cache : '+str(lc);
    for i in range(0,10):
        lc.put('key'+str(i),'val'+str(i));
        print 'After add #'+str(i+1)+':';
        lc.dumpState();
        lc.put('key2','val2');

    print lc.get('key8');
    lc.dumpState();