OPEN_CLOSE_BRACKET_REGREX = r'\(([^)]+)\)'
TITLE_INDEX_REGREX = r'^(m{0,4}(ix|iv|v?i{0,3})|([a-f]{1})|([0-9]{1}))\.?$'
ROMAN_NUMERAL_INDEX_REGREX = "^m{0,4}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})\.? "
BULLET_POINT_RE = r'^[0-9]$|^[!"#$%&''()*+,-./:;<=>?@[\]^_`{|}~]$|^[0-9][!"#$%&''()*+,-./:;<=>?@[\]^_`{|}~]$'
OCR_VOCAB_RE = r'^[aAàÀảẢãÃáÁạẠăĂằẰẳẲẵẴắẮặẶâÂầẦẩẨẫẪấẤậẬbBcCdDđĐeEèÈẻẺẽẼéÉẹẸêÊềỀểỂễỄếẾệỆfFgGhHiIìÌỉỈĩĨíÍịỊjJkKlLmMnNoOòÒỏỎõÕóÓọỌôÔồỒổỔỗỖốỐộỘơƠờỜởỞỡỠớỚợỢpPqQrRsStTuUùÙủỦũŨúÚụỤưƯừỪửỬữỮứỨựỰvVwWxXyYỳỲỷỶỹỸýÝỵỴzZ0123456789!"#$%&''()*+,-./:;<=>?@[\]^_`{|}~ ]+$'
VN_CITIES = ["hà nội", "hồ chí minh", "hải phòng", "đà nẵng", "cần thơ", 'quảng nam', 'quảng ngãi', 'quảng ninh',
             'quảng trị', 'sóc trăng', 'sơn la', 'tây ninh', 'thái bình', 'thái nguyên', 'thanh hóa', 'thừa thiên huế',
             'tiền giang', 'trà vinh', 'tuyên quang', 'vĩnh long', 'vĩnh phúc', 'yên bái', 'phú yên', 'hà nam',
             'hà tĩnh', 'hải dương', 'hậu giang', 'hòa bình', 'hưng yên', 'khánh hòa', 'kiên giang', 'kon tum',
             'lai châu', 'lâm đồng', 'lạng sơn', 'lào cai', 'long an', 'nam định', 'nghệ an', 'ninh bình', 'ninh thuận',
             'phú thọ', 'quảng bình', 'an giang', 'bà rịa - vũng tàu', 'bắc giang', 'bắc kạn', 'bạc liêu', 'bắc ninh',
             'bến tre', 'bình định', 'bình dương', 'bình phước', 'bình thuận', 'cà mau', 'cao bằng', 'đắk lắk',
             'đắk nông', 'điện biên', 'đồng nai', 'đồng tháp', 'gia lai', 'hà giang', 'tt huế', 't t huế']
TEXT_REPLACEMENTS = [
    ("\x01", " "),
    (" ", " "),
    ("\t", " "),
    ("…", "..."),
    ("—", "-"),
    ("–", "-"),
    ("•", "-"),
    ("★", "-"),
    ("", "-"),
    ("", "-"),
    ("ò", "*"),
    ("⇒", "=>"),
    ("ﬁ", "fi"),
    ("�", ""),  # \x08 backspace
    ("\r", ""),
    ("", "X"),  # checkmark
    ("●", "-"),
    ("́", ""),  # dấu sắc
    ("̀", ""),  # dấu huyền
    ("̉", ""),  # dấu hỏi
    ("̣", ""),  # dấu nặng
    ("̃", ""),  # dấu ngã
]
TEXT_REPLACEMENTS_REGREX = r"[_-]{2,}"

IMG_WIDTH = 1000
IMG_HEIGHT = 600

TIME_RANGE_REGREX = r'(from|tu) [0-9\/]{4,} (to |den )?([0-9\/]{4,}|now|present|hien tai)'
ONNX_PROVIDERS = {
    "cpu": ['CPUExecutionProvider'],
    "cuda": ['TensorrtExecutionProvider', 'CUDAExecutionProvider'],
    "gpu": ['TensorrtExecutionProvider', 'CUDAExecutionProvider']
}

