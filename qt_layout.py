# QT layout
from PySide6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton, QLineEdit, QMessageBox, QFrame, QScrollArea, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QColor, QPainter, QFont, QPen
import random # For random stars
import math # For shooting star angle calc
import time # For updating stars

# LLM integration
from llm import get_llm_response

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # The layout 

        # The little title in the window description
        self.setWindowTitle('✨ AstroScholar ✨')

        # Background (starry night)
        self.background = StarryBackground(self)
        self.background.lower() # Lower it so we can see everything else
        self.background.setGeometry(self.rect())  # Make it fill entire window

        # Main layout
        container_all =  QWidget() # Main container, inherits background
        self.layout_all = QVBoxLayout() # Vertically stack other containers
        layout_static = QVBoxLayout() # Vertically stacked elements for the input/top (unchanging size)
        
        # Scroll settings (for responses)
        self.scroll = QScrollArea() # Scrolling area for the response
        self.scroll.setStyleSheet("background: transparent;")
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn) # Even if the responses fit always display the scroll bar
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True) # Resize widgets inside to match size of scroll space 

        # Response widget set-up
        self.widget_response = QWidget() # Widget contains collection of vertical responses
        self.layout_response = QVBoxLayout() # Vertical elements layout
        self.widget_response.setLayout(self.layout_response)

        # The elements

        title = QLabel('AstroScholar')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("SansSerif", 38, QFont.Bold)) 
        title.setStyleSheet("color: #FFE27A;")

        glow_title = QGraphicsDropShadowEffect() 
        glow_title.setBlurRadius(50) # Blurs the edges into the glow
        glow_title.setColor(QColor("#FFE27A")) #  #F5F107 also looks good
        glow_title.setOffset(0) # Make it right on top
        title.setGraphicsEffect(glow_title)

        def on_focus():
            glow_title.setBlurRadius(40)
            glow_title.setColor(QColor("#F5F107" )) # FFE27A, F5F107, note: currently set to same colour

        title.focusInEvent = lambda e: on_focus() # If title is 'focused' by the window, change the colour, note that default focus is on the text input

        subtitle = QLabel('Historical Astrology Research Assistant')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("SansSerif", 18, QFont.Bold)) 
        subtitle.setStyleSheet("color: white;")

        prompt = QLabel('What would you like to know?')
        prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prompt.setFont(QFont("SansSerif", 12, QFont.Bold)) 
        prompt.setStyleSheet("color: #FFCC66;")
        
        hint = QLabel('Hint: Try "Metals associated with Venus" or "Plant attributions to Jupiter in Christian Astrology".')
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setFont(QFont("SansSerif", 8)) 
        hint.setStyleSheet("color: white;") 

        self.input_question = QLineEdit()
        self.input_question.setPlaceholderText('Ask me a question about Astrology...')
        self.input_question.setFixedWidth(500)
        self.input_question.setFont(QFont("SansSerif", 10))
        self.input_question.setAlignment(Qt.AlignHCenter) # Aligns the text inside

        button = QPushButton('Search the Stars')
        button.setFixedWidth(500) # This also sets the default min width of the window at 500 px
        button.setFont(QFont("SansSerif", 10, QFont.Weight.Bold))
        # button.clicked.connect(self.search_the_stars) # Alternative to on_hit 
        self.input_question.returnPressed.connect(self.search_the_stars) # If just enter is pressed
        
        # Glow effect
        glow_button = QGraphicsDropShadowEffect() 
        glow_button.setBlurRadius(20) # Blurs the edges into the glow
        glow_button.setColor(QColor("#F5F107")) # FFE27A or F5F107
        glow_button.setOffset(0) # Make it right on top        
        button.setGraphicsEffect(glow_button)

        def on_hit():
            glow_button.setBlurRadius(40)
            glow_button.setColor(QColor("#F5F107" )) # FFE27A, F5F107, note: currently set to same colour
            self.search_the_stars()

        button.hitButton = lambda e: on_hit()
        
        # Add each element to the layout
        layout_static.addWidget(title)
        layout_static.addWidget(subtitle)
        layout_static.addWidget(prompt)
        layout_static.addWidget(hint)
        layout_static.addWidget(self.input_question, alignment = Qt.AlignHCenter)
        layout_static.addWidget(button, alignment = Qt.AlignHCenter)

        # Add the layouts together (responses added later if generated)
        self.layout_all.addLayout(layout_static)
        self.layout_all.setAlignment(Qt.AlignCenter)
        
        container_all.setLayout(self.layout_all)
        self.setCentralWidget(container_all)

        self.showMaximized() # Make it full screen windowed automatically on startup

    def search_the_stars(self): 
        """
        Fired when user asks a question, calls and handles the response from the LLM and inserts it into the layout. 
        """
        if self.input_question.text().strip(): # If input text exists (is not empty)
            self.layout_all.addWidget(self.scroll)
            self.layout_all.setAlignment(Qt.AlignTop) # Move all content from centering in the middle to alignign with the top
            self.clear_content(self.layout_response) # Remove prev q

            answer = get_llm_response(self.input_question.text()) # Actually asks LLM
            
            for response in answer.responses: # For each source-response pair

                source, source_details, info = response.source, response.source_details, response.info # Seperate response for layout

                if source_details: # If there are extra source details
                    source = f"{source} ({source_details})" # Combine them into the source for easier formatting
                
                # Formatting each response: text
                source_text = QLabel(f"{source}")
                source_text.setFont(QFont("Garamond", 10, QFont.Bold))
                source_text.setStyleSheet("color: silver; margin-top: 0px; margin-bottom: 0px; padding-top: 0px; padding-bottom: 0px; border-width: 0px; ")
                source_text.setWordWrap(True)
                source_text.setTextInteractionFlags(Qt.TextSelectableByMouse) # Allow selection (and copy and paste) of text
                #source_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred) # DO NOT USE - This is bugged in combo with word wrap, if used on both texts text height calculation is massive 

                info_text = QLabel(f"{info}")
                info_text.setFont(QFont("Garamond", 10, QFont.Bold))
                info_text.setStyleSheet("color: #D4A45A; margin-top: 10px; margin-bottom: 10px; ")
                info_text.setWordWrap(True)
                info_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
                #info_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred) # Bugged

                # Adding a box underneath them to clearly indicate seperate responses at a glance
                response_box = QFrame()
                response_box.setObjectName("responseBox")  # Identifier, otherwise qframe css applies to every single qframe in the app 
                response_box.setStyleSheet("""
                    QFrame#responseBox {
                        background-color: rgba(0, 0, 0, 100); /* black */
                        border-radius: 14px;
                        border: 2px solid rgba(255, 255, 255, 50);  /* white */
                    }
                    QLabel#responseBox {
                        background: transparent; /* so we can see the qframe */
                    }
                """)
                each_response_container = QVBoxLayout(response_box) # Container for each response (with the frame)

                # Adding the text 
                each_response_container.addWidget(source_text)
                each_response_container.addWidget(info_text)

                #response_box.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding) # Bugged: Not expected behaviour, does not expand vertically
                #response_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) # Bugged: Not have expected behaviour, expands vertically instead
                self.layout_response.addWidget(response_box)

            #Scroll Area Properties

            #self.layout_response.addStretch() # Fixes wordwrap vertical height issues, but doesnt recalc scroll area

            self.scroll.setWidget(self.widget_response) # Add scrolling for the whole response

        else: # Error message if they didn't put anything in the text box
            QMessageBox.information(self, 'Empty Question', "Oh no! \nLooks like you haven't asked a question yet. \nPlease type your question in the input box first.")
            
    def resizeEvent(self, event): # If window is resized
        self.background.setGeometry(self.rect()) # Resize background
        super().resizeEvent(event) # Call normal resize event

    def clear_content(self, layout): # Removes the previous question's responses
        while layout.count(): # If there are widgets/other items in the layout
            item = layout.takeAt(0) # The first item is taken out of the layout and assigned to the variable 'item'
            if item.widget(): # If it's a widget
                item.widget().deleteLater() # Delete during next event loop

