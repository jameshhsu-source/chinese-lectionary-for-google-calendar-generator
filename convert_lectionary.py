from icalendar import Calendar, Event
from collections import defaultdict
from datetime import date, timedelta
import datetime
import re
import icalendar
import json

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
    "Pentecost 1": "First Sunday",
    "Pentecost 2": "Second Sunday",
    "Pentecost 3": "Third Sunday",
    "Pentecost 4": "Fourth Sunday",
    "Pentecost 5": "Fifth Sunday",
    "Pentecost 6": "Sixth Sunday",
    "Pentecost 7": "Seventh Sunday",
    "Pentecost 8": "Eighth Sunday",
    "Pentecost 9": "Ninth Sunday",
    "Pentecost 10": "Tenth Sunday",
    "Pentecost 11": "Eleventh Sunday",
    "Pentecost 12": "Twelfth Sunday",
    "Pentecost 13": "Thirteenth Sunday",
    "Pentecost 14": "Fourteenth Sunday",
    "Pentecost 15": "Fifteenth Sunday",
    "Pentecost 16": "Sixteenth Sunday",
    "Pentecost 17": "Seventeenth Sunday",
    "Pentecost 18": "Eighteenth Sunday",
    "Pentecost 19": "Nineteenth Sunday",
    "Pentecost 20": "Twentieth Sunday",

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