DAY_MAP = {
    "Monday": "Thứ 2",
    "Tuesday": "Thứ 3",
    "Wednesday": "Thứ 4",
    "Thursday": "Thứ 5",
    "Friday": "Thứ 6",
    "Saturday": "Thứ 7",
    "Sunday": "Chủ nhật"
}

STORE_COORDINATES = {"longitude": 16.036285067313134, "latitude": 108.21766380071921}
FREE_DELIVERY_DISTANCE_KM = 5.0
MID_TIER_DISTANCE_KM = 10.0
MID_TIER_FEE = 15000

STORE_LOCATIONS = [
    "- Cơ sở 1: 59 Đ. Lê Duẩn, Hải Châu 1, Hải Châu, Đà Nẵng. Tel 0236.3888.348",
    "- Cơ sở 2: 143 Điện Biên Phủ, Chính Gián, Thanh Khê, Đà Nẵng. Tel: 0236.3626.799",
    "- Cơ sở 3: 2 Xô Viết Nghệ Tĩnh, Hoà Cường Nam, Hải Châu, Đà Nẵng. Tel: 0236.3799.679",
    "- Cơ sở 4: 78 Lê Thanh Nghị, Hoà Cường Bắc, Hải Châu, Đà Nẵng. Tel: 0236.3619.779",
    "- Cơ sở 5: 68 Hàm Nghi, Thạc Gián, Hải Châu, Đà Nẵng. Tel: 0236.3836.779"
]
EXTRA_ITEM_PRICES = {
    "extra_plate_set": 10000,  # Bộ Dĩa + Muỗng giấy (10 cái dĩa + 10 muỗng)
    "extra_hat": 8000,  # Mũ sinh nhật giấy
    "topper": 12000,  # Topper cắm "Happy Birthday"
}

