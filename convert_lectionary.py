from icalendar import Calendar, Event
from collections import defaultdict
from datetime import date, timedelta
import datetime
import re

summary_map = {
    # Advent
    "Advent 1": "First Sunday",
    "Advent 2": "Second Sunday",
    "Advent 3": "Third Sunday",
    "Advent 4": "Fourth Sunday",

    # Christmas
    "Christmas Day": "Christmas Day",
    "Christmas 1": "First Sunday",
    "Christmas 2": "Second Sunday",
    "Christmas 3": "Third Sunday",
    "Christmas 4": "Fourth Sunday",

    # Epiphany
    "Epiphany": "Epiphany",
    "Epiphany 1": "First Sunday",
    "Epiphany 2": "Second Sunday",
    "Epiphany 3": "Third Sunday",
    "Epiphany 4": "Fourth Sunday",
    "Epiphany 5": "Fifth Sunday",
    "Epiphany 6": "Sixth Sunday",
    "Epiphany 7": "Seventh Sunday",
    "Epiphany Last": "Last Sunday",
    "Baptism of Our Lord": "First Sunday",  # 特殊情況，仍歸到 First Sunday
    "Transfiguration": "Last Sunday",      # 特殊情況，仍歸到 Last Sunday

    # Lent
    "Lent 1": "First Sunday",
    "Lent 2": "Second Sunday",
    "Lent 3": "Third Sunday",
    "Lent 4": "Fourth Sunday",
    "Lent 5": "Fifth Sunday",
    "Ash Wednesday": "Ash Wednesday",
    "Palm Sunday": "Palm Sunday",
    "Good Friday": "Good Friday",
    "Maundy Thursday": "Maundy Thursday",
    "Holy Saturday": "Holy Saturday",

    # Easter
    "Easter Sunday": "Easter Sunday",
    "Easter 2": "Second Sunday",
    "Easter 3": "Third Sunday",
    "Easter 4": "Fourth Sunday",
    "Easter 5": "Fifth Sunday",
    "Ascension": "Ascension",

    # Pentecost
    "Pentecost Sunday": "Pentecost Sunday",
    # "Pentecost 1": "First Sunday",
    # "Pentecost 2": "Second Sunday",
    # "Pentecost 3": "Third Sunday",
    # "Pentecost 4": "Fourth Sunday",
    # "Pentecost 5": "Fifth Sunday",
    # "Pentecost 6": "Sixth Sunday",
    # "Pentecost 7": "Seventh Sunday",
    # "Pentecost 8": "Eighth Sunday",
    # "Pentecost 9": "Ninth Sunday",
    # "Pentecost 10": "Tenth Sunday",
    # "Pentecost 11": "Eleventh Sunday",
    # "Pentecost 12": "Twelfth Sunday",
    # "Pentecost 13": "Thirteenth Sunday",
    # "Pentecost 14": "Fourteenth Sunday",
    # "Pentecost 15": "Fifteenth Sunday",
    # "Pentecost 16": "Sixteenth Sunday",
    # "Pentecost 17": "Seventeenth Sunday",
    # "Pentecost 18": "Eighteenth Sunday",
    # "Pentecost 19": "Nineteenth Sunday",
    # "Pentecost 20": "Twentieth Sunday",

    # Ordinary / Proper / Trinity
    "Ordinary 1": "First Sunday",
    "Ordinary 2": "Second Sunday",
    "Ordinary 3": "Third Sunday",
    "Ordinary 4": "Fourth Sunday",
    "Ordinary 5": "Fifth Sunday",
    "Ordinary 6": "Sixth Sunday",
    "Ordinary 7": "Seventh Sunday",
    "Ordinary 8": "Eighth Sunday",
    "Ordinary 9": "Ninth Sunday",
    "Ordinary 10": "Tenth Sunday",
    "Ordinary 11": "Eleventh Sunday",
    "Ordinary 12": "Twelfth Sunday",
    "Ordinary 13": "Thirteenth Sunday",
    "Ordinary 14": "Fourteenth Sunday",
    "Ordinary 15": "Fifteenth Sunday",
    "Ordinary 16": "Sixteenth Sunday",
    "Ordinary 17": "Seventeenth Sunday",
    "Ordinary 18": "Eighteenth Sunday",
    "Ordinary 19": "Nineteenth Sunday",
    "Ordinary 20": "Twentieth Sunday",

    "Proper 1": "First Sunday",
    "Proper 2": "Second Sunday",
    "Proper 3": "Third Sunday",
    "Proper 4": "Fourth Sunday",
    "Proper 5": "Fifth Sunday",
    "Proper 6": "Sixth Sunday",
    "Proper 7": "Seventh Sunday",
    "Proper 8": "Eighth Sunday",
    "Proper 9": "Ninth Sunday",
    "Proper 10": "Tenth Sunday",
    "Proper 11": "Eleventh Sunday",
    "Proper 12": "Twelfth Sunday",
    "Proper 13": "Thirteenth Sunday",
    "Proper 14": "Fourteenth Sunday",
    "Proper 15": "Fifteenth Sunday",
    "Proper 16": "Sixteenth Sunday",
    "Proper 17": "Seventeenth Sunday",
    "Proper 18": "Eighteenth Sunday",
    "Proper 19": "Nineteenth Sunday",
    "Proper 20": "Twentieth Sunday",

    "Trinity Sunday": "Trinity Sunday",
    "Christ the King": "Christ the King"
}

# === 英中節期與特殊節日對照表 ===
season_map = {
    # === 特殊節日 ===
    "Last Sunday of End Time-Christ  King": "末期最後一主日-基督君王主日",
    "Christmas Eve": "平安夜",  
    "Nativity of Our Lord": "主降生日", 
    "Reformation Day": "宗教改革日",
    "Reformation": "宗教改革日",
    "Christ the King": "基督君王主日",
    "Christ King": "基督君王主日",
    "Christ  King": "基督君王主日",
    "Christ the King Sunday": "基督君王主日",
    "All Saints": "古聖紀念日", 
    "All Saints Day": "古聖紀念日",
    "All Saints' Day": "古聖紀念日",
    "All Saints'": "古聖紀念日",
    "Ash Wednesday": "聖灰日",
    "Palm Sunday": "棕枝主日",
    "Maundy Thursday": "主立聖餐日", 
    "Holy Thursday": "主立聖餐日",
    "Good Friday": "受難日",
    "Holy Saturday": "聖週六",
    "Easter Vigil": "復活前夕守夜",
    "Easter Sunday": "復活節", 
    "Easter Day": "復活節",
    "Pentecost Sunday": "聖靈降臨主日",  
    "Day of Pentecost": "聖靈降臨主日",
    "Holy Trinity": "三一主日",
    "Trinity Sunday": "三一主日",
    "Trinity": "三一主日",
    "Presentation of Our Lord": "主奉獻日",
    "Annunciation": "天使報喜日",
    "Visitation": "探望日",
    "Nativity of John the Baptist": "施洗約翰誕辰",
    "Conversion of St. Paul": "聖保羅歸主日",
    "St. Michael and All Angels": "聖米迦勒與眾天使日",
    "Transfiguration of Our Lord": "登山變像主日",  
    "Transfiguration": "登山變像主日",
    "The Baptism of Our Lord": "耶穌受洗主日",  
    "Baptism of Our Lord": "耶穌受洗主日",
    "Epiphany of Our Lord": "主顯日",  
    "Ascension": "基督升天日", 
    "Ascension of Our Lord": "基督升天日",
    "Ascension of our Lord": "基督升天日",
    "Christmas Day": "聖誕節",
    "Chistmas Day": "聖誕節",
    "Last Judgment": "末日審判主日",
    "Last Sunday in the Church Year": "教會年最後一主日",
    "Last Sunday of the Church Year": "教會年最後一主日",
    "Last Sunday of End Time": "末期最後一主日",
    "Resurrection of our Lord": "耶穌基督復活了！",
    "Martin Luther's birthday": "馬丁路德誕辰",
    "None": "",
    "Saints Triumphant": "聖徒得勝日",
    "Sunday of the Passion": "受難主日",
    "Thanksgiving Day": "感恩節",
    "Thanksgiving": "感恩節",
    "Easter Sunday - Dawn": "復活節早晨",
    "Easter Dawn": "復活節早晨",
    # === 季節 (依據講義譯名) ===
    "Advent": "將臨期",
    "Christmas": "聖誕期",
    "Epiphany": "顯現期", 
    "Ephphany": "顯現期",
    "Lent": "預苦期",
    "Holy Week": "聖週",
    "Easter": "復活期", 
    "Pentecost": "聖靈降臨期",
    "Ordinary Time": "常年期",
    "End Time": "末期"
}

# === 依據講義新增：節期意義對照表 ===
season_meaning_map = {
    "Advent": "將臨期—預備慶祝基督的降生，預備等候基督的再臨。",
    "Christmas": "聖誕期—慶賀基督降生，展望與基督永恆同在。",
    "Epiphany": "顯現期-慶賀基督顯明身份，開展其在世的工作。",
    "Ephphany": "顯現期-慶賀基督顯明身份，開展其在世的工作。",
    "Lent": "預苦期-藉憂傷與悔罪預備等候為我們受苦受死的基督。",
    "Holy Week": "聖週-藉憂傷與悔罪預備等候為我們受苦受死的基督。",
    "Easter": "復活期-慶賀復活的基督已為我們勝過罪與死亡。",
    "Pentecost": "聖靈降臨期-慶賀主應許的聖靈降臨。",
    "Ordinary Time": "常年期-聖靈降臨後常年期，在聖靈光照中持續學習聖道。",
    "End Time": "聖靈降臨期-慶賀主應許的聖靈降臨。"
}

# 2. 序數詞對照表
ordinal_map = {
    "First": "第一",
    "Second": "第二",
    "Third": "第三",
    "Fourth": "第四",
    "Fifth": "第五",
    "Sixth": "第六",
    "Seventh": "第七",
    "Eighth": "第八",
    "Ninth": "第九",
    "Tenth": "第十",
    "Eleventh": "第十一",
    "Twelfth": "第十二",
    "Twelth": "第十二",
    "Thirteenth": "第十三",
    "Fourteenth": "第十四",
    "Fourtheenth": "第十四",
    "Fifteenth": "第十五",
    "Sixteenth": "第十六",
    "Seventeenth": "第十七",
    "Eighteenth": "第十八",
    "Nineteenth": "第十九",
    "Twentieth": "第二十",
    "Twent-first": "第二十一",
    "Twenty-first": "第二十一",
    "Twenty-second": "第二十二", 
    "Twenty-third": "第二十三", 
    "Twenty-fourth": "第二十四", 
    "Twenty-fifth": "第二十五", 
    "Twenty-sixth": "第二十六", 
    "Twenty-seventh": "第二十七", 
    "Twenty-eighth": "第二十八", 
    "Twenty-ninth": "第二十九", 
    "Thirtieth": "第三十"
}

# 給生成事件用的序數詞對應表
ordinal_map_2 = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
    "eleventh": 11,
    "twelfth": 12,
    "thirteenth": 13,
    "fourteenth": 14,
    "fifteenth": 15,
    "sixteenth": 16,
    "seventeenth": 17,
    "eighteenth": 18,
    "nineteenth": 19,
    "twentieth": 20,
    "twenty-first": 21,
    "twenty-second": 22,
    "twenty-third": 23,
    "twenty-fourth": 24,
    "twenty-fifth": 25,
}
# === 新增：阿拉伯數字轉中文數字對照表 ===
arabic_to_zh = {
    "1": "一", "2": "二", "3": "三", "4": "四", "5": "五", "6": "六", "7": "七", "8": "八", "9": "九", "10": "十",
    "11": "十一", "12": "十二", "13": "十三", "14": "十四", "15": "十五", "16": "十六", "17": "十七", "18": "十八", "19": "十九", "20": "二十",
    "21": "二十一", "22": "二十二", "23": "二十三", "24": "二十四", "25": "二十五", "26": "二十六", "27": "二十七", "28": "二十八", "29": "二十九", "30": "三十",
    "31": "三十一", "32": "三十二", "33": "三十三", "34": "三十四"
}
# === 英文 → 中文 書卷對照表 ===
book_map = {
    "Genesis": "創世記","Exodus": "出埃及記","Leviticus": "利未記","Numbers": "民數記",
    "Deuteronomy": "申命記","Joshua": "約書亞記","Judges": "士師記","Ruth": "路得記",
    "1 Samuel": "撒母耳記上","2 Samuel": "撒母耳記下","1 Kings": "列王紀上","2 Kings": "列王紀下",
    "1 Chronicles": "歷代志上","2 Chronicles": "歷代志下","Ezra": "以斯拉記","Nehemiah": "尼希米記",
    "Esther": "以斯帖記","Job": "約伯記","Psalm": "詩篇","Proverbs": "箴言",
    "Ecclesiastes": "傳道書","Song of Solomon": "雅歌","Isaiah": "以賽亞書","Jeremiah": "耶利米書",
    "Lamentations": "耶利米哀歌","Ezekiel": "以西結書","Daniel": "但以理書","Hosea": "何西阿書",
    "Joel": "約珥書","Amos": "阿摩司書","Obadiah": "俄巴底亞書","Jonah": "約拿書",
    "Micah": "彌迦書","Nahum": "那鴻書","Habakkuk": "哈巴谷書","Zephaniah": "西番雅書",
    "Haggai": "哈該書","Zechariah": "撒迦利亞書","Malachi": "瑪拉基書",
    "Matthew": "馬太福音","Mark": "馬可福音","Luke": "路加福音","John": "約翰福音",
    "Acts": "使徒行傳","Romans": "羅馬書","1 Corinthians": "哥林多前書","2 Corinthians": "哥林多後書",
    "Galatians": "加拉太書","Ephesians": "以弗所書","Philippians": "腓立比書","Colossians": "歌羅西書",
    "1 Thessalonians": "帖撒羅尼迦前書","2 Thessalonians": "帖撒羅尼迦後書","1 Timothy": "提摩太前書",
    "2 Timothy": "提摩太後書","Titus": "提多書","Philemon": "腓利門書","Hebrews": "希伯來書",
    "James": "雅各書","1 Peter": "彼得前書","2 Peter": "彼得後書","1 John": "約翰一書",
    "2 John": "約翰二書","3 John": "約翰三書","Jude": "猶大書","Revelation": "啟示錄"
}

