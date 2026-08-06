import os
from PIL import Image, ImageDraw, ImageFont

def create_directory():
    os.makedirs("assets", exist_ok=True)
    print("Created 'assets' directory.")

def draw_rear_bumper():
    # Create a 600x400 image with a soft blue-grey background
    img = Image.new("RGB", (600, 400), "#f0f2f6")
    draw = ImageDraw.Draw(img)

    # Draw the car outline (rear view)
    draw.rounded_rectangle([(100, 100), (500, 320)], radius=30, fill="#2c3e50", outline="#34495e", width=5)
    # Windshield
    draw.rounded_rectangle([(120, 110), (480, 200)], radius=10, fill="#7f8c8d", outline="#34495e", width=3)
    # Taillights
    draw.rounded_rectangle([(110, 220), (160, 250)], radius=5, fill="#e74c3c")
    draw.rounded_rectangle([(440, 220), (490, 250)], radius=5, fill="#e74c3c")
    
    # Bumper
    draw.rectangle([(90, 260), (510, 310)], fill="#7f8c8d", outline="#34495e", width=3)
    # Tires
    draw.rectangle([(130, 320), (190, 350)], fill="#1a252f")
    draw.rectangle([(410, 320), (470, 350)], fill="#1a252f")

    # Draw DENT & CRACK (Impact Zone on Rear Bumper)
    # Impact circle
    draw.ellipse([(260, 270), (340, 310)], fill="#95a5a6", outline="#c0392b", width=2)
    # Cracks
    draw.line([(300, 290), (280, 280)], fill="#c0392b", width=3)
    draw.line([(300, 290), (325, 275)], fill="#c0392b", width=3)
    draw.line([(300, 290), (305, 305)], fill="#c0392b", width=3)
    
    # Highlight text box
    draw.rounded_rectangle([(230, 20), (370, 60)], radius=5, fill="#e74c3c")
    draw.text((250, 30), "REAR PROFILE", fill="white")
    draw.text((235, 360), "[Visible Damage: Rear Bumper Dent/Crack]", fill="#c0392b")

    img.save("assets/rear_bumper_dent.png")
    print("Saved assets/rear_bumper_dent.png")

def draw_front_bumper():
    img = Image.new("RGB", (600, 400), "#f0f2f6")
    draw = ImageDraw.Draw(img)

    # Draw the car outline (front view)
    draw.rounded_rectangle([(100, 100), (500, 320)], radius=30, fill="#34495e", outline="#2c3e50", width=5)
    # Windshield
    draw.rounded_rectangle([(120, 110), (480, 200)], radius=10, fill="#95a5a6", outline="#2c3e50", width=3)
    # Headlights (On)
    draw.ellipse([(110, 220), (160, 255)], fill="#f1c40f", outline="#d35400", width=2)
    draw.ellipse([(440, 220), (490, 255)], fill="#f1c40f", outline="#d35400", width=2)
    
    # Front Grille (Cracked)
    draw.rectangle([(200, 230), (400, 260)], fill="#1a252f", outline="#7f8c8d", width=2)
    # Draw grille vertical bars
    for x in range(215, 390, 15):
        draw.line([(x, 230), (x, 260)], fill="#7f8c8d", width=2)
    # Draw crack on grille
    draw.line([(280, 225), (320, 265)], fill="#c0392b", width=4)
    
    # Front Bumper with Dent
    draw.rectangle([(90, 270), (510, 315)], fill="#bdc3c7", outline="#7f8c8d", width=3)
    
    # Bumper Dent (Left side of vehicle front, i.e., right side on image)
    draw.ellipse([(350, 280), (430, 315)], fill="#95a5a6", outline="#c0392b", width=3)
    draw.line([(390, 290), (370, 310)], fill="#c0392b", width=2)
    
    # Highlight text box
    draw.rounded_rectangle([(230, 20), (370, 60)], radius=5, fill="#e67e22")
    draw.text((245, 30), "FRONT PROFILE", fill="white")
    draw.text((210, 360), "[Visible Damage: Front Bumper & Grille Dent]", fill="#c0392b")

    img.save("assets/front_bumper_dent.png")
    print("Saved assets/front_bumper_dent.png")

def draw_hail_damage():
    img = Image.new("RGB", (600, 400), "#f0f2f6")
    draw = ImageDraw.Draw(img)

    # Draw the car outline (angled hood & windshield view)
    # Windshield area
    draw.polygon([(150, 80), (450, 80), (500, 220), (100, 220)], fill="#5d6d7e", outline="#2c3e50", width=4)
    # Spiderweb crack on windshield (right side)
    draw.ellipse([(330, 130), (370, 170)], outline="#ecf0f1", width=2)
    for angle in range(0, 360, 45):
        import math
        rad = math.radians(angle)
        x_end = 350 + int(35 * math.cos(rad))
        y_end = 150 + int(35 * math.sin(rad))
        draw.line([(350, 150), (x_end, y_end)], fill="#ecf0f1", width=2)

    # Reflective face overlay (Privacy Risk)
    draw.ellipse([(200, 120), (230, 160)], fill="#34495e", outline="#e74c3c", width=2) # head
    draw.ellipse([(207, 128), (213, 134)], fill="#e74c3c") # eye
    draw.ellipse([(217, 128), (223, 134)], fill="#e74c3c") # eye
    draw.arc([(208, 140), (222, 150)], 0, 180, fill="#e74c3c", width=2) # mouth
    draw.rounded_rectangle([(170, 165), (260, 185)], radius=3, fill="#e74c3c")
    draw.text((175, 170), "REFLECTED FACE", fill="white")

    # Hood area
    draw.polygon([(100, 220), (500, 220), (550, 340), (50, 340)], fill="#7f8c8d", outline="#2c3e50", width=4)
    
    # Hail dents on Hood (small circular indentations)
    dents = [(150, 250), (220, 280), (280, 240), (320, 300), (390, 260), (450, 290)]
    for dent in dents:
        draw.ellipse([(dent[0]-8, dent[1]-5), (dent[0]+8, dent[1]+5)], fill="#7f8c8d", outline="#34495e", width=2)
        # Shadow highlight
        draw.arc([(dent[0]-8, dent[1]-5), (dent[0]+8, dent[1]+5)], 0, 180, fill="#bdc3c7", width=1)

    # License Plate (Privacy Risk)
    draw.rectangle([(240, 310), (360, 335)], fill="white", outline="#34495e", width=2)
    draw.text((250, 315), "LICENSE: TX 48A9", fill="#2c3e50")
    # Draw privacy alert border around plate
    draw.rectangle([(235, 305), (365, 340)], outline="#e74c3c", width=2)
    draw.text((260, 345), "PRIVACY DETECTED", fill="#e74c3c")

    # Title Banner
    draw.rounded_rectangle([(230, 20), (370, 60)], radius=5, fill="#3498db")
    draw.text((238, 30), "HOOD/WINDSHIELD", fill="white")
    draw.text((200, 375), "[Visual Damage: Hail Dents & Cracked Glass]", fill="#c0392b")

    img.save("assets/hail_damage.png")
    print("Saved assets/hail_damage.png")

if __name__ == "__main__":
    create_directory()
    draw_rear_bumper()
    draw_front_bumper()
    draw_hail_damage()
    print("All mock asset images generated successfully.")