OCCASIONS = [
    ["wedding", "đám cưới", "kết hôn", "lễ cưới", "tiệc cưới", "hôn lễ", "honeymoon",
     "cô dâu", "chú rể", "bride", "groom", "nhẫn cưới", "hoa cưới", "váy cưới", "vest",
     "tiệc mừng", "lứa đôi", "ngày trọng đại", "hạnh phúc", "vĩnh cửu", "forever", "tiệc độc thân", "cưới"],
    ["anniversary", "wedding anniversary", "ngày kỷ niệm", "đám cưới bạc", "đám cưới vàng",
     "silver wedding", "golden wedding", "tình yêu", "kỷ niệm", "lứa đôi", "vĩnh cửu",
     "hạnh phúc", "mãi mãi", "forever", "love", "trái tim", "heart", "rose", "hoa hồng", "kỷ niệm ngày cưới"],
    ["cúng", "grand opening", "opening ceremony", "lễ khai trương", "khai mạc", "opening",
     "business", "công ty", "doanh nghiệp", "thành công", "phát đạt", "may mắn", "tài lộc",
     "phong thủy", "tiền tài", "prosperity", "success", "lucky", "fortune", "mèo thần tài", "khai trương"],
    ["long life celebration", "cúng", "thượng thọ", "đại thọ", "khánh thọ", "long life", "trường thọ",
     "sức khỏe", "health", "phúc lộc thọ", "tuổi thọ", "cụ", "ông bà", "ancestor",
     "trang nghiêm", "truyền thống", "classical", "cổ điển", "thanh lịch", "elegant", "mừng thọ"],
    ["graduation", "commencement", "graduate", "tốt nghiệp", "ra trường", "học vị", "diploma",
     "bằng cấp", "mũ tốt nghiệp", "áo choàng", "gown", "cap", "trường học", "tri thức",
     "tương lai", "hành trình mới", "thành công", "chúc mừng", "congratulations", "lễ tốt nghiệp"],
    ["đón em bé", "baby shower", "welcome baby", "đón em bé", "new born", "mới sinh", "nhà có trẻ",
     "baby", "bé yêu", "con trai", "con gái", "boy", "girl", "chào đời", "tã em bé",
     "bình sữa", "núm vú giả", "xe đẩy", "cũi em bé", "màu xanh", "màu hồng", "sơ sinh", "thôi nôi"],
    ["ngày lễ tình nhân", "valentine's day", "14/2", "ngày tình yêu", "love day", "love",
     "tình yêu", "trái tim", "heart", "hoa hồng", "rose", "quà tặng", "chocolate", "socola",
     "lãng mạn", "romantic", "đôi", "couple", "người yêu", "bạn trai", "bạn gái", "valentine"],
    ["christmas", "noel", "lễ giáng sinh", "xmas", "ông già noel", "santa claus", "santa",
     "reindeer", "tuần lộc", "cây thông", "christmas tree", "quà tặng", "present", "gift",
     "tuyết", "snow", "ngôi sao", "star", "chuông", "bell", "vòng nguyệt quế", "wreath", "giáng sinh"],
    ["new year", "tết dương lịch", "happy new year", "năm mới", "chúc mừng năm mới",
     "đêm giao thừa", "new year's eve", "countdown", "đếm ngược", "pháo hoa", "firework",
     "champagne", "rượu sâm panh", "tiệc tùng", "party", "hy vọng", "hope", "khởi đầu mới",
     "new beginning", "celebration", "lời chúc", "wish", "năm mới"]
]
INDENTED_FORS = [
    ["ba", "cha", "father", "daddy", "lịch lãm", "thanh lịch", "áo vest", "phong trần", "mạnh mẽ", "khí chất",
     "nam tính", "đàn ông", "bia rượu", "hút thuốc", "thể thao", "bố"],
    ["má", "mami", "má mì", "má mỳ", "mother", "mom", "tinh tế", "dịu dàng", "hoa", "nữ tính", "trà", "hoa hồng",
     "sang trọng", "chăm sóc", "sắc đẹp", "mẹ"],
    ["bạn gái", "bạn trai", "boyfriend", "girlfriend", "lover", "partner", "lãng mạn", "tình yêu", "trái tim",
     "hoa hồng", "hồng", "ngọt ngào", "couple", "valentine", "kỷ niệm", "ngày cưới", "anniversary", "người yêu"],
    ["con trai", "boy", "nam sinh", "cậu bé", "siêu nhân", "khủng long", "đua xe", "robot", "xe đồ chơi", "bóng đá",
     "thể thao", "game", "hoạt hình", "phiêu lưu", "tàu vũ trụ", "cướp biển", "năng động", "anh hùng", "em trai"],
    ["con gái", "girl", "nữ sinh", "cô bé", "công chúa", "lâu đài", "búp bê", "barbie", "unicorn", "kỳ lân",
     "hello kitty", "elsa", "frozen", "thần tiên", "nàng tiên", "phép thuật", "cầu vồng", "ngọt ngào", "dễ thương",
     "nữ hoàng", "bé gái", "em gái"],
    ["ông nội", "ông ngoại", "grandpa", "grandfather", "cụ ông", "trưởng thượng", "sang trọng", "truyền thống",
     "thâm trầm", "thanh lịch", "cổ điển", "trà", "sức khỏe", "trường thọ", "châu ấu", "ông"],
    ["bà nội", "bà ngoại", "grandma", "grandmother", "cụ bà", "truyền thống", "gia đình", "ấm áp", "yêu thương",
     "trang nhã", "nhẹ nhàng", "chăm sóc", "bánh truyền thống", "trà", "hoa", "cổ điển", "bà"],
    ["giám đốc", "trưởng phòng", "leader", "boss", "manager", "chuyên nghiệp", "sang trọng", "đẳng cấp", "áo vest",
     "thanh lịch", "tinh tế", "businessperson", "thành công", "lịch lãm", "khí chất", "sếp"],
    ["đồng sự", "colleague", "coworker", "bạn đồng nghiệp", "team", "nhóm", "văn phòng", "công sở", "chuyên nghiệp",
     "hợp tác", "làm việc nhóm", "thân thiện", "đồng nghiệp"],
    ["bạn thân", "friend", "best friend", "bạn học", "bạn cùng lớp", "đồng môn", "vui vẻ", "thoải mái", "niềm vui",
     "kỷ niệm", "chia sẻ", "thân thiết", "gắn bó", "squad", "gang", "bạn bè"]
]

