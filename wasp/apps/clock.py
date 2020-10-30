# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
#
# Modified by Graham Harby

"""Themed digital clock
~~~~~~~~~~~~~~~~~~~~~~~

Modified version of Daniel Thompson's wasp-os stock digital clock
to provide a display loosely based on the theme of the Star Trek
computer.

v0.1
Displays time (HH:MM), date (ddd d MMM yyyy) a battery meter bar
graph with charging animation and a daily step counter.

Areas to develop are heart rate, weather and alert message display

"""

import wasp
import watch
import machine      #required for performance timer only, clean after
import gadgetbridge

import icons

import w_icons      #weather icons
import fonts.font10 as font10
import fonts.sans36 as sans36

class ClockApp():
    """Simple digital clock application.
    """
    NAME = 'Clock'
    ICON = icons.clock

    def __init__(self):
        watch.accel.reset()
        self.charging = 0
        self.screen = 1
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.few_clouds = (
            b'\x02'
            b'$\x12'
            b'\x0c\xc5\x08@\xd2E\x11\xc7\x06G\x0f\xc9\x04I\r\xcb'
            b'\x02K\x0c\xcb\x01M\x0b\xcb\x01M\x0b\xceK\x07\xd3J'
            b'\x06\xd5I\x05\xd6H\x05\xd7G\x06\xd8A\xc3A\x07\xdd'
            b'\x07\xde\x06\xde\x07\xdd\x08\xdb\n\xd9\x06'
        )
        # 2-bit RLE, generated from /home/graham/Pictures/weather/clear_sky.png, 42 bytes
        self.clear_sky = (
            b'\x02'
            b'$\x12'
            b'\x0f@\xd2F\x1cJ\x19L\x17N\x15P\x14P\x13R'
            b'\x12R\x12R\x12R\x12R\x12R\x13P\x14P\x15N'
            b'\x17L\x19J\x1cF\x0f'
        )

        #self.last_note = " "

    def foreground(self):
        """Activate the application."""
        self.alerts = 0b00000000    # alert holder
        self.scr_cnt = 0            # scroll counter
        self.ticker = 0             # ticker tape needed
        self.full_sec = 0           # count half sec tick for ticker tape
        self.on_screen = ( -1, -1, self.on_screen[2], -1, -1, -1 )
        self.draw()
        self.write_wthr()
        wasp.system.request_tick(500)

    def sleep(self):
        return True

    def wake(self):
        self.update()

    def tick(self, ticks):
        body = wasp.system.last_note
        if self.ticker and body != " ":
            self.write_ticker(body)
        if self.full_sec:
            self.update()
        self.full_sec = not self.full_sec

    def draw(self):
        """Redraw the display from scratch."""
        # Screen graphics
        # Top left
        tl = (
            148, 38,
            b'\x07\x8d\x05\x8f\x04\x90\x03\x91\x02\x92\x01\x93\x01\x93'
            b'\x00\x94\x00\x94\x00\x94\x00\x94\x00\x94\x00\x94\x00\x94'
            b'\x00\x94\x00\x94\x00\x94\x00\x94\x00\x94\x00\x94'
            b'\x00\x21\x73\x20\x74\x1f\x75\x1e\x76\x1e\x76\x1e\x76'
            b'\x1e\x76\x1e\x76\x1e\x76\x1e\x76\x1e\x76\x1e\x76'
            b'\x1e\x76\x1e\x76\x1e\x76\x1e\x76\x1e\x76\x1e\x76'
        )

        # Top right
        tr = (
            88, 20,
            b'\x00\x52\x06\x54\x04\x56\x02\x56\x02\x00'
            b'\x1e\x39\x01\x00\x1e\x3a\x1e\x3a\x1e\x3a'
            b'\x58\x00\x58\x00\x58\x00\x58\x00'
            b'\x1e\x3a\x1e\x3a\x1e\x3a\x1e\x3a'
            b'\x00\x58\x00\x58\x00\x58\x00\x58'
        )

        # Right centre lower
        rcl = (
            40, 26,
            b"\x00!\x07#\x05$\x04%\x03&\x02'\x01'\x01(\x11"
            b'\x17\x12\x16\x13\x15\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b'\x14\x14\x14'
        )

        # Left centre
        lc = (
            40, 38,
            b'\x00\x1e\n\x1e\n\x1e\n\x1e\n\x1e\n\x1e\n\x1e\n\x1e\n'
            b'\x1e\n\x1e\n\x1e\n\x1e\n\x1e\n\x1e\n\x1e\n\x1f\t'
            b" \x08!\x07\xff\x00\xff\x00\n\x01'\x01'\x02&\x03"
            b'%\x04$\x05#\x07!'
        )

        # Right centre
        rc = (
            40, 94,
            b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b"\x14\x14\x14\x14\x14\x14\x13\x15\x12\x16\x11f\x01'\x01&"
            b'\x02%\x03$\x04#\x05!\x07'
        )

        # Bottom
        bt = (
            240, 38,
            b'\xdc\x14\xdc\x14\xdc\x14\xdc\x14\xdc\x14\xdc\x14\xdc\x14\xdc\x14'
            b'\xdc\x14\xdc\x14\xdc\x14\xdc\x14\xdc\x14\xdc\x14\xdc\x14\xdc\x14'
            b'\xdc\x14\xdc\x14\xdc\x14\xdc\x14\xdc\x14\xdc\x14\xdc\x14\xdc\x14'
            b'\xdc\x14\xdb\x15\xda\x16\xd9\x17\x03\xed\x02\xee\x01\xff\x00\xdf'
            b'\x01\xef\x01\xee\x02\xed\x04\xeb\x06\xe9\x08\xe6\x07'
        )

        # Tag
        tg = (
            20, 20,
            b'\x07\x0d\x05\x0f\x04\x10\x03\x11\x02\x12\x01\x13\x01\x13'
            b'\x00\x14\x00\x14\x00\x14\x00\x14\x00\x14\x00\x14\x00\x14'
            b'\x01\x13\x01\x13\x02\x12\x03\x11\x04\x10\x05\x0f\x07\x0d'
        )

        #Colours
        b = 0x003f      #blue
        y = 0xf7c0      #yellow
        o = 0xfc20      #orange
        s = 0xf927      #salmon red
        dg = 0x636d     #dark grey
        scrs = ("Time", "Alerts", " ", "Steps", "Weather")

        #draw = wasp.watch.drawable
        fill = wasp.watch.drawable.fill
        blit = wasp.watch.drawable.blit
        drw_s = wasp.watch.drawable.string
        set_f = wasp.watch.drawable.set_font
        set_c = wasp.watch.drawable.set_color

        fill()
        blit(tl, 0 , 0, fg=y)
        blit(tr, 152, 0, fg=dg)
        blit(lc, 0 , 92, fg=y)
        blit(rc, 200 , 24, fg=y)
        blit(rcl, 200 , 122, fg=s)
        blit(bt, 0 , 202, fg=s)
        #weather icon test
        #blit(w_icons.few_clouds, 145, 135 + 24 *3)
        #fill(b, 0, 42, 30, 46)
        fill(b, 220, 152, 20, 46)
        fill(s, 44, 122, 152, 8)

        set_f(font10)
        set_c(0, o)
        for i in range(0, 4):
            blit(tg, 0, 134 + i * 24, o)
            fill(o, 24, 134 + i * 24, 80, 20)
            drw_s(scrs[i + self.screen], 28, 137 + i *24)
            i += 1
        set_c(0xffff)
        now = wasp.watch.rtc.get_localtime()
        self.update()

    def scroll(self, font, s, w):
        s_w = 0
        c_count = 0
        for ch in s:
            glyph = font.get_ch(ch)
            s_w += glyph[2]
            if s_w < w:
                c_count += 1
                s_w += 1
            else:
                break
        return s[: c_count]

    def write_time(self, now):
        r = 0xf800      #red
        g = 0x0783      #green
        b = 0x003f      #blue
        o = 0xfc20      #orange
        lg = 0xa596     #light grey
        fill = wasp.watch.drawable.fill
        drw_s = wasp.watch.drawable.string
        set_f = wasp.watch.drawable.set_font

        timeStr = str(now[3] // 10) + str(now[3] % 10) + ":" + str(now[4] // 10) + str(now[4] % 10)
        set_f(sans36)
        drw_s(timeStr, 42, 32)

        min_delta = now[4] - self.on_screen[4]
        if min_delta < 0 or self.on_screen[4] == -1:
            fill(lg, 108, 110, 60, 8)
            fill(b, 108, 110, now[4], 8)
        else:
            #min_change = now[4] - self.on_screen[4]
            fill(b, 108 - min_delta + now[4], 110, min_delta, 8)

        if self.on_screen[3] == -1 or now[3] == 0:
            fill(lg, 172, 110, 24, 8)
            if self.on_screen[3] == -1:
                fill(b, 172, 110, now[3], 8)
        else:
            hr_change = now[3] - self.on_screen[3]
            fill(b, 172 - hr_change + now[3], 110, hr_change, 8)

        """ Update battery level if not charging """
        if not watch.battery.charging():
            self.charging = 0
            level = (watch.battery.level() + 10) // 20
            fill(0, 152, 5, 29, 10)
            if level == 0:
                fill(r, 152, 5, 5, 10)
            elif level == 1:
                fill(o, 152, 5, 5, 10)
            else:
                for i in range(0, level):
                    fill(g, 152 + 6 * i, 5, 5, 10)

    def write_date(self, now):
        drw_s = wasp.watch.drawable.string
        set_f = wasp.watch.drawable.set_font
        set_f(font10)
        month = now[1] - 1
        month = 'JanFebMarAprMayJunJulAugSepOctNovDec'[month*3:(month+1)*3]
        day = 'MonTueWedThuFriSatSun'[now[6]*3:(now[6]+1)*3]
        drw_s('{} {} {} {}'.format(day, now[2], month, now[0]), 46, 84)

    def write_wthr(self):
        fill = wasp.watch.drawable.fill
        drw_s = wasp.watch.drawable.string
        set_f = wasp.watch.drawable.set_font
        blit = wasp.watch.drawable.blit
        wthr = wasp.system.wthr
        if len(wthr):
            set_f(font10)
            fill(0, 107, 134 + 24 * 3, 113, 20)
            drw_s('{}C'.format(wthr['temp'] - 273), 115, 137 + 24 * 3)
            icon = wthr['txt'].lower()
            if icon == 'clear sky':
                blit(w_icons.clear_sky, 184, 136 + 24 *3)
            elif icon == 'few clouds':
                blit(w_icons.few_clouds, 184, 136 + 24 *3)
            elif icon == 'scattered clouds':
                blit(w_icons.scattered_clouds, 184, 136 + 24 *3)
            elif 'clouds' in icon: # == 'broken cloud':
                blit(w_icons.broken_cloud, 184, 136 + 24 *3)
            elif 'drizzle' in icon: # == 'light rain':
                blit(w_icons.shower_rain, 184, 136 + 24 *3)
            elif 'rain' in icon: # == 'rain':
                blit(w_icons.rain, 184, 136 + 24 *3)
            elif icon == 'thunderstorm':
                blit(w_icons.thunderstorm, 184, 136 + 24 *3)
            elif 'snow' in icon: # == '13d':
                blit(w_icons.snow, 184, 136 + 24 *3)
            elif icon == 'mist':
                blit(w_icons.mist, 184, 136 + 24 *3)

    def write_ticker(self, body):
        fill = wasp.watch.drawable.fill
        drw_s = wasp.watch.drawable.string
        #body = wasp.system.last_note
        if self.scr_cnt == 0:
            temp = self.scroll(font10, body, 184)
            fill(0, 203, 134 + 24, 9, 20) # fill last half character only to reduce flicker
            drw_s(temp, 28, 137 + 24)
        if self.scr_cnt > 2:
            i = self.scr_cnt - 2
            test = self.scroll(font10, body[i:], 184)
            if test == body[i:]:
                self.scr_cnt = -4
            fill(0, 203, 134 + 24, 9, 20) # fill last half character only to reduce flicker
            drw_s(test, 28, 137 + 24)
        self.scr_cnt += 1

    def update(self):
        b = 0x003f      #blue
        g = 0x0783      #green
        lg = 0xa596     #light grey
        dg = 0x636d     #dark grey
        o = 0xfc20      #orange
        draw = wasp.watch.drawable
        fill = wasp.watch.drawable.fill
        drw_s = wasp.watch.drawable.string
        set_f = wasp.watch.drawable.set_font
        now = wasp.watch.rtc.get_localtime()

        """ Update seconds bar """
        sec_delta = now[5] - self.on_screen[5]
        if self.on_screen[5] == -1 or sec_delta < 0:
            fill(lg, 44, 110, 60, 8)
            fill(b, 44, 110, now[5], 8)
        else:
            fill(b, 44 - sec_delta + now[5], 110, sec_delta, 8)
        if now[3] != self.on_screen[3] or now[4] != self.on_screen[4]:
            self.write_time(now)
        if now[2] != self.on_screen[2] or now[1] != self.on_screen[1]:
            self.write_date(now)
            if now[2] != self.on_screen[2]:
                watch.accel.steps = 0   # Reset step count on new day
                # TODO: Make fill dynamic with selected screen
                fill(0, 107, 134 + 24 * 2, 113, 20)

        """ If charging animate charging """
        if watch.battery.charging():
            if self.charging == 0:
                fill(0, 152, 5, 29, 10)
            else:
                for i in range(0, self.charging):
                    fill(g, 152 + 6 * i, 5, 5, 10)
            self.charging += 1
            if self.charging > 5:
                self.charging = 0
        set_f(font10)

        """ Draw Bluetooth connection state """
        if wasp.watch.connected():
            fill(b, 0, 42, 30, 46)
        else:
            fill(dg, 0, 42, 30, 46)

        """ Write notifications """
        srcs = wasp.system.srcs
        if srcs != self.alerts:
            i = 0
            fill(0x0000, 107, 134, 113, 20)
            if srcs & 0b00000001:
                fill(0xf80f, 111, 134, 17, 20)
                i += 1
            if srcs & 0b00000010:
                fill(g, 111 + i * 21, 134, 17, 20)
                i += 1
            if srcs & 0b00000100:
                fill(b,  111 + i * 21, 134, 17, 20)
                i += 1
            if srcs & 0b00001000:
                fill(0xf800,  111 + i * 21, 134, 17, 20)
                i += 1
            if srcs & 0b00010000:
                fill(dg,  111 + i * 21, 134, 17, 20)

            body = wasp.system.last_note
            if body != " ":
                test = self.scroll(font10, body, 184)
                if test != body:
                    self.ticker = 1
                    self.scr_cnt = 0
                else:
                    self.ticker = 0
                fill(0, 24, 134 + 24, 192, 20)
                drw_s(test, 28, 137 + 24)
            else:
                fill(o, 24, 134 + 24, 80, 20)
                fill(0, 104, 134 + 24, 116, 20)
                self.ticker = 0

            """ Write weather if updated """
            if srcs & 0b10000000:
                wasp.system.srcs &= 0b01111111
                self.write_wthr()

            self.alerts = wasp.system.srcs

        """ Write steps """
        # TODO: Make drw_s dynamic with selected screen
        drw_s(str(watch.accel.steps), 115, 137 + 24 * 2)

        """ Set on_screen to now time """
        self.on_screen = now
        return True