class StarryBackground(QWidget):
    """
    Creates an animated night sky background (with twinkling stars).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stars = [self.generate_star() for _ in range(250)] # Generate random position, brightness, change for each star (250 stars)
        self.shooting_stars = []

        self.shooting_star_timer = 0
        self.star_timer = QTimer()
        self.star_timer.timeout.connect(self.update_stars) # Twinkle
        self.star_timer.start(80) # Every 80 milliseconds
        self.last_time = time.time()

    def generate_star(self): 
        return {
            "pos": QPointF(random.randint(0, 1920), random.randint(0, 1920)), # Randomly position the stars
            "brightness": random.randint(100, 255), # Random brightness
            "change": random.choice([-10, 10]) # Random change in brightness
        }
    
    def generate_shooting_star(self):
        start_pos = QPointF(random.randint(0, 1920), random.randint(0, 1920)) # Generate random start position
        direction_deg = random.choice([-30, 150])  # Pick a random direction to shoot in
        direction_rad = math.radians(direction_deg) 
        speed = random.uniform(50, 300)  # Set speed in pixels per second

        return {
        "pos": start_pos,
        "velocity": QPointF(math.cos(direction_rad) * speed, math.sin(direction_rad) * speed),
        "brightness": 255,
        "lifetime": random.uniform(1.8, 4.5),  # seconds (of existance)
        "age": 0.0,
        "trail": []  # for tail effect
    }

    def update_stars(self): # Called every 80 ms to update each star
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        # Update static stars
        for star in self.stars: # For each star
            star["brightness"] += star["change"] # Change the brightness (randomly brighter or dimmer)
            if star["brightness"] > 255 or star["brightness"] < 100: # If it is out of range
                star["change"] *= -1 # Reverse the change direction (effect is stars go from 100-255 and back)

        # Update shooting stars
        for star in self.shooting_stars[:]:
            star["age"] += dt
            star["pos"] += star["velocity"] * dt # Adding distance to calculate new position
            star["trail"].append(QPointF(star["pos"])) # 'Painting' trail of old position
            if len(star["trail"]) > 20:
                star["trail"].pop(0) # Removing the 21st oldest position from the trail

            # Fade out near end of life
            if star["age"] > star["lifetime"] * 0.7:
                star["brightness"] = max(0, int(255 * (1 - (star["age"] - star["lifetime"]*0.7) / (star["lifetime"]*0.3)))) # Approaches 0

            if star["age"] > star["lifetime"] or not self.rect().contains(star["pos"].toPoint(), True): # If old or it goes off the screen
                self.shooting_stars.remove(star) 

        # Randomly spawn new shooting star
        self.shooting_star_timer += dt
        if self.shooting_star_timer > random.uniform(3, 8):  # Every 3–8 seconds
            self.shooting_stars.append(self.generate_shooting_star())
            self.shooting_star_timer = 0

        self.update() # Refreshes the qwidget

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(10, 5, 25))  # Navy blue background

        for star in self.stars:
            colour = QColor(255, 255, 200, star["brightness"]) # Star brightness = transparency of the yellow colour
            painter.setPen(colour) # Sets the paint as a width 1 line with the colour above
            painter.drawPoint(int(star["pos"].x()), int(star["pos"].y())) # Just dots this at the x and y positions already generated

        # Trail (shooting stars)
        for star in self.shooting_stars:
            if not star["trail"]: # If there isn't a trail yet
                continue # Move to the next star

            # Draw trail (fading backward)
            for i, point in enumerate(star["trail"]):
                alpha = int(star["brightness"] * (i + 1) / len(star["trail"]) * 0.6) # Transparency value, later points have a larger i and are brighter etc
                if alpha <= 0: # Don't draw the point if it's 0 or less transparency
                    continue
                color = QColor(200, 220, 255, alpha) # Set colour of trail point
                painter.setPen(QPen(color, 1)) # Set size of trail point
                painter.drawPoint(int(point.x()), int(point.y())) # Draw the point

            # Bright head
            head_color = QColor(255, 255, 255, star["brightness"])
            painter.setPen(QPen(head_color, 3))
            painter.drawPoint(int(star["pos"].x()), int(star["pos"].y()))