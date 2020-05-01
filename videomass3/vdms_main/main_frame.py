# -*- coding: UTF-8 -*-

#########################################################
# Name: main_frame.py
# Porpose: top window main frame
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
#########################################################

# This file is part of Videomass.

#    Videomass is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass.  If not, see <http://www.gnu.org/licenses/>.

#########################################################
import wx
import wx.lib.agw.gradientbutton as GB
import webbrowser
import ssl
import urllib.request
import os
from videomass3.vdms_dialogs import time_selection
from videomass3.vdms_dialogs import settings
from videomass3.vdms_dialogs import infoprg
from videomass3.vdms_frames import while_playing
from videomass3.vdms_frames import ffmpeg_search
from videomass3.vdms_frames.mediainfo import Mediainfo
from videomass3.vdms_panels import choose_topic
from videomass3.vdms_panels import filedrop
from videomass3.vdms_panels import textdrop
from videomass3.vdms_panels import youtubedl_ui
from videomass3.vdms_panels import av_conversions
from videomass3.vdms_panels.long_processing_task import Logging_Console
from videomass3.vdms_panels import presets_manager
from videomass3.vdms_io import IO_tools
from videomass3.vdms_sys.msg_info import current_release

# get videomass wx.App attribute
get = wx.GetApp()
PYLIB_YDL = get.pylibYdl  # youtube_dl library with None is in use
EXEC_YDL = get.execYdl  # youtube-dl executable with False do not exist
OS = get.OS  # ID of the operative system:
DIR_CONF = get.DIRconf  # default configuration directory
FILE_CONF = get.FILEconf  # pathname of the file configuration
WORK_DIR = get.WORKdir  # pathname of the current work directory
LOGDIR = get.LOGdir
CACHEDIR = get.CACHEdir
# # colour rappresentetion in rgb
AZURE_NEON = 158, 201, 232
YELLOW_LMN = 255, 255, 0
BLUE = 0, 7, 12
# colour rappresentetion in html
ORANGE = '#f28924'
YELLOW = '#a29500'

# set widget colours in some case with html rappresentetion:
# AZURE = '#d9ffff'  # rgb form (wx.Colour(217,255,255))
# YELLOW = '#a29500'
# RED = '#ea312d'
# ORANGE = '#f28924'
# GREENOLIVE = '#6aaf23'
# GREEN = '#268826'


