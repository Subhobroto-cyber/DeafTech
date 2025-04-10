import pickle
import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from gtts import gTTS
from gtts.lang import tts_langs
import os
from googletrans import Translator
import pygame  # Import pygame for audio playback
import requests

# Initialize pygame mixer
pygame.mixer.init()

# Load the trained model
with open('C:/Users/Subhobroto Sasmal/Downloads/DeafTech---SignLanguageDetector-main/DeafTech---SignLanguageDetector-main/Backend/model.p', 'rb') as f:
    model_dict = pickle.load(f)
model = model_dict['model']

# Initialize webcam
cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Update the labels dictionary as per your classes
labels_dict = {str(i): str(i) for i in range(10)}  # 0-9
labels_dict.update({chr(i): chr(i) for i in range(65, 91)})  # A-Z

recognized_text = ""
gesture_detected = False
last_character = ""
current_character = ""

# Initialize translator
translator = Translator()
translated_text = ""  # Store translated text

# Initialize suggestions list
suggestions = []  # Example suggestions
suggestion_buttons = []

# Function to speak recognized text or translated text
def speak_text():
    global translated_text, recognized_text
    text_to_speak = translated_text if translated_text else recognized_text
    lang = 'en' if not translated_text else translated_lang_code  # Use translated language code

    if text_to_speak:
        file_name = "temp.mp3"
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

            if os.path.exists(file_name):
                os.remove(file_name)

            tts = gTTS(text=text_to_speak, lang=lang)
            tts.save(file_name)

            pygame.mixer.music.load(file_name)
            pygame.mixer.music.play()

        except Exception as e:
            print(f"Error in speak_text: {e}")

# Function to translate recognized text
def translate_text():
    global translated_text, translated_lang_code
    languages = {
        'Hindi': 'hi',
        'Bengali': 'bn',
        'Telugu': 'te',
        'Marathi': 'mr',
        'Tamil': 'ta',
        'Gujarati': 'gu',
        'Malayalam': 'ml',
        'Kannada': 'kn',
        'Punjabi': 'pa',
        'Urdu': 'ur'
    }

    def on_language_select(lang_code):
        global translated_text, translated_lang_code
        try:
            translated = translator.translate(recognized_text, dest=lang_code)
            translated_text = translated.text
            translated_lang_code = lang_code  # Store the selected language code
            translator_label.config(text=f"Translated: {translated_text}")
            speak_text()  # Speak translated text
        except Exception as e:
            print(f"Translation Error: {e}")
            translated_text = ""
            translated_lang_code = ''
        finally:
            lang_window.destroy()

    lang_window = tk.Toplevel(root)
    lang_window.title("Select Language")
    lang_window.geometry("300x470")

    tk.Label(lang_window, text="Select a language:", font=language_font).pack(pady=10)

    for lang_name, lang_code in languages.items():
        tk.Button(lang_window, text=lang_name, command=lambda code=lang_code: on_language_select(code), font=language_font).pack(pady=5)

# Create the main window
root = tk.Tk()
root.title("Sign Language Recognition")
root.configure(bg='#f7f7f7')  # Change background to #f7f7f7
root.attributes('-fullscreen', True)

# Define fonts
heading_font = ('Helvetica', 30, 'bold')
text_font = ('Helvetica', 24)
translator_font = ('Helvetica', 20)
button_font = ('Helvetica', 16)
language_font = ('Helvetica', 12)

# Create a frame to add a border effect
border_frame = ttk.Frame(root, padding=20)
border_frame.pack(fill=tk.BOTH, expand=True)

# Create a heading
heading = tk.Label(border_frame, text="Sign Language to Text & Speech Translator-DeafTech©", bg=None, fg='#000000', font=heading_font)
heading.pack(pady=20)

# Create a frame inside the border frame for content
content_frame = tk.Frame(border_frame, bg='#f7f7f7')
content_frame.pack(fill=tk.BOTH, expand=True)

# Create and place the widgets
text_display = tk.Label(content_frame, text="Sentence: ", bg='#f7f7f7', fg='#000000', font=text_font)
text_display.pack(pady=20, anchor='w', padx=20)

# Translator label
translator_label = tk.Label(content_frame, text="", bg='#f7f7f7', fg='#333333', font=translator_font)
translator_label.pack(pady=10, anchor='w', padx=20)

# Button functions
def on_next():
    global recognized_text, current_character
    if current_character:
        recognized_text += current_character
        current_character = ""
    display_text = f"Sentence: {recognized_text}"
    text_display.config(text=display_text)
    clear_suggestions()  # Hide suggestions before updating them
    show_suggestions()  # Regenerate suggestions based on updated text

def on_space():
    global recognized_text
    recognized_text += ' '
    display_text = f"Sentence: {recognized_text}"
    text_display.config(text=display_text)
    clear_suggestions()  # Hide suggestions before updating them
    # show_suggestions()  # Regenerate suggestions based on updated text

def on_backspace():
    global recognized_text
    recognized_text = recognized_text[:-1]
    display_text = f"Sentence: {recognized_text}"
    text_display.config(text=display_text)
    clear_suggestions()  # Hide suggestions before updating them
    show_suggestions()  # Regenerate suggestions based on updated text

def on_clear():
    global recognized_text, translated_text
    recognized_text = ""
    translated_text = ""
    display_text = "Sentence: "
    text_display.config(text=display_text)
    translator_label.config(text="")
    clear_suggestions()  # Hide suggestions since the text is cleared

# Similarly, for other button functions like on_translate or on_quit, add hide_suggestions() and show_suggestions() if needed.

def select_suggestion(index):
    global recognized_text
    # Append the selected suggestion to the recognized text
    recognized_text += suggestion_buttons[index].cget('text')[len(recognized_text):]
    text_display.config(text=f"Sentence: {recognized_text}")
    clear_suggestions()  # Hide old suggestions
    show_suggestions()  # Regenerate suggestions based on updated text

def on_quit():
    pygame.mixer.music.stop()
    root.quit()

def on_speak():
    speak_text()
    clear_suggestions()  # Hide old suggestions

def on_clear():
    global recognized_text, translated_text
    recognized_text = ""
    translated_text = ""
    display_text = "Sentence: "
    text_display.config(text=display_text)
    translator_label.config(text="")
    clear_suggestions()

def on_translate():
    translate_text()
    clear_suggestions()  # Hide old suggestions


# Intellisense suggestion functionality
def clear_suggestions():
    for button in suggestion_buttons:
        button.config(text="", state=tk.DISABLED)

