# -*- coding: UTF-8 -*-
"""
Name: sequence_to_video.py
Porpose: A slideshow maker based on FFmpeg
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Apr.07.2022
Code checker:
    flake8: --ignore F821, W504
    pylint: --ignore E0602, E1101
########################################################

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
import os
import sys
import wx
import wx.lib.agw.hyperlink as hpl
import wx.lib.scrolledpanel as scrolled
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_dialogs.epilogue import Formula
from videomass.vdms_dialogs.filter_scale import Scale
from videomass.vdms_threads.ffprobe import ffprobe
from videomass.vdms_utils.utils import make_newdir_with_id
from videomass.vdms_utils.utils import get_seconds as getsec
from videomass.vdms_utils.utils import get_milliseconds as getms
from videomass.vdms_utils.utils import milliseconds2clock as clockms


def check_images_size(flist):
    """
    Check for images size, if not equal return True,
    None otherwise.
    """
    sizes = []
    for index in flist:
        if 'video' in index.get('streams')[0]['codec_type']:
            width = index['streams'][0]['width']
            height = index['streams'][0]['height']
            sizes.append(f'{width}x{height}')

    if len(set(sizes)) > 1:
        wx.MessageBox(_('Images need to be resized, '
                        'please use Resizing function.'),
                      'Videomass', wx.ICON_INFORMATION)
        return True

    return None
# -------------------------------------------------------------------------


class SequenceToVideo(wx.Panel):
    """
    This is an new implementation class to create
    Slideshow and static videos with the ability to
    add an audio track, resizing, and more.

    """
    VIOLET = '#D64E93'
    MSG_1 = _("\n1. Import one or more image files such as JPG, PNG and BMP "
              "formats, then select one."
              "\n\n2. Use the Resizing function to resize images which "
              "have different sizes such as width and height. "
              "It is optional in other cases."
              "\n\n3. Use the Timeline editor (CTRL+T) to set the time "
              "interval between images by scrolling the DURATION slider."
              "\n\n4. Start the conversion."
              "\n\n\nThe produced video will have the name of the selected "
              "file in the 'Queued File' list, which will be saved in a "
              "folder named 'Still-Images'\nwith a progressive digit, "
              "in the path you specify.")
    # ----------------------------------------------------------------#

    def __init__(self, parent, icons):
        """
        Simple GUI panel with few controls to create slideshows
        based on ffmpeg syntax.
        .
        """
        get = wx.GetApp()
        appdata = get.appset
        self.ffprobe_cmd = appdata['ffprobe_cmd']
        self.parent = parent  # parent is the MainFrame
        self.opt = {"Scale": "", "Setdar": "", "Setsar": "",
                    "RESIZE": "", "ADuration": 0, "AudioMerging": "",
                    "Map": "-map 0:v?", "Shortest": ["", "Disabled"],
                    "Interval": "", "Clock": "00:00:00:000",
                    "Preinput": "1/0", "Fps": ["fps=10,", "10"],
                    }
        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up
            bmpresize = get_bmp(icons['scale'], ((16, 16)))
            bmpatrack = get_bmp(icons['atrack'], ((16, 16)))
        else:
            bmpresize = wx.Bitmap(icons['scale'], wx.BITMAP_TYPE_ANY)
            bmpatrack = wx.Bitmap(icons['atrack'], wx.BITMAP_TYPE_ANY)

        wx.Panel.__init__(self, parent=parent, style=wx.BORDER_THEME)
        sizer = wx.BoxSizer(wx.VERTICAL)

        panelscroll = scrolled.ScrolledPanel(self, -1, size=(-1, 200),
                                             style=wx.TAB_TRAVERSAL
                                             | wx.BORDER_THEME,
                                             name="panelscr",
                                             )
        fgs1 = wx.BoxSizer(wx.VERTICAL)
        lbl_help = wx.StaticText(panelscroll, wx.ID_ANY,
                                 label=SequenceToVideo.MSG_1)
        fgs1.Add(lbl_help, 0, wx.ALL | wx.EXPAND, 5)

        sizer.Add(panelscroll, 0, wx.ALL | wx.EXPAND, 0)

        panelscroll.SetSizer(fgs1)
        panelscroll.SetAutoLayout(1)
        panelscroll.SetupScrolling()

        sizer_link1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer_link1)
        lbl_link = wx.StaticText(self, wx.ID_ANY,
                                 label=_("For more information, "
                                         "visit the official FFmpeg "
                                         "documentation:")
                                 )
        link1 = hpl.HyperLinkCtrl(self, -1, ("FFmpeg Slideshow wiki"),
                                  URL="https://trac.ffmpeg.org/wiki/Slideshow"
                                  )
        sizer_link1.Add(lbl_link, 0, wx.ALL | wx.EXPAND, 5)
        sizer_link1.Add(link1)
        line1 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizer.Add(line1, 0, wx.ALL | wx.EXPAND, 5)
        # sizer.Add((5, 5))
        boxctrl = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY), wx.VERTICAL)
        sizer.Add(boxctrl, 0, wx.ALL | wx.EXPAND, 5)
        sizFormat = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(sizFormat)

        self.ckbx_static_img = wx.CheckBox(self, wx.ID_ANY,
                                           _('Enable a single still image'))
        boxctrl.Add(self.ckbx_static_img, 0, wx.ALL | wx.EXPAND, 5)
        siz_pict = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(siz_pict)
        lbl_fps = wx.StaticText(self, wx.ID_ANY, label="FPS:")
        siz_pict.Add(lbl_fps, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_fps = wx.ComboBox(self, wx.ID_ANY,
                                   choices=[("None"),
                                            ("ntsc"),
                                            ("pal"),
                                            ("film"),
                                            ("23.976"),
                                            ("24"),
                                            ("25"),
                                            ("29.97"),
                                            ("30"),
                                            ("5"),
                                            ("10"),
                                            ("15"),
                                            ("60")
                                            ],
                                   size=(160, -1),
                                   style=wx.CB_DROPDOWN | wx.CB_READONLY
                                   )
        siz_pict.Add(self.cmb_fps, 0, wx.ALL, 5)
        self.cmb_fps.SetSelection(10)
        self.btn_resize = wx.Button(self, wx.ID_ANY, _("Resizing"),
                                    size=(-1, -1)
                                    )
        self.btn_resize.SetBitmap(bmpresize, wx.LEFT)
        siz_pict.Add(self.btn_resize, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        siz_audio = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(siz_audio)
        self.ckbx_audio = wx.CheckBox(self, wx.ID_ANY, _('Include audio file'))
        siz_audio.Add(self.ckbx_audio, 0, wx.ALL | wx.EXPAND, 5)
        self.ckbx_shortest = wx.CheckBox(self, wx.ID_ANY,
                                         _('Play the video until '
                                           'audio file ends'
                                           ))
        siz_audio.Add(self.ckbx_shortest, 0, wx.ALL | wx.EXPAND, 5)
        self.ckbx_shortest.Disable()
        siz_afile = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(siz_afile)
        self.btn_openaudio = wx.Button(self, wx.ID_ANY, _("Open audio file"),
                                       size=(-1, -1)
                                       )
        self.btn_openaudio.SetBitmap(bmpatrack, wx.LEFT)
        siz_afile.Add(self.btn_openaudio, 0, wx.ALL
                      | wx.ALIGN_CENTER_VERTICAL, 5)
        self.btn_openaudio.Disable()

        self.txt_apath = wx.TextCtrl(self, wx.ID_ANY, size=(500, -1),
                                     style=wx.TE_READONLY
                                     )
        siz_afile.Add(self.txt_apath, 0, wx.ALL, 5)
        self.txt_apath.Disable()

        siz_addparams = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(siz_addparams, 0, wx.EXPAND, 0)

        self.ckbx_edit = wx.CheckBox(self, wx.ID_ANY,
                                     _('Additional arguments'))
        siz_addparams.Add(self.ckbx_edit, 0, wx.ALL, 5)
        self.txt_addparams = wx.TextCtrl(self, wx.ID_ANY,
                                         value=('-c:v libx264 -crf 23 '
                                                '-tune:v stillimage'),
                                         size=(-1, -1),)
        siz_addparams.Add(self.txt_addparams, 1, wx.ALL | wx.EXPAND, 5)
        self.txt_addparams.Disable()

        self.SetSizer(sizer)

        if appdata['ostype'] == 'Darwin':
            lbl_help.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
            lbl_link.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            lbl_help.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
            lbl_link.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.Bind(wx.EVT_CHECKBOX, self.on_enable_audio, self.ckbx_audio)
        self.Bind(wx.EVT_BUTTON, self.on_addaudio_track, self.btn_openaudio)
        self.Bind(wx.EVT_CHECKBOX, self.on_shortest, self.ckbx_shortest)
        self.Bind(wx.EVT_CHECKBOX, self.on_addparams, self.ckbx_edit)
        self.Bind(wx.EVT_COMBOBOX, self.on_fps, self.cmb_fps)
        self.Bind(wx.EVT_BUTTON, self.on_resizing, self.btn_resize)
    # ---------------------------------------------------------

    def reset_all_values(self):
        """
        Reset all control and dictionary values
        NOTE this method is not used for now
        """
        self.opt["Scale"], self.opt["Setdar"] = "", ""
        self.opt["Setsar"], self.opt["RESIZE"] = "", ""
        self.opt["Preinput"] = "1/0"
        self.opt["Shortest"] = ["", "Disabled"]
        self.opt["Interval"] = ""
        self.opt["Clock"] = "00:00:00.000"
        self.ckbx_static_img.SetValue(False)
        self.btn_resize.SetBackgroundColour(wx.NullColour)
        self.ckbx_audio.SetValue(False)
        self.on_enable_audio(self)
        self.ckbx_shortest.SetValue(False)
    # ---------------------------------------------------------

    def on_addparams(self, event):
        """
        Enable additional args to command line
        """
        if self.ckbx_edit.IsChecked():
            self.txt_addparams.Enable()
        else:
            self.txt_addparams.Disable()
    # ---------------------------------------------------------

    def file_selection(self):
        """
        Gets the selected file on queued files and returns an object
        of type list [str('selected file name'), int(index)].
        Returns None if no files are selected.

        """
        if len(self.parent.file_src) == 1:
            return (self.parent.file_src[0], 0)

        if not self.parent.filedropselected:
            wx.MessageBox(_("A target file must be selected in the "
                            "queued files"),
                          'Videomass', wx.ICON_INFORMATION, self)
            return None

        clicked = self.parent.filedropselected
        return (clicked, self.parent.file_src.index(clicked))
    # ------------------------------------------------------------------#

    def get_video_stream(self):
        """
        Given a frame or a video file, it returns a tuple of data
        containing information on the streams required by some video
        filters.

        """
        fget = self.file_selection()
        if not fget:
            return None

        index = self.parent.data_files[fget[1]]

        if 'video' in index.get('streams')[0]['codec_type']:
            width = int(index['streams'][0]['width'])
            height = int(index['streams'][0]['height'])
            return (width, height)

        wx.MessageBox(_('The file is not a frame or a video file'),
                      'Videomass', wx.ICON_INFORMATION)
        self.on_FiltersClear(self)
        return None
    # ------------------------------------------------------------------#

    def on_resizing(self, event):
        """
        Enable or disable scale, setdar and setsar filters
        """
        sdf = self.get_video_stream()
        if not sdf:
            return
        with Scale(self,
                   self.opt["Scale"],
                   self.opt["Setdar"],
                   self.opt["Setsar"],
                   sdf[0],  # width
                   sdf[1],  # height
                   ) as sizing:

            if sizing.ShowModal() == wx.ID_OK:
                data = sizing.getvalue()
                if not [x for x in data.values() if x]:
                    self.btn_resize.SetBackgroundColour(wx.NullColour)
                    self.opt["Setdar"] = ""
                    self.opt["Setsar"] = ""
                    self.opt["Scale"] = ""
                    self.opt["RESIZE"] = ''
                else:
                    self.btn_resize.SetBackgroundColour(
                        wx.Colour(SequenceToVideo.VIOLET))
                    self.opt["Scale"] = data['scale']
                    self.opt['Setdar'] = data['setdar']
                    self.opt['Setsar'] = data['setsar']

                    flt = ''.join([f'{x},' for x in data.values() if x])[:-1]
                    if flt:
                        self.opt["RESIZE"] = f'-vf {flt}'
    # ---------------------------------------------------------

    def on_fps(self, event):
        """
        Set frame per seconds using ComboBox
        """
        val = self.cmb_fps.GetValue()
        if val == 'None':
            self.opt["Fps"] = ['', 'None']
        else:
            self.opt["Fps"] = [f'fps={val},', val]
    # ---------------------------------------------------------

    def on_shortest(self, event):
        """
        Enable or disable shortest when audio file is loaded.
        Always disabled otherwise.
        """
        if self.ckbx_shortest.IsChecked():
            self.opt["Shortest"] = ["", "Disabled"]
        else:
            self.opt["Shortest"] = ["-shortest", "Enabled"]
    # ---------------------------------------------------------

    def on_enable_audio(self, event):
        """
        Enables controls to create a video file from a
        sequence of images using Concat Demuxer.
        """
        if self.ckbx_audio.IsChecked():
            self.btn_openaudio.Enable()
            self.txt_apath.Enable()
            self.ckbx_shortest.Enable()
            self.opt["Shortest"] = ["-shortest", "Enabled"]
        else:
            self.btn_openaudio.Disable()
            self.txt_apath.Disable()
            self.txt_apath.Clear()
            self.ckbx_shortest.Disable()
            self.ckbx_shortest.SetValue(False)
            self.btn_openaudio.SetBackgroundColour(wx.NullColour)
            self.btn_openaudio.SetLabel(_("Open audio file"))
            self.opt["AudioMerging"] = ''
            self.opt["Map"] = '-map 0:v?'
            self.opt["ADuration"] = 0
            self.opt["Shortest"] = ["", "Disabled"]
    # ---------------------------------------------------------

    def on_addaudio_track(self, event):
        """
        Add audio track to video.
        """
        fmt = '*.wav;*.aiff;*.flac;*.oga;*.ogg;*.m4a;*.aac;*.ac3;*.mp3;'

        with wx.FileDialog(self, _("Open an audio file"),
                           wildcard=f"Audio source ({fmt})|{fmt}",
                           style=wx.FD_OPEN |
                           wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()

        self.btn_openaudio.SetBackgroundColour(
                        wx.Colour(SequenceToVideo.VIOLET))
        ext = os.path.splitext(pathname)[1].replace('.', '').upper()
        self.btn_openaudio.SetLabel(ext)
        self.txt_apath.write(pathname)

        self.opt["AudioMerging"] = f'-i "{pathname}"'
        self.opt["Map"] = '-map 0:v:0 -map 1:a:0'
        probe = ffprobe(pathname, self.ffprobe_cmd, hide_banner=None)
        ms = float(probe[0]['format']['duration']) * 1000
        self.opt["ADuration"] = round(ms)
    # ---------------------------------------------------------

    def build_command_slideshow(self, timeline):
        """
        Set ffmpeg arguments for a slideshow.
        """
        loop = ''
        if self.ckbx_audio.IsChecked():
            if self.opt["Shortest"][0]:
                duration = getms(timeline) * len(self.parent.file_src)
                self.opt["Clock"] = clockms(duration)
                sec = round(getsec(timeline))
            else:
                self.opt["Clock"] = clockms(self.opt["ADuration"])
                #sec = round(getsec(self.parent.time_seq.split()[3]))
                sec = round(getsec(timeline))
                duration = self.opt["ADuration"]
                loop = f'-loop 1 -t {self.opt["Clock"]}'

        else:
            duration = getms(timeline) * len(self.parent.file_src)
            self.opt["Clock"] = clockms(duration)
            sec = round(getsec(timeline))

        framerate = '-framerate 1/1' if not sec else f'-framerate 1/{sec}'
        self.opt["Preinput"] = f'{loop} {framerate}'
        self.opt["Interval"] = sec

        if self.txt_addparams.IsEnabled():
            addparam = self.txt_addparams.GetValue()
        else:
            addparam = ''

        cmd_2 = (f'{self.opt["AudioMerging"]} {addparam} -vf '
                 f'"{self.opt["Fps"][0]}format=yuv420p" {self.opt["Map"]} '
                 f'{self.opt["Shortest"][0]}')

        return cmd_2, duration
    # ---------------------------------------------------------

    def build_command_loop_image(self, timeline):
        """
        Set ffmpeg arguments for a static video,
        the checkbox `create a static video from image` is checked.

        """
        if self.ckbx_audio.IsChecked():
            if self.opt["Shortest"][0]:
                duration = getms(timeline)
                self.opt["Clock"] = timeline
                sec = round(getsec(timeline))
            else:
                self.opt["Clock"] = clockms(self.opt["ADuration"])
                duration = self.opt["ADuration"]
                sec = round(self.opt["ADuration"] / 1000)
        else:
            duration = getms(timeline)
            self.opt["Clock"] = timeline
            sec = round(duration / 1000)

        self.opt["Preinput"] = f'-loop 1 -t {self.opt["Clock"]}'
        self.opt["Interval"] = sec

        if self.txt_addparams.IsEnabled():
            addparam = self.txt_addparams.GetValue()
        else:
            addparam = ''

        cmd_2 = (f'{self.opt["AudioMerging"]} {addparam} -vf '
                 f'"{self.opt["Fps"][0]}format=yuv420p" {self.opt["Map"]} '
                 f'{self.opt["Shortest"][0]}')

        return cmd_2, duration
    # ---------------------------------------------------------

    def check_to_slide(self, fsource):
        """
        Check compatibility between loaded images and files exist.
        """
        itemcount = self.parent.fileDnDTarget.flCtrl.GetItemCount()
        for x in range(itemcount):
            typemedia = self.parent.fileDnDTarget.flCtrl.GetItemText(x, 3)
            if 'video' not in typemedia or 'sequence' not in typemedia:
                wx.MessageBox(_("Invalid file: '{}'").format(fsource[x]),
                              _('ERROR'), wx.ICON_ERROR, self)
                return True

        unsupp = [f for f in fsource if os.path.splitext(f)[1]
                  not in ('.jpeg', '.jpg', '.png', '.bmp',
                          '.JPEG', '.JPG', '.PNG', '.BMP')
                  ]
        if unsupp:
            ext = os.path.splitext(unsupp[0])[1]
            wx.MessageBox(_("Unsupported format '{}'").format(ext),
                          _('ERROR'), wx.ICON_ERROR, self)
            return True

        for fn in fsource:
            if not os.path.isfile(os.path.abspath(fn)):
                wx.MessageBox(_('File does not exist:\n\n"{}"\n').format(fn),
                              "Videomass", wx.ICON_ERROR, self)
                return True
        return None
    # ---------------------------------------------------------

    def check_to_loop(self, typemedia, clicked):
        """
        Check the compatibility of the selected image and file exist.
        """
        if 'video' not in typemedia or 'sequence' not in typemedia:
            wx.MessageBox(_("Invalid file: '{}'").format(clicked),
                          _('ERROR'), wx.ICON_ERROR, self)
            return True

        supp = ('.jpeg', '.jpg', '.png', '.bmp',
                '.JPEG', '.JPG', '.PNG', '.BMP')
        ext = os.path.splitext(clicked)[1]
        if ext not in supp:
            wx.MessageBox(_("Unsupported format '{}'").format(ext),
                          _('ERROR'), wx.ICON_ERROR, self)
            return True

        if not os.path.isfile(os.path.abspath(clicked)):
            wx.MessageBox(_('File does not exist:'
                            '\n\n"{}"\n').format(clicked),
                          "Videomass", wx.ICON_ERROR, self)
            return True
        return None
    # ---------------------------------------------------------

    def get_args_line(self):
        """
        get arguments line for 'loop' or 'slide' modes
        """
        if self.parent.time_seq.split()[3] == '00:00:00.000':
            timeline = '00:00:01.000'
        else:
            timeline = self.parent.time_seq.split()[3]

        if self.ckbx_static_img.IsChecked():
            args = self.build_command_loop_image(timeline)
        else:
            args = self.build_command_slideshow(timeline)

        return args
    # ---------------------------------------------------------

    def on_start(self):
        """
        Redirect to `switch_to_processing`
        """
        fget = self.file_selection()
        if not fget:
            return

        fsource = self.parent.file_src

        if self.parent.same_destin is True:
            destdir = os.path.dirname(fget[0])
        else:
            destdir = self.parent.outpath_ffmpeg

        basename = os.path.basename(fget[0].rsplit('.')[0])
        outputdir = make_newdir_with_id(destdir, 'Still-Images_1')
        destdir = os.path.join(outputdir, f"{basename}.mkv")

        if self.ckbx_static_img.IsChecked():
            countmax = 1
            files = (fget[0],)
            prop = self.parent.fileDnDTarget.flCtrl.GetItemText(fget[1], 3)
            if self.check_to_loop(prop, fget[0]) is True:
                return
        else:
            files = fsource
            countmax = len(files)
            if self.check_to_slide(files) is True:
                return
            if not self.opt["RESIZE"] and countmax != 1:
                if check_images_size(self.parent.data_files):
                    return

        args = self.get_args_line()  # get args for command line

        valupdate = self.update_dict(f"{basename}.mkv",
                                     outputdir,
                                     countmax,
                                     'mkv',
                                     )
        ending = Formula(self, valupdate[0], valupdate[1], _('Starts'))

        if ending.ShowModal() == wx.ID_OK:
            self.parent.switch_to_processing('sequence_to_video',  # topic
                                             files,  # file list
                                             outputdir,
                                             destdir,
                                             (self.opt["RESIZE"], args[0]),
                                             self.opt["Preinput"],
                                             args[1],  # duration
                                             None,
                                             'still_image_maker.log',
                                             countmax,
                                             skiptimeline=True
                                             )
    # -----------------------------------------------------------

    def update_dict(self, newfile, destdir, count, ext):
        """
        Update information before send to epilogue

        """
        time = self.opt["Clock"]
        resize = _('Enabled') if self.opt["RESIZE"] else _('Disabled')
        short = _(self.opt["Shortest"][1])
        preinput = self.opt["Preinput"]
        duration = self.opt["Interval"]
        if self.ckbx_edit.IsChecked():
            addargs = self.txt_addparams.GetValue()
        else:
            addargs = ''

        formula = (_(f"SUMMARY\n\nFile to process\nOutput filename\
                      \nDestination\nOutput Format\nAttional arguments\
                      \nAudio file\nShortest\nResize\nPre-input\
                      \nFrame per Second (FPS)\nStill image duration\
                      \nOverall video duration")
                   )
        dictions = (f'\n\n{count}\n{newfile}\n{destdir}\n{ext}\n{addargs}'
                    f'\n{self.txt_apath.GetValue()}\n{short}'
                    f'\n{resize}\n{preinput}\n{self.opt["Fps"][1]}'
                    f'\n{duration} Seconds\n{time}'
                    )
        return formula, dictions
