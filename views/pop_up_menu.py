import subprocess
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import PhotoImage

def exit_program(window):
    window.destroy()

def button_clicked(mode, window, depth, visualize):
    exit_program(window)
    args = ["python", "controllers/game_controller.py", str(mode), str(depth), str(int(visualize))]
    subprocess.run(args)

def main_menu():
    style = ttk.Style(theme="morph")

    # Configuration
    common_font = ('Arial', 20, 'bold')
    text_color = 'darkblue'
    element_bg = '#f0f0f0'  # Unified background color [[1]][[6]]

    # Unified style configurations
    style.configure("TLabel", font=common_font, foreground=text_color)
    style.configure("Cloud.TEntry", 
                   font=common_font, 
                   padding=10, 
                   fieldbackground=element_bg,
                   borderwidth=2)
    
    style.configure("Cloud.TCheckbutton",
                   font=common_font, 
                   padding=10,
                   foreground=text_color,
                   background=element_bg,
                   indicatorsize=25)
    
    style.configure("Algorithm.TButton",
                   font=common_font,
                   padding=10,  # Match entry padding [[6]]
                   foreground=text_color,
                   background=element_bg,
                   borderwidth=2,
                   width=25)

    # Window setup
    window = style.master
    window.title("Connect 4")
    window.geometry("800x750")
    window.resizable(False, False)

    # Canvas setup
    canvas = ttk.Canvas(window, width=800, height=750)
    canvas.pack(fill='both', expand=True)

    # Background image or fallback color
    try:
        bg_img = PhotoImage(file="assests/img/resized_bg.png")
        canvas.bg_img = bg_img
        canvas.create_image(0, 0, image=bg_img, anchor='nw')
    except Exception:
        bg_color = style.colors.get("light") or "#d0e7f9"
        canvas.create_rectangle(0, 0, 800, 750, fill=bg_color, outline=bg_color)

    # Logo or fallback text
    try:
        logo_img = PhotoImage(file="assests/img/Connect_4_game_logo2.png")
        canvas.logo_img = logo_img
        canvas.create_image(400, 120, image=logo_img)
    except Exception:
        header = ttk.Label(window, text="CONNECT 4", font=('Arial', 36, 'bold'), foreground=text_color)
        canvas.create_window(400, 120, window=header)

    # Depth input with spacing
    depth_container_y = 230
    depth_label = ttk.Label(window, text="Search Depth:")
    canvas.create_window(330, depth_container_y, window=depth_label)

    depth_var = ttk.Entry(window, width=5, style="Cloud.TEntry", justify='center')
    depth_var.configure(font=("Arial", 18, "bold"), foreground="darkblue")
    depth_var.insert(0, '3')

    def clear_default(event):
        if depth_var.get() == "3":
            depth_var.delete(0, "end")

    depth_var.bind("<FocusIn>", clear_default)
    canvas.create_window(470, depth_container_y, window=depth_var)

    # Tree Visualizer checkbox
    visualize_var = ttk.IntVar(value=0)
    visualize_cb = ttk.Checkbutton(window, text="Show Tree Visualizer",
                                   variable=visualize_var, style="Cloud.TCheckbutton")
    canvas.create_window(400, 300, window=visualize_cb)

    # Algorithm buttons with unified styling
    button_y_start = 380
    button_spacing = 80

    btn_prune = ttk.Button(window, text="Minimax with Pruning",
                           style="Algorithm.TButton",
                           command=lambda: button_clicked(1, window, depth_var.get(), visualize_var.get()))
    canvas.create_window(400, button_y_start, window=btn_prune)

    btn_no_prune = ttk.Button(window, text="Minimax without Pruning",
                              style="Algorithm.TButton",
                              command=lambda: button_clicked(2, window, depth_var.get(), visualize_var.get()))
    canvas.create_window(400, button_y_start + button_spacing, window=btn_no_prune)

    btn_expectimax = ttk.Button(window, text="Expectiminimax",
                                style="Algorithm.TButton",
                                command=lambda: button_clicked(3, window, depth_var.get(), visualize_var.get()))
    canvas.create_window(400, button_y_start + 2*button_spacing, window=btn_expectimax)

    window.mainloop()

if __name__ == '__main__':
    main_menu()