TYPE_OF_CAKES = [
    ["bánh gato", "gateau", "gâteau", "bánh kem gato", "bánh gạt tô", "sponge cake", "gato"],
    ["bánh tiramisu", "bánh tiramisù", "bánh tira mi su", "tiramisu"],
    ["bánh mousse", "bánh kem mousse", "kem mousse", "mousse"],
    ["bánh phô mai", "cheese cake", "bánh pho mai", "bánh kem phô mai", "cheesecake"],
    ["bánh cup cake", "bánh kem nhỏ", "bánh muffin", "cup cake", "cupcake"],
    ["bánh entrement", "bánh entremets", "bánh kiểu pháp", "bánh kiểu Pháp", "entremet", "entrement"],
    ["bánh red velvet", "bánh nhung đỏ", "red velvet cake", "red velvet"],
    ["bánh bông lan", "bánh bông lan trứng muối", "bánh bông lan sữa tươi", "bông lan trứng", "chiffon cake",
     "bông lan"],
    ["bánh opera", "opera cake", "bánh kem opera", "opera"],
    ["bánh tart", "bánh pie", "bánh tart trái cây", "fruit tart", "tart"],
    ["bánh crepe", "bánh crepe cake", "bánh ngàn lớp", "crepe"]
]

FLAVORS = [
    ["chocolate", "sô cô la", "choco", "ca cao", "cacao", "socola"],
    ["dâu tây", "strawberry", "quả dâu", "trái dâu", "dâu"],
    ["passion fruit", "chanh dây", "passion", "maracuja", "chanh leo"],
    ["blueberry", "quả việt quất", "trái việt quất", "việt quất"],
    ["mango", "quả xoài", "trái xoài", "xoài"],
    ["vani", "vanilla", "va ni", "vanila"],
    ["matcha", "green tea", "trà matcha", "trà xanh"],
    ["coffee", "espresso", "cappuccino", "mocha", "cà phê"],
    ["cheese", "cream cheese", "cheesecake", "phô mai"],
    ["caramen", "caramel", "caramelo", "caramel"],
    ["coconut", "cùi dừa", "nước cốt dừa", "dừa"],
    ["orange", "quả cam", "trái cam", "cam"],
    ["lemon", "lime", "quả chanh", "trái chanh"],
    ["apple", "quả táo", "trái táo", "chanh", "táo"]
]

DECORATIONS = [
    ["bông hoa", "hoa tươi", "flower", "hoa giả", "hoa trang trí", "hoa"],
    ["dâu tây", "strawberry", "trái dâu", "quả dâu", "quả dâu tây"],
    ["rượu", "wine bottle", "whisky", "champagne", "vodka", "chai rượu"],
    ["figure", "trang trí nổi", "mô hình nhân vật", "nhân vật", "tượng", "mô hình"],
    ["superhero", "người nhện", "ironman", "batman", "captain america", "anh hùng", "siêu nhân"],
    ["dinosaur", "khủng long bạo chúa", "t-rex", "dino", "khủng long"],
    ["princess", "elsa", "anna", "nữ hoàng", "hoàng tử", "nàng tiên", "công chúa"],
    ["fruit", "hoa quả", "trái cây tươi", "cherry", "berry", "quả", "trái cây"],
    ["sô cô la", "socola", "socola đắng", "socola trắng", "choco", "chocolate"],
    ["hạt", "nut", "hạnh nhân", "macadamia", "óc chó", "hạt điều", "hạt trái cây"],
    ["bông hồng", "rose", "hoa hồng", "nụ hoa hồng", "nụ hồng"]
]

COLORS = [
    ["màu hồng", "pink", "hồng phấn", "hồng đậm", "hồng nhạt", "hồng"],
    ["màu tím", "purple", "violet", "tím lavender", "tím đậm", "tím nhạt", "tím"],
    ["màu xanh lá", "xanh lá cây", "green", "xanh lục", "xanh lá"],
    ["màu trắng", "white", "trắng tinh", "trắng kem", "trắng"],
    ["màu vàng", "yellow", "vàng gold", "vàng nhạt", "vàng đậm", "vàng"],
    ["màu nâu", "brown", "nâu nhạt", "nâu đậm", "chocolate", "nâu"],
    ["màu đỏ", "red", "đỏ tươi", "đỏ đậm", "đỏ nhạt", "đỏ"],
    ["màu đen", "black", "đen"],
    ["màu xanh dương", "xanh biển", "blue", "navy", "xanh da trời", "xanh dương"],
    ["màu cam", "orange", "cam đậm", "cam nhạt", "cam"]
]