# === 英文 → 中文 節期對照表 ===
# === 英文 → 中文 節期與特殊節日對照表 ===
season_map = {
    # === 特殊節日 ===
    "Last Sunday of End Time-Christ  King": "末期最後一主日-基督君王",
    "Christmas Eve": "聖誕夜", 
    "Nativity of Our Lord": "主降生日", 
    "Reformation Day": "宗教改革日",
    "Reformation": "宗教改革日",
    "Christ the King": "基督君王主日",
    "Christ King": "基督君王主日",
    "Christ  King": "基督君王主日",
    "Christ the King Sunday": "基督君王主日",
    "All Saints": "諸聖日",
    "All Saints Day": "諸聖日",
    "All Saints' Day": "諸聖日",
    "Ash Wednesday": "聖灰日",
    "Palm Sunday": "棕枝主日",
    "Maundy Thursday": "濯足節 (聖禮拜四)",
    "Holy Thursday": "濯足節 (聖禮拜四)",
    "Good Friday": "受難日",
    "Holy Saturday": "聖週六",
    "Easter Vigil": "復活前夕守夜",
    "Easter Sunday": "復活節主日",
    "Easter Day": "復活節主日",
    "Pentecost Sunday": "聖靈降臨主日",
    "Day of Pentecost": "聖靈降臨日 (五旬節)",
    "Holy Trinity": "三一主日",
    "Trinity Sunday": "三一主日",
    "Trinity": "三一主日",
    "Presentation of Our Lord": "主奉獻日",
    "Annunciation": "天使報喜日",
    "Visitation": "探望日",
    "Nativity of John the Baptist": "施洗約翰誕辰",
    "Conversion of St. Paul": "聖保羅歸主日",
    "St. Michael and All Angels": "聖米迦勒與眾天使日",
    "Transfiguration of Our Lord": "登山變像日",
    "Transfiguration": "登山變像日",
    "The Baptism of Our Lord": "主受洗日",
    "Baptism of Our Lord": "主受洗日",
    "Epiphany of Our Lord": "主顯節",
    "Ascension": "耶穌升天節",
    "Ascension of Our Lord": "耶穌升天節",
    "Ascension of our Lord": "耶穌升天節",
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
    # === 季節 ===
    "Advent": "將臨期",
    "Christmas": "聖誕期",
    "Epiphany": "主顯節",
    "Ephphany": "主顯節",
    "Lent": "預苦期",
    "Holy Week": "聖週",
    "Easter": "復活節期",
    "Pentecost": "五旬節",
    "Ordinary Time": "常年期",
    "End Time": "末期"
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
    # Advent
    ("Advent", "First Sunday"): [
        "約書亞：《愛降世》",
        "讚美之泉：《最美的禮物》",
        "小羊：《聖善夜》"
    ],
    ("Advent", "Second Sunday"): [
        "約書亞：《更多尋求祢》",
        "讚美之泉：《主祢是我力量》",
        "小羊：《願祢的國降臨》"
    ],
    ("Advent", "Third Sunday"): [
        "約書亞：《祢愛真實》",
        "讚美之泉：《我們歡慶聖誕》",
        "小羊：《普世歡騰》"
    ],
    ("Advent", "Fourth Sunday"): [
        "約書亞：《祢掌權》",
        "讚美之泉：《有一位神》",
        "小羊：《神的帳幕在人間》"
    ],
    ("Advent", None): [  # fallback = First Sunday
        "約書亞：《這就是愛了》",
        "讚美之泉：《是為了愛》",
        "小羊：《讓小小燈火四處燃起》"
    ],

    # Christmas
    ("Christmas", "Christmas Eve"): [
        "約書亞：《普世歡騰》",
        "讚美之泉：《聖誕之願》",
        "小羊：《神的帳幕在人間》"
    ],
    ("Christmas", "Christmas Day"): [
        "約書亞：《祂好愛我》",
        "讚美之泉：《恩典之路》",
        "小羊：《一粒麥子》"
    ],
    ("Christmas", "First Sunday"): [
        "約書亞：《使我得生命》",
        "讚美之泉：《主禱文》",
        "小羊：《如果》"
    ],
    ("Christmas", "Second Sunday"): [
        "約書亞：《聽啊天使高聲唱》",
        "讚美之泉：《是為了愛》",
        "小羊：《眾神之中有誰能像祢》"
    ],
    ("Christmas", "Third Sunday"): [
        "約書亞：《榮美的救主》",
        "讚美之泉：《我們歡慶聖誕》",
        "小羊：《聖善夜》"
    ],
    ("Christmas", "Fourth Sunday"): [
        "約書亞：《愛降世》",
        "讚美之泉：《最美的禮物》",
        "小羊：《普世歡騰》"
    ],
    ("Christmas", None): [  # fallback = First Sunday
        "約書亞：《這就是愛了》",
        "讚美之泉：《榮耀歸於至高真神》",
        "小羊：《神的羔羊》"
    ],

    # Epiphany
    ("Epiphany", "Epiphany"): [
        "約書亞：《祢掌權》",
        "讚美之泉：《主祢是我力量》",
        "小羊：《願祢的國降臨》"
    ],
    ("Epiphany", "First Sunday"): [
        "約書亞：《求充滿這地》",
        "讚美之泉：《充滿我》",
        "小羊：《醫治這地》"
    ],
    ("Epiphany", "Second Sunday"): [
        "約書亞：《主的愛》",
        "讚美之泉：《不要忘記》",
        "小羊：《為我造清潔的心》"
    ],
    ("Epiphany", "Third Sunday"): [
        "約書亞：《更多尋求祢》",
        "讚美之泉：《主祢是我力量》",
        "小羊：《願祢的國降臨》"
    ],
    ("Epiphany", "Fourth Sunday"): [
        "約書亞：《祂好愛我》",
        "讚美之泉：《恩典之路》",
        "小羊：《一粒麥子》"
    ],
    ("Epiphany", "Fifth Sunday"): [
        "約書亞：《使我得生命》",
        "讚美之泉：《主禱文》",
        "小羊：《如果》"
    ],
    ("Epiphany", "Sixth Sunday"): [
        "約書亞：《祢掌權》",
        "讚美之泉：《雲上太陽》",
        "小羊：《神的帳幕在人間》"
    ],
    ("Epiphany", "Seventh Sunday"): [
        "約書亞：《榮美的救主》",
        "讚美之泉：《恩典之路》",
        "小羊：《那一天》"
    ],
    ("Epiphany", "Last Sunday"): [
        "約書亞：《祢掌權》",
        "讚美之泉：《主祢是我力量》",
        "小羊：《願祢的國降臨》"
    ],
    ("Epiphany", "Transfiguration"): [
        "約書亞：《榮美的救主》",
        "讚美之泉：《雲上太陽》",
        "小羊：《神的帳幕在人間》"
    ],
    ("Epiphany", None): [  # fallback = First Sunday
        "約書亞：《求充滿這地》",
        "讚美之泉：《充滿我》",
        "小羊：《醫治這地》"
    ],

    # Lent
    ("Lent", "First Sunday"): [
        "約書亞：《祂好愛我》",
        "讚美之泉：《有一位神》",
        "小羊：《一粒麥子》"
    ],
    ("Lent", "Second Sunday"): [
        "約書亞：《榮美的救主》",
        "讚美之泉：《恩典之路》",
        "小羊：《那一天》"
    ],
    ("Lent", "Third Sunday"): [
        "約書亞：《更多尋求祢》",
        "讚美之泉：《主祢是我力量》",
        "小羊：《願祢的國降臨》"
    ],
    ("Lent", "Fourth Sunday"): [
        "約書亞：《祢掌權》",
        "讚美之泉：《雲上太陽》",
        "小羊：《神的帳幕在人間》"
    ],
    ("Lent", "Fifth Sunday"): [
        "約書亞：《使我得生命》",
        "讚美之泉：《主禱文》",
        "小羊：《如果》"
    ],
    ("Lent", "Ash Wednesday"): [
        "約書亞：《純潔的心》",
        "讚美之泉：《十架的愛》",
        "小羊：《為我造清潔的心》"
    ],
    ("Lent", None): [  # fallback = First Sunday
        "約書亞：《祂好愛我》",
        "讚美之泉：《有一位神》",
        "小羊：《一粒麥子》"
    ],

    # Holy Week
    ("Holy Week", "Palm Sunday"): [
        "約書亞：《祢掌權》",
        "讚美之泉：《主祢是我力量》",
        "小羊：《願祢的國降臨》"
    ],
    ("Holy Week", "Maundy Thursday"): [
        "約書亞：《更多尋求祢》",
        "讚美之泉：《主祢是我力量》",
        "小羊：《願祢的國降臨》"
    ],
    ("Holy Week", "Good Friday"): [
        "約書亞：《榮美的救主》",
        "讚美之泉：《恩典之路》",
        "小羊：《那一天》"
    ],
    ("Holy Week", "Holy Saturday"): [
        "約書亞：《祂好愛我》",
        "讚美之泉：《有一位神》",
        "小羊：《一粒麥子》"
    ],
    ("Holy Week", None): [  # fallback = Palm Sunday
        "約書亞：《祢掌權》",
        "讚美之泉：《主祢是我力量》",
        "小羊：《願祢的國降臨》"
    ],

    # Easter
    ("Easter", "Easter Sunday"): [
        "約書亞：《使我得生命》",
        "讚美之泉：《主禱文》",
        "小羊：《如果》"
    ],
    ("Easter", "Second Sunday"): [
        "約書亞：《祂好愛我》",
        "讚美之泉：《有一位神》",
        "小羊：《一粒麥子》"
    ],
    ("Easter", "Third Sunday"): [
        "約書亞：《更多尋求祢》",
        "讚美之泉：《雲上太陽》",
        "小羊：《神的帳幕在人間》"
    ],
    ("Easter", "Fourth Sunday"): [
        "約書亞：《甦醒》",
        "讚美之泉：《和散那》",
        "小羊：《祢與我同在》"
    ],
    ("Easter", "Fifth Sunday"): [
        "約書亞：《祢掌權》",
        "讚美之泉：《雲上太陽》",
        "小羊：《神的帳幕在人間》"
    ],
    ("Easter", "Sixth Sunday"): [
        "約書亞：《祢掌權》",
        "讚美之泉：《雲上太陽》",
        "小羊：《神的帳幕在人間》"
    ],
    ("Easter", "Seventh Sunday"): [
        "約書亞：《榮美的救主》",
        "讚美之泉：《恩典之路》",
        "小羊：《那一天》"
    ],
    ("Easter", "Ascension"): [
        "約書亞：《祢掌權》",
        "讚美之泉：《主祢是我力量》",
        "小羊：《願祢的國降臨》"
    ],
    ("Easter", "Ascension of Our Lord"): [
         "約書亞：《祢掌權》",
        "讚美之泉：《主祢是我力量》",
        "小羊：《願祢的國降臨》"
    ],
    ("Easter", None): [  # fallback = First Sunday (Easter Sunday)
        "約書亞：《使我得生命》",
        "讚美之泉：《主禱文》",
        "小羊：《如果》"
    ],
    # Pentecost
    ("Pentecost", "Pentecost Sunday"): [
        "約書亞：《親愛聖靈》",
        "讚美之泉：《充滿我》",
        "小羊：《醫治這地》"
    ],
    ("Pentecost", "First Sunday"): [
        "約書亞：《求充滿這地》",
        "讚美之泉：《聖靈的火》",
        "小羊：《全地在歌唱》"
    ],
    ("Pentecost", "Second Sunday"): [
        "約書亞：《溫柔聖靈》",
        "讚美之泉：《充滿我》",
        "小羊：《聖靈的河》"
    ],
    ("Pentecost", "Third Sunday"): [
        "約書亞：《更多尋求祢》",
        "讚美之泉：《充滿我》",
        "小羊：《醫治這地》"
    ],
    ("Pentecost", None): [  # fallback = First Sunday
        "約書亞：《親愛聖靈》",
        "讚美之泉：《聖靈的火》",
        "小羊：《聖靈的河》"
    ],

    # Ordinary Time
    ("Ordinary Time", "Trinity Sunday"): [
        "約書亞：《更多尋求祢》",
        "讚美之泉：《雲上太陽》",
        "小羊：《神的帳幕在人間》"
    ],
    ("Ordinary Time", "First Sunday"): [
        "約書亞：《聖靈來風》",
        "讚美之泉：《主祢是我力量》",
        "小羊：《燃燒我的心》"
    ],
    ("Ordinary Time", "Second Sunday"): [
        "約書亞：《主掌權》",
        "讚美之泉：《為榮耀的創造》",
        "小羊：《我願為活祭》"
    ],
    # Saints Triumphant (聖徒得勝日 / End Time 3)
    ("Ordinary Time", "Saints Triumphant"): [
        "約書亞：《祢配得全所有》",
        "讚美之泉：《這世代》",
        "小羊：《萬民同來敬拜》"
    ],
    # Last Judgment (End Time 2)
    ("Ordinary Time", "Last Judgment"): [
        "約書亞：《祢掌權》",
        "讚美之泉：《有一位神》",
        "小羊：《抬頭仰望》"
    ],
    ("Ordinary Time", None): [  # fallback = First Sunday
        "約書亞：《聖靈請祢來充滿我心》",
        "讚美之泉：《不要忘記》",
        "小羊：《因我所遭遇的是出於祢》"
    ],
    # Christ the King (教會年最後一主日)
    ("Ordinary Time", "Christ the King"): [
        "約書亞：《祢掌權》",
        "讚美之泉：《主祢是我力量》",
        "小羊：《我心堅定於祢》"
    ],
    ("Ordinary Time", "Reformation"): [
        "約書亞：《佔據我心》",
        "讚美之泉：《不動搖的信心》",
        "小羊：《願祢的國降臨》" 
    ],
    # All Saints
    ("Ordinary Time", "All Saints"): [
        "約書亞：《祢配得全所有》",
        "讚美之泉：《這世代》",
        "小羊：《萬民同來敬拜》"
    ],
    ("Ordinary Time", "Thanksgiving"): [
        "約書亞：《感謝祢》",
        "讚美之泉：《數不盡》",
        "小羊：《陪我走過春夏秋冬》"
    ]
}