# === 英文 → 中文 片語對照表 ===
phrase_map = {
    "Last Sunday of End Time-Christ  King": "末期最後一主日-基督君王日",
    "Last Sunday of End Time-Christ King": "末期最後一主日-基督君王日",
    "Lessons and Psalm": "經課與詩篇",
    "Supplemental Lectionary": "補充經課",
    "Hymn of the Day": "今日詩歌",
    "Hymn of  Day": "今日詩歌",
    "FIRST READING": "第一部分讀經",
    "SECOND READING": "第二部分讀經",
    "GOSPEL": "福音經課",
    "PSALM": "詩篇",
    "Reading": "讀經課",  # 處理 Reading
    "Sunday": "主日"      # 處理 Sunday
}

# === 英文 → 中文 顏色對照表 ===
color_map = {
    "Red": "紅色","Green": "綠色","Blue": "藍色","Yellow": "黃色","Purple": "紫色",
    "Orange": "橙色","Black": "黑色","White": "白色","Gray": "灰色","Brown": "棕色","Pink": "粉紅色"
}

# === 詩歌對照表 ===
hymn_map = {
    # Advent (將臨期：盼望、等待)
    ("Advent", "First Sunday"): [
        "約書亞樂團：《打開眾城門》",
        "讚美之泉：《我們等候愛慕耶穌》",
        "小羊詩歌：《抬頭仰望》"
    ],
    ("Advent", "Second Sunday"): [
        "約書亞樂團：《祢是我盼望》",
        "讚美之泉：《有一件事》",
        "小羊詩歌：《我要等候耶和華》"
    ],
    ("Advent", "Third Sunday"): [
        "約書亞樂團：《祢的呼喚》",
        "讚美之泉：《聽見這世代的呼喚》",
        "小羊詩歌：《新郎的呼喚》"
    ],
    ("Advent", "Fourth Sunday"): [
        "約書亞樂團：《相信擁抱》",
        "讚美之泉：《深深地敬拜》",
        "小羊詩歌：《新婦的祈禱》"
    ],
    ("Advent", None): [
        "約書亞樂團：《抓住永恆》",
        "讚美之泉：《恢復敬拜》",
        "小羊詩歌：《奇妙的預備》"
    ],

    # Christmas (聖誕期：降生、歡慶)
    ("Christmas", "Christmas Eve"): [
        "約書亞樂團：《台北的聖誕節》",
        "讚美之泉：《我們歡慶聖誕》",
        "小羊詩歌：《彌賽亞》"
    ],
    ("Christmas", "Christmas Day"): [
        "約書亞樂團：《榮美的救主》",
        "讚美之泉：《是耶穌的名》",
        "小羊詩歌：《祂的兒子》"
    ],
    ("Christmas", "First Sunday"): [
        "約書亞樂團：《這是真愛》",
        "讚美之泉：《最大的福分》",
        "小羊詩歌：《耶穌,萬名之上的名》"
    ],
    ("Christmas", "Second Sunday"): [
        "約書亞樂團：《找到我》",
        "讚美之泉：《I Will Sing Hallelujah [我要唱哈利路亞]》",
        "小羊詩歌：《你們要讚美耶和華》"
    ],
    ("Christmas", "Third Sunday"): [
        "約書亞樂團：《天父祢都看顧》",
        "讚美之泉：《天父祢愛我》",
        "小羊詩歌：《耶穌基督是主》"
    ],
    ("Christmas", "Fourth Sunday"): [
        "約書亞樂團：《大過一切的愛》",
        "讚美之泉：《是祢，耶穌》",
        "小羊詩歌：《榮耀都歸神羔羊》"
    ],
    ("Christmas", None): [
        "約書亞樂團：《就這樣沉浸在祢愛中》",
        "讚美之泉：《大山可以挪開》",
        "小羊詩歌：《祢是配》"
    ],

    # Epiphany (主顯節：顯現、光照、創造)
    ("Epiphany", "Epiphany"): [
        "約書亞樂團：《我神真偉大》",
        "讚美之泉：《榮耀至高神》",
        "小羊詩歌：《萬民同來敬拜》"
    ],
    ("Epiphany", "First Sunday"): [
        "約書亞樂團：《榮美輝煌》",
        "讚美之泉：《榮耀榮耀榮耀》",
        "小羊詩歌：《願祢的國降臨》"
    ],
    ("Epiphany", "Second Sunday"): [
        "約書亞樂團：《主祢是我們的太陽》",
        "讚美之泉：《Holy, Holy [聖潔榮耀主]》",
        "小羊詩歌：《我是祢所造》"
    ],
    ("Epiphany", "Third Sunday"): [
        "約書亞樂團：《在呼召我之處》",
        "讚美之泉：《我的耶穌》",
        "小羊詩歌：《哦主,祢名何其美》"
    ],
    ("Epiphany", "Fourth Sunday"): [
        "約書亞樂團：《讓祂的喜樂充滿你》",
        "讚美之泉：《愛使我們勇敢》",
        "小羊詩歌：《我的幫助從何而來＋願神興起》"
    ],
    ("Epiphany", "Fifth Sunday"): [
        "約書亞樂團：《如祢》",
        "讚美之泉：《偉大的神》",
        "小羊詩歌：《哈利路!主我神作王了》"
    ],
    ("Epiphany", "Sixth Sunday"): [
        "約書亞樂團：《通往祢的路》",
        "讚美之泉：《聖潔和榮耀》",
        "小羊詩歌：《永遠稱頌祢》"
    ],
    ("Epiphany", "Seventh Sunday"): [
        "約書亞樂團：《敬畏的心》",
        "讚美之泉：《為榮耀的創造》",
        "小羊詩歌：《我願意》"
    ],
    ("Epiphany", "Eighth Sunday"): [
        "約書亞樂團：《我安然居住》",
        "讚美之泉：《不停讚美祢》",
        "小羊詩歌：《倚靠祢》"
    ],
    ("Epiphany", "Ninth Sunday"): [
        "約書亞樂團：《祂是你的幫助》",
        "讚美之泉：《披上讚美衣》",
        "小羊詩歌：《Faith Over Fear》"
    ],
    ("Epiphany", "Tenth Sunday"): [
        "約書亞樂團：《主你永遠與我同在》",
        "讚美之泉：《向我的神獻上感謝》",
        "小羊詩歌：《我知道祢愛我》"
    ],
    ("Epiphany", "Last Sunday"): [
        "約書亞樂團：《恢復榮耀》",
        "讚美之泉：《在祢沒有難成的事》",
        "小羊詩歌：《弟兄和睦同居》"
    ],
    ("Epiphany", "Transfiguration"): [
        "約書亞樂團：《榮美輝煌》",
        "讚美之泉：《我是承載神榮耀的器皿》",
        "小羊詩歌：《弟兄和睦同居》"
    ],
    ("Epiphany", None): [
        "約書亞樂團：《雙膝跪下觸摸天堂》",
        "讚美之泉：《大聲敬拜》",
        "小羊詩歌：《永遠稱謝祢(台)》"
    ],

    # Lent (預苦期：十架、悔改、救恩)
    ("Lent", "First Sunday"): [
        "約書亞樂團：《恩典之洋（即使我仍會軟弱）》",
        "讚美之泉：《煉淨過的生命》",
        "小羊詩歌：《一粒麥子》"
    ],
    ("Lent", "Second Sunday"): [
        "約書亞樂團：《憐憫的愛》",
        "讚美之泉：《十架的大能》",
        "小羊詩歌：《曠野之歌》"
    ],
    ("Lent", "Third Sunday"): [
        "約書亞樂團：《我要愛慕你》",
        "讚美之泉：《我的生命獻給祢》",
        "小羊詩歌：《我向祢回轉》"
    ],
    ("Lent", "Fourth Sunday"): [
        "約書亞樂團：《回家》",
        "讚美之泉：《那麼深的渴慕》",
        "小羊詩歌：《神啊,我渴慕祢》"
    ],
    ("Lent", "Fifth Sunday"): [
        "約書亞樂團：《堅強的愛》",
        "讚美之泉：《深愛耶穌》",
        "小羊詩歌：《跟隨到底》"
    ],
    ("Lent", "Ash Wednesday"): [
        "約書亞樂團：《餘燼》",
        "讚美之泉：《深不見底的愛》",
        "小羊詩歌：《為我造清潔的心》"
    ],
    ("Lent", None): [
        "約書亞樂團：《我願降服》",
        "讚美之泉：《浪子的我》",
        "小羊詩歌：《主啊,我們自卑》"
    ],

    # Holy Week (聖週：立約、受難、安靜)
    ("Holy Week", "Palm Sunday"): [
        "約書亞樂團：《和散那》",
        "讚美之泉：《和散那，歡迎君王》",
        "小羊詩歌：《錫安大道》"
    ],
    ("Holy Week", "Maundy Thursday"): [
        "約書亞樂團：《父的筵席》",
        "讚美之泉：《愛祢直到永遠》",
        "小羊詩歌：《何等深情》"
    ],
    ("Holy Week", "Good Friday"): [
        "約書亞樂團：《神羔羊配得》",
        "讚美之泉：《我是被主重價買回的人》",
        "小羊詩歌：《雞叫的時候》"
    ],
    ("Holy Week", "Holy Saturday"): [
        "約書亞樂團：《安靜》",
        "讚美之泉：《藏身之處》",
        "小羊詩歌：《藏身祢的懷裏》"
    ],
    ("Holy Week", None): [
        "約書亞樂團：《無盡的愛》",
        "讚美之泉：《盡情地微笑》",
        "小羊詩歌：《有誰》"
    ],

    # Easter (復活期：復活、得勝、掌權)
    ("Easter", "Easter Sunday"): [
        "約書亞樂團：《Happy Day》",
        "讚美之泉：《得勝的宣告》",
        "小羊詩歌：《復活.升天.大使命》"
    ],
    ("Easter", "Second Sunday"): [
        "約書亞樂團：《耶穌基督》",
        "讚美之泉：《高舉雙手敬拜》",
        "小羊詩歌：《主,我相信》"
    ],
    ("Easter", "Third Sunday"): [
        "約書亞樂團：《重來的力量》",
        "讚美之泉：《不管世界如何看我》",
        "小羊詩歌：《站起來》"
    ],
    ("Easter", "Fourth Sunday"): [
        "約書亞樂團：《上帝能夠》",
        "讚美之泉：《敬拜耶穌》",
        "小羊詩歌：《祢與我同在》"
    ],
    ("Easter", "Fifth Sunday"): [
        "約書亞樂團：《甦醒》",
        "讚美之泉：《我敬拜祢，耶穌》",
        "小羊詩歌：《有祢同行》"
    ],
    ("Easter", "Sixth Sunday"): [
        "約書亞樂團：《跨越》",
        "讚美之泉：《我活著要稱頌祢》",
        "小羊詩歌：《與祢一起飛翔》"
    ],
    ("Easter", "Seventh Sunday"): [
        "約書亞樂團：《基督是我滿足》",
        "讚美之泉：《與祢漫步》",
        "小羊詩歌：《誰能使我與神的愛隔絕》"
    ],
    ("Easter", "Ascension"): [
        "約書亞樂團：《向列國宣告》",
        "讚美之泉：《爭戰得勝在於祢》",
        "小羊詩歌：《寶座》"
    ],
    ("Easter", "Ascension of Our Lord"): [
        "約書亞樂團：《向列國宣告》",
        "讚美之泉：《爭戰得勝在於祢》",
        "小羊詩歌：《寶座》"
    ],
    ("Easter", None): [
        "約書亞樂團：《榮美的救主》",
        "讚美之泉：《Mighty [祢愛有能力]》",
        "小羊詩歌：《我的靈要醒起》"
    ],

    # Pentecost (聖靈降臨節：聖靈、恩雨、賜福)
    ("Pentecost", "Pentecost Sunday"): [
        "約書亞樂團：《降下你恩雨》",
        "讚美之泉：《有你在的地方》",
        "小羊詩歌：《點燃》"
    ],
    ("Pentecost", None): [
        "約書亞樂團：《天國文化復興》",
        "讚美之泉：《Reach One More [再贏得一個靈魂]》",
        "小羊詩歌：《有一道河》"
    ],

    # Ordinary Time (常年期/特殊節日：三一、信心、感謝、君王)
    ("Ordinary Time", "Trinity Sunday"): [
        "約書亞樂團：《榮美輝煌》",
        "讚美之泉：《三一頌》",
        "小羊詩歌：《聖哉全能主》"
    ],
    ("Ordinary Time", "Saints Triumphant"): [
        "約書亞樂團：《無價至寶》",
        "讚美之泉：《我是天父的孩子》",
        "小羊詩歌：《有福的人》"
    ],
    ("Ordinary Time", "Last Judgment"): [
        "約書亞樂團：《直到世界盡頭》",
        "讚美之泉：《我們的神》",
        "小羊詩歌：《全能神永遠掌權》"
    ],
    ("Ordinary Time", "Christ King"): [
        "約書亞樂團：《為著你的榮耀》",
        "讚美之泉：《耶和華作王》",
        "小羊詩歌：《神掌權》"
    ],
    ("Ordinary Time", "Christ the King"): [
        "約書亞樂團：《為著你的榮耀》",
        "讚美之泉：《耶和華作王》",
        "小羊詩歌：《神掌權》"
    ],
    ("Ordinary Time", "Reformation"): [
        "約書亞樂團：《恢復榮耀》",
        "讚美之泉：《我選擇喜樂》",
        "小羊詩歌：《耶和華我的山寨》"
    ],
    ("Ordinary Time", "All Saints"): [
        "約書亞樂團：《我們獻上》",
        "讚美之泉：《謝謝你成為我的家》",
        "小羊詩歌：《眾山怎樣圍繞耶路撒冷》"
    ],
    ("Ordinary Time", "Thanksgiving"): [
        "約書亞樂團：《恩典之流》",
        "讚美之泉：《獻上讚美祭》",
        "小羊詩歌：《陪我走過春夏秋冬》"
    ],
    ("Ordinary Time", None): [
        "約書亞樂團：《牽手》",
        "讚美之泉：《不動搖的信心》",
        "小羊詩歌：《凡事都有神的美意》"
    ]
}