class MainFrame(wx.Frame):
    """
    This is the main frame top window for panels implementation.
    """
    def __init__(self, setui, pathicons):
        """
        NOTE: 'SRCpath' is a current work directory of Videomass
               program. How it can be localized depend if Videomass is
               run as portable program or installated program.
        """
        barC = setui[4][12].split(',')
        barColor = wx.Colour(int(barC[0]), int(barC[1]), int(barC[2]))
        # toolbar panel colour
        bBtnC = setui[4][13].split(',')
        self.bBtnC = wx.Colour(int(bBtnC[0]), int(bBtnC[1]), int(bBtnC[2]))
        # toolbar buttons colour
        fBtnC = setui[4][14].split(',')
        self.fBtnC = wx.Colour(int(fBtnC[0]), int(fBtnC[1]), int(fBtnC[2]))
        # Buttons Font Colour
        SRCpath = setui[1]  # share dir (are where the origin files?):
        # ---------------------------#
        self.iconset = setui[4][11]
        self.videomass_icon = pathicons[0]
        self.icon_runconversion = pathicons[2]
        self.icon_ydl = pathicons[25]
        self.icon_mainback = pathicons[23]
        self.icon_mainforward = pathicons[24]
        # -------------------------------#
        self.data_files = None  # list of items in list control
        self.data_url = None  # list of urls in text box
        self.file_destin = None  # path name for file saved destination
        self.file_src = None  # input files list
        self.filedropselected = None  # selected name on file drop
        self.time_seq = ''  # ffmpeg format time specifier with flag -ss, -t
        self.time_read = {'start seek': ['', ''], 'time': ['', '']}
        self.duration = []  # empty if not file imported
        self.topicname = None  # panel name shown

        wx.Frame.__init__(self, None, -1, style=wx.DEFAULT_FRAME_STYLE)
        # ----------- panel toolbar buttons
        self.btnpanel = wx.Panel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL)

        infoIbmp = wx.Bitmap(pathicons[3], wx.BITMAP_TYPE_ANY)
        previewbmp = wx.Bitmap(pathicons[4], wx.BITMAP_TYPE_ANY)
        cutbmp = wx.Bitmap(pathicons[5], wx.BITMAP_TYPE_ANY)
        saveprfbmp = wx.Bitmap(pathicons[8], wx.BITMAP_TYPE_ANY)
        newprfbmp = wx.Bitmap(pathicons[20], wx.BITMAP_TYPE_ANY)
        delprfbmp = wx.Bitmap(pathicons[21], wx.BITMAP_TYPE_ANY)
        editprfbmp = wx.Bitmap(pathicons[22], wx.BITMAP_TYPE_ANY)

        self.btn_metaI = GB.GradientButton(self.btnpanel,
                                           size=(-1, 25),
                                           bitmap=infoIbmp,
                                           label=_("Multimedia Streams")
                                           )
        self.btn_metaI.SetBaseColours(startcolour=wx.Colour(AZURE_NEON),
                                      foregroundcolour=wx.Colour(self.fBtnC)
                                      )
        self.btn_metaI.SetBottomEndColour(self.bBtnC)
        self.btn_metaI.SetBottomStartColour(self.bBtnC)
        self.btn_metaI.SetTopStartColour(self.bBtnC)
        self.btn_metaI.SetTopEndColour(self.bBtnC)

        self.btn_playO = GB.GradientButton(self.btnpanel,
                                           size=(-1, 25),
                                           bitmap=previewbmp,
                                           label=_("Preview")
                                           )
        self.btn_playO.SetBaseColours(startcolour=wx.Colour(AZURE_NEON),
                                      foregroundcolour=wx.Colour(self.fBtnC)
                                      )
        self.btn_playO.SetBottomEndColour(self.bBtnC)
        self.btn_playO.SetBottomStartColour(self.bBtnC)
        self.btn_playO.SetTopStartColour(self.bBtnC)
        self.btn_playO.SetTopEndColour(self.bBtnC)

        self.btn_duration = GB.GradientButton(self.btnpanel,
                                              size=(-1, 25),
                                              bitmap=cutbmp,
                                              label=_("Duration")
                                              )
        self.btn_duration.SetBaseColours(startcolour=wx.Colour(AZURE_NEON),
                                         foregroundcolour=wx.Colour(self.fBtnC)
                                         )
        self.btn_duration.SetBottomEndColour(self.bBtnC)
        self.btn_duration.SetBottomStartColour(self.bBtnC)
        self.btn_duration.SetTopStartColour(self.bBtnC)
        self.btn_duration.SetTopEndColour(self.bBtnC)

        self.btn_saveprf = GB.GradientButton(self.btnpanel,
                                             size=(-1, 25),
                                             bitmap=saveprfbmp,
                                             label=_("Save Configuration")
                                             )
        self.btn_saveprf.SetBaseColours(startcolour=wx.Colour(AZURE_NEON),
                                        foregroundcolour=wx.Colour(self.fBtnC)
                                        )
        self.btn_saveprf.SetBottomEndColour(self.bBtnC)
        self.btn_saveprf.SetBottomStartColour(self.bBtnC)
        self.btn_saveprf.SetTopStartColour(self.bBtnC)
        self.btn_saveprf.SetTopEndColour(self.bBtnC)

        self.btn_newprf = GB.GradientButton(self.btnpanel,
                                            size=(-1, 25),
                                            bitmap=newprfbmp,
                                            label=_("New..")
                                            )
        self.btn_newprf.SetBaseColours(startcolour=wx.Colour(AZURE_NEON),
                                       foregroundcolour=wx.Colour(self.fBtnC)
                                       )
        self.btn_newprf.SetBottomEndColour(self.bBtnC)
        self.btn_newprf.SetBottomStartColour(self.bBtnC)
        self.btn_newprf.SetTopStartColour(self.bBtnC)
        self.btn_newprf.SetTopEndColour(self.bBtnC)

        self.btn_delprf = GB.GradientButton(self.btnpanel,
                                            size=(-1, 25),
                                            bitmap=delprfbmp,
                                            label=_("Delete..")
                                            )
        self.btn_delprf.SetBaseColours(startcolour=wx.Colour(AZURE_NEON),
                                       foregroundcolour=wx.Colour(self.fBtnC)
                                       )
        self.btn_delprf.SetBottomEndColour(self.bBtnC)
        self.btn_delprf.SetBottomStartColour(self.bBtnC)
        self.btn_delprf.SetTopStartColour(self.bBtnC)
        self.btn_delprf.SetTopEndColour(self.bBtnC)

        self.btn_editprf = GB.GradientButton(self.btnpanel,
                                             size=(-1, 25),
                                             bitmap=editprfbmp,
                                             label=_("Edit..")
                                             )
        self.btn_editprf.SetBaseColours(startcolour=wx.Colour(AZURE_NEON),
                                        foregroundcolour=wx.Colour(self.fBtnC)
                                        )
        self.btn_editprf.SetBottomEndColour(self.bBtnC)
        self.btn_editprf.SetBottomStartColour(self.bBtnC)
        self.btn_editprf.SetTopStartColour(self.bBtnC)
        self.btn_editprf.SetTopEndColour(self.bBtnC)

        self.btnpanel.SetBackgroundColour(barColor)
        # ---------- others panel instances:
        self.ChooseTopic = choose_topic.Choose_Topic(self,
                                                     OS,
                                                     pathicons[1],
                                                     pathicons[18],
                                                     pathicons[19]
                                                     )
        #self.ChooseTopic.SetBackgroundColour(BLUE)
        self.ytDownloader = youtubedl_ui.Downloader(self, OS)
        self.VconvPanel = av_conversions.AV_Conv(self,
                                                 OS,
                                                 pathicons[6],  # playfil
                                                 pathicons[7],  # resetfil
                                                 pathicons[9],  # resize
                                                 pathicons[10],  # crop
                                                 pathicons[11],  # rotate
                                                 pathicons[12],  # deinter
                                                 pathicons[13],  # ic_denoi
                                                 pathicons[14],  # analyzes
                                                 pathicons[15],  # settings
                                                 pathicons[17],  # peaklevel
                                                 pathicons[18],  # audiotr
                                                 self.bBtnC,
                                                 self.fBtnC,
                                                 )
        self.fileDnDTarget = filedrop.FileDnD(self)
        self.textDnDTarget = textdrop.TextDnD(self)
        self.ProcessPanel = Logging_Console(self)
        self.PrstsPanel = presets_manager.PrstPan(self,
                                                  SRCpath,
                                                  DIR_CONF,
                                                  WORK_DIR,
                                                  OS,
                                                  pathicons[14],  # analyzes
                                                  pathicons[17],  # peaklevel
                                                  self.bBtnC,
                                                  self.fBtnC,
                                                  )
        # hide panels
        self.fileDnDTarget.Hide()
        self.textDnDTarget.Hide()
        self.ytDownloader.Hide()
        self.VconvPanel.Hide()
        self.ProcessPanel.Hide()
        self.PrstsPanel.Hide()
        # Layout toolbar buttons:
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)  # sizer base global
        grid_pan = wx.FlexGridSizer(1, 7, 0, 0)
        grid_pan.Add(self.btn_metaI, 0, wx.CENTER | wx.ALL, 5)
        grid_pan.Add(self.btn_playO, 0, wx.CENTER | wx.ALL, 5)
        grid_pan.Add(self.btn_duration, 0, wx.CENTER | wx.ALL, 5)
        grid_pan.Add(self.btn_saveprf, 0, wx.CENTER | wx.ALL, 5)
        grid_pan.Add(self.btn_newprf, 0, wx.CENTER | wx.ALL, 5)
        grid_pan.Add(self.btn_delprf, 0, wx.CENTER | wx.ALL, 5)
        grid_pan.Add(self.btn_editprf, 0, wx.CENTER | wx.ALL, 5)
        self.btnpanel.SetSizer(grid_pan)  # set panel
        self.mainSizer.Add(self.btnpanel, 0, wx.EXPAND, 0)
        # Layout externals panels:
        self.mainSizer.Add(self.ChooseTopic, 1, wx.EXPAND | wx.ALL, 0)
        self.mainSizer.Add(self.fileDnDTarget, 1, wx.EXPAND | wx.ALL, 0)
        self.mainSizer.Add(self.textDnDTarget, 1, wx.EXPAND | wx.ALL, 0)
        self.mainSizer.Add(self.ytDownloader, 1, wx.EXPAND | wx.ALL, 0)
        self.mainSizer.Add(self.VconvPanel, 1, wx.EXPAND | wx.ALL, 0)
        self.mainSizer.Add(self.ProcessPanel, 1, wx.EXPAND | wx.ALL, 0)
        self.mainSizer.Add(self.PrstsPanel, 1, wx.EXPAND | wx.ALL, 0)
        # ----------------------Set Properties----------------------#
        self.SetTitle("Videomass")
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(self.videomass_icon, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        if OS == 'Darwin':
            self.SetSize((1030, 600))
        elif OS == 'Windows':
            self.SetSize((980, 650))
        else:
            # self.SetSize((930, 600))
            self.SetSize((980, 750))
        # self.CentreOnScreen() # se lo usi, usa CentreOnScreen anziche Centre
        self.SetSizer(self.mainSizer)
        # Tooltips:
        self.btn_duration.SetToolTip(_('Specify the duration or portion of '
                                       'the time globally. this can affect '
                                       'many functions.'))
        self.btn_metaI.SetToolTip(_("Show additional multimedia information."))
        self.btn_playO.SetToolTip(_("Choose a file to playback in the "
                                    "destination folder"))
        self.btn_saveprf.SetToolTip(_("Save the settings on presets manager"))
        self.btn_newprf.SetToolTip(_("Create a new profile from yourself "
                                     "and save it in the selected preset."))
        self.btn_delprf.SetToolTip(_("Delete the selected profile."))
        self.btn_editprf.SetToolTip(_("Edit the selected profile."))
        # menu bar
        self.videomass_menu_bar()
        # tool bar main
        self.videomass_tool_bar()
        # status bar
        self.sb = self.CreateStatusBar(1)
        # hide toolbar, buttons bar and disable some file menu items
        self.toolbar.Hide()
        self.btnpanel.Hide()
        self.menu_items()

        self.Layout()
        # ---------------------- Binding (EVT) ----------------------#
        self.fileDnDTarget.btn_save.Bind(wx.EVT_BUTTON, self.onCustomSave)
        self.textDnDTarget.btn_save.Bind(wx.EVT_BUTTON, self.onCustomSave)
        self.Bind(wx.EVT_BUTTON, self.Cut_range, self.btn_duration)
        self.Bind(wx.EVT_BUTTON, self.Saveprofile, self.btn_saveprf)
        self.Bind(wx.EVT_BUTTON, self.Newprofile, self.btn_newprf)
        self.Bind(wx.EVT_BUTTON, self.Delprofile, self.btn_delprf)
        self.Bind(wx.EVT_BUTTON, self.Editprofile, self.btn_editprf)
        self.Bind(wx.EVT_BUTTON, self.ImportInfo, self.btn_metaI)
        self.Bind(wx.EVT_BUTTON, self.ExportPlay, self.btn_playO)
        self.Bind(wx.EVT_CLOSE, self.on_close)  # controlla la chiusura (x)

    # -------------------Status bar settings--------------------#

    def statusbar_msg(self, msg, color):
        """
        set the status-bar with messages and color types
        """
        if color is None:
            self.sb.SetBackgroundColour(wx.NullColour)
        else:
            self.sb.SetBackgroundColour(color)
        self.sb.SetStatusText(msg)
        self.sb.Refresh()
    # ------------------------------------------------------------------#

    def choosetopicRetrieve(self):
        """
        Retrieve to choose topic panel
        """
        self.topicname = None
        self.textDnDTarget.Hide(), self.fileDnDTarget.Hide()
        if self.ytDownloader.IsShown():
            self.ytDownloader.Hide()

        elif self.VconvPanel.IsShown():
            self.VconvPanel.Hide()

        elif self.PrstsPanel.IsShown():
            self.PrstsPanel.Hide()

        self.ChooseTopic.Show(), self.toolbar.Hide()
        self.btnpanel.Hide(), self.avpan.Enable(False)
        self.prstpan.Enable(False), self.ydlpan.Enable(False)
        self.startpan.Enable(False), self.logpan.Enable(False)

        self.statusbar_msg('', None)
        self.Layout()
    # ------------------------------------------------------------------#

    def menu_items(self):
        """
        enable or disable some menu items in according by showing panels
        """
        self.saveme.Enable(False),
        self.new_prst.Enable(False), self.del_prst.Enable(False)
        self.restore.Enable(False), self.default.Enable(False)
        self.default_all.Enable(False), self.refresh.Enable(False)
        if self.ChooseTopic.IsShown() == True:
            self.avpan.Enable(False), self.prstpan.Enable(False),
            self.ydlpan.Enable(False), self.startpan.Enable(False)
            self.logpan.Enable(False)
        if PYLIB_YDL is not None:
            if EXEC_YDL:
                if os.path.exists(EXEC_YDL):
                    return
            self.ydlused.Enable(False)
            self.ydllatest.Enable(False)
            self.ydlupdate.Enable(False)
        else:
            self.ydlupdate.Enable(False)

    # ---------------------- Event handler (callback) ------------------#
    # This series of events are interceptions of the filedrop panel
    # ----------------------------- Options ----------------------------#

    def Cut_range(self, event):
        """
        Call dialog to Set a global time sequence on all imported
        media. Here set self.time_seq and self.time_read attributes
        """
        data = ''

        dial = time_selection.Time_Duration(self, self.time_seq)
        retcode = dial.ShowModal()
        if retcode == wx.ID_OK:
            data = dial.GetValue()
            if data == '-ss 00:00:00 -t 00:00:00':
                data = ''
                self.time_read['start seek'] = ['', '']
                self.time_read['time'] = ['', '']
                self.btn_duration.SetBottomEndColour(self.bBtnC)
            else:
                self.btn_duration.SetBottomEndColour(wx.Colour(YELLOW_LMN))
                # set a more readable time
                ss = data.split()[1]  # the -ss flag
                h, m, s = ss.split(':')
                start = (int(h) * 3600 + int(m) * 60 + int(s))
                t = data.split()[3]  # the -t flag
                h, m, s = t.split(':')
                time = (int(h) * 3600 + int(m) * 60 + int(s))
                self.time_read['start seek'] = [ss, start]
                self.time_read['time'] = [t, time]

            self.time_seq = data
        else:
            dial.Destroy()
            return
    # ------------------------------ Menu  Streams -----------------------#

    def ImportInfo(self, event):
        """
        Redirect input files at stream_info for media information
        """
        if self.topicname == 'Youtube Downloader':
            self.ytDownloader.on_show_info()
        else:
            dialog = Mediainfo(self.data_files, OS,)
            dialog.Show()
    # ------------------------------------------------------------------#

    def ExportPlay(self, event):
        """
        Playback with FFplay

        """
        with wx.FileDialog(self, "Videomass: Open a file to playback",
                           defaultDir=self.file_destin,
                           # wildcard="Audio source (%s)|%s" % (f, f),
                           style=wx.FD_OPEN |
                           wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()

        IO_tools.stream_play(pathname,
                             '',  # time_seq is useless for the exported file
                             '',  # no others parameters are needed
                             )
    # ------------------------------------------------------------------#

    def Saveprofile(self, event):
        """
        Store new profile with same current settings of the panel shown
        (Video Conversion & Audio Conversion)..
        Every modification on the panel shown will be reported when saving
        a new profile.
        """
        if self.VconvPanel.IsShown():
            self.VconvPanel.Addprof()
        # elif self.AconvPanel.IsShown():
            # self.AconvPanel.Addprof()
        else:
            print('Videomass: Error, no panels shown')
    # ------------------------------------------------------------------#

    def Newprofile(self, event):
        """
        Store new profile in the selected preset of the presets manager
        panel. The list is reloaded automatically after pressed ok button
        in the dialog for update view.
        """
        if self.PrstsPanel.IsShown():
            self.PrstsPanel.Addprof()
        else:
            print('Videomass: Error, no presets manager panel shown')
    # ------------------------------------------------------------------#

    def Delprofile(self, event):
        """
        Delete the selected preset of the presets manager
        panel.
        """
        if self.PrstsPanel.IsShown():
            self.PrstsPanel.Delprof()
    # ------------------------------------------------------------------#

    def Editprofile(self, event):
        """
        Edit selected item in the list control of the presets manager
        panel. The list is reloaded automatically after pressed ok button
        in the dialog.
        """
        if self.PrstsPanel.IsShown():
            self.PrstsPanel.Editprof(self)
    # ------------------------------------------------------------------#

    def onCustomSave(self, event):
        """
        Intercept the button 'save' event in the filedrop or textdrop
        panels and sets file destination path

        """
        self.File_Save(self)
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        switch to panels or destroy the videomass app.

        """
        if self.ProcessPanel.IsShown():
            self.ProcessPanel.on_close(self)

        # elif self.topicname:
        else:
            if wx.MessageBox(_('Are you sure you want to exit?'), _('Exit'),
                             wx.ICON_QUESTION | wx.YES_NO,
                             self) == wx.YES:
                self.Destroy()
    # ------------------------------------------------------------------#

    def on_Kill(self):
        """
        Try to kill application during a process thread
        that does not want to terminate with the abort button

        """
        self.Destroy()

    # -------------   BUILD THE MENU BAR  ----------------###

    def videomass_menu_bar(self):
        """
        Make a menu bar. Per usare la disabilitazione di un menu item devi
        prima settare l'attributo self sull'item interessato - poi lo gestisci
        con self.item.Enable(False) per disabilitare o (True) per abilitare.
        Se vuoi disabilitare l'intero top di items fai per esempio:
        self.menuBar.EnableTop(6, False) per disabilitare la voce Help.
        """
        self.menuBar = wx.MenuBar()

        # ----------------------- file
        fileButton = wx.Menu()
        dscrp = (_("Choose a Destination folder.."),
                 _("Choice a folder where save processed files"))
        self.file_save = fileButton.Append(wx.ID_SAVE, dscrp[0], dscrp[1])
        fileButton.AppendSeparator()
        dscrp = (_("Create new preset "),
                 _("Create a new preset to use on Presets Manager"))
        self.new_prst = fileButton.Append(wx.ID_NEW, dscrp[0], dscrp[1])
        fileButton.AppendSeparator()
        dscrp = (_("Save the current preset as separated file"),
                 _("Make a back-up of the selected preset on combobox"))
        self.saveme = fileButton.Append(wx.ID_REVERT_TO_SAVED,
                                        dscrp[0], dscrp[1])
        dscrp = (_("Restore a previously saved preset"),
                 _("Replace the selected preset with other saved custom "
                   "preset."))
        self.restore = fileButton.Append(wx.ID_REPLACE, dscrp[0], dscrp[1])
        dscrp = (_("Reset the current preset "),
                 _("Replace the selected preset with default values."))
        self.default = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        fileButton.AppendSeparator()
        dscrp = (_("Reset all presets "),
                 _("Revert all presets to default values"))
        self.default_all = fileButton.Append(wx.ID_UNDO, dscrp[0], dscrp[1])
        fileButton.AppendSeparator()
        dscrp = (_("Remove preset"),
                 _("Remove the selected preset on Presets Manager"))
        self.del_prst = fileButton.Append(wx.ID_DELETE, dscrp[0], dscrp[1])
        fileButton.AppendSeparator()
        self.refresh = fileButton.Append(wx.ID_REFRESH,
                                         _("Reload presets list"),
                                         _("..Sometimes it can be useful"))
        fileButton.AppendSeparator()
        exitItem = fileButton.Append(wx.ID_EXIT, _("Exit"),
                                     _("Close Videomass"))
        self.menuBar.Append(fileButton, "&File")

        # ------------------ tools button
        toolsButton = wx.Menu()

        ffmpegButton = wx.Menu()  # ffmpeg sub menu
        dscrp = (_("While playing"),
                 _("Show useful keyboard shortcuts when playing "
                   "or previewing with ffplay"))
        playing = ffmpegButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        ffmpegButton.AppendSeparator()
        dscrp = (_("Integrated specifications"),
                 _("Shows the built-ins configuration features of FFmpeg"))
        checkconf = ffmpegButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        ffmpegButton.AppendSeparator()
        dscrp = (_("Muxers and Demuxers"),
                 _("Muxers and demuxers available on FFmpeg in use."))
        ckformats = ffmpegButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        ffmpegButton.AppendSeparator()
        ckcoders = ffmpegButton.Append(wx.ID_ANY, _("Encoders"),
                                       _("Shows available encoders on FFmpeg"))
        dscrp = (_("Decoders"), _("Shows available decoders on FFmpeg"))
        ckdecoders = ffmpegButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        ffmpegButton.AppendSeparator()
        dscrp = (_("Search topics"),
                 _("A easy utility to search for information on FFmpeg "
                   "topics and options"))
        searchtopic = ffmpegButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        toolsButton.Append(wx.ID_ANY, "&FFmpeg", ffmpegButton)

        ydlButton = wx.Menu()  # ydl sub menu
        dscrp = (_("Version in Use"),
                 _("Shows the version in use"))
        self.ydlused = ydlButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Check for Update"),
                 _("Check for the latest version available on GitHub"))
        self.ydllatest = ydlButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        ydlButton.AppendSeparator()
        dscrp = (_("Update youtube-dl"),
                 _("Update with latest version of youtube-dl"))
        self.ydlupdate = ydlButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        toolsButton.Append(wx.ID_ANY, _("&Youtube-dl"), ydlButton, )

        self.menuBar.Append(toolsButton, _("&Tools"))
        # ------------------ Go button
        goButton = wx.Menu()
        self.startpan = goButton.Append(wx.ID_ANY, _("Home panel"),
                                        _("jump to the start panel"))
        goButton.AppendSeparator()
        self.prstpan = goButton.Append(wx.ID_ANY, _("Presets manager"),
                                       _("jump to the Presets Manager panel"))
        self.avpan = goButton.Append(wx.ID_ANY, _("A/V conversions"),
                                     _("jump to the Audio/Video Conv. panel"))
        goButton.AppendSeparator()
        self.ydlpan = goButton.Append(wx.ID_ANY, _("YouTube downloader"),
                                    _("jump to the YouTube Downloader panel"))
        goButton.AppendSeparator()
        dscrp = (_("Log viewing console"),
                _("View log messages of the last process executed"))

        self.logpan = goButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])

        sysButton = wx.Menu()  # system sub menu
        dscrp = (_("Configuration directory"),
                 _("Opens the Videomass configuration directory"))
        openconfdir = sysButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Log directory"),
                 _("Opens the Videomass log directory if it exists"))
        openlogdir = sysButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Cache directory"),
                 _("Opens the Videomass cache directory if exists"))
        opencachedir = sysButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        goButton.Append(wx.ID_ANY, _("&System"), sysButton)

        self.menuBar.Append(goButton, _("&View"))
        # ------------------ setup button
        setupButton = wx.Menu()
        setupItem = setupButton.Append(wx.ID_PREFERENCES, _("Setup"),
                                       _("General Settings"))

        self.menuBar.Append(setupButton, _("&Preferences"))

        # ------------------ help buton
        helpButton = wx.Menu()
        helpItem = helpButton.Append(wx.ID_HELP, _("User Guide"), "")
        wikiItem = helpButton.Append(wx.ID_ANY, _("Wiki"), "")
        helpButton.AppendSeparator()
        issueItem = helpButton.Append(wx.ID_ANY, _("Issue tracker"), "")
        helpButton.AppendSeparator()
        transItem = helpButton.Append(wx.ID_ANY, _('Translation...'), '')
        helpButton.AppendSeparator()
        DonationItem = helpButton.Append(wx.ID_ANY, _("Donation"), "")
        helpButton.AppendSeparator()
        docFFmpeg = helpButton.Append(wx.ID_ANY, _("FFmpeg documentation"), "")
        helpButton.AppendSeparator()
        checkItem = helpButton.Append(wx.ID_ANY, _("Check new releases"), "")
        infoItem = helpButton.Append(wx.ID_ABOUT, _("About Videomass"), "")
        self.menuBar.Append(helpButton, _("&Help"))

        self.SetMenuBar(self.menuBar)

        # -----------------------Binding menu bar-------------------------#
        # ----FILE----
        self.Bind(wx.EVT_MENU, self.File_Save, self.file_save)
        self.Bind(wx.EVT_MENU, self.New_preset, self.new_prst)
        self.Bind(wx.EVT_MENU, self.Saveme, self.saveme)
        self.Bind(wx.EVT_MENU, self.Restore, self.restore)
        self.Bind(wx.EVT_MENU, self.Default, self.default)
        self.Bind(wx.EVT_MENU, self.Default_all, self.default_all)
        self.Bind(wx.EVT_MENU, self.Del_preset, self.del_prst)
        self.Bind(wx.EVT_MENU, self.Refresh, self.refresh)
        self.Bind(wx.EVT_MENU, self.Quiet, exitItem)
        # ----TOOLS----
        self.Bind(wx.EVT_MENU, self.durinPlayng, playing)
        self.Bind(wx.EVT_MENU, self.Check_conf, checkconf)
        self.Bind(wx.EVT_MENU, self.Check_formats, ckformats)
        self.Bind(wx.EVT_MENU, self.Check_enc, ckcoders)
        self.Bind(wx.EVT_MENU, self.Check_dec, ckdecoders)
        self.Bind(wx.EVT_MENU, self.Search_topic, searchtopic)
        self.Bind(wx.EVT_MENU, self.ydl_used, self.ydlused)
        self.Bind(wx.EVT_MENU, self.ydl_latest, self.ydllatest)
        self.Bind(wx.EVT_MENU, self.youtubedl_uptodater, self.ydlupdate)
        # ---- GO -----
        self.Bind(wx.EVT_MENU, self.startPan, self.startpan)
        self.Bind(wx.EVT_MENU, self.prstPan, self.prstpan)
        self.Bind(wx.EVT_MENU, self.avPan, self.avpan)
        self.Bind(wx.EVT_MENU, self.ydlPan, self.ydlpan)
        self.Bind(wx.EVT_MENU, self.logPan, self.logpan)
        self.Bind(wx.EVT_MENU, self.openLog, openlogdir)
        self.Bind(wx.EVT_MENU, self.openConf, openconfdir)
        self.Bind(wx.EVT_MENU, self.openCache, opencachedir)
        # ----SETUP----
        self.Bind(wx.EVT_MENU, self.Setup, setupItem)
        # ----HELP----
        self.Bind(wx.EVT_MENU, self.Helpme, helpItem)
        self.Bind(wx.EVT_MENU, self.Wiki, wikiItem)
        self.Bind(wx.EVT_MENU, self.Issues, issueItem)
        self.Bind(wx.EVT_MENU, self.Translations, transItem)
        self.Bind(wx.EVT_MENU, self.Donation, DonationItem)
        self.Bind(wx.EVT_MENU, self.DocFFmpeg, docFFmpeg)
        self.Bind(wx.EVT_MENU, self.CheckNewReleases, checkItem)
        self.Bind(wx.EVT_MENU, self.Info, infoItem)

    # --------Menu Bar Event handler (callback)
    # -------------------------- File Menu -----------------------------#

    def File_Save(self, event):
        """
        Open the file browser dialog to choice output file destination
        """
        dialdir = wx.DirDialog(self, _("Videomass: Choose a directory"))
        if dialdir.ShowModal() == wx.ID_OK:
            self.file_destin = '%s' % (dialdir.GetPath())
            self.textDnDTarget.on_file_save(self.file_destin)
            self.fileDnDTarget.on_file_save(self.file_destin)
            self.textDnDTarget.file_dest = self.file_destin
            self.fileDnDTarget.file_dest = self.file_destin
            dialdir.Destroy()
    # --------------------------------------------------#

    def Quiet(self, event):
        """
        destroy the videomass.
        """
        self.on_close(self)
    # --------------------------------------------------#

    def New_preset(self, event):
        """
        Call New_preset_prst from Prrsets Manager panel

        """
        if self.PrstsPanel.IsShown():
            self.PrstsPanel.New_preset_prst()
    # --------------------------------------------------#

    def Saveme(self, event):
        """
        call method for save a single file copy of preset.
        """
        if self.PrstsPanel.IsShown():
            self.PrstsPanel.Saveme()
    # --------------------------------------------------#

    def Restore(self, event):
        """
        call restore a single preset file in the path presets of the program
        """
        if self.PrstsPanel.IsShown():
            self.PrstsPanel.Restore()
    # --------------------------------------------------#

    def Default(self, event):
        """
        call copy the single original preset file into the configuration
        folder. This replace new personal changes make at profile.
        """
        if self.PrstsPanel.IsShown():
            self.PrstsPanel.Default()
    # --------------------------------------------------#

    def Default_all(self, event):
        """
        call restore all preset files in the path presets of the program
        """
        if self.PrstsPanel.IsShown():
            self.PrstsPanel.Default_all()
    # --------------------------------------------------#

    def Del_preset(self, event):
        """
        Call Del_preset_prst from Prrsets Manager panel
        Remove the selected preset from /prst presets
        """
        if self.PrstsPanel.IsShown():
            self.PrstsPanel.Del_preset_prst()
    # --------------------------------------------------#

    def Refresh(self, event):
        """
        call Pass to reset_list function for re-charging list
        """
        if self.PrstsPanel.IsShown():
            self.PrstsPanel.Refresh()

    # --------- Menu  Preferences

    def Setup(self, event):
        """
        Call the module setup for setting preferences
        """
        # self.parent.Setup(self)
        setup_dlg = settings.Setup(self, self.iconset)
        setup_dlg.ShowModal()

    # --------- Menu Tools

    def durinPlayng(self, event):
        """
        show dialog with shortcuts keyboard for FFplay
        """
        dlg = while_playing.While_Playing(OS)
        dlg.Show()
    # ------------------------------------------------------------------#

    def Check_conf(self, event):
        """
        Call IO_tools.test_conf

        """
        IO_tools.test_conf()
    # ------------------------------------------------------------------#

    def Check_formats(self, event):
        """
        IO_tools.test_formats

        """
        IO_tools.test_formats()
    # ------------------------------------------------------------------#

    def Check_enc(self, event):
        """
        IO_tools.test_encoders

        """
        IO_tools.test_codecs('-encoders')
    # ------------------------------------------------------------------#

    def Check_dec(self, event):
        """
        IO_tools.test_encoders

        """
        IO_tools.test_codecs('-decoders')
    # ------------------------------------------------------------------#

    def Search_topic(self, event):
        """
        Show a dialog box to help you find FFmpeg topics

        """
        dlg = ffmpeg_search.FFmpeg_Search(OS)
        dlg.Show()
    # -------------------------------------------------------------------#

    def ydl_used(self, event, msgbox=True):
        """
        check version of youtube-dl used from 'Version in Use' bar menu
        """
        waitmsg = _('\nWait....\nCheck installed version\n')
        if PYLIB_YDL is None:  # youtube-dl library
            import youtube_dl
            this = youtube_dl.version.__version__
            if msgbox:
                wx.MessageBox(_('You are using youtube-dl '
                                'version {}').format(this), 'Videomass')
            return this
        else:
            if os.path.exists(EXEC_YDL):
                this = IO_tools.youtubedl_update([EXEC_YDL, '--version'],
                                                 waitmsg)
                if this[1]:  # failed
                    wx.MessageBox("%s" % this[0], "Videomass: error",
                                  wx.ICON_ERROR, self)
                    return None

                if msgbox:
                    wx.MessageBox(_('You are using youtube-dl '
                                    'version {}').format(this[0]), 'Videomass')
                    return this[0]

                return this[0].strip()
        if msgbox:
                wx.MessageBox(_('ERROR: {0}\n\nyoutube-dl has not been '
                              'installed yet.').format(PYLIB_YDL),
                              'Videomass', wx.ICON_ERROR)
        return None
    # -----------------------------------------------------------------#

    def ydl_latest(self, event, msgbox=True):
        """
        check for new releases of youtube-dl from 'Check for Update'
        bar menu
        """
        url = 'https://yt-dl.org/update/LATEST_VERSION'
        this = None if msgbox is False else self.ydl_used(self, False)

        if this:  # youtube-dl as pylibrary
            info = _("A new version of youtube-dl is available on GitHub:")
        else:
            info = _("The latest version of youtube-dl on GitHub is:")

        latest = IO_tools.youtubedl_latest(url)

        if latest[1]:  # failed
            wx.MessageBox("\n{0}\n\n{1}".format(url, latest[1]),
                          "Videomass: error", wx.ICON_ERROR, self)
            return latest

        if latest[0].strip() == this:
            if msgbox:
                wx.MessageBox(_("youtube-dl is up-to-date {}").format(this),
                              "Videomass", wx.ICON_INFORMATION, self)
            return None, None
        else:
            if msgbox:
                wx.MessageBox('{} {}'.format(info, latest[0]), 'Videomass',
                              wx.ICON_INFORMATION, self)
            return latest
    # -----------------------------------------------------------------#

    def youtubedl_uptodater(self, event):
        """
        Update to latest version from 'Update youtube-dl' bar menu
        """
        waitmsg = _('\nWait....\nUpdating youtube-dl')

        if os.path.exists(EXEC_YDL) and PYLIB_YDL is not None:
            if os.path.basename(EXEC_YDL) == 'youtube-dl':  # not youtube-dl.exe
                update = IO_tools.youtubedl_update([EXEC_YDL, '--update'],
                                                   waitmsg)
                if update[1]:  # failed
                    wx.MessageBox("\n%s" % update[0], "Videomass: error",
                                  wx.ICON_ERROR, self)
                    return
                else:
                    wx.MessageBox("\n%s" % update[0], 'Videomass',
                                  wx.ICON_INFORMATION, self)
                    return
            else:  # youtube-dl.exe
                url = 'https://yt-dl.org/update/LATEST_VERSION'
                latest = IO_tools.youtubedl_latest(url)
                if latest[1]:  # failed
                    wx.MessageBox("\n{0}\n\n{1}".format(url, latest[1]),
                                  "Videomass: error", wx.ICON_ERROR, self)
                    return
                this = self.ydl_used(self, False)
                if latest[0].strip() == this:
                    wx.MessageBox(_('youtube-dl is already '
                                    'up-to-date {}').format(this),
                                  "Videomass", wx.ICON_INFORMATION, self)
                    return
                else:
                    upgrade = IO_tools.youtubedl_upgrade(latest[0], EXEC_YDL)

                if upgrade[1]:  # failed
                    wx.MessageBox("%s" % (upgrade[1]), "Videomass: error",
                                  wx.ICON_ERROR, self)
                    return
                wx.MessageBox(_('Successful! youtube-dl is up-to-date '
                                '({0})').format(latest[0]),
                              'Videomass', wx.ICON_INFORMATION)
                return
        else:

            wx.MessageBox(_('ERROR: {0}\n\nyoutube-dl has not been '
                            'installed yet.').format(PYLIB_YDL),
                          'Videomass', wx.ICON_ERROR)
        return
    # ------------------------------------------------------------------#

    def startPan(self, event):
        """
        jump on start panel
        """
        self.choosetopicRetrieve()
    # ------------------------------------------------------------------#

    def prstPan(self, event):
        """
        jump on Presets Manager panel
        """
        if not self.file_src:
            self.statusbar_msg('No files added yet', YELLOW)
        else:
            self.topicname = 'Presets Manager'
            self.on_Forward(self)
    # ------------------------------------------------------------------#

    def avPan(self, event):
        """
        jump on AVconversions panel
        """
        if not self.file_src:
            self.statusbar_msg('No files added yet', YELLOW)
        else:
            self.topicname = 'Audio/Video Conversions'
            self.on_Forward(self)
    # ------------------------------------------------------------------#

    def ydlPan(self, event):
        """
        jumpe on youtube downloader
        """
        if not self.data_url:
            self.statusbar_msg('No URLs added yet', YELLOW)
        else:
            self.topicname = 'Youtube Downloader'
            self.on_Forward(self)
    # ------------------------------------------------------------------#

    def logPan(self, event):
        """
        view last log on console
        """
        self.switch_Process('console view only')
    # ------------------------------------------------------------------#


    def openLog(self, event):
        """
        Open the log diretctory with file manager

        """
        if not os.path.exists(LOGDIR):
            wx.MessageBox(_("Output log has not been created yet."),
                          "Videomass", wx.ICON_INFORMATION, None)
            return
        IO_tools.openpath(LOGDIR)
    # ------------------------------------------------------------------#

    def openConf(self, event):
        """
        Open the configuration folder with file manager

        """
        IO_tools.openpath(DIR_CONF)
    # -------------------------------------------------------------------#

    def openCache(self, event):
        """
        Open the cache dir with file manager if exists
        """
        if not os.path.exists(CACHEDIR):
            wx.MessageBox(_("cache directory has not been created yet."),
                          "Videomass", wx.ICON_INFORMATION, None)
            return
        IO_tools.openpath(CACHEDIR)

    # --------- Menu Edit

    def Helpme(self, event):
        """Online User guide"""
        page = 'https://jeanslack.github.io/Videomass/videomass_use.html'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def Wiki(self, event):
        """Wiki page """
        page = 'https://github.com/jeanslack/Videomass/wiki'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def Issues(self, event):
        """Display Issues page on github"""
        page = 'https://github.com/jeanslack/Videomass/issues'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def Translations(self, event):
        """Display Issues page on github"""
        page = ('https://github.com/jeanslack/Videomass/blob/master/docs/'
                'localization_howto.md')
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def Donation(self, event):
        """Display Issues page on github"""
        page = 'https://jeanslack.github.io/Videomass/donation.html'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def DocFFmpeg(self, event):
        """Display FFmpeg page documentation"""
        page = 'https://www.ffmpeg.org/documentation.html'
        webbrowser.open(page)
    # -------------------------------------------------------------------#

    def CheckNewReleases(self, event):
        """
        Check for new version releases of Videomass, useful for
        users with Videomass installer on Windows and MacOs.

        FIXME : There are was some error regarding
        [SSL: CERTIFICATE_VERIFY_FAILED]
        see:
        <https://stackoverflow.com/questions/27835619/urllib-and-ssl-
        certificate-verify-failed-error>
        <https://stackoverflow.com/questions/35569042/ssl-certificate-
        verify-failed-with-python3>
        """
        # HACK fix soon the ssl certificate
        cr = current_release()
        # ssl._create_default_https_context = ssl._create_unverified_context
        try:
            context = ssl._create_unverified_context()
            f = urllib.request.urlopen('https://pypi.org/project/videomass/',
                                       context=context
                                       )
            myfile = f.read().decode('UTF-8')
            page = myfile.strip().split()
            indx = ''
            for v in page:
                if 'class="package-header__name">' in v:
                    indx = page.index(v)

        except IOError as error:
            wx.MessageBox("%s" % error, "Videomass: ERROR",
                          wx.ICON_ERROR, None
                          )
            return

        except urllib.error.HTTPError as error:
            wx.MessageBox("%s" % error, "Videomass: ERROR",
                          wx.ICON_ERROR
                          )
            return

        if indx:
            new_major, new_minor, new_micro = page[indx + 2].split('.')
            new_version = int('%s%s%s' % (new_major, new_minor, new_micro))
            this_major, this_minor, this_micro = cr[2].split('.')
            this_version = int('%s%s%s' % (this_major, this_minor, this_micro))

            if new_version > this_version:
                wx.MessageBox(_('A new version (v{0}) of Videomass is '
                                'available\nfrom <https://pypi.org/project/'
                                'videomass/>').format(page[indx + 2]),
                              "Videomass: Check new version",
                              wx.ICON_INFORMATION, None)
            else:
                wx.MessageBox(_('You are already using the latest version '
                                '(v{0}) of Videomass').format(cr[2]),
                              "Videomass: Check new version",
                              wx.ICON_INFORMATION, None)
        else:
            wx.MessageBox(_('An error was found in the search for '
                            'the web page.\nSorry for this inconvenience.'),
                          "Videomass: Warning", wx.ICON_EXCLAMATION, None)
            return
    # -------------------------------------------------------------------#

    def Info(self, event):
        """
        Display the program informations and developpers
        """
        infoprg.info(self, self.videomass_icon)

    # -----------------  BUILD THE TOOL BAR  --------------------###

    def videomass_tool_bar(self):
        """
        Makes and attaches the view toolsBtn bar
        """
        # -------- Properties
        self.toolbar = self.CreateToolBar(style=(wx.TB_FLAT |
                                                 wx.TB_TEXT))
        self.toolbar.SetToolBitmapSize((32, 32))
        self.toolbar.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        # ------- Run process button
        self.toolbar.AddStretchableSpace()
        #self.toolbar.AddSeparator()
        back = self.toolbar.AddTool(wx.ID_FILE3, _('Back'),
                                    wx.Bitmap(self.icon_mainback))
        #self.toolbar.AddSeparator()
        forward = self.toolbar.AddTool(wx.ID_FILE4, _('Forward'),
                                       wx.Bitmap(self.icon_mainforward))
        #self.toolbar.AddSeparator()
        self.run_coding = self.toolbar.AddTool(wx.ID_FILE5, _('Convert'),
                                          wx.Bitmap(self.icon_runconversion))
        self.run_download = self.toolbar.AddTool(wx.ID_FILE6, _('Download'),
                                          wx.Bitmap(self.icon_ydl))
        #self.toolbar.AddSeparator()
        self.toolbar.AddStretchableSpace()

        # finally, create it
        self.toolbar.Realize()

        # ----------------- Tool Bar Binding (evt)-----------------------#
        self.Bind(wx.EVT_TOOL, self.Run_Coding, self.run_coding)
        self.Bind(wx.EVT_TOOL, self.Run_Coding, self.run_download)
        self.Bind(wx.EVT_TOOL, self.on_Back, back)
        self.Bind(wx.EVT_TOOL, self.on_Forward, forward)

    # --------------- Tool Bar Callback (event handler) -----------------#

    def on_Back(self, event):
        """
        Show URLs import panel.
        """
        if self.textDnDTarget.IsShown() or self.fileDnDTarget.IsShown():
            self.choosetopicRetrieve()
        elif self.topicname in ('Audio/Video Conversions', 'Presets Manager'):
            self.File_import(self, self.topicname)
        elif self.topicname == 'Youtube Downloader':
            self.Text_import(self, self.topicname)
    # ------------------------------------------------------------------#

    def on_Forward(self, event):
        """
        redirect on corresponding panel
        """
        if self.topicname in ['Audio/Video Conversions', 'Presets Manager']:
            data = self.fileDnDTarget.on_Redirect()
            if not data:
                wx.MessageBox(_('Drag at least one file'), "Videomass",
                              wx.ICON_INFORMATION, self)
                return

            self.data_files = data
            if self.topicname == 'Audio/Video Conversions':
                self.switch_av_conversions(self)
            else:
                self.switch_presets_manager(self)

        elif self.topicname == 'Youtube Downloader':
            data = self.textDnDTarget.topic_Redirect()
            if not data:
                wx.MessageBox(_('Append at least one URL'), "Videomass",
                              wx.ICON_INFORMATION, self)
                return
            self.youtube_Downloader(self, data)
    # ------------------------------------------------------------------#

    def File_import(self, event, which):
        """
        Show files import panel.

        """
        self.topicname = which
        self.textDnDTarget.Hide(), self.ytDownloader.Hide()
        self.VconvPanel.Hide(), self.ChooseTopic.Hide()
        self.PrstsPanel.Hide(), self.fileDnDTarget.Show()
        if self.file_destin:
            self.fileDnDTarget.text_path_save.SetValue("")
            self.fileDnDTarget.text_path_save.AppendText(self.file_destin)
        self.menu_items()  # disable some menu items
        self.avpan.Enable(True), self.prstpan.Enable(True),
        self.ydlpan.Enable(True), self.startpan.Enable(True)
        self.toolbar.Show(), self.btnpanel.Hide()
        self.logpan.Enable(False)
        self.toolbar.EnableTool(wx.ID_FILE4, True)
        self.toolbar.EnableTool(wx.ID_FILE5, False)
        self.toolbar.EnableTool(wx.ID_FILE6, False)
        self.Layout()
        self.statusbar_msg(_('Add Files'), None)
    # ------------------------------------------------------------------#

    def Text_import(self, event, which):
        """
        Show URLs import panel.
        """
        self.topicname = which
        self.fileDnDTarget.Hide(), self.ytDownloader.Hide()
        self.VconvPanel.Hide(), self.ChooseTopic.Hide()
        self.PrstsPanel.Hide(), self.textDnDTarget.Show()
        if self.file_destin:
            self.textDnDTarget.text_path_save.SetValue("")
            self.textDnDTarget.text_path_save.AppendText(self.file_destin)
        self.menu_items()  # disable some menu items
        self.avpan.Enable(True), self.prstpan.Enable(True),
        self.ydlpan.Enable(True), self.startpan.Enable(True)
        self.toolbar.Show(), self.btnpanel.Hide()
        self.logpan.Enable(False)
        self.toolbar.EnableTool(wx.ID_FILE4, True)
        self.toolbar.EnableTool(wx.ID_FILE5, False)
        self.toolbar.EnableTool(wx.ID_FILE6, False)
        self.Layout()
        self.statusbar_msg(_('Add URLs'), None)
    # ------------------------------------------------------------------#

    def youtube_Downloader(self, event, data):
        """
        Show youtube-dl downloader panel
        """
        if not data == self.data_url:
            self.ytDownloader.fcode.DeleteAllItems()
            self.ytDownloader.choice.SetSelection(0)
            self.ytDownloader.on_Choice(self)
            self.ytDownloader.info, self.ytDownloader.error = [], False
            if self.data_url:
                self.statusbar_msg(_('Warning: the previous settings may be '
                                    'reset to default values.'), ORANGE)
            else:
                self.statusbar_msg(_('Youtube Downloader'), None)
        self.data_url = data
        self.file_destin = self.textDnDTarget.file_dest
        self.fileDnDTarget.Hide(), self.textDnDTarget.Hide()
        self.VconvPanel.Hide(), self.PrstsPanel.Hide()
        self.ytDownloader.Show()
        self.toolbar.Show(), self.btnpanel.Show(), self.btn_playO.Show()
        self.btn_saveprf.Hide(), self.btn_duration.Hide()
        self.btn_metaI.Show(), self.btn_newprf.Hide()
        self.btn_metaI.SetLabel(_('Show More'))
        self.btn_delprf.Hide(), self.btn_editprf.Hide()
        self.menu_items()  # disable some menu items
        self.avpan.Enable(True), self.prstpan.Enable(True)
        self.ydlpan.Enable(False), self.startpan.Enable(True)
        self.logpan.Enable(True)
        self.toolbar.EnableTool(wx.ID_FILE4, False)
        self.toolbar.EnableTool(wx.ID_FILE5, False)
        self.toolbar.EnableTool(wx.ID_FILE6, True)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_av_conversions(self, event):
        """
        Show Video converter panel
        """
        self.file_destin = self.fileDnDTarget.file_dest
        self.fileDnDTarget.Hide(), self.textDnDTarget.Hide()
        self.ytDownloader.Hide(), self.PrstsPanel.Hide()
        self.VconvPanel.Show()
        self.statusbar_msg(_('Audio/Video Conversions'), None)
        filenames = [f['format']['filename'] for f in
                     self.data_files if f['format']['filename']
                     ]
        if not filenames == self.file_src:
            if self.file_src:
                self.statusbar_msg(_('Warning: the previous settings may be '
                                    'reset to default values.'), ORANGE)
            self.file_src = filenames
            self.duration = [f['format']['duration'] for f in
                             self.data_files if f['format']['duration']
                             ]
            self.VconvPanel.normalize_default()
            self.PrstsPanel.normalization_default()
        self.toolbar.Show(), self.btnpanel.Show()
        self.btn_newprf.Hide(), self.btn_delprf.Hide()
        self.btn_editprf.Hide(), self.btn_saveprf.Show()
        self.btn_duration.Show(), self.btn_metaI.Show()
        self.btn_metaI.SetLabel(_('Streams'))
        self.btn_playO.Show()
        self.menu_items()  # disable some menu items
        self.avpan.Enable(False), self.prstpan.Enable(True)
        self.ydlpan.Enable(True), self.startpan.Enable(True)
        self.logpan.Enable(True)
        self.toolbar.EnableTool(wx.ID_FILE4, False)
        self.toolbar.EnableTool(wx.ID_FILE5, True)
        self.toolbar.EnableTool(wx.ID_FILE6, False)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_presets_manager(self, event):
        """
        Show presets manager panel

        """
        self.file_destin = self.fileDnDTarget.file_dest
        self.fileDnDTarget.Hide(), self.textDnDTarget.Hide(),
        self.ytDownloader.Hide(), self.VconvPanel.Hide(),
        self.PrstsPanel.Show()
        self.statusbar_msg(_('Presets Manager'), None)
        filenames = [f['format']['filename'] for f in
                     self.data_files if f['format']['filename']
                     ]
        if not filenames == self.file_src:
            if self.file_src:
                self.statusbar_msg(_('Warning: the previous settings may be '
                                    'reset to default values.'), ORANGE)
            self.file_src = filenames
            self.duration = [f['format']['duration'] for f in
                             self.data_files if f['format']['duration']
                             ]
            self.PrstsPanel.normalization_default()
            self.VconvPanel.normalize_default()
        self.toolbar.Show(), self.btnpanel.Show()
        self.btn_newprf.Show(), self.btn_delprf.Show(), self.btn_editprf.Show()
        self.btn_saveprf.Hide(), self.btn_duration.Show()
        self.btn_metaI.Show(), self.btn_metaI.SetLabel(_('Multimedia Streams'))
        self.btn_playO.Show(), self.saveme.Enable(True)
        self.new_prst.Enable(True), self.del_prst.Enable(True)
        self.restore.Enable(True), self.default.Enable(True),
        self.default_all.Enable(True), self.refresh.Enable(True)
        self.avpan.Enable(True), self.prstpan.Enable(False),
        self.ydlpan.Enable(True), self.startpan.Enable(True)
        self.logpan.Enable(True)
        self.toolbar.EnableTool(wx.ID_FILE4, False)
        self.toolbar.EnableTool(wx.ID_FILE5, True)
        self.toolbar.EnableTool(wx.ID_FILE6, False)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_Process(self, *varargs):
        """
    1) TIME DEFINITION FOR THE PROGRESS BAR
        For a suitable and efficient progress bar, if a specific
        time sequence has been set with the duration tool, the total
        duration of each media file will be replaced with the set time
        sequence. Otherwise the duration of each media will be the one
        originated from its real duration.

    2) STARTING THE PROCESS
        Here the panel with the progress bar is instantiated which will
        assign a corresponding thread.

        """
        if self.time_seq:
            newDuration = []
            for n in self.duration:
                newDuration.append(self.time_read['time'][1])
            duration = newDuration
        else:
            duration = self.duration

        self.btnpanel.Hide()  # hide buttons bar
        # Hide all others panels:
        self.fileDnDTarget.Hide(), self.textDnDTarget.Hide(),
        self.ytDownloader.Hide(), self.VconvPanel.Hide(),
        self.PrstsPanel.Hide(),
        # Show the panel:
        self.ProcessPanel.Show()
        self.SetTitle(_('Processing Status - Videomass'))
        [self.menuBar.EnableTop(x, False) for x in range(0, 4)]
        # Hide the tool bar
        self.toolbar.Hide()
        self.ProcessPanel.topic_thread(self.topicname, varargs, duration)
        self.Layout()
    # ------------------------------------------------------------------#

    def Run_Coding(self, event):
        """
        By clicking the Start encoding button on the main frame, calls
        the on_ok method of the corresponding panel shown, which calls
        the 'switch_Process' method above.
        """
        if self.ytDownloader.IsShown():
            self.ytDownloader.on_Start()
        elif self.VconvPanel.IsShown():
            self.file_src = [f['format']['filename'] for f in
                             self.data_files if f['format']['filename']
                             ]
            self.VconvPanel.on_start()
        elif self.PrstsPanel.IsShown():
            self.file_src = [f['format']['filename'] for f in
                             self.data_files if f['format']['filename']
                             ]
            self.PrstsPanel.on_Start()
    # ------------------------------------------------------------------#

    def panelShown(self, panelshown):
        """
        When clicking 'close button' of the long_processing_task panel
        (see switch_Process method above), Retrieval at previous
        panel showing and re-enables the functions provided by
        the menu bar.
        """
        if panelshown == 'Audio/Video Conversions':
            self.ProcessPanel.Hide()
            self.switch_av_conversions(self)
            self.btnpanel.Show()
        elif panelshown == 'Youtube Downloader':
            self.ProcessPanel.Hide()
            self.youtube_Downloader(self, self.data_url)
        elif panelshown == 'Presets Manager':
            self.ProcessPanel.Hide()
            self.switch_presets_manager(self)
            self.btnpanel.Show()
        # Enable all top menu bar:
        [self.menuBar.EnableTop(x, True) for x in range(0, 4)]
        self.SetTitle("Videomass")  # set the appropriate title
        # show buttons bar if the user has shown it:
        self.Layout()