# Intellisense suggestion functionality
# Function to get word suggestions
def get_word_suggestions(word):
    # Example static list of suggestions for demonstration purposes
    dynamic_suggestions = ['APPLE', 'ANTELOPE', 'AARDVARK', 'ALBATROSS', 'AXE', 'ABYSS', 'ACRONYM', 'ACERBIC', 'ACROBAT', 'ACUMEN', 
                'ACOUSTIC', 'AGILE', 'ALTITUDE', 'AMBITION', 'AMICABLE', 'AMPHIBIAN', 'ANCHOR', 'ANCIENT', 'ANGER', 'ANIMAL', 
                'ANTIQUE', 'ANXIETY', 'APATHY', 'APEX', 'APOLOGY', 'APPARATUS', 'APPLE', 'APPRECIATE', 'APTITUDE', 'AQUARIUM', 
                'ARBITRARY', 'ARDENT', 'ARENA', 'ARGUMENT', 'ARID', 'ARITHMETIC', 'ARMOR', 'ARRIVE', 'ARROW', 'ART', 
                'ARTICULATE', 'ARTIFACT', 'ARTIFICIAL', 'ARTIST', 'ASCEND', 'ASPEN', 'ASPECT', 'ASSAULT', 'ASSERTIVE', 'ASSIGN', 
                'ASSIST', 'ASSOCIATE', 'ASSUME', 'ASTEROID', 'ASTUTE', 'ASYLUM', 'ATHLETE', 'ATLAS', 'ATMOSPHERE', 'ATOM', 
                'ATROCIOUS', 'ATTACH', 'ATTEMPT', 'ATTENTIVE', 'ATTITUDE', 'ATTORNEY', 'ATTRACT', 'AUCTION', 'AUDIENCE', 'AURA', 
                'AUTHOR', 'AUTHORITY', 'AUTUMN', 'AVAILABLE', 'AVENGE', 'AVENUE', 'AVERAGE', 'AVID', 'AVOID', 'AWAKE', 
                'AWARD', 'AWARE', 'AWESOME', 'AWKWARD', 'AXIOM', 'AXIS', 'AZURE', 'AID', 'AIM', 'ALARM', 
                'ALBUM', 'ALLEGE', 'ALLOCATE', 'ALLOW', 'ALTER', 'AMASS', 'AMAZE', 'AMBER', 'AMBUSH', 'AMEND', 
                'AMPLE', 'AMPLIFY', 'AMUSE', 'ANIMATE', 'ANNEX', 'ANNOUNCE', 'ANNOY', 'ANNUAL', 'ANSWER', 'ANTAGONIZE', 
                'ANTHEM', 'ANTICIPATE', 'ANTIDOTE', 'ANTIQUE', 'APEX', 'APPLAUD', 'APPLIANCE', 'APPLY', 'APPOINT', 'APPRAISE', 
                'APPROACH', 'APPROVE', 'APPROXIMATE', 'AQUATIC', 'ARBITRATE', 'ARBOR', 'ARCADE', 'ARCHER', 'ARCHIVE', 'ARCTIC', 
                'ARGUE', 'ARISE', 'ARMED', 'ARRANGE', 'ARRAY', 'ARREST', 'ARRIVE', 'ARROW', 'ARSON', 'ARTFUL', 
                'ARTICLE', 'ARTIFICIAL', 'ASCEND', 'ASCERTAIN', 'ASK', 'ASLEEP', 'ASPECT', 'ASSEMBLE', 'ASSERT', 'ASSESS', 
                'ASSIGN', 'ASSIST', 'ASSOCIATE', 'ASSUME', 'ASSURE', 'ASTOUND', 'ASTRAL', 'ASTRAY', 'ASYLUM', 'ATHLETIC', 
                'ATMOSPHERIC', 'ATOMIZE', 'ATTACH', 'ATTACK', 'ATTAIN', 'ATTEMPT', 'ATTEND', 'ATTEST', 'ATTRACT', 'ATTRIBUTE', 
                'AUCTIONEER', 'AUGMENT', 'AURORA', 'AUSPICIOUS', 'AUTHENTIC', 'AUTHORITATIVE', 'AUTOMATE', 'AUTONOMY', 'AVAIL', 'AVENGE', 
                'AVERAGE', 'AVERSION', 'AVOID', 'AWAIT', 'AWAKEN', 'AWARD', 'AWE', 'AWKWARD', 'AXIOM', 'AZURE', 
                'ABANDON', 'ABILITY', 'ABLE', 'ABOUT', 'ABOVE', 'ABSENCE', 'ABSOLUTE', 'ABSOLUTELY', 'ABSORB', 'ABSTRACT', 
                'ABUNDANCE', 'ACADEMIC', 'ACCEPT', 'ACCESS', 'ACCESSIBLE', 'ACCIDENT', 'ACCOMPANY', 'ACCOMPLISH', 'ACCORD', 'ACCOUNT', 
                'ACCUMULATE', 'ACCURATE', 'ACCUSATION', 'ACCUSE', 'ACHIEVE', 'ACHIEVEMENT', 'ACID', 'ACKNOWLEDGE', 'ACQUAINTANCE', 'ACQUIRE', 
                'ACROSS', 'ACT', 'ACTION', 'ACTIVE', 'ACTIVITY', 'ACTOR', 'ACTRESS', 'ACTUAL', 'ACTUALLY', 'ADAPT', 
                'ADD', 'ADDITION', 'ADDITIONAL', 'ADDRESS', 'ADEQUATE', 'ADJUST', 'ADMINISTER', 'ADMINISTRATION', 'ADMIRE', 'ADMIT', 
                'ADOPT', 'ADORE', 'ADVANCE', 'ADVANTAGE', 'ADVENTURE', 'ADVERB', 'ADVERTISE', 'ADVICE', 'ADVISE', 'ADVISOR', 
                'ADVOCATE', 'AESTHETIC', 'AFFECT', 'AFFECTION', 'AFFIRM', 'AFFORD', 'AFRAID', 'AFTER', 'AFTERNOON', 'AGAIN', 
                'AGAINST', 'AGE', 'AGENCY', 'AGENDA', 'AGENT', 'AGGRESSIVE', 'AGREE', 'AGREEMENT', 'AHEAD', 'AID', 
                'AIM', 'AIR', 'AIRPLANE', 'AIRPORT', 'ALARM', 'ALBEIT', 'ALERT', 'ALIEN', 'ALIGN', 'ALIKE', 
                'ALIVE', 'ALL', 'ALLEGE', 'ALLEGIANCE', 'ALLOCATE', 'ALLOW', 'ALLY', 'ALMOST', 'ALONE', 'ALONG', 
                'ALREADY', 'ALSO', 'ALTER', 'ALTERNATIVE', 'ALTHOUGH', 'ALTITUDE', 'ALTOGETHER', 'ALWAYS', 'AMATEUR', 'AMAZING', 
                'AMBASSADOR', 'AMBITION', 'AMBITIOUS', 'AMENDMENT', 'AMOUNT', 'AMPLE', 'AMUSE', 'ANALYSIS', 'ANALYST', 'ANALYZE', 
                'ANCESTOR', 'ANCHOR', 'ANCIENT', 'ANGER', 'ANGLE', 'ANGRY', 'ANIMAL', 'ANIMATE', 'ANNIVERSARY', 'ANNOUNCE', 
                'ANNUAL', 'ANSWER', 'ANTARCTICA', 'ANTICIPATE', 'ANXIETY', 'ANXIOUS', 'ANY', 'ANYBODY', 'ANYMORE', 'ANYONE', 
                'ANYTHING', 'ANYWAY', 'ANYWHERE', 'APART', 'APARTMENT', 'APOLOGY', 'APPARENT', 'APPARENTLY', 'APPEAR', 'APPEARANCE', 
                'APPETITE', 'APPLE', 'APPLIANCE', 'APPLICATION', 'APPLY', 'APPOINT', 'APPOINTMENT', 'APPRECIATE', 'APPRECIATION', 'APPROACH', 
                'APPROPRIATE', 'APPROVAL', 'APPROVE', 'APPROXIMATELY', 'APRIL', 'AREA', 'ARGUE', 'ARGUMENT', 'ARISE', 'ARM', 
                'ARMED', 'ARMY', 'AROUND', 'ARRANGE', 'ARRANGEMENT', 'ARREST', 'ARRIVE', 'ARROW', 'ART', 'ARTICLE', 
                'ARTIST', 'ARTISTIC', 'AS', 'ASH', 'ASIDE', 'ASK', 'ASLEEP', 'ASPECT', 'ASSAULT', 'ASSEMBLE', 
                'ASSERT', 'ASSESS', 'ASSESSMENT', 'ASSIGN', 'ASSIGNMENT', 'ASSIST', 'ASSISTANCE', 'ASSISTANT', 'ASSOCIATE', 'ASSOCIATION', 
                'ASSUME', 'ASSUMPTION', 'ASSURE', 'AT', 'ATHLETE', 'ATHLETIC', 'ATMOSPHERE', 'ATTACH', 'ATTACK', 'ATTEMPT', 
                'ATTEND', 'ATTENTION', 'ATTITUDE', 'ATTORNEY', 'ATTRACT', 'ATTRACTION', 'ATTRACTIVE', 'ATTRIBUTE', 'AUDIENCE', 'AUTHOR', 
                'AUTHORITY', 'AUTO', 'AUTOMATIC', 'AUTOMATICALLY', 'AUTUMN', 'AVAILABLE', 'AVERAGE', 'AVOID', 'AWARD', 'AWARE', 
                'AWAY', 'AWFUL', 'AWKWARD', 'ABANDONMENT', 'ABBREVIATE', 'ABDOMEN', 'ABDUCTION', 'ABERRATION', 'ABIDE', 'ABILITY', 
                'ABLE-BODIED', 'ABNORMAL', 'ABOARD', 'ABOMINABLE', 'ABORT', 'ABOUND', 'ABOUT-FACE', 'ABOVE-AVERAGE', 'ABRASION', 'ABRUPT',
                'BABY', 'BACK', 'BAD', 'BALANCE', 'BALL', 'BANK', 'BAR', 'BASIC', 'BATH', 'BATTLE',
                'BE', 'BEACH', 'BEAR', 'BEAUTIFUL', 'BECOME', 'BED', 'BEE', 'BEER', 'BEFORE', 'BEGIN',
                'BEHIND', 'BELIEVE', 'BELL', 'BELONG', 'BELOW', 'BENCH', 'BEND', 'BENEATH', 'BENEFIT', 'BEST',
                'BET', 'BETWEEN', 'BEYOND', 'BICYCLE', 'BIG', 'BILL', 'BIND', 'BIRD', 'BIRTH', 'BITE',
                'BLACK', 'BLAME', 'BLANK', 'BLAST', 'BLESS', 'BLIND', 'BLOCK', 'BLOOD', 'BLOW', 'BLUE',
                'BOARD', 'BOAT', 'BODY', 'BOLD', 'BOMB', 'BOND', 'BONE', 'BOOK', 'BOOT', 'BORDER',
                'BORN', 'BORROW', 'BOSS', 'BOTH', 'BOTTLE', 'BOTTOM', 'BOUNCE', 'BOUND', 'BOWL', 'BOX',
                'BOY', 'BRAIN', 'BRANCH', 'BRAVE', 'BREAD', 'BREAK', 'BREATH', 'BRICK', 'BRIDGE', 'BRIEF',
                'BRIGHT', 'BRING', 'BROAD', 'BROKE', 'BROKEN', 'BROTHER', 'BROWN', 'BRUSH', 'BUBBLE', 'BUCKET',
                'BUDDY', 'BUILD', 'BUILT', 'BULK', 'BULLET', 'BUNCH', 'BURDEN', 'BURN', 'BURST', 'BUS',
                'BUSH', 'BUSINESS', 'BUST', 'BUSY', 'BUT', 'BUTTER', 'BUTTON', 'BUY', 'BUZZ', 'BY',
                'BABBLE', 'BABYSIT', 'BACKBONE', 'BACKDROP', 'BACKFIRE', 'BACKGROUND', 'BACKPACK', 'BACKWARD', 'BACKYARD', 'BACTERIA',
                'BADGE', 'BADLY', 'BAFFLE', 'BAG', 'BAIL', 'BAIT', 'BAKE', 'BALCONY', 'BALD', 'BALLOON',
                'BALLOT', 'BAND', 'BANDAGE', 'BANG', 'BANKRUPT', 'BANQUET', 'BAPTISM', 'BARBECUE', 'BARBER', 'BARE',
                'BARGAIN', 'BARK', 'BARN', 'BARREL', 'BASE', 'BASEBALL', 'BASEMENT', 'BASICALLY', 'BASIN', 'BASKET',
                'BASS', 'BAT', 'BATCH', 'BATHE', 'BATTERY', 'BATTLEFIELD', 'BAY', 'BEACON', 'BEAD', 'BEAM',
                'BEAN', 'BEARD', 'BEAST', 'BEAT', 'BEATING', 'BEAUTY', 'BECOMING', 'BEDROOM', 'BEEF', 'BEET',
                'BEFOREHAND', 'BEG', 'BEGGAR', 'BEGINNER', 'BEGINNING', 'BEGUN', 'BEHALF', 'BEING', 'BELIEF', 'BELIEVER',
                'BELLY', 'BELT', 'BENCHMARK', 'BENEFACTOR', 'BENEFICIAL', 'BENEVOLENT', 'BENT', 'BERRY', 'BETRAY', 'BETTER',
                'BEVERAGE', 'BEYOND', 'BIBLE', 'BICYCLE', 'BIGGER', 'BIGGEST', 'BILLION', 'BINDING', 'BIOGRAPHY', 'BIOLOGY',
                'BIRTHDAY', 'BISCUIT', 'BISHOP', 'BITE', 'BITTER', 'BLANKET', 'BLEND', 'BLESSING', 'BLINDLY', 'BLINK',
                'BLISTER', 'BLOAT', 'BLOCKADE', 'BLOG', 'BLOODSTREAM', 'BLOOM', 'BLOSSOM', 'BLOWN', 'BLUFF', 'BLUR',
                'BLURRY', 'BOARDER', 'BOAST', 'BOATLOAD', 'BOATING', 'BODYGUARD', 'BOIL', 'BOLDLY', 'BOLT', 'BONUS',
                'BOOKING', 'BOOM', 'BOOTH', 'BORDERLINE', 'BORED', 'BORING', 'BORN', 'BORROWER', 'BOSSY', 'BOTHER',
                'BOTTLED', 'BOUQUET', 'BOUT', 'BOW', 'BOWEL', 'BOWL', 'BOXER', 'BOYCOTT', 'BOYHOOD', 'BRACE',
                'BRACELET', 'BRAG', 'BRAINSTORM', 'BRAKE', 'BRAND', 'BRANDED', 'BRANDISH', 'BRAVERY', 'BREACH', 'BREAKAGE',
                'BREAKDOWN', 'BREAKFAST', 'BREED', 'BREEZE', 'BREW', 'BRIBE', 'BRICKLAYER', 'BRIEFCASE', 'BRILLIANT', 'BRIM',
                'BRINK', 'BRISK', 'BROADCAST', 'BROADER', 'BROCHURE', 'BROKER', 'BRONZE', 'BROOD', 'BROOK', 'BROOM',
                'BROW', 'BROWSE', 'BRUISE', 'BRUNCH', 'BRUTAL', 'BUBBLEGUM', 'BUCKETFUL', 'BUDGET', 'BUFFALO', 'BUFFET',
                'BUG', 'BUILDING', 'BULB', 'BULGE', 'BULKHEAD', 'BULL', 'BULLDOZER', 'BULLETIN', 'BULLFIGHT', 'BULLY',
                'BUMBLE', 'BUMP', 'BUNCHES', 'BUNDLE''BUNGALOW','CAB', 'CABBAGE', 'CABIN', 'CABINET', 'CABLE', 'CACHE', 'CACKLE', 'CACTUS', 'CAGE', 
                'CAKE', 'CALAMITY', 'CALCIUM', 'CALCULATE', 'CALENDAR', 'CALF', 'CALL', 'CALLER', 'CALM',
                'CAMEL', 'CAMEO', 'CAMERA', 'CAMP', 'CAMPAIGN', 'CAMPER', 'CAMPSITE', 'CAMPUS', 'CAN', 
                'CANAL', 'CANCEL', 'CANCER', 'CANDID', 'CANDIDATE', 'CANDLE', 'CANDY', 'CANINE', 
                'CANISTER', 'CANNON', 'CANNOT', 'CANOE', 'CANOPY', 'CANTEEN', 'CANVAS', 'CAP', 
                'CAPACITY', 'CAPE', 'CAPITAL', 'CAPITALISM', 'CAPITALIST', 'CAPITOL','TREE', 'CAPRICORN',
                'CAPSULE', 'CAPTAIN', 'CAPTION', 'CAPTURE', 'CAR', 'CARBON', 'CARCASS', 'CARD', 
                'CARDINAL', 'CARE', 'CAREER', 'CAREFUL', 'CARESS', 'CARGO', 'CARIBOU', 'CARING',
                'CARNAGE', 'CARNATION', 'CARNIVAL', 'CAROL', 'CARPENTER', 'CARPET', 'CARRIAGE', 'CARRIER', 'CARROT', 
                'CARRY', 'CART', 'CARTOON', 'CARVE', 'CASE', 'CASH', 'CASHEW', 'CASKET', 'CAST', 'CASTLE', 'CASUAL', 
                'CASUALTY', 'CAT', 'CATCH', 'CATER', 'CATHEDRAL', 'CATTLE', 'CAULIFLOWER', 'CAUSE', 'CAUTION', 'CAVE', 
                'CEASE', 'CEILING', 'CELEBRATE', 'CELEBRATION', 'CELEBRITY', 'CELL', 'CELLAR', 'CELLO', 'CEMENT', 'CEMETERY', 'CENSUS', 
                'CENTER', 'CENTRAL', 'CENTRE', 'CENTURY', 'CERAMIC', 'CEREMONY', 'CERTAIN', 'CERTAINTY', 'CERTIFICATE', 'CHAIN', 'CHAIR', 'CHAIRMAN', 
                'CHAIRPERSON', 'CHAIRWOMAN', 'CHALK', 'CHALLENGE', 'CHAMBER', 'CHAMPION', 'CHANCE', 'CHANGE', 'CHANNEL', 'CHAOS', 'CHAPEL', 'CHAPTER', 'CHARACTER', 
                'CHARACTERISTIC', 'CHARCOAL', 'CHARGE', 'CHARITY', 'CHARM', 'CHART', 'CHASE', 'CHASM', 'CHAT', 'CHEAP', 'CHEAT', 'CHECK', 'CHECKLIST', 'CHEEK', 
                'CHEER', 'CHEERFUL', 'CHEESE', 'CHEETAH', 'CHEF', 'CHEMICAL', 'CHEMISTRY', 'CHERRY', 'CHESS', 'CHEST', 'CHESTNUT', 'CHEW', 'CHICK', 'CHICKEN', 
                'CHIEF', 'CHILD', 'CHILDHOOD', 'CHILDISH', 'CHILL', 'CHIMNEY', 'CHIN', 'CHINA', 'CHINESE', 'CHIP', 'CHOCOLATE', 'CHOICE', 'CHOOSE', 'CHOP', 
                'CHOPPER', 'CHORUS', 'CHRISTMAS', 'CHRONIC', 'CHUNK', 'CHURCH', 'CIDER', 'CIGAR', 'CIGARETTE', 'CINEMA', 'CIRCLE', 'CIRCULAR', 'CIRCULATE', 'CIRCULATION', 
                'CIRCUMFERENCE', 'CIRCUMSTANCE', 'CIRCUS', 'CITATION', 'CITE', 'CITIZEN', 'CITY', 'CIVIC', 'CIVIL', 'CIVILIZATION', 'CLAIM', 'CLAM', 'CLAMP', 'CLARIFY', 'CLASH', 
                'CLASP', 'CLASS', 'CLASSIC', 'CLASSICAL', 'CLASSIFICATION', 'CLASSIFY', 'CLASSMATE', 'CLASSROOM', 'CLAUSE', 'CLAW', 'CLAY', 'CLEAN', 'CLEANER', 'CLEANING', 
                'CLEAR', 'CLEARANCE', 'CLEARLY', 'CLERGY', 'CLERK', 'CLEVELAND', 'CLICK', 'CLIENT', 'CLIFF', 'CLIMATE', 'CLIMB', 'CLINIC', 'CLINICAL', 'CLIP', 'CLOCK', 'CLOG', 
                'CLOSE', 'CLOSER', 'CLOSET', 'CLOSURE', 'CLOTH', 'CLOTHE', 'CLOTHES', 'CLOTHING', 'CLOUD', 'CLOUDY', 'CLOVER', 'CLUB', 'CLUE', 'CLUMSY', 'CLUSTER', 'COACH', 
                'COAL', 'COAST', 'COASTER', 'COAT', 'COBBLE', 'COBRA', 'COCOA', 'COCONUT', 'CODE', 'COFFEE', 'COIL', 'COIN', 'COLD', 'COLLAPSE', 'COLLAR', 'COLLEAGUE', 'COLLECT', 
                'COLLECTION', 'COLLECTIVE', 'COLLECTOR', 'COLLEGE', 'COLLIDE', 'COLLISION', 'COLON', 'COLONY', 'COLOR', 'COLOSSAL', 'COLUMN', 'COMA', 'COMBAT', 'COMBINATION',
                'COMBINE', 'COMBO', 'COME', 'COMEDY', 'COMET', 'COMFORT', 'COMFORTABLE', 'COMMAND', 'COMMANDER', 'COMMENCE', 'COMMEND', 'COMMENT', 'COMMENTARY', 'COMMENTATOR', 
                'COMMERCE', 'COMMERCIAL', 'COMMISSION', 'COMMIT', 'COMMITMENT', 'COMMITTEE', 'COMMON', 'COMMUNICATE', 'COMMUNICATION', 'COMMUNISM', 'COMMUNIST', 'COMMUNITY', 
                'COMPACT', 'COMPANION', 'COMPANY', 'COMPARE', 'COMPARISON', 'COMPASS', 'COMPASSION', 'COMPATIBLE', 'COMPEL', 'COMPENSATE', 'COMPENSATION', 'COMPETE', 'COMPETITION', 
                'COMPETITIVE', 'COMPETITOR', 'COMPILE', 'COMPLAIN', 'COMPLAINT', 'COMPLETE', 'COMPLETELY', 'COMPLETION', 'COMPLEX', 'COMPLEXITY', 'COMPLIANCE', 'COMPLIANT', 'COMPLICATE', 
                'COMPLICATED', 'COMPLICATION', 'COMPLIMENT', 'COMPONENT', 'COMPOSE', 'COMPOSER', 'COMPOSITE', 'COMPOSITION', 'COMPOST', 'COMPOUND', 'COMPREHEND', 'COMPREHENSION', 'COMPREHENSIVE', 
                'COMPRESS', 'COMPRISE', 'COMPROMISE', 'COMPUTE', 'COMPUTER', 'CONCEAL', 'CONCEDE', 'CONCEIT', 'CONCEIVE', 'CONCENTRATE', 'CONCENTRATION', 'CONCEPT', 'CONCEPTION', 'CONCERN', 
                'CONCERNED', 'CONCERT', 'CONCESSION', 'CONCLUDE', 'CONCLUSION', 'CONCRETE', 'CONDITION', 'CONDUCT', 'CONFERENCE', 'CONFESS', 'CONFESSION', 'CONFIDENCE', 'CONFIDENT', 
                'CONFIDENTIAL', 'CONFINE', 'CONFINEMENT', 'CONFIRM', 'CONFIRMATION', 'CONFLICT', 'CONFORM', 'CONFRONT', 'CONFUSE', 'CONFUSION', 'CONGRATULATE', 'CONGRATULATION', 
                'CONGREGATION', 'CONGRESS', 'CONNECT', 'CONNECTION', 'CONQUER', 'CONQUEST', 'CONSCIENCE', 'CONSCIOUS', 'CONSCIOUSNESS', 'CONSENSUS', 'CONSENT', 'CONSEQUENCE', 
                'CONSERVATION', 'CONSERVATIVE', 'CONSERVE', 'CONSIDER', 'CONSIDERABLE', 'CONSIDERATION', 'CONSIST', 'CONSISTENCY', 'CONSISTENT', 'CONSOLE', 'CONSOLIDATE', 
                'CONSONANT', 'CONSPIRACY', 'CONSPIRE', 'CONSTANT', 'CONSTANTLY', 'CONSTELLATION', 'CONSTIPATION', 'CONSTITUTE', 'CONSTITUTION', 'CONSTRAIN', 'CONSTRAINT', 
                'CONSTRUCT', 'CONSTRUCTION', 'CONSULT', 'CONSULTANT', 'CONSUME', 'CONSUMER', 'CONSUMPTION', 'CONTACT', 'CONTAIN', 'CONTAINER', 'CONTEMPLATE', 'CONTEMPLATION', 
                'CONTEMPORARY', 'CONTENDER', 'CONTENT', 'CONTEST', 'CONTEXT', 'CONTINENT', 'CONTINUE', 'CONTINUITY', 'CONTINUOUS', 'CONTRACT', 'CONTRACTION', 'CONTRACTOR', 
                'CONTRADICT', 'CONTRADICTION', 'CONTRARY', 'CONTRAST', 'CONTRIBUTE', 'CONTRIBUTION', 'CONTRIBUTOR', 'CONTROL', 'CONTROVERSIAL', 'CONTROVERSY', 'CONVENIENCE', 
                'CONVENIENT', 'CONVENTION', 'CONVENTIONAL', 'CONVERGE', 'CONVERSATION', 'CONVERSE', 'CONVERSION', 'CONVERT', 'CONVEY', 'CONVICT', 'CONVICTION', 'CONVINCE', 'COOK', 'COOKER',
                'COOKIE', 'COOKING', 'COOL', 'COOP', 'COPE', 'COPPER', 'COPY', 'COPYRIGHT', 'CORAL', 'CORK', 'CORN', 'CORNER', 'CORONER', 'CORPORATE', 'CORPORATION', 'CORRECT', 'CORRECTION',
                'CORRECTLY', 'CORRELATE', 'CORRESPOND', 'CORRESPONDENCE', 'CORRESPONDENT', 'CORRIDOR', 'CORRUPT', 'CORRUPTION', 'COST', 'COSTLY', 'COTTAGE', 'COTTON', 'COUCH', 'COUGH', 'COULD', 
                'COUNCIL', 'COUNSEL', 'COUNSELLOR', 'COUNT', 'COUNTDOWN', 'COUNTER', 'COUNTERACT', 'COUNTERPART', 'COUNTRY', 'COUNTRYMAN', 'COUNTRYSIDE', 'COUNTY', 'COUPLE', 'COURAGE', 'COURSE', 
                'COURT', 'COURTESY', 'COURTROOM', 'COUSIN', 'COVER', 'COVERAGE', 'COW', 'COWARD', 'COWBOY', 'CRAB', 'CRACK', 'CRACKER', 'CRAFT', 'CRAFTSMAN', 'CRANE', 'CRASH', 'CRATE', 'CRAWL', 
                'CRAYON', 'CRAZY', 'CREAM', 'CREATE', 'CREATION', 'CREATIVE', 'CREATOR', 'CREATURE', 'CREDIT', 'CREEK', 'CREEP', 'CREEPY', 'CREST', 'CREW', 'CRIB', 'CRICKET', 'CRIME', 'CRIMINAL',
                'CRIMSON', 'CRISIS', 'CRISP', 'CRITIC', 'CRITICAL', 'CRITICISM', 'CRITICIZE', 'CROCODILE', 'CROOK', 'CROP', 'CROSS', 'CROSSING', 'CROUCH', 'CROWD', 'CROWN', 'CRUCIAL', 'CRUEL', 
                'CRUISE', 'CRUMB', 'CRUMBLE', 'CRUNCH', 'CRUSADE', 'CRUSH', 'CRY', 'CRYSTAL', 'CUB', 'CUBE', 'CUBIC', 'CUBICLE', 'CUCUMBER', 'CULTIVATE', 'CULTURE', 'CUP', 'CUPBOARD', 'CUPCAKE',
                'CURB', 'CURE', 'CURIOSITY', 'CURIOUS', 'CURL', 'CURRENT', 'CURRICULUM', 'CURRY', 'CURSE', 'CURTAIN', 'CURVE', 'CUSHION', 'CUSTOM', 'CUSTOMARY', 'CUSTOMER', 'CUT', 'CUTE', 'CUTTER', 
                'CUTTING', 'CYBER', 'CYCLE', 'CYCLONE','CYLINDER','DENTIST', 'DENY', 'DEPART', 'DEPARTMENT', 'DEPARTURE', 'DEPEND', 'DEPENDENCE', 'DEPENDENT', 'DEPICT', 'DEPLOY', 'DEPOSIT', 'DEPRESS',
                'DEPRESSED', 'DEPRESSION', 'DEPRIVE', 'DEPTH', 'DEPUTY', 'DERIVE', 'DESCEND', 'DESCRIBE', 'DESCRIPTION', 'DESERT', 'DESERVE', 'DESIGN', 'DESIGNER', 'DESIRABLE', 'DESIRE', 'DESK', 'DESPAIR', 
                'DESPERATE', 'DESPITE', 'DESTINATION', 'DESTINY', 'DESTROY', 'DESTRUCTION', 'DETAILED', 'DETAIL', 'DETECT', 'DETECTION', 'DETECTIVE', 'DETERMINE', 'DETERMINED', 'DEVELOP', 'DEVELOPMENT', 
                'DEVICE', 'DEVIL', 'DEVOTE', 'DEVOTED', 'DIALOGUE', 'DIAMETER', 'DIAMOND', 'DIARY', 'DICE', 'DICTIONARY', 'DIE', 'DIET', 'DIFFER', 'DIFFERENCE', 'DIFFERENT', 'DIFFICULT', 'DIFFICULTY',
                'DIG', 'DIGITAL', 'DIGNITY', 'DILEMMA', 'DIM', 'DIMENSION', 'DINE', 'DINER', 'DINGY', 'DINNER', 'DIP', 'DIRECT', 'DIRECTION', 'DIRECTLY', 'DIRECTOR', 'DIRT', 'DIRTY', 'DISABLE', 
                'DISADVANTAGE', 'DISAGREE', 'DISAGREEMENT', 'DISAPPEAR', 'DISAPPOINT', 'DISAPPOINTED', 'DISAPPOINTMENT', 'DISASTER', 'DISC', 'DISCARD', 'DISCIPLINE', 'DISCLOSE', 'DISCOUNT',
                'DISCOVER', 'DISCOVERY', 'DISCREET', 'DISCRETION', 'DISCRIMINATE', 'DISCUSS', 'DISCUSSION', 'DISEASE', 'DISGUST', 'DISH', 'DISLIKE', 'DISMISS', 'DISORDER', 'DISPLAY', 'DISPOSE', 
                'DISPUTE', 'DISTANCE', 'DISTANT', 'DISTINCT', 'DISTINCTION', 'DISTINGUISH', 'DISTRIBUTE', 'DISTRIBUTION', 'DISTRICT', 'DISTURB', 'DIVE', 'DIVERSE', 'DIVERSITY', 'DIVIDE', 'DIVIDEND', 
                'DIVINE', 'DIVISION', 'DIVORCE', 'DIZZY', 'DO', 'DOCTOR', 'DOCUMENT', 'DOG', 'DOLL', 'DOLLAR', 'DOMAIN', 'DOME', 'DOMESTIC', 'DOMINANT', 'DOMINATE', 'DONATE', 'DONATION', 'DONE',
                'DONKEY', 'DOOR', 'DOPE', 'DORM', 'DOUBLE', 'DOUBT', 'DOUBTFUL', 'DOWN', 'DOWNHILL', 'DOWNLOAD', 'DOWNWARD', 'DOZEN', 'DRAFT', 'DRAG', 'DRAGON', 'DRAIN', 'DRAMA', 'DRAMATIC', 'DRAW', 
                'DRAWER', 'DRAWING', 'DREAD', 'DREAM', 'DRESS', 'DRESSED', 'DRESSER', 'DRIFT', 'DRILL', 'DRINK', 'DRIP', 'DRIVE', 'DRIVER', 'DRIVING', 'DROOL', 'DROP', 'DROUGHT', 'DROWN', 'DRUG', 
                'DRUGSTORE', 'DRUM', 'DRUNK', 'DRY', 'DUAL', 'DUBIOUS', 'DUCK', 'DUE', 'DULL', 'DUMB', 'DUMP', 'DUNE', 'DUNGEON', 'DURABLE', 'DURATION', 'DURING', 'DUSK', 'DUST', 'DUTY', 'DWARF', 
                'DWELL', 'DWELLING', 'DYE', 'DYING', 'DYNAMIC', 'DYNAMITE','DYNASTY','EACH', 'EAGER', 'EAGLE', 'EAR', 'EARLY', 'EARN', 'EARNEST', 'EARNINGS', 'EARTH', 'EARTHQUAKE', 'EASE', 'EASIER', 
                'EASILY', 'EAST', 'EASTERN', 'EASY', 'EAT', 'EATER', 'EATING', 'ECHO', 'ECOLOGICAL', 'ECONOMIC', 'ECONOMICAL', 'ECONOMICS', 'ECONOMIST', 'ECONOMY', 'ECOSYSTEM', 'EDGE', 'EDIT', 'EDITION',
                'EDITOR', 'EDUCATE', 'EDUCATED', 'EDUCATING', 'EDUCATION', 'EDUCATIONAL', 'EDUCATOR', 'EFFECT', 'EFFECTIVE', 'EFFECTIVELY', 'EFFICIENCY', 'EFFICIENT', 'EFFORT', 'EGG', 'EGO', 'EITHER', 
                'ELABORATE', 'ELBOW', 'ELDER', 'ELDERLY', 'ELECT', 'ELECTION', 'ELECTORAL', 'ELECTRIC', 'ELECTRICAL', 'ELECTRICITY', 'ELECTRON', 'ELECTRONIC', 'ELEGANT', 'ELEMENT', 'ELEMENTARY', 'ELEPHANT',
                'ELEVATE', 'ELEVATION', 'ELEVATOR', 'ELEVEN', 'ELIGIBLE', 'ELIMINATE', 'ELITE', 'ELSE', 'ELSEWHERE', 'EMBARRASS', 'EMBARRASSING', 'EMBARRASSMENT', 'EMBRACE', 'EMERGE','EMERGENCY',"FACE", "FACT", 
                "FAIR", "FALL", "FAMILY", "FAR", "FAST", "FATHER", "FEEL", "FEW", "FIGHT", "FIND", "FINE", "FINGER", "FIRE", "FIRST", "FISH", "FIX", "FLY", "FOOD", "FOR", "FORM", "FOUND", "FREE", "FRIEND", "FROM", 
                "FULL", "FUN", "FUR", "FACEBOOK", "FACILITY", "FALLEN", "FAN", "FARM", "FAVOURITE", "FEAR", "FEED", "FINE", "FLAME", "FLIGHT", "FLOW", "FLOWER", "FOCUS", "FOLLOW", "FORCE", "FOREST", "FORGET", "FORWARD", 
                "FRUIT", "FREEZE", "FROST", "FESTIVAL", "FIGHTER", "FLESH", "FINGERPRINT", "FAIRLY", "FAMOUS", "FATAL", "FREEDOM", "FLAVOR", "FRIENDLY", "FAULT", "FOND", "FAVOR", "FORCEFUL", "FROG", "FORWARDING", "FURTHER", 
                "FESTIVE", "FADE", "FABRIC", "FEST", "FINDING", "FALLING", "FAMILIAR", "FINEST", "FUND", "FOLD", "FLAT", "FLIGHTY", "FAITH", "FIGHTING", "FLOOR", "FLATTER", "FREIGHT", "FASHION", "FIXED", "FLOAT", "FAMOUSLY",
                "FOUR", "FORGIVE", "FESTIVITY", "FUNDAMENTAL", "FELT", "FATE", "FANCY", "FARMS", "FORCEFULLY", "FAT", "FILL", "FRESH", "FALLS", "FIRM", "FLEET", "FANATIC", "FLEW", "FASTEN", "FAITHFUL", "FANCIES", "FATEFUL", 
                "FESTIVALS", "FILING", "FAUNA", "FESTIVELY", "FURNACE", "FADED", "FAIRNESS", "FOREVER", "FANATICS", "FOSSIL", "FATIGUE", "FESTIVITIES", "FAMINES", "FENCES", "FEATHERS", "FRIENDS", "FESTERING", "FORGOTTEN", 
                "FOURTH", "FATALLY", "FELLOWS", "FUNDING", "FACED", "FACTOR", "FIBER", "FABRICS", "FILM", "FIR", "FLOOD", "FOUNTAIN", "FLOWS", "FOLDING", "FIZZ", "FINDERS", "FRAIL", "FAIRLY", "FORESTED", "FAB", "FANTASTIC",
                "FOURS", "FUSSY", "FASTLY", "FIERCE", "FRAGMENT", "FUNDS", "FAILING", "FARTHER", "FALLACY", "FALLOUT", "FANG", "FRENZY", "FREEBIE", "FELL", "FEVER", "FREED", "FURNISH", "FAVORABLY", "FANS", "FOCUSING", "FOGGY", 
                "FOREST", "FESTIVE", "FLARE", "FLINT", "FRESHLY", "FAMINE", "FANTASIES", "FANCIFUL", "FATHOM", "FORCEPS", "FAKE", "FANTASIZING", "FRICTION", "FAMILY", "FIGHTERS", "FORMAL", "FIVE", "FESTIVAL", "FEELINGS", "FRONT","FLEE", "FRENCH", "FEEL",
                "FALLEN", "FASTEST", "FRENCHY", "FOREGONE", "FUEL", "FAME", "FLINTY", "FAMOUSLY", "FRIGHTEN", "FABLES", "FOCAL", "FABRICATE", "FURNISHED", "FINDINGS", "FINISH", "FAINT", "FOLDS", "FRAGILE", "FLOUR", "FANTASTICALLY",'GAB', 'GADGET', 'GAG', 'GAIN', 
                'GALE', 'GALL', 'GALLON', 'GAMBLE', 'GAME', 'GAMING', 'GANG', 'GAP', 'GAS', 'GASP', 'GATE', 'GATHER', 'GAY', 'GEM', 'GENERAL', 'GENERATE', 'GENERATION', 'GENETIC', 'GENTLE', 'GENTLEMAN', 'GENTLY', 'GEOGRAPHY', 'GEORGE', 'GHOST', 'GIFT', 'GIG', 'GILL', 
                'GIMME', 'GINGER', 'GIRL', 'GIRLFRIEND', 'GIVE', 'GIVEN', 'GIVING', 'GLAD', 'GLANCE', 'GLARE', 'GLASS', 'GLOW', 'GLUE', 'GO', 'GOAL', 'GOALIE', 'GOLD', 'GOLDEN', 'GOLF', 'GOOD', 'GOODBYE', 'GOOGLE', 'GOSSIP', 'GOT', 'GOVERN', 'GOVERNMENT', 'GRAB', 'GRADUATE',
                'GRAIN', 'GRAND', 'GRANDCHILD', 'GRANDDAUGHTER', 'GRANDSON', 'GRAPE', 'GRASS', 'GRATITUDE', 'GREAT', 'GREED', 'GREEN', 'GREETING', 'GRID', 'GRIM', 'GRIN', 'GRIP', 'GROAN', 'GROW', 'GROWN', 'GROWTH', 'GUARD', 'GUESS', 
                'GUIDE', 'GUITAR', 'GUM', 'GUN', 'GUST', 'GYM', 'GYMNAST', 'GYMNASIUM', 'GYST', 'GYSTER', 'GYRO', 'GYPSY','GYOZA',
                'HABIT', 'HACK', 'HAIL', 'HAIR', 'HALF', 'HALL', 'HALT', 'HAMMER', 'HAND', 'HANDLE','HANDSOME', 'HANDY', 'HANG', 'HAPPEN', 'HAPPY', 'HARBOR', 'HARD', 'HARDEN', 'HARDLY', 'HARM',
                'HARSH', 'HASTE', 'HASTY', 'HATCH', 'HATE', 'HAUL', 'HAUNT', 'HAVE', 'HAWK', 'HAZE','HAZY', 'HEAD', 'HEADED', 'HEADING', 'HEADLINE', 'HEADQUARTERS', 'HEAL', 'HEALTH', 'HEALTHY', 'HEAP',
                'HEAR', 'HEARD', 'HEARING', 'HEART', 'HEAVEN', 'HEAVY', 'HEDGE', 'HEED', 'HEEL', 'HEIGHT','HEIR', 'HELICOPTER', 'HELL', 'HELP', 'HELPFUL', 'HELPLESS', 'HEM', 'HER', 'HERB', 'HERD',
                'HERE', 'HERITAGE', 'HERO', 'HEROIC', 'HEROIN', 'HERS', 'HESITATE', 'HIDDEN', 'HIDE', 'HIGH','HIGHER', 'HIGHLIGHT', 'HIGHLY', 'HIGHWAY', 'HIKE', 'HILL', 'HINDER', 'HINT', 'HIP', 'HIRE',
                'HIS', 'HISS', 'HISTORIC', 'HISTORICAL', 'HISTORY', 'HIT', 'HITCH', 'HIVE', 'HOBBY', 'HOIST','HOLD', 'HOLE', 'HOLIDAY', 'HOLLOW', 'HOLY', 'HOME', 'HOMEMADE', 'HOMEWORK', 'HONEST', 'HONEY',
                'HONOR', 'HONOUR', 'HOOD', 'HOOK', 'HOOT', 'HOPE', 'HOPEFUL', 'HOPPER', 'HORIZON', 'HORIZONTAL',
                'HORN', 'HORRIBLE', 'HORROR', 'HORSE', 'HOSE', 'HOSPITAL', 'HOST', 'HOSTAGE', 'HOSTEL', 'HOSTESS','HOT', 'HOTEL', 'HOUR', 'HOUSE', 'HOUSEHOLD', 'HOUSEKEEPER', 'HOVER', 'HOW', 'HOWEVER', 'HUGE',
                'HUGELY', 'HUM', 'HUMAN', 'HUMANE', 'HUMBLE', 'HUMID', 'HUMIDITY', 'HUMOR', 'HUMOROUS', 'HUMP','HUNDRED', 'HUNGER', 'HUNGRY', 'HUNT', 'HUNTER', 'HURDLE', 'HURL', 'HURRY', 'HURT', 'HUSBAND',
                'HUSH', 'HUSTLE', 'HYBRID', 'HYDRAULIC', 'HYDROGEN', 'HYPER', 'HYPERACTIVE', 'HYPERTENSION', 'HYPOTHESIS', 'HYSTERIA',
                'HYSTERICAL', 'HABITAT', 'HALFHEARTED', 'HARDWARE', 'HEARTBREAK', 'HEARTBEAT', 'HEARTFELT', 'HEARTLESS', 'HEDGEHOG', 'HELMET',
                'HELPFULNESS', 'HINDERANCE', 'HIPPOPOTAMUS', 'HOMECOMING', 'HOMELAND', 'HOMELESS', 'HOMELY', 'HOMOGENEOUS', 'HONORABLE', 'HOPELESS',
                'HOPEFULNESS', 'HORIZONTALLY', 'HOSPITABLE', 'HOSTILITY', 'HOTHEADED', 'HOURGLASS', 'HOUSEHOLDER', 'HOUSEMAID', 'HOUSEWIFE', 'HOUSEWORK',
                'HUMANITY', 'HUMANITARIAN', 'HUMBLENESS', 'HUMIDIFIER', 'HUMILIATION', 'HUMORLESS', 'HUNCHBACK', 'HUNDREDTH', 'HUNGRILY', 'HURTFUL',
                'HYDRANGEA', 'HYDROCARBON', 'HYGIENE', 'HYPERLINK', 'HYPERSPACE', 'HYPERTEXT', 'HYPERVISOR', 'HYPOCHONDRIA', 'HYPOTHETICAL','HUMIDIFY','ICE', 'ICICLE', 'ICON', 'IDEA', 'IDENTIFY', 'IDENTITY', 
                'IDLE', 'IGNORE', 'ILL', 'ILLUMINATE', 'ILLUSION', 'IMAGINE', 'IMMEDIATE', 'IMMIGRANT', 'IMPACT', 'IMPLEMENT', 'IMPLANT', 'IMPORT', 'IMPORTANT', 'IMPOSE', 'IMPROVE', 'IMPULSE', 'INCLUDE', 'INCLUSION', 
                'INCOME', 'INCREASE', 'INDEED', 'INDEPENDENT', 'INDEX', 'INDICATE', 'INDICATION', 'INDIE', 'INDOOR', 'INDUSTRY', 'INFINITE', 'INFLATE', 'INFLUENCE', 'INFORM', 'INFORMATION', 'INFORMAL', 'INFRASTRUCTURE', 'INHABIT', 
                'INHERIT', 'INITIATE', 'INJURY', 'INJECT', 'INJUNCTION', 'INJUSTICE', 'INSTRUMENT', 'INTEGRATE', 'INTEGRITY', 'INTELLIGENT', 'INTEND', 'INTENSIFY', 'INTENTION', 'INTERACT', 'INTEREST', 'INTERIOR', 'INTERNAL', 'INTERNET', 
                'INTERVIEW', 'INTRODUCE', 'INVEST', 'INVESTIGATE', 'INVITE', 'INVOLUTION', 'INVOICE', 'IRON', 'ISLAND', 'ISSUE', 'ITEM', 'ITALIAN', 'ITSELF', 'ICONIC', 'IDIOSYNCRATIC', 'IMPOSSIBLE', 'IMPROVEMENT', 'IMPERIAL', 'IMPRINT', 'INCORPORATE', 'INTERNAL', 
                'INTEGRATE', 'INDICATION', 'INSTANT', 'INTEGRAL', 'INHERENT', 'INFRARED', 'INTERMITTENT', 'INCAPACITATE', 'INNOVATE', 'INHIBIT', 'INSPIRE', 'INSERT', 'INSERTION', 'INTERNALIZE', 'INTERCEDE', 'INDUCTION', 'INQUIRE', 'INTEGRITY', 'INTERVENE', 'INDULGE', 'IMPOSED', 
                'INTERFACE', 'INTEGRAL', 'INFRACTION', 'IMPROVISE', 'INSTINCT', 'INTERRUPT', 'IMPERFECTION', 'INVISIBLE', 'INTERVAL', 'INTEGRAL', 'INVESTMENT', 'IMMORTAL', 'INFLAMMABLE', 'INTERFACE', 'IMPACTFUL', 'INDIVIDUAL', 'INVINCIBLE', 'INCAPACITY', 'INTERPOLATE', 'INTEGRATE', 
                'INTERRUPTION', 'INTERPRETER', 'INSOLVENCY', 'INDEFINITELY', 'INHUMANE', 'INVOLVEMENT', 'INDEPENDENCE', 'INFLAMMATION', 'INDIGENOUS', 'INFLAMMABLE', 'INHIBITION', 'INTERRUPTING', 'INVISIBILITY', 'INDESTRUCTIBLE', 'INVESTIGATION', 'INDIVIDUALLY', 'IMPERMISSIBLE', 'INEXPLICABLE', 
                'INTERNATIONALLY', 'INEXPERIENCE', 'INFINITESIMAL', 'INDESTRUCTIBLE',
                'JACK', 'JACKAL', 'JACKASS', 'JACKET', 'JACKPOT', 'JACKFRUIT', 'JACKKNIFE', 'JACKSON', 'JACOB', 'JAGGER', 'JAGUAR', 'JAUNT', 'JAVELIN', 'JAW', 'JAWBONE', 'JAY', 'JAYWALK', 'JEANS', 'JEER', 'JELLY', 
                'JELLYFISH', 'JENNY', 'JEST', 'JET', 'JETSAM', 'JEWEL', 'JIG', 'JIGSAW', 'JINGLE', 'JINX', 
                'JOKER', 'JOKE', 'JOLLY', 'JOLT', 'JOURNAL', 'JOURNEY', 'JOVIAL', 'JUDGE', 'JUDGMENT', 'JUG', 
                'JUGGLE', 'JUGGLER', 'JULY', 'JUMP', 'JUMPER', 'JUNGLE', 'JUNIOR', 'JUNK', 'JUROR', 'JUST', 
                'JUSTICE', 'JUT', 'JUTTING', 'JUGULAR', 'JOVIALITY', 'JUTS', 'JITTERY', 'JUMBLED', 'JUMBLES', 'JURISDICTION', 
                'JUVENILE', 'JUMBO', 'JACKS', 'JACKED', 'JACKING', 'JACKS', 'JAIL', 'JAILER', 'JAILING', 'JARS', 
                'JASPER', 'JAZZ', 'JAZZED', 'JAZZES', 'JERKS', 'JERSEY', 'JETS', 'JIVES', 'JOKES', 'JUMBOS', 
                'JACKIE', 'JACKAL', 'JAPAN', 'JANGLES', 'JAZZING', 'JIBES', 'JINGLES', 'JARGONS', 'JANGLES', 'JUDGES', 
                'JAILS', 'JITTER', 'JOKES', 'JOBS', 'JAZZY', 'JANGLES', 'JAGGERY', 'JOVIAL', 'JUNGLED', 'JUMPS', 
                'JITNEY', 'JITTER', 'JACKING', 'JINGLED', 'JACKING', 'JACKSONS', 'JERKY', 'JINGLES', 'JOLTS', 'JINGLY', 
                'JURORS', 'JAZZED', 'JUMBLE', 'JUMBLES', 'JAZZING', 'JUMBLED', 'JACINTH', 'JAGGED', 'JOURNALS', 'JINGLY', 
                'JAMMED', 'JOVIAL', 'JUNGLE', 'JUMBLES', 'JOWLS', 'JACKFRUITS', 'JACKFRUIT', 'JIGGER', 'JOLIE', 
                'JUBILEE', 'JAYWALKING', 'JURISPRUDENCE', 'JACKFRUITS', 'JARHEADS', 'JACKED', 'JELLIER', 'JAGGIER', 
                'JUNKYARD', 'JUGGLING', 'JUMPSTART', 'JOVIALITY', 'JAMMIEST', 'JUMBLED', 'JACKFRUIT', 'JOVIALLY', 
                'JACKPOT', 'JOCKEYS', 'JACKPOT', 'JUNKIE', 'JAWBONES', 'JUNKING', 'JUNKED', 'JELLIED','JACKKNIFES',
                'KABOB', 'KAYAK', 'KNEE', 'KNEELED', 'KNEEL', 'KNEELING', 'KNIFE', 'KNIT', 'KNITTING', 'KNOT', 'KNOTTED', 'KNOTTY', 
                'KNOCK', 'KNOCKED', 'KNOCKING', 'KNOW', 'KNOWLEDGE', 'KNOWN', 'KNOX', 'KID', 'KIDDING', 'KIDNEY', 'KILL', 'KILLED', 'KILLING', 
                'KILO', 'KILOMETER', 'KILOWATT', 'KILN', 'KIND', 'KINDLY', 'KINDER', 'KINDNESS', 'KING', 'KINGDOM', 'KINK', 'KITCHEN', 'KITE', 
                'KITTY', 'KISS', 'KISSED', 'KISSING', 'KISSY', 'KNACK', 'KNACKER', 'KNAVE', 'KNIGHT', 'KNOWING', 'KALAMATA', 'KALAMAZOO', 'KANGAROO',
                'KAPOK', 'KARATE', 'KARMA', 'KAYAKING', 'KINDRED', 'KINDLE', 'KINDLEING', 'KINKY', 'KINO', 'KIDNAPPING', 'KNOCKOUT', 'KNOTLESS', 'KINGSIZE', 
                'KNITTED', 'KITCHENWARE', 'KETTLE', 'KITTEN', 'KICK', 'KICKED', 'KICKING', 'KILLER', 'KILLINGLY', 'KNEEDEEP', 'KITCHENETTE', 'KINDNESS', 'KISSABLE', 
                'KNEECAP', 'KINESIS', 'KITESURF', 'KICKSTART', 'KAMIKAZE', 'KALIDAS', 'KAPPA', 'KINKAJOU', 'KASHMIR', 'KAYAKED', 'KURTOS', 'KNIFING', 'KINGS', 'KALAM',
                'KELP', 'KELPERS', 'KILTS', 'KENTUCKY', 'KELVIN', 'KIDNAP', 'KISSES', 'KILOBYTE', 'KELPERS', 'KILOBIT', 'KILOGRAM', 'KELT', 'KIDDO', 'KNOLL', 'KNURLED', 
                'KNACKS', 'KINESTHETIC', 'KETTLEBELL', 'KIEV', 'KRAKEN', 'KARST', 'KISSINGLY', 'KNITTINGLY', 'KILLINGLY', 'KIDNAPPED', 'KNEELER', 'KINKINESS', 'KITCHENWARES', 
                'KICKOFF', 'KIDNAPPERS', 'KNOWHOW', 'KNOWLEDGEABLE', 'KALASH', 'KALAMATA', 'KNITTINGS', 'KNELL', 'KIDWELD', 'KINKINESS', 'KNICKERS', 'KITCHENS','KAKEMONO',
                'LABORATORY', 'LABOR', 'LACK', 'LADDER', 'LADY', 'LAKE', 'LAMB', 'LAME', 'LAMP', 'LANE',
                'LARGE', 'LAST', 'LATCH', 'LATE', 'LAUNCH', 'LAYER', 'LEAD', 'LEAF', 'LEARN', 'LEAST',
                'LEAVE', 'LED', 'LEFT', 'LENGTH', 'LESS', 'LEVER', 'LIFE', 'LIFT', 'LIGHT', 'LIKE',
                'LIMOUSINE', 'LINE', 'LINK', 'LINT', 'LION', 'LIST', 'LOAN', 'LORD', 'LOST', 'LOVE',
                'LARGE', 'LAP', 'LAG', 'LAUGH', 'LEAVE', 'LOVELY', 'LUMBER', 'LUNCH', 'LOOK', 'LOAN',
                'LITERATURE', 'LOG', 'LUNCH', 'LOOP', 'LAY', 'LATCH', 'LEAD', 'LEND', 'LOW', 'LANTERN',
                'LOGIC', 'LAUNDRY', 'LEAD', 'LIVING', 'LIMIT', 'LOBBY', 'LANGUAGE', 'LAPTOP', 'LENGTH',
                'LAC', 'LIT', 'LOWER', 'LINK', 'LABEL', 'LEMON', 'LUNAR', 'LAD', 'LONELY', 'LAZY',
                'LAN', 'LOST', 'LUXURY', 'LASH', 'LEASH', 'LACE', 'LABEL', 'LOTION', 'LEVEL', 'LORD',
                'LOFT', 'LUNGE', 'LARK', 'LATCH', 'LAST', 'LENT', 'LOST', 'LINT', 'LIT', 'LIMIT',
                'LONG', 'LOST', 'LEAF', 'LEAVE', 'LESSON', 'LAMP', 'LAKE', 'LAVENDER', 'LORDLY', 'LUXE',
                'LUNCH', 'LIVING', 'LULL', 'LASS', 'LITTLE', 'LAY', 'LARK', 'LIBRARY', 'LEAFY', 'LUMP',
                'LOVE', 'LEVEL', 'LARGE', 'LIGHT', 'LEAF', 'LOST', 'LOOK', 'LIMIT', 'LATER', 'LOUSE',
                'LAKE', 'LAYER', 'LEAVE', 'LUNCH', 'LADDER', 'LOUNGE', 'LEVEL', 'LENGTH', 'LIE', 'LEAK',
                'LOW', 'LUXURY', 'LATCH', 'LUMBER', 'LANE', 'LATCH', 'LAST', 'LINT', 'LEND', 'LEASH',
                'LATCH', 'LINE', 'LOG', 'LOVE', 'LUX', 'LOST', 'LAVENDER', 'LUXURY', 'LAG', 'LATCH',
                'LOOT', 'LAUGHTER', 'LAMP', 'LIT', 'LABEL', 'LENGTH', 'LUXURY', 'LEMON', 'LOGIC',
                'LATCH', 'LARGE', 'LEAF', 'LAMP', 'LUNCH', 'LIT', 'LATCH', 'LEAFY', 'LEND', 'LINE',
                'LAMB', 'LIBRARY', 'LOW', 'LIMB', 'LAMP', 'LUMBER', 'LEAFY', 'LIVELY', 'LABEL','LOST',
                'MACHINE', 'MAGAZINE', 'MAGIC', 'MAGNET', 'MAIL', 'MAJOR', 'MAKE', 'MAKING', 'MALLET', 'MALT', 'MAN', 
                'MANAGE', 'MANAGER', 'MANDATE', 'MANGAGE', 'MANIC', 'MANIFEST', 'MANNER', 'MANSION', 'MANY', 'MAP', 'MATERIAL', 'MATHEMATICS', 
                'MATTRESS', 'MAY', 'MAYBE', 'MEAL', 'MEASURE', 'MECHANIC', 'MEDIA', 'MEDICAL', 'MEETING', 'MELT', 'MEMBER', 'MEMORY', 'MENTAL', 'MESSAGE', 
                'METAL', 'METHOD', 'MIDDLE', 'MIDST', 'MIGHT', 'MILL', 'MILLION', 'MIND', 'MINERAL', 'MINIMUM', 'MINUTE', 'MISSION', 'MIX', 'MIXTURE', 'MODEL', 
                'MODERN', 'MODIFY', 'MODULE', 'MOIST', 'MONEY', 'MONITOR', 'MONTH', 'MORNING', 'MOTHER', 'MOTEL', 'MOTIVE', 'MOTOR', 'MOUNT', 'MOVE', 'MOVEMENT', 'MOWER', 'MUD', 
                'MULTIPLE', 'MUSEUM', 'MUSIC', 'MUTE', 'MYSELF', 'MOTHERBOARD', 'MOLECULE', 'MAGNETIC', 'MODIFICATION', 'MECHANISM', 'MONUMENT', 'MOBILITY', 'MANAGEMENT', 'MISTAKE',
                'MANTLE', 'MARINE', 'MACHINE', 'MOTIVATION', 'MICROPHONE', 'MOTIVATED', 'MONARCH', 'MINDFUL', 'MIGRATE', 'MIGRATION', 'MIGRANT', 'MISUNDERSTANDING', 'MEDICINE', 'MELANCHOLY', 
                'MARGINAL', 'MEDICAL', 'MARKET', 'MASSIVE', 'MIXED', 'MORAL', 'MUSCLE', 'MONETARY', 'MIRACLE', 'MARK', 'MIMIC', 'MANUFACTURING', 'MARGARET', 'MORALITY', 'MANGROVE', 'MAGNETISM',
                'MISSED', 'MENTION', 'MULTIPLY', 'MAGNETIC', 'MOLE', 'MAGAZINES', 'MALICIOUS', 'MECHANICAL', 'MASS', 'MOTIVATES', 'MENTALITY', 'MINDFULNESS', 'MISPLACED', 'MARGINALIZED', 'MOTORCYCLE', 
                'MULTIMEDIA', 'MANUAL', 'MATURITY', 'MONITORING', 'MAGICIAN', 'MASSACHUSETTS', 'MIMICKING', 'MELT', 'MAGAZINE', 'MELODY', 'MANTAIN', 'MORPH', 'MAJORLY', 'MICROSCOPE', 'MATHEMATICS', 'MANUFACTURE', 'MILLIONS','MUSEUMS',    
                'NATION', 'NATURE', 'NIGHT', 'NAME', 'NEVER', 'NEED', 'NOW', 'NOTE', 'NUMBER', 'NICE', 
                'NEW', 'NORTH', 'NATIONAL', 'NAMES', 'NEEDLE', 'NOT', 'NAMES', 'NEXT', 'NO', 'NINE',
                'NEWSPAPER', 'NORTH', 'NEIGHBOR', 'NOMINATION', 'NURSE', 'NAMES', 'NATIONAL', 'NOTEBOOK', 
                'NOTHING', 'NETWORK', 'NUT', 'NEUTRAL', 'NEWSPAPER', 'NIGHT', 'NOTIFICATION', 'NATURE',
                'NOBLE', 'NAMES', 'NURSE', 'NOT', 'NIGHT', 'NICE', 'NORTH', 'NINE', 'NOTEBOOK', 
                'NOTES', 'NATION', 'NORM', 'NOTHING', 'NUMBER', 'NICK', 'NEW', 'NAMES', 'NIGHT', 
                'NEIGHBOR', 'NUTRITION', 'NOTE', 'NEWS', 'NOTIFICATION', 'NUT', 'NOMINATION', 
                'NEEDED', 'NINTH', 'NURSE', 'NUTRITION', 'NAME', 'NATIONAL', 'NOTES', 'NETWORK', 
                'NICE', 'NEW', 'NAMES', 'NEVER', 'NAMES', 'NORTH', 'NECESSARY', 'NIGHT', 'NEXT', 
                'NOMINATED', 'NOT', 'NORM', 'NUMBER', 'NUT', 'NURSE', 'NAMES', 'NICK', 'NOTES', 
                'NEUTRAL', 'NETWORK', 'NEWS', 'NOTEBOOK', 'NORTH', 'NINTH', 'NICE', 'NEEDED', 
                'NOTHING', 'NATIONAL', 'NIGHT', 'NEXT', 'NAME', 'NEW', 'NAMES', 'NURSE', 'NUT', 
                'NAMES', 'NEIGHBOR', 'NATION', 'NURSE', 'NEED', 'NATIONAL', 'NORM', 'NIGHT', 
                'NOTE', 'NUMBER', 'NECESSARY', 'NINE', 'NEWSPAPER', 'NOMINATION', 'NETWORK', 
                'NUT', 'NAMES', 'NOTES', 'NEXT', 'NINTH', 'NEWS', 'NOTHING', 'NORTH', 'NIGHT', 
                'NURSE', 'NEUTRAL', 'NATION', 'NAMES', 'NAME', 'NATIONAL', 'NINE', 'NEEDED', 
                'NOMINATED', 'NEVER', 'NICE', 'NEW', 'NORM', 'NOTEBOOK', 'NUTRITION', 'NUMBER', 
                'NETWORK', 'NOTIFICATION', 'NICE', 'NAMES', 'NORTH', 'NOTHING', 'NEIGHBOR', 
                'NATIONAL', 'NOTE', 'NURSE', 'NUTRITION', 'NEWSPAPER', 'NEEDED', 'NIGHT', 
                'NAMES', 'NEXT', 'NETWORK', 'NOTES', 'NINTH', 'NORTH', 'NIGHT','NICE',
                'OBEDIENCE', 'OBJECT', 'OBJECTION', 'OBLIGE', 'OBLIGATION', 'OBLIVIOUS', 'OBSERVATION', 'OBSERVE', 'OBSTACLE', 'OBSTRUCT', 
                'OBTAIN', 'OBVIOUS', 'OCCASION', 'OCCUPY', 'OCEAN', 'OCTOBER', 'ODD', 'ODOR', 'OFF', 'OFFICIAL', 'OFFSET', 'OIL', 'OINTMENT', 
                'OLD', 'OLDER', 'OLDEST', 'OMIT', 'ONCE', 'ONE', 'ONGOING', 'ONLINE', 'ONLY', 'OPEN', 'OPENING', 'OPERATE', 'OPERATION', 'OPINION', 
                'OPPORTUNITY', 'OPPOSE', 'OPPOSITION', 'OPTIMIZE', 'OPTION', 'OR', 'ORANGE', 'ORDER', 'ORDINARY', 'ORGANIC', 'ORGANIZE', 'ORIGIN', 'ORIGINAL', 
                'OUT', 'OUTCOME', 'OUTDOOR', 'OUTLINE', 'OUTSIDE', 'OVER', 'OVERALL', 'OVERCOME', 'OVERLAP', 'OVERLOOK', 'OVERSEAS', 'OVERTIME', 'OWNER', 'OWNERSHIP', 'OXYGEN', 
                'OUTLOOK', 'OUTBREAK', 'OUTDATED', 'OVERLOAD', 'OVERSEE', 'OUTSMART', 'OPPOSING', 'OCCUPATION', 'OBLITERATE', 'OCCULT', 'OVERRIDE', 'OPENING', 'ORCHESTRA', 'OUTREACH', 
                'OPPONENT', 'OUTLAW', 'OVERWHELM', 'OVERCOME', 'OFFER', 'OUTLOOK', 'OPTICAL', 'OPPORTUNE', 'OBJECTIONABLE', 'ORIGINATE', 'OBSOLETE', 'ORIENTED', 'OUTDATED', 'OVERALL', 
                'OVERRIDE', 'OUTSTANDING', 'OFFICER', 'OXYGENATE', 'OPERATIONAL', 'OUTSOURCING', 'ORGANIZATION', 'OXYGENATION', 'ORIENTATION', 'OVERSTATED', 'ONLOOKER', 'OPENNESS', 'OUTNUMBER', 
                'OUTDATED', 'OVERPOWER', 'OPENING', 'OCEANIC', 'OPPOSITIONAL', 'ONBOARD', 'OVERHEAD', 'OBLIGATED', 'OUTSPOKEN', 'OVERUSE', 'OUTCAST', 'OUTLOOKS', 'OVERRULE', 'OUTDATED', 'OUTSOURCE', 
                'OPPORTUNITIES', 'OUTBREAKS', 'ORGANISMS', 'OBSESSION', 'OBLIGES', 'OCCUR', 'OPINIONS', 'OXYGENIC', 'OUTSTRETCH', 'ORACLES','OUTSTRIP',
                'PAINT', 'PAPER', 'PARENT', 'PART', 'PASS', 'PAST', 'PATH', 'PATTERN', 'PEACE', 'PEAR', 'PEOPLE', 'PERIOD', 'PERSON', 'PLACE', 'PLAN', 'PLANT', 'PLASTIC', 'PLAY', 'POINT', 'POLICE', 
                'POLICY', 'POLITICS', 'POOL', 'POSITION', 'POSSIBLE', 'POWER', 'PREMISE', 'PRESS', 'PRICE', 'PRIORITY', 'PROBLEM', 'PROGRAM', 'PROJECT', 'PROMISE', 'PROOF', 'PUBLIC', 'PUBLISH', 'PULL', 
                'PUSH', 'PAPERBACK', 'PARTICULAR', 'PLAIN', 'PARTY', 'PERFORM', 'PRINT', 'PRINCE', 'PROCEDURE', 'PROFESSOR', 'PUSH', 'PRESENT', 'PRINCIPLE', 'PROGRESS', 'PROTEST', 'PLANET', 'PREVIOUS', 
                'PRESIDENT', 'PUNCTUAL', 'PACK', 'POET', 'POINTER', 'PERSONAL', 'POTENTIAL', 'PARK', 'PROVIDE', 'PREPARE', 'PROTECT', 'PREACH', 'PREVENT', 'PERSIST', 'PROGRAMMER', 'PATIENT', 'PARKING', 
                'PICK', 'PLAYGROUND', 'PIANO', 'PASTOR', 'PUNISH', 'PRESCRIPT', 'PREMIUM', 'PRISON', 'PERCEIVE', 'PLUMB', 'PERFECT', 'POLISHED', 'PROBLEMATIC', 'PROFESSIONAL', 'POPPY', 'PULSE', 'POLICYMAKER', 
                'PATTERNED', 'PASTEL', 'PORTION', 'PANEL', 'PLOTTING', 'PROPER', 'PRESCRIPTIVE', 'PRESENTATION', 'PRONOUNCE', 'PARTICIPATE', 'PRINCIPAL', 'PLATFORM', 'PROFICIENCY', 'PROSPER', 'PROVE', 'POINTE', 
                'PREMISES', 'PHYSICAL', 'PASTURE', 'PRAYER', 'PRIZE', 'PROLIFIC', 'POT', 'PASTIME', 'PICKUP', 'PRINCIPALITY', 'PRETEND', 'PROCEED', 'PRETENTIOUS', 'PEDESTAL', 'PITCH', 'PROLIFERATE', 
                'PATRIOT', 'PEPPER', 'PROFUSE', 'PHOTOGRAPH', 'PICKLE', 'PLENTY', 'PRESENTLY', 'PRIMAL', 'PLOT', 'PLUNGE', 'PROOFREAD', 'PARALLEL', 'PAIN', 'POTENTIAL', 'PRESENTABLE', 'PARTNER', 'POLLUTION', 
                'PERFORMANCE', 'PREMIUMS', 'POSITIVE', 'PURCHASE', 'PROVOCATIVE', 'POSSESSION', 'PERIODIC', 'PRINTER', 'PLATFORMER', 'PERSONNEL', 'PILOT', 'POST', 'PERIPHERAL', 'PINE', 'PRECIOUS', 'PROPOSAL', 
                'PAINTER', 'PROJECTOR', 'PRAGMATIC', 'PROFESSION', 'PROPOSING', 'POINTLESS', 'POLL', 'PURPOSE', 'PANELIST', 'PREVAIL', 'PHRASE', 'PROVISION', 'PUBLICATION', 'PATRIARCH', 'PREDICT', 'PATROL', 
                'PROTOCOL', 'POLAR', 'PATIENCE', 'PATENT', 'PRIMALITY', 'PLACEMENT', 'PUNCTUATE', 'PRAGMATIST', 'PARTIAL', 'POINTERS', 'PROTESTER', 'PROPERLY','PARTICIPANT',
                'QUAD', 'QUADRANT', 'QUAKE', 'QUALIFY', 'QUALITY', 'QUANTIFY', 'QUANTITY', 'QUARANTINE', 'QUART', 'QUARTER', 'QUASAR', 'QUASH', 'QUESTION', 'QUEUE', 'QUIET', 'QUIETLY', 'QUIZ',
                'QUICK', 'QUICKLY', 'QUICKNESS', 'QUOTATION', 'QUOTE', 'QUOTA', 'QUOTIENT', 'QUORUM', 'QUADRIC', 'QUAGMIRE', 'QUADRANT', 'QUAINT', 'QUASHED', 'QUALIFYING', 'QUALIFIED', 'QUALITIES', 
                'QUALITATIVE', 'QUANDARY', 'QUADRUPLE', 'QUERIES', 'QUICKEN', 'QUANTITIES', 'QUINCE', 'QUARTERLY', 'QUINTET', 'QUICKSTEP', 'QUADRUPLET', 'QUICKWIT', 'QUINQUENNIAL', 'QUOTABLE', 'QUIXOTIC', 
                'QUASI', 'QUICKLY', 'QUINTESSENTIAL', 'QUICKLY', 'QUIESCENT', 'QUANTUM', 'QUANDARY', 'QUOTABLE', 'QUIESCENCE', 'QUENCH', 'QUAD', 'QUANTUM', 'QUICKFIRE', 'QUALITYCONTROL', 'QUADRANT', 'QUICKSILVER', 
                'QUANTIFIABLE', 'QUINTUPLET', 'QUATERNARY', 'QUADRANTAL', 'QUOTATIONMARK', 'QUINTUPLETS', 'QUINQUENNIAL', 'QUICKSILVERED', 'QUOTIENTS', 'QUICKSTEP', 'QUO', 'QUARTERBACK', 'QUASI', 'QUORUMS', 'QUAD', 
                'QUIN', 'QUADRIC', 'QUICKS', 'QUAG', 'QUICKS', 'QUARTET', 'QUANTITYS', 'QUORUMED', 'QUINQUE', 'QUADRANTAL', 'QUINT', 'QUINTS', 'QUIRK', 'QUACK', 'QUOIT', 'QUASI', 'QUINSY', 'QUARTILE', 'QUICKWITTED', 
                'QUADREN', 'QUOTABLES', 'QUANTITATIVE', 'QUANTITYED', 'QUANT', 'QUANTAL', 'QUADRAGESIMAL', 'QUARTERS', 'QUENCHED', 'QUINN', 'QUIN', 'QUAGMIRE', 'QUININE', 'QUIESCING', 'QUINTUPLE', 'QUICKENED', 'QUARTZ','QUANTIZE',
                'RABBIT', 'RACE', 'RACK', 'RADIO', 'RAIL', 'RAIN', 'RAISE', 'RANGE', 'RAPID', 'RATE',
                'RAT', 'RAVE', 'RAZOR', 'READ', 'REACT', 'REAL', 'REAP', 'REAR', 'REBEL', 'RECEIVE',
                'RECENT', 'RECESS', 'RECORD', 'RED', 'REDDEN', 'REDUCE', 'REFLECT', 'REFRESH', 'REFUSE', 'REGARD',
                'REGISTER', 'REHAB', 'REHIRE', 'RELAY', 'RELATE', 'RELEASE', 'RELY', 'REMIND', 'REMOVE', 'REPAIR',
                'REPEAT', 'REPEL', 'REPLAY', 'REPOSE', 'REPORT', 'REPROACH', 'REPTILE', 'REQUEST', 'REQUIRE', 'RESCUE',
                'RESIGN', 'RESIST', 'RESULT', 'RETIRE', 'RETURN', 'REVIEW', 'REVOKE', 'RHYME', 'RICE', 'RICH',
                'RIDE', 'RIDDLE', 'RING', 'RISE', 'RISK', 'RITE', 'ROBOT', 'ROCK', 'RODE', 'ROLL',
                'ROOF', 'ROOM', 'ROPE', 'ROSE', 'ROTATE', 'ROUGH', 'ROUTE', 'RUBBER', 'RUBY', 'RUFF',
                'RUG', 'RUMOR', 'RUN', 'RUNG', 'RUST', 'RUT', 'RAVE', 'RATIFY', 'REACT', 'REACTOR',
                'READER', 'REALITY', 'RECKON', 'RECTIFY', 'REDO', 'REFINE', 'REGION', 'REJOICE', 'RELIEF', 'REMAIN',
                'REMIX', 'RESEARCH', 'RESIDE', 'REVEL', 'REWRITE', 'RIBBON', 'REBEL', 'RECUR', 'REGRET', 'REMINDER',
                'RACIAL', 'RESUME', 'RECITE', 'RENEW', 'REACT', 'REVEAL', 'RESTRICT', 'RADIANT', 'RETRIEVE', 'REVOKE',
                'REFUTE', 'RECESS', 'RECEIPT', 'REGULAR', 'REUNITE', 'REWRITE', 'REHEARSE', 'REMODE', 'REFLECT', 'REACH',
                'RELIST', 'REWRITE', 'RESPECT', 'REVERSE', 'REHIRE', 'REMARK', 'RECOUNT', 'RETRIEVE', 'RELEASE','RELAX',
                'SABOTAGE', 'SABRE', 'SAD', 'SAFE', 'SAFETY', 'SAG', 'SAGE', 'SAIL', 'SAINT', 'SALE',
                'SALARY', 'SALT', 'SAME', 'SANCTION', 'SAND', 'SANE', 'SANG', 'SANTA', 'SAT', 'SATELLITE',
                'SAVAGE', 'SAVE', 'SAY', 'SCHOOL', 'SCIENCE', 'SCIENTIFIC', 'SCREAM', 'SCROLL', 'SEARCH', 'SECURE',
                'SEE', 'SEEK', 'SEEM', 'SELF', 'SELL', 'SEND', 'SENSE', 'SERIOUS', 'SET', 'SEVEN',
                'SHADE', 'SHADOW', 'SHARE', 'SHARP', 'SHOES', 'SHOULDER', 'SHOUT', 'SHOWN', 'SHY', 'SICK',
                'SIDE', 'SIGN', 'SILENT', 'SIMPLE', 'SING', 'SINK', 'SISTER', 'SIZE', 'SKILL', 'SKY',
                'SLAVE', 'SLEEP', 'SLEET', 'SLIDE', 'SLOW', 'SMALL', 'SMART', 'SMILE', 'SMOKE', 'SNOW',
                'SOCIETY', 'SOFT', 'SOLID', 'SOME', 'SOUND', 'SOURCE', 'SPACE', 'SPARE', 'SPEAK', 'SPEED',
                'SPELL', 'SPEND', 'SPORT', 'SPRING', 'STATE', 'STAY', 'STEADY', 'STICK', 'STILL', 'STONE',
                'STOP', 'STORE', 'STRESS', 'STREET', 'STUDY', 'SUBJECT', 'SUCCEED', 'SUGGEST', 'SUMMER', 'SUN',
                'SURE', 'SURFACE', 'SURVEY', 'SUSPICIOUS', 'SWIM', 'SWITCH', 'SYMBOL', 'SYSTEM', 'SAYING', 'SCARED',
                'SCENARIO', 'SCOUT', 'SECURITY', 'SCORE', 'SERVICE', 'SHOW', 'SHELTER', 'SHIFT', 'SHAREHOLDER', 'SHEET',
                'SUGAR', 'SIGHT', 'SIMPLE', 'SUBSCRIBE', 'SLEEK', 'SILVER', 'SPECTACLE', 'SELECTION', 'SLEEPY', 'SAGGY',
                'STRATEGY', 'SILENTLY', 'STRENGTH', 'SUBMISSION', 'SYNONYM', 'SILENTLY', 'SUCCESS', 'SUSPENSE', 'SOLUTION','SIMPLETON',
                'TABLE', 'TACKLE', 'TAG', 'TAKE', 'TAKEN', 'TAKING', 'TALK', 'TALL', 'TALLER', 'TALLEST', 'TAME', 'TANK', 'TARGET', 'TASK', 'TASTE', 'TASTY', 'TAX', 'TEACH', 
                'TEACHER', 'TEAM', 'TEAR', 'TECH', 'TECHNICIAN', 'TECHNOLOGY', 'TELEPHONE', 'TELEVISION', 'TEMPORARY', 'TEND', 'TENDENCY', 'TENDENTIOUS', 'TEN', 'TENDENCY', 'TENDENTIOUS', 
                'TENDER', 'TENET', 'TENNIS', 'TENT', 'TERM', 'TERMINAL', 'TERMS', 'TEST', 'TESTING', 'TEXT', 'TEXTBOOK', 'THE', 'THEATER', 'THEORY', 'THERMOMETER', 'THICK', 'THIN', 'THIRD', 
                'THIRST', 'THIS', 'THOUGH', 'THOUSAND', 'THREAT', 'THREE', 'THRILL', 'THROW', 'THROWN', 'THUMB', 'THUMP', 'TICK', 'TICKET', 'TIDE', 'TIGHT', 'TIME', 'TIMELY', 'TIMES', 'TIN', 'TINY', 
                'TIP', 'TITLE', 'TO', 'TODAY', 'TOGETHER', 'TOO', 'TOOL', 'TOP', 'TOTAL', 'TOUCH', 'TOUR', 'TOWN', 'TRACK', 'TRADE', 'TRAFFIC', 'TRAIN', 'TRANSFER', 'TRANSFORM', 'TRAVEL', 'TREAT', 'TREE', 'TRICK', 
                'TRIP', 'TROUBLE', 'TRUE', 'TRUST', 'TRY', 'TUBE', 'TURN', 'TWICE', 'TWIST', 'TYPE', 'TYPICAL', 'TYPICALLY', 'TURTLE', 'TAP', 'TENDERLY', 'THOUGHT', 'TRANSIT', 'TRUTH', 'TROPHY', 'TANKED', 'TRANSLATE', 
                'TIDY', 'TREND', 'TEMPERATURE', 'TALENT', 'TEA', 'TEMPO', 'TIDAL', 'TICKED', 'TIGHTLY', 'TUNNEL', 'TROLLEY', 'TRAIL', 'TENURE', 'TASKS', 'TWEET', 'TURMOIL', 'TRACKS', 'THOROUGH', 'THICKER', 'TACK', 'TURBINE', 
                'TURNOVER', 'TRAVELER', 'THRIVE', 'TIGHTNESS', 'TREATMENT', 'TIMELESS','TEMPTATION','UNABLE', 'UNACCEPTABLE', 'UNACCOMPANIED', 'UNACHIEVABLE', 'UNACCOUNTABLE', 'UNCONDITIONAL', 'UNCONSCIOUS', 'UNDER', 'UNDERSTAND', 
                'UNDERSTANDING', 'UNDERSTATED', 'UNDERTAKE', 'UNDERTAKING', 'UNDERWEAR', 'UNIQUE', 'UNIVERSAL', 'UNION', 'UNIT', 'UNITY', 'UNLOCK', 'UNVEIL', 'UNVEILING', 'UNSTOPPABLE', 'UNLIMITED', 'UNFORTUNATE', 'UNHAPPY', 
                'UNSETTLED', 'UNSAFE', 'UNUSUAL', 'UNFAMILIAR', 'UNASSIGNED', 'UNEXPECTED', 'UNRELIABLE', 'UNLESS', 'UNFRIENDLY', 'UNVEILING', 'UNWANTED', 'UNIQUE', 'UNKNOWING', 'UNWANTED', 'UNAUTHORIZED', 'UNPREDICTABLE', 
                'UNFOLD', 'UNSURE', 'UNTRUSTED', 'UNWANTED', 'UNLIMITED', 'UNBIASED', 'UNREMARKABLE', 'UNMOVED', 'UNCONVINCING', 'UNFIT', 'UNABLE', 'UNASSISTED', 'UNHINGED', 'UNLIKELY', 'UNRECOGNIZED', 'UNPLANNED', 
                'UNSHARED', 'UNINTERESTED', 'UNHEALTHY', 'UNSUCCESSFUL', 'UNTESTED', 'UNDEFINED', 'UNBIASED', 'UNFOLDING', 'UNTOUCHED', 'UNCOMMON', 'UNFORGOTTEN', 'UNBROKEN', 'UNSPOKEN', 'UNINFORMED', 'UNTRUSTWORTHY', 
                'UNBEKNOWNST', 'UNPRECEDENTED', 'UNFOUNDED', 'UNFAIR', 'UNRECOGNIZED', 'UNASSUMING', 'UNWORRIED', 'UNTRUSTING', 'UNFOLDED', 'UNNOTICED', 'UNEXPECTEDLY', 'UNMATCHED', 'UNFRIENDLY', 'UNAPOLOGETIC', 'UNALIGNED', 
                'UNEXPLAINED', 'UNORGANIZED', 'UNREPENTANT', 'UNSEEN', 'UNHINDERED', 'UNSATISFACTORY', 'UNMISTAKABLE', 'UNWANTED', 'UNFETTERED', 'UNSHAKEN', 'UNHARMED', 'UNGRATEFUL', 'UNRECOGNIZABLE', 'UNATTACHED', 'UNSPECTACULAR', 
                'UNCONVENTIONAL', 'UNPROMISING', 'UNREQUIRING', 'UNASSURED', 'UNRESTRICTED', 'UNTRIED', 'UNFATHOMABLE', 'UNREMARKABLY', 'UNFAMILIARITY', 'UNBREAKABLE', 'UNSUPPORTED', 'UNCOMPLICATED', 'UNFORGIVEN', 'UNCHALLENGED', 'UNPROTECTED','UNBELIEVABLE',
                'VACANT', 'VACATION', 'VACCINE', 'VALID', 'VALUE', 'VALVE', 'VARIETY', 'VARIABLE',
                'VAST', 'VEGETABLE', 'VEHICLE', 'VENUE', 'VERDICT', 'VERBAL', 'VERIFY', 'VERSION',
                'VERTICAL', 'VEST', 'VICTORY', 'VIDEO', 'VIEW', 'VIGIL', 'VILLAIN', 'VINE', 'VITAL',
                'VITAMIN', 'VOICE', 'VOLCANIC', 'VOLUME', 'VOLUNTEER', 'VOUCHER', 'VOW', 'VOWEL',
                'VULNERABLE', 'VANITY', 'VEIL', 'VOLUME', 'VAMPIRE', 'VINEGAR', 'VAPOR', 'VIRTUAL',
                'VINTAGE', 'VIGOR', 'VAGUE', 'VICINITY', 'VINEYARD', 'VIRUS', 'VACUUM', 'VANISH',
                'VANILLA', 'VALOR', 'VOUCH', 'VASTLY', 'VILLAGE', 'VIGOROUS', 'VIRTUALITY', 'VESTED',
                'VIGILANT', 'VALIDATE', 'VERBOSE', 'VANGUARD', 'VOLITION', 'VANGUARD', 'VIZIER',
                'VENERATE', 'VANQUISH', 'VERTEX', 'VALENTINE', 'VERB', 'VINTNER', 'VIBRATE', 'VIRILE',
                'VESTIGE', 'VIRULENT', 'VOCAL', 'VAGABOND', 'VINEYARD', 'VENTURE', 'VINTAGE', 'VIGNETTE',
                'VOTIVE', 'VARIANT', 'VIGOR', 'VINCULUM', 'VERIFIED', 'VULCAN', 'VICTOR', 'VULTURE',
                'VIRTUAL', 'VOLATILE', 'VASTNESS', 'VERITY', 'VAGABOND', 'VOTER', 'VOICEMAIL', 'VILLAGE',
                'VORACIOUS', 'VINTNER', 'VIGNETTE', 'VIVACIOUS', 'VERIFICATION', 'VOCATION', 'VIGILANCE',
                'VIRILITY', 'VANQUISH', 'VINCIBLE', 'VOTING', 'VITREOUS', 'VANGUARD', 'VINCENT', 'VITAMINS',
                'VERDANT', 'VAGUELY', 'VITALITY', 'VALENTINE', 'VIVID', 'VINE', 'VENISON', 'VOCABULARY',
                'VENERATE', 'VASTLY', 'VALOROUS', 'VINCULATE', 'VERIFIED', 'VERBALIZE', 'VILLAINOUS',
                'VITALS', 'VIRULENCE', 'VOLCANO', 'VIVACIOUS', 'VILLAIN', 'VENDOR', 'VINTAGE', 'VAGRANT',
                'VISCERAL', 'VALVE', 'VOLATILITY', 'VOTABLE', 'VERBALLY', 'VALISE', 'VILLAGE', 'VILLAGER',
                'VERIFIABLE', 'VEIN', 'VITALITY', 'VEINED', 'VIRILE', 'VARIANCE', 'VOLATILITY','VAGABONDS',
                'WAGON', 'WAIL', 'WAIT', 'WAIVE', 'WALK', 'WALL', 'WALLOW', 'WALNUT', 'WANT', 'WANTED', 'WANTING', 'WAR', 'WARM', 'WARMTH', 'WARRANT', 'WARS', 'WASH', 'WASTE', 'WATCH', 
                'WATER', 'WAVE', 'WAVES', 'WEAK', 'WEAR', 'WEARABLE', 'WEARY', 'WEB', 'WEDDING', 'WEEK', 'WEEKEND', 'WEIGH', 'WEIGHT', 'WELCOME', 'WELFARE', 'WELL', 'WELLNESS', 'WET', 'WHATEVER', 
                'WHEN', 'WHERE', 'WHICH', 'WHILE', 'WHISPER', 'WHITE', 'WHO', 'WHOLE', 'WHY', 'WIDE', 'WIDELY', 'WILD', 'WILDER', 'WILDEST', 'WILL', 'WILLOW', 'WIN', 'WIND', 'WINDY', 'WINDOW', 'WINNER', 
                'WISE', 'WISH', 'WISTFUL', 'WITH', 'WITHDRAW', 'WITNESS', 'WON', 'WONDER', 'WONDERFUL', 'WORD', 'WORK', 'WORKING', 'WORLD', 'WORRY', 'WORTH', 'WOUND', 'WRAP', 'WRITE', 'WRITING', 'WROTE', 
                'WRONG', 'WROTE', 'WASHED', 'WALKED', 'WONDERING', 'WELLKNOWN', 'WILDLY', 'WILLING', 'WONDERMENT', 'WILLFULLY', 'WATERFALL', 'WILLINGLY', 'WASHING', 'WORKPLACE', 'WORKSHOP', 'WIDEOPEN', 'WRIST', 
                'WAGER', 'WAITING', 'WARMING', 'WHOLESALE', 'WHEAT', 'WAILING', 'WASHABLE', 'WEIGHED', 'WHISTLE', 'WOUNDING', 'WALLET', 'WIRING', 'WHISKEY', 'WHEELS', 'WISHES', 'WORKED', 'WATERED', 'WONDERED', 'WAGERING', 
                'WETLAND', 'WORKOUT', 'WAXING', 'WORTHY', 'WEATHER', 'WAILS', 'WHICHES', 'WETNESS', 'WAXED', 'WORKING', 'WILLOWY', 'WONDER', 'WRAPPED', 'WALKS', 'WARMED', 'WILDLY', 'WIDEN', 'WORLDS', 'WORRIED', 'WIDE', 'WHIPPED', 
                'WALKING', 'WEARY', 'WEALTH', 'WRINKLED','WELDING','X-RAY', 'XENON', 'XYLOPHONE', 'XEROX', 'XENOPHOBIA', 'XENIAL', 'XENOGRAFT', 'XIPHOID', 'XENOPHILE', 'XEROPHYTE',
                'XANTHATE', 'XYST', 'XENOGENY', 'XENOPHOBIC', 'XEROPHILOUS', 'XEROGRAPHY', 'XYLEM', 'XANTHIC', 'XANTHIN', 'XERODERMA',
                'XIPHOIDAL', 'XANTHATES', 'XENOPHILES', 'XERANSIS', 'XERIC', 'XANTHOPHYLL', 'XERANTHUM', 'XYLENE', 'XENOLITH', 'XEROPHYTIC',
                'XENOBIOTIC', 'XYLOTOMOUS', 'XENODOCHIAL', 'XANTHOPHYLLS', 'XANTHOMA', 'XEROTHERMIC', 'XIPHIAS', 'XEROPHYTES', 'XENOGENESIS', 'XYLOGRAPH',
                'XANTHINE', 'XYSTUS', 'XEROGRAPHIC', 'XENOGENIC', 'XANTHOLITE', 'XENOTIME', 'XYLOSE', 'XYLIDINE', 'XENOTRANSPLANT', 'XENIC',
                'XERISCAPING', 'XEROPHAGIC', 'XYLOID', 'XEROSERE', 'XERARCH', 'XEROSTOMIA', 'XYLITOL', 'XEROPHYTE', 'XEROTIC', 'XENOPHONIC',
                'XEROPHYTISM', 'XENOPHILIC', 'XENOTRANSPLANTS', 'XYLOGRAPHY', 'XYLITIC', 'XIPHOIDALS', 'XEROPSYCHIC', 'XANTHYL', 'XANTHOID', 'XYLOIDAL',
                'XERANIC', 'XANTHOCHROMIA', 'XYLOPHAGOUS', 'XEROSIS', 'XEROMORPHIC', 'XEROTHERMY', 'XYLOL', 'XYLANS', 'XYLOGEN', 'XANTHOCHROMATIC',
                'XYLONITE', 'XENOBOTANY', 'XEROPHYTICALLY', 'XEROTROPIC', 'XYLOSTOMY', 'XANTHOSINE', 'XERANSES', 'XEROMORPH', 'XEROTHERM', 'XYLOGLYPH',
                'XYLOGENESIS', 'XYLITICALLY', 'XANTHOUS', 'XYLITON', 'XYLONITES', 'XYLOMETER', 'XYLAN', 'XEROSOMIA', 'XEROTHERMICALLY', 'XYLOSTOMOUS',
                'XYLIDINES', 'XENOGENICITY', 'XYLOCARP', 'XANTHINS', 'XYLONOMIC', 'XYLORIMETER', 'XYLIDITE', 'XYLANIC', 'XYLANASE', 'XANTHOMAS',
                'XYLOSTOMA', 'XYLANE', 'XYSTER', 'XYLOGENIC', 'XYLOSOMIA', 'XYLORIMETERS', 'XYLOSTOMATOUS', 'XEROCOPIC', 'XYLANORIMETER', 'XYLONOMY',
                'XYLOGRAPHERS', 'XANTHOMATOUS', 'XYLOGRAPHIC', 'XYLOGENICITY', 'XYLOGEOLOGY', 'XYLOPHONIC', 'XYLORIMETRY', 'XYLOCARPOUS', 'XYLANOGRAPHY', 'XYLOIDIC',
                'XERODERMIC', 'XYLIDINES', 'XEROSCAPES', 'XENOGAMY', 'XYLOSTOMAL', 'XYLOMORPHIC', 'XYLOSTOME', 'XYLANICALLY', 'XANTHATES', 'XYLOPLASTIC',
                'XYLOGENETIC', 'XEROSCAPED', 'XYLOCOPHAGIC', 'XANTHID', 'XYLOGRAPHS', 'XANTHOTIC', 'XYLOSTOMIES', 'XYLOCYTES', 'XYLOSCOPIC', 'XEROBIOTIC',
                'XEROGRAPHICALLY', 'XANTHIC', 'XYLOSTOMATOID', 'XYLOGEOLOGIC', 'XYLOTHORAX', 'XYLOCARPIC', 'XYLOSTOMIASIS', 'XYLORIMETRIC', 'XYLITICITY', 'XEROPHOBIC',
                'XERANTHIC', 'XYLOGLOBULIN', 'XYLORIMETRICAL', 'XERISCAPES', 'XENOGENE', 'XYLANOSOMIA', 'XYLONOMOUS', 'XYLORIMETRICALLY', 'XYLOCYTOLOGY', 'XYLOPHYTONIC',
                'XANTHOPHYLLIC', 'XYLOSTOMEOGRAPHY', 'XANTHICLY', 'XYLOCIDAL', 'XYLORIMETERIC', 'XEROSOMIAC', 'XANTHONE', 'XENOBIOTICALLY', 'XYLOPLASTICITY','XYLOGENOUS',
                'YARD', 'YAWN', 'YELLOW', 'YIELD', 'YACHT', 'YEAR', 'YOUNG', 'YOKE', 'YOGURT', 'YARDSTICK',
                'YOUTH', 'YESTERDAY', 'YEN', 'YEARN', 'YONDER', 'YOLK', 'YODEL', 'YAHOO', 'YIELDING', 'YOGI',
                'YAWNING', 'YOURS', 'YUCK', 'YAK', 'YEAST', 'YOUNGEST', 'YET', 'YACHTING', 'YELP', 'YOKELESS',
                'YAM', 'YOUTHFUL', 'YETI', 'YESTERYEAR', 'YAW', 'YON', 'YELLOWISH', 'YAWNER', 'YEARLY', 'YEW',
                'YUP', 'YANK', 'YURT', 'YUM', 'YELLOWED', 'YODELING', 'YAPPER', 'YOGIC', 'YESTER', 'YELLED',
                'YOUTHFULLY', 'YARDAGE', 'YUMMIEST', 'YAKKING', 'YIELDERS', 'YEARNED', 'YOGURTY', 'YAWNER', 'YANKING', 'YUGOSLAVIAN',
                'YAWPED', 'YOUTHFULNESS', 'YIELDABLE', 'YACHTER', 'YOKES', 'YEASTY', 'YAWP', 'YONKS', 'YESTERNIGHT', 'YUMMIER',
                'YOKING', 'YOUTHLESS', 'YACHTSMAN', 'YEALINGS', 'YEANLING', 'YENNING', 'YELLOWTAIL', 'YACKING', 'YESTERMORROW', 'YERBA',
                'YOGURTS', 'YOUNGSTERS', 'YENNER', 'YAWNSOME', 'YACHTED', 'YEALINGS', 'YELLOWER', 'YODELS', 'YOMIM', 'YETTING',
                'YEOMAN', 'YODELERS', 'YENINGS', 'YIELDLY', 'YAHWEH', 'YONKS', 'YAKIMA', 'YEASTIER', 'YANG', 'YIPS',
                'YIPPEE', 'YELPING', 'YATTER', 'YACKETY', 'YELPER', 'YORKER', 'YAPPING', 'YATTERING', 'YOUNGER', 'YOKELET',
                'YUPPY', 'YULETIDE', 'YANGTZE', 'YAWLESS', 'YELLOWS', 'YOLKS', 'YOGIN', 'YELLOWS', 'YOKEL', 'YUNTA',
                'YOGINS', 'YAGIS', 'YAMMER', 'YOUNGLING', 'YACHTS', 'YOUTHILY', 'YELLOWSKIN', 'YACK', 'YEMENITE', 'YENTA',
                'YOWZA', 'YEELING', 'YELLOWLEAF', 'YONNIES', 'YAKKED', 'YODLER', 'YEGGS', 'YAWLS', 'YOLKY', 'YUTZ',
                'YARNS', 'YUCKIER', 'YORKIST', 'YOUTHLESSLY', 'YEOMANLY', 'YOKELOAD', 'YAMMERING', 'YAKKER', 'YOBBO', 'YONDERLY',
                'YEOMEN', 'YELT', 'YATAGAN', 'YENTAISH', 'YAWPING', 'YOUTHWARDS', 'YAKISH', 'YARDARM', 'YELLOWEST', 'YIELDFUL',
                'YASHMAK', 'YODLER', 'YAKUTS', 'YUPSTER', 'YUZU', 'YANGIST', 'YACHTSWOMAN', 'YOUTHQUAKE', 'YAMBO', 'YESTREEN',
                'YEALD', 'YEX', 'YAWPERS', 'YEASTLINGS', 'YEUK', 'YOUTHLING', 'YOUNGKIN', 'YONI', 'YACKERS', 'YAPSTER',
                'YEASTILY', 'YANKTON', 'YELLOWCAKE', 'YONNY', 'YARMULKE', 'YELLOWBACK', 'YOUTHFICATION', 'YEASTILY', 'YESTERN','YAPS',
                'ZEBRA', 'ZEST', 'ZIGZAG', 'ZENITH', 'ZIP', 'ZIPPER', 'ZEAL', 'ZANY', 'ZOMBIE', 'ZODIAC',
                'ZONE', 'ZOOM', 'ZEPHYR', 'ZILLION', 'ZUCCHINI', 'ZINC', 'ZONAL', 'ZOOKEEPER', 'ZIGGURAT', 'ZEALOT',
                'ZYGOTE', 'ZIRCON', 'ZINNIA', 'ZAP', 'ZESTFUL', 'ZEBU', 'ZONK', 'ZEPPELIN', 'ZINGER', 'ZILCH',
                'ZONING', 'ZORRO', 'ZOO', 'ZODIACAL', 'ZIGZAGGING', 'ZERO', 'ZIN', 'ZIPLINE', 'ZONKED', 'ZAPPA',
                'ZOOGAMY', 'ZONATION', 'ZEUS', 'ZESTINESS', 'ZIRCONIUM', 'ZEITGEIST', 'ZONATE', 'ZAPPY', 'ZYMURGY', 'ZAPATEADO',
                'ZOONOSIS', 'ZEBRAS', 'ZOOGENY', 'ZESTY', 'ZIPPY', 'ZEBRASS', 'ZEOLITE', 'ZEPHYRS', 'ZOOS', 'ZEALOUS',
                'ZONER', 'ZYMOTIC', 'ZOONOMY', 'ZAZZ', 'ZANYNESS', 'ZOOT', 'ZINCATE', 'ZEOLITES', 'ZINKY', 'ZINGY',
                'ZOOLOGY', 'ZINCING', 'ZEROING', 'ZEP', 'ZYMOGEN', 'ZIRCONIA', 'ZOONIC', 'ZONDA', 'ZOANTHROPY', 'ZOOID',
                'ZYGOMORPHIC', 'ZAPPIER', 'ZOOPHILE', 'ZAX', 'ZANYISM', 'ZEROED', 'ZOOPHYTE', 'ZOMBIFY', 'ZINCITE', 'ZONINGLY',
                'ZOOPLASM', 'ZIT', 'ZIRCONITES', 'ZOOMORPHIC', 'ZEUGMA', 'ZYGOSIS', 'ZIRCONS', 'ZIBET', 'ZINE', 'ZOOIDAL',
                'ZOOLATRY', 'ZINCY', 'ZYMOSIS', 'ZEUSLIKE', 'ZABAGLIONE', 'ZIPLESS', 'ZIRCONIAN', 'ZINCIDES', 'ZOOCHEMICAL', 'ZYTHUM',
                'ZINCKING', 'ZITHER', 'ZIPPINESS', 'ZEEM', 'ZOOPHORIC', 'ZAG', 'ZYGOTIC', 'ZEPHRUS', 'ZESTIER', 'ZOMBISH',
                'ZOOTOMY', 'ZINCOPHILIC', 'ZETTABYTE', 'ZOOTHERAPY', 'ZONER', 'ZOOGONIC', 'ZEROES', 'ZONERS', 'ZIZZ', 'ZED',
                'ZYGOMATIC', 'ZONULATE', 'ZUCCHINIS', 'ZAMBONI', 'ZOOTROPE', 'ZOOPSYCHOLOGY', 'ZEBRALIKE', 'ZULU', 'ZOOCENTRIC', 'ZOMBIFICATION',
                'ZUCCHETTO', 'ZAZZY', 'ZINKIER', 'ZORIL', 'ZEBUAN', 'ZIGGURATS','ZEP'
                ]
            
    # Get matching suggestions based on the input word
    matching_suggestions = [s for s in dynamic_suggestions if s.startswith(word.upper())][:10]
    return matching_suggestions