# === 使用剩餘未使用的歌曲，自動輪替補齊常年期 (Proper) ===
proper_pool_joshua = [
    "全然為你", "與你更靠近", "竭力追求", "用信心宣告", "都指向祢", 
    "我相信", "我獻上我心", "主你永遠與我同在", "直到世界盡頭", "安靜"
]
proper_pool_sop = [
    "深愛耶穌", "謝謝你成為我的家", "我選擇喜樂", "與祢漫步", "那麼深的渴慕", 
    "主啊，我們敬畏祢", "耶和華是應當稱頌的", "只願有耶穌", "好喜歡與你在一起", 
    "不管世界如何看我", "我能給你什麼", "愛祢直到永遠", "數不盡", "我全然獻上", 
    "我心堅定於祢", "深深地敬拜", "盡情地微笑", "頌讚歸於祢", "祢就是唯一", "獻上讚美祭"
]
proper_pool_lamb = [
    "我心堅定於祢", "倚靠祢", "Faith Over Fear", "我知道祢愛我", "最愛的地方", 
    "即或不然", "主的小羊", "祢是我的神", "天父的小花", "阿們", "真理的話語", 
    "祢的居所何等可愛", "一路靠著祂", "祢歡喜的祭(台)", "詩篇二十三篇(台)", 
    "我的最愛", "可喜悅的祭", "序曲(詩篇90篇1-2)", "主耶和華是我的幫助", "詩篇二十三篇"
]

for i in range(1, 33):
    hymn_map[(f"Ordinary Time", f"Proper {i}")] = [
        f"約書亞樂團：《{proper_pool_joshua[i % len(proper_pool_joshua)]}》",
        f"讚美之泉：《{proper_pool_sop[i % len(proper_pool_sop)]}》",
        f"小羊詩歌：《{proper_pool_lamb[i % len(proper_pool_lamb)]}》"
    ]

# === 使用剩餘未使用的歌曲，自動輪替補齊五旬節 (Pentecost) ===
pentecost_pool_joshua = [
    "親愛聖靈", "求充滿這地", "聖靈請你來充滿我心", "溫柔聖靈", "點燃", "觸摸天堂"
]
pentecost_pool_sop = [
    "不要忘記", "Stay [停留]", "披上讚美衣", "我揚聲敬拜", "曠野中唯一的力量", 
    "當祢走進我們當中", "我在這裡", "愛祢，是我一生的呼召", "蒙恩", "讓我尋見祢", "和散那"
]
pentecost_pool_lamb = [
    "看哪,田裡莊稼成熟了", "與我同往", "祢是我的平安", "祢是我的平安 Live", 
    "因我所遭遇的是出於祢", "祢的恩典夠我用", "父啊,我向祢呼求", "我欲等候耶和華(台)"
]

num_to_word_map = {
    1: "First", 2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth",
    6: "Sixth", 7: "Seventh", 8: "Eighth", 9: "Ninth", 10: "Tenth",
    11: "Eleventh", 12: "Twelfth", 13: "Thirteenth", 14: "Fourteenth",
    15: "Fifteenth", 16: "Sixteenth", 17: "Seventeenth", 18: "Eighteenth",
    19: "Nineteenth", 20: "Twentieth", 21: "Twenty-first", 22: "Twenty-second",
    23: "Twenty-third", 24: "Twenty-fourth", 25: "Twenty-fifth",
    26: "Twenty-sixth", 27: "Twenty-seventh", 28: "Twenty-eighth",
    29: "Twenty-ninth", 30: "Thirtieth"
}

for i in range(1, 31):
    word_key = f"{num_to_word_map[i]} Sunday"
    hymns = [
        f"約書亞樂團：《{pentecost_pool_joshua[i % len(pentecost_pool_joshua)]}》",
        f"讚美之泉：《{pentecost_pool_sop[i % len(pentecost_pool_sop)]}》",
        f"小羊詩歌：《{pentecost_pool_lamb[i % len(pentecost_pool_lamb)]}》"
    ]
    
    # 同時註冊兩種常見寫法，確保滴水不漏
    hymn_map[("Pentecost", word_key)] = hymns
    hymn_map[("Pentecost", f"Pentecost {i}")] = hymns
    
# 新增：主顯節延長週數的詩歌捷徑
hymn_map[("Epiphany", "Sixth Sunday after Epiphany")] = hymn_map.get(("Epiphany", "Sixth Sunday"), [])
hymn_map[("Epiphany", "Seventh Sunday after Epiphany")] = hymn_map.get(("Epiphany", "Seventh Sunday"), [])
hymn_map[("Epiphany", "Eighth Sunday after Epiphany")] = hymn_map.get(("Epiphany", "Eighth Sunday"), [])
hymn_map[("Epiphany", "Ninth Sunday after Epiphany")] = hymn_map.get(("Epiphany", "Ninth Sunday"), [])

fallback_tracker = []

stats = {
    "yearly_count": defaultdict(int),
    "untranslated": [],     # 標題仍含英文
    "untranslated_desc": [],  # ★ 新增：用來記錄 Description 裡殘留的英文
    "no_scripture": [],     # 找不到對應經文
    "no_hymn": []           # 找不到對應詩歌
}

all_final_events = [] # 用來存儲所有產出的事件，最後交給報告區塊分析

# === 補充罕見主日的經文 (區分甲乙丙年，已填寫完整 RCL 三代經課) ===
scripture_patch = {
    "A": {
        ("Advent", "First Sunday in Advent"): ["以賽亞書 2:1-5", "詩篇 122", "羅馬書 13:11-14", "馬太福音 24:36-44"],
        # 主顯節後延長
        ("Epiphany", "Sixth Sunday after Epiphany"): ["申命記 30:15-20", "詩篇 119:1-8", "哥林多前書 3:1-9", "馬太福音 5:21-37"],
        ("Epiphany", "Seventh Sunday after Epiphany"): ["利未記 19:1-2, 9-18", "詩篇 119:33-40", "哥林多前書 3:10-11, 16-23", "馬太福音 5:38-48"],
        ("Epiphany", "Eighth Sunday after Epiphany"): ["以賽亞書 49:8-16a", "詩篇 131", "哥林多前書 4:1-5", "馬太福音 6:24-34"],
        ("Epiphany", "Ninth Sunday after Epiphany"): ["創世記 6:9-22; 8:14-19", "詩篇 46", "羅馬書 1:16-17; 3:22b-28", "馬太福音 7:21-29"],
        
        # 甲年常年期缺漏 (Proper 1 與 Epiphany 6 相同)
        ("Ordinary Time", "Proper 1"): ["申命記 30:15-20", "詩篇 119:1-8", "哥林多前書 3:1-9", "馬太福音 5:21-37"],
        ("Ordinary Time", "Proper 5"): ["創世記 12:1-9", "詩篇 33:1-12", "羅馬書 4:13-25", "馬太福音 9:9-13, 18-26"],
        ("Ordinary Time", "Proper 25"): ["申命記 34:1-12", "詩篇 90:1-6, 13-17", "帖撒羅尼迦前書 2:1-8", "馬太福音 22:34-46"],
        ("Ordinary Time", "Proper 28"): ["西番雅書 1:7, 12-18", "詩篇 90:1-8, 12", "帖撒羅尼迦前書 5:1-11", "馬太福音 25:14-30"],
        
        # 基督君王主日 (Proper 29, 30, 31 統一對齊)
        ("Ordinary Time", "Proper 29"): ["以西結書 34:11-16, 20-24", "詩篇 100", "以弗所書 1:15-23", "馬太福音 25:31-46"],
        ("Ordinary Time", "Proper 30"): ["以西結書 34:11-16, 20-24", "詩篇 100", "以弗所書 1:15-23", "馬太福音 25:31-46"],
        ("Ordinary Time", "Proper 31"): ["以西結書 34:11-16, 20-24", "詩篇 100", "以弗所書 1:15-23", "馬太福音 25:31-46"]
    },
    "B": {
        # 主顯節後延長
        ("Epiphany", "Fifth Sunday after Epiphany"): ["以賽亞書 40:21-31", "詩篇 147:1-11, 20c", "哥林多前書 9:16-23", "馬可福音 1:29-39"],
        ("Epiphany", "Sixth Sunday after Epiphany"): ["列王紀下 5:1-14", "詩篇 30", "哥林多前書 9:24-27", "馬可福音 1:40-45"],
        ("Epiphany", "Seventh Sunday after Epiphany"): ["以賽亞書 43:18-25", "詩篇 41", "哥林多後書 1:18-22", "馬可福音 2:1-12"],
        ("Epiphany", "Eighth Sunday after Epiphany"): ["何西阿書 2:14-20", "詩篇 103:1-13, 22", "哥林多後書 3:1-6", "馬可福音 2:13-22"],
        ("Epiphany", "Ninth Sunday after Epiphany"): ["申命記 5:12-15", "詩篇 81:1-10", "哥林多後書 4:5-12", "馬可福音 2:23-3:6"],
        
        # 乙年常年期缺漏 (Proper 1 與 Epiphany 6 相同)
        ("Ordinary Time", "Proper 1"): ["列王紀下 5:1-14", "詩篇 30", "哥林多前書 9:24-27", "馬可福音 1:40-45"],
        ("Ordinary Time", "Proper 5"): ["撒母耳記上 8:4-11, 16-20", "詩篇 138", "哥林多後書 4:13-5:1", "馬可福音 3:20-35"],
        ("Ordinary Time", "Proper 25"): ["約伯記 42:1-6, 10-17", "詩篇 34:1-8, 19-22", "希伯來書 7:23-28", "馬可福音 10:46-52"],
        ("Ordinary Time", "Proper 28"): ["但以理書 12:1-3", "詩篇 16", "希伯來書 10:11-14, 19-25", "馬可福音 13:1-8"],
        
        # 基督君王主日 (Proper 29, 30, 31 統一對齊)
        ("Ordinary Time", "Proper 29"): ["撒母耳記下 23:1-7", "詩篇 132:1-12", "啟示錄 1:4b-8", "約翰福音 18:33-37"],
        ("Ordinary Time", "Proper 30"): ["撒母耳記下 23:1-7", "詩篇 132:1-12", "啟示錄 1:4b-8", "約翰福音 18:33-37"],
        ("Ordinary Time", "Proper 31"): ["撒母耳記下 23:1-7", "詩篇 132:1-12", "啟示錄 1:4b-8", "約翰福音 18:33-37"]
    },
    "C": {
        # 主顯節後延長
        ("Epiphany", "Sixth Sunday after Epiphany"): ["耶利米書 17:5-10", "詩篇 1", "哥林多前書 15:12-20", "路加福音 6:17-26"],
        ("Epiphany", "Seventh Sunday after Epiphany"): ["創世記 45:3-11, 15", "詩篇 37:1-11, 39-40", "哥林多前書 15:35-38, 42-50", "路加福音 6:27-38"],
        ("Epiphany", "Eighth Sunday after Epiphany"): ["以賽亞書 55:10-13", "詩篇 92:1-4, 12-15", "哥林多前書 15:51-58", "路加福音 6:39-49"],
        ("Epiphany", "Ninth Sunday after Epiphany"): ["列王紀上 8:22-23, 41-43", "詩篇 96:1-9", "加拉太書 1:1-12", "路加福音 7:1-10"],
        
        # 丙年常年期缺漏 (Proper 1 與 Epiphany 6 相同)
        ("Ordinary Time", "Proper 1"): ["耶利米書 17:5-10", "詩篇 1", "哥林多前書 15:12-20", "路加福音 6:17-26"],
        ("Ordinary Time", "Proper 5"): ["列王紀上 17:8-16", "詩篇 146", "加拉太書 1:11-24", "路加福音 7:11-17"],
        ("Ordinary Time", "Proper 25"): ["約珥書 2:23-32", "詩篇 65", "提摩太後書 4:6-8, 16-18", "路加福音 18:9-14"],
        ("Ordinary Time", "Proper 28"): ["瑪拉基書 4:1-2a", "詩篇 98", "帖撒羅尼迦後書 3:6-13", "路加福音 21:5-19"],
        
        # 基督君王主日 (Proper 29, 30, 31 統一對齊)
        ("Ordinary Time", "Proper 29"): ["耶利米書 23:1-6", "詩篇 46", "歌羅西書 1:11-20", "路加福音 23:33-43"],
        ("Ordinary Time", "Proper 30"): ["耶利米書 23:1-6", "詩篇 46", "歌羅西書 1:11-20", "路加福音 23:33-43"],
        ("Ordinary Time", "Proper 31"): ["耶利米書 23:1-6", "詩篇 46", "歌羅西書 1:11-20", "路加福音 23:33-43"]
    }
}

