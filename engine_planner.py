# engine_planner.py - NLU, Multilingual detection, Context memory, Safety shield
import re

class PlannerEngine:
    def __init__(self):
        # Conversation history & context tracker
        self.context = {
            "current_site": None,
            "current_app": None,
            "current_url": None
        }
        # Language mapped replies matching detected user language
        self.detected_lang = "en"
        self.language_replies = {
            "en": {
                "confirm_payment": "⚠️ High safety action detected. Please confirm: Do you want to proceed with this payment?",
                "confirm_delete": "⚠️ Safety Warning: Are you sure you want to delete these files?",
                "confirm_email": "⚠️ Email dispatch requested. Do you confirm sending this email?",
                "confirm_power": "⚠️ System shutdown/restart requested. Confirm power action?",
                "safety_block": "Safety confirmation is required to proceed.",
                "plan_prefix": "I have created the execution plan:",
                "done": "✅ Task completed successfully."
            },
            "hi": {  # Hindi / Hinglish
                "confirm_payment": "⚠️ सुरक्षा चेतावनी: क्या आप इस भुगतान (payment) को आगे बढ़ाना चाहते हैं? कृपया पुष्टि करें।",
                "confirm_delete": "⚠️ सुरक्षा चेतावनी: क्या आप इन फ़ाइलों को डिलीट करना चाहते हैं?",
                "confirm_email": "⚠️ क्या आप यह ईमेल भेजना चाहते हैं?",
                "confirm_power": "⚠️ सिस्टम बंद या रीस्टार्ट करने की पुष्टि करें।",
                "safety_block": "आगे बढ़ने के लिए सुरक्षा मंजूरी आवश्यक है।",
                "plan_prefix": "मैंने कार्य की योजना बना ली है:",
                "done": "✅ कार्य सफलतापूर्वक पूरा हो गया।"
            },
            "mr": {  # Marathi / Marathinglish
                "confirm_payment": "⚠️ सुरक्षा चेतावणी: आपण हे पेमेंट करू इच्छिता? कृपया पुष्टी करा.",
                "confirm_delete": "⚠️ सुरक्षेची खात्री: आपण या फाइल्स डिलीट करू इच्छिता?",
                "confirm_email": "⚠️ आपण हा ईमेल पाठवू इच्छिता?",
                "confirm_power": "⚠️ कॉम्प्युटर बंद किंवा रीस्टार्ट करण्याची पुष्टी करा.",
                "safety_block": "पुढे जाण्यासाठी सुरक्षा पुष्टीकरण आवश्यक आहे.",
                "plan_prefix": "मी खालीलप्रमाणे नियोजन केले आहे:",
                "done": "✅ कार्य यशस्वीरित्या पूर्ण झाले."
            },
            "gu": {  # Gujarati
                "confirm_payment": "⚠️ પેમેન્ટ કરવા માટે કૃપા કરીને કન્ફર્મ કરો.",
                "confirm_delete": "⚠️ શું તમે આ ફાઇલો ડિલીટ કરવા માંગો છો?",
                "confirm_email": "⚠️ શું તમે આ ઈમેલ મોકલવા માંગો છો?",
                "confirm_power": "⚠️ કમ્પ્યુટર બંધ અથવા રીસ્ટાર્ટ કરવા માટે કન્ફર્મ કરો.",
                "safety_block": "આગળ વધવા માટે કન્ફર્મેશન જરૂરી છે.",
                "plan_prefix": "મેં આ કામ માટેની યોજના બનાવી છે:",
                "done": "✅ કામ સફળતાપૂર્વક પૂરું થયું છે."
            },
            "te": {  # Telugu
                "confirm_payment": "⚠️ పేమెంట్ చేయడానికి దయచేసి ధృవీకరించండి.",
                "confirm_delete": "⚠️ మీరు నిజంగానే ఈ ఫైళ్లను డిలీట్ చేయాలనుకుంటున్నారా?",
                "confirm_email": "⚠️ ఈ ఈమెయిల్ పంపడానికి మీ అనుమతి కావాలి.",
                "confirm_power": "⚠️ సిస్టమ్ రీస్టార్ట్ లేదా షట్‌డౌన్ చేయడానికి కన్ఫర్మ్ చేయండి.",
                "safety_block": "కొనసాగించడానికి అనుమతి అవసరం.",
                "plan_prefix": "నేను ప్రణాళిక సిద్ధం చేశాను:",
                "done": "✅ పని విజయవంతంగా పూర్తయింది."
            },
            "ta": {  # Tamil
                "confirm_payment": "⚠️ கட்டணம் செலுத்த உறுதிப்படுத்தவும்.",
                "confirm_delete": "⚠️ கோப்புகளை நீக்க விரும்புகிறீர்களா?",
                "confirm_email": "⚠️ இந்த மின்னஞ்சலை அனுப்ப ஒப்புதல் அளிக்கிறீர்களா?",
                "confirm_power": "⚠️ கணினியை அணைக்க அல்லது மறுதொடக்கம் செய்ய உறுதிப்படுத்தவும்.",
                "safety_block": "தொடர அனுமதி தேவை.",
                "plan_prefix": "செயல் திட்டம் உருவாக்கப்பட்டுள்ளது:",
                "done": "✅ பணி வெற்றிகரமாக முடிந்தது."
            },
            "kn": {  # Kannada
                "confirm_payment": "⚠️ ಪಾವತಿ ಮಾಡಲು ದಯವಿಟ್ಟು ಖಚಿತಪಡಿಸಿ.",
                "confirm_delete": "⚠️ ಈ ಫೈಲ್ಗಳನ್ನು ಅಳಿಸಲು ನೀವು ಖಚಿತವಾಗಿದ್ದೀರಾ?",
                "confirm_email": "⚠️ ಈ ಇಮೇಲ್ ಕಳುಹಿಸಲು ನೀವು ಅನುಮತಿಸುತ್ತೀರಾ?",
                "confirm_power": "⚠️ ಸಿಸ್ಟಮ್ ಸ್ಥಗಿತಗೊಳಿಸಲು ಖಚಿತಪಡಿಸಿ.",
                "safety_block": "ಮುಂದುವರಿಯಲು ಅನುಮತಿ ಬೇಕು.",
                "plan_prefix": "ಕಾರ್ಯ ಯೋಜನೆ ಸಿದ್ಧವಾಗಿದೆ:",
                "done": "✅ ಕೆಲಸ ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಂಡಿದೆ."
            },
            "ml": {  # Malayalam
                "confirm_payment": "⚠️ പേയ്‌മെന്റ് നടത്തുന്നതിനായി സ്ഥിരീകരിക്കുക.",
                "confirm_delete": "⚠️ ഈ ഫയലുകൾ ഇല്ലാതാക്കണമെന്ന് ഉറപ്പാണോ?",
                "confirm_email": "⚠️ ഈ ഇമെയിൽ അയക്കാൻ നിങ്ങൾ ആഗ്രഹിക്കുന്നുണ്ടോ?",
                "confirm_power": "⚠️ സിസ്റ്റം ഷട്ട്ഡൗൺ അല്ലെങ്കിൽ റീസ്റ്റാർട്ട് ചെയ്യാൻ സ്ഥിരീകരിക്കുക.",
                "safety_block": "തുടരുന്നതിന് സ്ഥിരീകരണം ആവശ്യമാണ്.",
                "plan_prefix": "പ്രവർത്തന പദ്ധതി തയ്യാറാണ്:",
                "done": "✅ ജോലി വിജയകരമായി പൂർത്തിയായി."
            },
            "bn": {  # Bengali
                "confirm_payment": "⚠️ পেমেন্ট করার জন্য অনুগ্রহ করে নিশ্চিত করুন।",
                "confirm_delete": "⚠️ আপনি কি ফাইলগুলি মুছে ফেলতে চান?",
                "confirm_email": "⚠️ আপনি কি এই ইমেলটি পাঠাতে চান?",
                "confirm_power": "⚠️ কম্পিউটার বন্ধ বা রিস্টার্ট করার বিষয়টি নিশ্চিত করুন।",
                "safety_block": "এগিয়ে যাওয়ার জন্য সম্মতি প্রয়োজন।",
                "plan_prefix": "আমি কাজের পরিকল্পনা তৈরি করেছি:",
                "done": "✅ কাজটি সফলভাবে সম্পন্ন হয়েছে।"
            },
            "pa": {  # Punjabi
                "confirm_payment": "⚠️ ਪੇਮੈਂਟ ਕਰਨ ਲਈ ਪੁਸ਼ਟੀ ਕਰੋ ਜੀ।",
                "confirm_delete": "⚠️ ਕੀ ਤੁਸੀਂ ਫਾਈਲਾਂ ਡਿਲੀਟ ਕਰਨਾ ਚਾਹੁੰਦੇ ਹੋ?",
                "confirm_email": "⚠️ ਕੀ ਤੁਸੀਂ ਇਹ ਈਮੇਲ ਭੇਜਣਾ ਚਾਹੁੰਦੇ ਹੋ?",
                "confirm_power": "⚠️ ਕੰਪਿਊਟਰ ਬੰਦ ਜਾਂ ਰੀਸਟਾਰਟ ਕਰਨ ਦੀ ਪੁਸ਼ਟੀ ਕਰੋ।",
                "safety_block": "ਅੱਗੇ ਵਧਣ ਲਈ ਮਨਜ਼ੂਰੀ ਲੋੜੀਂਦੀ ਹੈ।",
                "plan_prefix": "ਮੈਂ ਕਾਰਜ ਯੋਜਨਾ ਤਿਆਰ ਕੀਤੀ ਹੈ:",
                "done": "✅ ਕੰਮ ਸਫਲਤਾਪੂਰਵਕ ਪੂਰਾ ਹੋ ਗਿਆ ਹੈ।"
            },
            "ur": {  # Urdu
                "confirm_payment": "⚠️ ادائیگی کرنے کے لیے تصدیق کریں۔",
                "confirm_delete": "⚠️ کیا آپ فائلیں حذف کرنا چاہتے ہیں؟",
                "confirm_email": "⚠️ کیا آپ یہ ای میل بھیجنا چاہتے ہیں؟",
                "confirm_power": "⚠️ کمپیوٹر بند یا ری اسٹارٹ کرنے کی تصدیق کریں۔",
                "safety_block": "آگے بڑھنے کے لیے تصدیق درکار ہے۔",
                "plan_prefix": "میں نے کام کا منصوبہ تیار کر لیا ہے:",
                "done": "✅ کام کامیابی کے ساتھ مکمل ہو گیا۔"
            },
            "or": {  # Odia
                "confirm_payment": "⚠️ ପେମେଣ୍ଟ କରିବା ପାଇଁ ଦୟାକରି ନିଶ୍ଚିତ କରନ୍ତୁ।",
                "confirm_delete": "⚠️ ଆପଣ ଫାଇଲ୍ ଡିଲିଟ୍ କରିବାକୁ ଚାହାଁନ୍ତି କି?",
                "confirm_email": "⚠️ ଆପଣ ଏହି ଇମେଲ୍ ପଠାଇବାକୁ ଚାହାଁନ୍ତି କି?",
                "confirm_power": "⚠️ କମ୍ପ୍ୟୁଟର ବନ୍ଦ କିମ୍ବା ରିଷ୍ଟାର୍ଟ କରିବାକୁ ନିଶ୍ଚିତ କରନ୍ତୁ।",
                "safety_block": "ଆଗକୁ ବଢିବା ପାଇଁ ଅନୁମତି ଆବଶ୍ୟକ।",
                "plan_prefix": "କାର୍ଯ୍ୟ ଯୋଜନା ପ୍ରସ୍ତୁତ ହୋଇଛି:",
                "done": "✅ କାର୍ଯ୍ୟ ସଫଳତାର ସହ ସମାପ୍ତ ହେଲା।"
            }
        }

    def detect_language(self, text: str) -> str:
        """Detect query language, including support for mixed regional/English inputs."""
        txt = text.lower()
        # Look for script markers or distinct regional terms
        # Hindi/Hinglish indicators
        if any(w in txt for w in ["kholo", "kar", "chalu", "pe", "karo", "bhej", "hatao"]):
            self.detected_lang = "hi"
        # Marathi/Marathinglish indicators
        elif any(w in txt for w in ["मध्ये", "तयार", "पाठव", "दाखव", "बंद"]):
            self.detected_lang = "mr"
        # Telugu indicators
        elif any(w in txt for w in ["ఓపెన్", "చేయి", "వెళ్ళు", "చూపించు"]):
            self.detected_lang = "te"
        # Tamil indicators
        elif any(w in txt for w in ["திற", "செய்", "அனுப்பு", "நீக்கு"]):
            self.detected_lang = "ta"
        # Gujarati indicators
        elif any(w in txt for w in ["ખોલો", "કરો", "મોકલો", "બંધ"]):
            self.detected_lang = "gu"
        # Bengali indicators
        elif any(w in txt for w in ["খোল", "কর", "পাঠাও", "বন্ধ"]):
            self.detected_lang = "bn"
        # Punjabi indicators
        elif any(w in txt for w in ["ਖੋਲ੍ਹੋ", "ਕਰੋ", "ਭੇਜੋ", "ਹਟਾਓ"]):
            self.detected_lang = "pa"
        # Odia indicators
        elif any(w in txt for w in ["ଖୋଲନ୍ତୁ", "କରନ୍ତୁ", "ପଠାନ୍ତୁ"]):
            self.detected_lang = "or"
        else:
            self.detected_lang = "en"
        return self.detected_lang

    def get_localized_string(self, key: str) -> str:
        """Return reply in the active detected language, falling back to English if missing."""
        lang_dict = self.language_replies.get(self.detected_lang, self.language_replies["en"])
        return lang_dict.get(key, self.language_replies["en"].get(key, ""))

    def check_safety(self, goal_txt: str) -> str | None:
        """Determine if a confirmation shield is required before execution."""
        txt = goal_txt.lower()
        if any(w in txt for w in ["pay", "payment", "buy", "purchase", "check out", "खरीद", "पेमेंट"]):
            return self.get_localized_string("confirm_payment")
        if any(w in txt for w in ["delete", "remove", "erase", "trash", "डिलीट", "काढून", "नष्ट"]):
            return self.get_localized_string("confirm_delete")
        if any(w in txt for w in ["send email", "email send", "mail kar", "ईमेल भेज"]):
            return self.get_localized_string("confirm_email")
        if any(w in txt for w in ["shutdown", "restart", "reboot", "बंद करा"]):
            return self.get_localized_string("confirm_power")
        return None

    def plan_steps(self, text: str) -> tuple[list, dict]:
        """Parse natural goal input, resolve context memory, and output a detailed action plan."""
        txt = text.lower().strip()
        self.detect_language(text)
        
        steps = []
        intent_info = {"display": text}

        # ── Context Memory Resolution ─────────────────────────────────────────
        # "open X"
        open_match = re.match(r'^(?:open|kholo|chalu kar|shuru kar|start)\s+(.+)', txt)
        # Handle regional tail verbs: "chrome kholo", "vs code open kar"
        if not open_match:
            open_match = re.match(r'(.+?)\s+(?:kholo|open kar|chalu kar|open chey|open pannu)$', txt)

        if open_match:
            target = open_match.group(1).strip()
            # Check site vs app
            if target in ["chrome", "google chrome", "browser"]:
                steps = [
                    {"step": "open_application", "app": "chrome"},
                    {"step": "wait_time", "seconds": 1.5}
                ]
                self.context["current_app"] = "chrome"
                self.context["current_site"] = None
            elif target in ["file explorer", "explorer", "files", "my computer"]:
                steps = [
                    {"step": "open_application", "app": "explorer"},
                    {"step": "wait_time", "seconds": 1.0}
                ]
                self.context["current_app"] = "explorer"
                self.context["current_site"] = None
            elif target in ["notepad", "vs code", "vscode", "spotify", "calculator"]:
                steps = [
                    {"step": "open_application", "app": target},
                    {"step": "wait_time", "seconds": 1.5}
                ]
                self.context["current_app"] = target
                self.context["current_site"] = None
            else:
                # Treat as site
                url = f"https://www.{target}.com" if not target.startswith("http") else target
                steps = [
                    {"step": "navigate", "url": url},
                    {"step": "wait_time", "seconds": 2.0}
                ]
                self.context["current_site"] = target
                self.context["current_app"] = "chrome"
                self.context["current_url"] = url
            return steps, intent_info

        # "go to X" / "navigate to X"
        nav_match = re.match(r'^(?:go to|navigate to|visit|take me to|browse to)\s+(.+)', txt)
        if nav_match:
            target = nav_match.group(1).strip()
            url = f"https://www.{target}.com" if not target.startswith("http") else target
            steps = [
                {"step": "navigate", "url": url},
                {"step": "wait_time", "seconds": 2.0}
            ]
            self.context["current_site"] = target
            self.context["current_url"] = url
            self.context["current_app"] = "chrome"
            return steps, intent_info

        # "search X on Y"
        search_match = re.search(r'search\s+(.+?)\s+(?:on|in|using)\s+(.+)', txt)
        if search_match:
            query = search_match.group(1).strip()
            site = search_match.group(2).strip()
            url = ""
            if "flipkart" in site:
                url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
                self.context["current_site"] = "flipkart"
            elif "amazon" in site:
                url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
                self.context["current_site"] = "amazon"
            elif "youtube" in site:
                url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                self.context["current_site"] = "youtube"
            else:
                url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                self.context["current_site"] = "google"

            steps = [
                {"step": "navigate", "url": url},
                {"step": "wait_time", "seconds": 2.0}
            ]
            self.context["current_app"] = "chrome"
            self.context["current_url"] = url
            return steps, intent_info

        # Context-aware relative command: "search product" or "search headphones"
        relative_search = re.match(r'^(?:search|dhoond|dikhaye)\s+(.+)', txt)
        if relative_search:
            query = relative_search.group(1).strip()
            site = self.context.get("current_site")
            if site == "flipkart":
                url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
            elif site == "amazon":
                url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
            elif site == "youtube":
                url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            else:
                url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

            steps = [
                {"step": "navigate", "url": url},
                {"step": "wait_time", "seconds": 2.0}
            ]
            self.context["current_url"] = url
            return steps, intent_info

        # Context-aware navigation: "go to cart" or "cart kholo"
        if "cart" in txt or "basket" in txt:
            site = self.context.get("current_site")
            url = None
            if site == "flipkart":
                url = "https://www.flipkart.com/cart"
            elif site == "amazon":
                url = "https://www.amazon.in/gp/cart/view.html"
            
            if url:
                steps = [
                    {"step": "navigate", "url": url},
                    {"step": "wait_time", "seconds": 2.0}
                ]
                self.context["current_url"] = url
                return steps, intent_info

        # Basic browser actions
        if "back" in txt or "piche" in txt:
            return [{"step": "browser_back"}], intent_info
        if "forward" in txt or "aage" in txt:
            return [{"step": "browser_forward"}], intent_info
        if "refresh" in txt or "reload" in txt:
            return [{"step": "browser_refresh"}], intent_info
        if "scroll down" in txt or "niche scroll" in txt:
            return [{"step": "scroll", "direction": "down"}], intent_info
        if "scroll up" in txt or "upar scroll" in txt:
            return [{"step": "scroll", "direction": "up"}], intent_info
        if "screenshot" in txt or "photo" in txt:
            return [{"step": "screenshot"}], intent_info

        # Key pressing / Keyboard controls
        if txt.startswith("press "):
            key_name = txt.replace("press ", "").strip()
            return [{"step": "press_key", "key": key_name}], intent_info

        # Text input / Typing
        if txt.startswith("type "):
            typed_val = text[5:].strip()
            return [{"step": "type_query", "query": typed_val}], intent_info

        # Default fallback: Google search query
        url = f"https://www.google.com/search?q={txt.replace(' ', '+')}"
        steps = [
            {"step": "navigate", "url": url},
            {"step": "wait_time", "seconds": 2.0}
        ]
        return steps, intent_info