# Update the show_suggestions function
def show_suggestions():
    global recognized_text
    clear_suggestions()  # Clear the old suggestions first

    # Split the recognized text into words
    words = recognized_text.split()
    
    if words:
        # Get the current word (last word in the recognized text)
        current_word = words[-1]
        
        # Get suggestions for the current word
        matching_suggestions = get_word_suggestions(current_word)

        # Update the suggestion buttons to show new suggestions
        for i in range(len(suggestion_buttons)):
            if i < len(matching_suggestions):
                suggestion_buttons[i].config(text=matching_suggestions[i], state=tk.NORMAL)
            else:
                suggestion_buttons[i].config(state=tk.DISABLED)

# Modify the select_suggestion function
def select_suggestion(index):
    global recognized_text
    # Get the selected suggestion
    selected_suggestion = suggestion_buttons[index].cget('text')

    # Split the recognized text into words
    words = recognized_text.split()

    if words:
        # Replace the last word with the selected suggestion
        words[-1] = selected_suggestion
        recognized_text = ' '.join(words)
        text_display.config(text=f"Sentence: {recognized_text}")
        clear_suggestions()
        show_suggestions()

# Function to create a button with updated styles
def create_rounded_button(text, command, row, col):
    button = tk.Button(button_frame, text=text, command=command, font=button_font, height=2, width=12, relief=None, borderwidth=4, bg='#d3d3d3', fg='#000000')  # Updated button background color to light gray
    button.grid(row=row, column=col, padx=20, pady=10, sticky="nsew")
    button.bind("<Enter>", lambda e: e.widget.config(bg='#b0b0b0'))  # Shade of gray for hover effect
    button.bind("<Leave>", lambda e: e.widget.config(bg='#d3d3d3'))