def replace_with_map(text: str, mapping: dict) -> str:
    """
    使用 mapping 做字串替換：
    - 長字串優先（避免 'Easter' 先替換掉 'Easter Dawn'）
    - 忽略大小寫
    """
    text = text.strip() # 先清理空格
    for eng, zh in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
        text = re.sub(re.escape(eng), zh, text, flags=re.IGNORECASE)
    return text
    
def replace_season_num(m):
    season_name = m.group(1)
    num_str = m.group(2)
    zh_num = arabic_to_zh.get(num_str, num_str)
    return f"{season_name}第{zh_num}主日"

# 3. 翻譯函式
def translate_summary(summary: str) -> str:
    # 常見拼字錯誤修正
    corrections = {
        r"\bTwelth\b": "Twelfth",
        r"\bFourtheenth\b": "Fourteenth",
        r"\bTwent[- ]?first\b": "Twenty-first", # 這裡會順便把錯字的破折號修好
        r"Easter Sunday\s*[-－–—]\s*Dawn": "Easter Dawn",
        r"\bProepr\b": "Proper"
    }
    for wrong, right in corrections.items():
        summary = re.sub(wrong, right, summary, flags=re.IGNORECASE)

    # =====================================================================
    # ★ 按照您的要求：保護「英文數字帶破折號」不被切開
    # 將 Twenty-first, Twenty-fourth 等數字裡的破折號暫時替換為特殊標記
    # =====================================================================
    summary = re.sub(
        r"\b(Twenty|Thirty)[-－–—](first|second|third|fourth|fifth|sixth|seventh|eighth|ninth)\b", 
        r"\1_NUM_HYPHEN_\2", 
        summary, 
        flags=re.IGNORECASE
    )

    # 1. 遇到破折號切開分別翻譯 (這時 Twenty-first 已經被保護，不會被切)
    parts = re.split(r"\s*[－–—-]\s*", summary)
    if len(parts) > 1:
        # 切開後，若裡面有剛才保護的數字，把它還原回標準的 "-" 再去遞迴翻譯
        translated_parts = [translate_summary(p.strip().replace("_NUM_HYPHEN_", "-")) for p in parts]
        return "－".join(translated_parts)

    # 2. 若沒有被切開，也要記得把保護的標記還原成標準的 "-"
    summary = summary.replace("_NUM_HYPHEN_", "-")

    # 3. 先替換季節/節日（大小寫不敏感，長字串優先） 
    summary = replace_with_map(summary, season_map)    

    # 4. 處理 (Proper X) 
    match = re.search(r"\(Proper\s+(\d+)\)", summary, flags=re.IGNORECASE) 
    if match: 
        proper_num = match.group(1) 
        zh_num = arabic_to_zh.get(proper_num, proper_num)
        summary = summary.replace(match.group(0), f"(常年期第{zh_num}組經課)")    
        
    match_plain = re.search(r"Proper\s+(\d+)", summary, flags=re.IGNORECASE)
    if match_plain:
        proper_num = match_plain.group(1)
        zh_num = arabic_to_zh.get(proper_num, proper_num)
        return f"常年期第{zh_num}組經課"

    # 5. 套用 Nth Sunday 句型 (全部加上 flags=re.IGNORECASE)
    match = re.match(
        r"(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth|Thirteenth|Fourteenth|Fifteenth|Sixteenth|Seventeenth|Eighteenth|Nineteenth|Twentieth|Twenty-first|Twenty-second|Twenty-third|Twenty-fourth|Twenty-fifth|Twenty-sixth|Twenty-seventh|Twenty-eighth|Twenty-ninth|Thirtieth)\s+Sunday\s+in\s+(.+)",
        summary,
        flags=re.IGNORECASE
    )
    if match:
        ordinal, season = match.groups()
        zh_ordinal = ordinal_map.get(ordinal.capitalize(), ordinal)
        season_zh = season_map.get(season.strip(), season.strip())
        return f"{season_zh}{zh_ordinal}主日"

    match = re.match(
        r"(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth|Thirteenth|Fourteenth|Fifteenth|Sixteenth|Seventeenth|Eighteenth|Nineteenth|Twentieth|Twenty-first|Twenty-second|Twenty-third|Twenty-fourth|Twenty-fifth|Twenty-sixth|Twenty-seventh|Twenty-eighth|Twenty-ninth|Thirtieth)\s+Sunday\s+after\s+(.+)",
        summary,
        flags=re.IGNORECASE
    )
    if match:
        ordinal, season = match.groups()
        zh_ordinal = ordinal_map.get(ordinal.capitalize(), ordinal)
        season_zh = season_map.get(season.strip(), season.strip())
        return f"{season_zh}後{zh_ordinal}主日"

    match = re.match(
        r"(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth|Thirteenth|Fourteenth|Fifteenth|Sixteenth|Seventeenth|Eighteenth|Nineteenth|Twentieth|Twenty-first|Twenty-second|Twenty-third|Twenty-fourth|Twenty-fifth|Twenty-sixth|Twenty-seventh|Twenty-eighth|Twenty-ninth|Thirtieth)\s+Sunday\s+of\s+(.+)",
        summary,
        flags=re.IGNORECASE
    )
    if match:
        ordinal, season = match.groups()
        zh_ordinal = ordinal_map.get(ordinal.capitalize(), ordinal)
        season_zh = season_map.get(season.strip(), season.strip())
        return f"{season_zh}{zh_ordinal}主日"

    match = re.match(r"Last Sunday after (.+)", summary, flags=re.IGNORECASE)
    if match:
        season = match.group(1).strip()
        season_zh = season_map.get(season, season)
        return f"{season_zh}後最後一主日"

    match = re.match(r"(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth|Thirteenth|Fourteenth|Fifteenth|Sixteenth|Seventeenth|Eighteenth|Nineteenth|Twentieth|Twenty-first|Twenty-second|Twenty-third|Twenty-fourth|Twenty-fifth|Twenty-sixth|Twenty-seventh|Twenty-eighth|Twenty-ninth|Thirtieth)\s+Sunday$", summary, flags=re.IGNORECASE)
    if match:
        ordinal = match.group(1)
        zh_ordinal = ordinal_map.get(ordinal.capitalize(), ordinal)
        return f"{zh_ordinal}主日"

    summary = re.sub(r"(聖靈降臨期|將臨期|聖誕期|顯現期|預苦期|復活期|常年期)\s+(\d+)", replace_season_num, summary)
    return summary

# 翻譯片語與書卷名稱 + 特殊規則
def translate_text(text, cycle_label=None, season=None, sunday=None):
    if not text:
        return ""

    text = text.strip().lstrip("\ufeff")
    text = re.sub(r"1\s*Corthnians", "1 Corinthians", text, flags=re.IGNORECASE)
    text = re.sub(r"\bthe\b", "", text, flags=re.IGNORECASE)

    # 專門處理 Supplemental Lectionary 段落：逐行翻譯並保留
    def fix_supplemental(match):
        block = match.group(0)
        lines = block.splitlines()
        new_lines = []
        for line in lines:
            if "Supplemental Lectionary" in line:
                new_lines.append("補充經課:")
            elif line.strip():  # 保留非空行，避免縮排或空格造成漏掉
                new_lines.append(replace_with_map(line.strip(), book_map))
        return "\n".join(new_lines)

    # 捕捉 "Supplemental Lectionary:" 到下一個段落標題 (以冒號結尾) 或檔案結尾
    text = re.sub(
        r"Supplemental Lectionary:[\s\S]*?(?=\n[A-Za-z ]+:|\nPrayer|\nColor:|\Z)",
        fix_supplemental,
        text,
        flags=re.IGNORECASE
    )

    # 移除 Prayer 段落直到 Color
    text = re.sub(r"Prayer of the Day:[\s\S]*?(?=Color:)", "Color:", text, flags=re.IGNORECASE)

    # === 處理 "X Sunday after Y" 結構 ===
    sunday_map = {
        "First": "第一",
        "Second": "第二",
        "Third": "第三",
        "Fourth": "第四",
        "Fifth": "第五",
        "Sixth": "第六",
        "Seventh": "第七",
        "Last": "最後一"
    }
    for eng_num, zh_num in sunday_map.items():
        text = re.sub(
            rf"{eng_num}\s+Sunday\s+after\s+(\w+)",
            rf"\1後{zh_num}主日",
            text,
            flags=re.IGNORECASE
        )

    # 經文範圍正規化
    text = re.sub(r"(\d+:\d+)\s*[-－–—]\s*(\d+(:\d+)?[a-z]?)", r"\1-\2", text)
    text = re.sub(r"[－–—]", "-", text)

    # 特殊標題翻譯
    special_titles = {
        "Transfiguration of Our Lord": "登山變像日",
        "The Baptism of Our Lord": "主受洗日",
        "Baptism of Our Lord": "主受洗日",
        "Epiphany of Our Lord": "主顯節",
        "Holy Trinity": "三一主日",
        "Resurrection of our Lord": "耶穌基督復活了！"
    }
    text = replace_with_map(text, special_titles)

    # 顏色翻譯
    match = re.search(r"Color:\s*(\w+)", text)
    if match:
        eng_color = match.group(1)
        zh_color = color_map.get(eng_color, eng_color)
        text = re.sub(r"Color:\s*\w+", f"代表顏色: {zh_color}", text)

    # 固定片語翻譯
    text = replace_with_map(text, phrase_map)
    text = replace_with_map(text, {**season_map, **book_map, **ordinal_map})

    return text
   