for i in range(1, 33):
    hymn_map[(f"Ordinary Time", f"Proper {i}")] = [
        "約書亞：《祢掌權》",
        "讚美之泉：《主祢是我力量》",
        "小羊：《願祢的國降臨》"
    ]

# 新增：主顯節延長週數的詩歌捷徑
hymn_map[("Epiphany", "Sixth Sunday after Epiphany")] = hymn_map.get(("Epiphany", "Sixth Sunday"), [])
hymn_map[("Epiphany", "Seventh Sunday after Epiphany")] = hymn_map.get(("Epiphany", "Seventh Sunday"), [])
hymn_map[("Epiphany", "Eighth Sunday after Epiphany")] = hymn_map.get(("Epiphany", "Eighth Sunday"), [])
hymn_map[("Epiphany", "Ninth Sunday after Epiphany")] = hymn_map.get(("Epiphany", "Ninth Sunday"), [])

cycle_map = {"A": "甲", "B": "乙", "C": "丙"}

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
        summary = summary.replace(match.group(0), f"(普通期第{proper_num}組經課)")    
    match_plain = re.search(r"Proper\s+(\d+)", summary, flags=re.IGNORECASE)
    if match_plain:
        proper_num = match_plain.group(1)
        return f"普通期第{proper_num}組經課"

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

    summary = re.sub(r"^(五旬節|將臨期|聖誕期|主顯節|預苦期|復活節期|常年期)\s+(\d+)$", r"\1 第\2主日", summary)

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
        return "Easter", "Ascension", "耶穌升天節"
    if "Reformation" in raw_summary:
        return "Ordinary Time", "Reformation", "宗教改革日"
    if "Palm Sunday" in raw_summary or "Passion" in raw_summary:
        return "Holy Week", "Palm Sunday", "棕枝主日"
    if "Transfiguration" in raw_summary:
        return "Epiphany", "Transfiguration", "登山變像日"
    if "Trinity" in raw_summary:
        return "Ordinary Time", "Trinity Sunday", "三一主日"
    if "All Saints" in raw_summary:
        return "Ordinary Time", "All Saints", "諸聖日"
    # 處理 "Last Sunday of the Church Year" [cite: 2153] 與 "Christ the King"
    if "Christ the King" in raw_summary or ("Last Sunday" in raw_summary and "Church Year" in raw_summary):
        return "Ordinary Time", "Christ the King", "基督君王主日"
    if "Ash Wednesday" in raw_summary:
        return "Lent", "Ash Wednesday", "聖灰日"
    if "Maundy" in raw_summary or "Holy Thursday" in raw_summary:
        return "Holy Week", "Maundy Thursday", "濯足節"
    if "Good Friday" in raw_summary:
        return "Holy Week", "Good Friday", "受難日"
    if "Easter Vigil" in raw_summary:
        return "Easter", "Easter Vigil", "復活前夕守夜"
    if "Baptism" in raw_summary:
        return "Epiphany", "First Sunday", "主受洗日"

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

    # 先查精確的 (season, sunday)
    hymns = hymn_map.get((season, sunday))

    # 如果沒有，查季節預設 (season, None)
    if not hymns:
        hymns = hymn_map.get((season, None))

    # 如果還是沒有，給一個 fallback 提示
    if not hymns:
        return ""

    return "\n".join(hymns)