# Create suggestion buttons (max 3)
suggestion_frame = tk.Frame(content_frame, bg='#f7f7f7')
suggestion_frame.pack(pady=10, anchor='w', padx=20)
for i in range(10):
    btn = tk.Button(suggestion_frame, text="", font=button_font, height=2, width=10, state=tk.DISABLED, command=lambda i=i: select_suggestion(i))
    btn.grid(row=0, column=i, padx=10)
    suggestion_buttons.append(btn)

# Create buttons
button_canvas = tk.Canvas(content_frame, bg='#f7f7f7')
button_frame = tk.Frame(button_canvas, bg='#f7f7f7')

button_canvas.create_window((0, 0), window=button_frame, anchor='nw')
button_canvas.pack(side="right", fill="both", expand=True)
button_frame.bind("<Configure>", lambda e: button_canvas.configure(scrollregion=button_canvas.bbox("all")))

buttons = [
    ("Next", on_next),
    ("Space", on_space),
    ("Speak", on_speak),
    ("Translate", on_translate),
    ("Clear", on_clear),
    ("Backspace", on_backspace),
    ("Quit", on_quit)
]

for i, (text, command) in enumerate(buttons):
    row = i // 2
    col = i % 2
    create_rounded_button(text, command, row, col)

# Create label to display the webcam feed
image_label = tk.Label(content_frame)
image_label.pack(side=tk.TOP, padx=20, pady=10)