def parse_summary(summary_text):
    """
    將 ICS SUMMARY 轉換成 (season, sunday_name, display_summary)
    與簡化版 hymn_map 對齊
    """
    summary_text = summary_text.strip()
    # === 強制修正原始資料的拼字錯誤 ===
    summary_text = summary_text.replace("Proepr", "Proper").replace("Ephphany", "Epiphany")
    # 去掉最後的年字母 (A/B/C)
    parts = summary_text.split()
    if parts and parts[-1] in ("A", "B", "C"):
        raw_summary = " ".join(parts[:-1])
    else:
        raw_summary = summary_text

    # 1. 強制統一特殊節日名稱 (解決 Ascension, Reformation, Palm Sunday 找不到的問題)
    if "Ascension" in raw_summary:
        return "Easter", "Ascension", "基督升天日" 
    if "Reformation" in raw_summary:
        return "Ordinary Time", "Reformation", "宗教改革日"
    if "Palm Sunday" in raw_summary or "Passion" in raw_summary:
        return "Holy Week", "Palm Sunday", "棕枝主日"
    if "Transfiguration" in raw_summary:
        return "Epiphany", "Transfiguration", "登山變像主日" 
    if "Trinity" in raw_summary:
        return "Ordinary Time", "Trinity Sunday", "三一主日"
    if "All Saints" in raw_summary:
        return "Ordinary Time", "All Saints", "古聖紀念日" 
    # 處理 "Last Sunday of the Church Year" 與 "Christ the King"
    if "Christ the King" in raw_summary or ("Last Sunday" in raw_summary and "Church Year" in raw_summary):
        return "Ordinary Time", "Christ the King", "基督君王主日"
    if "Ash Wednesday" in raw_summary:
        return "Lent", "Ash Wednesday", "聖灰日"
    if "Maundy" in raw_summary or "Holy Thursday" in raw_summary:
        return "Holy Week", "Maundy Thursday", "主立聖餐日" 
    if "Good Friday" in raw_summary:
        return "Holy Week", "Good Friday", "受難日"
    if "Easter Vigil" in raw_summary:
        return "Easter", "Easter Vigil", "復活前夕守夜"
    if "Baptism" in raw_summary:
        return "Epiphany", "First Sunday", "耶穌受洗主日" 

    # 正規化名稱
    match_proper = re.search(r"Proper\s+(\d+)", raw_summary, flags=re.IGNORECASE)
    if match_proper:
        normalized = f"Proper {match_proper.group(1)}"
    else:
        # 如果不是 Proper，才去查那張大表
        normalized = summary_map.get(raw_summary, raw_summary)

    # 判斷 season
    if "Advent" in raw_summary:
        season = "Advent"
    elif "Christmas" in raw_summary:
        season = "Christmas"
    elif "Epiphany" in raw_summary or "Baptism" in raw_summary or "Transfiguration" in raw_summary:
        season = "Epiphany"
    elif "Lent" in raw_summary or raw_summary in ("Ash Wednesday", "Palm Sunday", "Good Friday", "Maundy Thursday", "Holy Saturday"):
        season = "Lent" if "Lent" in raw_summary else "Holy Week"
    elif "Easter" in raw_summary or raw_summary == "Ascension":
        season = "Easter"
    elif "Pentecost" in raw_summary:
        season = "Pentecost"
    elif "Ordinary" in raw_summary or "Proper" in raw_summary or "Trinity" in raw_summary or raw_summary == "Christ the King":
        season = "Ordinary Time"
    elif raw_summary == "Last Sunday in the Church Year":
        season = "Ordinary Time"
        normalized = "Christ the King"
    elif raw_summary == "Thanksgiving":
        season = "Ordinary Time"
        normalized = "Thanksgiving"
    else:
        season = None

    # 顯示用中文翻譯
    display_summary = translate_summary(normalized)

    # 回傳三元組
    return season, normalized, display_summary

# === 工具函式 ===
def get_advent_start(year):
    """
    計算某年的將臨期第一主日（Advent 1）。
    規則：11 月 27 日到 12 月 3 日之間的星期日。
    """
    date = datetime.date(year, 11, 27)
    while date.weekday() != 6:  # 6 = Sunday
        date += datetime.timedelta(days=1)
    return date

def get_cycle_label(date):
    """改良版：避免跨年錯誤"""
    base_year = 2025
    if isinstance(date, datetime.datetime):
        date = date.date()
    advent_start = get_advent_start(date.year)
    liturgical_year = date.year - 1 if date < advent_start else date.year
    cycle_index = (liturgical_year - base_year) % 3
    return ["A", "B", "C"][cycle_index]
    
def get_hymn_text(summary: str, date: datetime.date = None) -> str:
    season, sunday, _ = parse_summary(summary)

    # === 1. 智慧路由與別名轉換 ===
    # 修正：將 Proper X 強制導向 Ordinary Time (因為字典裡 Proper 建在常年期)
    if "Proper" in sunday:
        season = "Ordinary Time"
        
    # 修正：各種特殊節日名稱的別名對應
    if season == "Easter" and ("Resurrection" in summary or "Easter Day" in summary or "Easter Dawn" in summary):
        sunday = "Easter Sunday"
    if season == "Christmas" and "Nativity" in summary:
        sunday = "Christmas Eve" if "Eve" in summary else "Christmas Day"
    if season == "Epiphany" and "Epiphany of" in summary:
        sunday = "Epiphany"
    if season == "Pentecost" and "Day of Pentecost" in summary:
        sunday = "Pentecost Sunday"

    # === 2. 先嘗試精確比對 ===
    hymns = hymn_map.get((season, sunday))

    # === 3. 啟動模糊比對 (Fuzzy Match) ===
    if not hymns:
        # 修正：將字典的項目依據 map_sunday 的「字串長度」由長到短排序
        # 確保 "Second Sunday" 會比 "Epiphany" 更早被比對到，避免短字串誤攔截！
        sorted_items = sorted(hymn_map.items(), key=lambda x: len(x[0][1] or ""), reverse=True)
        
        for (map_season, map_sunday), map_hymns in sorted_items:
            if map_season == season and map_sunday:
                
                # 【關鍵防呆】：如果 map_sunday 剛好等於節期名稱 (例如 "Epiphany")
                # 請直接跳過！否則它會攔截所有包含 "after Epiphany" 的週數
                if map_sunday.lower() == season.lower():
                    continue
                
                if map_sunday.lower() in sunday.lower() or map_sunday.lower() in summary.lower():
                    hymns = map_hymns
                    break

    # === 4. 如果還是找不到，啟用 Fallback 備案並追蹤 ===
    if not hymns:
        hymns = hymn_map.get((season, None))
        if hymns and date:
            date_str = date.strftime("%Y%m%d")
            fallback_tracker.append(f"- {date_str} | 節期: {season} | 字典缺漏名稱: '{sunday}' (原始: {summary})")

    if not hymns:
        return ""

    return "\n".join(hymns)
    
def calculate_advent1(year: int) -> date:
    """計算某年 Advent 1：11/27–12/3 之間的第一個主日"""
    for day in range(27, 34):
        d = date(year, 11 if day <= 30 else 12, day if day <= 30 else day - 30)
        if d.weekday() == 6:  # 星期日
            return d
    raise ValueError("Advent 1 not found")

def determine_cycle(dt) -> str:
    """根據日期判斷屬於哪個 cycle (A/B/C)，以 Advent 起算"""
    if hasattr(dt, "date"):
        dt = dt.date()
    advent1 = calculate_advent1(dt.year)
    if dt < advent1:
        year = dt.year - 1
    else:
        year = dt.year
    base_year = 2025
    offset = (year - base_year) % 3
    return ["A", "B", "C"][offset]

def determine_formula(summary: str, dt: date = None) -> str:
    s = summary.lower()
    if dt and dt.weekday() == 6: # 只有當天是週日才做檢查
        # 針對 C 年被吃掉的那兩個主日
        if "reformation" in s or "all saints" in s:
             # 假設 calculate_easter 可以在此處被呼叫 (或從外部傳入年份)
             # 這裡我們現場算一次當年的復活節，用來推算是第幾週
             easter = calculate_easter(dt.year)
             pentecost = easter + timedelta(days=49)
             
             # 如果這一天在五旬節之後
             if dt > pentecost:
                 weeks = (dt - pentecost).days // 7
                 # 回傳「五旬節公式」取代原本的「固定日期公式」
                 # 這樣程式就學會了：這個事件其實是 Pentecost X
                 return f"(calculate_easter(year+1) + timedelta(days=49)) + timedelta(weeks={weeks})"
    # === 在判斷公式前，先強制修正錯字 ===
    if "ephphany" in s:
        s = s.replace("ephphany", "epiphany")

    # --- Christmas ---
    if "christmas eve" in s: return "date(year, 12, 24)"
    if "christmas day" in s: return "date(year, 12, 25)"
    
    # 聖誕後主日 (Christmas 1, 2...)
    # 邏輯：從 12月26日 開始往後找第一個星期日，然後加上 (N-1) 週
    
    # 1. 先嘗試抓數字 (例如 Christmas 1)
    match_num = re.search(r"christmas\s+(\d+)", s)
    if match_num:
        num = int(match_num.group(1))
        return f"date(year, 12, 26) + timedelta(days=(6 - date(year, 12, 26).weekday() + 7) % 7) + timedelta(weeks={num-1})"
    
    # 2. 再嘗試抓序數單字 (例如 First Sunday after Christmas)
    if "christmas" in s:
        for word, num in ordinal_map_2.items():
            # 只要包含 christmas 且包含序數詞 (first, second...)
            if word in s or str(num) in s:
                 return f"date(year, 12, 26) + timedelta(days=(6 - date(year, 12, 26).weekday() + 7) % 7) + timedelta(weeks={num-1})"
    # --- Epiphany ---
    # 1. 處理主受洗日 (Baptism) 或 顯現後第一主日
    if "baptism" in s or ("epiphany" in s and (" 1" in s or "first" in s)):
        # 邏輯：1月7日之後的第一個主日
        return "date(year+1, 1, 7) + timedelta(days=(6 - date(year+1, 1, 7).weekday() + 7) % 7)"

    # 2. 處理顯現後其他主日 (Epiphany 2, 3... 或 Fifth Sunday...)
    # 先嘗試抓數字 (如 Epiphany 2)
    match_num = re.search(r"epiphany\s+(\d+)", s)
    if match_num:
        num = int(match_num.group(1))
        return f"date(year+1, 1, 7) + timedelta(days=(6 - date(year+1, 1, 7).weekday() + 7) % 7) + timedelta(weeks={num-1})"

    # 再嘗試抓序數單字 (如 Fifth Sunday after Ephphany)
    for word, num in ordinal_map_2.items():
        # 這裡放寬條件：只要有 epiphany (或錯字 ephphany) 且有序數詞
        if ("epiphany" in s or "ephphany" in s) and (word in s or str(num) in s):
             # 回傳簡單公式：基準日 + (N-1) 週
             return f"date(year+1, 1, 7) + timedelta(days=(6 - date(year+1, 1, 7).weekday() + 7) % 7) + timedelta(weeks={num-1})"
    # 登山變像日 (最後主日)
    if "transfiguration" in s or "last sunday after epiphany" in s:
        return "calculate_easter(year+1) - timedelta(days=49)"

    # 純主顯節 (1/6 固定) - 必須放在上面含有數字的判斷之後
    if "epiphany" in s: return "date(year+1, 1, 6)"

    # --- Lent ---
    if "ash wednesday" in s: return "calculate_easter(year+1) - timedelta(days=46)"
    
    # 預苦期主日基準應為 Easter - 42天 (Lent 1 主日)，而非聖灰日
    for word, num in ordinal_map_2.items():
        if "lent" in s and (word in s or str(num) in s):
             return f"calculate_easter(year+1) - timedelta(days={42 - (num-1)*7})"

    # --- Holy Week / Easter ---
    if "palm" in s or "passion" in s: 
        return "calculate_easter(year+1) - timedelta(days=7)"
    if "maundy" in s or "holy thursday" in s: 
        return "calculate_easter(year+1) - timedelta(days=3)"
    if "good friday" in s: return "calculate_easter(year+1) - timedelta(days=2)"
    # 復活期其他主日
    for word, num in ordinal_map_2.items():
        if "easter" in s and (word in s or str(num) in s):
            return f"calculate_easter(year+1) + timedelta(weeks={num-1})"

    # 包含 Dawn 和 Day
    if "easter" in s and ("day" in s or "sunday" in s or "dawn" in s or "resurrection" in s) and "2" not in s and "3" not in s: 
        return "calculate_easter(year+1)"

    # --- Pentecost ---
    if "ascension" in s: return "calculate_easter(year+1) + timedelta(days=39)"
    if "day of pentecost" in s or s.strip() == "pentecost": 
        return "calculate_easter(year+1) + timedelta(days=49)"
    if "trinity" in s: return "calculate_easter(year+1) + timedelta(days=56)"
    # 針對 Proper 的處理
    match_proper = re.search(r"proper\s+(\d+)", s)
    if match_proper:
        proper_num = int(match_proper.group(1))
        # Proper 6 約等於 Pentecost 3 (Proper N - 3 = Pentecost N)
        # 公式：五旬節(49天) + (Proper數 - 3) 週
        offset_weeks = proper_num - 3
        if offset_weeks < 1: offset_weeks = 1
        return f"(calculate_easter(year+1) + timedelta(days=49)) + timedelta(weeks={offset_weeks})"
    
    # 聖靈降臨後主日 (Pentecost N)
    # 1. 優先找「獨立數字」 (\b 代表單字邊界，確保 10 不會被當成 1)
    match_num = re.search(r"\b(\d+)\b", s)
    if "pentecost" in s and match_num:
        num = int(match_num.group(1))
        return f"(calculate_easter(year+1) + timedelta(days=49)) + timedelta(weeks={num})"

    # 2. 沒數字才找單字 (例如 First, Second)
    for word, num in ordinal_map_2.items():
        if "pentecost" in s and word in s:
             return f"(calculate_easter(year+1) + timedelta(days=49)) + timedelta(weeks={num})"
    # --- Advent / Others ---
    if "reformation" in s: return "date(year+1, 10, 31)"
    if "all saints" in s: return "date(year+1, 11, 1)"
    if "thanksgiving" in s: return "fourth_thursday_of_november(year+1)"
    if "christ the king" in s or "last sunday" in s: 
        return "calculate_advent1(year+1) - timedelta(days=7)"
    # Last Judgment (末日審判主日) = 倒數第二主日 = 下一個 Advent 往前推 2 週
    if "last judgment" in s:
        return "calculate_advent1(year+1) - timedelta(days=14)"
    # Saints Triumphant (聖徒得勝日) = 倒數第三主日 = 下一個 Advent 往前推 3 週
    if "saints triumphant" in s:
        return "calculate_advent1(year+1) - timedelta(days=21)"

    for word, num in ordinal_map_2.items():
        if "advent" in s and (word in s or str(num) in s):
            return f"calculate_advent1(year) + timedelta(weeks={num-1})"
    
    return ""

