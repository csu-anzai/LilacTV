# -*- coding: utf-8 -*-
import sys
import os
import time
import json
from xml.dom import minidom
import xml.etree.ElementTree as ET
import xbmc
import xbmcgui

import iptv
import FileUtil

import xbmcaddon

__cwd__ = '/storage/.kodi/addons/script.updateShortCut'
__UpdateFlag__ = os.path.join( __cwd__, 'resources', "script.skinshortcuts" )
__lib__ = os.path.join( __cwd__, 'resources')
__AddonPath__ = '/storage/.kodi/addons'
__favouritepath__ = '/storage/.kodi/userdata/addon_data/plugin.program.super.favourites/Super Favourites'


def dis_or_enable_addon(addon_id, enable="true"):
    addon = '"%s"' % addon_id
    if xbmc.getCondVisibility("System.HasAddon(%s)" % addon_id) and enable == "true":
        return xbmc.log("### Skipped %s, reason = allready enabled" % addon_id)
    elif not xbmc.getCondVisibility("System.HasAddon(%s)" % addon_id) and enable == "false":
        xbmc.log("### Skipped %s, reason = not installed" % addon_id)
        quit()
    else:
        do_json = '{"jsonrpc":"2.0","id":1,"method":"Addons.SetAddonEnabled","params":{"addonid":%s,"enabled":%s}}' % (addon, enable)
        query = xbmc.executeJSONRPC(do_json)
        response = json.loads(query)
        if enable == "true":
            xbmc.log("### Enabled %s, response = %s" % (addon_id, response))
        else:
            xbmc.log("### Disabled %s, response = %s" % (addon_id, response))
    return xbmc.executebuiltin('Container.Update(%s)' % xbmc.getInfoLabel('Container.FolderPath'))


def AddonEnable():
    fi=open(os.path.join(__UpdateFlag__, 'mainmenu.DATA.xml'))
    lines=fi.readlines()
    fi.close()

    for line in lines:
        if 'plugin://' in line:
            item=line.split('"')[1]
            addon=item.split('/')[2]
            dis_or_enable_addon(addon)


def AddNewRepo(repo):
    sPath=os.path.join(__lib__, repo)
    if os.path.exists(sPath):
        if not os.path.exists(os.path.join(__AddonPath__,repo)):
            os.system("cp -r "+sPath+" "+ __AddonPath__)
            time.sleep(0.5)
            xbmc.executebuiltin('UpdateLocalAddons')
            time.sleep(0.5)
            dis_or_enable_addon(repo)

        os.system("rm -rf "+sPath)


def AddNewAddon(repo, addon):
    Flag = False
    #Check addon
    AddonPath = os.path.join(__AddonPath__, addon)
    if not os.path.exists(AddonPath):
        #Add-ons
        AddNewRepo(repo)
        time.sleep(2)
        xbmc.executebuiltin('InstallAddon(%s)' % addon)
        Flag = True

    #Custom file
    UsrDataPath = os.path.join(__lib__, 'usr', addon)
    if os.path.exists(UsrDataPath):
        FileUtil.TargetFileUpdate('usr/'+addon, '/storage/.kodi/userdata/addon_data', isFolder = True)

    return Flag


def CheckValue_XML(xml_file,PTag,STag,value):
    if not (os.path.exists(xml_file)):
        return False

    doc = ET.parse(xml_file)
    root = doc.getroot()

    for e in root.iter(PTag):
        if e.findtext(STag) == value:
            return True

    return False


def CheckSkin():
    settings_file = '/storage/.kodi/userdata/guisettings.xml'
    #Change skin
    ParentTag = 'lookandfeel'
    SubTag = 'skin'

    if os.path.exists("/storage/.kodi/userdata/addon_data/service.libreelec.settings"):
        if not CheckValue_XML(settings_file, ParentTag, SubTag, 'skin.arctic.zephyr.plus'):
            dialog = xbmcgui.Dialog()
            yes = dialog.yesno("Skin Error", "LilacTV doesn't support this skin.", "You may need to re-install to go back LilacTV.","Do you want to re-install now?")
            if yes:
                xbmc.executebuiltin("RunScript(/etc/seebo/python_updater.py, Kor, true, true)")
                sys.exit()