# Update the frame with the webcam feed and handle gesture recognition
def update_frame():
    global recognized_text, gesture_detected, last_character, current_character

    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        root.quit()
        return

    H, W, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            data_aux = []
            x_, y_ = [], []

            for lm in hand_landmarks.landmark:
                x_.append(lm.x)
                y_.append(lm.y)

            for lm in hand_landmarks.landmark:
                data_aux.append(lm.x - min(x_))
                data_aux.append(lm.y - min(y_))

            # Predict the character
            prediction = model.predict([np.asarray(data_aux)])
            predicted_label = prediction[0]

            # Check if the predicted label is in the dictionary
            if predicted_label in labels_dict:
                predicted_character = labels_dict[predicted_label]

                # Detect gesture
                if not gesture_detected:
                    if predicted_character != last_character:  # Check if it's different from the last character
                        current_character = predicted_character
                        last_character = predicted_character
                        gesture_detected = True
                else:
                    if predicted_character != last_character:  # Check if it's different from the last character
                        current_character = predicted_character
                        last_character = predicted_character

                # Draw a rectangle with a border around the detected gesture area
                x1 = int(min(x_) * W) - 10
                y1 = int(min(y_) * H) - 10
                x2 = int(max(x_) * W) + 10
                y2 = int(max(y_) * H) + 10

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Border color

                # Display the current character in the middle of the gesture box
                text_size = cv2.getTextSize(predicted_character, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
                # Display the current character in the top-left corner of the gesture box
                text_x = x1 + 10  # Add some padding from the left edge
                text_y = y1 + text_size[1] + 10  # Add some padding from the top edge
                cv2.putText(frame, predicted_character, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    else:
        # Reset detection when no hand is detected
        if gesture_detected:
            gesture_detected = False
            show_suggestions()  # Show suggestions when no gesture is detected

    # Convert the frame to RGB for Tkinter
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
    image_label.config(image=img)
    image_label.image = img
    root.after(30, update_frame)

# Start the Tkinter event loop
update_frame()
root.mainloop()