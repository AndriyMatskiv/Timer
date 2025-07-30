import flet as ft
from datetime import datetime
import asyncio
import win32gui
import win32con
import keyboard
import gc
import os
import sys


def resource_path(filename):
    if hasattr(sys, "_MEIPASS"):  
        return os.path.join(sys._MEIPASS, filename) 
    return os.path.join(os.path.abspath("."), filename)

async def main(page: ft.Page):
    page.title = "Timer"
    page.window.icon = r"D:\Uni\PyProj\Timer\cloak.ico" # path for icon
    page.window.bgcolor = ft.Colors.TRANSPARENT
    page.bgcolor = ft.Colors.TRANSPARENT
    page.window.width = 310
    page.window.height = 200
    page.window.always_on_top = True
    page.window.title_bar_hidden = False
    page.window.frameless = False
    page.window.resizable = False
    
    
    hwnd = win32gui.FindWindow(None, "Timer")
    if hwnd:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 300, 200,
                              win32con.SWP_NOMOVE | win32con.SWP_NOACTIVATE)
        
    is_paused = False
    is_count_up = False
    stop_timer= False
    timer_task = None
    audio_file = resource_path("timer-ticks.mp3")
    audio = ft.Audio(src=audio_file,autoplay=False)
    page.overlay.append(audio)
    total_sec = 0
    
    async def reset(e):
        nonlocal total_sec,is_count_up,stop_timer,timer_task
        total_sec = 0
        is_count_up = False
        stop_timer = True
        if timer_task is not None and not timer_task.done():
            timer_task.cancel()
            input_hours.value = ""
            input_minutes.value = ""
            input_seconds.value = ""
            try:
                await timer_task
            except asyncio.CancelledError:
                pass

    async def timer_loop():
        nonlocal total_sec, is_paused, is_count_up, stop_timer, audio
        while not stop_timer:
            if not is_paused:
                await asyncio.sleep(1)

                if is_count_up:
                    total_sec += 1
                else:
                    total_sec -= 1

                v_hrs = total_sec // 3600
                v_min = (total_sec % 3600) // 60
                v_sec = total_sec % 60
                input_hours.value = str(v_hrs)
                input_minutes.value = str(v_min)
                input_seconds.value = str(v_sec)
                page.update()

                if not is_count_up and total_sec <= 0:
                    audio.pause()
                    stop_timer = True
                    total_sec = 0
                    input_hours.value = ""
                    input_minutes.value = ""
                    input_seconds.value = ""
                    page.update()
                    break

                if not is_count_up and total_sec == 5:
                    audio.play()
            else:
                await asyncio.sleep(0.1)
                
    async def start_timer(e):
        nonlocal is_paused, total_sec, is_count_up,stop_timer,timer_task
        is_paused = False
        stop_timer = False
        
        v_hrs = int(input_hours.value) if input_hours.value.strip() else 0
        v_min = int(input_minutes.value) if input_minutes.value.strip() else 0
        v_sec = int(input_seconds.value) if input_seconds.value.strip() else 0

        total_sec = v_hrs * 3600 + v_min * 60 + v_sec
        is_count_up = total_sec == 0

        if timer_task is not None and not timer_task.done():
            timer_task.cancel()
            try:
                await timer_task
            except asyncio.CancelledError:
                pass

        timer_task = asyncio.create_task(timer_loop())
        
    
    async def pause(e):
        nonlocal is_paused,total_sec
        is_paused = not is_paused
        if total_sec > 0:
            if is_paused:
                control_btn.text = "Resume"
            else:
                control_btn.text = "Pause"
            page.update()
        
    
    
    rn = datetime.now().strftime('%H:%M:%S')
    
    my_time=ft.Text(rn,text_align=ft.TextAlign.CENTER)
    input_hours = ft.TextField(width=58,border_color=ft.Colors.WHITE24,max_length=3,text_align=ft.TextAlign.CENTER,label="Hrs")
    input_minutes = ft.TextField(width=58,border_color=ft.Colors.WHITE24,max_length=3,text_align=ft.TextAlign.CENTER,label="Min")
    input_seconds = ft.TextField(width=58, border_color=ft.Colors.WHITE24,max_length=3, text_align=ft.TextAlign.CENTER,label="Sec")
    
    
    
    r1 = ft.Row(controls=[my_time],alignment=ft.MainAxisAlignment.CENTER)
    r2 = ft.Row(controls=[input_hours,input_minutes,input_seconds],alignment=ft.MainAxisAlignment.CENTER)
    
    timer_btn = ft.FilledButton(
        "Start Timer"
        ,bgcolor="#1A1A1A"
        ,color="#D0CFCC"
        ,style=ft.ButtonStyle(
            text_style=ft.TextStyle(
                size=12
            ),
        ),on_click= start_timer
    )
    
    
    control_btn = ft.FilledButton(
        "Pause"
        ,bgcolor="#1A1A1A"
        ,color="#D0CFCC"
        ,style=ft.ButtonStyle(
            text_style=ft.TextStyle(
                size=12
            ),
        ),on_click= pause
    )
    
    reset_btn = ft.FilledButton(
        "Reset"
        ,bgcolor="#1A1A1A"
        ,color="#D0CFCC"
        ,style=ft.ButtonStyle(
            text_style=ft.TextStyle(
                size=12
            ),
        ),on_click= reset
    )
    
    functionality = ft.Row(controls=[
            timer_btn,control_btn,reset_btn
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    
    r3 = ft.Row(
        controls=[
            ft.Text("'Shift + 5' - 'Start'",size=8),
            ft.Text("'Shift + 6' - 'Pause/Resume'",size=8),
            ft.Text("'Shift + 7' - 'Reset'",size=8)
        ]
    )
    
    
    
    async def update_time():
        while True:
            my_time.value = datetime.now().strftime('%H:%M:%S')
            page.update()
            await asyncio.sleep(1)
            
    page.run_task(update_time)
    
    async def hotkeys_listener():
        loop = asyncio.get_event_loop()

        def on_hotkey_start():
            asyncio.run_coroutine_threadsafe(start_timer(None), loop)

        def on_hotkey_pause():
            asyncio.run_coroutine_threadsafe(pause(None), loop)

        def on_hotkey_reset():
            asyncio.run_coroutine_threadsafe(reset(None), loop)

        keyboard.add_hotkey('shift+5', on_hotkey_start)
        keyboard.add_hotkey('shift+6', on_hotkey_pause)
        keyboard.add_hotkey('shift+7', on_hotkey_reset)

        while True:
            await asyncio.sleep(0.1)

    page.run_task(hotkeys_listener)

    page.add(r1,r2,functionality,r3)
    
if __name__ == "__main__":
    ft.app(target=main)