def build_scripture_map(cal):
    """
    從既有 ICS 檔案建立 scripture_map
    使用 parse_summary 標準化 Key，確保特殊節日名稱一致
    """
    scripture_map = {}

    for component in cal.walk("VEVENT"):
        summary_text = str(component.get("summary"))
        description = str(component.get("description") or "").strip()

        # [關鍵] 使用修改後的 parse_summary 來標準化 Key
        # 這樣 "Palm Sunday/Sunday of the Passion" 就會變成 ("Holy Week", "Palm Sunday")
        season, sunday, _ = parse_summary(summary_text)

        if season and sunday and description:
            # 把 DESCRIPTION 拆成行，過濾掉空行
            lines = [line.strip() for line in description.splitlines() if line.strip()]

            # 過濾掉「今日詩歌」之後的部分，只保留經文
            scripture_lines = []
            for line in lines:
                if line.startswith("今日詩歌") or "Hymn of the Day" in line:
                    break
                scripture_lines.append(line)

            # 存入 map
            scripture_map[(season, sunday)] = scripture_lines

    return scripture_map
    
def build_canonical_set(cal):
    """
    從 ICS 檔案抓出所有 SUMMARY 行，建立事件名稱清單 (canonical set)。
    這份清單就是唯一的事件名稱來源。
    """
    canonical_set = set()
    for component in cal.walk("VEVENT"):
        summary_text = str(component.get("summary")).strip()
        if summary_text:
            canonical_set.add(summary_text)
    return sorted(canonical_set)

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
    # 復活節期其他主日
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

            #formula = determine_formula(season_keeping_summary)
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
    """抓出 Description 中包含英文的行，排除網址、專有名詞與經文後綴 (a,b,c)"""
    lines_with_english = []
    for line in text.splitlines():
        # 1. 移除網址
        clean_line = re.sub(r'http[s]?://\S+', '', line)
        
        # 2. 移除 Google Meet 與單獨的 Meet (專有名詞)
        clean_line = re.sub(r'Google Meet|Meet', '', clean_line, flags=re.IGNORECASE)
        
        # 3. ★ 排除經文中的 a, b, c 標記 (例如 5:2-5a, 119b, 7b-10)
        # 規則：數字後面緊跟著 a, b 或 c 的情況，將該字母抹除再進行檢查
        clean_line = re.sub(r'(?<=\d)[abc]', '', clean_line)
        
        # 4. 檢查這行是否還有剩餘的英文字母 A-Za-z
        if re.search(r'[A-Za-z]', clean_line):
            lines_with_english.append(line.strip())
    return lines_with_english
    
