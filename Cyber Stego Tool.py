from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from stegano import lsb
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import base64
import os
import urllib.request

# ========== Check & Download Required Files ==========
includes_path = ".includes"
photo_path = os.path.join(includes_path, "photo.png")
icon_path = os.path.join(includes_path, "icon.ico")

if not os.path.exists(includes_path):
    os.makedirs(includes_path)

if not os.path.exists(photo_path):
    urllib.request.urlretrieve("https://raw.githubusercontent.com/rootuserdj/rootuserdj/master/photo.png", photo_path)

if not os.path.exists(icon_path):
    urllib.request.urlretrieve("https://raw.githubusercontent.com/rootuserdj/rootuserdj/master/icon.ico", icon_path)

# ========== Initialize Window ==========
win = Tk()
win.geometry('780x530')
win.title("Cyber Stego Tool - Secure Image Messaging (Created by Dhananjay Sah)")
win.iconbitmap(icon_path)
win.config(bg='#0f172a')
win.resizable(False, False)

open_file = None
hide_msg = None

# ========== Encryption / Decryption ==========
def encrypt_message(message, key):
    key_bytes = hashlib.sha256(key.encode()).digest()
    cipher = AES.new(key_bytes, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return iv + ":" + ct

def decrypt_message(encrypted_msg, key):
    try:
        key_bytes = hashlib.sha256(key.encode()).digest()
        iv, ct = encrypted_msg.split(":")
        iv = base64.b64decode(iv)
        ct = base64.b64decode(ct)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')
    except:
        return None

# ========== App Functions ==========
def open_img():
    global open_file
    open_file = filedialog.askopenfilename(
        initialdir=os.getcwd(),
        title='Select Image File',
        filetypes=[('Image Files', '*.png *.jpg')]
    )
    load_image(open_file)

def load_image(filepath):
    global open_file
    if filepath:
        open_file = filepath
        try:
            img = Image.open(filepath).resize((240, 210))
            img = ImageTk.PhotoImage(img)
            image_label.configure(image=img)
            image_label.image = img
        except:
            messagebox.showerror('Error', 'Failed to load image.')

def hide():
    global hide_msg
    key = code.get().strip()
    message = text_area.get(1.0, END).strip()

    if not key or not message or not open_file:
        messagebox.showerror('Error', 'Please provide image, message, and key.')
        return

    encrypted = encrypt_message(message, key)
    hide_msg = lsb.hide(open_file, encrypted)
    messagebox.showinfo('Success', 'Message hidden successfully! Now save the image.')

def save_img():
    if hide_msg:
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            title="Save Image As"
        )
        if filepath:
            hide_msg.save(filepath)
            messagebox.showinfo('Saved', 'Image saved successfully!')
    else:
        messagebox.showerror('Error', 'No hidden message to save')

def show():
    key = code.get().strip()
    if not open_file or not key:
        messagebox.showerror('Error', 'Please select image and enter key.')
        return

    try:
        encrypted = lsb.reveal(open_file)
        decrypted = decrypt_message(encrypted, key)
        if decrypted:
            text_area.delete(1.0, END)
            text_area.insert(END, decrypted)
        else:
            messagebox.showerror('Error', 'Wrong key or no message found.')
    except:
        messagebox.showerror('Error', 'Failed to reveal message.')

# ========== Animated Title ==========
title_text = "Cyber Stego Tool"
title_label = Label(win, text="", font='impact 28 bold', bg='#0f172a', fg='#38bdf8')
title_label.place(x=235, y=10)

def animate_title(i=0):
    title_label.config(text=title_text[:i])
    if i <= len(title_text):
        win.after(120, animate_title, i + 1)

animate_title()

# ========== Image Frame ==========
img_frame = Frame(win, width=250, height=220, bd=5, bg='#1e293b')
img_frame.place(x=40, y=90)

# Load and apply opacity to default image
try:
    base_img = Image.open(photo_path).convert("RGBA")
    alpha = 0.6
    new_data = [(r, g, b, int(a * alpha)) for r, g, b, a in base_img.getdata()]
    base_img.putdata(new_data)
    base_img = base_img.resize((240, 210))
    display_img = ImageTk.PhotoImage(base_img)
    image_label = Label(img_frame, bg='#1e293b', image=display_img)
    image_label.image = display_img
    image_label.place(x=0, y=0)
except:
    image_label = Label(img_frame, bg='#1e293b', text="Image Load Error", fg="white")
    image_label.place(x=0, y=0)

# ========== Drag & Drop ==========
def on_drop(event):
    filepath = event.data.strip("{}")  # Handles paths with spaces
    load_image(filepath)

try:
    # Try importing tkdnd for drag-drop
    win.tk.call('package', 'require', 'tkdnd')
    win.drop_target_register(DND_FILES)
    win.dnd_bind('<<Drop>>', on_drop)
except:
    pass  # Skip if not supported

# ========== Message Frame ==========
msg_frame = Frame(win, width=420, height=220, bd=5, bg='#e2e8f0')
msg_frame.place(x=300, y=90)
text_area = Text(msg_frame, font='Arial 12', wrap=WORD, bg='#f8fafc', fg='black')
text_area.place(x=0, y=0, width=410, height=210)

# ========== Secret Key Entry ==========
Label(win, text='Enter Secret Key', font='Arial 12 bold', bg='#0f172a', fg='white').place(x=175, y=355)
code = StringVar()
key_entry = Entry(win, textvariable=code, bd=2, font='Arial 12', show='*', width=30)
key_entry.place(x=310, y=355)

# ========== Buttons ==========
def on_enter(e): e.widget['bg'] = '#334155'
def on_leave(e): e.widget['bg'] = e.widget.original_bg

def create_button(text, command, x, y, bg, fg):
    btn = Button(win, text=text, font='Arial 11 bold', bg=bg, fg=fg, width=14, cursor='hand2', command=command)
    btn.place(x=x, y=y)
    btn.original_bg = bg
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

create_button('Open Image', open_img, 90, 420, '#3b82f6', 'white')
create_button('Save Image', save_img, 245, 420, '#22c55e', 'white')
create_button('Hide Data', hide, 400, 420, '#ef4444', 'white')
create_button('Show Data', show, 555, 420, '#f59e0b', 'white')

# ========== Footer ==========
footer = Label(win, text="Created by Dhananjay Sah", font='Arial 12 italic', bg='#0f172a', fg='#94a3b8')
footer.place(relx=0.5, rely=0.96, anchor=CENTER)

# ========== Run ==========
win.mainloop()
