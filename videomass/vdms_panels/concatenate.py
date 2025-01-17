# -*- coding: UTF-8 -*-
"""
Name: concatenate.py
Porpose: A simple concat demuxer UI
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.21.2024
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
import os
import wx
import wx.lib.agw.hyperlink as hpl
from videomass.vdms_dialogs.widget_utils import NormalTransientPopup
from videomass.vdms_io.checkup import check_files
from videomass.vdms_dialogs.epilogue import Formula


def compare_media_param(data):
    """
    This function expects json data from FFprobe to checks
    that the indexed streams of each item in the list have
    the same codec, video size and audio sample rate in order
    to ensure correct file concatenation.
    Returns an error message if any error found,
    Returns None otherwise.
    """
    if len(data) == 1:
        return _('At least two files are required to perform concatenation.')
    com = {}

    for streams in data:
        name = streams.get('format').get('filename')
        com[name] = {}
        for items in streams.get('streams'):
            if items.get('codec_type') == 'video':
                com[name][items.get('index')] = [items.get('codec_name')]
                size = f"{items.get('width')}x{items.get('height')}"
                com[name][items.get('index')].append(size)
            if items.get('codec_type') == 'audio':
                com[name][items.get('index')] = [items.get('codec_name')]
                com[name][items.get('index')].append(items.get('sample_rate'))

    if not com:
        return _('Invalid data found')

    totest = list(com.values())[0]
    if not all(val == totest for val in com.values()):
        return _('The files do not have the same "codec_types", '
                 'same "sample_rate" or same "width" or "height". '
                 'Unable to proceed.')
    return None
# -------------------------------------------------------------------------


class Conc_Demuxer(wx.Panel):
    """
    A simple concat demuxer UI to set media files
    concatenation using concat demuxer,
    see <https://ffmpeg.org/ffmpeg-formats.html#concat>

    """
    LGREEN = '#52ee7d'
    BLACK = '#1f1f1f'
    MSG_1 = _("\n- The concatenation function is performed only with "
              "Audio files or only with Video files."
              "\n\n- The order of concatenation depends on the order in "
              "which the files were added."
              "\n\n- The output file name will have the same name as the "
              "first file added (also depends on the\n"
              "  settings made in the preferences dialog or the renaming "
              "functions used)."
              "\n\n- Video files must have exactly same streams, same "
              "codecs and same\n  width/height, but can be wrapped in "
              "different container formats."
              "\n\n- Audio files must have exactly the same formats, "
              "same codecs with equal sample rate.")

    # ----------------------------------------------------------------#

    def __init__(self, parent):
        """
        This is a panel impemented on MainFrame
        """
        get = wx.GetApp()
        appdata = get.appset
        self.cachedir = appdata['cachedir']
        self.parent = parent  # parent is the MainFrame
        self.args = ''
        self.duration = None

        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((20, 20))
        self.btn_help = wx.Button(self, wx.ID_ANY, _("Read me"), size=(-1, -1))
        self.btn_help.SetBackgroundColour(wx.Colour(Conc_Demuxer.LGREEN))
        self.btn_help.SetForegroundColour(wx.Colour(Conc_Demuxer.BLACK))
        sizer.Add(self.btn_help, 0, wx.ALL, 5)

        sizer.Add((20, 20))
        boxctrl = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY), wx.VERTICAL)
        sizer.Add(boxctrl, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add((20, 20))
        sizer_link2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer_link2)
        self.lbl_msg3 = wx.StaticText(self, wx.ID_ANY,
                                      label=_("For more details, see the "
                                              "Videomass User Guide:")
                                      )
        if appdata['GETLANG'] in appdata['SUPP_LANGs']:
            lang = appdata['GETLANG'].split('_')[0]
            page = (f"https://jeanslack.github.io/Videomass/"
                    f"Pages/User-guide-languages/{lang}/1-User_"
                    f"Interface_Overview_{lang}.pdf")
        else:
            page = ("https://jeanslack.github.io/Videomass/"
                    "Pages/User-guide-languages/en/1-User_"
                    "Interface_Overview_en.pdf"
                    )
        link2 = hpl.HyperLinkCtrl(self, -1, ("1.4 Concatenate media files "
                                             "(demuxer)"), URL=page)
        sizer_link2.Add(self.lbl_msg3, 0, wx.ALL | wx.EXPAND, 5)
        sizer_link2.Add(link2)
        sizer_link1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer_link1)
        self.lbl_msg2 = wx.StaticText(self, wx.ID_ANY,
                                      label=_("For more information, "
                                              "visit the official FFmpeg "
                                              "documentation:")
                                      )
        link1 = hpl.HyperLinkCtrl(self, -1, "3.4 concat",
                                  URL="https://ffmpeg.org/ffmpeg-formats."
                                      "html#concat"
                                  )
        sizer_link1.Add(self.lbl_msg2, 0, wx.ALL | wx.EXPAND, 5)
        sizer_link1.Add(link1)
        self.SetSizer(sizer)

        if appdata['ostype'] == 'Darwin':
            self.lbl_msg2.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            self.lbl_msg3.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            self.lbl_msg2.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            self.lbl_msg3.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.Bind(wx.EVT_BUTTON, self.on_help, self.btn_help)
    # ---------------------------------------------------------

    def on_help(self, event):
        """
        event on button help
        """
        win = NormalTransientPopup(self,
                                   wx.SIMPLE_BORDER,
                                   Conc_Demuxer.MSG_1,
                                   Conc_Demuxer.LGREEN,
                                   Conc_Demuxer.BLACK)

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()
    # ---------------------------------------------------------

    def on_start(self):
        """
        Builds FFmpeg command arguments

        """
        fsource = self.parent.file_src
        ftext = os.path.join(self.cachedir, 'tmp', 'flist.txt')

        diff = compare_media_param(self.parent.data_files)
        if diff:
            wx.MessageBox(diff, _('ERROR'), wx.ICON_ERROR, self)
            return

        textstr = []
        ext = os.path.splitext(self.parent.file_src[0])[1].split('.')[1]
        self.duration = sum(self.parent.duration)
        for f in self.parent.file_src:
            escaped = f.replace(r"'", r"'\''")  # need escaping some chars
            textstr.append(f"file '{escaped}'")
        self.args = (f'"{ftext}" -map 0:v? -map_chapters 0 '
                     f'-map 0:s? -map 0:a? -map_metadata 0 -c copy')

        with open(ftext, 'w', encoding='utf8') as txt:
            txt.write('\n'.join(textstr))

        checking = check_files((fsource[0],),
                               self.parent.outputdir,
                               self.parent.same_destin,
                               self.parent.suffix,
                               ext,
                               self.parent.outputnames
                               )
        if not checking:  # User changing idea or not such files exist
            return
        newfile = checking[1]

        self.concat_demuxer(self.parent.file_src, newfile[0], ext)
    # -----------------------------------------------------------

    def concat_demuxer(self, filesrc, newfile, outext):
        """
        Redirect to processing

        """
        logname = 'concatenate_demuxer.log'
        valupdate = self.update_dict(newfile, os.path.dirname(newfile), outext)
        ending = Formula(self, valupdate[0], valupdate[1], (600, 170),
                         self.parent.movetotrash, self.parent.emptylist,
                         )
        if ending.ShowModal() == wx.ID_OK:
            self.parent.movetotrash, self.parent.emptylist = ending.getvalue()
            self.parent.switch_to_processing('concat_demuxer',
                                             filesrc,
                                             None,
                                             newfile,
                                             self.args,
                                             None,
                                             self.duration,  # modify
                                             None,
                                             logname,
                                             1,
                                             )
    # -----------------------------------------------------------

    def update_dict(self, newfile, destdir, ext):
        """
        Update information before send to epilogue

        """
        lenfile = len(self.parent.file_src)

        formula = (_("File to concatenate\nOutput filename"
                     "\nDestination\nOutput Format\nTime Period"
                     ))
        dictions = (f"{lenfile}\n{newfile}\n{destdir}\n{ext}\n"
                    f"Not applicable")
        return formula, dictions