# === 年度範圍設定 ===
START_YEAR = 2025
YEARS = 101
END_YEAR = START_YEAR + YEARS - 1

with open("lectionary.ics", "rb") as f:
    cal = Calendar.from_ical(f.read())

canonical_events = build_canonical_set(cal)

cn_cal = Calendar()
cn_cal.add('prodid', '-//Chinese Lectionary//mxm.dk//')
cn_cal.add('version', '2.0')

events = []
original_events = []
scripture_map = build_scripture_map(cal)

# 用來記錄已經處理過的日期
seen_dates_original = set()

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
        description = description.replace("", "-").replace("–", "-").replace("—", "-")
        lines = description.splitlines()
        # === 新增: 找到第一個 phrase_map 相關的片語位置 ===
        start_index = 0
        found_match = False  # 新增一個標記
        for i, line in enumerate(lines):
            for phrase in phrase_map.keys():
                if phrase.lower() in line.lower():
                    start_index = i
                    found_match = True  # 標記已找到
                    break
            if found_match:  # 只要找到了，不管 index 是多少，立刻停止搜尋
                break

        # 只保留從第一個片語開始的行
        lines = lines[start_index:]
        merged_lines = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if i + 1 < len(lines) and re.match(r"^\d+$", lines[i+1].strip()):
                # 下一行是純數字，合併成「書卷名稱 + 空格 + 數字」
                merged_lines.append(line + " " + lines[i+1].strip())
                i += 2
            else:
                merged_lines.append(line)
                i += 1
        lines = merged_lines
        new_lines = []
        skip_mode = False

        for line in lines:
            if "Prayer of the Day" in line:
                skip_mode = True
                continue
            if skip_mode:
                continue
            if re.match(r"^\s*\d+\s+[A-Za-z]", line) and ":" not in line:
                continue
            if re.match(r"^\s*(First Reading|Second Reading|Gospel)", line, flags=re.IGNORECASE):
                continue
            if line.strip() == "":
                new_lines.append("")
                continue
            if re.search(r"(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth|Thirteenth|Fourteenth|Fifteenth|Sixteenth|Seventeenth|Eighteenth|Nineteenth|Twentieth|Twenty-first|Twenty-second|Twenty-third|Twenty-fourth|Twenty-fifth|Twenty-sixth|Twenty-seventh|Twenty-eighth|Twenty-ninth|Thirtieth) Sunday (after|of|in)", line, flags=re.IGNORECASE):
                line = translate_summary(line)
            new_lines.append(translate_text(line, cycle_label, season, sunday))

        description = "\n".join(new_lines)

        hymn_text = get_hymn_text(summary_text, start_date)
        # 檢查詩歌
        if not hymn_text:
            stats["no_hymn"].append(f"{start_date.strftime('%Y%m%d')} | {summary_text}")
        if hymn_text:
            description += "\n\n今日詩歌：\n" + hymn_text

        chinese_cycle = {"A": "甲年", "B": "乙年", "C": "丙年"}[cycle_label]
        subject = f"{subject} ({chinese_cycle})"
        # 檢查 DESCRIPTION 是否含英文，有的話就抓出來記進 stats
        eng_lines = get_english_lines_in_desc(description)
        if eng_lines:
            # 第一個迴圈請用 check_date.strftime('%Y%m%d')，第二個迴圈請用 dt_str
            # 為了方便，我們統一抓 subject (標題) 跟殘留英文的行
            stats["untranslated_desc"].append(f"{subject} -> 殘留: {', '.join(eng_lines)}")
        event = Event()
        event.add("summary", subject)
        event.add("description", description if description.strip() else subject)
        event.add("dtstart", start_date)
        event.add("dtend", end_date)
        cn_cal.add_component(event)
        stats["yearly_count"][start_date.year] += 1

        # 收集資料供報告使用
        all_final_events.append({"date": check_date, "name": summary_text, "source": "original"})
        
        events.append({
            "date": start_date.strftime("%Y%m%d"),
            "subject": subject,
            "description": description,
            "hymns": hymns
        })

        # === 新增：收集原始 ICS 事件清單 ===
        original_events.append({
            "name": summary_text,
            "date": start_date.strftime("%Y%m%d")
        })

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
            # 先去補丁找有沒有該年專屬的經文
            scripture_lines = scripture_patch.get(cycle_label, {}).get((season, sunday))
            # 如果補丁裡沒有，才從原始範本抓出來的字典找
            if not scripture_lines:
                scripture_lines = scripture_map.get((season, sunday), [])
            if not scripture_lines:
                stats["no_scripture"].append(f"{dt.strftime('%Y%m%d')} | {translated_summary} ({e['name']})")            
            scripture_lines = [line.replace("–", "-").replace("–", "-").replace("—", "-") for line in scripture_lines]
            merged_lines = []
            i = 0
            while i < len(scripture_lines):
                line = scripture_lines[i].strip()
                if i + 1 < len(scripture_lines) and re.match(r"^\d+$", scripture_lines[i+1].strip()):
                    merged_lines.append(line + " " + scripture_lines[i+1].strip())
                    i += 2
                else:
                    merged_lines.append(line)
                    i += 1
            lines = merged_lines
            new_lines = []
            skip_mode = False
            for line in lines:
                if "Prayer of the Day" in line:
                    skip_mode = True
                    continue
                if skip_mode: continue
                if re.match(r"^\s*\d+\s+[A-Za-z]", line) and ":" not in line: continue
                if re.match(r"^\s*(First Reading|Second Reading|Gospel)", line, flags=re.IGNORECASE): continue
                if line.strip() == "":
                    new_lines.append("")
                    continue
                if re.search(r"(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth|Thirteenth|Fourteenth|Fifteenth|Sixteenth|Seventeenth|Eighteenth|Nineteenth|Twentieth|Twenty-first|Twenty-second|Twenty-third|Twenty-fourth|Twenty-fifth|Twenty-sixth|Twenty-seventh|Twenty-eighth|Twenty-ninth|Thirtieth) Sunday (after|of|in)", line, flags=re.IGNORECASE):
                    line = translate_summary(line)
                new_lines.append(translate_text(line, cycle_label, season, sunday))

            description = "\n".join(new_lines)
            hymn_text = get_hymn_text(e["name"], dt)
            # ★ 新增：如果找不到詩歌，就記錄到 stats 裡
            if not hymn_text:
                stats["no_hymn"].append(f"{dt.strftime('%Y%m%d')} | {translated_summary} ({e['name']})")
            if hymn_text:
                description += "\n\n今日詩歌：\n" + hymn_text                
            
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
        all_final_events.append({"date": selected["dt"], "name": selected["name"], "source": "generated"})
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
                 all_final_events.append({"date": curr_sun, "name": "Auto-filled (Fixed)", "source": "generated"})
                 stats["yearly_count"][curr_sun.year] += 1
                 
                 # ★ 把這筆新補的也存回表裡 ★
                 # 這樣如果下週還缺，就會查到這筆，然後繼續抄下去
                 final_event_lookup[s_str] = new_desc
                 generated_dates.add(s_str)
             
        curr_sun += timedelta(days=7)     