def fourth_thursday_of_november(year: int) -> date:
    """計算某年 11 月的第四個星期四 (美國感恩節)"""
    d = date(year, 11, 1)
    # 找到第一個星期四 (weekday() == 3)
    while d.weekday() != 3:
        d += timedelta(days=1)
    # 再加上三週就是第四個星期四
    return d + timedelta(weeks=3)

def calculate_easter(year: int) -> date:
    """計算某年西方教會的復活節日期 (Gregorian calendar)"""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)

def eval_formula(formula: str, year: int) -> date:
    """執行公式字串，回傳實際日期"""
    safe_env = {
        "date": date,
        "timedelta": timedelta,
        "calculate_easter": calculate_easter,
        "calculate_advent1": calculate_advent1,
        "fourth_thursday_of_november": fourth_thursday_of_november,
        "year": year,
    }
    try:
        return eval(formula, {"__builtins__": {}}, safe_env)
    except Exception:
        return None

def build_canonical_set_with_formula(cal):
    """抓 ICS SUMMARY，建立事件清單，精確判定教會年週期"""
    canonical_set = []
    seen_cycle_names = set()
    
    corrections = {
        r"\bTwelth\b": "Twelfth",
        r"\bFourtheenth\b": "Fourteenth",
        r"\bTwent[- ]?first\b": "Twenty-first",
        r"\bProepr\b": "Proper"
    }

    for component in cal.walk("VEVENT"):
        summary_text = str(component.get("summary")).strip()
        dtstart = component.get("dtstart").dt
        if hasattr(dtstart, "date"):
            dtstart = dtstart.date()

        # 抓取範圍：從 2025 Advent 1 到 2028 Advent 1 之前
        # 建議設為 2028-12-02 以確保完整抓完丙年
        if date(2025, 11, 30) <= dtstart <= date(2028, 12, 2):
            
            # --- [核心修正：正確判定 Cycle] ---
            # 計算該日期所在年份的 Advent 1
            adv1_of_year = calculate_advent1(dtstart.year)
            
            # 判斷教會年年份 (Liturgical Year Start Year)
            # 如果日期 >= 今年的 Advent 1，它屬於「今年開始」的教會年
            # 如果日期 < 今年的 Advent 1，它屬於「去年開始」的教會年
            if dtstart >= adv1_of_year:
                lit_start_year = dtstart.year
            else:
                lit_start_year = dtstart.year - 1
            
            # 計算週期：基準是 2025 年 11 月開始為 Cycle A
            # 2025 -> A (0), 2026 -> B (1), 2027 -> C (2)
            cycle_idx = (lit_start_year - 2025) % 3
            cycle = ["A", "B", "C"][cycle_idx]
            # ----------------------------------

            # 拼字修正
            season_keeping_summary = summary_text
            for wrong, right in corrections.items():
                season_keeping_summary = re.sub(wrong, right, season_keeping_summary, flags=re.IGNORECASE)

            if season_keeping_summary.strip() == "Last Sunday in the Church Year":
                season_keeping_summary = "Christ the King"

            # 唯一鍵值去重：避免同一週期有重複名稱，但允許同一天有不同事件
            unique_key = (cycle, season_keeping_summary)
            if unique_key in seen_cycle_names:
                continue
            seen_cycle_names.add(unique_key)

            formula = determine_formula(season_keeping_summary, dtstart)

            canonical_set.append({
                "name": season_keeping_summary,
                "date": dtstart,
                "cycle": cycle, # 這是修正後正確的 Cycle
                "formula": formula
            })
            
    # =========================================================================
    # ★★★ [新增：強制補齊所有缺失的 Proper 與 Epiphany 公式] ★★★
    # 解決範本因年份短或被特殊節期佔據，導致 Proper 及長主顯節漏缺的問題
    # =========================================================================
    existing_propers = {"A": set(), "B": set(), "C": set()}
    existing_epiphanies = {"A": set(), "B": set(), "C": set()}
    num_to_ordinal = {5: "Fifth", 6: "Sixth", 7: "Seventh", 8: "Eighth", 9: "Ninth"}

    for e in canonical_set:
        name_str = e["name"]
        
        # 1. 收集已有的 Proper
        match = re.search(r"Proper\s+(\d+)", name_str, flags=re.IGNORECASE)
        if match:
            existing_propers[e["cycle"]].add(int(match.group(1)))
            
        # 2. 收集已有的 Epiphany (第 5 到 9)
        for num, word in num_to_ordinal.items():
            if f"{word} Sunday after Epiphany".lower() in name_str.lower():
                existing_epiphanies[e["cycle"]].add(num)

    for c in ["A", "B", "C"]:
        # 補齊 Proper 1 到 29
        for p in range(1, 33):  
            if p not in existing_propers[c]:
                offset_weeks = p - 3
                if offset_weeks < 1: offset_weeks = 1
                canonical_set.append({
                    "name": f"Proper {p}",
                    "date": datetime.date(2000, 1, 1), # 給予假日期以防止後續 sort 發生 TypeError
                    "cycle": c,
                    "formula": f"(calculate_easter(year+1) + timedelta(days=49)) + timedelta(weeks={offset_weeks})"
                })
                
        # 補齊 主顯節後第 5 到 9 主日
        for ep_num in range(5, 10):
            if ep_num not in existing_epiphanies[c]:
                ep_word = num_to_ordinal[ep_num]
                canonical_set.append({
                    "name": f"{ep_word} Sunday after Epiphany",
                    "date": datetime.date(2000, 1, 1), # 給予假日期
                    "cycle": c,
                    "formula": f"date(year+1, 1, 7) + timedelta(days=(6 - date(year+1, 1, 7).weekday() + 7) % 7) + timedelta(weeks={ep_num-1})"
                })
    # =========================================================================
              
        # ★ 新增：強制為每一週期補上「基督君王主日」
        # 公式：下一個 Advent 1 往前推 7 天
        canonical_set.append({
            "name": "Christ the King",
            "date": datetime.date(2000, 1, 1), 
            "cycle": c,
            "formula": "calculate_advent1(year+1) - timedelta(days=7)"
        })
    # =========================================================================
    cycle_order = {"A": 0, "B": 1, "C": 2}
    canonical_set.sort(key=lambda e: (cycle_order[e["cycle"]], e["date"]))
    return canonical_set
    
def is_english_title(text):
    """檢查標題是否包含未翻譯的英文字母"""
    # 只移除句尾的 (甲年)、(乙年)、(丙年)，保留中間所有的字
    main_text = re.sub(r"\s*\([甲乙丙]年\)$", "", text).strip()
    
    # 只要字串中含有任何 a-z 或 A-Z 的字母，就回傳 True
    if re.search(r'[A-Za-z]', main_text):
        return True
    return False
    
# 判斷是否為泛用主日 (用於重疊時排序)
def is_generic_sunday(name):
    # 加上 Proper，讓這些補進去的泛用主日遇到宗教改革/諸聖日時能自動退讓
    pattern = r"^(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth|Thirteenth|Fourteenth|Fifteenth|Sixteenth|Seventeenth|Eighteenth|Nineteenth|Twentieth|Twenty-|Last) Sunday|Proper"
    return re.match(pattern, name, flags=re.IGNORECASE) is not None    

def get_english_lines_in_desc(text):
    """抓出 Description 中包含英文的行，排除網址、專有名詞、經文標記與合法詩歌"""
    lines_with_english = []
    for line in text.splitlines():
        # 1. 移除網址
        clean_line = re.sub(r'http[s]?://\S+', '', line)
        
        # 2. 移除 Google Meet 與單獨的 Meet (專有名詞)
        clean_line = re.sub(r'Google Meet|Meet', '', clean_line, flags=re.IGNORECASE)
        
        # 3. 排除經文中的 a, b, c 標記 (例如 5:2-5a, 119b, 7b-10)
        clean_line = re.sub(r'(?<=\d)[abc]', '', clean_line)
        
        # 4. 只要這行包含這些樂團名稱，就不算殘留英文
        if re.search(r'讚美之泉|約書亞樂團|小羊', line):
            continue
            
        # 5. 檢查這行是否還有剩餘的英文字母 A-Za-z
        if re.search(r'[A-Za-z]', clean_line):
            lines_with_english.append(line.strip())
            
    return lines_with_english

# === 代表顏色自動判斷函式 ===
def get_liturgical_color(season, sunday):
    """依據指定的顏色規則，精準判斷代表顏色"""
    # 1. 將臨期：藍色
    if season == "Advent": 
        return "🔵 藍色"
        
    if season == "Christmas": 
        return "⚪ 白色"
        
    if season == "Epiphany":
        # 主顯日、耶穌受洗主日、登山變像主日 為白色
        if sunday in ["Epiphany", "First Sunday", "Transfiguration"]: 
            return "⚪ 白色"
        return "🟢 綠色" 
        
    # 2. 預苦期與聖週
    if season in ["Lent", "Holy Week"]:
        # 棕枝主日、主立聖餐日：紅色
        if sunday in ["Palm Sunday", "Maundy Thursday"]:
            return "🔴 紅色"
        # 受難日、聖週六：黑色
        if sunday in ["Good Friday", "Holy Saturday"]: 
            return "⚫ 黑色"
        # 預苦期其他日子：紫色
        return "🟣 紫色"
        
    if season == "Easter": 
        return "⚪ 白色"
        
    if season in ["Pentecost", "Ordinary Time"]:
        # 聖靈降臨主日：紅色
        if sunday == "Pentecost Sunday": 
            return "🔴 紅色"
        if sunday in ["Trinity Sunday", "Christ the King"]: 
            return "⚪ 白色"
        return "🟢 綠色" 
        
    return ""
    
# === 年度範圍設定 ===
START_YEAR = 2025
YEARS = 101
END_YEAR = START_YEAR + YEARS - 1

with open("lectionary.ics", "rb") as f:
    cal = Calendar.from_ical(f.read())

cn_cal = Calendar()
cn_cal.add('prodid', '-//Chinese Lectionary//mxm.dk//')
cn_cal.add('version', '2.0')

# 用來記錄已經處理過的日期
seen_dates_original = set()

# 👇 新增：完美的模板庫
perfect_templates = {}

