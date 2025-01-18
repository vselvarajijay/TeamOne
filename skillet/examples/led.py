import tkinter as tk
from PIL import Image, ImageDraw
import pykos

# Configuration
GRID_WIDTH = 32
GRID_HEIGHT = 16
CELL_SIZE = 10  # Pixel size for drawing

# Initialize KOS connection
kos = pykos.KOS('192.168.42.1')

# Create a blank image (1-bit per pixel)
image = Image.new("1", (GRID_WIDTH, GRID_HEIGHT), "black")
draw = ImageDraw.Draw(image)

# Tkinter setup
root = tk.Tk()
root.title("32x16 Bitmap Drawer")
canvas = tk.Canvas(root, width=GRID_WIDTH * CELL_SIZE, height=GRID_HEIGHT * CELL_SIZE, bg="white")
canvas.pack()

# Draw grid
def draw_grid():
    for x in range(0, GRID_WIDTH * CELL_SIZE, CELL_SIZE):
        canvas.create_line(x, 0, x, GRID_HEIGHT * CELL_SIZE, fill="gray")
    for y in range(0, GRID_HEIGHT * CELL_SIZE, CELL_SIZE):
        canvas.create_line(0, y, GRID_WIDTH * CELL_SIZE, y, fill="gray")

draw_grid()

# Send bitmap to KOS
def send_bitmap():
    try:
        # Convert image to raw bytes (1-bit per pixel)
        bitmap_data = image.tobytes()
        response = kos.led_matrix.write_buffer(bitmap_data)
        if response.success:
            pass
        else:
            print("Failed to send bitmap")
    except Exception as e:
        print(f"Error sending bitmap: {e}")

# Event handlers
def draw_pixel(event, erase=False):
    x, y = event.x // CELL_SIZE, event.y // CELL_SIZE
    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
        # Check if shift is held down
        erase = event.state & 0x1  # Check shift state
        # Draw on canvas
        canvas.create_rectangle(
            x * CELL_SIZE, y * CELL_SIZE,
            (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
            fill="white" if erase else "black"
        )
        
        # Redraw grid lines for this cell if erasing
        if erase:
            # Vertical lines (left and right)
            canvas.create_line(x * CELL_SIZE, y * CELL_SIZE, 
                             x * CELL_SIZE, (y + 1) * CELL_SIZE, 
                             fill="gray")
            canvas.create_line((x + 1) * CELL_SIZE, y * CELL_SIZE,
                             (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                             fill="gray")
            # Horizontal lines (top and bottom)
            canvas.create_line(x * CELL_SIZE, y * CELL_SIZE, 
                             (x + 1) * CELL_SIZE, y * CELL_SIZE, 
                             fill="gray")
            canvas.create_line(x * CELL_SIZE, (y + 1) * CELL_SIZE,
                             (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                             fill="gray")
            
        # Update PIL image with shifted y coordinate
        shifted_y = (y - 1) % GRID_HEIGHT
        draw.rectangle([x, shifted_y, x, shifted_y], fill="black" if erase else "white")
        # Send bitmap after each pixel update
        send_bitmap()

def clear_canvas():
    canvas.delete("all")
    draw_grid()
    draw.rectangle([0, 0, GRID_WIDTH, GRID_HEIGHT], fill="black")
    # Send bitmap after clearing
    send_bitmap()

# Add buttons
clear_button = tk.Button(root, text="Clear", command=clear_canvas)
clear_button.pack(side="left", padx=10)

send_button = tk.Button(root, text="Send", command=send_bitmap)
send_button.pack(side="right", padx=10)

# Bind events
canvas.bind("<B1-Motion>", draw_pixel)
canvas.bind("<Button-1>", draw_pixel)

# Run application
root.mainloop()