# # === 輸出檔案 (15年自動分批切割版) ===
# CHUNK_YEARS = 15  # 每 15 年切成一個檔案，確保 Google 日曆順暢匯入
# print("\n開始分批產出 ICS 檔案...")

# for chunk_start in range(START_YEAR, END_YEAR + 3, CHUNK_YEARS):
    # chunk_end = min(chunk_start + CHUNK_YEARS - 1, END_YEAR + 2)
    
    # # 建立這個區間專用的暫存日曆
    # temp_cal = Calendar()
    # temp_cal.add('prodid', '-//Chinese Lectionary//mxm.dk//')
    # temp_cal.add('version', '2.0')
    
    # event_count = 0
    # # 從剛剛算好的 cn_cal 總表中，把落在這個區間的事件挑出來
    # for component in cn_cal.subcomponents:
        # if component.name == "VEVENT":
            # dtstart = component.get('dtstart').dt
            # # 兼容 datetime 和 date 格式
            # year = dtstart.year if hasattr(dtstart, 'year') else dtstart.date().year
            
            # if chunk_start <= year <= chunk_end:
                # temp_cal.add_component(component)
                # event_count += 1
                
    # # 只要這個區間有事件，就存成獨立的 ics 檔
    # if event_count > 0:
        # out_name = f"lectionary_cht_{chunk_start}_{chunk_end}.ics"
        # with open(out_name, "wb") as f:
            # f.write(temp_cal.to_ical())
        # print(f"✅ 已產出: {out_name} (包含 {event_count} 個事件)")

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
            
        season, sunday, display_summary = parse_summary(name)
        cycle_label = determine_cycle(ev["date"])
        
        # 1. 先查新補丁
        has_scripture = scripture_patch.get(cycle_label, {}).get((season, sunday))
        
        # 2. 如果補丁沒有，再去查原始的舊字典
        if not has_scripture:
            has_scripture = scripture_map.get((season, sunday), [])
            
        # 3. ★ 簡單粗暴的判斷邏輯：如果沒東西，或者裡面有「請填入」，就是缺失！
        is_missing = False
        if not has_scripture:
            is_missing = True
        elif any("請填入" in str(line) for line in has_scripture):
            is_missing = True
            
        # 兩邊都沒有(或只有佔位符)才正式寫入缺失報告
        if is_missing:
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
    f.write("每年事件數量統計與異常偵測:\n")
    f.write("-" * 130 + "\n")
    f.write(f"{'教會年':<8} {'週期':<4} {'教會年日期區間 (YYYYMMDD)':<32} | {'數量':<5} | {'狀態'}\n")
    f.write("-" * 130 + "\n")

    # 白名單
    safe_keywords = ["Christmas", "Epiphany", "Ash Wednesday", "Holy Thursday", "Good Friday", "Ascension", "Reformation", "All Saints", "Thanksgiving", "君王", "最後一主日"]

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
print(f"報告已生成: {report_file}")    