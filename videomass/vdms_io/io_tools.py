# -*- coding: UTF-8 -*-
"""
Name: io_tools.py
Porpose: input/output redirection to processes (aka threads)
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.13.2023
Code checker: flake8, pylint

This file is part of Videomass.

   Videomass is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   Videomass is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with Videomass.  If not, see <http://www.gnu.org/licenses/>.
"""
import requests
import wx
from videomass.vdms_threads.ffplay_file import FilePlay
from videomass.vdms_threads import generic_downloads
from videomass.vdms_threads.volumedetect import VolumeDetectThread
from videomass.vdms_threads.check_bin import (ff_conf,
                                              ff_formats,
                                              ff_codecs,
                                              ff_topics,
                                              )
from videomass.vdms_utils.utils import open_default_application
from videomass.vdms_dialogs.widget_utils import PopupDialog
from videomass.vdms_ytdlp.ydl_extractinfo import YdlExtractInfo


def youtubedl_getstatistics(url, ssl, parent=None):
    """
    Call `YdlExtractInfo` thread to extract data info.
    During this process a wait pop-up dialog is shown.

    Returns a generator.

    Usage example without pop-up dialog:
        thread = YdlExtractInfo(url)
        thread.join()
        data = thread.data
        yield data
    """
    thread = YdlExtractInfo(url, ssl)
    dlgload = PopupDialog(parent,
                          _("Videomass - Loading..."),
                          _("Wait....\nRetrieving required data."))
    dlgload.ShowModal()
    # thread.join()
    data = thread.data
    dlgload.Destroy()
    yield data
# --------------------------------------------------------------------------#


def stream_play(filepath, tseq, param, autoexit):
    """
    Call Thread for playback with ffplay
    """
    get = wx.GetApp()  # get data from bootstrap
    tseq = tseq if tseq != "-ss 00:00:00.000 -t 00:00:00.000" else ''
    try:
        with open(filepath, encoding='utf8'):
            FilePlay(filepath,
                     tseq,
                     param,
                     get.appset['logdir'],
                     get.appset['ffplay_cmd'],
                     get.appset['ffplayloglev'],
                     get.appset['ffplay+params'],
                     autoexit
                     )
            # thread.join() > attende fine thread, se no ritorna subito
            # error = thread.data
    except IOError:
        wx.MessageBox(_("File does not exist or is invalid:  %s") % (
            filepath), "Videomass", wx.ICON_EXCLAMATION, None)
        return
# -----------------------------------------------------------------------#


def volume_detect_process(filelist, time_seq, audiomap, parent=None):
    """
    Run thread to get audio peak level data and show a
    pop-up dialog with message.
    """
    get = wx.GetApp()
    thread = VolumeDetectThread(time_seq,
                                filelist,
                                audiomap,
                                get.appset['logdir'],
                                get.appset['ffmpeg_cmd']
                                )
    dlgload = PopupDialog(parent,
                          _("Videomass - Loading..."),
                          _("Wait....\nAudio peak analysis."))
    dlgload.ShowModal()
    # thread.join()
    data = thread.data
    dlgload.Destroy()

    return data
# -------------------------------------------------------------------------#


def test_conf():
    """
    Call `check_bin.ffmpeg_conf` to get data to test the building
    configurations of the used FFmpeg executable.
    """
    get = wx.GetApp()
    out = ff_conf(get.appset['ffmpeg_cmd'], get.appset['ostype'])
    return out
# -------------------------------------------------------------------------#


def test_formats():
    """
    Call `check_bin.ff_formats` to get available formats by
    FFmpeg executable.
    """
    get = wx.GetApp()
    out = ff_formats(get.appset['ffmpeg_cmd'], get.appset['ostype'])
    return out
# -------------------------------------------------------------------------#


def test_codecs(type_opt):
    """
    Call `check_bin.ff_codecs` to get available encoders
    and decoders by FFmpeg executable.
    """
    get = wx.GetApp()
    out = ff_codecs(get.appset['ffmpeg_cmd'],
                    type_opt,
                    get.appset['ostype'],
                    )
    return out
# -------------------------------------------------------------------------#


def findtopic(topic):
    """
    Call * check_bin.ff_topic * to run the ffmpeg command to search
    a certain topic..
    """
    get = wx.GetApp()
    retcod = ff_topics(get.appset['ffmpeg_cmd'], topic, get.appset['ostype'])

    if 'Not found' in retcod[0]:
        notf = f"\n{retcod[1]}"
        return notf

    return retcod[1]
# -------------------------------------------------------------------------#


def openpath(where):
    """
    Call `vdms_threads.opendir.open_default_application`.
    """
    ret = open_default_application(where)
    if ret:
        wx.MessageBox(ret, 'Videomass', wx.ICON_ERROR, None)
# -------------------------------------------------------------------------#


def get_github_releases(url, keyname):
    """
    Check for releases data on github page using github API:
        https://developer.github.com/v3/repos/releases/#get-the-latest-release

    see keyname examples here:
    <https://api.github.com/repos/jeanslack/Videomass/releases>
    """
    try:
        response = requests.get(url, timeout=15)
        not_found = None, None

    except Exception as err:
        not_found = 'request error:', err

    else:

        try:
            version = response.json()[f"{keyname}"]

        except Exception as err:
            not_found = 'response error:', err

    if not_found[0]:
        return not_found

    return version, None
# --------------------------------------------------------------------------#


def get_presets(url, dest, msg, parent=None):
    """
    get latest Videomass presets
    """
    thread = generic_downloads.FileDownloading(url, dest)
    dlgload = PopupDialog(parent, _("Videomass - Downloading..."), msg)
    dlgload.ShowModal()
    # thread.join()
    status = thread.data
    dlgload.Destroy()

    return status
# --------------------------------------------------------------------------#