# === 事件處理主流程 ===
for component in cal.walk():
    if component.name == "VEVENT":
        start_date = component.get("dtstart").dt
        end_date = component.get("dtend").dt
        # 確保 start_date 是 date 格式
        if hasattr(start_date, "date"):
            check_date = start_date.date()
        else:
            check_date = start_date

        if not (START_YEAR <= start_date.year <= END_YEAR):
            continue
        # 如果這一天已經有事件了，就跳過之後的（例如跳過重複的聖誕夜）
        if check_date in seen_dates_original:
            continue
        seen_dates_original.add(check_date)

        summary_text = str(component.get("summary"))
        cycle_label = get_cycle_label(start_date)
        season, sunday, display_summary = parse_summary(summary_text)
        hymns = hymn_map.get((season, sunday), [])
        subject = translate_text(display_summary, cycle_label, season, sunday)
        # 檢查翻譯
        if is_english_title(subject):
            stats["untranslated"].append(f"{start_date.strftime('%Y%m%d')} | {summary_text} -> {subject}")
        description = str(component.get("description"))
        description = description.replace("–", "-").replace("–", "-").replace("—", "-")
        lines = description.splitlines()
        
        # === 找到第一個 phrase_map 相關的片語位置 ===
        start_index = 0
        found_match = False  
        for i, line in enumerate(lines):
            for phrase in phrase_map.keys():
                if phrase.lower() in line.lower():
                    start_index = i
                    found_match = True  
                    break
            if found_match:  
                break

        # 只保留從第一個片語開始的行
        lines = lines[start_index:]
        merged_lines = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if i + 1 < len(lines) and re.match(r"^\d+$", lines[i+1].strip()):
                merged_lines.append(line + " " + lines[i+1].strip())
                i += 2
            else:
                merged_lines.append(line)
                i += 1
        lines = merged_lines
        
        # =======================================================
        # 🚀 恢復原本最健康、最乾淨的過濾邏輯
        # =======================================================
        new_lines = []
        skip_mode = False

        for line in lines:
            # 0.1 暴力清洗亂碼！
            line = re.sub(r'[–—−\x96\x97\u2013\u2014]', '-', line)

            # 1. 碰到祈禱文，開啟跳過模式
            if "Prayer of the Day" in line:
                skip_mode = True
                continue
            if skip_mode:
                continue
            
            # 2. 略過 Alleluia 等冗長英文金句歡呼
            if "Alleluia" in line or "alleluia" in line.lower():
                continue
            
            # 3. 略過舊版的標題雜訊規則 (保留你原本的邏輯)
            if re.match(r"^\s*\d+\s+[A-Za-z]", line) and ":" not in line:
                continue
                
            # 4. 【黑名單】如果這行有括號 (代表是替代經文或註解)，直接踢掉！
            if "(" in line and ")" in line:
                continue
                
            # 5. 【白名單】判斷這行是否包含「英文字母 + 數字」(代表書卷加章節)
            # 因為空白行已經在第 0 步安全過關了，所以這裡只會殺掉「沒有數字的純文字標題」！
            if not re.search(r'[A-Za-z]+\s+\d+', line):
                continue
                
            # 6. 如果有標題包含在內，進行翻譯
            if re.search(r"(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth|Thirteenth|Fourteenth|Fifteenth|Sixteenth|Seventeenth|Eighteenth|Nineteenth|Twentieth|Twenty-first|Twenty-second|Twenty-third|Twenty-fourth|Twenty-fifth|Twenty-sixth|Twenty-seventh|Twenty-eighth|Twenty-ninth|Thirtieth) Sunday (after|of|in)", line, flags=re.IGNORECASE):
                line = translate_summary(line)
            
            # 7. 翻譯並清理行首標籤
            clean_trans = translate_text(line, cycle_label, season, sunday)
            clean_trans = re.sub(r"^(第一部分讀經|第二部分讀經|福音經課|補充經課|經課與詩篇)[\s:]*", "", clean_trans).strip()
            new_lines.append(clean_trans)

        description = "\n".join(new_lines)
        # 🦃 感恩節專屬彩蛋 (特赦火雞，會跟著存入模板庫傳承百年) 🦃
        if sunday == "Thanksgiving":
            egg_text = "🦃 太18:18 我實在告訴你們，凡你們在地上所捆綁的，在天上也要捆綁；凡你們在地上所釋放的，在天上也要釋放。 🦃"
            if egg_text not in description:
                description = (description + "\n\n" + egg_text).strip()

        hymn_text = get_hymn_text(summary_text, start_date)
        if not hymn_text:
            stats["no_hymn"].append(f"{start_date.strftime('%Y%m%d')} | {summary_text}")
        if hymn_text:
            description += "\n\n今日詩歌：\n" + hymn_text
        # --- 🌟 依據講義與客製化需求加入「代表顏色」 ---
        color_str = get_liturgical_color(season, sunday)
        if color_str:
            description += f"\n\n代表顏色：{color_str}"

        meaning_str = season_meaning_map.get(season, "")
        if meaning_str:
            description += f"\n節期意義：{meaning_str}"

        chinese_cycle = {"A": "甲年", "B": "乙年", "C": "丙年"}[cycle_label]
        subject = f"{subject} ({chinese_cycle})"
        
        # 👇 將洗好的乾淨文字存入模板庫，留給未來生成使用！
        perfect_templates[(cycle_label, season, sunday)] = description 

        event = Event()
        event.add("summary", subject)
        event.add("description", description if description.strip() else subject)
        event.add("dtstart", start_date)
        event.add("dtend", end_date)
        cn_cal.add_component(event)
        stats["yearly_count"][start_date.year] += 1

        # 收集資料供報告使用
        all_final_events.append({"date": check_date, "name": summary_text, "source": "original","description": description})
        
# === 新增：生成 2028/11/27 Advent 1 以後的事件 ===
canonical_set_with_formula = build_canonical_set_with_formula(cal)

# 從 2028 Advent 1 開始生成，直到 END_YEAR 的教會年
for church_year in range(2028, END_YEAR+2):
    advent1 = calculate_advent1(church_year)
    next_advent1 = calculate_advent1(church_year+1)
    cycle_label = determine_cycle(advent1)
    chinese_cycle = {"A": "甲年", "B": "乙年", "C": "丙年"}[cycle_label]
    # [緩衝區]
    daily_buffer = defaultdict(list)

    # 1. 遍歷公式庫生成事件 (Loop 1)
    # 這裡不做任何過濾，完全保留原本邏輯
    for e in canonical_set_with_formula:
        if e["cycle"] != cycle_label: continue
            
        dt = eval_formula(e["formula"], church_year)
        if dt and advent1 <= dt < next_advent1:
            dt_str = dt.strftime('%Y%m%d')
            
            # (以下解析、翻譯、經文邏輯照舊，保持不變)
            season, sunday, display_summary = parse_summary(e["name"])
            translated_summary = translate_summary(e["name"])
            if is_english_title(translated_summary):
                stats["untranslated"].append(f"{dt.strftime('%Y%m%d')} | {e['name']} -> {translated_summary}")
           
            # =====================================================================
            # 🚀 終極簡化：查字典套用模板！
            # =====================================================================
            if (cycle_label, season, sunday) in perfect_templates:
                # 情況 A：前三年有這個事件，直接無腦 Copy 第一個迴圈洗好的完美版！
                description = perfect_templates[(cycle_label, season, sunday)]
            else:
                # 情況 B：前三年沒有這事件（例如主顯節後第五主日），去手動補丁拿！
                scripture_lines = scripture_patch.get(cycle_label, {}).get((season, sunday), [])
                if not scripture_lines:
                    stats["no_scripture"].append(f"{dt.strftime('%Y%m%d')} | {translated_summary} ({e['name']})")
                
                desc_body = "\n".join(scripture_lines)
                hymn_text = get_hymn_text(e["name"], dt)
                if not hymn_text:
                    stats["no_hymn"].append(f"{dt.strftime('%Y%m%d')} | {translated_summary} ({e['name']})")
                    
                description = desc_body + ("\n\n今日詩歌：\n" + hymn_text if hymn_text else "")
                # --- 🌟 未來生成事件也要加入「代表顏色」 ---
                color_str = get_liturgical_color(season, sunday)
                if color_str:
                    description += f"\n\n代表顏色：{color_str}"
                meaning_str = season_meaning_map.get(season, "")
                if meaning_str:
                    description += f"\n節期意義：{meaning_str}"
            # =====================================================================

            subject = f"{translated_summary} ({chinese_cycle})"
            eng_lines = get_english_lines_in_desc(description)            
            if eng_lines:
                stats["untranslated_desc"].append(f"{subject} -> 殘留: {', '.join(eng_lines)}")

            ical_event = Event()
            ical_event.add("summary", subject)
            ical_event.add("description", description if description.strip() else subject)
            ical_event.add("dtstart", dt)
            ical_event.add("dtend", dt + timedelta(days=1))
            
            # 存入緩衝區 (包含最終描述)
            daily_buffer[dt_str].append({
                "event": ical_event,
                "name": e["name"],
                "dt": dt,
                "final_desc": description
            })

    # 2. 寫入 ICS 並建立「最終查閱表」 (Loop 2)
    # ★★★ 這裡最重要：只存最後被選上的事件 ★★★
    final_event_lookup = {} # Key: YYYYMMDD, Value: description
    
    generated_dates = set()
    for dt_str in sorted(daily_buffer.keys()):
        candidates = daily_buffer[dt_str]
        
        # 篩選邏輯：如果重疊，把泛用主日排後面 (保留特殊節期，或者您之前的邏輯)
        if len(candidates) > 1:
            candidates.sort(key=lambda x: (1 if is_generic_sunday(x["name"]) else 0))
        
        selected = candidates[0]
        cn_cal.add_component(selected["event"])
        stats["yearly_count"][selected["dt"].year] += 1
        all_final_events.append({"date": selected["dt"], "name": selected["name"], "source": "generated", "description": selected["final_desc"]})
        generated_dates.add(dt_str)
        
        # 存入查閱表：這就是那一天的「最終真相」
        final_event_lookup[dt_str] = selected["final_desc"]

    # 3. 補漏迴圈：單純查表 (Loop 3)
    curr_sun = advent1
    while curr_sun < next_advent1:
        s_str = curr_sun.strftime('%Y%m%d')
        
        # 如果這天沒資料 (generated_dates 裡沒有)
        if s_str not in generated_dates: 
             
             # 計算「7 天前」的日期
             prev_sun = curr_sun - timedelta(days=7)
             prev_s_str = prev_sun.strftime('%Y%m%d')
             
             # ★ 直接查表：7天前寫了什麼？ ★
             # 因為 final_event_lookup 只存最後贏家，所以抓到的肯定是正確的 (如 五旬節 21)
             if prev_s_str in final_event_lookup:
                 
                 # 1. 標題：固定
                 new_summary = f"補進來的主日 ({chinese_cycle})"
                 
                 # 2. 內容：照抄 7 天前的描述
                 new_desc = final_event_lookup[prev_s_str]
                 
                 # 建立事件
                 ical_event = Event()
                 ical_event.add("summary", new_summary)
                 ical_event.add("dtstart", curr_sun)
                 ical_event.add("dtend", curr_sun + timedelta(days=1))
                 ical_event.add("description", new_desc)
                 
                 cn_cal.add_component(ical_event)
                 all_final_events.append({"date": curr_sun, "name": "Auto-filled (Fixed)", "source": "generated", "description": new_desc})
                 stats["yearly_count"][curr_sun.year] += 1
                 
                 # ★ 把這筆新補的也存回表裡 ★
                 # 這樣如果下週還缺，就會查到這筆，然後繼續抄下去
                 final_event_lookup[s_str] = new_desc
                 generated_dates.add(s_str)
             
        curr_sun += timedelta(days=7)     

# === 輸出檔案 (15年自動分批切割版 - 教會年邏輯) ===
CHUNK_YEARS = 15  # 每 15 個「教會年」切成一個檔案
print("\n開始分批產出 ICS 檔案...")