def GetVPNCheck():
    fi=open("/storage/.config/vpnbook.sh")
    lines=fi.readlines()
    fi.close()

    for line in lines:
        if '#curl' in line:
            return True
        else:
            pass

    return False


def CheckUpdate():
    if os.path.exists("/storage/.config/CheckUpdate.sh"):
        os.system("/storage/.config/./CheckUpdate.sh")


def UpgradeDependency(addon_id, currentVersion):
    if os.path.exists(os.path.join(__lib__, addon_id)):
        if os.path.exists(os.path.join(__AddonPath__, addon_id)):
            version = xbmcaddon.Addon(addon_id).getAddonInfo('version')
            if not version == currentVersion:
                FileUtil.TargetFileUpdate(addon_id, __AddonPath__, isFolder = True)
        else: 
            FileUtil.TargetFileUpdate(addon_id, __AddonPath__, isFolder = True)


if __name__=='__main__':

    if os.path.exists("/storage/.kodi/userdata/addon_data/service.libreelec.settings/oe_settings.xml"):

        if os.path.exists("/storage/.kodi/patches"):
            os.system("python /storage/.kodi/patches/patch.py")
            os.system("rm -rf /storage/.kodi/patches")

        if not os.path.exists(__UpdateFlag__):
            if not os.path.exists("/storage/.NeedUpdate.ch"):
                CheckUpdate()

        Flag = False        
        if FileUtil.UpdateCheck4Favourites("예능"):
            Flag = True
        if FileUtil.UpdateCheck4Favourites("YouTube"):
            Flag = True
        if FileUtil.UpdateCheck4YouTubeLive():
            Flag = True
        if FileUtil.UpdateCheck4LilacTV():
            Flag = True
        if not os.path.exists(os.path.join(__favouritepath__,'System','JooVideo')):
            #즐겨찾기 [어저께 티비] 업데이트
            FileUtil.TargetFileUpdate("JooVideo", os.path.join(__favouritepath__,'System'), isFolder = True)        

        if os.path.exists(__UpdateFlag__):

            if os.path.exists(os.path.join(__lib__, 'reloadPVR.py')):
                FileUtil.TargetFileUpdate('autostart.sh', '/storage/.config', isFolder = False)
                FileUtil.TargetFileUpdate('reloadPVR.py', '/storage', isFolder = False)
                FileUtil.TargetFileUpdate('Seebo.cron', '/storage', isFolder = False)
                FileUtil.TargetFileUpdate('vpnbook.sh', '/storage/.config', isFolder = False)
                time.sleep(0.2)
                os.system("chmod -R 777 /storage/.config/autostart.sh")                
                os.system("chmod -R 777 /storage/.config/vpnbook.sh")
                os.system("chmod -R 777 /storage/reloadPVR.py")
                os.system("chmod -R 777 /storage/Seebo.cron")
                os.system("crontab /storage/Seebo.cron")
                os.system("/storage/.config/./vpnbook.sh")
                time.sleep(0.5)

            UpgradeDependency('script.module.urlresolver','5.0.32a')

            if FileUtil.UpdateCheck4Skin():
                Flag = True

            os.system("rm -rf /storage/.kodi/addons/script.updateShortCut/resources/plugin.*")
            os.system("rm -rf /storage/.kodi/addons/script.updateShortCut/resources/service.*")

        else:
            CheckSkin()

        if Flag and not os.path.exists("/storage/.NeedUpdate.ch"):
            xbmc.executebuiltin('ReloadSkin()')

        AddNewAddon('repository.tempest', 'plugin.video.tempest')
        AddNewAddon('repository.supremacy', 'plugin.video.yoda')
        AddNewAddon('repository.supremacy', 'plugin.video.themagicdragon')
        AddNewAddon('repository.mancaverepo', 'plugin.video.mc1080p')
        

