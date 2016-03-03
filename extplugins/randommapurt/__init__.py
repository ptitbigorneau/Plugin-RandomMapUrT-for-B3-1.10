# -*- coding: utf-8 -*-
#
# RandomMapUrT For Urban Terror plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2015 PtitBigorneau - www.ptitbigorneau.fr
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

__author__  = 'PtitBigorneau www.ptitbigorneau.fr'
__version__ = '1.3'

import b3
import b3.plugin
import b3.events
from b3.functions import getCmd

import random
import time, threading, thread

def fexist(fichier):
    
    try:
    
        file(fichier)
     
        return True
   
    except:
  
        return False 

class RandommapurtPlugin(b3.plugin.Plugin):
    
    _adminPlugin = None
    _shufflemapcycle = False
    _rmonoff = True
    _test = None
    _listmap = []
    _listmapsplayed = []
    _comptemaps = 1
	
    def onLoadConfig(self):
	
        self._shufflemapcycle = self.getSetting('settings', 'shufflemapcycle', b3.BOOLEAN, self._shufflemapcycle)

    def onStartup(self):

        self._adminPlugin = self.console.getPlugin('admin')
        
        if not self._adminPlugin:

            self.error('Could not find admin plugin')
            return False
        
        self.registerEvent('EVT_GAME_MAP_CHANGE', self.onGameMapChange)

        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

                func = getCmd(self, cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)
        
        self._listmapsplayed.append(self.console.game.mapName)

        self.listemaps()

        if not self._shufflemapcycle:

            if self.nmap <= 5:

                self._shufflemapcycle = True
                self.debug('maps < 6 shufflemapcycle : %s' % self._shufflemapcycle)

        if self._shufflemapcycle:

            random.shuffle(self._listmap)

            if self.console.game.mapName == self._listmap[0]:

                self.console.write("g_nextmap %s"%self._listmap[1])

            else:

                self.console.write("g_nextmap %s"%self._listmap[0])

    def onGameMapChange(self, event):
        
        self._listmapsplayed.append(self.console.game.mapName)

        if self._rmonoff:

            self._comptemaps += 1

            if self._shufflemapcycle:

                if self._comptemaps == self.nmap and self.nmap > 1:

                    self._comptemaps = 1

                    random.shuffle(self._listmap)

                x = self._comptemaps - 1

                if self.console.game.mapName == self._listmap[x] and self.nmap > 1:

                    x += 1

                self.nextmap = self._listmap[x]

                thread.start_new_thread(self.wait, (50,))

                self.console.write("g_nextmap %s"%self.nextmap)

            else:

                if self.nmap >= 8:

                    z = 5

                if self.nmap < 8:

                    z = self.nmap / 2

                if self._comptemaps == z:

                    self._comptemaps = z -1 
                    self._listmapsplayed.remove(self._listmapsplayed[0])

                self.randommap()

        self.debug("shufflemapcycle %s"%self._listmap)
        self.debug("listmapsplayed %s"%self._listmapsplayed)
        self.debug("mapsplayed %s / %s"%(self._comptemaps, self.nmap))
    
    def randommap(self):

        self.random()

        while self.nextmap in  self._listmapsplayed:

            self.random()

        thread.start_new_thread(self.wait, (50,))

        self.console.write("g_nextmap %s"%self.nextmap)

    def listemaps(self):

        self._listemap = []

        mapcycletxt = self.console.getCvar('g_mapcycle').getString()
        homepath = self.console.getCvar('fs_homepath').getString()
        basepath = self.console.getCvar('fs_basepath').getString()
        gamepath = self.console.getCvar('fs_game').getString()

        mapcyclefile = basepath + "/" + gamepath + "/" + mapcycletxt

        if fexist(mapcyclefile) == False:
                
            mapcyclefile = homepath + "/" + gamepath + "/" + mapcycletxt

        self.debug('Mapcycle : %s' % mapcyclefile)

        fichier = open(mapcyclefile, "r")

        contenu = fichier.readlines()
        fichier.close()

        for ligne in contenu:
            
            ligne = ligne.replace("\n", "")
            ligne = ligne.replace("\r", "")
            ligne = ligne.replace(" ", "")
            
            if ligne != "":
                
                if self._test == None:
                    
                    if "{" in ligne:

                        self._test = "test"
                        continue
            
                    else:

                        self._listmap.append(ligne)
                        
                    if self._test != None:
            
                        if "}" in ligne:

                            self._test = None

        self.nmap = 0

        for map in self._listmap:
            self.nmap += 1

    def random(self):

        namap = random.randint(0, self.nmap-1)

        x = namap
        self.nextmap = self._listmap[x]

        return

    def ut4mapname(self, map):

        if map[:4] == 'ut4_': map = map[4:]
        
        elif map[:3] == 'ut_': map = map[3:]

        return map

    def wait(self, temps):

        time.sleep(temps)
          
        map = self.nextmap

        map = self.ut4mapname(map)

        if not self._shufflemapcycle:

            self.console.write('bigtext "^2Random Nextmap: ^4%s^7"'%map)

        else:

            self.console.write('bigtext "^3ShuffleMapcycle Nextmap: ^4%s^7"'%map)

    def cmd_randommap(self, data, client, cmd=None):
        
        """\
        activate / deactivate RandomMapUrT
        """
        
        if data:
            
            input = self._adminPlugin.parseUserCmd(data)
        
        else:
        
            if self._rmonoff:

                client.message('RandomMapUrT ^2activated')

            else:

                client.message('RandomMapUrT ^1deactivated')

            client.message('!randommap <on / off>')
            return

        if input[0] == 'on':

            if not self._rmonoff:

                self._rmonoff = True
                message = '^2activated'

            else:

                client.message('RandomMapUrT is already ^2activated') 

                return False

        if input[0] == 'off':

            if self._rmonoff:

                self._rmonoff = False
                message = '^1deactivated'

            else:
                
                client.message('RandomMapUrT is already ^1disabled')                

                return False

        client.message('RandomMapUrT %s'%(message))

    def cmd_shufflemapcycle(self, data, client, cmd=None):
        
        """\
        activate / deactivate ShuffleMapcycle
        """
        
        if data:
            
            input = self._adminPlugin.parseUserCmd(data)
        
        else:
        
            if self._shufflemapcycle:

                client.message('ShuffleMapcycle ^2activated')

            else:

                client.message('ShuffleMapcycle ^1deactivated')

            client.message('!shufflemapcycle <on / off>')
            return

        if input[0] == 'on':

            if not self._shufflemapcycle:

                self._shufflemapcycle = True
                message = '^2activated'

            else:

                client.message('ShuffleMapcycle is already ^2activated') 

                return False

        if input[0] == 'off':

            if self._shufflemapcycle:

                self._shufflemapcycle = False
                message = '^1deactivated'

            else:
                
                client.message('ShuffleMapcycle is already ^1disabled')                

                return False

        client.message('ShuffleMapcycle %s'%(message))

    def cmd_shufflemaps(self, data, client, cmd=None):
        
        """\
        Shuffle mapcycle
        """

        random.shuffle(self._listmap)

        if self.console.game.mapName == self._listmap[0] and self.nmap > 1:

            map = self._listmap[1]

        else:

            map = self._listmap[0]

        self.console.write("g_nextmap %s"%map)

        map = self.ut4mapname(map)

        client.message('ShuffleMapcycle Nextmap : %s'%map)

        self.console.write('bigtext "^3ShuffleMapcycle Nextmap: ^4%s^7"'%map)

        self.debug("shufflemapcycle %s"%self._listmap)