for chunk_start in range(START_YEAR, END_YEAR + 3, CHUNK_YEARS):
    chunk_end = min(chunk_start + CHUNK_YEARS - 1, END_YEAR + 2)
    
    # 建立這個區間專用的暫存日曆
    temp_cal = Calendar()
    temp_cal.add('prodid', '-//Chinese Lectionary//mxm.dk//')
    temp_cal.add('version', '2.0')
    
    event_count = 0
    # 從總表中把落在這個「教會年區間」的事件挑出來
    for component in cn_cal.subcomponents:
        if component.name == "VEVENT":
            dtstart = component.get('dtstart').dt
            d = dtstart.date() if hasattr(dtstart, 'date') else dtstart
            
            # ★ 關鍵修改：計算該事件屬於哪一個「教會年」(以 Advent 1 為基準)
            adv1 = calculate_advent1(d.year)
            lit_year = d.year if d >= adv1 else d.year - 1
            
            # 用教會年來決定它該被分進哪一個檔案
            if chunk_start <= lit_year <= chunk_end:
                temp_cal.add_component(component)
                event_count += 1
                
    # 只要這個區間有事件，就存成獨立的 ics 檔
    if event_count > 0:
        out_name = f"lectionary_cht_{chunk_start}_{chunk_end}.ics"
        with open(out_name, "wb") as f:
            f.write(temp_cal.to_ical())
        print(f"✅ 已產出: {out_name} (包含 {event_count} 個事件, 教會年 {chunk_start}~{chunk_end})")
        
# === 在寫入報告前，重新精準結算「缺失經文」的事件 ===
stats["no_scripture"] = []

for ev in all_final_events:
    if ev["source"] == "generated":
        name = ev["name"]
        
        # 略過自動補全的主日
        if "Auto-filled" in name or "補進來" in name:
            continue
            
        # 💡 直接赦免感恩節，不檢查它有沒有經文，就像赦免感恩節的火雞
        if "Thanksgiving" in name or "感恩節" in name:
            continue
            
        # 取得我們真正寫入 ICS 的 description
        desc = ev.get("description", "")
        
        # 切割出「今日詩歌」之前的段落 (也就是純經文區塊)
        scripture_part = desc.split("今日詩歌")[0].strip()
        
        # 判斷這個區塊是否真的有經文 (至少要有數字 跟 中文書卷名稱)
        has_digit = bool(re.search(r'\d', scripture_part))
        has_book = False
        for zh_book in book_map.values():
            if zh_book in scripture_part:
                has_book = True
                break
                
        # 只要經文區塊是空的，或沒有數字，或沒有書卷名，這天就是被誤刪或缺經文了！
        if not scripture_part or not has_digit or not has_book:
            dt_str = ev["date"].strftime('%Y%m%d')
            translated = translate_summary(name)
            stats["no_scripture"].append(f"{dt_str} | {translated} ({name})")
            
# === 生成統計報告 (最終修正版：強化規則比對、日期判定與邊界優化) ===
report_file = "generation_report.txt"

with open(report_file, "w", encoding="utf-8") as f:
    f.write(f"=== 經課表生成報告 ({START_YEAR} - {END_YEAR+1}) ===\n")
    f.write(f"生成時間: {datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')}\n\n")

    # A. 整理資料
    events_by_lit_year = defaultdict(list)
    for ev in all_final_events:
        d = ev["date"]
        adv1 = calculate_advent1(d.year)
        lit_year = d.year if d >= adv1 else d.year - 1
        events_by_lit_year[lit_year].append(ev)

    # B. 建立標準範本 (採樣指定年份 + 強制修正錯字)
    target_sample_years = {"A": 2025, "B": 2026, "C": 2027}
    cycle_templates = {"A": set(), "B": set(), "C": set()}
    
    template_corrections = {
        r"Fourtheenth": "Fourteenth",
        r"Twelth": "Twelfth",
        r"Proepr": "Proper",
        r"Twent[- ]?first": "Twenty-first",
        r"Last Sunday (of|in) the Church Year": "Christ the King"
    }

    for ev in all_final_events:
        if ev["source"] == "original" and ev["name"] != "None":
            d = ev["date"]
            adv1 = calculate_advent1(d.year)
            lit_year = d.year if d >= adv1 else d.year - 1
            cycle = determine_cycle(d)
            
            if lit_year == target_sample_years[cycle]:
                clean_name = ev["name"]
                for wrong, right in template_corrections.items():
                    clean_name = re.sub(wrong, right, clean_name, flags=re.IGNORECASE)
                cycle_templates[cycle].add(clean_name.strip())

    # D. 每年事件數量統計 (最終完美版：含重疊事件與補漏分析)
    f.write("每年事件數量統計與異常偵測 (僅列出異常年份):\n")  # ★ 修改這裡
    f.write("-" * 130 + "\n")
    f.write(f"{'教會年':<8} {'週期':<4} {'教會年日期區間 (YYYYMMDD)':<32} | {'數量':<5} | {'狀態'}\n")
    f.write("-" * 130 + "\n")

    # 白名單
    safe_keywords = ["Christmas", "Epiphany", "Ash Wednesday", "Holy Thursday", "Good Friday", "Ascension", "Reformation", "All Saints", "Thanksgiving", "君王", "最後一主日"]

    has_anomalies = False  # ★ 新增這行 (用來追蹤有沒有異常)

    for yr in sorted(events_by_lit_year.keys()):
        if yr < START_YEAR and yr != 2025: continue
        adv1_start = calculate_advent1(yr)
        adv1_next = calculate_advent1(yr + 1)
        cycle = determine_cycle(adv1_start)
        
        current_events = events_by_lit_year[yr]
        actual_dates_str = {e["date"].strftime('%Y%m%d') for e in current_events}
        count = len(current_events)

        # 分析重疊事件 (同一天有多個事件)
        date_counts = defaultdict(list)
        for e in current_events:
            d_str = e["date"].strftime('%Y%m%d')
            date_counts[d_str].append(e["name"])
        
        duplicates = []
        for d, names in date_counts.items():
            if len(names) > 1:
                duplicates.append(f"{d}: {', '.join(names)}")

        # 分析自動補全事件
        auto_filled = [f"{e['date'].strftime('%Y%m%d')}" for e in current_events if "Auto-filled" in e["name"] or "自動補全" in e["name"]]

        # 狀態判定
        status_msgs = []
        if not auto_filled and not duplicates:
            status_msgs.append("完整")
        else:
            if duplicates: status_msgs.append(f"含 {len(duplicates)} 組重疊")
            if auto_filled: status_msgs.append(f"補 {len(auto_filled)} 個主日")

        # 檢查是否有缺失主日 (理論上應該沒有了)
        curr_sun = adv1_start
        missing_sundays = []
        while curr_sun < adv1_next:
            if curr_sun.strftime('%Y%m%d') not in actual_dates_str:
                missing_sundays.append(curr_sun.strftime('%Y%m%d'))
            curr_sun += timedelta(days=7)
        
        if missing_sundays: status_msgs.append(f"缺 {len(missing_sundays)} 主日")
        # ==========================================
        # ★ 新增這三行：如果狀態完整且無缺失，就跳過不印！
        if status_msgs == ["完整"] and not missing_sundays:
            continue
        has_anomalies = True
        # ==========================================

        # 輸出主行
        date_range = f"[{adv1_start.strftime('%Y%m%d')} ~ {(adv1_next - timedelta(days=1)).strftime('%Y%m%d')}]"
        f.write(f"{yr:<10} ({cycle}) {date_range:<32} | {count:<7} | {', '.join(status_msgs)}\n")

        # 輸出詳細資訊
        if duplicates:
            f.write(f"      └─ 重疊事件: {'; '.join(sorted(duplicates))}\n")
        if auto_filled:
            f.write(f"      └─ 自動補全: {', '.join(sorted(auto_filled))}\n")
        if missing_sundays:
            f.write(f"      └─ 缺失主日: {', '.join(missing_sundays)}\n")
    # ★ 新增這兩行：跑完迴圈後，如果都沒有異常就印出恭喜
    if not has_anomalies:
        f.write("恭喜！這 100 年間的所有教會年皆為「完整」狀態，無任何異常事件。\n")
        
# === 取得今日日期字串 (YYYYMMDD) 作為過濾基準 ===
today_str = datetime.datetime.now().strftime('%Y%m%d')

# --- 診斷所有未完全翻譯的事件標題並寫入報表 ---
with open(report_file, "a", encoding="utf-8") as f:
    f.write("\n=== 所有未完全翻譯的事件標題 (未來事件) ===\n")
    future_untranslated = [item for item in stats.get("untranslated", []) if item.split(" | ")[0] >= today_str]
    if not future_untranslated:
        f.write("恭喜！未來的事件皆已成功翻譯。\n")
    else:
        unique_untranslated = sorted(list(set(future_untranslated)))
        for item in unique_untranslated:
            f.write(f"- {item}\n")
    f.write("============================================================\n")

# --- 診斷 Description 中未完全翻譯的事件並寫入報表 ---
with open(report_file, "a", encoding="utf-8") as f:
    f.write("\n=== 所有 Description 未完全翻譯的行 (未來事件) ===\n")
    # 這裡的格式稍微不同是 "XXX -> 殘留: ... "，如果開頭有包含日期可用日期比對，若無則全部印出
    # (依您先前的程式碼，這部分若沒有加上日期前綴，可以維持原樣，或您後續可自行加上日期)
    if not stats.get("untranslated_desc"):
        f.write("恭喜！未來的 Description 皆已無殘留英文。\n")
    else:
        unique_desc = sorted(list(set(stats.get("untranslated_desc", []))))
        for item in unique_desc:
            f.write(f"- {item}\n")
    f.write("============================================================\n")

# --- 診斷沒有對到經文的事件並寫入報表 ---
with open(report_file, "a", encoding="utf-8") as f:
    f.write("\n=== 所有未配對到經文的事件 (缺失經課) ===\n")
    future_no_scripture = [item for item in stats.get("no_scripture", []) if item.split(" | ")[0] >= today_str]
    if not future_no_scripture:
        f.write("恭喜！未來的事件皆已成功配對到經文。\n")
    else:
        unique_no_scripture = sorted(list(set(future_no_scripture)))
        for item in unique_no_scripture:
            f.write(f"- {item}\n")
    f.write("============================================================\n")

# --- 診斷沒有配對到詩歌的事件並寫入報表 ---
with open(report_file, "a", encoding="utf-8") as f:
    f.write("\n=== 所有未配對到詩歌的事件 (缺失詩歌) ===\n")
    future_no_hymn = [item for item in stats.get("no_hymn", []) if item.split(" | ")[0] >= today_str]
    if not future_no_hymn:
        f.write("恭喜！未來的事件皆已成功配對到詩歌。\n")
    else:
        unique_no_hymn = sorted(list(set(future_no_hymn)))
        for item in unique_no_hymn:
            f.write(f"- {item}\n")
    f.write("============================================================\n")

# --- 診斷教會年最後一主日是否為「基督君王主日」 ---
with open(report_file, "a", encoding="utf-8") as f:
    f.write("\n=== 診斷：教會年最後一主日非「基督君王主日」之紀錄 ===\n")
    missing_king_sundays = []

    # 建立一個快速尋找最終事件名稱的字典
    final_events_dict = {}
    for ev in all_final_events:
        if ev["source"] == "generated":
            final_events_dict[ev["date"]] = ev["name"]

    # 檢查我們生成的每一個教會年
    for church_year in range(START_YEAR, END_YEAR + 2):
        # 找出明年的 Advent 1，往前推 7 天就是今年的最後一個主日
        next_advent1 = calculate_advent1(church_year + 1)
        last_sunday = next_advent1 - datetime.timedelta(days=7)

        if last_sunday in final_events_dict:
            raw_name = final_events_dict[last_sunday]
            translated_name = translate_summary(raw_name)
            
            # 檢查原始名稱或翻譯名稱是否包含君王的關鍵字
            if "Christ the King" not in raw_name and "君王" not in translated_name:
                missing_king_sundays.append(f"{last_sunday.strftime('%Y%m%d')} | 應為基督君王，卻產出: {translated_name} ({raw_name})")

    if not missing_king_sundays:
        f.write("恭喜！所有教會年的最後一主日皆正確標示為「基督君王主日」。\n")
    else:
        for item in missing_king_sundays:
            f.write(f"- {item}\n")
    f.write("============================================================\n")    
# --- 診斷：觸發詩歌 Fallback 的事件紀錄 ---
with open(report_file, "a", encoding="utf-8") as f:
    f.write("\n=== 診斷：觸發詩歌 Fallback (備案) 之紀錄 (20251130 起) ===\n")
    
    # ★ 篩選：只抓出日期大於等於 20251130 的項目
    future_fallbacks = [item for item in fallback_tracker if item.startswith("- ") and item[2:10] >= "20251130"]
    
    if not future_fallbacks:
        f.write("恭喜！所有事件都有精確配對到專屬詩歌，沒有觸發任何 Fallback。\n")
    else:
        # 使用 set() 去除重複，並用 sorted() 依照日期排序
        unique_fallbacks = sorted(list(set(future_fallbacks)))
        for item in unique_fallbacks:
            f.write(f"{item}\n")
    f.write("============================================================\n")

print(f"報告已生成: {report_file}")    